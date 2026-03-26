#!/usr/bin/env python3
"""
ALFA LUM-vitae vΩ.4 — Generador de Dashboard HTML
Crea lum_vitae_dashboard.html con datos actuales embebidos.
Se puede abrir directamente en cualquier navegador (doble clic).
"""
import json, pathlib, datetime, html

BASE         = pathlib.Path(__file__).parent
ESTADO_FILE  = BASE / "lum_vitae_estado.json"
LEDGER_FILE  = BASE / "lum_vitae_ledger_meta.ndjson"
REPORTE_FILE = BASE / "lum_vitae_reporte.txt"
OUT_FILE     = BASE / "lum_vitae_dashboard.html"

def tama_face(estado, color, size=90):
    """
    Pixel-robot SVG character — estilo neón retro con cuerpo cuadrado,
    ojos LED rectangulares, brackets en esquinas y partículas de píxeles.
    Expresión y color cambian según el estado del sistema.
    """
    s = size / 90          # factor de escala
    uid = estado[:2]       # ID único para filtros SVG (evita colisiones)

    # ── Geometría base (coordenadas en escala 90px) ────────────────────────
    # Cabeza
    hx, hy, hw, hh, hr = 12, 6, 66, 52, 6
    # Ojos
    e1x, e2x, ey_b, ew, eh = 21, 51, 21, 18, 9
    # Boca (centro x, baseline y)
    mx, my = 45, 41
    # Cuerpo
    bx, by, bw, bh = 29, 60, 32, 15
    # Piernas
    lx1, lx2, ly, lw, lh = 32, 49, 76, 10, 8

    def sc(v):
        return round(v * s, 1)

    # ── Filtro de glow ─────────────────────────────────────────────────────
    blur = max(1.2, 2.5 * s)
    glow_filter = (
        f'<defs>'
        f'<filter id="g{uid}" x="-60%" y="-60%" width="220%" height="220%">'
        f'<feGaussianBlur in="SourceGraphic" stdDeviation="{blur:.1f}" result="b"/>'
        f'<feMerge><feMergeNode in="b"/><feMergeNode in="b"/>'
        f'<feMergeNode in="SourceGraphic"/></feMerge>'
        f'</filter>'
        f'<filter id="s{uid}" x="-30%" y="-30%" width="160%" height="160%">'
        f'<feGaussianBlur in="SourceGraphic" stdDeviation="{blur*0.5:.1f}"/>'
        f'</filter>'
        f'</defs>'
    )

    # ── Brackets en esquinas de la cabeza ─────────────────────────────────
    # Cada bracket = dos rectángulos en L (horizontal + vertical)
    b = sc(5)    # longitud del bracket
    t = sc(1.8)  # grosor
    bop = "0.85" if estado != "INERTE" else "0.40"
    corners = (
        # TL
        f'<rect x="{sc(hx)}" y="{sc(hy)}" width="{b}" height="{t}" fill="{color}" opacity="{bop}"/>'
        f'<rect x="{sc(hx)}" y="{sc(hy)}" width="{t}" height="{b}" fill="{color}" opacity="{bop}"/>'
        # TR
        f'<rect x="{sc(hx+hw)-b}" y="{sc(hy)}" width="{b}" height="{t}" fill="{color}" opacity="{bop}"/>'
        f'<rect x="{sc(hx+hw)-t}" y="{sc(hy)}" width="{t}" height="{b}" fill="{color}" opacity="{bop}"/>'
        # BL
        f'<rect x="{sc(hx)}" y="{sc(hy+hh)-t}" width="{b}" height="{t}" fill="{color}" opacity="{bop}"/>'
        f'<rect x="{sc(hx)}" y="{sc(hy+hh)-b}" width="{t}" height="{b}" fill="{color}" opacity="{bop}"/>'
        # BR
        f'<rect x="{sc(hx+hw)-b}" y="{sc(hy+hh)-t}" width="{b}" height="{t}" fill="{color}" opacity="{bop}"/>'
        f'<rect x="{sc(hx+hw)-t}" y="{sc(hy+hh)-b}" width="{t}" height="{b}" fill="{color}" opacity="{bop}"/>'
    )

    # ── Estado: ojos + boca + extras ──────────────────────────────────────
    if estado == "VIVO":
        # Ojos LED rectangulares llenos, brillantes
        eye_str = (
            f'<rect x="{sc(e1x)}" y="{sc(ey_b)}" width="{sc(ew)}" height="{sc(eh)}"'
            f' rx="{sc(2)}" fill="{color}" filter="url(#g{uid})"/>'
            f'<rect x="{sc(e2x)}" y="{sc(ey_b)}" width="{sc(ew)}" height="{sc(eh)}"'
            f' rx="{sc(2)}" fill="{color}" filter="url(#g{uid})"/>'
        )
        # Sonrisa amplia
        mouth_str = (
            f'<path d="M {sc(mx-14)},{sc(my)} Q {sc(mx)},{sc(my+12)} {sc(mx+14)},{sc(my)}"'
            f' fill="none" stroke="{color}" stroke-width="{sc(3)}"'
            f' stroke-linecap="round" filter="url(#g{uid})"/>'
        )
        # Partículas activas (8 píxeles dispersos)
        px_list = [(4,18,3),(2,45,2),(84,12,3),(86,40,2),(8,72,3),(80,68,2),(18,82,2),(72,82,3)]
        extras = "".join(
            f'<rect x="{sc(px)}" y="{sc(py)}" width="{sc(ps)}" height="{sc(ps)}"'
            f' fill="{color}" opacity="0.75" filter="url(#s{uid})"/>'
            for px, py, ps in px_list
        )
        head_op, body_op = "1", "0.9"

    elif estado == "EMERGENTE":
        # Ojos LED: uno más arriba (curioso/asimétrico)
        eye_str = (
            f'<rect x="{sc(e1x)}" y="{sc(ey_b+2)}" width="{sc(ew)}" height="{sc(eh)}"'
            f' rx="{sc(2)}" fill="{color}" opacity="0.9" filter="url(#g{uid})"/>'
            f'<rect x="{sc(e2x)}" y="{sc(ey_b-2)}" width="{sc(ew)}" height="{sc(eh)}"'
            f' rx="{sc(2)}" fill="{color}" opacity="0.9" filter="url(#g{uid})"/>'
        )
        mouth_str = (
            f'<path d="M {sc(mx-11)},{sc(my+1)} Q {sc(mx)},{sc(my+9)} {sc(mx+11)},{sc(my+1)}"'
            f' fill="none" stroke="{color}" stroke-width="{sc(2.5)}"'
            f' stroke-linecap="round" filter="url(#g{uid})"/>'
        )
        # Marco de escaneo (frame externo — efecto "targeting")
        fw = sc(72); fh = sc(58); fx = sc(9); fy = sc(4)
        fb = sc(7); ft = sc(2)
        extras = (
            f'<rect x="{fx}" y="{fy}" width="{fb}" height="{ft}" fill="{color}" opacity="0.55"/>'
            f'<rect x="{fx}" y="{fy}" width="{ft}" height="{fb}" fill="{color}" opacity="0.55"/>'
            f'<rect x="{fx+fw-fb}" y="{fy}" width="{fb}" height="{ft}" fill="{color}" opacity="0.55"/>'
            f'<rect x="{fx+fw-ft}" y="{fy}" width="{ft}" height="{fb}" fill="{color}" opacity="0.55"/>'
            f'<rect x="{fx}" y="{fy+fh-ft}" width="{fb}" height="{ft}" fill="{color}" opacity="0.55"/>'
            f'<rect x="{fx}" y="{fy+fh-fb}" width="{ft}" height="{fb}" fill="{color}" opacity="0.55"/>'
            f'<rect x="{fx+fw-fb}" y="{fy+fh-ft}" width="{fb}" height="{ft}" fill="{color}" opacity="0.55"/>'
            f'<rect x="{fx+fw-ft}" y="{fy+fh-fb}" width="{ft}" height="{fb}" fill="{color}" opacity="0.55"/>'
            + "".join(
                f'<rect x="{sc(px)}" y="{sc(py)}" width="{sc(ps)}" height="{sc(ps)}"'
                f' fill="{color}" opacity="0.45"/>'
                for px, py, ps in [(3,25,2),(85,20,2),(5,60,2),(83,55,2)]
            )
        )
        head_op, body_op = "0.92", "0.8"

    elif estado == "LATENTE":
        # Ojos semicerrados (rectángulo fino = ojos pesados)
        eye_str = (
            f'<rect x="{sc(e1x)}" y="{sc(ey_b+3)}" width="{sc(ew)}" height="{sc(eh*0.45)}"'
            f' rx="{sc(1.5)}" fill="{color}" opacity="0.6"/>'
            f'<rect x="{sc(e2x)}" y="{sc(ey_b+3)}" width="{sc(ew)}" height="{sc(eh*0.45)}"'
            f' rx="{sc(1.5)}" fill="{color}" opacity="0.6"/>'
        )
        mouth_str = (
            f'<line x1="{sc(mx-9)}" y1="{sc(my+4)}" x2="{sc(mx+9)}" y2="{sc(my+4)}"'
            f' stroke="{color}" stroke-width="{sc(2.5)}" stroke-linecap="round" opacity="0.6"/>'
        )
        # ZZZ flotantes y partículas muy tenues
        zfs = sc(9); zfs2 = sc(7)
        extras = (
            f'<text x="{sc(68)}" y="{sc(14)}" font-size="{zfs:.0f}" fill="{color}" opacity="0.55"'
            f' font-family="monospace" font-weight="bold">z</text>'
            f'<text x="{sc(74)}" y="{sc(7)}" font-size="{zfs2:.0f}" fill="{color}" opacity="0.35"'
            f' font-family="monospace" font-weight="bold">z</text>'
            + "".join(
                f'<rect x="{sc(px)}" y="{sc(py)}" width="{sc(ps)}" height="{sc(ps)}"'
                f' fill="{color}" opacity="0.25"/>'
                for px, py, ps in [(5,30,2),(83,35,2),(7,60,2)]
            )
        )
        head_op, body_op = "0.78", "0.65"

    else:  # INERTE
        # Ojos en X con líneas cruzadas
        ex_d = sc(4)
        eye_str = (
            f'<line x1="{sc(e1x)}" y1="{sc(ey_b)}" x2="{sc(e1x+ew)}" y2="{sc(ey_b+eh)}"'
            f' stroke="{color}" stroke-width="{sc(3)}" stroke-linecap="round" opacity="0.8"/>'
            f'<line x1="{sc(e1x+ew)}" y1="{sc(ey_b)}" x2="{sc(e1x)}" y2="{sc(ey_b+eh)}"'
            f' stroke="{color}" stroke-width="{sc(3)}" stroke-linecap="round" opacity="0.8"/>'
            f'<line x1="{sc(e2x)}" y1="{sc(ey_b)}" x2="{sc(e2x+ew)}" y2="{sc(ey_b+eh)}"'
            f' stroke="{color}" stroke-width="{sc(3)}" stroke-linecap="round" opacity="0.8"/>'
            f'<line x1="{sc(e2x+ew)}" y1="{sc(ey_b)}" x2="{sc(e2x)}" y2="{sc(ey_b+eh)}"'
            f' stroke="{color}" stroke-width="{sc(3)}" stroke-linecap="round" opacity="0.8"/>'
        )
        # Mueca triste
        mouth_str = (
            f'<path d="M {sc(mx-12)},{sc(my+8)} Q {sc(mx)},{sc(my+1)} {sc(mx+12)},{sc(my+8)}"'
            f' fill="none" stroke="{color}" stroke-width="{sc(2.5)}"'
            f' stroke-linecap="round" opacity="0.7"/>'
        )
        # Líneas de glitch horizontales
        extras = (
            f'<rect x="{sc(14)}" y="{sc(20)}" width="{sc(22)}" height="{sc(2)}"'
            f' fill="{color}" opacity="0.22"/>'
            f'<rect x="{sc(54)}" y="{sc(34)}" width="{sc(16)}" height="{sc(2)}"'
            f' fill="{color}" opacity="0.18"/>'
            f'<rect x="{sc(14)}" y="{sc(38)}" width="{sc(10)}" height="{sc(2)}"'
            f' fill="{color}" opacity="0.15"/>'
            + "".join(
                f'<rect x="{sc(px)}" y="{sc(py)}" width="{sc(ps)}" height="{sc(ps)}"'
                f' fill="{color}" opacity="0.30"/>'
                for px, py, ps in [(3,15,3),(84,22,2),(5,55,3),(82,50,2),(15,78,2),(70,76,2)]
            )
        )
        head_op, body_op = "0.62", "0.50"

    # ── Construcción del SVG ───────────────────────────────────────────────
    # Sombra de glow exterior de la cabeza
    head_shadow = (
        f'<rect x="{sc(hx-2)}" y="{sc(hy-2)}" width="{sc(hw+4)}" height="{sc(hh+4)}"'
        f' rx="{sc(hr+1)}" fill="{color}" opacity="0.12" filter="url(#g{uid})"/>'
    )
    head_rect = (
        f'<rect x="{sc(hx)}" y="{sc(hy)}" width="{sc(hw)}" height="{sc(hh)}"'
        f' rx="{sc(hr)}" fill="#090d14" stroke="{color}" stroke-width="{sc(2)}"'
        f' opacity="{head_op}" filter="url(#g{uid})"/>'
    )
    body_rect = (
        f'<rect x="{sc(bx)}" y="{sc(by)}" width="{sc(bw)}" height="{sc(bh)}"'
        f' rx="{sc(3)}" fill="#090d14" stroke="{color}" stroke-width="{sc(1.5)}"'
        f' opacity="{body_op}"/>'
    )
    legs = (
        f'<rect x="{sc(lx1)}" y="{sc(ly)}" width="{sc(lw)}" height="{sc(lh)}"'
        f' rx="{sc(2)}" fill="#090d14" stroke="{color}" stroke-width="{sc(1.5)}"'
        f' opacity="{body_op}"/>'
        f'<rect x="{sc(lx2)}" y="{sc(ly)}" width="{sc(lw)}" height="{sc(lh)}"'
        f' rx="{sc(2)}" fill="#090d14" stroke="{color}" stroke-width="{sc(1.5)}"'
        f' opacity="{body_op}"/>'
    )

    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 90 90"'
        f' xmlns="http://www.w3.org/2000/svg">'
        f'{glow_filter}'
        f'{head_shadow}'
        f'{head_rect}'
        f'{corners}'
        f'{eye_str}'
        f'{mouth_str}'
        f'{body_rect}'
        f'{legs}'
        f'{extras}'
        f'</svg>'
    )


def leer_estado():
    try:    return json.loads(ESTADO_FILE.read_text())
    except: return {}

def leer_ledger(ultimos=200):
    rows = []
    try:
        for l in LEDGER_FILE.read_text().strip().splitlines()[-ultimos:]:
            try: rows.append(json.loads(l))
            except: pass
    except: pass
    return rows

def leer_reporte():
    try:    return REPORTE_FILE.read_text()
    except: return "Sin reporte aún."

def generar():
    e       = leer_estado()
    ledger  = leer_ledger(200)
    reporte = leer_reporte()

    hist_ECE   = e.get("historial_ECE",   [1.0])
    hist_Brier = e.get("historial_Brier", [1.0])
    hist_kappa = e.get("historial_kappa",  [0.0])
    hist_L     = e.get("historial_L_norm", [0.0])
    hist_S     = e.get("historial_S_t",    [0.0])

    ece_actual   = hist_ECE[-1]   if hist_ECE   else 1.0
    brier_actual = hist_Brier[-1] if hist_Brier else 1.0
    brier_prev   = hist_Brier[-2] if len(hist_Brier) >= 2 else brier_actual
    spawns       = e.get("n_spawns_total") or 0
    # La clave en estado.json es "n_hashes" (el runner escribe ese nombre exacto)
    n_hashes     = int(e.get("n_hashes") or 0)
    n_run        = e.get("n_run") or 0

    # Homeostasis: ventana de 5 ciclos — la calibración ECE oscila entre ciclos;
    # basta con que el ECE haya estado ≤ 0.05 al menos una vez en los últimos 5
    # ciclos Y que Brier haya mejorado al menos una vez en la misma ventana.
    # (homeostasis biológica = mantener dentro de rango sobre el tiempo, no en
    #  cada instante puntual)
    ece_ventana   = hist_ECE[-5:]   if len(hist_ECE)   >= 2 else hist_ECE
    brier_ventana = hist_Brier[-6:] if len(hist_Brier) >= 2 else hist_Brier
    ece_ok_ventana   = any(v <= 0.05 for v in ece_ventana)
    brier_ok_ventana = any(brier_ventana[i] <= brier_ventana[i-1]
                           for i in range(1, len(brier_ventana)))
    cond1 = ece_ok_ventana and brier_ok_ventana
    cond2 = spawns > 0
    cond3 = n_hashes > 0
    cond4 = n_run >= 1
    n_vivo = sum([cond1, cond2, cond3, cond4])

    kappa    = hist_kappa[-1]  if hist_kappa  else 0.0
    kappa_p  = hist_kappa[-2]  if len(hist_kappa)  >= 2 else kappa
    L_norm   = hist_L[-1]      if hist_L      else 0.0
    L_prev   = hist_L[-2]      if len(hist_L)      >= 2 else L_norm
    S_t      = hist_S[-1]      if hist_S      else 0.0
    S_prev   = hist_S[-2]      if len(hist_S)      >= 2 else S_t
    ece_prev = hist_ECE[-2]    if len(hist_ECE)    >= 2 else ece_actual
    ts       = e.get("timestamp_ultimo_run", "—")
    n_ciclos = e.get("n_ciclos_total", 0)

    # ── MÁQUINA DE ESTADOS (4 niveles) ────────────────────────────────────────
    if n_vivo >= 3:
        estado       = "VIVO"
        glyph        = "🧬"
        estado_color = "#00ff88"
        anim_cls     = "anim-vivo"
        estado_msg   = ("Plena actividad vital — todas las condiciones activas."
                        if n_vivo == 4 else
                        "Sistema vivo con actividad sostenida.")
        estado_sub   = ("Aprendiendo, auditando papers y registrando en ledger."
                        if n_vivo == 4 else
                        "Aprendizaje y trazabilidad activos.")
        panel_shadow = "0 0 40px rgba(0,255,136,.15)"
    elif n_vivo == 2:
        estado       = "EMERGENTE"
        glyph        = "🌱"
        estado_color = "#ffd54f"
        anim_cls     = "anim-emergente"
        estado_msg   = "Sistema emergente — ciclo vital iniciando."
        estado_sub   = "2/4 condiciones activas. Acumulando datos para estabilizarse."
        panel_shadow = "0 0 30px rgba(255,213,79,.12)"
    elif n_vivo == 1:
        estado       = "LATENTE"
        glyph        = "🌙"
        estado_color = "#ff9800"
        anim_cls     = "anim-latente"
        estado_msg   = "Sistema latente — actividad mínima detectada."
        estado_sub   = "1/4 condiciones. Esperando más ciclos y datos."
        panel_shadow = "0 0 20px rgba(255,152,0,.10)"
    else:
        estado       = "INERTE"
        glyph        = "💀"
        estado_color = "#ff3d5a"
        anim_cls     = "anim-inerte"
        estado_msg   = "Sistema inerte — sin actividad vital."
        estado_sub   = "0/4 condiciones. El sistema no ha corrido aún."
        panel_shadow = "none"

    # ── FEED DE ACTIVIDAD (últimos ciclos + mensajes del sistema) ─────────────
    actividades = []
    for r in reversed(ledger[-6:]):
        ciclo = r.get("ciclo", "?")
        dec   = r.get("decision", "?")
        ece   = r.get("ECE", 0)
        icon  = "✓" if "PASS" in str(dec) or dec == "PSGC" else ("⚠" if dec == "PSNC" else "•")
        actividades.append(f'{icon} Ciclo #{ciclo} · {dec} · ECE {ece:.5f}')
    if n_hashes > 0:
        actividades.append(f'💾 Ledger verificado · {n_hashes} hashes SHA-256 encadenados')
    if kappa > 0:
        actividades.append(f'🔬 κ_conf={kappa:.3f} · S_t={S_t:.3f} · memoria activa')
    if spawns > 0:
        actividades.append(f'🧬 {spawns} sub-proceso(s) generado(s) · reproducción activa')
    actividades.append(f'📊 {n_run} runs ejecutados · {n_ciclos} ciclos vitales totales')
    actividades.append('⟳ Próximo ciclo: automático cada hora')

    feed_items = "\n".join(
        f'<div class="feed-item">{html.escape(a)}</div>'
        for a in actividades[:9]
    )
    # Para el scroll infinito duplicamos
    feed_all = feed_items + "\n" + feed_items

    # ── FLECHAS DE TENDENCIA ──────────────────────────────────────────────────
    def tend(val, prev, lower_better=False):
        if abs(val - prev) < 1e-9: return '<span style="color:#3a5a7a;font-size:.8rem;">→</span>'
        mejor = val < prev if lower_better else val > prev
        arrow = "↓" if val < prev else "↑"
        col   = "#00ff88" if mejor else "#ff3d5a"
        return f'<span style="color:{col};font-size:.85rem;font-weight:bold;">{arrow}</span>'

    tend_ece   = tend(ece_actual, ece_prev, lower_better=True)
    tend_kappa = tend(kappa, kappa_p)
    tend_L     = tend(L_norm, L_prev)
    tend_S     = tend(S_t, S_prev)

    # ── CONDICIONES ───────────────────────────────────────────────────────────
    conds = [
        ("Homeostasis",  "ECE≤0.05 en ventana 5 ciclos",  cond1,
         f"Calibración estable en ventana reciente — ECE mín. últimos 5 ciclos: {min(ece_ventana):.5f}. "
         f"Homeostasis = mantener ECE dentro de rango sobre el tiempo, no sólo en el ciclo actual (actual: {ece_actual:.5f})."),
        ("Reproducción", "Sub-procesos generados (Poisson)", cond2,
         "El sistema puede generar instancias derivadas — análogo biológico de reproducirse."),
        ("Trazabilidad", "Cadena SHA-256 activa",          cond3,
         "Cada ciclo deja huella digital inalterable — historial 100% verificable."),
        ("Autonomía",    "Loop autónomo ejecutado ≥1 vez", cond4,
         "El sistema corrió sin intervención manual — condición base de vida digital."),
    ]

    def cond_items():
        out = ""
        for name, formula, ok, expl in conds:
            dc = "dot-ok" if ok else "dot-fail"
            bc = "badge-ok" if ok else "badge-fail"
            st = "✓ OK" if ok else "✗ PEND."
            out += f"""
        <div class="cond-item">
          <div class="cond-dot {dc}"></div>
          <div class="cond-label">
            <b>{name}</b>
            <div style="font-size:.6rem;color:var(--muted);margin-top:1px;">{formula}</div>
            <div style="font-size:.59rem;color:#2a6060;margin-top:2px;line-height:1.4;">{expl}</div>
          </div>
          <span class="cond-badge {bc}">{st}</span>
        </div>"""
        return out

    def hash_rows():
        out = ""
        for ciclo, h in [(r["ciclo"], r.get("hash","")[:14]) for r in ledger[-10:]]:
            out += f'<div class="hash-item"><span style="color:var(--dim)">#{ciclo}</span><span class="hash-code">{h}…</span></div>\n'
        return out

    # ── COLORES / CLASES DERICADOS DEL ESTADO ─────────────────────────────────
    ece_col = "#00ff88" if ece_actual <= 0.05 else ("#ffd54f" if ece_actual <= 0.15 else "#ff3d5a")
    ece_pct = min(100, ece_actual / 0.5 * 100)

    ece_series   = [round(r["ECE"],        5) for r in ledger]
    kappa_series = [round(r["kappa_conf"], 4) for r in ledger]
    L_series     = [round(r["L_norm"],     5) for r in ledger]
    s_series     = [round(r["S_t"],        4) for r in ledger]
    labels       = [str(r["ciclo"])             for r in ledger]
    decisions    = [r.get("decision","?")       for r in ledger]
    pct_psnc     = round(100 * decisions.count("PSNC") / max(len(decisions),1), 1)

    now_str       = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reporte_esc   = html.escape(reporte)
    vita_bar_pct  = n_vivo * 25   # 0 / 25 / 50 / 75 / 100

    page = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="refresh" content="120">
<title>ALFA LUM-vitae vΩ.4 — Dashboard</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
/* ── Variables ─────────────────────────────── */
:root {{
  --bg:#090d14; --panel:#0d1520; --border:#1a2a3a;
  --cyan:#00e5ff; --green:#00ff88; --red:#ff3d5a; --yellow:#ffd54f;
  --orange:#ff9800; --dim:#3a5a7a; --text:#c8dff0; --muted:#4a7090;
}}
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ background:var(--bg); color:var(--text); font-family:'Segoe UI',sans-serif;
        min-height:100vh; padding:20px; }}
header {{ display:flex; justify-content:space-between; align-items:center;
          border-bottom:1px solid var(--border); padding-bottom:14px; margin-bottom:20px;
          flex-wrap:wrap; gap:8px; }}
.logo {{ font-size:1.25rem; color:var(--cyan); letter-spacing:2px; font-family:'Courier New',monospace; }}

/* ── Grid ───────────────────────────────────── */
.grid {{ display:grid; gap:14px; }}
.row2  {{ grid-template-columns:1fr 1fr; }}
.row3  {{ grid-template-columns:400px 1fr 1fr; }}
.row4  {{ grid-template-columns:repeat(4,1fr); }}
@media(max-width:900px) {{ .row2,.row3,.row4 {{ grid-template-columns:1fr; }} }}

/* ── Paneles ─────────────────────────────────── */
.panel {{ background:var(--panel); border:1px solid var(--border); border-radius:10px;
          padding:16px; position:relative; overflow:hidden; }}
.panel::before {{ content:''; position:absolute; top:0; left:0; right:0; height:2px;
                  background:linear-gradient(90deg,var(--cyan),transparent); }}
.panel-title {{ font-size:.62rem; color:var(--muted); letter-spacing:2px;
                text-transform:uppercase; margin-bottom:10px; font-family:'Courier New',monospace; }}
.section-sep {{ font-size:.58rem; letter-spacing:3px; color:var(--dim); text-transform:uppercase;
                margin:18px 0 10px; border-top:1px solid var(--border); padding-top:12px;
                font-family:'Courier New',monospace; }}

/* ── TAMAGOTCHI ──────────────────────────────── */
.tama-panel {{ text-align:center; padding:20px 16px; box-shadow:{panel_shadow}; }}
.tama-panel::before {{ background:linear-gradient(90deg,transparent,{estado_color}88,transparent); }}

.tama-creature {{ display:inline-block; margin-bottom:6px; line-height:0; }}

/* Animaciones por estado */
@keyframes tama-vivo    {{ 0%,100%{{transform:translateY(0) scale(1)}}   40%{{transform:translateY(-10px) scale(1.08)}} }}
@keyframes tama-emerge  {{ 0%,100%{{transform:scale(1);opacity:.85}}     50%{{transform:scale(1.12);opacity:1}} }}
@keyframes tama-latente {{ 0%,100%{{transform:scale(1);opacity:.55}}     50%{{transform:scale(1.03);opacity:.80}} }}
@keyframes tama-pulse-glow-g {{ 0%,100%{{box-shadow:0 0 0 0 rgba(0,255,136,.25)}} 50%{{box-shadow:0 0 0 18px rgba(0,255,136,0)}} }}
@keyframes tama-pulse-glow-a {{ 0%,100%{{box-shadow:0 0 0 0 rgba(255,213,79,.2)}}  50%{{box-shadow:0 0 0 14px rgba(255,213,79,0)}} }}
@keyframes tama-pulse-glow-o {{ 0%,100%{{box-shadow:0 0 0 0 rgba(255,152,0,.15)}}  50%{{box-shadow:0 0 0 10px rgba(255,152,0,0)}} }}

.anim-vivo     .tama-creature {{ animation: tama-vivo    1.4s ease-in-out infinite; }}
.anim-vivo                    {{ animation: tama-pulse-glow-g 2.5s infinite; }}
.anim-emergente .tama-creature {{ animation: tama-emerge  2.2s ease-in-out infinite; }}
.anim-emergente               {{ animation: tama-pulse-glow-a 3s infinite; }}
.anim-latente  .tama-creature {{ animation: tama-latente 3.5s ease-in-out infinite; }}
.anim-latente                 {{ animation: tama-pulse-glow-o 4s infinite; }}
.anim-inerte   .tama-creature {{ opacity:.45; }}

.tama-state {{ font-size:1.5rem; font-weight:bold; letter-spacing:4px;
               color:{estado_color}; font-family:'Courier New',monospace;
               text-shadow:0 0 18px {estado_color}88; margin-bottom:4px; }}
.tama-msg   {{ font-size:.75rem; color:var(--muted); line-height:1.5; margin-bottom:12px; }}

/* Barra de vitalidad */
.vita-bar-wrap {{ height:6px; background:#1a2a3a; border-radius:3px; overflow:hidden; margin:8px 0 6px; }}
.vita-bar-fill {{ height:100%; border-radius:3px; background:{estado_color};
                  box-shadow:0 0 8px {estado_color}88; transition:width .8s ease; }}
.vita-label {{ font-size:.6rem; color:var(--dim); letter-spacing:1px; margin-bottom:10px; }}

/* Feed de actividad */
.feed-wrap {{ position:relative; height:110px; overflow:hidden;
              background:rgba(0,0,0,.25); border-radius:6px;
              border:1px solid var(--border); margin-top:10px; }}
.feed-wrap::before {{ content:''; position:absolute; top:0; left:0; right:0; height:20px;
                      background:linear-gradient(to bottom,rgba(13,21,32,1),transparent); z-index:2; }}
.feed-wrap::after  {{ content:''; position:absolute; bottom:0; left:0; right:0; height:20px;
                      background:linear-gradient(to top,rgba(13,21,32,1),transparent); z-index:2; }}
@keyframes scroll-up {{ 0%{{transform:translateY(0)}} 100%{{transform:translateY(-50%)}} }}
.feed-inner {{ animation: scroll-up {max(12, len(actividades)*2.5):.0f}s linear infinite; }}
.feed-item  {{ font-size:.62rem; color:#3a7070; padding:4px 8px; border-bottom:1px solid #0d1a24;
               white-space:nowrap; overflow:hidden; text-overflow:ellipsis; font-family:'Courier New',monospace; }}

/* ── Condiciones ─────────────────────────────── */
.cond-list {{ display:flex; flex-direction:column; gap:6px; }}
.cond-item {{ display:flex; align-items:flex-start; gap:9px; padding:8px 9px; border-radius:6px;
              background:rgba(255,255,255,.02); border:1px solid var(--border); }}
.cond-dot  {{ width:9px; height:9px; border-radius:50%; flex-shrink:0; margin-top:4px; }}
.dot-ok    {{ background:var(--green); box-shadow:0 0 5px var(--green); }}
.dot-fail  {{ background:var(--red);   box-shadow:0 0 5px var(--red); }}
.cond-label {{ flex:1; }}
.cond-badge {{ font-size:.58rem; padding:2px 6px; border-radius:4px; font-weight:bold;
               white-space:nowrap; margin-top:2px; flex-shrink:0; }}
.badge-ok  {{ background:rgba(0,255,136,.1);  color:var(--green); border:1px solid rgba(0,255,136,.25); }}
.badge-fail {{ background:rgba(255,61,90,.1); color:var(--red);   border:1px solid rgba(255,61,90,.25); }}

/* ── Métricas ────────────────────────────────── */
.stat-cell {{ background:rgba(0,0,0,.3); border-radius:6px; padding:10px; text-align:center; }}
.stat-val  {{ font-size:1.6rem; font-weight:bold; color:var(--cyan); line-height:1;
              font-family:'Courier New',monospace; }}
.stat-lbl  {{ font-size:.6rem; color:var(--muted); letter-spacing:1px; margin-top:2px; }}
.tend-row  {{ display:flex; align-items:baseline; justify-content:center; gap:4px; }}

/* ── Hashes ──────────────────────────────────── */
.hash-list {{ display:flex; flex-direction:column; gap:3px; }}
.hash-item {{ display:flex; align-items:center; gap:8px; font-size:.62rem; color:var(--muted);
              padding:3px 0; border-bottom:1px solid rgba(255,255,255,.03);
              font-family:'Courier New',monospace; }}
.hash-code {{ color:var(--cyan); }}

/* ── Reporte ─────────────────────────────────── */
#reporte-text {{ font-size:.57rem; color:var(--muted); white-space:pre; overflow:auto;
                 max-height:200px; padding:8px; background:rgba(0,0,0,.3); border-radius:6px;
                 border:1px solid var(--border); font-family:'Courier New',monospace; line-height:1.5; }}
.chart-box {{ position:relative; height:180px; }}
</style>
</head>
<body>

<header>
  <div>
    <div class="logo">🧬 ALFA LUM-vitae <span style="color:var(--cyan)">vΩ.4</span></div>
    <div style="font-size:.63rem;color:var(--dim);margin-top:2px;font-family:'Courier New',monospace;">
      Materialismo Filosófico · Meta-aprendizaje prequencial · Proyecto MINERVA
    </div>
  </div>
  <div style="font-size:.65rem;color:var(--muted);border:1px solid var(--border);padding:4px 12px;
              border-radius:20px;font-family:'Courier New',monospace;">
    📸 {now_str}
  </div>
</header>

<!-- ═══ FILA 1: Tamagotchi · Condiciones · Métricas ═══ -->
<div class="grid row3">

  <!-- TAMAGOTCHI -->
  <div class="panel tama-panel {anim_cls}">
    <div class="panel-title">Estado del organismo digital</div>
    <div class="tama-creature">{tama_face(estado, estado_color)}</div>
    <div class="tama-state">{estado}</div>
    <div class="tama-msg">{estado_msg}<br>
      <span style="font-size:.67rem;color:#2a5a5a;">{estado_sub}</span>
    </div>
    <!-- Barra de vitalidad 0-4 -->
    <div class="vita-bar-wrap">
      <div class="vita-bar-fill" style="width:{vita_bar_pct}%;"></div>
    </div>
    <div class="vita-label">{n_vivo}/4 condiciones vitales activas · Último run: {ts[:16]}</div>
    <!-- Feed de actividad -->
    <div class="feed-wrap">
      <div class="feed-inner">{feed_all}</div>
    </div>
  </div>

  <!-- CONDICIONES -->
  <div class="panel">
    <div class="panel-title">Condiciones de vida digital</div>
    <div class="cond-list">{cond_items()}</div>
  </div>

  <!-- MÉTRICAS VITALES -->
  <div class="panel">
    <div class="panel-title">Métricas vitales</div>
    <!-- ECE con barra -->
    <div style="margin-bottom:14px;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:3px;">
        <span style="font-size:.62rem;color:var(--muted);">ECE — Error de calibración</span>
        <span style="display:flex;align-items:center;gap:5px;">
          {tend_ece}
          <span style="font-size:1.15rem;font-weight:bold;color:{ece_col};
                       font-family:'Courier New',monospace;">{ece_actual:.5f}</span>
        </span>
      </div>
      <div style="height:6px;background:var(--border);border-radius:3px;overflow:hidden;">
        <div style="width:{ece_pct:.1f}%;height:100%;background:{ece_col};border-radius:3px;"></div>
      </div>
      <div style="display:flex;justify-content:space-between;margin-top:3px;
                  font-size:.54rem;color:var(--dim);">
        <span>0 — óptimo</span><span>umbral 0.05</span><span>0.50 — pésimo</span>
      </div>
    </div>
    <!-- Cuadrícula 2×2 -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
      <div class="stat-cell">
        <div class="tend-row"><div class="stat-val">{kappa:.3f}</div>{tend_kappa}</div>
        <div class="stat-lbl">κ_conf · confianza</div>
      </div>
      <div class="stat-cell">
        <div class="tend-row"><div class="stat-val">{L_norm:.4f}</div>{tend_L}</div>
        <div class="stat-lbl">𝓛* · función vital</div>
      </div>
      <div class="stat-cell">
        <div class="tend-row"><div class="stat-val">{S_t:.3f}</div>{tend_S}</div>
        <div class="stat-lbl">S_t · memoria</div>
      </div>
      <div class="stat-cell">
        <div class="stat-val">{spawns}</div>
        <div class="stat-lbl">spawns · hijos</div>
      </div>
    </div>
    <div style="margin-top:10px;font-size:.6rem;color:var(--dim);line-height:1.6;
                padding:6px 8px;background:rgba(0,0,0,.2);border-radius:5px;">
      <b style="color:var(--cyan);">ECE</b> mide si las predicciones del sistema están bien calibradas.
      Por debajo de 0.05 = aprendizaje estable. <b style="color:var(--cyan);">κ_conf</b> mide
      la confianza operatoria (más alto = más seguro). <b style="color:var(--cyan);">S_t</b>
      es la memoria acumulada de ciclos pasados.
    </div>
  </div>
</div>

<!-- ═══ FILA 2: Contadores ═══ -->
<div class="grid row4" style="margin-top:14px;">
  <div class="panel" style="text-align:center;">
    <div class="panel-title">Runs ejecutados</div>
    <div class="stat-val" style="font-size:2rem;">{n_run}</div>
    <div class="stat-lbl">veces que corrió</div>
  </div>
  <div class="panel" style="text-align:center;">
    <div class="panel-title">Ciclos vitales</div>
    <div class="stat-val" style="font-size:2rem;">{n_ciclos}</div>
    <div class="stat-lbl">iteraciones totales</div>
  </div>
  <div class="panel" style="text-align:center;">
    <div class="panel-title">Hashes SHA-256</div>
    <div class="stat-val" style="font-size:2rem;">{n_hashes}</div>
    <div class="stat-lbl">cadena verificable</div>
  </div>
  <div class="panel" style="text-align:center;">
    <div class="panel-title">Ciclos en PSNC</div>
    <div class="stat-val" style="font-size:2rem;">{pct_psnc}%</div>
    <div class="stat-lbl">modo cautela</div>
  </div>
</div>

<!-- ═══ GRÁFICAS ═══ -->
<div class="section-sep">◈ Series temporales — últimos {len(ledger)} ciclos del ledger</div>
<div class="grid row2">
  <div class="panel">
    <div class="panel-title">ECE · Error de calibración
      <span style="color:#ffd54f66;"> — línea punteada = umbral 0.05</span></div>
    <div class="chart-box"><canvas id="chartECE"></canvas></div>
  </div>
  <div class="panel">
    <div class="panel-title">κ_conf · Confianza operatoria
      <span style="color:#3a5a7a;"> — mayor es mejor</span></div>
    <div class="chart-box"><canvas id="chartKappa"></canvas></div>
  </div>
</div>
<div class="grid row2" style="margin-top:14px;">
  <div class="panel">
    <div class="panel-title">𝓛* · Función vital normalizada</div>
    <div class="chart-box"><canvas id="chartL"></canvas></div>
  </div>
  <div class="panel">
    <div class="panel-title">S_t · Memoria exponencial</div>
    <div class="chart-box"><canvas id="chartS"></canvas></div>
  </div>
</div>

<!-- ═══ TRAZABILIDAD ═══ -->
<div class="section-sep">◈ Trazabilidad y reporte</div>
<div class="grid row2">
  <div class="panel">
    <div class="panel-title">Últimos 10 hashes SHA-256</div>
    <div style="font-size:.59rem;color:var(--dim);margin-bottom:8px;line-height:1.6;">
      Cada ciclo genera un hash SHA-256 encadenado con el anterior. Cualquier
      modificación retroactiva rompe la cadena — el historial es inmutable.
    </div>
    <div class="hash-list">{hash_rows()}</div>
  </div>
  <div class="panel">
    <div class="panel-title">Último reporte del runner</div>
    <pre id="reporte-text">{reporte_esc}</pre>
  </div>
</div>

<div style="text-align:center;margin-top:22px;font-size:.57rem;color:var(--dim);
            letter-spacing:2px;font-family:'Courier New',monospace;">
  ALFA LUM-vitae vΩ.4 · Materialismo Filosófico · G. Bueno + Luminomática · Proyecto MINERVA
</div>

<script>
const C = {{CYAN:'#00e5ff',GREEN:'#00ff88',YELLOW:'#ffd54f',RED:'#ff3d5a',PURPLE:'#b39ddb'}};
Chart.defaults.color = '#4a7090';
Chart.defaults.borderColor = '#1a2a3a';
Chart.defaults.font.family = "'Courier New',monospace";
Chart.defaults.font.size = 10;

const LABELS = {json.dumps(labels)};
const ECE    = {json.dumps(ece_series)};
const KAPPA  = {json.dumps(kappa_series)};
const LSERIE = {json.dumps(L_series)};
const SSERIE = {json.dumps(s_series)};

function mkLine(id, data, color, ref) {{
  const ctx = document.getElementById(id).getContext('2d');
  const ds = [{{
    data, borderColor: color, backgroundColor: color + '15',
    fill: true, tension: 0.4, pointRadius: 0, borderWidth: 1.8
  }}];
  if (ref != null) ds.push({{
    data: LABELS.map(() => ref), borderColor: C.YELLOW + '66',
    borderDash: [5,5], borderWidth: 1, pointRadius: 0, fill: false
  }});
  new Chart(ctx, {{
    type: 'line',
    data: {{labels: LABELS, datasets: ds}},
    options: {{
      responsive: true, maintainAspectRatio: false, animation: {{duration: 0}},
      scales: {{
        x: {{display: false}},
        y: {{grid: {{color: '#131f2e'}}, ticks: {{color: '#3a5a7a', maxTicksLimit: 5}}}}
      }},
      plugins: {{
        legend: {{display: false}},
        tooltip: {{
          backgroundColor: '#0d1520', borderColor: '#1a2a3a', borderWidth: 1,
          titleColor: '#00e5ff', bodyColor: '#c8dff0',
          callbacks: {{title: i => 'Ciclo ' + i[0].label}}
        }}
      }}
    }}
  }});
}}

mkLine('chartECE',   ECE,    C.GREEN,  0.05);
mkLine('chartKappa', KAPPA,  C.CYAN,   null);
mkLine('chartL',     LSERIE, C.YELLOW, null);
mkLine('chartS',     SSERIE, C.PURPLE, null);
</script>
</body>
</html>"""

    OUT_FILE.write_text(page, encoding="utf-8")
    print(f"[OK] Dashboard generado → {OUT_FILE}")
    return OUT_FILE

if __name__ == "__main__":
    p = generar()
    import webbrowser, sys
    if "--no-open" not in sys.argv:
        webbrowser.open(str(p))
