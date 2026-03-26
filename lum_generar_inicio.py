#!/usr/bin/env python3
"""
Genera 🏠 INICIO.html con datos embebidos del último estado del sistema.
No requiere servidor ni fetch() — funciona con doble clic en cualquier navegador.
"""
import json, pathlib, datetime, html as html_mod

BASE        = pathlib.Path(__file__).parent
ESTADO_FILE = BASE / "lum_vitae_estado.json"
MAPA_FILE   = BASE / "lum_mapa_cierres.json"
OUT_FILE    = BASE / "🏠 INICIO.html"

def tama_face(estado, color, size=52):
    """SVG carita animada para badge de inicio (tamaño compacto)."""
    # Versión compacta del robot pixel — misma lógica, tamaño reducido
    # Reutiliza la misma función del dashboard pero con viewBox fijo 0 0 90 90
    s = size / 90
    uid = estado[:2] + "i"   # ID único para filtros (sufijo 'i' = inicio)

    def sc(v): return round(v * s, 1)

    hx, hy, hw, hh, hr = 12, 6, 66, 52, 6
    e1x, e2x, ey_b, ew, eh = 21, 51, 21, 18, 9
    mx, my = 45, 41
    bx, by, bw, bh = 29, 60, 32, 15
    lx1, lx2, ly, lw, lh = 32, 49, 76, 10, 8

    blur = max(0.8, 2.0 * s)
    glow_f = (
        f'<defs><filter id="g{uid}" x="-60%" y="-60%" width="220%" height="220%">'
        f'<feGaussianBlur in="SourceGraphic" stdDeviation="{blur:.1f}" result="b"/>'
        f'<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
        f'</filter></defs>'
    )
    b = sc(5); t = sc(1.8); bop = "0.85" if estado != "INERTE" else "0.40"
    corners = (
        f'<rect x="{sc(hx)}" y="{sc(hy)}" width="{b}" height="{t}" fill="{color}" opacity="{bop}"/>'
        f'<rect x="{sc(hx)}" y="{sc(hy)}" width="{t}" height="{b}" fill="{color}" opacity="{bop}"/>'
        f'<rect x="{sc(hx+hw)-b}" y="{sc(hy)}" width="{b}" height="{t}" fill="{color}" opacity="{bop}"/>'
        f'<rect x="{sc(hx+hw)-t}" y="{sc(hy)}" width="{t}" height="{b}" fill="{color}" opacity="{bop}"/>'
        f'<rect x="{sc(hx)}" y="{sc(hy+hh)-t}" width="{b}" height="{t}" fill="{color}" opacity="{bop}"/>'
        f'<rect x="{sc(hx)}" y="{sc(hy+hh)-b}" width="{t}" height="{b}" fill="{color}" opacity="{bop}"/>'
        f'<rect x="{sc(hx+hw)-b}" y="{sc(hy+hh)-t}" width="{b}" height="{t}" fill="{color}" opacity="{bop}"/>'
        f'<rect x="{sc(hx+hw)-t}" y="{sc(hy+hh)-b}" width="{t}" height="{b}" fill="{color}" opacity="{bop}"/>'
    )
    if estado == "VIVO":
        eye_s = (
            f'<rect x="{sc(e1x)}" y="{sc(ey_b)}" width="{sc(ew)}" height="{sc(eh)}"'
            f' rx="{sc(2)}" fill="{color}" filter="url(#g{uid})"/>'
            f'<rect x="{sc(e2x)}" y="{sc(ey_b)}" width="{sc(ew)}" height="{sc(eh)}"'
            f' rx="{sc(2)}" fill="{color}" filter="url(#g{uid})"/>'
            f'<path d="M {sc(mx-14)},{sc(my)} Q {sc(mx)},{sc(my+12)} {sc(mx+14)},{sc(my)}"'
            f' fill="none" stroke="{color}" stroke-width="{sc(3)}" stroke-linecap="round"/>'
        )
        ho = "1"
    elif estado == "EMERGENTE":
        eye_s = (
            f'<rect x="{sc(e1x)}" y="{sc(ey_b+2)}" width="{sc(ew)}" height="{sc(eh)}"'
            f' rx="{sc(2)}" fill="{color}" opacity="0.9"/>'
            f'<rect x="{sc(e2x)}" y="{sc(ey_b-2)}" width="{sc(ew)}" height="{sc(eh)}"'
            f' rx="{sc(2)}" fill="{color}" opacity="0.9"/>'
            f'<path d="M {sc(mx-11)},{sc(my+1)} Q {sc(mx)},{sc(my+9)} {sc(mx+11)},{sc(my+1)}"'
            f' fill="none" stroke="{color}" stroke-width="{sc(2.5)}" stroke-linecap="round"/>'
        )
        ho = "0.92"
    elif estado == "LATENTE":
        eye_s = (
            f'<rect x="{sc(e1x)}" y="{sc(ey_b+3)}" width="{sc(ew)}" height="{sc(eh*0.45)}"'
            f' rx="{sc(1.5)}" fill="{color}" opacity="0.55"/>'
            f'<rect x="{sc(e2x)}" y="{sc(ey_b+3)}" width="{sc(ew)}" height="{sc(eh*0.45)}"'
            f' rx="{sc(1.5)}" fill="{color}" opacity="0.55"/>'
            f'<line x1="{sc(mx-9)}" y1="{sc(my+4)}" x2="{sc(mx+9)}" y2="{sc(my+4)}"'
            f' stroke="{color}" stroke-width="{sc(2.5)}" stroke-linecap="round" opacity="0.55"/>'
            f'<text x="{sc(68)}" y="{sc(14)}" font-size="{sc(9):.0f}" fill="{color}" opacity="0.5"'
            f' font-family="monospace" font-weight="bold">z</text>'
        )
        ho = "0.75"
    else:
        eye_s = (
            f'<line x1="{sc(e1x)}" y1="{sc(ey_b)}" x2="{sc(e1x+ew)}" y2="{sc(ey_b+eh)}"'
            f' stroke="{color}" stroke-width="{sc(3)}" stroke-linecap="round" opacity="0.8"/>'
            f'<line x1="{sc(e1x+ew)}" y1="{sc(ey_b)}" x2="{sc(e1x)}" y2="{sc(ey_b+eh)}"'
            f' stroke="{color}" stroke-width="{sc(3)}" stroke-linecap="round" opacity="0.8"/>'
            f'<line x1="{sc(e2x)}" y1="{sc(ey_b)}" x2="{sc(e2x+ew)}" y2="{sc(ey_b+eh)}"'
            f' stroke="{color}" stroke-width="{sc(3)}" stroke-linecap="round" opacity="0.8"/>'
            f'<line x1="{sc(e2x+ew)}" y1="{sc(ey_b)}" x2="{sc(e2x)}" y2="{sc(ey_b+eh)}"'
            f' stroke="{color}" stroke-width="{sc(3)}" stroke-linecap="round" opacity="0.8"/>'
            f'<path d="M {sc(mx-12)},{sc(my+8)} Q {sc(mx)},{sc(my+1)} {sc(mx+12)},{sc(my+8)}"'
            f' fill="none" stroke="{color}" stroke-width="{sc(2.5)}" stroke-linecap="round" opacity="0.7"/>'
        )
        ho = "0.6"
    head_r = (
        f'<rect x="{sc(hx-2)}" y="{sc(hy-2)}" width="{sc(hw+4)}" height="{sc(hh+4)}"'
        f' rx="{sc(hr+1)}" fill="{color}" opacity="0.10" filter="url(#g{uid})"/>'
        f'<rect x="{sc(hx)}" y="{sc(hy)}" width="{sc(hw)}" height="{sc(hh)}"'
        f' rx="{sc(hr)}" fill="#090d14" stroke="{color}" stroke-width="{sc(2)}" opacity="{ho}"/>'
    )
    body_r = (
        f'<rect x="{sc(bx)}" y="{sc(by)}" width="{sc(bw)}" height="{sc(bh)}"'
        f' rx="{sc(3)}" fill="#090d14" stroke="{color}" stroke-width="{sc(1.5)}" opacity="{ho}"/>'
        f'<rect x="{sc(lx1)}" y="{sc(ly)}" width="{sc(lw)}" height="{sc(lh)}"'
        f' rx="{sc(2)}" fill="#090d14" stroke="{color}" stroke-width="{sc(1.5)}" opacity="{ho}"/>'
        f'<rect x="{sc(lx2)}" y="{sc(ly)}" width="{sc(lw)}" height="{sc(lh)}"'
        f' rx="{sc(2)}" fill="#090d14" stroke="{color}" stroke-width="{sc(1.5)}" opacity="{ho}"/>'
    )
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 90 90"'
        f' xmlns="http://www.w3.org/2000/svg" style="display:inline-block;vertical-align:middle;">'
        f'{glow_f}{head_r}{corners}{eye_s}{body_r}</svg>'
    )


def leer_estado():
    try: return json.loads(ESTADO_FILE.read_text())
    except: return {}

def leer_mapa():
    try: return json.loads(MAPA_FILE.read_text())
    except: return {}

def generar():
    e    = leer_estado()
    mapa_data = leer_mapa()
    mapa  = mapa_data.get("mapa", {})
    resumen = mapa_data.get("resumen", {})
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    # ── Estado del sistema ──────────────────────────────────────────────────
    hist_ECE  = e.get("historial_ECE", [1.0])
    ece_actual = hist_ECE[-1] if hist_ECE else 1.0
    spawns     = e.get("n_spawns_total") or 0
    # La clave en estado.json es "n_hashes" (el runner escribe ese nombre exacto)
    n_hashes   = int(e.get("n_hashes") or 0)
    n_run      = e.get("n_run") or 0
    hist_Brier = e.get("historial_Brier", [1.0])
    brier_a    = hist_Brier[-1] if hist_Brier else 1.0
    brier_p    = hist_Brier[-2] if len(hist_Brier) >= 2 else brier_a

    # Homeostasis: ventana de 5 ciclos (igual lógica que el dashboard)
    ece_vent   = hist_ECE[-5:]   if len(hist_ECE)   >= 2 else hist_ECE
    brier_vent = hist_Brier[-6:] if len(hist_Brier) >= 2 else hist_Brier
    cond1 = (any(v <= 0.05 for v in ece_vent) and
             any(brier_vent[i] <= brier_vent[i-1] for i in range(1, len(brier_vent))))
    cond2 = spawns > 0
    cond3 = n_hashes > 0
    cond4 = n_run >= 1
    n_vivo = sum([cond1, cond2, cond3, cond4])

    # 4 estados (igual que el dashboard)
    if n_vivo >= 3:
        vita_color, vita_estado, vita_text = "#00ff88", "VIVO", "VIVO"
        vita_msg = "Sistema en plena actividad vital."
    elif n_vivo == 2:
        vita_color, vita_estado, vita_text = "#ffd54f", "EMERGENTE", "EMERGENTE"
        vita_msg = "Sistema emergente — ciclos activos, convergencia en curso."
    elif n_vivo == 1:
        vita_color, vita_estado, vita_text = "#ff9800", "LATENTE", "LATENTE"
        vita_msg = "Sistema latente — actividad mínima detectada."
    else:
        vita_color, vita_estado, vita_text = "#ff3d5a", "INERTE", "INERTE"
        vita_msg = "Sistema inerte — aún no ha corrido."
    vita_face = tama_face(vita_estado, vita_color, size=44)
    ts_run = e.get("timestamp_ultimo_run", "—")[:16]

    # ── Ranking del mapa de cierres ─────────────────────────────────────────
    C = {"GREEN":"#00ff88","AMBER":"#ffd54f","RED":"#ff3d5a","N/A":"#3a5a7a"}
    E = {"GREEN":"🟢","AMBER":"🟡","RED":"🔴","N/A":"⬜"}
    orden = sorted(mapa.items(), key=lambda x: x[1]["resultado"]["p_sintetico"], reverse=True)

    scores_html = ""
    for clave, disc in orden:
        res  = disc["resultado"]
        meta = disc["meta"]
        p    = res["p_sintetico"]
        sc   = C.get(res["semaforo"], "#3a5a7a")
        em   = E.get(res["semaforo"], "?")
        pct  = f"{p*100:.0f}%"
        scores_html += f"""
        <div style="display:flex;align-items:center;gap:10px;padding:7px 0;border-bottom:1px solid #131f2e;">
          <span style="font-size:1.1rem;">{meta['icono']}</span>
          <div style="flex:1;min-width:0;">
            <div style="font-size:.8rem;font-weight:bold;color:{sc};">{html_mod.escape(meta['nombre'])}</div>
            <div style="height:4px;background:#1a2a3a;border-radius:2px;margin-top:3px;">
              <div style="width:{pct};height:100%;background:{sc};border-radius:2px;"></div>
            </div>
          </div>
          <span style="font-size:.72rem;color:{sc};font-weight:bold;white-space:nowrap;">{em} {p:.3f}</span>
        </div>"""

    ult_exp = resumen.get("ultima_exploracion","—")[:10]
    n_papers = resumen.get("total_papers", 0)
    n_ens    = resumen.get("total_ensayos", 0)
    res_global = html_mod.escape(resumen.get("resumen_global","")[:300])

    page = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="refresh" content="120">
<title>PROYECTO MINERVA · ALFA LUM-vitae — Inicio</title>
<style>
  :root {{
    --bg:#090d14; --panel:#0d1520; --border:#1a2a3a;
    --cyan:#00e5ff; --green:#00ff88; --yellow:#ffd54f;
    --dim:#3a5a7a; --text:#c8dff0; --muted:#4a7090;
  }}
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ background:var(--bg); color:var(--text); font-family:'Segoe UI',sans-serif; min-height:100vh; padding:36px 24px; }}

  .header {{ text-align:center; margin-bottom:40px; }}
  .header h1 {{ font-size:2rem; color:var(--cyan); letter-spacing:3px; font-family:'Courier New',monospace; }}
  .header p {{ color:var(--muted); margin-top:8px; font-size:.85rem; }}
  .ts-badge {{ display:inline-block; margin-top:10px; font-size:.62rem; color:var(--muted);
    border:1px solid var(--border); padding:3px 12px; border-radius:20px; font-family:'Courier New',monospace; }}

  .layout {{ display:grid; grid-template-columns:320px 1fr; gap:20px; max-width:1100px; margin:0 auto; }}
  @media(max-width:860px) {{ .layout {{ grid-template-columns:1fr; }} }}

  .panel {{ background:var(--panel); border:1px solid var(--border); border-radius:12px; padding:22px; position:relative; overflow:hidden; margin-bottom:16px; }}
  .panel::before {{ content:''; position:absolute; top:0; left:0; right:0; height:2px; background:linear-gradient(90deg,var(--cyan),transparent); }}
  .panel-title {{ font-size:.62rem; color:var(--muted); letter-spacing:2px; text-transform:uppercase;
    margin-bottom:14px; font-family:'Courier New',monospace; }}

  .card-link {{ background:var(--panel); border:1px solid var(--border); border-radius:12px;
    padding:22px; text-decoration:none; display:block; position:relative; overflow:hidden;
    margin-bottom:14px; transition:transform .15s, border-color .15s; cursor:pointer; }}
  .card-link:hover {{ transform:translateY(-2px); border-color:var(--cyan); }}
  .card-link::before {{ content:''; position:absolute; top:0; left:0; right:0; height:3px; }}
  .card-link.verde::before  {{ background:var(--green); }}
  .card-link.cyan::before   {{ background:var(--cyan); }}
  .card-link.yellow::before {{ background:var(--yellow); }}
  .card-link.morado::before {{ background:#b39ddb; }}

  .card-icon  {{ font-size:2.2rem; margin-bottom:10px; }}
  .card-title {{ font-size:1.05rem; font-weight:bold; color:var(--text); margin-bottom:5px; }}
  .card-desc  {{ font-size:.78rem; color:var(--muted); line-height:1.6; }}
  .card-action {{ margin-top:12px; font-size:.72rem; font-weight:bold; }}
  .card-link.verde  .card-action {{ color:var(--green); }}
  .card-link.cyan   .card-action {{ color:var(--cyan); }}
  .card-link.yellow .card-action {{ color:var(--yellow); }}
  .card-link.morado .card-action {{ color:#b39ddb; }}

  .vita-badge {{
    display:inline-flex; align-items:center; gap:8px;
    font-size:1rem; font-weight:bold; letter-spacing:2px;
    padding:6px 16px; border-radius:8px; margin-bottom:12px;
    font-family:'Courier New',monospace;
    border:1px solid {vita_color}44; background:{vita_color}11; color:{vita_color};
  }}

  .paso {{ display:flex; gap:14px; align-items:flex-start; margin-bottom:14px; padding-bottom:14px; border-bottom:1px solid var(--border); }}
  .paso:last-child {{ border-bottom:none; margin-bottom:0; padding-bottom:0; }}
  .num {{ width:28px; height:28px; border-radius:50%; flex-shrink:0; display:flex;
    align-items:center; justify-content:center; font-weight:bold; font-size:.85rem;
    background:var(--cyan); color:#090d14; }}
  .paso-body {{ flex:1; }}
  .paso-title {{ font-weight:bold; color:var(--text); margin-bottom:3px; font-size:.88rem; }}
  .paso-desc  {{ font-size:.75rem; color:var(--muted); line-height:1.6; }}
  .tag {{ display:inline-block; font-size:.6rem; padding:2px 8px; border-radius:10px; margin-top:5px; font-weight:bold; }}
  .tag-auto   {{ background:rgba(0,255,136,.12); color:var(--green);  border:1px solid rgba(0,255,136,.3); }}
  .tag-manual {{ background:rgba(0,229,255,.12); color:var(--cyan);   border:1px solid rgba(0,229,255,.3); }}

  .section-title {{ font-size:.6rem; letter-spacing:3px; color:var(--dim); text-transform:uppercase;
    margin:28px 0 14px; border-top:1px solid var(--border); padding-top:14px;
    font-family:'Courier New',monospace; max-width:1100px; margin-left:auto; margin-right:auto; }}

  table {{ width:100%; border-collapse:collapse; font-size:.76rem; }}
  th {{ text-align:left; padding:7px 6px; color:var(--cyan); font-size:.65rem;
    letter-spacing:1px; border-bottom:1px solid var(--border); }}
  td {{ padding:7px 6px; border-bottom:1px solid #131f2e; vertical-align:top; }}
  td:first-child {{ font-family:'Courier New',monospace; }}

  .footer {{ text-align:center; margin-top:40px; font-size:.6rem; color:var(--dim); letter-spacing:2px; font-family:'Courier New',monospace; }}
</style>
</head>
<body>

<!-- CABECERA -->
<div class="header">
  <h1>◈ PROYECTO MINERVA</h1>
  <p>ALFA LUM-vitae vΩ.4 · Mapa de Cierres Categoriales · Materialismo Filosófico</p>
  <div class="ts-badge">📸 Generado {now_str}</div>
</div>

<!-- LAYOUT PRINCIPAL -->
<div class="layout">

  <!-- SIDEBAR: Estado + Ranking -->
  <div>

    <!-- Estado del sistema -->
    <div class="panel">
      <div class="panel-title">Estado del sistema</div>
      <div class="vita-badge">{vita_face} {vita_text}</div>
      <div style="font-size:.72rem;color:var(--muted);line-height:1.7;margin-bottom:10px;">
        {vita_msg}<br>
        <b style="color:var(--text);">{n_vivo}/4</b> condiciones de vida activas
        (<span style="color:#00ff88;">Reprod.</span>
         <span style="color:#3a7070;"> · Trazab.</span>
         <span style="color:#3a7070;"> · Homeost.</span>
         <span style="color:#3a7070;"> · Autonom.</span>).<br>
        Último run: <span style="color:var(--text);">{ts_run}</span><br>
        Runs: <span style="color:var(--cyan);font-family:'Courier New',monospace;">{n_run}</span> ·
        Ciclos: <span style="color:var(--cyan);font-family:'Courier New',monospace;">{e.get('n_ciclos_total',0)}</span> ·
        Hashes: <span style="color:var(--cyan);font-family:'Courier New',monospace;">{n_hashes}</span>
      </div>
    </div>

    <!-- Ranking de cierres -->
    <div class="panel">
      <div class="panel-title">Ranking — Cierres categoriales</div>
      {scores_html if scores_html else '<div style="font-size:.72rem;color:var(--muted);">Sin datos aún. Ejecuta el sistema para ver el ranking.</div>'}
      <div style="margin-top:12px;font-size:.62rem;color:var(--dim);line-height:1.5;">
        {res_global}
      </div>
      <div style="margin-top:8px;font-size:.58rem;color:#2a4a5a;">
        {n_papers} papers · {n_ens} ensayos propios · Última exploración: {ult_exp}
      </div>
    </div>

  </div>

  <!-- DERECHA: Documentos + Guía -->
  <div>

    <!-- Dashboards principales -->
    <div style="margin-bottom:4px;font-size:.6rem;color:var(--dim);letter-spacing:2px;font-family:'Courier New',monospace;">◈ ABRE ESTOS PARA VER TODO</div>

    <a class="card-link verde" href="lum_vitae_dashboard.html">
      <div class="card-icon">🧬</div>
      <div class="card-title">Dashboard — Vida Digital</div>
      <div class="card-desc">
        ¿Está vivo el sistema? Veredicto VIVO / NO VIVO en tiempo real,
        gráficas de ECE y κ_conf, flechas de tendencia, hashes SHA-256
        y el reporte completo del último run.
      </div>
      <div class="card-action">→ Abrir lum_vitae_dashboard.html</div>
    </a>

    <a class="card-link cyan" href="lum_mapa_cierres.html">
      <div class="card-icon">◈</div>
      <div class="card-title">Mapa de Cierres Categoriales</div>
      <div class="card-desc">
        ¿Qué ciencias tienen cierre según Bueno? Ranking de 6 dominios
        con semáforo 🟢🟡🔴, veredictos en lenguaje llano, papers reales
        con enlace, tendencias y corpus propio de Jules.
      </div>
      <div class="card-action">→ Abrir lum_mapa_cierres.html</div>
    </a>

    <a class="card-link yellow" href="INFORME_CIERRES.docx">
      <div class="card-icon">📄</div>
      <div class="card-title">Informe Word — Descubrimientos</div>
      <div class="card-desc">
        Análisis completo de los 6 dominios: dictámenes, hallazgos clave,
        papers encontrados, tendencias 2023-2025 y próximos pasos.
        136 párrafos validados.
      </div>
      <div class="card-action">→ Abrir INFORME_CIERRES.docx</div>
    </a>

    <!-- Guía de uso -->
    <div class="panel" style="margin-top:8px;">
      <div class="panel-title">¿Cómo funciona?</div>

      <div class="paso">
        <div class="num">1</div>
        <div class="paso-body">
          <div class="paso-title">El sistema corre solo — no tienes que hacer nada</div>
          <div class="paso-desc">
            Cada hora, una tarea automática ejecuta el runner, actualiza los datos
            y regenera los dashboards HTML. Solo abre el HTML que quieras ver y presiona
            <strong>F5</strong> para actualizar.
          </div>
          <span class="tag tag-auto">Automático — cada hora</span>
        </div>
      </div>

      <div class="paso">
        <div class="num">2</div>
        <div class="paso-body">
          <div class="paso-title">Para explorar ciencias nuevas — pídele a Claude</div>
          <div class="paso-desc">
            El mapa de cierres se actualiza cuando Claude hace búsquedas reales
            en bases de datos académicas. Di: <em>"actualiza el mapa de cierres"</em>
            o <em>"explora [disciplina]"</em> y lo hace al momento.
          </div>
          <span class="tag tag-manual">Manual — cuando quieras</span>
        </div>
      </div>

      <div class="paso">
        <div class="num">3</div>
        <div class="paso-body">
          <div class="paso-title">Los tres archivos que importan</div>
          <div class="paso-desc">
            Solo necesitas abrir los <strong>2 HTML</strong> y el <strong>informe Word</strong>.
            Los archivos .py y .json son el motor — se actualizan solos y no necesitas tocarlos.
          </div>
          <span class="tag tag-auto">Los .py y .json se actualizan automáticamente</span>
        </div>
      </div>
    </div>

  </div>
</div>

<!-- TABLA DE ARCHIVOS -->
<div class="section-title">◈ Mapa de archivos — qué es qué</div>
<div class="panel" style="max-width:1100px;margin:0 auto;">
  <table>
    <thead>
      <tr>
        <th>Archivo</th>
        <th>Para qué sirve</th>
        <th>¿Lo abres tú?</th>
      </tr>
    </thead>
    <tbody>
      <tr><td style="color:#00ff88;">🏠 INICIO.html</td><td>Esta página — punto de entrada al proyecto</td><td style="color:#00ff88;">✓ Sí, esta misma</td></tr>
      <tr><td style="color:#00ff88;">🧬 lum_vitae_dashboard.html</td><td>Ver si el sistema está VIVO + gráficas + hashes</td><td style="color:#00ff88;">✓ Sí</td></tr>
      <tr><td style="color:#00e5ff;">◈ lum_mapa_cierres.html</td><td>Ver el mapa de cierres por dominio científico</td><td style="color:#00ff88;">✓ Sí</td></tr>
      <tr><td style="color:#ffd54f;">📄 INFORME_CIERRES.docx</td><td>Análisis escrito completo de los hallazgos (136 párrafos)</td><td style="color:#00ff88;">✓ Sí</td></tr>
      <tr><td style="color:#3a5a7a;">⚡ EJECUTAR AHORA.bat</td><td>Doble clic para correr el sistema manualmente (Windows)</td><td style="color:#ffd54f;">Opcional</td></tr>
      <tr><td style="color:#2a4a6a;">lum_vitae_runner.py</td><td>Motor principal — bucle vital cada hora</td><td style="color:#3a5a7a;">No, corre solo</td></tr>
      <tr><td style="color:#2a4a6a;">lum_mapa_cierres.py</td><td>Analizador de cierre por dominio científico</td><td style="color:#3a5a7a;">No, lo llama Claude</td></tr>
      <tr><td style="color:#2a4a6a;">lum_vitae_generar_html.py</td><td>Genera el dashboard de vida digital</td><td style="color:#3a5a7a;">No, corre automático</td></tr>
      <tr><td style="color:#2a4a6a;">lum_generar_inicio.py</td><td>Genera esta página de inicio</td><td style="color:#3a5a7a;">No, corre automático</td></tr>
      <tr><td style="color:#2a4a6a;">lum_vitae_estado.json</td><td>Memoria del sistema entre runs</td><td style="color:#3a5a7a;">No, es del motor</td></tr>
      <tr><td style="color:#2a4a6a;">lum_mapa_cierres.json</td><td>Datos del mapa de cierres (se actualizan con cada exploración)</td><td style="color:#3a5a7a;">No, es del motor</td></tr>
      <tr><td style="color:#2a4a6a;">lum_vitae_reporte.txt</td><td>Log del último run (visible en el dashboard)</td><td style="color:#4a7090;">Opcional</td></tr>
    </tbody>
  </table>
</div>

<div class="footer">
  ALFA LUM-vitae vΩ.4 · LUM-PE vΩ.2026-02 · Proyecto MINERVA · Julio David Rojas
</div>

</body>
</html>"""

    OUT_FILE.write_text(page, encoding="utf-8")
    print(f"[OK] INICIO.html generado → {OUT_FILE}")
    return OUT_FILE

if __name__ == "__main__":
    generar()
