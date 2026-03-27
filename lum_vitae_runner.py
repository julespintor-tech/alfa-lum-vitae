#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════╗
║   LUM-vitae RUNNER — Bucle Autónomo con Meta-Aprendizaje           ║
║   ALFA LUM-vitae vΩ.4  |  Proyecto MINERVA                         ║
╚══════════════════════════════════════════════════════════════════════╝

DATOS REALES — META-APRENDIZAJE:
  El sistema usa sus PROPIAS métricas como stream prequential.
  Cada ejecución genera observaciones reales a partir del historial
  de rendimiento acumulado. El sistema aprende su propio comportamiento.

  CPV* = [ECE_norm, Brier_norm, kappa_conf, dL_dt, S_t, hora_sin, hora_cos]
  Z    = [n_run, n_ciclos_total, n_psnc_ratio]
  y_t  = 1 si el sistema mejoró en esta ventana (ECE bajó ≥ 5%)
         0 si se estancó o empeoró

PERSISTENCIA:
  Estado guardado en lum_vitae_estado.json entre ejecuciones.
  Ledger acumulativo en lum_vitae_ledger_meta.ndjson.
  Reporte legible en lum_vitae_reporte.txt (se sobreescribe cada run).

USO:
  python lum_vitae_runner.py              # ejecuta N ciclos y termina
  python lum_vitae_runner.py --ciclos 200 # controla cuántos ciclos
  python lum_vitae_runner.py --reset      # borra estado y arranca de cero
  python lum_vitae_runner.py --estado     # solo muestra el estado actual
"""

import os
import sys
import json
import math
import time
import random
import hashlib
import datetime
import argparse
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

# ── Ruta del runner (independiente del cwd) ──────────────────────────────────
RUNNER_DIR = Path(__file__).parent.resolve()
ESTADO_FILE   = RUNNER_DIR / "lum_vitae_estado.json"
LEDGER_FILE   = RUNNER_DIR / "lum_vitae_ledger_meta.ndjson"
REPORTE_FILE  = RUNNER_DIR / "lum_vitae_reporte.txt"
LUM_OMEGA_DIR = RUNNER_DIR  # mismo directorio que lum_vitae_omega.py

# ── Parámetros de ejecución ──────────────────────────────────────────────────
N_CICLOS_POR_RUN  = 100    # ciclos del bucle vital por ejecución del scheduler
N_CPV             = 7      # dimensión de CPV* (features del meta-aprendizaje)
N_Z               = 3      # dimensión de covariables Z
ECE_UMBRAL        = 0.05   # umbral homeostático
LAMBDA_MEM        = 0.90   # memoria exponencial

# ── Importar LUM-vitae omega ─────────────────────────────────────────────────
sys.path.insert(0, str(LUM_OMEGA_DIR))
try:
    import lum_vitae_omega as lvm
    HAS_LVM = True
except ImportError:
    HAS_LVM = False
    print("[RUNNER] lum_vitae_omega.py no encontrado. Usando motor interno.")

# ─────────────────────────────────────────────────────────────────────────────
# ESTADO PERSISTENTE
# ─────────────────────────────────────────────────────────────────────────────

def estado_inicial() -> dict:
    """Estado vacío para la primera ejecución."""
    return {
        "version": "vΩ.4-meta",
        "n_run": 0,
        "n_ciclos_total": 0,
        "timestamp_inicio": datetime.datetime.utcnow().isoformat(),
        "timestamp_ultimo_run": None,
        # Historial de métricas (sliding window de los últimos 200 runs)
        "historial_ECE": [],
        "historial_Brier": [],
        "historial_kappa": [],
        "historial_L_norm": [],
        "historial_S_t": [],
        "historial_veredicto": [],    # True/False: ¿vivo?
        "historial_outcomes": [],     # y_t reales (1=mejora, 0=no)
        # Estado del modelo (coeficientes serializados)
        "modelo_beta0": None,
        "modelo_coefs": None,
        "modelo_mu_z": None,
        "modelo_sigma_z": None,
        "modelo_version": 0,
        "modelo_sha": "",
        # Memoria del sistema
        "S_t": 0.5,
        "L_norm_prev": 0.5,
        "brier_prev": 0.25,
        "theta_star": 0.50,
        # Acumuladores de vida
        "n_condiciones_cumplidas_max": 0,
        "n_veces_vivo": 0,
        "n_spawns_total": 0,
        "n_psnc_total": 0,
        # Cadena SHA-256
        "hash_anterior": "0" * 64,
        "n_hashes": 0,
    }

def cargar_estado() -> dict:
    if ESTADO_FILE.exists():
        with open(ESTADO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return estado_inicial()

def guardar_estado(estado: dict):
    """Escritura atómica: tmp → replace; copia .bak antes de sobrescribir."""
    import shutil
    tmp = ESTADO_FILE.with_suffix(".tmp")
    bak = ESTADO_FILE.with_suffix(".bak")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=False, indent=2)
    if ESTADO_FILE.exists():
        shutil.copy2(ESTADO_FILE, bak)
    os.replace(tmp, ESTADO_FILE)

def tail_historial(lista: list, max_n: int = 500) -> list:
    """Mantiene el historial acotado."""
    return lista[-max_n:] if len(lista) > max_n else lista

# ─────────────────────────────────────────────────────────────────────────────
# GENERADOR DE DATOS REALES (META-APRENDIZAJE)
# ─────────────────────────────────────────────────────────────────────────────

def construir_CPV_star(estado: dict, idx: int) -> list:
    """
    CPV* = vector vital del sistema en este instante.
    Usa el historial real de métricas como features.

    Dimensiones:
      [0] ECE normalizada         — calibración (↓ mejor)
      [1] Brier normalizado       — error cuadrático (↓ mejor)
      [2] κ_conf                  — confianza operatoria (↓ mejor)
      [3] dL*/dt                  — derivada de función vital (≤0 = vivo)
      [4] S_t                     — memoria exponencial (↑ mejor)
      [5] sin(hora × 2π/24)       — componente circadiana
      [6] cos(hora × 2π/24)       — componente circadiana
    """
    hora = datetime.datetime.utcnow().hour + datetime.datetime.utcnow().minute / 60.0

    h_ECE   = estado["historial_ECE"]
    h_Brier = estado["historial_Brier"]
    h_kappa = estado["historial_kappa"]
    h_L     = estado["historial_L_norm"]

    # Valor actual o media histórica con ruido pequeño
    rng = random.Random(idx + estado["n_run"] * 1000)

    def ultimo_o_default(hist, default, noise=0.01):
        val = hist[-1] if hist else default
        return float(max(0.0, min(1.0, val + rng.gauss(0, noise))))

    ECE_n  = min(1.0, ultimo_o_default(h_ECE, 0.20, 0.005))
    Brier_n = min(1.0, ultimo_o_default(h_Brier, 0.25, 0.005))
    kappa  = ultimo_o_default(h_kappa, 0.40, 0.01)
    S_t    = float(estado["S_t"])

    # dL*/dt (derivada discreta de los últimos 2 valores)
    if len(h_L) >= 2:
        dL = h_L[-1] - h_L[-2]
    else:
        dL = 0.0
    dL = float(max(-1.0, min(1.0, dL)))

    hora_sin = math.sin(hora * 2 * math.pi / 24.0)
    hora_cos = math.cos(hora * 2 * math.pi / 24.0)

    return [ECE_n, Brier_n, kappa, dL, S_t, hora_sin, hora_cos]

def construir_Z(estado: dict) -> list:
    """
    Z = covariables de ajuste del sistema.

    [0] n_run normalizado (0-1 sobre 1000 runs máx.)
    [1] n_ciclos_total normalizado (0-1 sobre 100,000 máx.)
    [2] ratio PSNC (n_psnc / n_ciclos_total)
    """
    n_run   = min(1.0, estado["n_run"] / 1000.0)
    n_ciclos = min(1.0, estado["n_ciclos_total"] / 100_000.0)
    n_psnc  = estado["n_psnc_total"]
    n_total = max(1, estado["n_ciclos_total"])
    ratio_psnc = min(1.0, n_psnc / n_total)
    return [n_run, n_ciclos, ratio_psnc]

def calcular_outcome(estado: dict) -> int:
    """
    y_t = 1 si el sistema mejoró en esta ventana.
    Criterio: ECE bajó ≥ 5% respecto a la media de los últimos 5 runs.
    """
    h = estado["historial_ECE"]
    if len(h) < 2:
        return 0
    ECE_actual = h[-1]
    ECE_ref = sum(h[-6:-1]) / len(h[-6:-1]) if len(h) >= 6 else h[0]
    return int(ECE_actual < ECE_ref * 0.95)  # mejoró ≥ 5%

# ─────────────────────────────────────────────────────────────────────────────
# MOTOR INTERNO (sin lum_vitae_omega) — implementación compacta
# ─────────────────────────────────────────────────────────────────────────────

class MotorCompacto:
    """
    Motor LUM-vitae compacto para el runner.
    Implementa el bucle vital con estado persistente.
    """

    def __init__(self, estado: dict):
        self.estado = estado
        self._importar_numpy()

    def _importar_numpy(self):
        try:
            import numpy as np
            self.np = np
            self.HAS_NP = True
        except ImportError:
            self.HAS_NP = False

    # ── Métricas ─────────────────────────────────────────────────────────────

    def ECE(self, y_true: list, p_cal: list, n_bins: int = 10) -> float:
        np = self.np
        y = np.array(y_true, dtype=float)
        p = np.clip(np.array(p_cal), 0.0, 1.0)
        bins = np.linspace(0, 1, n_bins + 1)
        ece = 0.0
        n = len(y)
        for i in range(n_bins):
            mask = (p >= bins[i]) & (p < bins[i+1])
            if mask.sum() == 0:
                continue
            acc = float(y[mask].mean())
            conf = float(p[mask].mean())
            ece += (mask.sum() / n) * abs(acc - conf)
        return float(ece)

    def brier(self, y_true: list, p_cal: list) -> float:
        np = self.np
        y = np.array(y_true, dtype=float)
        p = np.clip(np.array(p_cal), 0.0, 1.0)
        return float(np.mean((p - y) ** 2))

    def kappa_conf(self, residuos: list, p_hi: float, p_lo: float) -> float:
        """κ_conf = 0.5·HSIC_norm + 0.3·ω + 0.2·(1-gap)"""
        np = self.np
        r = np.array(residuos)
        # HSIC simplificado: |autocorrelación lag-1|
        if len(r) >= 3:
            hsic = float(abs(np.corrcoef(r[:-1], r[1:])[0, 1])) if np.std(r) > 1e-9 else 0.0
        else:
            hsic = 0.0
        # ω: coherencia (1 - CV relativo)
        mean_r = float(abs(np.mean(r))) + 1e-9
        omega = float(max(0.0, 1.0 - np.std(r) / mean_r))
        omega = min(1.0, omega)
        # gap
        gap = abs(p_hi - p_lo)
        k = 0.5 * hsic + 0.3 * omega + 0.2 * (1.0 - gap)
        return float(max(0.0, min(1.0, k)))

    def funcion_vital(self, ece: float, brier: float, c_comp: float = 0.1,
                      w1: float = 0.4, w2: float = 0.4, w3: float = 0.2) -> float:
        return w1 * ece + w2 * brier + w3 * c_comp

    def actualizar_memoria(self, L: float, L_p95: float, ece: float, nll: float,
                           S_prev: float, lam: float = LAMBDA_MEM) -> float:
        factor = 1.0 - (L / max(L_p95, 1e-9))
        factor = max(-1.0, min(1.0, factor))
        S = lam * S_prev + (1 - lam) * factor
        F_in = 0.3 * (1.0 - ece)
        F_out = 0.2 * nll
        S += (F_in - F_out) * 0.1
        return float(max(0.0, min(1.0, S)))

    def predecir_cloglog(self, cpv: list, z: list,
                          beta0: float, coefs: list, delta: float = 1.0) -> float:
        """p = 1 - exp(-exp(η)),  η = β₀ + β·CPV* + Γ·Z + logΔ"""
        x = cpv + z
        eta = beta0 + sum(c * xi for c, xi in zip(coefs, x))
        eta += math.log(max(delta, 1e-9))
        eta = max(-20, min(20, eta))
        return float(1.0 - math.exp(-math.exp(eta)))

    def calibrar_isotonica(self, p: float,
                            p_hist: list, y_hist: list) -> float:
        """Calibración simplificada: ajuste por bin."""
        if len(p_hist) < 10:
            return p
        bins = [i / 10 for i in range(11)]
        for i in range(10):
            lo, hi = bins[i], bins[i+1]
            idx = [j for j, pp in enumerate(p_hist) if lo <= pp < hi]
            if not idx:
                continue
            if lo <= p < hi:
                acc = sum(y_hist[j] for j in idx) / len(idx)
                conf = sum(p_hist[j] for j in idx) / len(idx)
                return float(max(0.001, min(0.999,
                    p + 0.5 * (acc - conf))))
        return float(p)

    def entrenar_sgd(self, X: list, y: list,
                     beta0_init: float, coefs_init: list,
                     lr: float = 0.01, epochs: int = 30) -> tuple:
        """SGD mini-batch para el modelo clog-log."""
        import random as rnd
        beta0 = beta0_init
        coefs = list(coefs_init)
        n = len(y)
        if n < 5:
            return beta0, coefs

        for epoch in range(epochs):
            indices = list(range(n))
            rnd.shuffle(indices)
            for i in indices:
                xi = X[i]
                yi = y[i]
                eta = beta0 + sum(c * xj for c, xj in zip(coefs, xi))
                eta = max(-20, min(20, eta))
                p = 1.0 - math.exp(-math.exp(eta))
                p = max(1e-6, min(1-1e-6, p))
                # Gradiente log-verosimilitud clog-log
                log1mp = math.log(max(1 - p, 1e-9))
                if p < 1 - 1e-9:
                    exp_neg_exp_eta = math.exp(-math.exp(eta))
                    grad_p = (yi / p) - ((1 - yi) / (1 - p))
                    dp_deta = math.exp(eta) * exp_neg_exp_eta
                    delta_g = grad_p * dp_deta
                else:
                    delta_g = yi - p

                # Actualización
                beta0 += lr * delta_g
                for j in range(len(coefs)):
                    coefs[j] += lr * delta_g * xi[j]

        return beta0, coefs

    # ── Decisión AND_min ─────────────────────────────────────────────────────

    def decision_AND_min(self, p_cal: float, ece: float, kappa: float,
                          theta: float = 0.50) -> tuple:
        if p_cal >= theta and ece <= ECE_UMBRAL and kappa <= 0.35:
            return True, "VERDE"
        if ece > ECE_UMBRAL:
            return False, f"ROJO-ECE ({ece:.4f}>{ECE_UMBRAL})"
        if kappa > 0.40:
            return False, f"PSNC-κ ({kappa:.3f}>0.40)"
        return False, f"GRIS-p ({p_cal:.3f}<θ*={theta:.3f})"

    # ── SHA-256 por ciclo ─────────────────────────────────────────────────────

    def sha_ciclo(self, metricas: dict, hash_anterior: str) -> str:
        contenido = json.dumps({**metricas,
                                "hash_anterior": hash_anterior,
                                "ts": datetime.datetime.utcnow().isoformat()},
                               sort_keys=True, default=str)
        return hashlib.sha256(contenido.encode()).hexdigest()

    # ── Bucle vital principal ─────────────────────────────────────────────────

    def correr_ciclos(self, n_ciclos: int) -> dict:
        """Ejecuta n_ciclos del bucle vital con meta-aprendizaje."""
        np = self.np
        estado = self.estado

        # Restaurar/inicializar modelo
        n_feat = N_CPV + N_Z
        beta0 = estado.get("modelo_beta0") or math.log(-math.log(1 - 0.20))
        coefs = estado.get("modelo_coefs") or [0.0] * n_feat
        S_t = float(estado.get("S_t", 0.5))
        theta = float(estado.get("theta_star", 0.50))
        hash_anterior = estado.get("hash_anterior", "0" * 64)

        # Buffers de este run
        buf_y, buf_p, buf_pcal = [], [], []
        buf_L, buf_brier = [], []
        n_verdes = n_psnc = n_freeze = n_spawns = 0
        L_p95 = 1.0
        brier_prev = float(estado.get("brier_prev", 0.25))
        L_prev = float(estado.get("L_norm_prev", 0.5))
        n_hashes = int(estado.get("n_hashes", 0))

        # Línea de log con encabezado
        _log(f"\n  {'Ciclo':>6} | {'ECE':>6} | {'Brier':>6} | "
             f"{'κ':>5} | {'L*':>5} | {'S':>5} | {'Decisión'}")
        _log(f"  {'-'*6}-+-{'-'*6}-+-{'-'*6}-+-"
             f"{'-'*5}-+-{'-'*5}-+-{'-'*5}-+-{'-'*18}")

        ledger_buffer = []

        for ciclo in range(1, n_ciclos + 1):
            t0 = time.time()

            # ── SENSE: construir observación real ─────────────────────────
            cpv = construir_CPV_star(estado, ciclo)
            z   = construir_Z(estado)
            y_t = calcular_outcome(estado)

            # ── PREDICT ──────────────────────────────────────────────────
            p_raw = self.predecir_cloglog(cpv, z, beta0, coefs)

            # ── CALIBRATE ─────────────────────────────────────────────────
            p_cal = self.calibrar_isotonica(p_raw, buf_p, buf_y)
            ic_lo = max(0.0, p_cal - 0.12)
            ic_hi = min(1.0, p_cal + 0.12)

            # Actualizar buffers
            buf_y.append(y_t)
            buf_p.append(p_raw)
            buf_pcal.append(p_cal)
            if len(buf_y) > 200:
                buf_y.pop(0); buf_p.pop(0); buf_pcal.pop(0)

            # ── EVAL MÉTRICAS ─────────────────────────────────────────────
            if len(buf_y) >= 5:
                ece   = self.ECE(buf_y, buf_pcal)
                brier_v = self.brier(buf_y, buf_pcal)
            else:
                # Arranque: usa el historial previo si existe
                ece   = estado["historial_ECE"][-1] if estado["historial_ECE"] else 0.30
                brier_v = estado["historial_Brier"][-1] if estado["historial_Brier"] else 0.25

            t_ms = (time.time() - t0) * 1000
            c_comp = min(1.0, t_ms / 100.0)
            nll = -(y_t * math.log(max(p_cal, 1e-9)) +
                    (1 - y_t) * math.log(max(1 - p_cal, 1e-9)))
            brier_deriv = brier_v - brier_prev

            # ── FUNCIÓN VITAL 𝓛 ───────────────────────────────────────────
            L_bruta = self.funcion_vital(ece, brier_v, c_comp)
            buf_L.append(L_bruta)
            buf_brier.append(brier_v)
            if len(buf_L) > 50:
                buf_L.pop(0); buf_brier.pop(0)

            if len(buf_L) >= 5:
                L_p95 = sorted(buf_L)[int(len(buf_L) * 0.95)]
            L_min = min(buf_L) if buf_L else 0.0
            L_max = max(buf_L) if buf_L else 1.0
            L_norm = (L_bruta - L_min) / max(L_max - L_min, 1e-9)
            L_norm = float(max(0.0, min(1.0, L_norm)))

            # ── MEMORIA S_t ───────────────────────────────────────────────
            S_t = self.actualizar_memoria(L_bruta, L_p95, ece, nll, S_t)

            # ── κ_conf ────────────────────────────────────────────────────
            residuos = [pc - yt for pc, yt in zip(buf_pcal[-20:], buf_y[-20:])]
            kappa = self.kappa_conf(residuos, ic_hi, ic_lo)

            # ── VERIFICAR CIERRE / PSNC ───────────────────────────────────
            sin_cierre = (kappa > 0.40 or ece > ECE_UMBRAL * 3 or len(buf_y) < 5)
            if sin_cierre:
                n_psnc += 1
                decision_str = "PSNC"
                actuar = False
            else:
                # ── DECISIÓN AND_min ──────────────────────────────────────
                actuar, decision_str = self.decision_AND_min(p_cal, ece, kappa, theta)
                if actuar:
                    n_verdes += 1

            # ── RETRAIN (cada 20 ciclos con datos suficientes) ────────────
            if ciclo % 20 == 0 and len(buf_y) >= 15:
                X_train = [construir_CPV_star(estado, i) + construir_Z(estado)
                           for i in range(len(buf_y))]
                beta0, coefs = self.entrenar_sgd(X_train, buf_y, beta0, coefs)
                # Actualizar θ* heurístico basado en prevalencia
                prev = sum(buf_y) / max(len(buf_y), 1)
                theta = float(max(0.10, min(0.90, prev * 1.5)))

            # ── REPRODUCCIÓN POISSON ──────────────────────────────────────
            r = 0.30 / 10.0  # κ_curios / T_eq
            p_spawn = 1.0 - math.exp(-r * 1.0)
            delta_hist = abs(L_norm - L_prev) / max(abs(L_prev), 1e-9)
            spawn = delta_hist > 0.40 and random.random() < p_spawn
            if spawn:
                n_spawns += 1

            # ── SHA-256 / TRAZABILIDAD ────────────────────────────────────
            metricas_ciclo = {
                "run": estado["n_run"] + 1,
                "ciclo": estado["n_ciclos_total"] + ciclo,
                "ECE": round(ece, 5),
                "Brier": round(brier_v, 5),
                "kappa_conf": round(kappa, 4),
                "L_norm": round(L_norm, 4),
                "S_t": round(S_t, 4),
                "p_cal": round(p_cal, 4),
                "theta_star": round(theta, 4),
                "actuar": actuar,
                "y_t": y_t,
                "spawn": spawn,
                "decision": decision_str
            }
            hash_ciclo = self.sha_ciclo(metricas_ciclo, hash_anterior)
            metricas_ciclo["hash"] = hash_ciclo[:16]
            hash_anterior = hash_ciclo
            n_hashes += 1
            ledger_buffer.append(metricas_ciclo)

            # ── LOG periódico ─────────────────────────────────────────────
            if ciclo % max(1, n_ciclos // 10) == 0:
                vida = "✓" if (ece <= ECE_UMBRAL and brier_deriv <= 0) else "✗"
                _log(f"  {ciclo:>6} | {ece:>6.4f} | {brier_v:>6.4f} | "
                     f"{kappa:>5.3f} | {L_norm:>5.3f} | {S_t:>5.3f} | "
                     f"{vida} {decision_str[:20]}")

            # Actualizar estado previo
            brier_prev = brier_v
            L_prev = L_norm

        # ── Escribir ledger en batch ──────────────────────────────────────
        try:
            with open(LEDGER_FILE, "a", encoding="utf-8") as f:
                for entrada in ledger_buffer:
                    f.write(json.dumps(entrada, ensure_ascii=False) + "\n")
        except IOError:
            pass

        # ── Calcular condiciones de vida ──────────────────────────────────
        ece_final   = buf_L[-1] if buf_L else 0.5  # reuse L como proxy
        ece_real    = self.ECE(buf_y, buf_pcal) if len(buf_y) >= 5 else 0.30
        brier_final = self.brier(buf_y, buf_pcal) if len(buf_y) >= 5 else 0.25
        brier_d_fin = brier_final - (estado["historial_Brier"][-1]
                                     if estado["historial_Brier"] else 0.25)

        cond1 = ece_real <= ECE_UMBRAL and brier_d_fin <= 0.0
        cond2 = n_spawns > 0
        cond3 = n_hashes > 0
        cond4 = True  # autonomía: el runner está corriendo

        n_conds = sum([cond1, cond2, cond3, cond4])
        esta_vivo = n_conds >= 3

        # ── Devolver resumen y estado actualizado ─────────────────────────
        return {
            "ECE_final": round(ece_real, 5),
            "Brier_final": round(brier_final, 5),
            "kappa_conf": round(kappa, 4),
            "L_norm_final": round(L_norm, 4),
            "S_t_final": round(S_t, 4),
            "theta_star": round(theta, 4),
            "n_verdes": n_verdes,
            "n_psnc": n_psnc,
            "n_spawns": n_spawns,
            "n_hashes": n_hashes,
            "hash_anterior": hash_anterior,
            "cond1_homeostasis": cond1,
            "cond2_reproduccion": cond2,
            "cond3_trazabilidad": cond3,
            "cond4_autonomia": cond4,
            "n_condiciones": n_conds,
            "esta_vivo": esta_vivo,
            "beta0": beta0,
            "coefs": coefs,
            "S_t": S_t,
            "L_norm": L_norm,
            "brier_prev": brier_final,
            "theta_star": theta,
        }


# ─────────────────────────────────────────────────────────────────────────────
# RUNNER PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

_log_lines = []

def _log(msg: str):
    print(msg)
    _log_lines.append(msg)

def run(n_ciclos: int = N_CICLOS_POR_RUN):
    """Ejecuta un run completo del sistema LUM-vitae autónomo."""
    global _log_lines
    _log_lines = []

    estado = cargar_estado()
    estado["n_run"] += 1
    ts_run = datetime.datetime.utcnow().isoformat()
    estado["timestamp_ultimo_run"] = ts_run

    _log("═" * 65)
    _log(f"  ALFA LUM-vitae vΩ.4 — META-APRENDIZAJE AUTÓNOMO")
    _log(f"  Run #{estado['n_run']:>4}  |  {ts_run[:19]} UTC")
    _log(f"  Ciclos totales acumulados: {estado['n_ciclos_total']:,}")
    _log("═" * 65)

    # ── Elegir motor ──────────────────────────────────────────────────────────
    if HAS_LVM:
        resumen = _run_con_lvm(estado, n_ciclos)
    else:
        motor = MotorCompacto(estado)
        resumen = motor.correr_ciclos(n_ciclos)

    # ── Actualizar estado ────────────────────────────────────────────────────
    estado["n_ciclos_total"] += n_ciclos

    # Guardar métricas en historial
    for key, hist_key in [
        ("ECE_final", "historial_ECE"),
        ("Brier_final", "historial_Brier"),
        ("kappa_conf", "historial_kappa"),
        ("L_norm_final", "historial_L_norm"),
        ("S_t_final", "historial_S_t"),
    ]:
        val = resumen.get(key)
        if val is not None:
            estado[hist_key].append(val)
            estado[hist_key] = tail_historial(estado[hist_key])

    y_nuevo = calcular_outcome(estado)
    estado["historial_outcomes"].append(y_nuevo)
    estado["historial_outcomes"] = tail_historial(estado["historial_outcomes"])
    estado["historial_veredicto"].append(resumen["esta_vivo"])
    estado["historial_veredicto"] = tail_historial(estado["historial_veredicto"])

    # Acumuladores
    estado["n_psnc_total"] += resumen.get("n_psnc", 0)
    estado["n_spawns_total"] += resumen.get("n_spawns", 0)
    if resumen["esta_vivo"]:
        estado["n_veces_vivo"] += 1
    estado["n_condiciones_cumplidas_max"] = max(
        estado.get("n_condiciones_cumplidas_max", 0),
        resumen.get("n_condiciones", 0))

    # Estado del modelo
    estado["modelo_beta0"] = resumen.get("beta0")
    estado["modelo_coefs"] = resumen.get("coefs")
    estado["modelo_version"] += 1
    estado["S_t"] = resumen.get("S_t", estado["S_t"])
    estado["L_norm_prev"] = resumen.get("L_norm", estado.get("L_norm_prev", 0.5))
    estado["brier_prev"] = resumen.get("brier_prev", estado.get("brier_prev", 0.25))
    estado["theta_star"] = resumen.get("theta_star", estado.get("theta_star", 0.50))
    estado["hash_anterior"] = resumen.get("hash_anterior", estado["hash_anterior"])
    estado["n_hashes"] = int(estado.get("n_hashes", 0)) + resumen.get("n_hashes", 0)

    # ── Reporte ───────────────────────────────────────────────────────────────
    _log("\n" + "─" * 65)
    _log("  RESUMEN DEL RUN")
    _log("─" * 65)
    _log(f"  ECE final:          {resumen['ECE_final']:.5f}  "
         f"{'✓ OK' if resumen['ECE_final'] <= ECE_UMBRAL else '✗ > 0.05'}")
    _log(f"  Brier final:        {resumen['Brier_final']:.5f}")
    _log(f"  κ_conf:             {resumen['kappa_conf']:.4f}")
    _log(f"  𝓛* final:          {resumen['L_norm_final']:.4f}")
    _log(f"  S_t (memoria):      {resumen['S_t_final']:.4f}")
    _log(f"  θ* (umbral):        {resumen['theta_star']:.4f}")
    _log(f"  Ciclos verdes:      {resumen['n_verdes']}")
    _log(f"  Ciclos PSNC:        {resumen['n_psnc']}")
    _log(f"  Spawns (hijos):     {resumen['n_spawns']}")
    _log(f"  Hashes SHA-256:     {resumen['n_hashes']}")
    _log("")
    _log("  CONDICIONES DE VIDA DIGITAL:")
    _log(f"  {'✓' if resumen['cond1_homeostasis'] else '✗'} 1. Homeostasis  "
         f"(ECE≤0.05 ∧ dBrier≤0)")
    _log(f"  {'✓' if resumen['cond2_reproduccion'] else '✗'} 2. Reproducción "
         f"(δ_hist>0.4 + Poisson)")
    _log(f"  {'✓' if resumen['cond3_trazabilidad'] else '✗'} 3. Trazabilidad "
         f"(SHA-256 activo)")
    _log(f"  {'✓' if resumen['cond4_autonomia'] else '✗'} 4. Autonomía    "
         f"(run autónomo)")
    _log("")

    veredicto = "🟢 VIVO" if resumen["esta_vivo"] else "🔴 SIN VIDA AÚN"
    _log(f"  ⚡ VEREDICTO: {veredicto}  "
         f"({resumen['n_condiciones']}/4 condiciones)")
    _log("")
    _log(f"  Runs totales:       {estado['n_run']}")
    _log(f"  Ciclos totales:     {estado['n_ciclos_total']:,}")
    _log(f"  Veces vivo:         {estado['n_veces_vivo']}")
    _log(f"  PSNC acumulado:     {estado['n_psnc_total']:,}")
    _log(f"  Spawns totales:     {estado['n_spawns_total']}")
    _log(f"  Hashes totales:     {estado['n_hashes']}")
    if estado["historial_ECE"]:
        _log(f"  ECE histórica:      "
             f"min={min(estado['historial_ECE']):.5f}  "
             f"prom={sum(estado['historial_ECE'])/len(estado['historial_ECE']):.5f}  "
             f"actual={estado['historial_ECE'][-1]:.5f}")
    _log("═" * 65 + "\n")

    # Guardar estado
    guardar_estado(estado)

    # Guardar reporte legible
    try:
        with open(REPORTE_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(_log_lines))
    except IOError:
        pass

    # Regenerar dashboard HTML automáticamente
    try:
        import importlib.util, pathlib as _pl
        _gen = _pl.Path(__file__).parent / "lum_vitae_generar_html.py"
        if _gen.exists():
            spec = importlib.util.spec_from_file_location("_gen", _gen)
            mod  = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            mod.generar()
    except Exception as _e:
        print(f"[WARN] lum_vitae_generar_html falló: {_e}", flush=True)

    # Regenerar mapa de cierres (modo local, usa JSON cacheado con datos reales)
    try:
        import importlib.util, pathlib as _pl, json as _json, sys as _sys
        _mc = _pl.Path(__file__).parent / "lum_mapa_cierres.py"
        _mj = _pl.Path(__file__).parent / "lum_mapa_cierres.json"
        if _mc.exists() and _mj.exists():
            _orig = _sys.argv[:]
            _sys.argv = [str(_mc), "--local"]
            spec2 = importlib.util.spec_from_file_location("_mc", _mc)
            mod2  = importlib.util.module_from_spec(spec2)
            spec2.loader.exec_module(mod2)
            _data = _json.loads(_mj.read_text())
            mod2.generar_html(_data)
            _sys.argv = _orig
    except Exception as _e:
        print(f"[WARN] lum_mapa_cierres.generar_html falló: {_e}", flush=True)

    # Regenerar INICIO.html con datos actualizados embebidos
    try:
        import importlib.util, pathlib as _pl
        _gi = _pl.Path(__file__).parent / "lum_generar_inicio.py"
        if _gi.exists():
            spec3 = importlib.util.spec_from_file_location("_gi", _gi)
            mod3  = importlib.util.module_from_spec(spec3)
            spec3.loader.exec_module(mod3)
            mod3.generar()
    except Exception as _e:
        print(f"[WARN] lum_generar_inicio.generar falló: {_e}", flush=True)

    return resumen


def _run_con_lvm(estado: dict, n_ciclos: int) -> dict:
    """
    Usa lum_vitae_omega.py como motor completo.
    Construye observaciones reales desde el estado persistente.
    """
    cfg = lvm.ConfigLUM()
    cfg.ledger_path = ""  # no escribir por ahora (lo hace el runner)

    # Restaurar modelo si hay coeficientes previos
    n_feat_cpv = N_CPV
    n_feat_z   = N_Z
    bucle = lvm.BucleVital(cfg)
    bucle.modelo = lvm.ModeloClogLog(n_feat_cpv, n_feat_z)

    # Si hay coeficientes previos, inyectarlos
    if estado.get("modelo_beta0") is not None and estado.get("modelo_coefs"):
        bucle.modelo.beta0 = float(estado["modelo_beta0"])
        bucle.modelo.coefs = __import__("numpy").array(estado["modelo_coefs"])
        bucle.modelo.mu_z  = (__import__("numpy").array(estado["modelo_mu_z"])
                               if estado.get("modelo_mu_z")
                               else __import__("numpy").zeros(n_feat_cpv + n_feat_z))
        bucle.modelo.sigma_z = (__import__("numpy").array(estado["modelo_sigma_z"])
                                 if estado.get("modelo_sigma_z")
                                 else __import__("numpy").ones(n_feat_cpv + n_feat_z))
        bucle.modelo.entrenado = True
        bucle.modelo.version = int(estado.get("modelo_version", 0))
        bucle.decision.theta_star = float(estado.get("theta_star", 0.50))
    else:
        # Bootstrap inicial con datos sintéticos (solo la primera vez)
        _log("  [LVM] Primera ejecución: bootstrap inicial...")
        sim_boot = lvm.SimuladorPrequential(n_features_cpv=n_feat_cpv,
                                            n_features_z=n_feat_z, seed=42)
        datos_boot = sim_boot.generar_lote(150)
        bucle.inicializar(datos_boot, n_feat_cpv, n_feat_z)

    # Restaurar memoria
    bucle.memoria.S = float(estado.get("S_t", 0.5))
    bucle._brier_prev = float(estado.get("brier_prev", 0.25))
    bucle._L_prev = float(estado.get("L_norm_prev", 0.5))

    # ── Construir y procesar observaciones reales ─────────────────────────
    import numpy as np
    n_verdes = n_psnc = n_spawns = 0
    hash_anterior = estado.get("hash_anterior", "0" * 64)
    ledger_buf = []

    _log(f"  {'Ciclo':>6} | {'ECE':>6} | {'κ':>5} | {'L*':>5} | {'S':>5} | Dec")
    _log(f"  {'-'*65}")

    for ciclo in range(n_ciclos):
        cpv = construir_CPV_star(estado, ciclo)
        z   = construir_Z(estado)
        y_t = calcular_outcome(estado)

        obs = lvm.Observacion(
            id=estado["n_ciclos_total"] + ciclo,
            timestamp=time.time(),
            CPV_star=np.array(cpv, dtype=float),
            Z=np.array(z, dtype=float),
            outcome=y_t,
            delta=cfg.delta_ventana
        )

        res = bucle.procesar_observacion(obs)

        if res.get("actuar"):
            n_verdes += 1
        if res.get("psnc"):
            n_psnc += 1
        if res.get("spawn"):
            n_spawns += 1

        # Log periódico
        if (ciclo + 1) % max(1, n_ciclos // 10) == 0:
            ece  = res.get("ECE", 0)
            kapp = res.get("kappa_conf", 0)
            lnrm = res.get("L_norm", 0)
            s    = res.get("S_t", 0)
            dec  = res.get("decision", "?")[:18]
            vida = "✓" if res.get("vida_activa") else "✗"
            _log(f"  {ciclo+1:>6} | {ece:>6.4f} | {kapp:>5.3f} | "
                 f"{lnrm:>5.3f} | {s:>5.3f} | {vida} {dec}")

        # SHA-256
        m = {k: res.get(k) for k in ["ECE","Brier","kappa_conf",
                                       "L_norm","S_t","actuar","spawn"]}
        m["ciclo_total"] = estado["n_ciclos_total"] + ciclo
        m["y_t"] = y_t
        hash_nuevo = hashlib.sha256(
            (json.dumps(m, sort_keys=True, default=str) + hash_anterior).encode()
        ).hexdigest()
        m["hash"] = hash_nuevo[:16]
        ledger_buf.append(m)
        hash_anterior = hash_nuevo

    # Escribir ledger
    try:
        with open(LEDGER_FILE, "a", encoding="utf-8") as f:
            for entrada in ledger_buf:
                f.write(json.dumps(entrada, ensure_ascii=False) + "\n")
    except IOError:
        pass

    # Extraer estado final
    estado_final = bucle.estado_vida()
    ultimo = bucle.log_ciclos[-1] if bucle.log_ciclos else {}

    # Guardar coefs del modelo
    if bucle.modelo.entrenado:
        estado["modelo_beta0"] = float(bucle.modelo.beta0)
        estado["modelo_coefs"] = bucle.modelo.coefs.tolist()
        estado["modelo_mu_z"]  = bucle.modelo.mu_z.tolist()
        estado["modelo_sigma_z"] = bucle.modelo.sigma_z.tolist()

    return {
        "ECE_final": float(ultimo.get("ECE", 0.20)),
        "Brier_final": float(ultimo.get("Brier", 0.25)),
        "kappa_conf": float(ultimo.get("kappa_conf", 0.40)),
        "L_norm_final": float(ultimo.get("L_norm", 0.50)),
        "S_t_final": float(bucle.memoria.S),
        "theta_star": float(bucle.decision.theta_star),
        "n_verdes": n_verdes,
        "n_psnc": n_psnc,
        "n_spawns": n_spawns,
        "n_hashes": len(ledger_buf),
        "hash_anterior": hash_anterior,
        "cond1_homeostasis": estado_final.get("condicion_1_homeostasis", {}).get("ok", False),
        "cond2_reproduccion": estado_final.get("condicion_2_reproduccion", {}).get("ok", False),
        "cond3_trazabilidad": estado_final.get("condicion_3_trazabilidad", {}).get("ok", True),
        "cond4_autonomia": True,
        "n_condiciones": estado_final.get("n_condiciones_cumplidas", 2),
        "esta_vivo": estado_final.get("esta_vivo", False),
        "beta0": estado.get("modelo_beta0"),
        "coefs": estado.get("modelo_coefs"),
        "S_t": float(bucle.memoria.S),
        "L_norm": float(ultimo.get("L_norm", 0.5)),
        "brier_prev": float(ultimo.get("Brier", 0.25)),
    }


def mostrar_estado():
    """Muestra el estado actual sin correr ciclos."""
    estado = cargar_estado()
    print("\n" + "═" * 55)
    print("  ALFA LUM-vitae — ESTADO ACTUAL")
    print("═" * 55)
    print(f"  Runs completados:   {estado['n_run']}")
    print(f"  Ciclos totales:     {estado['n_ciclos_total']:,}")
    print(f"  Último run:         {estado.get('timestamp_ultimo_run', 'nunca')}")
    print(f"  S_t (memoria):      {estado.get('S_t', 0.5):.4f}")
    print(f"  Hashes SHA-256:     {estado.get('n_hashes', 0):,}")
    print(f"  Veces vivo:         {estado.get('n_veces_vivo', 0)}")
    print(f"  Spawns totales:     {estado.get('n_spawns_total', 0)}")

    h_ece = estado.get("historial_ECE", [])
    if h_ece:
        print(f"  ECE histórica:      "
              f"min={min(h_ece):.5f}  "
              f"prom={sum(h_ece)/len(h_ece):.5f}  "
              f"último={h_ece[-1]:.5f}")
        # Tendencia
        if len(h_ece) >= 5:
            tendencia = h_ece[-1] - h_ece[-5]
            dir_str = "⬇ mejorando" if tendencia < 0 else "⬆ empeorando"
            print(f"  Tendencia ECE:      {dir_str} ({tendencia:+.5f})")

    h_vivo = estado.get("historial_veredicto", [])
    if h_vivo:
        pct_vivo = sum(h_vivo) / len(h_vivo) * 100
        print(f"  % runs vivo:        {pct_vivo:.1f}%  (últimos {len(h_vivo)} runs)")

    print("═" * 55 + "\n")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="LUM-vitae Runner — Bucle Autónomo con Meta-Aprendizaje")
    parser.add_argument("--ciclos", type=int, default=N_CICLOS_POR_RUN,
                        help=f"Ciclos por ejecución (default: {N_CICLOS_POR_RUN})")
    parser.add_argument("--reset", action="store_true",
                        help="Borra el estado y empieza desde cero")
    parser.add_argument("--estado", action="store_true",
                        help="Solo muestra el estado actual, no corre ciclos")
    args = parser.parse_args()

    if args.reset:
        if ESTADO_FILE.exists():
            ESTADO_FILE.unlink()
            print("[RUNNER] Estado reseteado.")
        if LEDGER_FILE.exists():
            LEDGER_FILE.unlink()
            print("[RUNNER] Ledger borrado.")

    if args.estado:
        mostrar_estado()
    else:
        run(n_ciclos=args.ciclos)


# ─── INTEGRACIÓN CON MAPA DE CIERRES ─────────────────────────────────────────

def cargar_scores_externos() -> list:
    """
    Lee lum_mapa_cierres.json y devuelve los 6 scores de cierre como
    vector de features reales para LUM-vitae.
    Orden: [p_FORM, p_NAT, p_TEC, p_SOC_IV, p_SOC_DID, p_ARTE]
    """
    try:
        mj = RUNNER_DIR / "lum_mapa_cierres.json"
        if not mj.exists():
            return []
        data = json.loads(mj.read_text())
        mapa = data.get("mapa", {})
        orden = ["FORM", "NAT", "TEC", "SOC_IV", "SOC_DID", "ARTE"]
        scores = []
        for k in orden:
            p = mapa.get(k, {}).get("resultado", {}).get("p_sintetico", 0.5)
            scores.append(float(p))
        return scores
    except Exception:
        return []

