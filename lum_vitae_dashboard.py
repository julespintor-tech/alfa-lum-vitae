#!/usr/bin/env python3
"""
ALFA LUM-vitae vΩ.4 — Dashboard Visual
Servidor local: http://localhost:5050
Ejecuta: python3 lum_vitae_dashboard.py
"""
import json, pathlib, threading, webbrowser, time
from flask import Flask, jsonify, render_template_string

BASE = pathlib.Path(__file__).parent
ESTADO_FILE  = BASE / "lum_vitae_estado.json"
LEDGER_FILE  = BASE / "lum_vitae_ledger_meta.ndjson"
REPORTE_FILE = BASE / "lum_vitae_reporte.txt"

app = Flask(__name__)

def leer_estado():
    try:
        return json.loads(ESTADO_FILE.read_text())
    except Exception:
        return {}

def leer_ledger(ultimos=200):
    lineas = []
    try:
        texto = LEDGER_FILE.read_text().strip().splitlines()
        for l in texto[-ultimos:]:
            try:
                lineas.append(json.loads(l))
            except Exception:
                pass
    except Exception:
        pass
    return lineas

def leer_reporte():
    try:
        return REPORTE_FILE.read_text()
    except Exception:
        return "Sin reporte aún."

# ─── API ────────────────────────────────────────────────────────────────────

@app.route("/api/estado")
def api_estado():
    e = leer_estado()
    ledger = leer_ledger(200)

    # Series temporales del ledger
    ece_series    = [round(r["ECE"],    5) for r in ledger]
    brier_series  = [round(r["Brier"],  5) for r in ledger]
    kappa_series  = [round(r["kappa_conf"], 4) for r in ledger]
    L_series      = [round(r["L_norm"], 5) for r in ledger]
    s_series      = [round(r["S_t"],    4) for r in ledger]
    labels        = [f"#{r['ciclo']}" for r in ledger]
    decision_list = [r.get("decision","?") for r in ledger]
    hash_list     = [r.get("hash","")[:8] for r in ledger[-10:]]

    # Condiciones de vida
    hist_ECE = e.get("historial_ECE", [1.0])
    hist_Brier = e.get("historial_Brier", [1.0])
    ece_actual = hist_ECE[-1] if hist_ECE else 1.0
    brier_actual = hist_Brier[-1] if hist_Brier else 1.0
    brier_prev   = hist_Brier[-2] if len(hist_Brier) >= 2 else brier_actual
    spawns = e.get("n_spawns_total", 0)
    n_hashes = e.get("n_hashes_total", len(ledger))

    cond1 = ece_actual <= 0.05 and brier_actual <= brier_prev
    cond2 = spawns > 0
    cond3 = n_hashes > 0
    cond4 = e.get("n_run", 0) >= 1
    vivo  = sum([cond1, cond2, cond3, cond4]) >= 3

    return jsonify({
        "n_run":        e.get("n_run", 0),
        "n_ciclos":     e.get("n_ciclos_total", 0),
        "n_hashes":     n_hashes,
        "spawns":       spawns,
        "ECE":          ece_actual,
        "Brier":        brier_actual,
        "kappa":        e.get("historial_kappa", [0])[-1],
        "L_norm":       e.get("historial_L_norm", [0])[-1],
        "S_t":          e.get("historial_S_t", [0])[-1],
        "veredicto":    vivo,
        "condiciones":  [cond1, cond2, cond3, cond4],
        "n_vivo":       sum([cond1, cond2, cond3, cond4]),
        "timestamp":    e.get("timestamp_ultimo_run", "—"),
        "ece_series":   ece_series,
        "brier_series": brier_series,
        "kappa_series": kappa_series,
        "L_series":     L_series,
        "s_series":     s_series,
        "labels":       labels,
        "decision_list": decision_list,
        "hash_list":    hash_list,
        "pct_psnc":     round(100 * decision_list.count("PSNC") / max(len(decision_list),1), 1),
        "pct_vivo":     round(100 * e.get("n_vivo", e.get("n_run",1)) / max(e.get("n_run",1),1), 1),
    })

@app.route("/api/reporte")
def api_reporte():
    return jsonify({"texto": leer_reporte()})

# ─── DASHBOARD HTML ──────────────────────────────────────────────────────────

TEMPLATE = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ALFA LUM-vitae vΩ.4 — Dashboard</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
  :root {
    --bg:     #090d14;
    --panel:  #0d1520;
    --border: #1a2a3a;
    --cyan:   #00e5ff;
    --green:  #00ff88;
    --red:    #ff3d5a;
    --yellow: #ffd54f;
    --dim:    #3a5a7a;
    --text:   #c8dff0;
    --muted:  #4a7090;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Courier New', monospace;
    min-height: 100vh;
    padding: 20px;
  }

  /* HEADER */
  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border);
    padding-bottom: 14px;
    margin-bottom: 20px;
  }
  .logo { font-size: 1.3rem; color: var(--cyan); letter-spacing: 2px; }
  .logo span { color: var(--muted); font-size: 0.85rem; }
  .refresh-badge {
    font-size: 0.7rem;
    color: var(--muted);
    border: 1px solid var(--border);
    padding: 4px 10px;
    border-radius: 20px;
  }
  #tick { color: var(--green); }

  /* GRID LAYOUT */
  .grid { display: grid; gap: 16px; }
  .row2 { grid-template-columns: 1fr 1fr; }
  .row3 { grid-template-columns: 1fr 1fr 1fr; }
  .row4 { grid-template-columns: repeat(4, 1fr); }

  /* PANEL */
  .panel {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 18px;
    position: relative;
    overflow: hidden;
  }
  .panel::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--cyan), transparent);
  }
  .panel-title {
    font-size: 0.68rem;
    color: var(--muted);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 10px;
  }

  /* VEREDICTO */
  .veredicto-panel {
    text-align: center;
    padding: 30px 18px;
  }
  .veredicto-panel::before {
    background: linear-gradient(90deg, transparent, var(--cyan), transparent);
  }
  .veredicto-glyph {
    font-size: 3.5rem;
    line-height: 1;
    margin-bottom: 8px;
  }
  .veredicto-text {
    font-size: 1.6rem;
    font-weight: bold;
    letter-spacing: 4px;
  }
  .vivo-text  { color: var(--green); text-shadow: 0 0 20px var(--green); }
  .muerto-text { color: var(--red);  text-shadow: 0 0 20px var(--red); }
  .veredicto-sub {
    font-size: 0.75rem;
    color: var(--muted);
    margin-top: 6px;
    letter-spacing: 1px;
  }

  @keyframes pulse-green {
    0%, 100% { box-shadow: 0 0 0 0 rgba(0,255,136,0.3); }
    50%       { box-shadow: 0 0 0 16px rgba(0,255,136,0); }
  }
  @keyframes pulse-red {
    0%, 100% { box-shadow: 0 0 0 0 rgba(255,61,90,0.3); }
    50%       { box-shadow: 0 0 0 16px rgba(255,61,90,0); }
  }
  .veredicto-panel.vivo-panel   { animation: pulse-green 2.5s infinite; }
  .veredicto-panel.muerto-panel { animation: pulse-red 2.5s infinite; }

  /* CONDICIONES */
  .cond-list { display: flex; flex-direction: column; gap: 8px; }
  .cond-item {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 0.78rem;
    padding: 6px 10px;
    border-radius: 6px;
    background: rgba(255,255,255,0.02);
    border: 1px solid var(--border);
  }
  .cond-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
  }
  .dot-ok  { background: var(--green); box-shadow: 0 0 6px var(--green); }
  .dot-fail{ background: var(--red);   box-shadow: 0 0 6px var(--red); }
  .cond-label { flex: 1; color: var(--text); }
  .cond-badge {
    font-size: 0.65rem;
    padding: 2px 6px;
    border-radius: 4px;
    font-weight: bold;
  }
  .badge-ok   { background: rgba(0,255,136,0.15); color: var(--green); border: 1px solid rgba(0,255,136,0.3); }
  .badge-fail { background: rgba(255,61,90,0.15);  color: var(--red);   border: 1px solid rgba(255,61,90,0.3); }

  /* STATS */
  .stat-val {
    font-size: 2rem;
    font-weight: bold;
    color: var(--cyan);
    line-height: 1;
    margin-bottom: 4px;
  }
  .stat-label {
    font-size: 0.65rem;
    color: var(--muted);
    letter-spacing: 1.5px;
  }
  .stat-unit {
    font-size: 0.8rem;
    color: var(--dim);
    margin-left: 2px;
  }

  /* ECE meter */
  .ece-bar-wrap {
    margin-top: 10px;
    position: relative;
    height: 8px;
    background: var(--border);
    border-radius: 4px;
    overflow: hidden;
  }
  .ece-bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.8s ease, background 0.5s;
  }
  .ece-threshold {
    position: absolute;
    top: -2px;
    width: 2px;
    height: 12px;
    background: var(--yellow);
    border-radius: 1px;
  }
  .ece-label-row {
    display: flex;
    justify-content: space-between;
    margin-top: 4px;
    font-size: 0.6rem;
    color: var(--muted);
  }

  /* GAUGE */
  .gauge-wrap { position: relative; width: 90px; margin: 0 auto; }
  .gauge-svg  { width: 90px; height: 50px; overflow: visible; }

  /* CHART container */
  .chart-box { position: relative; height: 180px; }
  .chart-box-tall { position: relative; height: 220px; }

  /* HASH LIST */
  .hash-list { display: flex; flex-direction: column; gap: 4px; margin-top: 6px; }
  .hash-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.65rem;
    color: var(--muted);
    padding: 3px 0;
    border-bottom: 1px solid rgba(255,255,255,0.03);
  }
  .hash-code { color: var(--cyan); font-family: monospace; }

  /* REPORTE */
  #reporte-text {
    font-size: 0.62rem;
    color: var(--muted);
    white-space: pre;
    overflow-x: auto;
    max-height: 200px;
    overflow-y: auto;
    line-height: 1.5;
    padding: 8px;
    background: rgba(0,0,0,0.3);
    border-radius: 6px;
    border: 1px solid var(--border);
  }

  /* TIMESTAMP */
  .ts { font-size: 0.65rem; color: var(--dim); margin-top: 10px; }

  /* SEPARADOR */
  .section-title {
    font-size: 0.65rem;
    letter-spacing: 3px;
    color: var(--dim);
    text-transform: uppercase;
    margin: 20px 0 10px;
    border-top: 1px solid var(--border);
    padding-top: 14px;
  }

  canvas { max-width: 100%; }

  @media (max-width: 800px) {
    .row2, .row3, .row4 { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>

<header>
  <div>
    <div class="logo">ALFA LUM-vitae <span style="color:var(--cyan)">vΩ.4</span></div>
    <div style="font-size:0.65rem; color:var(--dim); margin-top:2px;">
      Materialismo Filosófico · Meta-aprendizaje continuo
    </div>
  </div>
  <div class="refresh-badge">⟳ auto-refresh 30s &nbsp;|&nbsp; <span id="tick">●</span> <span id="last-update">—</span></div>
</header>

<!-- ROW 1: Veredicto + Condiciones + Stats principales -->
<div class="grid row3">

  <!-- VEREDICTO -->
  <div class="panel veredicto-panel" id="veredicto-panel">
    <div class="panel-title">Veredicto vital</div>
    <div class="veredicto-glyph" id="vglyph">🔄</div>
    <div class="veredicto-text" id="vtext">—</div>
    <div class="veredicto-sub" id="vsub">cargando...</div>
  </div>

  <!-- CONDICIONES -->
  <div class="panel">
    <div class="panel-title">Condiciones de vida digital</div>
    <div class="cond-list">
      <div class="cond-item">
        <div class="cond-dot" id="dot1"></div>
        <div class="cond-label">1. Homeostasis (ECE≤0.05)</div>
        <span class="cond-badge" id="badge1">—</span>
      </div>
      <div class="cond-item">
        <div class="cond-dot" id="dot2"></div>
        <div class="cond-label">2. Reproducción (δ_hist>0.4)</div>
        <span class="cond-badge" id="badge2">—</span>
      </div>
      <div class="cond-item">
        <div class="cond-dot" id="dot3"></div>
        <div class="cond-label">3. Trazabilidad (SHA-256)</div>
        <span class="cond-badge" id="badge3">—</span>
      </div>
      <div class="cond-item">
        <div class="cond-dot" id="dot4"></div>
        <div class="cond-label">4. Autonomía (72h loop)</div>
        <span class="cond-badge" id="badge4">—</span>
      </div>
    </div>
    <div class="ts">Último run: <span id="ts-run">—</span></div>
  </div>

  <!-- STATS VITALES -->
  <div class="panel">
    <div class="panel-title">Métricas vitales</div>

    <!-- ECE con barra -->
    <div style="margin-bottom:14px;">
      <div style="display:flex; justify-content:space-between; align-items:baseline;">
        <div class="stat-label">ECE (Error Calibración)</div>
        <div style="font-size:1.4rem; font-weight:bold;" id="ece-val">—</div>
      </div>
      <div class="ece-bar-wrap">
        <div class="ece-bar-fill" id="ece-bar" style="width:0%;"></div>
        <div class="ece-threshold" id="ece-thresh" style="left:5%;"></div>
      </div>
      <div class="ece-label-row"><span>0</span><span>umbral 0.05</span><span>1.0</span></div>
    </div>

    <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
      <div>
        <div class="stat-val" id="kappa-val">—</div>
        <div class="stat-label">κ_conf</div>
      </div>
      <div>
        <div class="stat-val" id="L-val">—</div>
        <div class="stat-label">𝓛* función vital</div>
      </div>
      <div>
        <div class="stat-val" id="S-val">—</div>
        <div class="stat-label">S_t memoria</div>
      </div>
      <div>
        <div class="stat-val" id="spawns-val">—</div>
        <div class="stat-label">Spawns (hijos)</div>
      </div>
    </div>
  </div>

</div>

<!-- ROW 2: Counters -->
<div class="grid row4" style="margin-top:16px;">
  <div class="panel" style="text-align:center;">
    <div class="panel-title">Runs totales</div>
    <div class="stat-val" id="n-run">—</div>
    <div class="stat-label">ejecuciones</div>
  </div>
  <div class="panel" style="text-align:center;">
    <div class="panel-title">Ciclos totales</div>
    <div class="stat-val" id="n-ciclos">—</div>
    <div class="stat-label">iteraciones vitales</div>
  </div>
  <div class="panel" style="text-align:center;">
    <div class="panel-title">Hashes SHA-256</div>
    <div class="stat-val" id="n-hashes">—</div>
    <div class="stat-label">cadena trazable</div>
  </div>
  <div class="panel" style="text-align:center;">
    <div class="panel-title">Modo PSNC</div>
    <div class="stat-val" id="pct-psnc">—</div>
    <div class="stat-label">% de ciclos en cautela</div>
  </div>
</div>

<!-- ROW 3: Gráficas -->
<div class="section-title">◈ Series temporales — últimos 200 ciclos del ledger</div>

<div class="grid row2">
  <div class="panel">
    <div class="panel-title">ECE — Error de calibración</div>
    <div class="chart-box-tall">
      <canvas id="chartECE"></canvas>
    </div>
  </div>
  <div class="panel">
    <div class="panel-title">κ_conf — Confianza operatoria</div>
    <div class="chart-box-tall">
      <canvas id="chartKappa"></canvas>
    </div>
  </div>
</div>

<div class="grid row2" style="margin-top:16px;">
  <div class="panel">
    <div class="panel-title">𝓛* — Función vital normalizada</div>
    <div class="chart-box">
      <canvas id="chartL"></canvas>
    </div>
  </div>
  <div class="panel">
    <div class="panel-title">S_t — Memoria exponencial</div>
    <div class="chart-box">
      <canvas id="chartS"></canvas>
    </div>
  </div>
</div>

<!-- ROW 4: Hash ledger + Reporte -->
<div class="section-title">◈ Trazabilidad y reporte</div>
<div class="grid row2">
  <div class="panel">
    <div class="panel-title">Últimos 10 hashes SHA-256</div>
    <div class="hash-list" id="hash-list">cargando...</div>
  </div>
  <div class="panel">
    <div class="panel-title">Último reporte del runner</div>
    <pre id="reporte-text">cargando...</pre>
  </div>
</div>

<div style="text-align:center; margin-top:20px; font-size:0.6rem; color:var(--dim); letter-spacing:2px;">
  ALFA LUM-vitae vΩ.4 · Materialismo Filosófico · G. Bueno + Luminomática
</div>

<script>
// ─── CHARTS SETUP ────────────────────────────────────────────────────────────
const C = Chart.defaults;
C.color = '#4a7090';
C.borderColor = '#1a2a3a';
C.font.family = "'Courier New', monospace";
C.font.size = 10;

const CYAN   = '#00e5ff';
const GREEN  = '#00ff88';
const YELLOW = '#ffd54f';
const RED    = '#ff3d5a';
const DIM    = '#1a2a3a';

function mkChart(id, color, label, yMin=0, yMax=1, refLine=null) {
  const ctx = document.getElementById(id).getContext('2d');
  const datasets = [{
    label,
    data: [],
    borderColor: color,
    backgroundColor: color + '18',
    fill: true,
    tension: 0.35,
    pointRadius: 0,
    borderWidth: 1.5,
  }];
  if (refLine !== null) {
    datasets.push({
      label: 'umbral',
      data: [],
      borderColor: YELLOW + '99',
      borderDash: [4,4],
      borderWidth: 1,
      pointRadius: 0,
      fill: false,
    });
  }
  return new Chart(ctx, {
    type: 'line',
    data: { labels: [], datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 600 },
      scales: {
        x: {
          display: false,
          grid: { color: DIM },
        },
        y: {
          min: yMin, max: yMax,
          grid: { color: '#131f2e' },
          ticks: { color: '#3a5a7a', maxTicksLimit: 5 },
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#0d1520',
          borderColor: '#1a2a3a',
          borderWidth: 1,
          titleColor: '#00e5ff',
          bodyColor: '#c8dff0',
          callbacks: {
            title: (items) => `Ciclo ${items[0].label}`,
          }
        }
      }
    }
  });
}

const charts = {
  ece:   mkChart('chartECE',   GREEN,  'ECE',   0, 0.5, 0.05),
  kappa: mkChart('chartKappa', CYAN,   'κ_conf', 0, 1.05),
  L:     mkChart('chartL',     YELLOW, '𝓛*',    0, 1.05),
  S:     mkChart('chartS',     '#b39ddb', 'S_t', 0, 1.05),
};

function updateChart(chart, labels, data, refLine=null) {
  chart.data.labels = labels;
  chart.data.datasets[0].data = data;
  if (refLine !== null && chart.data.datasets[1]) {
    chart.data.datasets[1].data = labels.map(() => refLine);
  }
  chart.update('none');
}

// ─── ACTUALIZAR UI ────────────────────────────────────────────────────────────
function setDot(id, ok) {
  const el = document.getElementById(id);
  el.className = 'cond-dot ' + (ok ? 'dot-ok' : 'dot-fail');
}
function setBadge(id, ok) {
  const el = document.getElementById(id);
  el.textContent = ok ? '✓ OK' : '✗ PENDIENTE';
  el.className = 'cond-badge ' + (ok ? 'badge-ok' : 'badge-fail');
}
function fmt(v, d=4) { return (typeof v === 'number') ? v.toFixed(d) : '—'; }
function fmtTs(s) {
  if (!s || s==='—') return '—';
  return s.replace('T',' ').substring(0,19) + ' UTC';
}

async function refresh() {
  try {
    const r = await fetch('/api/estado');
    const d = await r.json();

    // Veredicto
    const vp = document.getElementById('veredicto-panel');
    vp.className = 'panel veredicto-panel ' + (d.veredicto ? 'vivo-panel' : 'muerto-panel');
    document.getElementById('vglyph').textContent = d.veredicto ? '🧬' : '💀';
    const vt = document.getElementById('vtext');
    vt.textContent = d.veredicto ? 'VIVO' : 'NO VIVO';
    vt.className = 'veredicto-text ' + (d.veredicto ? 'vivo-text' : 'muerto-text');
    document.getElementById('vsub').textContent =
      `${d.n_vivo}/4 condiciones activas`;

    // Condiciones
    d.condiciones.forEach((ok, i) => {
      setDot('dot' + (i+1), ok);
      setBadge('badge' + (i+1), ok);
    });
    document.getElementById('ts-run').textContent = fmtTs(d.timestamp);

    // ECE bar
    const pct = Math.min(100, d.ECE / 1.0 * 100);
    const bar = document.getElementById('ece-bar');
    bar.style.width = pct + '%';
    bar.style.background = d.ECE <= 0.05 ? GREEN : RED;
    const ev = document.getElementById('ece-val');
    ev.textContent = fmt(d.ECE, 5);
    ev.style.color = d.ECE <= 0.05 ? GREEN : RED;

    // Stats
    document.getElementById('kappa-val').textContent  = fmt(d.kappa, 3);
    document.getElementById('L-val').textContent      = fmt(d.L_norm, 4);
    document.getElementById('S-val').textContent      = fmt(d.S_t, 3);
    document.getElementById('spawns-val').textContent = d.spawns;
    document.getElementById('n-run').textContent      = d.n_run;
    document.getElementById('n-ciclos').textContent   = d.n_ciclos;
    document.getElementById('n-hashes').textContent   = d.n_hashes;
    document.getElementById('pct-psnc').textContent   = d.pct_psnc + '%';

    // Charts
    updateChart(charts.ece,   d.labels, d.ece_series, 0.05);
    updateChart(charts.kappa, d.labels, d.kappa_series);
    updateChart(charts.L,     d.labels, d.L_series);
    updateChart(charts.S,     d.labels, d.s_series);

    // Hashes
    const hl = document.getElementById('hash-list');
    if (d.hash_list.length) {
      hl.innerHTML = d.hash_list.map((h,i) =>
        `<div class="hash-item">
           <span style="color:var(--dim);">#${d.n_ciclos - d.hash_list.length + i + 1}</span>
           <span class="hash-code">${h}…</span>
           <span style="color:var(--dim); font-size:0.6rem;">SHA-256</span>
         </div>`
      ).join('');
    }

    // Timestamp
    const now = new Date();
    document.getElementById('last-update').textContent =
      now.toTimeString().substring(0,8);

  } catch(e) {
    console.error('Error al cargar estado:', e);
  }

  // Reporte
  try {
    const r2 = await fetch('/api/reporte');
    const d2 = await r2.json();
    document.getElementById('reporte-text').textContent = d2.texto;
  } catch(e) {}
}

// Tick animado
let tickOn = true;
setInterval(() => {
  document.getElementById('tick').style.color = (tickOn = !tickOn)
    ? '#00ff88' : '#1a2a3a';
}, 1000);

// Refresh automático cada 30s
refresh();
setInterval(refresh, 30000);
</script>
</body>
</html>"""

@app.route("/")
def index():
    return render_template_string(TEMPLATE)

# ─── MAIN ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    PORT = 5050
    print(f"""
╔══════════════════════════════════════════════════════╗
║   ALFA LUM-vitae vΩ.4 — Dashboard Visual            ║
║                                                      ║
║   Abre en tu navegador:                              ║
║   → http://localhost:{PORT}                           ║
║                                                      ║
║   Ctrl+C para detener                                ║
╚══════════════════════════════════════════════════════╝
""")
    def abrir():
        time.sleep(1.2)
        webbrowser.open(f"http://localhost:{PORT}")
    threading.Thread(target=abrir, daemon=True).start()
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)
