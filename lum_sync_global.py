#!/usr/bin/env python3
"""
lum_sync_global.py — Orquestador de sincronización global del proyecto ALFA LUM-vitae.

Lee las dos fuentes canónicas:
  1. lum_vitae_estado.json  → vida digital
  2. lum_mapa_cierres.json  → mapa de cierres MINERVA

Regenera todos los HTML derivados en orden correcto:
  1. lum_vitae_dashboard.html  (desde lum_vitae_generar_html.py)
  2. lum_mapa_cierres.html     (desde lum_mapa_cierres.py --html-only)
  3. 🏠 INICIO.html            (desde lum_generar_inicio.py)

Uso:
  python3 lum_sync_global.py          # regenera todo
  python3 lum_sync_global.py --check  # solo verifica coherencia, no regenera
"""

import json
import sys
import importlib.util
import pathlib
import datetime

BASE = pathlib.Path(__file__).parent

ESTADO_FILE = BASE / "lum_vitae_estado.json"
MAPA_FILE   = BASE / "lum_mapa_cierres.json"
DASHBOARD_HTML = BASE / "lum_vitae_dashboard.html"
MAPA_HTML      = BASE / "lum_mapa_cierres.html"
INICIO_HTML    = BASE / "🏠 INICIO.html"

MODO_CHECK = "--check" in sys.argv

# ─── Utilidades ───────────────────────────────────────────────────────────────

def ts() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def leer_json(path: pathlib.Path) -> dict:
    if not path.exists():
        print(f"  [ERR] No existe: {path.name}")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  [ERR] No se pudo leer {path.name}: {e}")
        return {}

def cargar_mod(path: pathlib.Path):
    """Carga un módulo Python desde su ruta absoluta."""
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

# ─── Verificación de coherencia ───────────────────────────────────────────────

def verificar_coherencia():
    """Comprueba que los HTMLs derivados no estén stale respecto al JSON canónico."""
    estado = leer_json(ESTADO_FILE)
    mapa   = leer_json(MAPA_FILE)
    if not estado or not mapa:
        print("  [WARN] No se pudo leer algún JSON canónico.")
        return False

    _uv = estado.get("ultimo_veredicto", {})
    n_conds = _uv.get("n_condiciones", -1)
    n_hashes_canon = estado.get("n_hashes", -1)
    n_run_canon = estado.get("n_run", -1)

    # Regla visual: ≤1→SIN VIDA, 2→EMERGENTE, ≥3→VIVO
    if n_conds >= 3:
        label_canon = "VIVO"
    elif n_conds == 2:
        label_canon = "EMERGENTE"
    else:
        label_canon = "SIN VIDA"

    print(f"\n{'─'*58}")
    print(f"  VERIFICACIÓN DE COHERENCIA  [{ts()}]")
    print(f"{'─'*58}")
    print(f"  JSON canónico:")
    print(f"    n_run={n_run_canon} | n_hashes={n_hashes_canon:,} | "
          f"n_condiciones={n_conds} → label={label_canon}")

    ok = True

    for html_path, html_name in [(DASHBOARD_HTML, "dashboard"), (INICIO_HTML, "INICIO")]:
        if not html_path.exists():
            print(f"  [WARN] {html_name}: no existe todavía")
            continue
        content = html_path.read_text(encoding="utf-8", errors="ignore")
        # Checks básicos: el HTML no debería mostrar hashes del snapshot viejo
        stale_hashes = "1,424,337,090" in content or "1424337090" in content
        if stale_hashes:
            print(f"  [ERR] {html_name}: contiene n_hashes VIEJO (1.4B)")
            ok = False
        else:
            print(f"  [OK]  {html_name}: sin hashes viejos")

    return ok

# ─── Regeneración de HTMLs ────────────────────────────────────────────────────

def regenerar_dashboard():
    gen_path = BASE / "lum_vitae_generar_html.py"
    if not gen_path.exists():
        print("  [ERR] No existe lum_vitae_generar_html.py")
        return False
    try:
        mod = cargar_mod(gen_path)
        mod.generar()
        print(f"  [OK]  lum_vitae_dashboard.html  [{ts()}]")
        return True
    except Exception as e:
        print(f"  [ERR] dashboard HTML: {e}")
        return False

def regenerar_mapa_html():
    """Regenera lum_mapa_cierres.html en modo seguro (--html-only) sin tocar el JSON."""
    mapa_py = BASE / "lum_mapa_cierres.py"
    mapa_json = BASE / "lum_mapa_cierres.json"
    if not mapa_py.exists():
        print("  [ERR] No existe lum_mapa_cierres.py")
        return False
    if not mapa_json.exists():
        print("  [ERR] No existe lum_mapa_cierres.json — no se puede regenerar HTML")
        return False
    try:
        orig_argv = sys.argv[:]
        sys.argv = [str(mapa_py), "--html-only"]  # modo seguro: no toca el JSON
        mod = cargar_mod(mapa_py)
        if hasattr(mod, "generar"):
            mod.generar()
        elif hasattr(mod, "generar_html"):
            data = json.loads(mapa_json.read_text(encoding="utf-8"))
            mod.generar_html(data)
        sys.argv = orig_argv
        print(f"  [OK]  lum_mapa_cierres.html       [{ts()}]")
        return True
    except Exception as e:
        sys.argv = orig_argv if 'orig_argv' in dir() else sys.argv
        print(f"  [ERR] mapa HTML: {e}")
        return False

def regenerar_inicio():
    gen_path = BASE / "lum_generar_inicio.py"
    if not gen_path.exists():
        print("  [ERR] No existe lum_generar_inicio.py")
        return False
    try:
        mod = cargar_mod(gen_path)
        mod.generar()
        print(f"  [OK]  🏠 INICIO.html             [{ts()}]")
        return True
    except Exception as e:
        print(f"  [ERR] INICIO HTML: {e}")
        return False

# ─── Entry point ──────────────────────────────────────────────────────────────

def sincronizar():
    """Regenera todos los HTML derivados en orden. Retorna True si todo OK."""
    print(f"\n{'═'*58}")
    print(f"  LUM SYNC GLOBAL  [{ts()}]")
    print(f"{'═'*58}")

    # Leer JSON canónicos
    estado = leer_json(ESTADO_FILE)
    mapa   = leer_json(MAPA_FILE)

    if not estado:
        print("  [FATAL] No se pudo leer lum_vitae_estado.json — abortando.")
        return False

    _uv = estado.get("ultimo_veredicto", {})
    n_conds = _uv.get("n_condiciones", 0)
    label = "VIVO" if n_conds >= 3 else ("EMERGENTE" if n_conds == 2 else "SIN VIDA")

    print(f"\n  Fuentes canónicas:")
    print(f"    vida digital: run={estado.get('n_run')} | "
          f"n_hashes={estado.get('n_hashes',0):,} | "
          f"{n_conds}/4 → {label}")
    if mapa:
        resumen = mapa.get("resumen", {})
        print(f"    mapa cierres: papers_curados={resumen.get('total_papers_curados','?')} | "
              f"papers_live={resumen.get('total_papers','?')}")

    print(f"\n  Regenerando HTMLs:")

    r1 = regenerar_dashboard()
    r2 = regenerar_mapa_html()
    r3 = regenerar_inicio()

    all_ok = r1 and r2 and r3
    print(f"\n{'═'*58}")
    if all_ok:
        print(f"  ✓ Sincronización completa — todos los HTML actualizados")
    else:
        print(f"  ⚠ Sincronización parcial — revisa errores arriba")
    print(f"{'═'*58}\n")
    return all_ok

if __name__ == "__main__":
    if MODO_CHECK:
        ok = verificar_coherencia()
        sys.exit(0 if ok else 1)
    else:
        ok = sincronizar()
        sys.exit(0 if ok else 1)
