#!/usr/bin/env python3
"""
ALFA LUM-vitae vΩ.4 — Generador de Dashboard HTML
Crea lum_vitae_dashboard.html con datos actuales embebidos.
Se puede abrir directamente en cualquier navegador (doble clic).
"""
import json, pathlib, datetime, html

BASE            = pathlib.Path(__file__).parent
ESTADO_FILE     = BASE / "lum_vitae_estado.json"
LEDGER_FILE     = BASE / "lum_vitae_ledger_meta.ndjson"
REPORTE_FILE    = BASE / "lum_vitae_reporte.txt"
OUT_FILE        = BASE / "lum_vitae_dashboard.html"
HISTORIAL_FILE          = BASE / "lum_minerva_historial.json"
CLASICOS_FILE           = BASE / "lum_clasicos_cierres.json"
CLASICOS_HISTORIAL_FILE = BASE / "lum_clasicos_historial.json"

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

    # ── MINERVA — datos del mapa de cierres categoriales ──────────────────────
    MAPA_FILE    = BASE / "lum_mapa_cierres.json"
    minerva_mapa = {}
    minerva_ts   = "—"
    try:
        _md = json.loads(MAPA_FILE.read_text())
        minerva_mapa = _md.get("mapa", {})
        _ts_raw = (_md.get("resumen") or {}).get("timestamp", "") or ""
        minerva_ts = _ts_raw[:16].replace("T", " ") if _ts_raw else "—"
    except Exception:
        pass

    # ── MINERVA — historial persistente de búsquedas ───────────────────────────
    minerva_historial = []
    try:
        if HISTORIAL_FILE.exists():
            _hd = json.loads(HISTORIAL_FILE.read_text())
            minerva_historial = _hd.get("historial", [])
    except Exception:
        pass

    # ── CLÁSICOS — corpus de obras fundacionales analizadas con TCC ─────────────
    clasicos_data = {}
    try:
        if CLASICOS_FILE.exists():
            _cd = json.loads(CLASICOS_FILE.read_text())
            clasicos_data = _cd.get("clasicos", {})
    except Exception:
        pass

    # ── CLÁSICOS — historial de verificaciones SS ─────────────────────────────
    clasicos_historial = []
    try:
        if CLASICOS_HISTORIAL_FILE.exists():
            clasicos_historial = json.loads(
                CLASICOS_HISTORIAL_FILE.read_text()
            ).get("historial", [])
    except Exception:
        pass

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

    def minerva_cards():
        """Tarjetas de los 6 dominios de cierre categorial — datos de lum_mapa_cierres.json."""
        DISC_META = {
            "FORM":    ("∑", "#00e5ff", "Ciencias Formales",
                        "Matemáticas, Lógica, Estadística",
                        "mathematical+closure+axiomatization+completeness"),
            "NAT":     ("⚛", "#00ff88", "Ciencias Naturales",
                        "Física, Química, Biología, Neurociencia",
                        "natural+science+causal+closure+empirical+laws"),
            "TEC":     ("⚙", "#b39ddb", "Ingeniería & IA",
                        "Informática, Cibernética, Inteligencia Artificial",
                        "cybernetics+feedback+closure+formal+verification"),
            "SOC_IV":  ("◈", "#ffd54f", "Cs. Sociales Interpret.",
                        "Psicología, Sociología, Economía",
                        "social+science+operationalization+construct+validity"),
            "SOC_DID": ("⏳", "#ff9800", "Cs. Sociales Diacrónicas",
                        "Historia, Antropología, Arqueología",
                        "historical+method+scientific+demarcation+historiography"),
            "ARTE":    ("🎨", "#f48fb1", "Arte & Estética",
                        "Pintura, Música, Literatura, Arquitectura",
                        "aesthetic+closure+art+theory+pictorial+materialist"),
        }
        if not minerva_mapa:
            return '<div style="color:var(--dim);font-size:.62rem;padding:10px;">Sin datos MINERVA — ejecuta python3 lum_mapa_cierres.py para generar el mapa.</div>'
        out = ""
        for key, (icon, color, name, subcampos, q) in DISC_META.items():
            d   = minerva_mapa.get(key, {})
            lum = d.get("lum_pe", {})
            p   = lum.get("p_media", 0.0)
            state = lum.get("state_lum", "?")
            n_c = lum.get("n_campos", 0)
            ss_n = (d.get("semanticscholar") or {}).get("n_papers", 0)
            pct = int(round(p * 100))
            bar_col = "#00ff88" if p >= 0.70 else ("#ffd54f" if p >= 0.40 else "#ff3d5a")
            state_label = state if state not in ("?", "N/A") else (
                "VERDE ≥70%" if p >= 0.70 else ("ÁMBAR ≥40%" if p >= 0.40 else "ROJO <40%"))
            ss_url  = f"https://www.semanticscholar.org/search?q={q}&sort=Relevance"
            phi_url = f"https://philpapers.org/s/{q.replace('+', '%20')[:50]}"
            out += f"""<div id="mc-{key}" style="background:rgba(0,0,0,.3);border:1px solid {color}22;border-radius:6px;padding:9px;position:relative;">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
    <span style="color:{color};font-size:.70rem;font-weight:bold;">{icon} {name}</span>
    <span id="mc-state-{key}" style="font-size:.55rem;color:{bar_col};background:rgba(0,0,0,.5);padding:1px 6px;border-radius:3px;">{state_label}</span>
  </div>
  <div style="font-size:.54rem;color:var(--dim);margin-bottom:5px;">{subcampos}</div>
  <div style="height:4px;background:#1a2a3a;border-radius:3px;overflow:hidden;margin-bottom:5px;">
    <div style="width:{pct}%;height:100%;background:{bar_col};border-radius:3px;"></div>
  </div>
  <div style="display:flex;justify-content:space-between;align-items:center;font-size:.55rem;color:var(--dim);">
    <span>p_cierre LUM-PE={p:.3f} · {n_c} campos · <span id="mc-n-{key}">{ss_n} papers SS</span></span>
    <span>
      <a href="{ss_url}" target="_blank" style="color:{color}88;text-decoration:none;margin-right:6px;" title="Buscar en Semantic Scholar">SS↗</a>
      <a href="{phi_url}" target="_blank" style="color:{color}88;text-decoration:none;" title="Buscar en PhilPapers">Phil↗</a>
    </span>
  </div>
</div>\n"""
        return out

    def clasicos_historial_panel():
        """Panel de historial de verificaciones SS para la sección Clásicos."""
        if not clasicos_historial:
            return ('<div id="cl-historial-panel">'
                    '<div style="color:var(--dim);font-size:.6rem;padding:6px 0;">'
                    'Sin verificaciones registradas — usa el botón '
                    '<b style="color:#ffd54f">📚 Verificar en SS</b> para registrar la primera.'
                    '</div></div>')

        entradas = list(reversed(clasicos_historial))
        VISIBLE  = 3

        def entrada_html(idx, en, hidden=False):
            ts     = en.get("timestamp", "")[:16].replace("T", " ") + " UTC"
            total  = en.get("total_papers", 0)
            obras  = en.get("obras", {})
            obras_html = ""
            for key, info in list(obras.items())[:8]:   # max 8 obras visibles por entrada
                n   = info.get("n_papers", 0)
                col = "#00ff88" if n >= 3 else ("#ffd54f" if n > 0 else "#3a5a7a")
                lbl = (key.replace("_", " ").replace("EUCLID ELEMENTOS", "Euclides")
                          .replace("NEWTON PRINCIPIA", "Newton")
                          .replace("BUENO TCC", "Bueno TCC")
                          .replace("DARWIN ORIGEN", "Darwin")
                          .replace("HEGEL FENOMENOLOGIA", "Hegel")
                          .replace("FREUD SUENOS", "Freud")[:18])
                obras_html += (
                    f'<span title="{key} · {n} papers SS" '
                    f'style="display:inline-block;padding:2px 5px;border-radius:3px;'
                    f'border:1px solid {col}44;background:{col}11;color:{col};'
                    f'font-size:.52rem;margin:2px;">{lbl} {n}p</span>'
                )
            n_mas = max(0, len(obras) - 8)
            if n_mas:
                obras_html += (f'<span style="font-size:.52rem;color:var(--dim);">+{n_mas} más</span>')
            vis = 'style="display:none;"' if hidden else ''
            return (
                f'<div class="cl-hist-entry" {vis} style="padding:7px 9px;margin-bottom:5px;'
                f'border:1px solid #ffd54f22;border-radius:5px;background:rgba(255,213,79,.03);">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">'
                f'<span style="font-size:.57rem;color:var(--dim);">{ts}</span>'
                f'<span style="font-size:.54rem;color:#ffd54f88;">📚 SS · {total} papers</span>'
                f'</div>'
                f'<div>{obras_html}</div>'
                f'</div>'
            )

        items_html = ""
        for i, en in enumerate(entradas):
            items_html += entrada_html(i, en, hidden=(i >= VISIBLE))

        n_hidden = max(0, len(entradas) - VISIBLE)
        ver_mas_btn = ""
        if n_hidden > 0:
            ver_mas_btn = (
                f'<button id="btn-cl-historial-mas" onclick="toggleClHistorial()" '
                f'style="background:none;border:1px solid #ffd54f33;color:var(--dim);'
                f'font-size:.6rem;padding:4px 12px;border-radius:4px;cursor:pointer;'
                f'font-family:\'Courier New\',monospace;margin-top:4px;">'
                f'▼ Ver {n_hidden} más ({len(entradas)} total)</button>'
            )

        return f'''<div id="cl-historial-panel">
{items_html}{ver_mas_btn}
</div>
<script>
function toggleClHistorial() {{
  const entries = document.querySelectorAll('.cl-hist-entry');
  const btn = document.getElementById('btn-cl-historial-mas');
  let anyHidden = false;
  entries.forEach(function(el, i) {{
    if (i >= {VISIBLE}) {{
      if (el.style.display === 'none') {{ el.style.display = ''; anyHidden = true; }}
    }}
  }});
  if (!anyHidden) {{
    entries.forEach(function(el, i) {{ if (i >= {VISIBLE}) el.style.display = 'none'; }});
    if (btn) btn.textContent = '▼ Ver {n_hidden} más ({len(entradas)} total)';
  }} else {{
    if (btn) btn.textContent = '▲ Mostrar menos';
  }}
}}
</script>'''

    def clasicos_cards():
        """Tarjetas de obras clásicas analizadas con TCC — Corpus Fundacional."""
        SEM_COL  = {"GREEN": "#00ff88", "AMBER": "#ffd54f", "RED": "#ff3d5a"}
        SEM_ICON = {"GREEN": "🟢", "AMBER": "🟡", "RED": "🔴"}
        DOM_COL  = {"FORM": "#00e5ff", "NAT": "#00ff88", "TEC": "#b39ddb",
                    "SOC_IV": "#ffd54f", "SOC_DID": "#ff9800", "ARTE": "#f48fb1"}
        DOM_NAME = {"FORM": "Formal", "NAT": "Natural", "TEC": "Técnica",
                    "SOC_IV": "Social-IV", "SOC_DID": "Social-Diacr.", "ARTE": "Arte"}
        ORDER    = ["GREEN", "AMBER", "RED"]

        if not clasicos_data:
            return ('<div style="color:var(--dim);font-size:.62rem;padding:10px;">'
                    'Sin datos de clásicos — ejecuta <code>python3 lum_mapa_cierres.py --html-only</code>'
                    '</div>')

        # Ordenar: verde → ámbar → rojo, dentro de cada grupo por p_sintetico desc
        def sort_key(item):
            sem = item[1].get("semaforo", "RED")
            return (ORDER.index(sem), -item[1].get("p_sintetico", 0))

        entries = sorted(clasicos_data.items(), key=sort_key)
        out = ""
        for key, cl in entries:
            sem   = cl.get("semaforo", "RED")
            p     = cl.get("p_sintetico", 0.0)
            col   = SEM_COL.get(sem, "#9e9e9e")
            dom   = cl.get("dominio", "FORM")
            dcol  = DOM_COL.get(dom, "#9e9e9e")
            dname = DOM_NAME.get(dom, dom)
            pct   = int(round(p * 100))
            icon  = cl.get("icono", "◈")
            titulo = html.escape(cl.get("titulo", ""))
            autor  = html.escape(cl.get("autor", ""))
            anio   = html.escape(cl.get("anio", ""))
            desc   = html.escape(cl.get("descripcion", ""))
            tipo   = html.escape(cl.get("tipo_cierre", ""))
            bueno  = html.escape(cl.get("bueno_ref", ""))
            out += f"""<div style="background:rgba(0,0,0,.32);border:1px solid {col}28;
  border-radius:7px;padding:10px 11px;display:flex;flex-direction:column;gap:5px;
  transition:border-color .2s;" onmouseover="this.style.borderColor='{col}66'"
  onmouseout="this.style.borderColor='{col}28'">
  <!-- Header: icono + título + semáforo -->
  <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:6px;">
    <div style="display:flex;align-items:center;gap:6px;flex:1;min-width:0;">
      <span style="color:{col};font-size:.85rem;flex-shrink:0;">{icon}</span>
      <div style="min-width:0;">
        <div style="font-size:.64rem;font-weight:bold;color:{col};white-space:nowrap;
                    overflow:hidden;text-overflow:ellipsis;">{titulo}</div>
        <div style="font-size:.54rem;color:var(--dim);">{autor} · {anio}</div>
      </div>
    </div>
    <div style="display:flex;flex-direction:column;align-items:flex-end;gap:2px;flex-shrink:0;">
      <span style="font-size:.54rem;background:{col}20;color:{col};
                   border:1px solid {col}44;border-radius:3px;padding:1px 6px;
                   font-weight:bold;">{SEM_ICON.get(sem,'')} {sem}</span>
      <span style="font-size:.50rem;color:{dcol};background:{dcol}15;
                   border-radius:2px;padding:1px 5px;">{dname}</span>
    </div>
  </div>
  <!-- Barra de cierre + badge SS -->
  <div style="display:flex;align-items:center;gap:7px;">
    <div style="flex:1;height:4px;background:#1a2a3a;border-radius:3px;overflow:hidden;">
      <div style="width:{pct}%;height:100%;background:{col};border-radius:3px;"></div>
    </div>
    <span style="font-size:.58rem;color:{col};font-family:'Courier New',monospace;
                 flex-shrink:0;">p={p:.2f}</span>
    <span id="cl-badge-{key}" style="font-size:.50rem;color:#3a5a7a;flex-shrink:0;
          font-family:'Courier New',monospace;" title="Pulsa Verificar en SS para buscar">—</span>
  </div>
  <!-- Descripción + tipo de cierre -->
  <div style="font-size:.56rem;color:var(--dim);line-height:1.55;">{desc}</div>
  <div style="font-size:.53rem;color:{col}99;font-style:italic;border-top:1px solid {col}18;
              padding-top:4px;line-height:1.5;">⊢ {tipo}</div>
  <!-- Referencia Bueno (tooltip-like) -->
  <div style="font-size:.51rem;color:#3a6a8a;line-height:1.4;border-top:1px solid #1a3a5a;
              padding-top:4px;">◈ {bueno}</div>
</div>\n"""
        return out

    def clasicos_legend():
        """Leyenda de la sección clásicos con resumen de distribución GREEN/AMBER/RED."""
        counts = {"GREEN": 0, "AMBER": 0, "RED": 0}
        for cl in clasicos_data.values():
            s = cl.get("semaforo", "RED")
            counts[s] = counts.get(s, 0) + 1
        total = sum(counts.values())
        col   = {"GREEN": "#00ff88", "AMBER": "#ffd54f", "RED": "#ff3d5a"}
        lbl   = {"GREEN": "\U0001f7e2 Verde", "AMBER": "\U0001f7e1 \xc1mbar", "RED": "\U0001f534 Rojo"}
        parts = "".join(
            f'<span style="color:{col[s]};font-size:.6rem;">'
            f'{lbl.get(s, s)}: {n} '
            f'({int(n/total*100) if total else 0}%)</span>'
            for s, n in counts.items() if n > 0
        )
        return (f'<div style="display:flex;gap:14px;flex-wrap:wrap;align-items:center;">'
                f'{parts}'
                f'<span style="color:var(--dim);font-size:.55rem;">· {total} obras analizadas '
                f'con la TCC · Bueno 1992–1993</span>'
                f'</div>')

    def repo_links():
        """Panel de repositorios registrados del proyecto."""
        repos = [
            ("GitHub",          "https://github.com/julespintor-tech/alfa-lum-vitae",
             "#00ff88",  "⌥", "Código fuente, issues, releases"),
            ("Zenodo DOI",      "https://doi.org/10.5281/zenodo.19235185",
             "#00e5ff",  "◎", "Registro DOI · v1.0.0 · LUM-vitae"),
            ("OSF",             "https://osf.io/5jhr4",
             "#b39ddb",  "⬡", "Proyecto abierto · archivos y documentación"),
            ("ORCID",           "https://orcid.org/0009-0001-0800-5303",
             "#ffd54f",  "✦", "Perfil investigador · Julio David Rojas A."),
            ("LUM-PE DOI",      "https://doi.org/10.5281/zenodo.19142481",
             "#ff9800",  "◈", "Dataset LUM-PE · fundamento teórico"),
        ]
        out = ""
        for name, url, color, icon, desc in repos:
            out += f"""<a href="{url}" target="_blank" style="display:flex;align-items:center;gap:10px;
  padding:8px 10px;border:1px solid {color}22;border-radius:6px;background:rgba(0,0,0,.2);
  text-decoration:none;color:inherit;transition:border-color .2s;"
  onmouseover="this.style.borderColor='{color}'" onmouseout="this.style.borderColor='{color}22'">
  <span style="color:{color};font-size:.85rem;">{icon}</span>
  <div style="flex:1;min-width:0;">
    <div style="font-size:.65rem;color:{color};font-weight:bold;">{name}</div>
    <div style="font-size:.55rem;color:var(--dim);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{desc}</div>
  </div>
  <span style="font-size:.65rem;color:{color}66;">↗</span>
</a>\n"""
        return out

    def historial_panel():
        """Panel de historial persistente de búsquedas MINERVA — embebido en HTML."""
        sem_color = {"GREEN":"#00ff88","AMBER":"#ffd54f","RED":"#ff3d5a","BLACK":"#9e9e9e","N/A":"#3a5a7a"}
        dom_color = {"FORM":"#00e5ff","NAT":"#00ff88","TEC":"#b39ddb",
                     "SOC_IV":"#ffd54f","SOC_DID":"#ff9800","ARTE":"#f48fb1"}

        if not minerva_historial:
            return ('<div id="minerva-historial-panel">'
                    '<div style="color:var(--dim);font-size:.6rem;padding:8px 0;">'
                    'Sin búsquedas registradas — ejecuta <code>python3 lum_mapa_cierres.py</code> '
                    'o usa el botón Buscar para registrar la primera.</div>'
                    '</div>')

        # Más reciente primero
        entradas = list(reversed(minerva_historial))
        VISIBLE = 3  # cuántas mostrar por defecto

        def entrada_html(idx, en, hidden=False):
            ts = (en.get("timestamp","")[:16].replace("T"," ") + " UTC")
            total = en.get("total_papers", 0)
            src   = en.get("source","?")
            src_label = "🔬 búsqueda completa" if src == "full_run" else "⚡ búsqueda live"
            dominios  = en.get("dominios", {})
            dom_html  = ""
            for dk, dv in dominios.items():
                c = dom_color.get(dk, "#9e9e9e")
                sc = sem_color.get(dv.get("semaforo","N/A"), "#9e9e9e")
                p  = dv.get("p_sintetico", 0)
                n  = dv.get("n_papers_ss", 0)
                sem = dv.get("semaforo","N/A")
                dot = "\u25cf" if sem == "GREEN" else ("\u25d1" if sem == "AMBER" else "\u25cb")
                dom_html += (
                    f'<span title="{dk} · p={p} · {n} papers" '
                    f'style="display:inline-block;padding:2px 6px;border-radius:3px;'
                    f'border:1px solid {c}44;background:{c}11;color:{c};'
                    f'font-size:.55rem;margin:2px;">'
                    f'{dk} <span style="color:{sc}">{dot}</span>'
                    f'</span>'
                )
            vis = 'style="display:none;"' if hidden else ''
            return (
                f'<div class="hist-entry" {vis} style="padding:8px 10px;margin-bottom:6px;'
                f'border:1px solid var(--border);border-radius:6px;background:rgba(0,0,0,.18);">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">'
                f'<span style="font-size:.58rem;color:var(--dim);">{ts}</span>'
                f'<span style="font-size:.55rem;color:var(--muted);">{src_label} · {total} papers</span>'
                f'</div>'
                f'<div>{dom_html}</div>'
                f'</div>'
            )

        items_html = ""
        for i, en in enumerate(entradas):
            items_html += entrada_html(i, en, hidden=(i >= VISIBLE))

        n_hidden = max(0, len(entradas) - VISIBLE)
        ver_mas_btn = ""
        if n_hidden > 0:
            ver_mas_btn = (
                f'<button id="btn-historial-mas" onclick="toggleHistorial()" '
                f'style="background:none;border:1px solid var(--border);color:var(--dim);'
                f'font-size:.6rem;padding:4px 12px;border-radius:4px;cursor:pointer;'
                f'font-family:\'Courier New\',monospace;margin-top:4px;">'
                f'▼ Ver {n_hidden} más ({len(entradas)} total)</button>'
            )

        return f'''<div id="minerva-historial-panel">
{items_html}{ver_mas_btn}
</div>
<script>
function toggleHistorial() {{
  const panel   = document.getElementById('minerva-historial-panel');
  const entries = panel ? panel.querySelectorAll('.hist-entry') : [];
  const btn     = document.getElementById('btn-historial-mas');
  let anyHidden = false;
  entries.forEach(function(el, i) {{
    if (i >= {VISIBLE}) {{
      if (el.style.display === 'none') {{ el.style.display = ''; anyHidden = true; }}
    }}
  }});
  if (!anyHidden) {{
    entries.forEach(function(el, i) {{ if (i >= {VISIBLE}) el.style.display = 'none'; }});
    if (btn) btn.textContent = '▼ Ver {n_hidden} más ({len(entradas)} total)';
  }} else {{
    if (btn) btn.textContent = '▲ Mostrar menos';
  }}
}}
</script>'''

    # ── COLORES / CLASES DERICADOS DEL ESTADO ─────────────────────────────────
    ece_min_ventana = min(ece_ventana) if ece_ventana else ece_actual
    ece_col = "#00ff88" if ece_actual <= 0.05 else ("#ffd54f" if ece_actual <= 0.15 else "#ff3d5a")
    ece_min_col = "#00ff88" if ece_min_ventana <= 0.05 else ("#ffd54f" if ece_min_ventana <= 0.15 else "#ff3d5a")
    ece_pct = min(100, ece_actual / 0.5 * 100)
    ece_homeo_ok = ece_ok_ventana   # bool — ya calculado arriba

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

    # ── Notas contextuales (subtítulos auto-explicativos para cada métrica) ───
    kappa_note = ("coherencia alta"   if kappa >= 0.6 else
                  ("coherencia media" if kappa >= 0.3 else "coherencia baja"))
    kappa_col2 = "#00ff88" if kappa >= 0.6 else ("#ffd54f" if kappa >= 0.3 else "#ff9800")
    L_note     = ("mejora activa"    if L_norm >= 0.05 else
                  ("delta pequeño"   if L_norm > 0    else "≈0 · estable entre ciclos"))
    L_col2     = "#00ff88" if L_norm >= 0.05 else ("#ffd54f" if L_norm > 0 else "#4a7090")
    St_note    = ("memoria excelente" if S_t >= 0.8 else
                  ("memoria buena"    if S_t >= 0.5 else "memoria debilitada"))
    St_col2    = "#00ff88" if S_t >= 0.8 else ("#ffd54f" if S_t >= 0.5 else "#ff9800")
    sp_note    = (f"{spawns} instancias derivadas generadas" if spawns > 0
                  else "reproducción aún no activada")
    sp_col2    = "#00ff88" if spawns > 0 else "#4a7090"

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
@media(max-width:700px) {{ .minerva-grid {{ grid-template-columns:1fr 1fr !important; }} }}
@media(max-width:480px) {{ .minerva-grid {{ grid-template-columns:1fr !important; }} }}
@media(max-width:700px) {{ #mtab-clasicos > div[style*="grid-template-columns:repeat(2"] {{ grid-template-columns:1fr !important; }} }}

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

/* ── Botón MINERVA live search ───────────────── */
@keyframes spin {{ to {{ transform:rotate(360deg); }} }}
#btn-minerva {{
  cursor:pointer; background:rgba(0,229,255,.08);
  border:1px solid rgba(0,229,255,.30); color:var(--cyan);
  font-size:.57rem; padding:5px 13px; border-radius:4px;
  font-family:'Courier New',monospace; letter-spacing:1px;
  transition:all .2s; white-space:nowrap; flex-shrink:0; }}
#btn-minerva:hover:not(:disabled) {{
  background:rgba(0,229,255,.20); border-color:var(--cyan);
  box-shadow:0 0 8px rgba(0,229,255,.2); }}
#btn-minerva:disabled {{ opacity:.45; cursor:not-allowed; }}
#minerva-status {{
  display:none; font-size:.58rem; color:var(--dim); padding:5px 10px;
  background:rgba(0,0,0,.3); border-radius:4px;
  border-left:2px solid rgba(0,229,255,.3); margin-bottom:8px; line-height:1.5; }}
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
    <!-- ECE con barra + contexto ventana -->
    <div style="margin-bottom:14px;"
         title="ECE oscila naturalmente entre ciclos PSNC (~0.15) y ciclos VIVO (~0.001).&#10;Lo que determina Homeostasis es el mínimo en ventana de 5 ciclos, no el valor actual.&#10;Ventana mín: {ece_min_ventana:.5f} · Homeostasis: {'OK' if ece_homeo_ok else 'NO OK'}">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:3px;">
        <div>
          <span style="font-size:.62rem;color:var(--muted);">ECE — Error de calibración</span>
        </div>
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
      <!-- Fila de contexto: ventana mín + estado Homeostasis -->
      <div style="display:flex;justify-content:space-between;align-items:center;
                  margin-top:5px;padding:4px 7px;background:rgba(0,0,0,.25);
                  border-radius:4px;border:1px solid var(--border);">
        <span style="font-size:.54rem;color:var(--dim);">
          ventana 5 ciclos mín:
          <b style="color:{ece_min_col};font-family:'Courier New',monospace;">
            {ece_min_ventana:.5f}
          </b>
        </span>
        <span style="font-size:.54rem;{'color:#00ff88;' if ece_homeo_ok else 'color:#ffd54f;'}font-weight:bold;">
          {'✓ Homeostasis OK' if ece_homeo_ok else '⚠ Homeostasis NO OK'}
        </span>
      </div>
      <div style="font-size:.52rem;color:#2a4a5a;margin-top:3px;line-height:1.5;">
        El ECE oscila entre ciclos PSNC (~0.15) y VIVO (~0.001) — esto es normal.
        Homeostasis se evalúa sobre la ventana, no sobre el ciclo actual.
      </div>
    </div>
    <!-- Cuadrícula 2×2 — métricas vitales con contexto auto-explicativo -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
      <div class="stat-cell" title="κ_conf — Coeficiente de coherencia operatoria&#10;Mide qué tan consistentes son las predicciones del modelo con los resultados observados.&#10;Calculado vía HSIC + peso ω + gap de calibración.&#10;Rango [0,1] — más alto = predicciones más coherentes.">
        <div class="tend-row"><div class="stat-val">{kappa:.3f}</div>{tend_kappa}</div>
        <div class="stat-lbl">κ_conf · coherencia</div>
        <div style="font-size:.54rem;color:{kappa_col2};margin-top:3px;">{kappa_note}</div>
      </div>
      <div class="stat-cell" title="𝓛* — Delta de mejora por ciclo (función vital normalizada)&#10;Cuánto mejoró el sistema en la última ventana de ciclos.&#10;0.0 entre ciclos activos es NORMAL — no significa que el sistema esté muerto.&#10;Valores > 0 indican mejora activa en curso.">
        <div class="tend-row"><div class="stat-val">{L_norm:.4f}</div>{tend_L}</div>
        <div class="stat-lbl">𝓛* · delta mejora</div>
        <div style="font-size:.54rem;color:{L_col2};margin-top:3px;">{L_note}</div>
      </div>
      <div class="stat-cell" title="S_t — Memoria exponencial de supervivencia (λ=0.90)&#10;Promedio ponderado exponencialmente del historial de ciclos 'VIVO'.&#10;Rango [0,1] — 1 = historial perfecto, 0 = sin historial vital.&#10;&gt; 0.8 excelente · 0.5–0.8 bueno · &lt; 0.5 bajo">
        <div class="tend-row"><div class="stat-val">{S_t:.3f}</div>{tend_S}</div>
        <div class="stat-lbl">S_t · memoria vital</div>
        <div style="font-size:.54rem;color:{St_col2};margin-top:3px;">{St_note}</div>
      </div>
      <div class="stat-cell" title="Spawns — Instancias derivadas generadas por reproducción Poisson&#10;Cuando el sistema detecta mejora sostenida (δ_hist &gt; 0.4),&#10;lanza copias derivadas de sí mismo — análogo digital de la reproducción biológica.&#10;Condición 2 de vida: reproducción con variación.">
        <div class="stat-val">{spawns}</div>
        <div class="stat-lbl">spawns · hijos</div>
        <div style="font-size:.54rem;color:{sp_col2};margin-top:3px;">{sp_note}</div>
      </div>
    </div>
    <div style="margin-top:10px;font-size:.6rem;color:var(--dim);line-height:1.7;
                padding:8px 10px;background:rgba(0,229,255,.04);border:1px solid rgba(0,229,255,.08);border-radius:5px;">
      <b style="color:var(--cyan);">Guía rápida de métricas</b> — Pasa el cursor sobre cada celda para definición completa.<br>
      <b style="color:var(--cyan);">ECE</b> &lt;0.05 = calibración estable (óptimo). &nbsp;
      <b style="color:var(--cyan);">κ_conf</b> &gt;0.6 = coherencia alta. &nbsp;
      <b style="color:var(--cyan);">𝓛*=0</b> entre ciclos es <i>normal</i> — el sistema no mejora todo el tiempo. &nbsp;
      <b style="color:var(--cyan);">S_t</b> &gt;0.8 = excelente historial de vida.
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
    <div class="panel-title">κ_conf · Coherencia operatoria
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

<!-- ═══ MINERVA — MAPA DE CIERRES CATEGORIALES ═══ -->
<div class="section-sep">◈ MINERVA — Cierre categorial · LUM-PE + Semantic Scholar · Corpus Fundacional</div>

<!-- ── Tab bar ─────────────────────────────────────────────────────────────── -->
<div id="minerva-tab-bar" style="display:flex;gap:0;margin-bottom:12px;
     border-bottom:1px solid rgba(0,229,255,.18);">
  <button id="mtab-btn-dominios" onclick="switchMinervaTab('dominios')"
    style="cursor:pointer;background:rgba(0,229,255,.14);border:1px solid rgba(0,229,255,.4);
           border-bottom:none;color:#00e5ff;font-size:.68rem;font-weight:bold;
           padding:6px 16px;border-radius:6px 6px 0 0;font-family:'Courier New',monospace;
           letter-spacing:.5px;margin-right:3px;transition:all .2s;">
    ◈ Dominios Científicos
  </button>
  <button id="mtab-btn-clasicos" onclick="switchMinervaTab('clasicos')"
    style="cursor:pointer;background:rgba(0,0,0,.2);border:1px solid rgba(255,213,79,.22);
           border-bottom:none;color:#ffd54f88;font-size:.68rem;font-weight:bold;
           padding:6px 16px;border-radius:6px 6px 0 0;font-family:'Courier New',monospace;
           letter-spacing:.5px;transition:all .2s;">
    ★ Clásicos Fundacionales
  </button>
</div>

<!-- ── Panel: Dominios Científicos ───────────────────────────────────────── -->
<div id="mtab-dominios">
  <div style="display:flex;justify-content:space-between;align-items:center;gap:10px;
              flex-wrap:wrap;margin-bottom:8px;">
    <div style="font-size:.58rem;color:var(--dim);line-height:1.8;flex:1;min-width:200px;">
      Audita 6 dominios de cierre categorial (Bueno α/β/γ). Barras = probabilidad LUM-PE.
      El botón consulta Semantic Scholar en vivo — sin novedades lo indica solo.
      Cooldown 60 s entre búsquedas. · Datos base: <span style="color:var(--cyan);">{minerva_ts}</span>
      &nbsp;·&nbsp;
      <a href="lum_mapa_cierres.html" style="color:var(--cyan);" target="_blank">Ver mapa completo →</a>
    </div>
    <button id="btn-minerva" onclick="buscarMinerva()" style="
      cursor:pointer;background:rgba(0,229,255,.12);border:1px solid rgba(0,229,255,.45);
      color:#00e5ff;font-size:.72rem;font-weight:bold;padding:7px 16px;border-radius:6px;
      font-family:'Courier New',monospace;letter-spacing:1px;white-space:nowrap;
      flex-shrink:0;transition:all .2s;">🔍 Buscar ahora</button>
  </div>
  <div id="minerva-status"></div>
  <div class="minerva-grid" style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:14px;">
{minerva_cards()}
  </div>
  <!-- Historial dentro del panel de dominios -->
  <div style="display:flex;justify-content:space-between;align-items:center;
              flex-wrap:wrap;gap:6px;margin-bottom:6px;">
    <div style="font-size:.6rem;color:var(--cyan);font-weight:bold;letter-spacing:.5px;">
      ◈ HISTORIAL · Búsquedas anteriores
    </div>
    <div style="display:flex;gap:6px;align-items:center;">
      <div style="font-size:.55rem;color:var(--dim);">Se actualiza al buscar o al ejecutar <code>lum_mapa_cierres.py</code></div>
      <button onclick="_exportHistorial(_LS_MINERVA,'Dominios','#00e5ff')"
        style="background:none;border:1px solid #00e5ff44;color:#00e5ff99;font-size:.55rem;
               padding:3px 9px;border-radius:4px;cursor:pointer;font-family:monospace;"
        title="Descargar historial completo como archivo HTML">📥 Exportar</button>
    </div>
  </div>
  {historial_panel()}
</div>

<!-- ── Panel: Clásicos Fundacionales ─────────────────────────────────────── -->
<div id="mtab-clasicos" style="display:none;">
  <!-- Encabezado -->
  <div style="display:flex;justify-content:space-between;align-items:center;
              flex-wrap:wrap;gap:8px;margin-bottom:10px;">
    <div style="font-size:.58rem;color:var(--dim);line-height:1.8;flex:1;min-width:200px;">
      Obras fundacionales analizadas con la TCC (Teoría del Cierre Categorial · Bueno 1992).
      p_sint = grado de cierre alcanzado · τ_verde ≥ 0.80 · τ_rojo &lt; 0.40
      &nbsp;·&nbsp; {clasicos_legend()}
    </div>
    <button id="btn-clasicos" onclick="buscarClasicos()" style="
      cursor:pointer;background:rgba(255,213,79,.10);border:1px solid rgba(255,213,79,.40);
      color:#ffd54f;font-size:.68rem;font-weight:bold;padding:7px 16px;border-radius:6px;
      font-family:'Courier New',monospace;letter-spacing:1px;white-space:nowrap;
      flex-shrink:0;transition:all .2s;">📚 Verificar en SS</button>
  </div>
  <div id="cl-status" style="display:none;margin-bottom:8px;padding:6px 10px;
       background:rgba(0,0,0,.3);border-left:3px solid rgba(255,213,79,.4);border-radius:4px;
       font-size:.6rem;"></div>
  <!-- Grid de clásicos — 2 columnas en pantalla grande -->
  <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:9px;margin-bottom:16px;
              grid-auto-rows:auto;">
{clasicos_cards()}
  </div>
  <!-- Nota epistemológica -->
  <div style="font-size:.54rem;color:var(--dim);line-height:1.7;
              border-top:1px solid var(--border);padding-top:8px;margin-top:4px;">
    <span style="color:var(--cyan);">◈ Nota metodológica:</span>
    Los scores no provienen de Semantic Scholar sino de la aplicación directa de la TCC
    (Bueno 1992–1993). Verde = cierre categorial completo verificado históricamente.
    Ámbar = cierre parcial o en construcción. Rojo = proto-cierre sin identidades sintéticas
    estables.
  </div>

  <!-- Historial de verificaciones SS para clásicos -->
  <div style="display:flex;justify-content:space-between;align-items:center;
              flex-wrap:wrap;gap:6px;margin-top:12px;margin-bottom:6px;">
    <div style="font-size:.6rem;color:#ffd54f;font-weight:bold;letter-spacing:.5px;">
      📚 HISTORIAL · Verificaciones Semantic Scholar
    </div>
    <div style="display:flex;gap:6px;align-items:center;">
      <div style="font-size:.55rem;color:var(--dim);">Se actualiza al usar el botón Verificar en SS</div>
      <button onclick="_exportHistorial(_LS_CLASICOS,'Clásicos','#ffd54f')"
        style="background:none;border:1px solid #ffd54f44;color:#ffd54f99;font-size:.55rem;
               padding:3px 9px;border-radius:4px;cursor:pointer;font-family:monospace;"
        title="Descargar historial completo como archivo HTML">📥 Exportar</button>
    </div>
  </div>
  {clasicos_historial_panel()}
</div>

<!-- ═══ REPOSITORIOS REGISTRADOS ═══ -->
<div class="section-sep">◈ Repositorios registrados · presencia verificable en la web</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:14px;">
  <div>
    <div style="font-size:.6rem;color:var(--dim);margin-bottom:7px;line-height:1.6;">
      El proyecto está registrado en múltiples repositorios con DOI permanente.
      Haz clic en cualquier enlace para verificar su presencia en línea.
    </div>
    <div style="display:flex;flex-direction:column;gap:6px;">
{repo_links()}
    </div>
  </div>
  <div style="background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:14px;">
    <div class="panel-title">Buscar en repositorios de papers</div>
    <div style="display:flex;flex-direction:column;gap:7px;margin-top:4px;">
      <a href="https://www.semanticscholar.org/search?q=LUM+prequential+meta-learning+categorical+closure&sort=Relevance" target="_blank"
         style="display:flex;align-items:center;gap:8px;color:var(--cyan);font-size:.62rem;text-decoration:none;">
        <span style="color:#00e5ff;font-size:.9rem;">⟐</span> Semantic Scholar — LUM meta-learning
      </a>
      <a href="https://arxiv.org/search/?searchtype=all&query=prequential+meta-learning+categorical+closure" target="_blank"
         style="display:flex;align-items:center;gap:8px;color:var(--cyan);font-size:.62rem;text-decoration:none;">
        <span style="color:#b39ddb;font-size:.9rem;">⊕</span> arXiv — prequential meta-learning
      </a>
      <a href="https://philpapers.org/s/categorical+closure+materialist+philosophy" target="_blank"
         style="display:flex;align-items:center;gap:8px;color:var(--cyan);font-size:.62rem;text-decoration:none;">
        <span style="color:#ffd54f;font-size:.9rem;">◈</span> PhilPapers — cierre categorial
      </a>
      <a href="https://scholar.google.com/scholar?q=LUM-vitae+prequential+meta-learning+digital+organism" target="_blank"
         style="display:flex;align-items:center;gap:8px;color:var(--cyan);font-size:.62rem;text-decoration:none;">
        <span style="color:#00ff88;font-size:.9rem;">◎</span> Google Scholar — LUM-vitae
      </a>
      <a href="https://zenodo.org/search?q=LUM+vitae+meta-learning" target="_blank"
         style="display:flex;align-items:center;gap:8px;color:var(--cyan);font-size:.62rem;text-decoration:none;">
        <span style="color:#ff9800;font-size:.9rem;">📦</span> Zenodo — buscar repositorios LUM
      </a>
      <a href="https://osf.io/search/?q=LUM+vitae+prequential" target="_blank"
         style="display:flex;align-items:center;gap:8px;color:var(--cyan);font-size:.62rem;text-decoration:none;">
        <span style="color:#f48fb1;font-size:.9rem;">⬡</span> OSF — proyectos relacionados
      </a>
    </div>
  </div>
</div>

<!-- ═══ GUÍA PARA RECIÉN LLEGADOS ═══ -->
<details style="margin-top:20px;">
  <summary style="cursor:pointer;font-size:.75rem;color:var(--cyan);letter-spacing:1px;
                  font-family:'Courier New',monospace;padding:10px 14px;
                  background:rgba(0,229,255,.06);border:1px solid rgba(0,229,255,.15);
                  border-radius:7px;outline:none;">
    ◈ Para recién llegados — ¿Qué es esto y cómo leerlo?
  </summary>
  <div style="margin-top:10px;padding:16px 18px;background:var(--panel);border:1px solid var(--border);
              border-radius:7px;font-size:.65rem;color:var(--text);line-height:1.9;">

    <div style="font-size:.8rem;color:var(--cyan);font-weight:bold;margin-bottom:10px;
                font-family:'Courier New',monospace;">¿Qué es ALFA LUM-vitae?</div>
    <p style="margin-bottom:8px;">
      <b style="color:var(--green);">ALFA LUM-vitae</b> es un organismo digital mínimo: un programa de Python que
      aprende de sus propias métricas de rendimiento (meta-aprendizaje prequencial) y verifica
      en cada ciclo si cumple cuatro condiciones formales de <em>vida digital</em>, derivadas del
      <b style="color:var(--cyan);">Materialismo Filosófico</b> de Gustavo Bueno y la teoría
      <b style="color:var(--cyan);">Luminomática (LUM)</b>.
    </p>
    <p style="margin-bottom:12px;">
      No es metáfora: las condiciones son <em>operatorias y verificables</em> — se puede comprobar
      matemáticamente si el sistema las cumple o no, igual que se verifica un hash SHA-256.
    </p>

    <div style="font-size:.78rem;color:var(--cyan);font-weight:bold;margin-bottom:8px;
                font-family:'Courier New',monospace;">Las 4 condiciones de vida digital</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:14px;">
      <div style="padding:8px;background:rgba(0,255,136,.05);border:1px solid rgba(0,255,136,.15);border-radius:5px;">
        <div style="color:var(--green);font-weight:bold;font-size:.68rem;">① Homeostasis</div>
        <div style="font-size:.6rem;color:var(--muted);margin-top:3px;line-height:1.6;">
          ECE ≤ 0.05 en algún ciclo de la última ventana de 5 runs
          <b>Y</b> Brier mejoró al menos una vez.<br>
          <span style="color:var(--dim);">→ Mantener el error dentro de rango sobre el tiempo,
          como la temperatura corporal biológica.</span>
        </div>
      </div>
      <div style="padding:8px;background:rgba(0,255,136,.05);border:1px solid rgba(0,255,136,.15);border-radius:5px;">
        <div style="color:var(--green);font-weight:bold;font-size:.68rem;">② Reproducción con variación</div>
        <div style="font-size:.6rem;color:var(--muted);margin-top:3px;line-height:1.6;">
          El sistema detecta δ_hist &gt; 0.4 (mejora acumulada) y lanza
          instancias hijas vía distribución de Poisson.<br>
          <span style="color:var(--dim);">→ Análogo digital de generar descendencia con mutación.</span>
        </div>
      </div>
      <div style="padding:8px;background:rgba(0,255,136,.05);border:1px solid rgba(0,255,136,.15);border-radius:5px;">
        <div style="color:var(--green);font-weight:bold;font-size:.68rem;">③ Trazabilidad criptográfica</div>
        <div style="font-size:.6rem;color:var(--muted);margin-top:3px;line-height:1.6;">
          Cada ciclo genera un hash SHA-256 encadenado al anterior.
          El historial es inmutable y auditable.<br>
          <span style="color:var(--dim);">→ Análogo de la memoria genética — ADN no falsificable.</span>
        </div>
      </div>
      <div style="padding:8px;background:rgba(0,255,136,.05);border:1px solid rgba(0,255,136,.15);border-radius:5px;">
        <div style="color:var(--green);font-weight:bold;font-size:.68rem;">④ Autonomía operatoria</div>
        <div style="font-size:.6rem;color:var(--muted);margin-top:3px;line-height:1.6;">
          El sistema ejecutó al menos un ciclo sin intervención manual,
          activado por el scheduler (tarea cron, cada hora).<br>
          <span style="color:var(--dim);">→ El organismo "respira" solo.</span>
        </div>
      </div>
    </div>

    <div style="font-size:.78rem;color:var(--cyan);font-weight:bold;margin-bottom:8px;
                font-family:'Courier New',monospace;">Cómo leer las métricas del panel</div>
    <table style="width:100%;border-collapse:collapse;font-size:.6rem;">
      <thead>
        <tr style="color:var(--cyan);border-bottom:1px solid var(--border);">
          <th style="text-align:left;padding:4px 6px;font-family:'Courier New',monospace;">Métrica</th>
          <th style="text-align:left;padding:4px 6px;">Qué mide</th>
          <th style="text-align:left;padding:4px 6px;">Rango normal</th>
          <th style="text-align:left;padding:4px 6px;">¿Preocuparse si…?</th>
        </tr>
      </thead>
      <tbody>
        <tr style="border-bottom:1px solid rgba(26,42,58,.8);">
          <td style="padding:5px 6px;color:var(--cyan);font-family:'Courier New',monospace;">ECE</td>
          <td style="padding:5px 6px;color:var(--muted);">Error de calibración esperado</td>
          <td style="padding:5px 6px;color:var(--green);">&lt; 0.05</td>
          <td style="padding:5px 6px;color:var(--dim);">Se mantiene &gt;0.15 por muchos runs seguidos</td>
        </tr>
        <tr style="border-bottom:1px solid rgba(26,42,58,.8);">
          <td style="padding:5px 6px;color:var(--cyan);font-family:'Courier New',monospace;">κ_conf</td>
          <td style="padding:5px 6px;color:var(--muted);">Coherencia interna del modelo prequencial</td>
          <td style="padding:5px 6px;color:var(--green);">0.3 – 1.0</td>
          <td style="padding:5px 6px;color:var(--dim);">Cae sostenidamente por debajo de 0.2</td>
        </tr>
        <tr style="border-bottom:1px solid rgba(26,42,58,.8);">
          <td style="padding:5px 6px;color:var(--cyan);font-family:'Courier New',monospace;">𝓛*</td>
          <td style="padding:5px 6px;color:var(--muted);">Delta de mejora por ciclo — <b>≈0 entre runs es normal</b></td>
          <td style="padding:5px 6px;color:var(--green);">0.0 – 1.0 (oscila)</td>
          <td style="padding:5px 6px;color:var(--dim);">Nunca sube de 0 en cientos de runs</td>
        </tr>
        <tr style="border-bottom:1px solid rgba(26,42,58,.8);">
          <td style="padding:5px 6px;color:var(--cyan);font-family:'Courier New',monospace;">S_t</td>
          <td style="padding:5px 6px;color:var(--muted);">Memoria exponencial de ciclos vitales pasados</td>
          <td style="padding:5px 6px;color:var(--green);">&gt; 0.5</td>
          <td style="padding:5px 6px;color:var(--dim);">Cae por debajo de 0.3 y no se recupera</td>
        </tr>
        <tr>
          <td style="padding:5px 6px;color:var(--cyan);font-family:'Courier New',monospace;">spawns</td>
          <td style="padding:5px 6px;color:var(--muted);">Instancias derivadas generadas (reproducción)</td>
          <td style="padding:5px 6px;color:var(--green);">&gt; 0</td>
          <td style="padding:5px 6px;color:var(--dim);">Permanece en 0 tras muchos runs con δ_hist alto</td>
        </tr>
      </tbody>
    </table>

    <div style="margin-top:14px;padding:8px 10px;background:rgba(0,0,0,.3);border-left:2px solid var(--cyan);
                border-radius:0 5px 5px 0;font-size:.6rem;color:var(--dim);line-height:1.7;">
      <b style="color:var(--cyan);">Marco teórico</b> —
      LUM-vitae aplica el <em>Materialismo Filosófico</em> (Gustavo Bueno, 1972–2016) al dominio digital:
      la vida no es una esencia sino un conjunto de operaciones verificables en un sustrato material.
      La teoría <em>Luminomática</em> (LUM) formaliza el cierre categorial entre disciplinas científicas
      usando teoría de conjuntos y operadores normativos.
      <br>
      <b style="color:var(--cyan);">DOI</b>:
      <a href="https://doi.org/10.5281/zenodo.19235185" target="_blank"
         style="color:var(--cyan);">10.5281/zenodo.19235185</a> &nbsp;|&nbsp;
      Código fuente: <a href="https://github.com/julespintor-tech/alfa-lum-vitae" target="_blank"
         style="color:var(--cyan);">GitHub</a>
    </div>
  </div>
</details>

<div style="text-align:center;margin-top:22px;font-size:.57rem;color:var(--dim);
            letter-spacing:1px;font-family:'Courier New',monospace;line-height:2;">
  ALFA LUM-vitae vΩ.4 · Materialismo Filosófico · G. Bueno + Luminomática · Proyecto MINERVA<br>
  <a href="https://github.com/julespintor-tech/alfa-lum-vitae" target="_blank" style="color:#3a5a7a;text-decoration:none;margin:0 8px;">GitHub</a>·
  <a href="https://doi.org/10.5281/zenodo.19235185" target="_blank" style="color:#3a5a7a;text-decoration:none;margin:0 8px;">DOI Zenodo</a>·
  <a href="https://osf.io/5jhr4" target="_blank" style="color:#3a5a7a;text-decoration:none;margin:0 8px;">OSF</a>·
  <a href="https://orcid.org/0009-0001-0800-5303" target="_blank" style="color:#3a5a7a;text-decoration:none;margin:0 8px;">ORCID</a>
</div>

<script>
// ── HISTORIAL localStorage — persiste entre recargas sin necesidad de Flask ──
const _LS_MINERVA = 'lum_minerva_historial';
const _LS_CLASICOS = 'lum_clasicos_historial';
const _LS_MAX  = 200;
const _LS_SHOW = 20;
const _LS_KEEP = 100;
const _DEDUP_MS = 5 * 60 * 1000;  // 5 min — umbral anti-duplicados

// ── Session ID persistente — huella del navegador ─────────────────────────
// Se genera una sola vez y vive en localStorage para siempre.
// Identifica de qué perfil/equipo provienen las entradas y los archivos exportados.
function _lsGetSid() {{
  let sid = localStorage.getItem('lum_sid');
  if (!sid) {{
    sid = Date.now().toString(36) + Math.random().toString(36).slice(2,6);
    localStorage.setItem('lum_sid', sid);
  }}
  return sid;
}}
const _LUM_SID = _lsGetSid();

function _lsSave(key, entrada) {{
  try {{
    const arr = JSON.parse(localStorage.getItem(key) || '[]');

    // ── Dedup híbrido: bloquear solo si contenido idéntico Y menos de 30 min ──
    if (arr.length > 0) {{
      const last = arr[0];
      const diffMs = Date.now() - new Date(last.timestamp||0).getTime();
      const within30 = diffMs < 30 * 60 * 1000;
      if (within30) {{
        const sameTotal  = (last.total_papers||0) === (entrada.total_papers||0);
        const sameSource = last.source === entrada.source;
        if (sameTotal && sameSource) {{
          const lastDoms = JSON.stringify(Object.fromEntries(
            Object.keys(last.dominios||{{}}).map(k => [k, (last.dominios[k]||{{}}).n_papers_ss||0])
          ));
          const newDoms = JSON.stringify(Object.fromEntries(
            Object.keys(entrada.dominios||{{}}).map(k => [k, (entrada.dominios[k]||{{}}).n_papers_ss||0])
          ));
          if (lastDoms === newDoms) return;  // idéntico en <30 min — saltar
        }}
      }}
    }}

    entrada.sid = _LUM_SID;   // estampar huella de sesión
    arr.unshift(entrada);

    if (arr.length > _LS_MAX) {{
      const label = key.includes('clasicos') ? 'Clásicos' : 'Dominios';
      const col   = key.includes('clasicos') ? '#ffd54f' : '#00e5ff';
      const old100 = arr.slice(_LS_KEEP);
      _exportHistorialArr(old100, label + ' — Archivo ' + new Date().toISOString().slice(0,10), col);
      arr.splice(_LS_KEEP);
      const n = document.createElement('div');
      n.textContent = '📥 100 entradas antiguas exportadas — historial renovado (100 recientes conservadas)';
      n.style.cssText = 'position:fixed;bottom:20px;right:20px;background:#0a1a2a;border:1px solid '+col+';color:'+col+';padding:10px 16px;border-radius:6px;font-size:.7rem;z-index:9999;font-family:monospace;max-width:380px;';
      document.body.appendChild(n);
      setTimeout(() => n.remove(), 7000);
    }}
    localStorage.setItem(key, JSON.stringify(arr));
  }} catch(e) {{}}
}}

// ── EXPORTAR HISTORIAL como HTML descargable ──────────────────────────────
// _exportHistorialArr: núcleo — trabaja con un array ya cargado
// sid: session_id opcional para el nombre de archivo (si no se pasa, usa _LUM_SID global)
function _exportHistorialArr(arr, titulo, color, sid) {{
  if (!arr.length) {{ alert('Sin entradas en el historial aún.'); return; }}
  const _sid = sid || (typeof _LUM_SID !== 'undefined' ? _LUM_SID : 'local');
  const DCOL = {{FORM:'#00e5ff',NAT:'#00ff88',TEC:'#b39ddb',SOC_IV:'#ffd54f',SOC_DID:'#ff9800',ARTE:'#f48fb1'}};
  const SCOL = {{GREEN:'#00ff88',AMBER:'#ffd54f',RED:'#ff3d5a'}};
  const SDOT = {{GREEN:'●',AMBER:'◑',RED:'○'}};
  let rows = '';
  arr.forEach((e, i) => {{
    const ts  = (e.timestamp||'').slice(0,19).replace('T',' ');
    const src = e.source||'';
    const total = e.total_papers || e.total_papers_found || 0;
    const esid = e.sid || '—';
    let detail = '';
    if (e.dominios) {{
      Object.keys(e.dominios).forEach(k => {{
        const dd = e.dominios[k]||{{}};
        const sc = SCOL[dd.semaforo]||'#9e9e9e', dc = DCOL[k]||'#9e9e9e';
        detail += `<span style="display:inline-block;margin:2px 3px;padding:2px 7px;border-radius:3px;border:1px solid ${{dc}}55;background:${{dc}}14;color:${{dc}};font-size:.78rem;">${{k}} <span style="color:${{sc}}">${{SDOT[dd.semaforo]||'?'}}</span> ${{dd.n_papers_ss||0}}p</span>`;
      }});
    }} else if (e.obras) {{
      Object.keys(e.obras).forEach(k => {{
        const n = (e.obras[k]||{{}}).n_papers||0;
        const col2 = n>=3?'#00ff88':(n>0?'#ffd54f':'#555');
        detail += `<span style="display:inline-block;margin:2px 3px;padding:2px 7px;border-radius:3px;border:1px solid ${{col2}}55;background:${{col2}}14;color:${{col2}};font-size:.75rem;">${{k.replace(/_/g,' ')}} ${{n}}p</span>`;
      }});
    }}
    const bg = i%2===0?'#0a1520':'#0d1a28';
    rows += `<tr style="background:${{bg}};">
      <td style="padding:8px 12px;color:#4a7090;font-size:.8rem;">${{i+1}}</td>
      <td style="padding:8px 12px;color:#5a8aaa;font-size:.8rem;font-family:monospace;white-space:nowrap;">${{ts}}</td>
      <td style="padding:8px 12px;color:#3a6080;font-size:.75rem;">${{src}}</td>
      <td style="padding:8px 12px;color:${{color}};font-size:.8rem;font-weight:bold;">${{total}}</td>
      <td style="padding:8px 12px;color:#2a4060;font-size:.7rem;font-family:monospace;">${{esid}}</td>
      <td style="padding:8px 12px;">${{detail}}</td>
    </tr>`;
  }});
  const now = new Date().toISOString().slice(0,19).replace('T',' ');
  const tsFirst = (arr[arr.length-1]?.timestamp||'').slice(0,10);
  const tsLast  = (arr[0]?.timestamp||'').slice(0,10);
  const html = `<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">
<title>MINERVA — ${{titulo}}</title>
<style>
  body{{background:#060d14;color:#8aacbe;font-family:'Courier New',monospace;margin:0;padding:24px;}}
  h1{{color:${{color}};font-size:1.1rem;letter-spacing:2px;border-bottom:1px solid ${{color}}44;padding-bottom:10px;margin-bottom:6px;}}
  .meta{{font-size:.72rem;color:#3a5a7a;margin-bottom:6px;line-height:1.8;}}
  .sid{{display:inline-block;background:#0a1a2a;border:1px solid ${{color}}44;color:${{color}}bb;padding:2px 10px;border-radius:4px;font-size:.72rem;letter-spacing:1px;margin-bottom:14px;}}
  table{{width:100%;border-collapse:collapse;font-size:.82rem;}}
  th{{background:#0a1a2a;color:#3a6080;padding:8px 12px;text-align:left;border-bottom:1px solid #1a3a5a;font-size:.72rem;letter-spacing:1px;}}
  tr:hover td{{background:#0f2030!important;}}
  .total{{font-size:.78rem;color:#3a5a7a;margin-top:16px;}}
</style></head><body>
<h1>◈ MINERVA ALFA LUM-vitae — ${{titulo}}</h1>
<div class="meta">
  Exportado: ${{now}} UTC &nbsp;·&nbsp; ${{arr.length}} registros &nbsp;·&nbsp; rango: ${{tsFirst}} → ${{tsLast}}<br>
  Generado por ALFA LUM-vitae vΩ.4
</div>
<div class="sid">SID: ${{_sid}}</div>
<table>
  <thead><tr>
    <th>#</th><th>TIMESTAMP</th><th>FUENTE</th><th>PAPERS</th><th>SID</th><th>DETALLE</th>
  </tr></thead>
  <tbody>${{rows}}</tbody>
</table>
<div class="total">Total: ${{arr.length}} registros · SID sesión actual: ${{_sid}}</div>
</body></html>`;
  const blob = new Blob([html], {{type:'text/html;charset=utf-8'}});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  // Nombre incluye SID para identificar fácilmente el archivo
  const tipo = titulo.toLowerCase().includes('clás') || titulo.toLowerCase().includes('clas') ? 'clasicos' : 'dominios';
  a.download = `lum_hist_${{tipo}}_${{new Date().toISOString().slice(0,10)}}_${{_sid}}.html`;
  a.click();
  URL.revokeObjectURL(a.href);
}}
// Wrapper para los botones manuales — carga desde localStorage
function _exportHistorial(key, titulo, color) {{
  _exportHistorialArr(_lsLoad(key), titulo, color);
}}

function _lsLoad(key) {{
  try {{ return JSON.parse(localStorage.getItem(key) || '[]'); }}
  catch(e) {{ return []; }}
}}

function _buildMinEntry(e) {{
  const DCOL = {{FORM:'#00e5ff',NAT:'#00ff88',TEC:'#b39ddb',SOC_IV:'#ffd54f',SOC_DID:'#ff9800',ARTE:'#f48fb1'}};
  const SCOL = {{GREEN:'#00ff88',AMBER:'#ffd54f',RED:'#ff3d5a'}};
  const SDOT = {{GREEN:'●',AMBER:'◑',RED:'○'}};
  const ts16 = (e.timestamp||'').slice(0,16).replace('T',' ')+' UTC';
  const doms = e.dominios || {{}};
  let domHtml = '';
  Object.keys(doms).forEach(k => {{
    const dc=DCOL[k]||'#9e9e9e', dd=doms[k]||{{}}, sc=SCOL[dd.semaforo]||'#9e9e9e';
    domHtml+=`<span style="display:inline-block;padding:2px 6px;border-radius:3px;border:1px solid ${{dc}}44;background:${{dc}}11;color:${{dc}};font-size:.55rem;margin:2px;">${{k}} <span style="color:${{sc}}">${{SDOT[dd.semaforo]||'○'}}</span></span>`;
  }});
  const src = e.source==='full_run'?'🔄 run':'⚡ live';
  const ne = document.createElement('div');
  ne.className = 'hist-entry';
  ne.style.cssText = 'padding:8px 10px;margin-bottom:6px;border:1px solid #00e5ff33;border-radius:6px;background:rgba(0,229,255,.04);';
  ne.innerHTML = `<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;"><span style="font-size:.58rem;color:var(--dim);">${{ts16}}</span><span style="font-size:.55rem;color:var(--muted);">${{src}} · ${{e.total_papers||0}} papers</span></div><div>${{domHtml}}</div>`;
  return ne;
}}

function _buildClEntry(e) {{
  const ts16 = (e.timestamp||'').slice(0,16).replace('T',' ')+' UTC';
  const obras = e.obras || {{}};
  let obHtml = '';
  Object.keys(obras).slice(0,8).forEach(k => {{
    const n = (obras[k]||{{}}).n_papers || 0;
    const col = n >= 3 ? '#00ff88' : (n > 0 ? '#ffd54f' : '#3a5a7a');
    obHtml += `<span style="display:inline-block;padding:2px 5px;border-radius:3px;border:1px solid ${{col}}44;background:${{col}}11;color:${{col}};font-size:.52rem;margin:2px;">${{k.replace(/_/g,' ').slice(0,18)}} ${{n}}p</span>`;
  }});
  const ne = document.createElement('div');
  ne.className = 'cl-hist-entry';
  ne.style.cssText = 'padding:7px 9px;margin-bottom:5px;border:1px solid #ffd54f22;border-radius:5px;background:rgba(255,213,79,.03);';
  ne.innerHTML = `<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;"><span style="font-size:.57rem;color:var(--dim);">${{ts16}}</span><span style="font-size:.54rem;color:#ffd54f88;">📚 SS · ${{e.total_papers||0}} papers</span></div><div>${{obHtml}}</div>`;
  return ne;
}}

function _renderMinHistorial(panel, arr) {{
  if (!panel) return;
  panel.innerHTML = '';
  if (!arr.length) {{
    panel.innerHTML = '<div style="color:var(--dim);font-size:.6rem;padding:8px 0;">Sin búsquedas registradas aún.</div>';
    return;
  }}
  const visible = arr.slice(0, _LS_SHOW);
  visible.forEach(e => panel.appendChild(_buildMinEntry(e)));
  if (arr.length > _LS_SHOW) {{
    const rest = arr.length - _LS_SHOW;
    const btn = document.createElement('button');
    btn.textContent = `▾ ver ${{rest}} más (total ${{arr.length}})`;
    btn.style.cssText = 'background:none;border:1px solid #00e5ff33;color:#00e5ff99;font-size:.55rem;padding:4px 10px;border-radius:4px;cursor:pointer;margin-top:4px;width:100%;';
    btn.onclick = function() {{
      arr.slice(_LS_SHOW).forEach(e => panel.insertBefore(_buildMinEntry(e), btn));
      btn.remove();
    }};
    panel.appendChild(btn);
  }}
}}

function _renderClHistorial(panel, arr) {{
  if (!panel) return;
  panel.innerHTML = '';
  if (!arr.length) {{
    panel.innerHTML = '<div style="color:var(--dim);font-size:.6rem;padding:6px 0;">Sin verificaciones registradas aún.</div>';
    return;
  }}
  const visible = arr.slice(0, _LS_SHOW);
  visible.forEach(e => panel.appendChild(_buildClEntry(e)));
  if (arr.length > _LS_SHOW) {{
    const rest = arr.length - _LS_SHOW;
    const btn = document.createElement('button');
    btn.textContent = `▾ ver ${{rest}} más (total ${{arr.length}})`;
    btn.style.cssText = 'background:none;border:1px solid #ffd54f33;color:#ffd54f99;font-size:.55rem;padding:4px 10px;border-radius:4px;cursor:pointer;margin-top:4px;width:100%;';
    btn.onclick = function() {{
      arr.slice(_LS_SHOW).forEach(e => panel.insertBefore(_buildClEntry(e), btn));
      btn.remove();
    }};
    panel.appendChild(btn);
  }}
}}

// ── MINERVA TAB SWITCHER ──────────────────────────────────────────────────
const _tabAccents = {{ dominios:'#00e5ff', clasicos:'#ffd54f' }};
document.addEventListener('DOMContentLoaded', function() {{
  switchMinervaTab('dominios');
  const mPanel = document.getElementById('minerva-historial-panel');
  _renderMinHistorial(mPanel, _lsLoad(_LS_MINERVA));
  const cPanel = document.getElementById('cl-historial-panel');
  _renderClHistorial(cPanel, _lsLoad(_LS_CLASICOS));
}});
function switchMinervaTab(tab) {{
  ['dominios','clasicos'].forEach(t => {{
    const panel = document.getElementById('mtab-' + t);
    const btn   = document.getElementById('mtab-btn-' + t);
    if (!panel || !btn) return;
    const active = (t === tab);
    const ac = _tabAccents[t];
    panel.style.display = active ? 'block' : 'none';
    btn.style.background   = active ? `rgba(${{ac==='#00e5ff'?'0,229,255':'255,213,79'}},.14)` : 'rgba(0,0,0,.2)';
    btn.style.borderColor  = active ? `${{ac}}55` : '#1a2a3a';
    btn.style.color        = active ? ac : '#3a5a7a';
    btn.style.fontWeight   = active ? 'bold' : 'normal';
  }});
}}

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

// ── MINERVA LIVE SEARCH ──────────────────────────────────────────────
const SS_QUERIES = {{
  FORM:    'mathematical closure axiomatization completeness theorem formal system',
  NAT:     'natural science causal closure physical laws empirical measurement',
  TEC:     'cybernetics feedback closure formal verification control systems AI',
  SOC_IV:  'social science operationalization construct validity measurement',
  SOC_DID: 'historical method scientific demarcation historiography archaeology',
  ARTE:    'aesthetic closure art theory pictorial formalization materialist'
}};

// ── Variantes de query por dominio (rotación para obtener papers DISTINTOS) ─
const SS_QUERY_VARIANTS = {{
  FORM: [
    'mathematical closure axiomatization completeness theorem formal system',
    'formal logic proof theory deductive closure completeness incompleteness',
    'category theory algebraic closure structure morphism mathematics',
    'axiomatic system logical closure Hilbert program foundation mathematics'
  ],
  NAT: [
    'natural science causal closure physical laws empirical measurement',
    'physical causal closure hypothesis neuroscience physicalism mind',
    'scientific realism natural kinds empirical closure experimental method',
    'causal completeness physical world closure argument philosophy science'
  ],
  TEC: [
    'cybernetics feedback closure formal verification control systems AI',
    'feedback loop stability analysis formal closure property software',
    'formal methods model checking closure operator automata specification',
    'AI alignment formal verification closure safety machine learning'
  ],
  SOC_IV: [
    'social science operationalization construct validity measurement',
    'sociological theory operationalization validity reliability construct',
    'quantitative social research measurement demarcation methodology scale',
    'social measurement theory latent variable construct validation psychometrics'
  ],
  SOC_DID: [
    'historical method scientific demarcation historiography archaeology',
    'philosophy of history demarcation chronology systematic evidence',
    'historiography methodology historical explanation demarcation science',
    'archaeological stratigraphy dating method systematic evidence historical'
  ],
  ARTE: [
    'aesthetic closure art theory pictorial formalization materialist',
    'philosophy of art aesthetic formalism pictorial representation theory',
    'art theory materialist aesthetics pictorial space formalization',
    'aesthetic theory artistic closure pictorial analysis formal critique'
  ]
}};

const DOMAIN_COLORS = {{
  FORM:'#00e5ff', NAT:'#00ff88', TEC:'#b39ddb',
  SOC_IV:'#ffd54f', SOC_DID:'#ff9800', ARTE:'#f48fb1'
}};
const SIGNALS = {{
  FORM:    ['axiom','theorem','proof','completeness','formal system','closure','deductive'],
  NAT:     ['causal closure','physical law','experimental','measurement','replication','empirical'],
  TEC:     ['feedback loop','formal verification','closure property','specification','cybernetic'],
  SOC_IV:  ['operationalization','construct validity','reliability','demarcation','measurement'],
  SOC_DID: ['historical method','demarcation','chronology','dating method','systematic fieldwork'],
  ARTE:    ['pictorial','aesthetic closure','artistic operation','formal analysis','materialist']
}};

// ── Rotación de query variant + offset por dominio (localStorage) ──────────
const _SS_QROT_KEY   = 'lum_ss_qrot';
const _SS_OFFSET_KEY = 'lum_ss_offsets';

function _nextQuery(domKey) {{
  var rot = {{}};
  try {{ rot = JSON.parse(localStorage.getItem(_SS_QROT_KEY) || '{{}}'); }} catch(e) {{}}
  var variants = SS_QUERY_VARIANTS[domKey] || [SS_QUERIES[domKey]];
  var idx = (rot[domKey] || 0) % variants.length;
  rot[domKey] = (idx + 1) % variants.length;
  try {{ localStorage.setItem(_SS_QROT_KEY, JSON.stringify(rot)); }} catch(e) {{}}
  return variants[idx];
}}

function _nextOffset(domKey) {{
  var offs = {{}};
  try {{ offs = JSON.parse(localStorage.getItem(_SS_OFFSET_KEY) || '{{}}'); }} catch(e) {{}}
  var off = offs[domKey] || 0;
  offs[domKey] = (off + 8) % 48;  // 6 páginas de 8 (0,8,16,24,32,40)
  try {{ localStorage.setItem(_SS_OFFSET_KEY, JSON.stringify(offs)); }} catch(e) {{}}
  return off;
}}

// ── Síntesis breve desde papers encontrados ────────────────────────────────
function _genSintetico(papers) {{
  if (!papers || papers.length === 0) return null;
  var years = papers.map(function(p) {{ return p.year; }}).filter(function(y) {{ return y && y > 1900; }});
  var minY = years.length ? Math.min.apply(null, years) : null;
  var maxY = years.length ? Math.max.apply(null, years) : null;
  var maxCit = papers.reduce(function(m, p) {{ return Math.max(m, p.citationCount || 0); }}, 0);
  var s = papers.length + ' papers';
  if (minY && maxY && minY !== maxY) s += ' (' + minY + '–' + maxY + ')';
  else if (maxY) s += ' (' + maxY + ')';
  if (maxCit > 0) s += ', máx ' + maxCit + 'c';
  return s;
}}

// ── Estado de búsqueda — Dominios Científicos ─────────────────────────────
let _mSearching = false;
let _mLastAt    = 0;
let _mCache     = {{}};
const COOLDOWN  = 30000;  // ms — 30s entre búsquedas

// ── Estado de búsqueda — Clásicos ─────────────────────────────────────────
let _clSearching = false;
let _clLastAt    = 0;

// ── Queries SS para obras clásicas (citas y papers relacionados) ───────────
const CL_SS_QUERIES = {{
  EUCLID_ELEMENTOS:       'Euclid Elements geometry axiom proof mathematics',
  NEWTON_PRINCIPIA:       'Newton Principia Mathematica mechanics gravity classical physics',
  BUENO_TCC:              'categorical closure scientific theory philosophy Bueno',
  FREGE_BEGRIF:           'Frege Begriffsschrift predicate logic formalization',
  MAXWELL_ECUACIONES:     'Maxwell equations electromagnetism classical field theory',
  DARWIN_ORIGEN:          'Darwin natural selection evolution species origin',
  ARISTOTELES_ORGANON:    'Aristotle logic syllogism Categories Organon',
  KANT_KRV:               'Kant Critique Pure Reason transcendental categories',
  BUENO_ANIMAL_DIVINO:    'Bueno animal divino materialismo religion philosophy',
  MARX_CAPITAL:           'Marx Capital value labor surplus political economy',
  SAUSSURE_CLG:           'Saussure linguistics sign langue parole structural',
  FREUD_SUENOS:           'Freud interpretation dreams psychoanalysis unconscious',
  HEGEL_FENOMENOLOGIA:    'Hegel Phenomenology Spirit dialectic consciousness',
  NIETZSCHE_ZARATHUSTRA:  'Nietzsche Zarathustra will power philosophy eternal'
}};

function scoreTexto(txt, sigs) {{
  if (!txt) return 0;
  const t = txt.toLowerCase();
  return sigs.filter(s => t.includes(s)).length / Math.max(sigs.length * 0.3, 1);
}}

// ── Fetch con retry automático (timeout + 429 backoff) ─────────────────────
// SIN AbortController: evita error "AbortSignal cannot be cloned" en extensiones Chrome.
// El timeout se implementa con Promise.race + timer independiente.
async function fetchWithRetry(url, timeoutMs, maxRetries) {{
  maxRetries = maxRetries || 2;
  for (var attempt = 0; attempt <= maxRetries; attempt++) {{
    try {{
      var _fetchP   = fetch(url);
      var _toMs     = timeoutMs;
      var _timeoutP = new Promise(function(_, rej) {{
        setTimeout(function() {{ rej(new Error('timeout_' + _toMs)); }}, _toMs);
      }});
      var r = await Promise.race([_fetchP, _timeoutP]);
      if (r.status === 429) {{
        if (attempt < maxRetries) {{
          await new Promise(function(rv) {{ setTimeout(rv, 1500 * (attempt + 1)); }});
          continue;
        }}
        return null;
      }}
      return r;
    }} catch(e) {{
      if (attempt < maxRetries) {{
        await new Promise(function(rv) {{ setTimeout(rv, 900 * (attempt + 1)); }});
      }}
    }}
  }}
  return null;
}}

// ── Función de utilidad: estado del botón ─────────────────────────────────
function setBtnState(btnId, statusId, loading, loadingText, idleText) {{
  const btn = document.getElementById(btnId);
  const st  = document.getElementById(statusId);
  if (!btn) return;
  btn.disabled = loading;
  btn.innerHTML = loading
    ? `<span style="display:inline-block;animation:spin .7s linear infinite">⟳</span> ${{loadingText}}`
    : idleText;
  if (st) {{ st.style.display = loading ? 'block' : st.style.display; }}
}}

function showStatus(elId, color, html, autohide) {{
  const el = document.getElementById(elId);
  if (!el) return;
  el.style.display = 'block';
  el.style.borderLeftColor = color;
  el.innerHTML = html;
  if (autohide > 0) setTimeout(() => {{ el.style.display = 'none'; }}, autohide);
}}

// ── MINERVA: buscar Dominios Científicos ──────────────────────────────────
async function buscarMinerva() {{
  if (_mSearching) return;
  const now = Date.now();

  if (_mLastAt > 0 && (now - _mLastAt) < COOLDOWN) {{
    const seg = Math.ceil((COOLDOWN - (now - _mLastAt)) / 1000);
    showStatus('minerva-status','var(--dim)',
      `<span style="color:var(--dim)">⏱ Búsqueda reciente — espera <b style="color:var(--cyan)">${{seg}}s</b></span>`, 0);
    return;
  }}

  _mSearching = true;
  setBtnState('btn-minerva','minerva-status', true, 'Buscando…', '🔍 Buscar ahora');
  showStatus('minerva-status','rgba(0,229,255,.3)',
    '<span style="color:var(--dim)">Consultando Semantic Scholar (6 dominios)…</span>', 0);

  const newCache = {{}};
  let totalNew = 0, domainsWithNew = [], errCount = 0, successCount = 0;
  const keys = Object.keys(SS_QUERIES);

  for (let i = 0; i < keys.length; i++) {{
    const key = keys[i];
    const st  = document.getElementById('minerva-status');
    if (st) st.innerHTML = `<span style="color:var(--dim)">Dominio ${{i+1}}/${{keys.length}}: <b style="color:${{DOMAIN_COLORS[key]}}">${{key}}</b>…</span>`;

    const _qVariant = _nextQuery(key);
    const _qOffset  = _nextOffset(key);
    const url = 'https://api.semanticscholar.org/graph/v1/paper/search?query='
              + encodeURIComponent(_qVariant)
              + '&offset=' + _qOffset
              + '&limit=8&fields=title,abstract,year,citationCount';
    const r = await fetchWithRetry(url, 15000, 2);

    if (!r) {{
      errCount++;
      newCache[key] = {{n:0, titles: new Set()}};
    }} else if (!r.ok) {{
      if (r.status !== 429) errCount++;   // 429 ya fue reintentado — no contar doble
      newCache[key] = {{n:0, titles: new Set()}};
    }} else {{
      try {{
        const d = await r.json();
        // scoreTexto solo para ORDENAR, no filtrar
        const allPapers = (d.data || []);
        const scored = allPapers.map(p => ({{
          ...p,
          _score: scoreTexto((p.title||'')+' '+(p.abstract||''), SIGNALS[key])
        }})).sort((a,b) => b._score - a._score);
        const papers = scored.slice(0, 6);
        const titles = new Set(papers.map(p => (p.title||'').trim().toLowerCase()));
        const synth  = _genSintetico(papers);
        newCache[key] = {{n: papers.length, titles, papers, sintetico: synth}};
        successCount++;

        const prev = _mCache[key];
        const genuNew = [...titles].filter(t => !(prev && prev.titles.has(t)));
        if (genuNew.length > 0) {{ totalNew += genuNew.length; domainsWithNew.push(key); }}

        // ── Actualizar card visual ─────────────────────────────────────────
        const domCol   = DOMAIN_COLORS[key] || '#4a7090';
        const semCol   = papers.length >= 5 ? '#00ff88' : (papers.length > 0 ? '#ffd54f' : '#4a7090');
        const semLabel = papers.length >= 5 ? 'VERDE live' : (papers.length > 0 ? 'ÁMBAR live' : 'SIN SS');

        // Badge count
        const elN = document.getElementById('mc-n-' + key);
        if (elN) {{
          elN.textContent = papers.length + (papers.length !== 1 ? ' papers live' : ' paper live');
          elN.style.color = semCol;
        }}
        // Semáforo label
        const elS = document.getElementById('mc-state-' + key);
        if (elS) {{ elS.textContent = semLabel; elS.style.color = semCol; }}

        // Card border color (refleja semáforo live)
        const elCard = document.getElementById('mc-' + key);
        if (elCard) {{
          elCard.style.borderColor = semCol + '44';
          elCard.style.boxShadow   = papers.length >= 5 ? ('0 0 8px ' + semCol + '22') : 'none';

          // Lista de papers live (siempre reemplaza con los NUEVOS)
          let livelist = elCard.querySelector('.ss-live-list');
          if (!livelist) {{
            livelist = document.createElement('div');
            livelist.className = 'ss-live-list';
            livelist.style.cssText = 'margin-top:6px;border-top:1px solid #1a2a3a;padding-top:6px;';
            elCard.appendChild(livelist);
          }}
          if (papers.length > 0) {{
            livelist.innerHTML =
              '<div style="font-size:.52rem;color:#2a6a8a;margin-bottom:4px;letter-spacing:.4px;">'
              + '▸ PAPERS SS LIVE' + (synth ? ' · <span style="color:#3a8aaa">' + synth + '</span>' : '') + '</div>'
              + papers.map(function(p) {{
                  return '<div style="font-size:.57rem;color:#4a8aaa;margin-bottom:3px;line-height:1.4;">'
                    + '<span style="color:' + domCol + '99;">·</span> '
                    + (p.title||'').slice(0,82) + ((p.title||'').length>82?'…':'')
                    + (p.year ? '<span style="color:#2a4a6a;margin-left:4px;">' + p.year + '</span>' : '')
                    + (p.citationCount>0 ? '<span style="color:#ffd54f88;margin-left:4px;">' + p.citationCount + 'c</span>' : '')
                    + '</div>';
                }}).join('');
          }} else {{
            livelist.innerHTML = '<div style="font-size:.54rem;color:#3a5a7a;">Sin resultados SS</div>';
          }}
        }}
      }} catch(jsonErr) {{
        errCount++;
        newCache[key] = {{n:0, titles: new Set(), sintetico: null}};
      }}
    }}
    if (i < keys.length - 1) await new Promise(rv => setTimeout(rv, 500));
  }}

  _mCache     = newCache;
  _mLastAt    = Date.now();
  _mSearching = false;
  setBtnState('btn-minerva', 'minerva-status', false, '', '🔍 Buscar ahora');

  const hora          = new Date().toLocaleTimeString('es', {{hour:'2-digit',minute:'2-digit'}});
  const todosFallaron = errCount === keys.length;
  const mayoriaFallo  = errCount > keys.length / 2;
  const errExtra      = errCount > 0 && !todosFallaron
    ? ` <span style="color:#ff9800;font-size:.85em">(${{errCount}} dominio${{errCount>1?'s':''}} sin respuesta)</span>` : '';

  if (todosFallaron) {{
    showStatus('minerva-status','#ff9800',
      `<span style="color:#ff9800">⚠ Semantic Scholar no responde · ${{hora}}</span>
       <span style="font-size:.82em;color:#cc6600;display:block;margin-top:4px;">
         Sin conexión o rate-limit · intenta en 1–2 min<br>
         <span style="color:#3a7a5a">▸ El historial anterior sigue disponible en localStorage</span></span>`, 0);
  }} else if (mayoriaFallo && successCount === 0) {{
    showStatus('minerva-status','#ff9800',
      `<span style="color:#ff9800">⚠ ${{errCount}}/${{keys.length}} dominios sin respuesta · ${{hora}} — API lenta</span>`, 12000);
  }} else if (totalNew === 0) {{
    // "Sin novedades" ahora significa mismos títulos que antes en sesión — igual guardamos
    const totalEncontrados = keys.reduce((s,k) => s+(newCache[k]||{{}}).n||0, 0);
    showStatus('minerva-status','var(--dim)',
      `<span style="color:var(--dim)">✓ ${{totalEncontrados}} papers encontrados · ${{hora}} (mismos que antes en sesión)</span>${{errExtra}}`, 9000);
  }} else {{
    showStatus('minerva-status','var(--green)',
      `<span style="color:var(--green)">● ${{totalNew}} paper(s) nuevos en: <b>${{domainsWithNew.join(', ')}}</b> · ${{hora}}</span>${{errExtra}}`, 0);
  }}

  // ── Persistir historial (localStorage + Flask silencioso) ────────────────
  if (!todosFallaron && successCount > 0) {{
    const tsISO  = new Date().toISOString();
    const domData = {{}};
    keys.forEach(function(k) {{
      const c = newCache[k] || {{}};
      domData[k] = {{
        n_papers_ss: c.n || 0,
        semaforo:    c.n >= 5 ? 'GREEN' : (c.n > 0 ? 'AMBER' : 'RED'),
        p_sintetico: c.sintetico || null,
        score_ss:    null
      }};
    }});
    const totalPapers = keys.reduce(function(s,k) {{ return s + (newCache[k]||{{}}).n||0; }}, 0);
    const entrada = {{
      timestamp:    tsISO,
      source:       'live_search',
      total_papers: totalPapers,
      dominios:     domData
    }};

    // 1. localStorage
    _lsSave(_LS_MINERVA, entrada);

    // 2. Flask (silencioso)
    fetch('http://localhost:5050/api/minerva_historial', {{
      method:'POST', headers:{{'Content-Type':'application/json'}},
      body: JSON.stringify(entrada)
    }}).catch(function(){{}});

    // 3. Actualizar panel historial
    const panel = document.getElementById('minerva-historial-panel');
    if (panel) _renderMinHistorial(panel, _lsLoad(_LS_MINERVA));

    // 4. Actualizar resumen global de síntesis (si existe el bloque)
    const elSummary = document.getElementById('minerva-summary-live');
    if (elSummary) {{
      var summLines = keys.filter(function(k) {{ return (newCache[k]||{{}}).n > 0; }})
        .map(function(k) {{
          var c = newCache[k]; var col = DOMAIN_COLORS[k]||'#9e9e9e';
          return '<span style="color:' + col + ';margin-right:8px;">'
            + k + ' <span style="color:#00ff8888">' + c.n + 'p</span>'
            + (c.sintetico ? ' <span style="color:#3a6a8a;font-size:.85em;">[' + c.sintetico + ']</span>' : '')
            + '</span>';
        }});
      elSummary.innerHTML = summLines.join('') || '<span style="color:var(--dim)">—</span>';
    }}
  }}
}}

// ── CLÁSICOS: buscar papers sobre cada obra ───────────────────────────────
async function buscarClasicos() {{
  if (_clSearching) return;
  const now = Date.now();

  if (_clLastAt > 0 && (now - _clLastAt) < COOLDOWN) {{
    const seg = Math.ceil((COOLDOWN-(now-_clLastAt))/1000);
    showStatus('cl-status','var(--dim)',
      `<span style="color:var(--dim)">⏱ Espera <b style="color:var(--cyan)">${{seg}}s</b></span>`,0);
    return;
  }}

  _clSearching = true;
  setBtnState('btn-clasicos','cl-status',true,'Buscando…','📚 Verificar en SS');
  showStatus('cl-status','rgba(255,213,79,.3)',
    '<span style="color:var(--dim)">Consultando Semantic Scholar (14 obras)…</span>',0);

  const keys     = Object.keys(CL_SS_QUERIES);
  var ok=0, fail=0, found=0;
  var clCounts = {{}};  // rastreo directo de counts (no depende de DOM badges)

  for (let i=0; i<keys.length; i++) {{
    const key = keys[i];
    const st  = document.getElementById('cl-status');
    if (st) st.innerHTML = '<span style="color:var(--dim)">Obra ' + (i+1) + '/' + keys.length + ': <b style="color:#ffd54f">' + key.replace(/_/g,' ') + '</b>…</span>';

    // Rotar offset para obtener páginas distintas de resultados cada búsqueda
    const _clOff = _nextOffset('CL_' + key);
    const url = 'https://api.semanticscholar.org/graph/v1/paper/search?query='
              + encodeURIComponent(CL_SS_QUERIES[key])
              + '&offset=' + _clOff
              + '&limit=5&fields=title,year,citationCount';
    const r = await fetchWithRetry(url, 14000, 1);

    clCounts[key] = 0;
    if (!r || !r.ok) {{
      fail++;
    }} else {{
      try {{
        const d = await r.json();
        const n = (d.data||[]).length;
        found += n;
        ok++;
        clCounts[key] = n;  // guardar directamente (NO leer del DOM badge)
        // Actualizar badge DOM si existe
        const badge = document.getElementById('cl-badge-' + key);
        if (badge) {{
          badge.textContent = n > 0 ? (n + ' papers SS') : 'Sin resultados SS';
          badge.style.color = n >= 3 ? '#00ff88' : (n > 0 ? '#ffd54f' : '#ff3d5a');
        }}
      }} catch(e) {{ fail++; }}
    }}
    if (i < keys.length-1) await new Promise(function(rv) {{ setTimeout(rv, 500); }});
  }}

  _clLastAt    = Date.now();
  _clSearching = false;
  setBtnState('btn-clasicos','cl-status',false,'','📚 Verificar en SS');

  const hora = new Date().toLocaleTimeString('es',{{hour:'2-digit',minute:'2-digit'}});
  if (fail === keys.length) {{
    showStatus('cl-status','#ff9800',
      '<span style="color:#ff9800">⚠ Sin respuesta de Semantic Scholar · ' + hora + '</span>'
      + '<span style="font-size:.85em;color:#cc6600;display:block;margin-top:3px;">Sin conexión o API caída — intenta en 1-2 minutos.</span>', 0);
  }} else {{
    const extra = fail>0 ? (' <span style="color:#ff9800;font-size:.85em">(' + fail + ' sin respuesta)</span>') : '';
    showStatus('cl-status', found>0?'#ffd54f':'var(--dim)',
      '<span style="color:' + (found>0?'#ffd54f':'var(--dim)') + '">✓ ' + found + ' papers en ' + ok + ' obras verificadas · ' + hora + '</span>' + extra,
      found>0 ? 0 : 9000);

    // ── Persistir historial ────────────────────────────────────────────────
    if (ok > 0) {{
      const tsISO   = new Date().toISOString();
      const obrasData = {{}};
      keys.forEach(function(k) {{
        obrasData[k] = {{ n_papers: clCounts[k] || 0 }};  // usa variable local, no DOM
      }});
      const entrada = {{
        timestamp:    tsISO,
        total_papers: found,
        obras:        obrasData
      }};

      // 1. localStorage
      _lsSave(_LS_CLASICOS, entrada);

      // 2. Flask (silencioso)
      fetch('http://localhost:5050/api/clasicos_historial', {{
        method:'POST', headers:{{'Content-Type':'application/json'}},
        body: JSON.stringify(entrada)
      }}).catch(function(){{}});

      // 3. Actualizar panel historial
      const panel = document.getElementById('cl-historial-panel');
      if (panel) _renderClHistorial(panel, _lsLoad(_LS_CLASICOS));
    }}
  }}
}}

// ── AUTO-RECARGA via sentinel lum_build_vitae.txt (funciona con file://) ─────
// Python escribe ese archivo cada vez que regenera el HTML (solo ~20 bytes)
const _BUILD_TS = '{now_str}';
(function() {{
  let _arKnown = _BUILD_TS.trim(), _arNotif = null;
  // Sentinel PROPIO del dashboard (distinto al del mapa para evitar loops)
  const _arSentinel = location.href.replace(/[^/\\\\]*$/, 'lum_build_vitae.txt');
  async function _checkReload() {{
    try {{
      const r   = await fetch(_arSentinel + '?_=' + Date.now());
      const txt = (await r.text()).trim();
      if (!txt) return;
      if (_arKnown && txt !== _arKnown) {{
        if (_arNotif) return;
        _arKnown = txt;
        _arNotif = document.createElement('div');
        _arNotif.innerHTML = '🔄 Dashboard actualizado — recargando en <b id="_ar_cnt">5</b>s &nbsp;<span style="cursor:pointer;color:#3a6080;" onclick="this.parentElement.remove();">✕</span>';
        _arNotif.style.cssText = 'position:fixed;top:12px;right:12px;background:#0a1a2a;border:1px solid #00e5ff66;color:#00e5ffcc;padding:10px 16px;border-radius:6px;font-size:.72rem;z-index:9999;font-family:monospace;box-shadow:0 4px 20px #000a;';
        document.body.appendChild(_arNotif);
        let cnt = 5;
        const tick = setInterval(() => {{
          cnt--;
          const el = document.getElementById('_ar_cnt');
          if (el) el.textContent = cnt;
          if (cnt <= 0) {{ clearInterval(tick); location.reload(); }}
        }}, 1000);
      }}
      if (!_arKnown) _arKnown = txt;
    }} catch(e) {{}}
  }}
  setTimeout(_checkReload, 2000);
  setInterval(_checkReload, 10000);
}})();
</script>
</body>
</html>"""

    OUT_FILE.write_text(page, encoding="utf-8")
    # Sentinel PROPIO del dashboard (evita conflicto con el del mapa)
    sentinel = OUT_FILE.parent / "lum_build_vitae.txt"
    sentinel.write_text(now_str, encoding="utf-8")
    print(f"[OK] Dashboard generado → {OUT_FILE}")
    return OUT_FILE

if __name__ == "__main__":
    p = generar()
    import webbrowser, sys
    if "--no-open" not in sys.argv:
        webbrowser.open(str(p))
