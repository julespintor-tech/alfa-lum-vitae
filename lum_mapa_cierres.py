#!/usr/bin/env python3
"""
MAPA DE CIERRES CATEGORIALES — ALFA LUM-vitae + LUM-PE
=======================================================
Busca evidencia real de cierre categorial en Semantic Scholar
para cada familia de ciencias según la taxonomía del Materialismo Filosófico.
Genera lum_mapa_cierres.json y lum_mapa_cierres.html.

Uso:
    python3 lum_mapa_cierres.py           # completo (busca en red)
    python3 lum_mapa_cierres.py --html-only  # regenera HTML sin tocar la red
"""

import json, pathlib, datetime, time, re, math, html, sys, urllib.request, urllib.parse
import urllib.error

# ─── RUTAS ────────────────────────────────────────────────────────────────────
BASE        = pathlib.Path(__file__).parent
LUM_MARK2   = BASE.parent / "LUM MARK 2"
BUNDLES_DIR = LUM_MARK2 / "PUBLICACION_LUM" / "lum-pe-REPO" / "dataset" / "dataset_public_v0.1.0" / "bundles_public"
OUT_JSON       = BASE / "lum_mapa_cierres.json"
OUT_HTML       = BASE / "lum_mapa_cierres.html"
HISTORIAL_JSON         = BASE / "lum_minerva_historial.json"    # historial persistente de búsquedas
CLASICOS_JSON          = BASE / "lum_clasicos_cierres.json"     # obras clásicas — identidades sintéticas
CLASICOS_HISTORIAL_JSON = BASE / "lum_clasicos_historial.json"  # historial de verificaciones SS clásicos

MODO_HTML_ONLY = "--html-only" in sys.argv

# ─── CORPUS DE OBRAS CLÁSICAS ─────────────────────────────────────────────────
# Cada obra es analizada según la Teoría del Cierre Categorial (TCC) de Bueno:
# p_sintetico = grado de cierre alcanzado (0..1) · semaforo = GREEN/AMBER/RED
# τ_V=0.80 (verde), τ_R=0.40 (rojo) — igual que para los dominios científicos.
CLASICOS = {
    "EUCLID_ELEMENTOS": {
        "titulo":       "Elementos",
        "autor":        "Euclides de Alejandría",
        "anio":         "~300 a.C.",
        "dominio":      "FORM",
        "icono":        "△",
        "color":        "#00e5ff",
        "p_sintetico":  0.97,
        "semaforo":     "GREEN",
        "descripcion":  "13 libros de geometría axiomática. Cierre categorial perfecto: "
                        "5 postulados → 465 teoremas sin contradicción detectada en 2 300 años.",
        "evidencia":    "Primer sistema axiomático completo de la historia. "
                        "Todos los teoremas se derivan exclusivamente de los postulados mediante "
                        "construcción geométrica: el campo queda herméticamente cerrado.",
        "tipo_cierre":  "Cierre α — axiomático-deductivo completo",
        "bueno_ref":    "Prototipo de cierre α: la red operatoria de construcciones es la identidad sintética.",
    },
    "NEWTON_PRINCIPIA": {
        "titulo":       "Philosophiæ Naturalis Principia Mathematica",
        "autor":        "Isaac Newton",
        "anio":         "1687",
        "dominio":      "NAT",
        "icono":        "⊕",
        "color":        "#00ff88",
        "p_sintetico":  0.94,
        "semaforo":     "GREEN",
        "descripcion":  "3 leyes del movimiento + gravitación universal. "
                        "Cierre β canónico: todos los fenómenos mecánicos quedan bajo las mismas ecuaciones.",
        "evidencia":    "Predicciones verificadas durante 200 años: planetas, mareas, trayectorias. "
                        "Las leyes causales clausuran el dominio físico-mecánico sin excepción.",
        "tipo_cierre":  "Cierre β — leyes causales universales verificadas empíricamente",
        "bueno_ref":    "Cierre β paradigmático: las leyes causales clausuran el campo de la mecánica clásica.",
    },
    "BUENO_TCC": {
        "titulo":       "Teoría del Cierre Categorial (TCC)",
        "autor":        "Gustavo Bueno",
        "anio":         "1992–1993",
        "dominio":      "FORM",
        "icono":        "◈",
        "color":        "#00e5ff",
        "p_sintetico":  0.91,
        "semaforo":     "GREEN",
        "descripcion":  "Obra fundacional del Materialismo Filosófico. "
                        "Define las condiciones del cierre científico: identidades sintéticas, "
                        "operaciones, términos y figuras.",
        "evidencia":    "El propio texto produce un metacierre sobre el concepto de cierre — "
                        "autorreferencia productiva. Aplicado exitosamente a física, matemáticas, "
                        "biología, economía y arte.",
        "tipo_cierre":  "Metacierre — establece las condiciones formales del cierre en cualquier campo",
        "bueno_ref":    "La TCC es el instrumento analítico central del proyecto MINERVA.",
    },
    "FREGE_BEGRIF": {
        "titulo":       "Begriffsschrift",
        "autor":        "Gottlob Frege",
        "anio":         "1879",
        "dominio":      "FORM",
        "icono":        "⊢",
        "color":        "#00e5ff",
        "p_sintetico":  0.88,
        "semaforo":     "GREEN",
        "descripcion":  "Primera formalización completa de la lógica de predicados. "
                        "Establece el cierre formal del razonamiento deductivo.",
        "evidencia":    "Base de toda lógica formal moderna. Permite derivar mecánicamente "
                        "conclusiones desde premisas: el campo lógico queda cerrado operatoriamente.",
        "tipo_cierre":  "Cierre α — lógica de predicados como identidad sintética máxima",
        "bueno_ref":    "Cierre α por excelencia: el lenguaje lógico-formal como identidad sintética.",
    },
    "MAXWELL_ECUACIONES": {
        "titulo":       "Treatise on Electricity and Magnetism",
        "autor":        "James Clerk Maxwell",
        "anio":         "1873",
        "dominio":      "NAT",
        "icono":        "∿",
        "color":        "#00ff88",
        "p_sintetico":  0.85,
        "semaforo":     "GREEN",
        "descripcion":  "4 ecuaciones que unifican electricidad, magnetismo y luz. "
                        "Cierre β sobre todo el electromagnetismo clásico.",
        "evidencia":    "Predicen ondas electromagnéticas a velocidad c antes de ser observadas. "
                        "El campo electromagnético queda cerrado bajo un único sistema ecuacional.",
        "tipo_cierre":  "Cierre β — unificación de tres dominios físicos en un sistema formal",
        "bueno_ref":    "Ejemplo de cierre β ampliado: reduce múltiples campos a una sola identidad sintética.",
    },
    "DARWIN_ORIGEN": {
        "titulo":       "El origen de las especies",
        "autor":        "Charles Darwin",
        "anio":         "1859",
        "dominio":      "NAT",
        "icono":        "🌿",
        "color":        "#00ff88",
        "p_sintetico":  0.74,
        "semaforo":     "AMBER",
        "descripcion":  "Selección natural como mecanismo de la diversidad biológica. "
                        "Cierre β parcial: el mecanismo es verificable pero la historia evolutiva es irrepetible.",
        "evidencia":    "Predicciones confirmadas: fósiles de transición, biología molecular. "
                        "Sin embargo el campo biológico no alcanza el cierre completo de la mecánica.",
        "tipo_cierre":  "Cierre β aproximado — mecanismo causal sobre historias singulares",
        "bueno_ref":    "Cierre β parcial: las leyes de la selección natural operan sobre "
                        "materiales históricos no reproducibles.",
    },
    "ARISTOTELES_ORGANON": {
        "titulo":       "Organon",
        "autor":        "Aristóteles",
        "anio":         "~350 a.C.",
        "dominio":      "FORM",
        "icono":        "Α",
        "color":        "#00e5ff",
        "p_sintetico":  0.68,
        "semaforo":     "AMBER",
        "descripcion":  "Tratados lógicos: Categorías, Analíticos, Tópicos. "
                        "Primer sistema lógico-científico de Occidente. Cierre parcial.",
        "evidencia":    "El silogismo cierra el dominio de la deducción válida. "
                        "Cierre incompleto: la lógica de predicados de Frege lo superó en 1879.",
        "tipo_cierre":  "Proto-cierre α — silogística como antecedente sin axiomatización plena",
        "bueno_ref":    "Antecedente histórico del cierre α: identifica términos y predicados "
                        "pero sin formalización algebraica.",
    },
    "KANT_KRV": {
        "titulo":       "Crítica de la razón pura",
        "autor":        "Immanuel Kant",
        "anio":         "1781",
        "dominio":      "FORM",
        "icono":        "◻",
        "color":        "#00e5ff",
        "p_sintetico":  0.61,
        "semaforo":     "AMBER",
        "descripcion":  "Deducción trascendental de las categorías del entendimiento. "
                        "Intenta un cierre sobre las condiciones de posibilidad del conocimiento.",
        "evidencia":    "Las 12 categorías y las formas de la intuición delimitan el "
                        "campo posible del conocimiento objetivo. Cierre parcial: depende "
                        "de un sujeto trascendental no empíricamente verificable.",
        "tipo_cierre":  "Cierre α subjetivo — anclado en la conciencia trascendental",
        "bueno_ref":    "Precursor del cierre categorial: identifica identidades sintéticas a priori "
                        "pero las ancla en el sujeto en vez de en la materia.",
    },
    "BUENO_ANIMAL_DIVINO": {
        "titulo":       "El animal divino",
        "autor":        "Gustavo Bueno",
        "anio":         "1985",
        "dominio":      "ARTE",
        "icono":        "⌘",
        "color":        "#f48fb1",
        "p_sintetico":  0.64,
        "semaforo":     "AMBER",
        "descripcion":  "Análisis materialista de la religión como campo operatorio "
                        "con cierre simbólico. Demuestra que la religión produce "
                        "identidades sintéticas propias.",
        "evidencia":    "Aplica la TCC al campo religioso-artístico. Cierre simbólico-operatorio "
                        "del campo: los rituales son operaciones que producen identidades reales.",
        "tipo_cierre":  "Cierre simbólico-operatorio — campo religioso/artístico analizado desde la TCC",
        "bueno_ref":    "Prueba que arte y religión pueden analizarse con criterios científicos "
                        "sin reducirlos ni instrumentalizarlos.",
    },
    "MARX_CAPITAL": {
        "titulo":       "El Capital",
        "autor":        "Karl Marx",
        "anio":         "1867",
        "dominio":      "SOC_IV",
        "icono":        "⚒",
        "color":        "#ffd54f",
        "p_sintetico":  0.55,
        "semaforo":     "AMBER",
        "descripcion":  "Análisis del plusvalor y el modo de producción capitalista. "
                        "Cierre γ interpretativo: potente pero dependiente de presupuestos normativos.",
        "evidencia":    "Predicciones parcialmente verificadas (concentración de capital, "
                        "ciclos de crisis). El campo económico no alcanza cierre β pleno.",
        "tipo_cierre":  "Cierre γ interpretativo — red de identidades sobre relaciones sociales",
        "bueno_ref":    "Cierre γ relevante: construye identidades (mercancía = trabajo abstracto) "
                        "pero el campo permanece abierto a re-interpretación.",
    },
    "SAUSSURE_CLG": {
        "titulo":       "Curso de lingüística general",
        "autor":        "Ferdinand de Saussure",
        "anio":         "1916",
        "dominio":      "SOC_DID",
        "icono":        "∑",
        "color":        "#ff9800",
        "p_sintetico":  0.47,
        "semaforo":     "AMBER",
        "descripcion":  "Fundación de la lingüística estructural: signo, "
                        "significante, significado, sincronía/diacronía.",
        "evidencia":    "El sistema langue/parole delimita un campo formal. "
                        "Cierre incompleto: la variación diacrónica introduce apertura histórica.",
        "tipo_cierre":  "Cierre γ diacrónico parcial — identidades fonológicas sin cierre histórico",
        "bueno_ref":    "La lingüística identifica identidades (el fonema como unidad operatoria) "
                        "pero depende de comunidades hablantes cambiantes.",
    },
    "FREUD_SUENOS": {
        "titulo":       "La interpretación de los sueños",
        "autor":        "Sigmund Freud",
        "anio":         "1900",
        "dominio":      "SOC_IV",
        "icono":        "◑",
        "color":        "#ffd54f",
        "p_sintetico":  0.33,
        "semaforo":     "RED",
        "descripcion":  "Propuesta de un método interpretativo del inconsciente. "
                        "Proto-cierre: establece términos pero las operaciones no son reproducibles.",
        "evidencia":    "La terapia psicoanalítica es irrepetible. Las identidades "
                        "(sueño = deseo disfrazado) no son verificables sistemáticamente.",
        "tipo_cierre":  "Proto-cierre γ — red simbólica sin operaciones reproducibles",
        "bueno_ref":    "Ejemplo de pseudo-cierre: construye un vocabulario técnico "
                        "pero sin identidades sintéticas verificables.",
    },
    "HEGEL_FENOMENOLOGIA": {
        "titulo":       "Fenomenología del espíritu",
        "autor":        "G.W.F. Hegel",
        "anio":         "1807",
        "dominio":      "SOC_IV",
        "icono":        "∞",
        "color":        "#ffd54f",
        "p_sintetico":  0.20,
        "semaforo":     "RED",
        "descripcion":  "Dialéctica del espíritu absoluto. Sin cierre operatorio: "
                        "el sistema se auto-absorbe en la especulación pura.",
        "evidencia":    "Las identidades propuestas (Ser = Nada = Devenir) son tautológicas. "
                        "El campo hegeliano carece de criterios externos de refutación o verificación.",
        "tipo_cierre":  "Sin cierre — idealismo especulativo sin operaciones externas",
        "bueno_ref":    "Contra-ejemplo canónico: el idealismo absoluto disuelve el campo "
                        "en el discurso — exactamente lo que la TCC critica.",
    },
    "NIETZSCHE_ZARATHUSTRA": {
        "titulo":       "Así habló Zaratustra",
        "autor":        "Friedrich Nietzsche",
        "anio":         "1883–1885",
        "dominio":      "ARTE",
        "icono":        "⚡",
        "color":        "#f48fb1",
        "p_sintetico":  0.15,
        "semaforo":     "RED",
        "descripcion":  "Obra filosófico-poética sobre el superhombre y la voluntad de poder. "
                        "Campo simbólico sin cierre operatorio formal.",
        "evidencia":    "Ausencia de identidades sintéticas verificables. "
                        "El texto produce efectos retóricos y estéticos pero no "
                        "construye una red operatoria cerrada.",
        "tipo_cierre":  "Sin cierre — campo simbólico abierto sin operaciones determinadas",
        "bueno_ref":    "Ejemplo de campo artístico-filosófico sin identidades sintéticas: "
                        "potente expresión pero sin cierre categorial.",
    },
}

# ─── TAXONOMÍA DE DISCIPLINAS ─────────────────────────────────────────────────
# Basada en la clasificación de Bueno: ciencias alpha (formales), beta (naturales),
# gamma (humanidades/sociales), más tecnología e ingeniería.

DISCIPLINAS = {
    "FORM": {
        "nombre":   "Ciencias Formales",
        "icono":    "∑",
        "color":    "#00e5ff",
        "descripcion": "Matemáticas, Lógica, Estadística — cierran sobre estructuras abstractas",
        "tipo_bundle": "FORM_GENERAL",
        "subcampos": ["Matemáticas", "Lógica formal", "Estadística", "Teoría de la información"],
        "queries": [
            "mathematical closure axiomatization completeness theorem",
            "logical formalization consistency completeness proof",
            "statistical theory closure operational definition",
        ],
        "señales_cierre": [
            "axiom", "theorem", "proof", "completeness", "consistency",
            "formal system", "closure", "algebra", "deductive", "formaliz"
        ],
        "bueno_ref": "Ciencias α (alpha) — cierre por axiomatización"
    },
    "NAT": {
        "nombre":   "Ciencias Naturales",
        "icono":    "⚛",
        "color":    "#00ff88",
        "descripcion": "Física, Química, Biología — cierran sobre referentes naturales observables",
        "tipo_bundle": "NAT_GENERAL",
        "subcampos": ["Física", "Química", "Biología", "Neurociencia", "Geología"],
        "queries": [
            "natural science causal closure physical laws empirical",
            "scientific closure operationalization measurement protocol",
            "replication reproducibility experimental closure natural",
        ],
        "señales_cierre": [
            "causal closure", "physical law", "experimental", "measurement",
            "replication", "empirical", "operationalization", "protocol",
            "natural law", "invariant", "conservation"
        ],
        "bueno_ref": "Ciencias β (beta) — cierre por leyes causales"
    },
    "SOC_IV": {
        "nombre":   "Ciencias Sociales Interpretativas",
        "icono":    "◈",
        "color":    "#ffd54f",
        "descripcion": "Psicología, Sociología, Economía — cierran sobre operaciones intersubjetivas",
        "tipo_bundle": "SOC_IV",
        "subcampos": ["Psicología", "Sociología", "Economía", "Comunicación"],
        "queries": [
            "social science operationalization construct validity closure",
            "psychological measurement operationalization reliability validity",
            "sociological demarcation scientific status methodology",
        ],
        "señales_cierre": [
            "operationalization", "construct validity", "reliability",
            "demarcation", "measurement", "intersubjectivity", "protocol",
            "replication", "systematic", "operationally defined"
        ],
        "bueno_ref": "Ciencias γ (gamma) interpretativas — cierre parcial"
    },
    "SOC_DID": {
        "nombre":   "Ciencias Sociales Diacrónicas",
        "icono":    "⏳",
        "color":    "#ff9800",
        "descripcion": "Historia, Antropología, Arqueología — analizan el cambio temporal",
        "tipo_bundle": "SOC_DiD",
        "subcampos": ["Historia", "Antropología", "Arqueología", "Demografía"],
        "queries": [
            "historical method scientific demarcation historiography closure",
            "anthropological methodology scientific status ethnography",
            "archaeological scientific method chronology dating closure",
        ],
        "señales_cierre": [
            "historical method", "scientific history", "demarcation",
            "chronology", "stratigraphy", "dating method",
            "ethnographic", "systematic fieldwork", "hypothesis testing"
        ],
        "bueno_ref": "Ciencias γ (gamma) diacrónicas — proto-cierre"
    },
    "TEC": {
        "nombre":   "Ingeniería y Tecnología",
        "icono":    "⚙",
        "color":    "#b39ddb",
        "descripcion": "Informática, Cibernética, IA — cierran sobre sistemas diseñados",
        "tipo_bundle": "ENG_TEST",
        "subcampos": ["Informática", "Cibernética", "Inteligencia Artificial", "Ingeniería"],
        "queries": [
            "cybernetics feedback closure control systems formal",
            "artificial intelligence formal verification closure specification",
            "software engineering formal methods closure correctness",
        ],
        "señales_cierre": [
            "feedback loop", "formal verification", "closure property",
            "specification", "correctness", "system closure",
            "cybernetic", "control theory", "formal methods", "invariant"
        ],
        "bueno_ref": "Técnica — cierre operatorio-instrumental"
    },
    "ARTE": {
        "nombre":   "Arte y Estética",
        "icono":    "🎨",
        "color":    "#f48fb1",
        "descripcion": "Pintura, Música, Literatura — cierre simbólico-operatorio",
        "tipo_bundle": None,
        "subcampos": ["Pintura", "Música", "Literatura", "Arquitectura"],
        "queries": [
            "aesthetic closure art theory pictorial formalization",
            "art philosophy materialist analysis operational closure",
            "pictorial science materialist philosophy Bueno closure",
        ],
        "señales_cierre": [
            "pictorial", "aesthetic closure", "artistic operation",
            "formal analysis", "pictorial theory", "materialist",
            "operational", "symbolic closure", "compositional"
        ],
        "bueno_ref": "Campo simbólico-operatorio — cierre en construcción"
    },
}

# ─── SEMANTIC SCHOLAR API ────────────────────────────────────────────────────

SS_BASE    = "https://api.semanticscholar.org/graph/v1"
MODO_LOCAL = MODO_HTML_ONLY   # en modo html-only no tocamos la red

def buscar_papers(query: str, limit: int = 10) -> list:
    """Busca papers en Semantic Scholar con reintentos y backoff exponencial."""
    if MODO_LOCAL:
        return []
    params = urllib.parse.urlencode({
        "query": query,
        "limit": limit,
        "fields": "title,abstract,year,citationCount,fieldsOfStudy"
    })
    url = f"{SS_BASE}/paper/search?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "LUM-MINERVA/1.0"})
    max_intentos = 4
    espera = 1.0  # segundos iniciales
    for intento in range(max_intentos):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
                return data.get("data", [])
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print(f"  [warn] Semantic Scholar 429 — esperando {espera:.0f}s (intento {intento+1}/{max_intentos})")
                time.sleep(espera)
                espera *= 2  # backoff exponencial
            else:
                print(f"  [red] Error HTTP Semantic Scholar {e.code}: {e}")
                return []
        except Exception as e:
            print(f"  [red] Error Semantic Scholar: {e}")
            return []
    print("  [red] Semantic Scholar: máximo de reintentos alcanzado, se omite.")
    return []

def score_cierre_texto(texto: str, señales: list) -> float:
    """Calcula score de cierre en un texto (0..1) buscando señales."""
    if not texto:
        return 0.0
    txt = texto.lower()
    hits = sum(1 for s in señales if s.lower() in txt)
    # Penaliza textos muy cortos
    densidad = hits / max(len(txt.split()), 1) * 100
    raw = min(1.0, hits / max(len(señales) * 0.3, 1))
    return round(raw, 4)


# ─── LEER BUNDLES LUM-PE ─────────────────────────────────────────────────────

_bundles_cache: dict = {}  # caché en memoria para evitar leer 45 ficheros cada vez

def leer_bundles_por_tipo() -> dict:
    """Agrupa los 45 bundles LUM-PE por tipo y calcula estadísticas (cacheado)."""
    global _bundles_cache
    if _bundles_cache:
        return _bundles_cache
    if not BUNDLES_DIR.exists():
        return {}
    por_tipo = {}
    for f in sorted(BUNDLES_DIR.glob("*.json")):
        d = json.loads(f.read_text())
        inp = d.get("INPUT", {}) or {}
        out = d.get("OUTPUT", {}) or {}
        idx = out.get("indices", {}) or {}
        prb = out.get("probabilities", {}) or {}
        tipo = inp.get("domain_subtype", "UNKNOWN")
        if tipo not in por_tipo:
            por_tipo[tipo] = {"campos": [], "states": [], "p_vals": [], "ipu_vals": [], "conf_vals": []}
        p = prb.get("p_close_cal") or prb.get("p_close_raw") or 0
        por_tipo[tipo]["campos"].append(inp.get("field_id", ""))
        por_tipo[tipo]["states"].append(out.get("state", "?"))
        por_tipo[tipo]["p_vals"].append(p)
        por_tipo[tipo]["ipu_vals"].append(idx.get("ipu", 0))
        por_tipo[tipo]["conf_vals"].append(idx.get("conf", 0))
    # Estadísticas
    for tipo, data in por_tipo.items():
        n = len(data["p_vals"])
        data["n_campos"]   = n
        data["p_media"]    = round(sum(data["p_vals"]) / n, 4) if n else 0
        data["ipu_media"]  = round(sum(data["ipu_vals"]) / n, 4) if n else 0
        data["conf_media"] = round(sum(data["conf_vals"]) / n, 4) if n else 0
        from collections import Counter
        data["state_dist"] = dict(Counter(data["states"]))
        # Estado agregado por mayoría
        cnt = Counter(data["states"])
        data["state_agregado"] = cnt.most_common(1)[0][0] if cnt else "?"
    _bundles_cache = por_tipo
    return por_tipo

# ─── FUNCIÓN PRINCIPAL ────────────────────────────────────────────────────────

def calcular_mapa() -> dict:
    print("=" * 60)
    print("  MAPA DE CIERRES CATEGORIALES — LUM MINERVA")
    print(f"  {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Modo: COMPLETO (búsqueda en red + LUM-PE)")
    print("=" * 60)

    bundles  = leer_bundles_por_tipo()
    mapa     = {}
    resumen  = {"total_papers": 0, "timestamp": datetime.datetime.utcnow().isoformat()}

    # Cargar JSON existente para preservar papers/hallazgos si la red falla
    _cache_anterior = {}
    if OUT_JSON.exists():
        try:
            _cache_anterior = json.loads(OUT_JSON.read_text()).get("mapa", {})
        except Exception as _e:
            print(f"  [warn] No se pudo leer caché anterior: {_e}")

    for clave, disc in DISCIPLINAS.items():
        print(f"\n▶ {disc['nombre']} ({clave})")

        # 1. Datos LUM-PE internos
        tipo_bundle = disc["tipo_bundle"]
        bundle_data = bundles.get(tipo_bundle, {}) if tipo_bundle else {}
        p_lum   = bundle_data.get("p_media", 0)
        ipu_lum = bundle_data.get("ipu_media", 0)
        state_lum = bundle_data.get("state_agregado", "N/A")
        n_campos  = bundle_data.get("n_campos", 0)

        # 2. Búsqueda en Semantic Scholar
        papers_totales = []
        scores_papers  = []
        for q in disc["queries"]:
            print(f"  → buscando: {q[:60]}…")
            results = buscar_papers(q, limit=8)
            for p in results:
                abstract = p.get("abstract") or ""
                title    = p.get("title") or ""
                texto    = title + " " + abstract
                sc = score_cierre_texto(texto, disc["señales_cierre"])
                papers_totales.append({
                    "title":   title[:120],
                    "year":    p.get("year"),
                    "citas":   p.get("citationCount", 0),
                    "score_cierre": sc,
                    "abstract_frag": abstract[:200] if abstract else ""
                })
                scores_papers.append(sc)
            time.sleep(0.4)  # respetar rate limit

        # Score medio de cierre en papers
        n_papers = len(papers_totales)
        sc_papers = round(sum(scores_papers) / n_papers, 4) if n_papers else 0
        papers_top = sorted(papers_totales, key=lambda x: x["score_cierre"], reverse=True)[:5]

        # 3. Score LUM sintetizado
        # Combina: p_lum (del modelo LUM-PE), sc_papers (evidencia externa)
        if p_lum > 0 and sc_papers > 0:
            p_sintetico = round(0.6 * p_lum + 0.4 * sc_papers, 4)
        elif p_lum > 0:
            p_sintetico = p_lum
        else:
            p_sintetico = sc_papers

        # 5. Semáforo LUM (τ_V=0.8, τ_R=0.4)
        if state_lum == "N/A":
            if   p_sintetico >= 0.80: semaforo = "GREEN"
            elif p_sintetico >= 0.40: semaforo = "AMBER"
            else:                     semaforo = "RED"
        else:
            semaforo = state_lum

        print(f"  ✓ {n_papers} papers · score_cierre={sc_papers:.3f} · LUM_STATE={semaforo}")

        mapa[clave] = {
            "meta": {
                "nombre":      disc["nombre"],
                "icono":       disc["icono"],
                "color":       disc["color"],
                "descripcion": disc["descripcion"],
                "subcampos":   disc["subcampos"],
                "bueno_ref":   disc["bueno_ref"],
            },
            "lum_pe": {
                "n_campos":    n_campos,
                "p_media":     p_lum,
                "ipu_media":   ipu_lum,
                "state_lum":   state_lum,
                "state_dist":  bundle_data.get("state_dist", {}),
            },
            "semanticscholar": {
                "n_papers":    n_papers,
                "score_cierre": sc_papers,
                # Preservar papers del caché si la red no devolvió nada
                "papers_top":  papers_top if papers_top else
                               _cache_anterior.get(clave, {}).get("semanticscholar", {}).get("papers_top", []),
                # Preservar hallazgo y tendencia del caché
                "hallazgo_clave": _cache_anterior.get(clave, {}).get("semanticscholar", {}).get("hallazgo_clave", ""),
                "tendencia": _cache_anterior.get(clave, {}).get("semanticscholar", {}).get("tendencia", ""),
            },
            # Preservar datos_bibliograficos si los añadió MINERVA
            "datos_bibliograficos": _cache_anterior.get(clave, {}).get("datos_bibliograficos", {}),
            "resultado": {
                "p_sintetico": p_sintetico,
                "semaforo":    semaforo,
                # Preservar hallazgo/tendencia escritos por MINERVA
                "hallazgo":  _cache_anterior.get(clave, {}).get("resultado", {}).get("hallazgo", ""),
                "tendencia": _cache_anterior.get(clave, {}).get("resultado", {}).get("tendencia", ""),
            }
        }
        resumen["total_papers"]  += n_papers

    # Contar papers curados (datos_bibliograficos) — distintos de SS live
    resumen["total_papers_curados"] = sum(
        len(d.get("datos_bibliograficos", {}).get("papers", []))
        for d in mapa.values()
    )

    resultado_final = {"resumen": resumen, "mapa": mapa}
    OUT_JSON.write_text(json.dumps(resultado_final, ensure_ascii=False, indent=2))
    print(f"\n[OK] Mapa guardado → {OUT_JSON}")

    # ── Agregar entrada al historial persistente ──────────────────────────────
    _append_historial(mapa, resumen, source="full_run")

    return resultado_final


def calcular_clasicos() -> dict:
    """Genera/actualiza lum_clasicos_cierres.json con los clásicos de la TCC.
    Los scores son estáticos (basados en análisis TCC), no usan Semantic Scholar."""
    resultado = {
        "timestamp":  datetime.datetime.utcnow().isoformat(),
        "version":    1,
        "descripcion": "Corpus de obras clásicas analizadas según la Teoría del Cierre Categorial (TCC). "
                       "p_sintetico refleja el grado de cierre alcanzado según Gustavo Bueno.",
        "clasicos":   CLASICOS,
    }
    import os, shutil
    tmp = CLASICOS_JSON.with_suffix(".tmp")
    tmp.write_text(json.dumps(resultado, ensure_ascii=False, indent=2))
    if CLASICOS_JSON.exists():
        shutil.copy2(CLASICOS_JSON, CLASICOS_JSON.with_suffix(".bak"))
    os.replace(tmp, CLASICOS_JSON)
    print(f"[OK] Clásicos guardados → {CLASICOS_JSON} ({len(CLASICOS)} obras)")
    return resultado


def _append_historial(mapa: dict, resumen: dict, source: str = "full_run"):
    """Añade una entrada al historial persistente de búsquedas MINERVA.
    Mantiene máximo 50 entradas (FIFO). Escritura atómica."""
    import os, shutil
    entrada = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "source": source,
        "total_papers": resumen.get("total_papers", 0),
        "dominios": {
            k: {
                "p_sintetico": v.get("resultado", {}).get("p_sintetico", 0),
                "semaforo":    v.get("resultado", {}).get("semaforo", "N/A"),
                "n_papers_ss": v.get("semanticscholar", {}).get("n_papers", 0),
                "score_ss":    v.get("semanticscholar", {}).get("score_cierre", 0),
            }
            for k, v in mapa.items()
        }
    }
    try:
        historial_data: dict = {"version": 1, "historial": []}
        if HISTORIAL_JSON.exists():
            try:
                historial_data = json.loads(HISTORIAL_JSON.read_text())
            except Exception:
                pass
        lista = historial_data.get("historial", [])
        lista.append(entrada)
        # Mantener solo las últimas 50 entradas
        if len(lista) > 50:
            lista = lista[-50:]
        historial_data["historial"] = lista
        tmp = HISTORIAL_JSON.with_suffix(".tmp")
        tmp.write_text(json.dumps(historial_data, ensure_ascii=False, indent=2))
        if HISTORIAL_JSON.exists():
            shutil.copy2(HISTORIAL_JSON, HISTORIAL_JSON.with_suffix(".bak"))
        os.replace(tmp, HISTORIAL_JSON)
        print(f"  [OK] Historial actualizado → {HISTORIAL_JSON} ({len(lista)} entradas)")
    except Exception as e:
        print(f"  [warn] No se pudo guardar historial: {e}")

# ─── GENERADOR HTML ──────────────────────────────────────────────────────────

def generar_html(data: dict):
    mapa     = data["mapa"]
    resumen  = data["resumen"]
    ts       = resumen.get("timestamp", "")[:19].replace("T", " ") + " UTC"
    explo    = resumen.get("ultima_exploracion", ts)[:10]
    now_str  = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    C = {"GREEN":"#00ff88","AMBER":"#ffd54f","RED":"#ff3d5a","BLACK":"#9e9e9e","N/A":"#3a5a7a"}
    E = {"GREEN":"🟢","AMBER":"🟡","RED":"🔴","BLACK":"⚫","N/A":"⬜"}

    def barra(v, color):
        pct = min(100, v * 100)
        return (f'<div style="height:6px;border-radius:3px;'
                f'background:linear-gradient(90deg,{color} {pct:.1f}%,#1a2a3a {pct:.1f}%);'
                f'margin:4px 0;"></div>')

    def badge(text, color):
        return (f'<span style="font-size:.58rem;padding:2px 8px;border-radius:10px;'
                f'background:{color}18;color:{color};border:1px solid {color}33;'
                f'font-weight:bold;">{text}</span>')

    def relevancia_cierre(score):
        """Texto breve que explica qué tan fuerte es la evidencia de un paper."""
        if score >= 0.85: return "Evidencia directa y sólida de cierre categorial"
        if score >= 0.70: return "Evidencia significativa de cierre operatorio"
        if score >= 0.55: return "Evidencia moderada — apunta hacia proto-cierre"
        if score >= 0.40: return "Señal débil — relación indirecta con el cierre"
        return "Señal muy débil — contexto periférico"

    def why_score(disc):
        """Genera una explicación en lenguaje llano de por qué p es el que es."""
        res    = disc["resultado"]
        lum    = disc["lum_pe"]
        ss     = disc.get("semanticscholar", {})
        p      = res["p_sintetico"]
        ss_sc  = ss.get("score_cierre", 0)
        lum_p  = lum.get("p_media", 0)
        nc     = lum.get("n_campos", 0)
        np_    = ss.get("n_papers", 0)

        parts = []

        # Bibliografía
        if ss_sc >= 0.75:
            parts.append(f"bibliografía muy sólida: {np_} papers con score {ss_sc:.2f}")
        elif ss_sc >= 0.50:
            parts.append(f"bibliografía moderada: {np_} papers, score {ss_sc:.2f}")
        elif ss_sc > 0:
            parts.append(f"bibliografía débil: {np_} papers, score {ss_sc:.2f}")
        else:
            parts.append("sin evidencia bibliográfica directa")

        # LUM-PE
        if nc > 0:
            if lum_p >= 0.70:
                parts.append(f"LUM-PE confirma cierre en {nc} campos (p̄={lum_p:.3f})")
            elif lum_p >= 0.50:
                parts.append(f"LUM-PE detecta proto-cierre en {nc} campos (p̄={lum_p:.3f})")
            else:
                parts.append(f"LUM-PE detecta cierre débil en {nc} campos (p̄={lum_p:.3f})")
        else:
            parts.append("sin campos LUM-PE disponibles en este dominio")


        # Conclusión sobre el score
        if p >= 0.80:
            concl = "→ Score GREEN: evidencia convergente que confirma cierre operativo."
        elif p >= 0.60:
            concl = "→ Score AMBER alto: múltiples indicadores positivos, cierre parcial consolidado."
        elif p >= 0.40:
            concl = "→ Score AMBER bajo: señales mixtas, proto-cierre en construcción."
        else:
            concl = "→ Score RED: evidencia insuficiente o contradictoria, cierre no logrado."

        return " · ".join(parts) + "<br><span style='color:#2a8080;'>" + concl + "</span>"

    # Ordenar por p_sintetico desc
    orden = sorted(mapa.items(), key=lambda x: x[1]["resultado"]["p_sintetico"], reverse=True)

    # ── CARDS ─────────────────────────────────────────────────────────────────
    cards = ""
    for rank, (clave, disc) in enumerate(orden, 1):
        res  = disc["resultado"]
        meta = disc["meta"]
        lum  = disc["lum_pe"]
        ss   = disc.get("semanticscholar", {})
        sc   = C.get(res["semaforo"], "#3a5a7a")
        em   = E.get(res["semaforo"], "⬜")
        p    = res["p_sintetico"]
        dictamen  = res.get("dictamen", "")
        # MINERVA escribe en resultado.hallazgo; fallback a semanticscholar.hallazgo_clave
        hallazgo  = res.get("hallazgo", "") or ss.get("hallazgo_clave", "")
        # MINERVA escribe en resultado.tendencia; fallback a semanticscholar.tendencia
        tendencia = res.get("tendencia", "") or ss.get("tendencia", "")
        # MINERVA escribe en datos_bibliograficos.papers; fallback a semanticscholar.papers_top
        db_papers = disc.get("datos_bibliograficos", {}).get("papers", [])
        papers    = db_papers if db_papers else ss.get("papers_top", [])

        # subcampos
        sub_html = " ".join(
            f'<span style="font-size:.6rem;padding:2px 7px;border-radius:10px;'
            f'background:{meta["color"]}18;color:{meta["color"]};'
            f'border:1px solid {meta["color"]}33;">{html.escape(s)}</span>'
            for s in meta.get("subcampos", [])
        )

        # ── Papers: primeros 2 SIEMPRE VISIBLES, resto en details ─────────────
        def render_paper(p2, visible=True):
            # Normalizar campos: SS usa 'title/abstract_frag/score_cierre/citas'
            #                    MINERVA usa 'titulo/sintesis/relevancia/autores'
            title = p2.get("title","") or p2.get("titulo","")
            if not title: return ""
            url   = p2.get("url","")
            frag  = html.escape((p2.get("abstract_frag","") or p2.get("sintesis",""))[:220])
            yr    = p2.get("year","??") or p2.get("año","??")
            citas = p2.get("citas", 0)
            sc2   = p2.get("score_cierre", 0) or p2.get("relevancia", 0)
            rel   = html.escape(relevancia_cierre(sc2))
            title_tag = (
                f'<a href="{html.escape(url)}" target="_blank" style="color:{meta["color"]};'
                f'text-decoration:none;font-weight:bold;font-size:.68rem;line-height:1.4;">'
                f'{html.escape(title[:95])}</a>'
                if url else
                f'<span style="color:{meta["color"]};font-weight:bold;font-size:.68rem;">'
                f'{html.escape(title[:95])}</span>'
            )
            return f"""
            <div style="margin:7px 0;padding:9px 10px;background:rgba(0,0,0,.28);
                         border-radius:6px;border-left:3px solid {meta['color']}66;">
              {title_tag}
              {f'<div style="font-size:.63rem;color:#7ab0b0;margin-top:4px;line-height:1.5;">'
               f'<b style="color:#3a7a7a;">📝 Síntesis:</b> {frag}</div>' if frag else ''}
              <div style="font-size:.6rem;color:{meta["color"]}99;margin-top:4px;font-style:italic;">
                ↳ {rel}
              </div>
              <div style="font-size:.55rem;color:#2a4a6a;margin-top:3px;">
                {yr} · {citas} citas · relevancia para cierre: {sc2:.2f}
              </div>
            </div>"""

        visible_papers  = "".join(render_paper(p2, True)  for p2 in papers[:2])
        extra_papers    = "".join(render_paper(p2, False)  for p2 in papers[2:])

        # tendencia badge
        tend_col = (
            "#00e5ff" if any(k in tendencia for k in ["EXPANSIÓN","ACTIVO","ESTABLE"]) else
            "#ffd54f" if any(k in tendencia for k in ["TENSIÓN","CRISIS","TRANSFORMACIÓN"]) else
            "#3a5a7a"
        )
        tend_badge = (f'<span style="font-size:.6rem;padding:2px 8px;border-radius:10px;'
                      f'background:{tend_col}22;color:{tend_col};border:1px solid {tend_col}44;">'
                      f'&#x27F3; {html.escape(tendencia[:65])}</span>') if tendencia else ""

        # ── Bloque papers (precomputado para evitar f-strings anidadas) ────────
        n_pap = len(papers) or ss.get('n_papers', 0)
        if visible_papers:
            extra_det = ""
            if extra_papers:
                extra_det = (
                    f'<details style="margin-top:4px;">'
                    f'<summary style="font-size:.6rem;color:{meta["color"]}88;cursor:pointer;'
                    f'padding:3px 0;list-style:none;">'
                    f'<span>&#9656; Ver m&#225;s papers</span></summary>'
                    f'{extra_papers}</details>'
                )
            papers_block = (
                f'<div style="margin-bottom:8px;">'
                f'<div style="font-size:.58rem;color:#2a5a6a;letter-spacing:1px;margin-bottom:4px;'
                f'text-transform:uppercase;font-family:\'Courier New\',monospace;">'
                f'&#128218; Papers analizados ({n_pap} encontrados)</div>'
                f'{visible_papers}{extra_det}</div>'
            )
        else:
            papers_block = (
                f'<div style="font-size:.6rem;color:#2a4a5a;padding:8px 10px;'
                f'background:rgba(0,229,255,.04);border-radius:6px;border:1px dashed #1a3a4a;">'
                f'&#9711; Pendiente de exploración MINERVA &#8212; el agente autónomo cargará papers reales.<br>'
                f'<span style="color:#1a3a4a;font-size:.57rem;">Corre la tarea <b>lum-minerva-exploracion</b> '
                f'para poblar este dominio.</span></div>'
            )

        # ── Bloque corpus (precomputado) ────────────────────────────────────────
        corpus_block = ""

        # ── LUM-PE mini-grid ───────────────────────────────────────────────────
        lum_grid = ""
        if lum.get("n_campos", 0) > 0:
            lum_grid = f"""
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:4px;margin:8px 0 4px;">
              <div style="background:rgba(0,0,0,.28);border-radius:4px;padding:5px 4px;text-align:center;">
                <div style="font-size:.85rem;font-weight:bold;color:{meta['color']};
                             font-family:'Courier New',monospace;">{lum['n_campos']}</div>
                <div style="font-size:.52rem;color:#3a5a7a;">campos LUM-PE</div>
              </div>
              <div style="background:rgba(0,0,0,.28);border-radius:4px;padding:5px 4px;text-align:center;">
                <div style="font-size:.85rem;font-weight:bold;color:{meta['color']};
                             font-family:'Courier New',monospace;">{lum.get('p_media',0):.3f}</div>
                <div style="font-size:.52rem;color:#3a5a7a;">p̄ media</div>
              </div>
              <div style="background:rgba(0,0,0,.28);border-radius:4px;padding:5px 4px;text-align:center;">
                <div style="font-size:.85rem;font-weight:bold;color:{meta['color']};
                             font-family:'Courier New',monospace;">{lum.get('state_lum','?')}</div>
                <div style="font-size:.52rem;color:#3a5a7a;">estado LUM</div>
              </div>
            </div>"""

        cards += f"""
      <div class="card" style="border-color:{sc}55;border-top:2px solid {sc};">

        <!-- CABECERA -->
        <div style="display:flex;align-items:flex-start;gap:12px;margin-bottom:10px;">
          <div style="font-size:2rem;line-height:1;padding-top:2px;">{meta['icono']}</div>
          <div style="flex:1;min-width:0;">
            <div style="display:flex;align-items:center;gap:7px;flex-wrap:wrap;margin-bottom:3px;">
              <span style="font-size:.58rem;color:#2a4a6a;font-family:'Courier New',monospace;">#{rank}</span>
              <span style="font-size:1rem;font-weight:bold;color:{meta['color']};">{html.escape(meta['nombre'])}</span>
              {badge(res['semaforo'], sc)}
            </div>
            <div style="font-size:.67rem;color:#4a7090;line-height:1.4;">{html.escape(meta['descripcion'])}</div>
          </div>
          <div style="text-align:center;flex-shrink:0;">
            <div style="font-size:1.9rem;line-height:1;">{em}</div>
            <div style="font-size:1.15rem;font-weight:bold;color:{sc};
                         font-family:'Courier New',monospace;">{p:.3f}</div>
          </div>
        </div>

        <!-- BARRA PROBABILIDAD -->
        <div style="margin-bottom:8px;">
          <div style="display:flex;justify-content:space-between;font-size:.57rem;
                       color:#3a5a7a;margin-bottom:1px;">
            <span>probabilidad de cierre</span>
            <span style="color:{sc};">τ_V=0.80 · τ_R=0.40</span>
          </div>
          {barra(p, sc)}
        </div>

        <!-- SUBCAMPOS -->
        <div style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:10px;">{sub_html}</div>

        <!-- ╔═ LO QUE LUM DESCUBRIÓ ══════════════════╗ -->
        <div style="background:rgba(0,0,0,.22);border-radius:7px;padding:10px 12px;
                     margin-bottom:10px;border-left:3px solid {sc};">
          <div style="font-size:.58rem;color:#1a6a7a;letter-spacing:1.5px;margin-bottom:5px;
                       text-transform:uppercase;font-family:'Courier New',monospace;">
            ◈ Lo que LUM descubrió
          </div>
          {f'<div style="font-size:.7rem;color:#c0e0e8;line-height:1.6;margin-bottom:7px;">{html.escape(dictamen)}</div>' if dictamen else ''}
          {f'<div style="font-size:.65rem;color:#90b8c0;line-height:1.5;border-top:1px solid #1a3a4a;padding-top:6px;"><b style="color:#3a9aaa;">↳ Hallazgo principal:</b> {html.escape(hallazgo[:380])}</div>' if hallazgo else f'<div style="font-size:.65rem;color:#6080a0;line-height:1.5;font-style:italic;">LUM-PE analizó <b style="color:{sc};">{lum.get("n_campos",0)} campos</b> de este dominio con estado agregado <b style="color:{sc};">{lum.get("state_lum","?")}</b> y probabilidad media p̄ = <b style="color:{sc};">{lum.get("p_media",0):.3f}</b>.<br><span style="color:#2a4a6a;font-size:.6rem;">Hallazgo bibliográfico: pendiente — el agente MINERVA lo completará en la próxima exploración.</span></div>'}
        </div>

        <!-- ╔═ ¿POR QUÉ ESTE SCORE? ══════════════════╗ -->
        <div style="background:rgba(0,0,0,.18);border-radius:7px;padding:8px 12px;
                     margin-bottom:10px;border-left:3px solid {meta['color']}55;">
          <div style="font-size:.58rem;color:#1a5a6a;letter-spacing:1.5px;margin-bottom:5px;
                       text-transform:uppercase;font-family:'Courier New',monospace;">
            ↳ ¿Por qué p = {p:.3f}?
          </div>
          <div style="font-size:.65rem;color:#7aaab0;line-height:1.6;">{why_score(disc)}</div>
        </div>

        <!-- Referencia Bueno -->
        <div style="font-size:.6rem;color:#1a5050;font-style:italic;margin-bottom:8px;
                     padding:3px 8px;background:rgba(0,229,255,.04);border-radius:4px;
                     border-left:2px solid #00e5ff33;">
          {html.escape(meta.get('bueno_ref',''))}
        </div>

        <!-- Tendencia -->
        {f'<div style="margin-bottom:8px;">{tend_badge}</div>' if tend_badge else ''}

        <!-- LUM-PE mini-grid -->
        {lum_grid}

        <!-- ╔═ PAPERS — primeros 2 SIEMPRE VISIBLES ══╗ -->
        {papers_block}

        <!-- Corpus interno -->
        {corpus_block}

      </div>"""

    # ── ARCHIVO DE EVIDENCIA POR SEMÁFORO ────────────────────────────────────
    # Agrupa todos los papers de todos los dominios por color de semáforo y luego
    # por dominio, para que queden como índice de auditoría persistente.
    sem_defs = {
        "GREEN": {"color": "#00ff88", "emoji": "🟢",
                  "label": "VERDE — Cierre operatorio consolidado"},
        "AMBER": {"color": "#ffd54f", "emoji": "🟡",
                  "label": "ÁMBAR — Proto-cierre / cierre parcial"},
        "RED":   {"color": "#ff3d5a", "emoji": "🔴",
                  "label": "ROJO — Cierre no logrado / evidencia débil"},
    }
    # Recolectar papers por semáforo → dominio
    sem_buckets = {"GREEN": {}, "AMBER": {}, "RED": {}}

    for clave_a, disc_a in mapa.items():
        res_a  = disc_a["resultado"]
        meta_a = disc_a["meta"]
        sem_a  = res_a.get("semaforo", "N/A")
        if sem_a not in sem_buckets:
            continue
        db_p  = disc_a.get("datos_bibliograficos", {}).get("papers", [])
        ss_p  = disc_a.get("semanticscholar", {}).get("papers_top", [])
        plist = db_p if db_p else ss_p
        if not plist:
            continue
        bucket = sem_buckets[sem_a]
        if clave_a not in bucket:
            bucket[clave_a] = {
                "nombre": meta_a["nombre"],
                "icono":  meta_a["icono"],
                "color":  meta_a["color"],
                "papers": []
            }
        for p_item in plist:
            title_a = p_item.get("titulo","") or p_item.get("title","")
            if not title_a:
                continue
            bucket[clave_a]["papers"].append({
                "titulo":    title_a,
                "url":       p_item.get("url",""),
                "sintesis":  (p_item.get("sintesis","") or p_item.get("abstract_frag",""))[:240],
                "año":       p_item.get("año","??") or p_item.get("year","??"),
                "relevancia": p_item.get("relevancia",0) or p_item.get("score_cierre",0),
            })
        # Ordenar por relevancia desc
        bucket[clave_a]["papers"].sort(key=lambda x: x["relevancia"], reverse=True)

    def render_archivo_semaforo():
        out = ""
        for sem_key in ["GREEN","AMBER","RED"]:
            bucket = sem_buckets[sem_key]
            if not bucket:
                continue
            sd   = sem_defs[sem_key]
            sc   = sd["color"]
            total_p = sum(len(v["papers"]) for v in bucket.values())

            domain_cols = ""
            for clave_b, dom in bucket.items():
                dc    = dom["color"]
                rows  = ""
                for pi in dom["papers"]:
                    t_esc   = html.escape(pi["titulo"][:95])
                    t_tag   = (f'<a href="{html.escape(pi["url"])}" target="_blank" '
                               f'style="color:{dc};text-decoration:none;font-weight:bold;'
                               f'font-size:.68rem;line-height:1.4;">{t_esc}</a>'
                               if pi["url"] else
                               f'<span style="color:{dc};font-weight:bold;font-size:.68rem;">{t_esc}</span>')
                    rel_col = ("#00ff88" if pi["relevancia"] >= 0.80
                               else "#ffd54f" if pi["relevancia"] >= 0.60
                               else "#ff3d5a")
                    sint    = html.escape(pi["sintesis"])
                    rows   += (
                        f'<div style="padding:8px 10px;margin-bottom:6px;'
                        f'background:rgba(0,0,0,.25);border-radius:6px;'
                        f'border-left:3px solid {dc}55;">'
                        f'{t_tag}'
                        f'{f"""<div style="font-size:.62rem;color:#7ab0b0;margin-top:4px;line-height:1.5;">{sint}</div>""" if sint else ""}'
                        f'<div style="font-size:.57rem;color:#2a4a6a;margin-top:3px;">'
                        f'{pi["año"]} · '
                        f'<span style="color:{rel_col};font-weight:bold;">relevancia {pi["relevancia"]:.2f}</span>'
                        f'</div></div>'
                    )
                domain_cols += (
                    f'<div style="background:rgba(0,0,0,.18);border-radius:8px;padding:12px 14px;">'
                    f'<div style="display:flex;align-items:center;gap:7px;margin-bottom:9px;">'
                    f'<span style="font-size:1rem;">{dom["icono"]}</span>'
                    f'<span style="font-size:.7rem;color:{dc};font-weight:bold;letter-spacing:1px;'
                    f'text-transform:uppercase;font-family:\'Courier New\',monospace;">'
                    f'{html.escape(dom["nombre"])}</span>'
                    f'<span style="font-size:.57rem;color:#1a3a5a;background:{dc}11;'
                    f'padding:1px 6px;border-radius:8px;border:1px solid {dc}22;">'
                    f'{len(dom["papers"])} papers</span>'
                    f'</div>'
                    f'{rows}</div>'
                )

            out += (
                f'<div style="margin-bottom:28px;">'
                f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;'
                f'padding-bottom:9px;border-bottom:2px solid {sc}44;">'
                f'<span style="font-size:1.4rem;">{sd["emoji"]}</span>'
                f'<span style="font-size:.9rem;font-weight:bold;color:{sc};letter-spacing:2px;'
                f'font-family:\'Courier New\',monospace;">{sd["label"]}</span>'
                f'<span style="font-size:.62rem;color:{sc};background:{sc}11;'
                f'padding:2px 10px;border-radius:10px;border:1px solid {sc}33;margin-left:4px;">'
                f'{total_p} papers · {len(bucket)} dominio(s)</span>'
                f'</div>'
                f'<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:12px;">'
                f'{domain_cols}'
                f'</div></div>'
            )
        return out

    archivo_semaforo = render_archivo_semaforo()

    # ── CLÁSICOS — carga desde JSON ────────────────────────────────────────────
    clasicos_items = {}
    try:
        if CLASICOS_JSON.exists():
            clasicos_items = json.loads(CLASICOS_JSON.read_text()).get("clasicos", {})
    except Exception:
        pass

    # ── HISTORIALES — para paneles de búsquedas anteriores ─────────────────────
    minerva_historial = []
    try:
        if HISTORIAL_JSON.exists():
            minerva_historial = json.loads(HISTORIAL_JSON.read_text()).get("historial", [])
    except Exception:
        pass

    clasicos_historial = []
    try:
        if CLASICOS_HISTORIAL_JSON.exists():
            clasicos_historial = json.loads(CLASICOS_HISTORIAL_JSON.read_text()).get("historial", [])
    except Exception:
        pass

    def render_clasicos():
        """Genera HTML de la sección de obras clásicas."""
        if not clasicos_items:
            return '<div style="color:#3a5a7a;padding:16px;">Sin datos de clásicos.</div>'
        SEM_COL = {"GREEN": "#00ff88", "AMBER": "#ffd54f", "RED": "#ff3d5a"}
        SEM_ICO = {"GREEN": "🟢", "AMBER": "🟡", "RED": "🔴"}
        DOM_COL = {"FORM": "#00e5ff", "NAT": "#00ff88", "TEC": "#b39ddb",
                   "SOC_IV": "#ffd54f", "SOC_DID": "#ff9800", "ARTE": "#f48fb1"}
        DOM_NM  = {"FORM": "α Formal", "NAT": "β Natural", "TEC": "Técnica",
                   "SOC_IV": "γ Social-IV", "SOC_DID": "γ Social-Diacr.", "ARTE": "Simbólico"}
        ORDER   = ["GREEN", "AMBER", "RED"]

        def sk(item):
            s = item[1].get("semaforo", "RED")
            return (ORDER.index(s) if s in ORDER else 3, -item[1].get("p_sintetico", 0))

        out = '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:14px;">'
        for key, cl in sorted(clasicos_items.items(), key=sk):
            sem  = cl.get("semaforo", "RED")
            p    = cl.get("p_sintetico", 0.0)
            col  = SEM_COL.get(sem, "#9e9e9e")
            dom  = cl.get("dominio", "FORM")
            dcol = DOM_COL.get(dom, "#9e9e9e")
            dnm  = DOM_NM.get(dom, dom)
            pct  = int(round(p * 100))
            ico  = cl.get("icono", "◈")
            tit  = html.escape(cl.get("titulo", ""))
            aut  = html.escape(cl.get("autor", ""))
            anio = html.escape(cl.get("anio", ""))
            desc = html.escape(cl.get("descripcion", ""))
            tipo = html.escape(cl.get("tipo_cierre", ""))
            bref = html.escape(cl.get("bueno_ref", ""))
            out += f"""<div style="background:#0d1520;border:1px solid {col}30;border-radius:10px;
  padding:16px;position:relative;transition:transform .15s,border-color .2s;"
  onmouseover="this.style.transform='translateY(-2px)';this.style.borderColor='{col}66'"
  onmouseout="this.style.transform='';this.style.borderColor='{col}30'">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;margin-bottom:8px;">
    <div style="display:flex;align-items:center;gap:8px;flex:1;min-width:0;">
      <span style="font-size:1.4rem;flex-shrink:0;">{ico}</span>
      <div style="min-width:0;">
        <div style="font-size:.8rem;font-weight:bold;color:{col};margin-bottom:1px;">{tit}</div>
        <div style="font-size:.65rem;color:#4a7090;">{aut} · {anio}</div>
      </div>
    </div>
    <div style="display:flex;flex-direction:column;align-items:flex-end;gap:3px;flex-shrink:0;">
      <span style="font-size:.6rem;background:{col}20;color:{col};border:1px solid {col}44;
                   border-radius:4px;padding:2px 8px;font-weight:bold;">{SEM_ICO.get(sem,'')} {sem}</span>
      <span style="font-size:.55rem;color:{dcol};background:{dcol}15;border-radius:3px;
                   padding:1px 6px;">{dnm}</span>
    </div>
  </div>
  <div style="height:5px;background:#131f2e;border-radius:3px;overflow:hidden;margin-bottom:8px;">
    <div style="width:{pct}%;height:100%;background:{col};border-radius:3px;"></div>
  </div>
  <div style="display:flex;align-items:center;gap:6px;margin-bottom:8px;">
    <span style="font-size:.72rem;color:{col};font-family:'Courier New',monospace;
                 font-weight:bold;">p={p:.2f}</span>
    <span style="font-size:.6rem;color:#3a5a7a;">cierre sintético</span>
    <span id="cl-badge-{key}" style="font-size:.50rem;color:#3a5a7a;flex-shrink:0;
          font-family:'Courier New',monospace;" title="Pulsa Verificar en SS para buscar">—</span>
  </div>
  <div style="font-size:.68rem;color:var(--text);line-height:1.6;margin-bottom:8px;">{desc}</div>
  <details style="margin-top:4px;">
    <summary style="cursor:pointer;font-size:.6rem;color:{col}88;list-style:none;">
      ⊢ {tipo} &nbsp;▾
    </summary>
    <div style="font-size:.62rem;color:#3a7a5a;margin-top:6px;padding:8px;
                background:rgba(0,0,0,.25);border-radius:5px;border-left:2px solid {col}44;
                line-height:1.6;">◈ {bref}</div>
  </details>
</div>"""
        out += "</div>"
        return out

    clasicos_html = render_clasicos()

    # ── HISTORIAL PANELS ────────────────────────────────────────────────────────
    def render_minerva_historial_panel():
        if not minerva_historial:
            return ('<div style="color:var(--dim);font-size:.6rem;padding:8px 0;">'
                    'Sin búsquedas registradas — usa el botón <b style="color:#00e5ff">🔍 Buscar en SS</b>'
                    ' para registrar la primera.</div>')
        recent = list(reversed(minerva_historial[-10:]))
        out = ('<div id="mc-minerva-historial-list">'
               '<div style="font-size:.55rem;color:var(--dim);margin-bottom:4px;">'
               f'Últimas {len(recent)} de {len(minerva_historial)} búsquedas</div>')
        for h in recent:
            ts   = h.get("timestamp","")[:16].replace("T"," ")
            tp   = h.get("total_papers", 0)
            src  = h.get("source","")
            doms = h.get("dominios", {})
            _sc = {"GREEN":"#00ff88","AMBER":"#ffd54f","RED":"#ff3d5a"}
            dom_str = " · ".join(
                f'<span style="color:{_sc.get(v.get("semaforo",""),"#3a5a7a")}">'
                f'{k}:{v.get("p_sintetico",0):.2f}</span>'
                for k, v in doms.items()
            )
            out += (f'<div style="border-bottom:1px solid #131f2e;padding:5px 0;font-size:.58rem;">'
                    f'<span style="color:#3a5a7a;">{ts}</span>'
                    f'<span style="color:var(--cyan);margin-left:8px;">{tp} papers</span>'
                    f'<span style="color:#2a4a6a;margin-left:6px;">({src})</span>'
                    f'<div style="margin-top:2px;color:#3a5a7a;">{dom_str}</div>'
                    f'</div>')
        out += '</div>'
        return out

    def render_clasicos_historial_panel():
        if not clasicos_historial:
            return ('<div style="color:var(--dim);font-size:.6rem;padding:6px 0;">'
                    'Sin verificaciones registradas — usa el botón '
                    '<b style="color:#ffd54f">📚 Verificar en SS</b> para registrar la primera.</div>')
        recent = list(reversed(clasicos_historial[-8:]))
        out = '<div id="mc-cl-historial-list">'
        for h in recent:
            ts     = h.get("timestamp","")[:16].replace("T"," ")
            total  = h.get("total_papers_found", 0)
            hits   = h.get("obras_con_resultados", 0)
            out += (f'<div style="border-bottom:1px solid #131f2e;padding:5px 0;font-size:.58rem;">'
                    f'<span style="color:#3a5a7a;">{ts}</span>'
                    f'<span style="color:#ffd54f;margin-left:8px;">{hits} obras con resultados</span>'
                    f'<span style="color:#2a4a6a;margin-left:6px;">({total} papers total)</span>'
                    f'</div>')
        out += '</div>'
        return out

    minerva_historial_panel = render_minerva_historial_panel()
    clasicos_historial_panel = render_clasicos_historial_panel()

    # ── RANKING SIDEBAR ────────────────────────────────────────────────────────
    ranking = ""
    for i, (clave, disc) in enumerate(orden):
        res  = disc["resultado"]
        meta = disc["meta"]
        sc   = C.get(res["semaforo"], "#3a5a7a")
        p    = res["p_sintetico"]
        ranking += f"""
        <div style="display:flex;align-items:center;gap:9px;padding:8px 0;
                     border-bottom:1px solid #131f2e;">
          <div style="width:18px;text-align:center;font-size:.72rem;color:#2a4a6a;
                       font-family:'Courier New',monospace;">#{i+1}</div>
          <div style="font-size:1.1rem;">{meta['icono']}</div>
          <div style="flex:1;min-width:0;">
            <div style="font-size:.75rem;color:{meta['color']};font-weight:bold;
                         white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
              {html.escape(meta['nombre'])}</div>
            <div style="background:#1a2a3a;height:4px;border-radius:2px;margin-top:3px;">
              <div style="width:{p*100:.1f}%;height:100%;background:{sc};border-radius:2px;"></div>
            </div>
          </div>
          <div style="font-size:.7rem;color:{sc};font-weight:bold;white-space:nowrap;">
            {E.get(res['semaforo'],'?')} {p:.3f}</div>
        </div>"""

    # ── Resumen ────────────────────────────────────────────────────────────────
    n_green = sum(1 for _,d in orden if d["resultado"]["semaforo"]=="GREEN")
    n_amber = sum(1 for _,d in orden if d["resultado"]["semaforo"]=="AMBER")
    n_red   = sum(1 for _,d in orden if d["resultado"]["semaforo"]=="RED")
    # Papers curados: embebidos en datos_bibliograficos por MINERVA (distintos de SS live)
    n_papers_curados = sum(
        len(d.get("datos_bibliograficos", {}).get("papers", []))
        for _, d in orden
    )
    n_papers_live = resumen.get("total_papers", 0)  # solo resultados SS de este run

    page = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="refresh" content="120">
<title>Mapa de Cierres Categoriales — LUM MINERVA</title>
<style>
:root {{
  --bg:#090d14; --panel:#0d1520; --border:#1a2a3a;
  --cyan:#00e5ff; --green:#00ff88; --red:#ff3d5a; --yellow:#ffd54f;
  --dim:#3a5a7a; --text:#c8dff0; --muted:#4a7090;
}}
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ background:var(--bg); color:var(--text); font-family:'Segoe UI',sans-serif;
         min-height:100vh; padding:24px; }}
header {{ display:flex; justify-content:space-between; align-items:flex-start;
           border-bottom:1px solid var(--border); padding-bottom:16px; margin-bottom:24px;
           flex-wrap:wrap; gap:10px; }}
.logo {{ font-size:1.4rem; color:var(--cyan); letter-spacing:1px;
          font-family:'Courier New',monospace; }}
.subtitle {{ font-size:.75rem; color:var(--dim); margin-top:4px; }}
.ts-badge {{ font-size:.63rem; color:var(--muted); border:1px solid var(--border);
              padding:4px 12px; border-radius:20px; font-family:'Courier New',monospace; }}
.layout {{ display:grid; grid-template-columns:280px 1fr; gap:20px; }}
@media(max-width:900px) {{ .layout {{ grid-template-columns:1fr; }} }}
.sidebar {{ display:flex; flex-direction:column; gap:16px; }}
.panel {{ background:var(--panel); border:1px solid var(--border); border-radius:10px;
           padding:18px; position:relative; overflow:hidden; }}
.panel::before {{ content:''; position:absolute; top:0; left:0; right:0; height:2px;
                   background:linear-gradient(90deg,var(--cyan),transparent); }}
.panel-title {{ font-size:.63rem; color:var(--muted); letter-spacing:2px;
                 text-transform:uppercase; margin-bottom:12px;
                 font-family:'Courier New',monospace; }}
.cards-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(380px,1fr)); gap:16px; }}
.card {{ background:var(--panel); border:1px solid; border-radius:10px; padding:18px;
          position:relative; transition:transform .15s; }}
.card:hover {{ transform:translateY(-2px); }}
.stat-big {{ font-size:2rem; font-weight:bold; color:var(--cyan); line-height:1;
              margin-bottom:2px; font-family:'Courier New',monospace; }}
.stat-lbl {{ font-size:.63rem; color:var(--muted); letter-spacing:1px; }}
.legend-item {{ display:flex; align-items:flex-start; gap:8px; font-size:.72rem;
                 color:var(--text); padding:5px 0; }}
.legend-dot {{ width:10px; height:10px; border-radius:50%; flex-shrink:0; margin-top:3px; }}
details > summary {{ list-style:none; }}
details > summary::-webkit-details-marker {{ display:none; }}
</style>
</head>
<body>

<header>
  <div>
    <div class="logo">◈ MAPA DE CIERRES CATEGORIALES</div>
    <div class="subtitle">Materialismo Filosófico de Gustavo Bueno · ALFA LUM-vitae + LUM-PE · Proyecto MINERVA</div>
  </div>
  <div class="ts-badge">📸 {ts}</div>
</header>

<div class="layout">

  <!-- SIDEBAR ──────────────────────────────── -->
  <div class="sidebar">

    <div class="panel">
      <div class="panel-title">Resumen global</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px;">
        <div><div class="stat-big">{n_green}</div><div class="stat-lbl">🟢 cierre real</div></div>
        <div><div class="stat-big">{n_amber}</div><div class="stat-lbl">🟡 proto-cierre</div></div>
        <div><div class="stat-big">{n_red}</div><div class="stat-lbl">🔴 sin cierre</div></div>
        <div><div class="stat-big">{n_papers_curados}</div><div class="stat-lbl">papers curados</div></div>
        <div><div class="stat-big">{n_papers_live}</div><div class="stat-lbl">papers live (SS)</div></div>
        <div><div class="stat-big">45</div><div class="stat-lbl">campos LUM-PE</div></div>
      </div>
      <div style="font-size:.62rem;color:var(--dim);font-style:italic;line-height:1.6;">
        {html.escape(resumen.get('resumen_global','')[:280])}
      </div>
      <div style="margin-top:8px;font-size:.58rem;color:#2a4a5a;">
        Última exploración: {explo}
      </div>
    </div>

    <div class="panel">
      <div class="panel-title">Ranking de cierre</div>
      {ranking}
    </div>

    <div class="panel">
      <div class="panel-title">¿Qué significa el semáforo?</div>
      <div class="legend-item">
        <div class="legend-dot" style="background:#00ff88;box-shadow:0 0 6px #00ff88;"></div>
        <div><b style="color:#00ff88;">GREEN</b><br>
        <span style="font-size:.63rem;color:var(--dim);">Cierre real: la disciplina opera de forma sistemática, reproducible e independiente del sujeto. p ≥ 0.80</span></div>
      </div>
      <div class="legend-item" style="margin-top:6px;">
        <div class="legend-dot" style="background:#ffd54f;box-shadow:0 0 6px #ffd54f;"></div>
        <div><b style="color:#ffd54f;">AMBER</b><br>
        <span style="font-size:.63rem;color:var(--dim);">Proto-cierre: operaciones sistemáticas pero incompletas o en disputa. 0.40 ≤ p &lt; 0.80</span></div>
      </div>
      <div class="legend-item" style="margin-top:6px;">
        <div class="legend-dot" style="background:#ff3d5a;box-shadow:0 0 6px #ff3d5a;"></div>
        <div><b style="color:#ff3d5a;">RED</b><br>
        <span style="font-size:.63rem;color:var(--dim);">Sin cierre: las operaciones no forman un campo cerrado verificable. p &lt; 0.40</span></div>
      </div>
      <div style="margin-top:10px;font-size:.6rem;color:var(--dim);line-height:1.5;">
        Contrato LUM-I/O vΩ.2025-12<br>
        τ_V=0.80 · τ_R=0.40 · AND_min: IPU≥0.65 · A_norm≥0.55 · Conf≥0.60
      </div>
    </div>

    <div class="panel">
      <div class="panel-title">Marco teórico (Bueno)</div>
      <div style="font-size:.65rem;color:var(--muted);line-height:1.7;">
        El <b style="color:var(--cyan);">cierre categorial</b> (Bueno, 1992) es la condición que convierte una disciplina en <i>ciencia</i>: sus operaciones forman un campo cerrado sobre sus propios referentes.<br><br>
        <b style="color:#c0e0ff;">α — Formales:</b> cierran por axiomatización y prueba formal.<br>
        <b style="color:#c0e0ff;">β — Naturales:</b> por leyes causales y experimento reproducible.<br>
        <b style="color:#c0e0ff;">γ — Sociales:</b> cierres parciales, en construcción o disputa.<br><br>
        LUM mide p con modelo hazard clog-log + índices IPU, CPV, A_norm, κ_conf y cadena SHA-256 de auditoría.
      </div>
    </div>

  </div>

  <!-- CARDS + TAB SELECTOR ──────────────────── -->
  <div>
    <!-- Tab bar -->
    <div id="mc-tab-bar" style="display:flex;gap:0;margin-bottom:14px;
         border-bottom:1px solid rgba(0,229,255,.15);">
      <button id="mctab-btn-dominios" onclick="mcSwitchTab('dominios')"
        style="cursor:pointer;background:rgba(0,229,255,.14);
               border:1px solid rgba(0,229,255,.35);border-bottom:none;
               color:#00e5ff;font-size:.66rem;font-weight:bold;
               padding:6px 16px;border-radius:6px 6px 0 0;
               font-family:'Courier New',monospace;margin-right:3px;">
        ◈ Dominios Científicos
      </button>
      <button id="mctab-btn-clasicos" onclick="mcSwitchTab('clasicos')"
        style="cursor:pointer;background:rgba(0,0,0,.2);
               border:1px solid rgba(255,213,79,.2);border-bottom:none;
               color:#ffd54f88;font-size:.66rem;font-weight:bold;
               padding:6px 16px;border-radius:6px 6px 0 0;
               font-family:'Courier New',monospace;">
        ★ Clásicos Fundacionales
      </button>
    </div>

    <!-- Panel: Dominios Científicos -->
    <div id="mctab-dominios">
      <div style="display:flex;justify-content:space-between;align-items:center;gap:10px;
                  flex-wrap:wrap;margin-bottom:8px;">
        <div style="font-size:.58rem;color:var(--dim);letter-spacing:2px;
                     font-family:'Courier New',monospace;flex:1;min-width:200px;">
          ◈ ANÁLISIS POR DOMINIO — ordenado por p · Las síntesis de papers son siempre visibles.<br>
          <span style="color:#2a4a6a;">El botón consulta Semantic Scholar en vivo. Cooldown 60 s.</span>
        </div>
        <button id="mc-btn-minerva" onclick="mcBuscarMinerva()" style="
          cursor:pointer;background:rgba(0,229,255,.12);border:1px solid rgba(0,229,255,.45);
          color:#00e5ff;font-size:.72rem;font-weight:bold;padding:7px 16px;border-radius:6px;
          font-family:'Courier New',monospace;letter-spacing:1px;white-space:nowrap;
          flex-shrink:0;transition:all .2s;">🔍 Buscar en SS</button>
      </div>
      <div id="mc-minerva-status" style="display:none;margin-bottom:8px;padding:6px 10px;
           background:rgba(0,0,0,.3);border-left:3px solid rgba(0,229,255,.4);border-radius:4px;
           font-size:.6rem;"></div>
      <div class="cards-grid">
        {cards}
      </div>
      <!-- Historial Dominios -->
      <div style="margin-top:14px;border-top:1px solid #131f2e;padding-top:10px;">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px;margin-bottom:6px;">
          <div style="font-size:.6rem;color:var(--cyan);font-weight:bold;letter-spacing:.5px;">
            ◈ HISTORIAL · Búsquedas anteriores
          </div>
          <div style="display:flex;gap:6px;align-items:center;">
            <div style="font-size:.55rem;color:var(--dim);">Se actualiza al buscar o al ejecutar lum_mapa_cierres.py</div>
            <button onclick="_mcExportHistorial(_MC_LS_MINERVA,'Dominios','#00e5ff')"
              style="background:none;border:1px solid #00e5ff44;color:#00e5ff99;font-size:.54rem;
                     padding:3px 8px;border-radius:4px;cursor:pointer;font-family:monospace;"
              title="Descargar historial completo como HTML">📥 Exportar</button>
          </div>
        </div>
        <div id="mc-minerva-historial">{minerva_historial_panel}</div>
      </div>
    </div>

    <!-- Panel: Clásicos Fundacionales -->
    <div id="mctab-clasicos" style="display:none;">
      <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;
                  flex-wrap:wrap;margin-bottom:10px;">
        <div style="font-size:.58rem;color:var(--dim);line-height:1.8;flex:1;min-width:200px;">
          ★ CORPUS FUNDACIONAL — Obras clásicas · identidades sintéticas · TCC (Bueno 1992–1993)<br>
          p_sint = grado de cierre alcanzado · τ_verde ≥ 0.80 · τ_rojo &lt; 0.40 ·
          <span style="color:#3a5a7a;">Verificar busca papers relacionados en Semantic Scholar.</span>
        </div>
        <button id="mc-btn-clasicos" onclick="mcBuscarClasicos()" style="
          cursor:pointer;background:rgba(255,213,79,.10);border:1px solid rgba(255,213,79,.40);
          color:#ffd54f;font-size:.68rem;font-weight:bold;padding:7px 16px;border-radius:6px;
          font-family:'Courier New',monospace;letter-spacing:1px;white-space:nowrap;
          flex-shrink:0;transition:all .2s;">📚 Verificar en SS</button>
      </div>
      <div id="mc-cl-status" style="display:none;margin-bottom:8px;padding:6px 10px;
           background:rgba(0,0,0,.3);border-left:3px solid rgba(255,213,79,.4);border-radius:4px;
           font-size:.6rem;"></div>
      {clasicos_html}
      <div style="margin-top:8px;font-size:.54rem;color:var(--dim);line-height:1.7;
                  border-top:1px solid var(--border);padding-top:8px;">
        <span style="color:var(--cyan);">◈ Nota metodológica:</span>
        Los scores no provienen de Semantic Scholar sino de la aplicación directa de la TCC
        (Bueno 1992–1993). Verde = cierre categorial completo. Ámbar = cierre parcial.
        Rojo = proto-cierre sin identidades sintéticas estables.
      </div>
      <!-- Historial Clásicos -->
      <div style="margin-top:12px;border-top:1px solid #131f2e;padding-top:10px;">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px;margin-bottom:6px;">
          <div style="font-size:.6rem;color:#ffd54f;font-weight:bold;letter-spacing:.5px;">
            📚 HISTORIAL · Verificaciones Semantic Scholar
          </div>
          <div style="display:flex;gap:6px;align-items:center;">
            <div style="font-size:.55rem;color:var(--dim);">Se actualiza al usar el botón Verificar en SS</div>
            <button onclick="_mcExportHistorial(_MC_LS_CLASICOS,'Clásicos','#ffd54f')"
              style="background:none;border:1px solid #ffd54f44;color:#ffd54f99;font-size:.54rem;
                     padding:3px 8px;border-radius:4px;cursor:pointer;font-family:monospace;"
              title="Descargar historial completo como HTML">📥 Exportar</button>
          </div>
        </div>
        <div id="mc-cl-historial">{clasicos_historial_panel}</div>
      </div>
    </div>
  </div>

</div>
<script>
// ── HISTORIAL localStorage — persiste entre recargas ─────────────────────────
var _MC_LS_MINERVA = 'lum_minerva_historial';
var _MC_LS_CLASICOS = 'lum_clasicos_historial';
var _MC_LS_MAX  = 200;
var _MC_LS_SHOW = 20;
var _MC_LS_KEEP = 100;

// ── Session ID persistente ────────────────────────────────────────────────
function _mcGetSid() {{
  var sid = localStorage.getItem('lum_sid');
  if (!sid) {{ sid = Date.now().toString(36) + Math.random().toString(36).slice(2,6); localStorage.setItem('lum_sid', sid); }}
  return sid;
}}
var _MC_LUM_SID = _mcGetSid();

function _mcExportHistorialArr(arr, titulo, color) {{
  if (!arr.length) {{ alert('Sin entradas en el historial aún.'); return; }}
  var _sid = _MC_LUM_SID || 'local';
  var rows = '';
  arr.forEach(function(e, i) {{
    var ts = (e.timestamp||'').slice(0,19).replace('T',' ');
    var total = e.total_papers || e.total_papers_found || 0;
    var src = e.source||'';
    var esid = e.sid||'—';
    var detail = '';
    if (e.dominios) {{
      Object.keys(e.dominios).forEach(function(k) {{
        var dd = e.dominios[k]||{{}};
        var col2 = dd.semaforo==='GREEN'?'#00ff88':(dd.semaforo==='AMBER'?'#ffd54f':'#ff3d5a');
        detail += '<span style="display:inline-block;margin:2px 3px;padding:2px 7px;border-radius:3px;border:1px solid '+col2+'55;background:'+col2+'14;color:'+col2+';font-size:.78rem;">'+k+' '+(dd.n_papers_ss||0)+'p</span>';
      }});
    }} else if (e.obras) {{
      Object.keys(e.obras).forEach(function(k) {{
        var n = (e.obras[k]||{{}}).n_papers||0;
        var col2 = n>=3?'#00ff88':(n>0?'#ffd54f':'#555');
        detail += '<span style="display:inline-block;margin:2px 3px;padding:2px 7px;border-radius:3px;border:1px solid '+col2+'55;background:'+col2+'14;color:'+col2+';font-size:.75rem;">'+k.replace(/_/g,' ')+' '+n+'p</span>';
      }});
    }}
    var bg = i%2===0?'#0a1520':'#0d1a28';
    rows += '<tr style="background:'+bg+';">'
      +'<td style="padding:8px 12px;color:#4a7090;font-size:.8rem;">'+(i+1)+'</td>'
      +'<td style="padding:8px 12px;color:#5a8aaa;font-size:.8rem;font-family:monospace;white-space:nowrap;">'+ts+'</td>'
      +'<td style="padding:8px 12px;color:#3a6080;font-size:.75rem;">'+src+'</td>'
      +'<td style="padding:8px 12px;color:'+color+';font-weight:bold;font-size:.8rem;">'+total+'</td>'
      +'<td style="padding:8px 12px;color:#2a4060;font-size:.7rem;font-family:monospace;">'+esid+'</td>'
      +'<td style="padding:8px 12px;">'+detail+'</td>'
      +'</tr>';
  }});
  var now = new Date().toISOString().slice(0,19).replace('T',' ');
  var tsFirst = arr.length ? (arr[arr.length-1].timestamp||'').slice(0,10) : '';
  var tsLast  = arr.length ? (arr[0].timestamp||'').slice(0,10) : '';
  var html = '<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">'
    +'<title>MINERVA — '+titulo+'</title>'
    +'<style>body{{background:#060d14;color:#8aacbe;font-family:"Courier New",monospace;margin:0;padding:24px;}}'
    +'h1{{color:'+color+';font-size:1.1rem;letter-spacing:2px;border-bottom:1px solid '+color+'44;padding-bottom:10px;margin-bottom:6px;}}'
    +'.meta{{font-size:.72rem;color:#3a5a7a;margin-bottom:6px;line-height:1.8;}}'
    +'.sid{{display:inline-block;background:#0a1a2a;border:1px solid '+color+'44;color:'+color+'bb;padding:2px 10px;border-radius:4px;font-size:.72rem;letter-spacing:1px;margin-bottom:14px;}}'
    +'table{{width:100%;border-collapse:collapse;}} th{{background:#0a1a2a;color:#3a6080;padding:8px 12px;text-align:left;border-bottom:1px solid #1a3a5a;font-size:.72rem;letter-spacing:1px;}}'
    +'tr:hover td{{background:#0f2030!important;}} .total{{font-size:.78rem;color:#3a5a7a;margin-top:16px;}}</style></head><body>'
    +'<h1>◈ MINERVA ALFA LUM-vitae — '+titulo+'</h1>'
    +'<div class="meta">Exportado: '+now+' UTC &nbsp;·&nbsp; '+arr.length+' registros &nbsp;·&nbsp; rango: '+tsFirst+' → '+tsLast+'<br>Generado por ALFA LUM-vitae vΩ.4</div>'
    +'<div class="sid">SID: '+_sid+'</div>'
    +'<table><thead><tr><th>#</th><th>TIMESTAMP</th><th>FUENTE</th><th>PAPERS</th><th>SID</th><th>DETALLE</th></tr></thead>'
    +'<tbody>'+rows+'</tbody></table>'
    +'<div class="total">Total: '+arr.length+' registros · SID sesión actual: '+_sid+'</div>'
    +'</body></html>';
  var blob = new Blob([html], {{type:'text/html;charset=utf-8'}});
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  var tipo = (titulo.toLowerCase().indexOf('clas')>=0) ? 'clasicos' : 'dominios';
  a.download = 'lum_hist_'+tipo+'_'+new Date().toISOString().slice(0,10)+'_'+_sid+'.html';
  a.click();
  URL.revokeObjectURL(a.href);
}}
// Wrapper para botones manuales
function _mcExportHistorial(key, titulo, color) {{
  _mcExportHistorialArr(_mcLsLoad(key), titulo, color);
}}

function _mcLsSave(key, entrada) {{
  try {{
    var arr = JSON.parse(localStorage.getItem(key) || '[]');

    // ── Dedup híbrido: bloquear solo si contenido idéntico Y menos de 30 min ──
    if (arr.length > 0) {{
      var last = arr[0];
      var diffMs   = Date.now() - new Date(last.timestamp||0).getTime();
      var within30 = diffMs < 30 * 60 * 1000;
      if (within30) {{
        var sameTotal  = (last.total_papers||0) === (entrada.total_papers||0);
        var sameSource = last.source === entrada.source;
        if (sameTotal && sameSource) {{
          var mkMap = function(dom) {{
            var o = {{}};
            Object.keys(dom||{{}}).forEach(function(k) {{ o[k] = (dom[k]||{{}}).n_papers_ss||0; }});
            return JSON.stringify(o);
          }};
          if (mkMap(last.dominios) === mkMap(entrada.dominios)) return;
        }}
      }}
    }}

    entrada.sid = _MC_LUM_SID;   // estampar huella de sesión
    arr.unshift(entrada);

    if (arr.length > _MC_LS_MAX) {{
      var label = key.indexOf('clasicos')>=0 ? 'Clásicos' : 'Dominios';
      var col   = key.indexOf('clasicos')>=0 ? '#ffd54f' : '#00e5ff';
      _mcExportHistorialArr(arr.slice(_MC_LS_KEEP), label + ' — Archivo ' + new Date().toISOString().slice(0,10), col);
      arr.splice(_MC_LS_KEEP);
      var n = document.createElement('div');
      n.textContent = '📥 100 entradas antiguas exportadas — historial renovado (100 recientes conservadas)';
      n.style.cssText = 'position:fixed;bottom:20px;right:20px;background:#0a1a2a;border:1px solid '+col+';color:'+col+';padding:10px 16px;border-radius:6px;font-size:.7rem;z-index:9999;font-family:monospace;max-width:380px;';
      document.body.appendChild(n);
      setTimeout(function(){{ n.remove(); }}, 7000);
    }}
    localStorage.setItem(key, JSON.stringify(arr));
  }} catch(e) {{}}
}}

function _mcLsLoad(key) {{
  try {{ return JSON.parse(localStorage.getItem(key) || '[]'); }}
  catch(e) {{ return []; }}
}}

function _mcBuildMinEntry(e) {{
  var ts = (e.timestamp||'').slice(0,16).replace('T',' ');
  var doms = e.dominios || {{}};
  var tags = Object.keys(doms).map(function(k){{
    var dd = doms[k]||{{}};
    var col = dd.semaforo==='GREEN'?'#00ff88':(dd.semaforo==='AMBER'?'#ffd54f':'#ff3d5a');
    return '<span style="display:inline-block;padding:2px 5px;border-radius:3px;border:1px solid '+col+'44;background:'+col+'11;color:'+col+';font-size:.52rem;margin:2px;">'+k+'</span>';
  }}).join('');
  var ne = document.createElement('div');
  ne.className = 'mc-hist-entry';
  ne.style.cssText = 'border-bottom:1px solid #131f2e;padding:6px 0;font-size:.57rem;';
  ne.innerHTML = '<div style="display:flex;justify-content:space-between;">'
    +'<span style="color:#3a5a7a;">'+ts+'</span>'
    +'<span style="color:#00e5ff;">'+(e.total_papers||0)+' papers</span></div>'
    +'<div style="margin-top:3px;">'+tags+'</div>';
  return ne;
}}

function _mcBuildClEntry(e) {{
  var ts = (e.timestamp||'').slice(0,16).replace('T',' ');
  var obras = e.obras || {{}};
  var tags = Object.keys(obras).slice(0,6).map(function(k){{
    var n = (obras[k]||{{}}).n_papers||0;
    var col = n>=3?'#00ff88':(n>0?'#ffd54f':'#3a5a7a');
    return '<span style="display:inline-block;padding:2px 4px;border-radius:3px;border:1px solid '+col+'44;background:'+col+'11;color:'+col+';font-size:.50rem;margin:2px;">'+k.replace(/_/g,' ').slice(0,14)+' '+n+'p</span>';
  }}).join('');
  var ne = document.createElement('div');
  ne.className = 'mc-cl-hist-entry';
  ne.style.cssText = 'border-bottom:1px solid #131f2e;padding:6px 0;font-size:.57rem;';
  ne.innerHTML = '<div style="display:flex;justify-content:space-between;">'
    +'<span style="color:#3a5a7a;">'+ts+'</span>'
    +'<span style="color:#ffd54f;">'+(e.total_papers||e.total_papers_found||0)+' papers</span></div>'
    +'<div style="margin-top:3px;">'+tags+'</div>';
  return ne;
}}

function _mcRenderMinHist(panel, arr) {{
  if (!panel) return;
  panel.innerHTML = '';
  if (!arr.length) {{
    panel.innerHTML = '<div style="color:#2a4a6a;font-size:.57rem;padding:6px 0;">Sin búsquedas registradas aún.</div>';
    return;
  }}
  arr.slice(0, _MC_LS_SHOW).forEach(function(e){{ panel.appendChild(_mcBuildMinEntry(e)); }});
  if (arr.length > _MC_LS_SHOW) {{
    var rest = arr.length - _MC_LS_SHOW;
    var btn = document.createElement('button');
    btn.textContent = '▾ ver ' + rest + ' más (total ' + arr.length + ')';
    btn.style.cssText = 'background:none;border:1px solid #00e5ff33;color:#00e5ff88;font-size:.54rem;padding:4px 10px;border-radius:4px;cursor:pointer;margin-top:4px;width:100%;';
    btn.onclick = function() {{ arr.slice(_MC_LS_SHOW).forEach(function(e){{ panel.insertBefore(_mcBuildMinEntry(e), btn); }}); btn.remove(); }};
    panel.appendChild(btn);
  }}
}}

function _mcRenderClHist(panel, arr) {{
  if (!panel) return;
  panel.innerHTML = '';
  if (!arr.length) {{
    panel.innerHTML = '<div style="color:#2a4a6a;font-size:.57rem;padding:6px 0;">Sin verificaciones registradas aún.</div>';
    return;
  }}
  arr.slice(0, _MC_LS_SHOW).forEach(function(e){{ panel.appendChild(_mcBuildClEntry(e)); }});
  if (arr.length > _MC_LS_SHOW) {{
    var rest = arr.length - _MC_LS_SHOW;
    var btn = document.createElement('button');
    btn.textContent = '▾ ver ' + rest + ' más (total ' + arr.length + ')';
    btn.style.cssText = 'background:none;border:1px solid #ffd54f33;color:#ffd54f88;font-size:.54rem;padding:4px 10px;border-radius:4px;cursor:pointer;margin-top:4px;width:100%;';
    btn.onclick = function() {{ arr.slice(_MC_LS_SHOW).forEach(function(e){{ panel.insertBefore(_mcBuildClEntry(e), btn); }}); btn.remove(); }};
    panel.appendChild(btn);
  }}
}}

// ── TAB SWITCHER ──────────────────────────────────────────────────────────────
var _mcTabAccents = {{dominios:'#00e5ff',clasicos:'#ffd54f'}};
document.addEventListener('DOMContentLoaded', function() {{
  mcSwitchTab('dominios');
  _mcRenderMinHist(document.getElementById('mc-minerva-historial'), _mcLsLoad(_MC_LS_MINERVA));
  _mcRenderClHist(document.getElementById('mc-cl-historial'), _mcLsLoad(_MC_LS_CLASICOS));
}});
function mcSwitchTab(tab) {{
  ['dominios','clasicos'].forEach(function(t) {{
    var panel = document.getElementById('mctab-' + t);
    var btn   = document.getElementById('mctab-btn-' + t);
    if (!panel || !btn) return;
    var active = (t === tab);
    var ac = _mcTabAccents[t];
    panel.style.display = active ? 'block' : 'none';
    btn.style.background  = active ? (ac==='#00e5ff' ? 'rgba(0,229,255,.14)' : 'rgba(255,213,79,.14)') : 'rgba(0,0,0,.2)';
    btn.style.borderColor = active ? (ac==='#00e5ff' ? 'rgba(0,229,255,.35)' : 'rgba(255,213,79,.35)') : '#1a2a3a';
    btn.style.color       = active ? ac : '#3a5a7a';
    btn.style.fontWeight  = active ? 'bold' : 'normal';
  }});
}}

// ── HELPERS ───────────────────────────────────────────────────────────────────
function mcShowStatus(id, msg, col) {{
  var el = document.getElementById(id);
  if (!el) return;
  el.style.display = msg ? 'block' : 'none';
  el.style.borderLeftColor = col || 'rgba(0,229,255,.4)';
  el.innerHTML = msg || '';
}}
function mcSetBtn(id, disabled, label) {{
  var b = document.getElementById(id);
  if (!b) return;
  b.disabled = disabled;
  b.textContent = label;
  b.style.opacity = disabled ? '.5' : '1';
  b.style.cursor = disabled ? 'not-allowed' : 'pointer';
}}

// ── FETCH WITH RETRY ──────────────────────────────────────────────────────────
// SIN AbortController: evita error "AbortSignal cannot be cloned" en extensiones Chrome
async function mcFetchRetry(url, ms, tries) {{
  tries = tries || 2;
  for (var attempt=0; attempt<=tries; attempt++) {{
    try {{
      var _fp = fetch(url);
      var _tp = new Promise(function(_, rej) {{
        setTimeout(function() {{ rej(new Error('timeout_' + ms)); }}, ms);
      }});
      var r = await Promise.race([_fp, _tp]);
      if (r.status === 429) {{
        if (attempt < tries) {{ await new Promise(function(rv){{ setTimeout(rv, 1500*(attempt+1)); }}); continue; }}
        return null;
      }}
      return r;
    }} catch(e) {{
      if (attempt < tries) {{ await new Promise(function(rv){{ setTimeout(rv, 900*(attempt+1)); }}); }}
    }}
  }}
  return null;
}}

// ── Rotación de offset por clave (localStorage) ───────────────────────────
var _MC_OFFSET_KEY = 'lum_mc_offsets';
function _mcNextOffset(key) {{
  var offs = {{}};
  try {{ offs = JSON.parse(localStorage.getItem(_MC_OFFSET_KEY) || '{{}}'); }} catch(e) {{}}
  var off = offs[key] || 0;
  offs[key] = (off + 5) % 40;  // páginas de 5 (0,5,10,15,20,25,30,35)
  try {{ localStorage.setItem(_MC_OFFSET_KEY, JSON.stringify(offs)); }} catch(e) {{}}
  return off;
}}

// ── BUSCAR DOMINIOS EN SEMANTIC SCHOLAR ───────────────────────────────────────
var _mcSearching = false;
var _mcLastAt = 0;
var MC_SS_QUERIES = {{
  'FORM':    'categorical closure formal mathematics axiomatic systems',
  'NAT':     'categorical closure natural sciences causal laws empirical',
  'TEC':     'categorical closure engineering technology systems design',
  'SOC_IV':  'categorical closure social sciences interpretive hermeneutics',
  'SOC_DID': 'categorical closure social sciences diachronic historical',
  'ARTE':    'categorical closure aesthetics art symbolic materialist philosophy'
}};
async function mcBuscarMinerva() {{
  if (_mcSearching) return;
  var now = Date.now();
  if (now - _mcLastAt < 30000) {{
    mcShowStatus('mc-minerva-status', '⏳ Cooldown — espera ' + Math.ceil((30000-(now-_mcLastAt))/1000) + ' s', '#ffd54f');
    return;
  }}
  _mcSearching = true;
  _mcLastAt = now;
  mcSetBtn('mc-btn-minerva', true, '🔍 Buscando…');
  mcShowStatus('mc-minerva-status', '⏳ Consultando Semantic Scholar (6 dominios)…', '#00e5ff');
  var baseUrl = 'https://api.semanticscholar.org/graph/v1/paper/search';
  var results = {{}};
  var ok = 0;
  for (var dom in MC_SS_QUERIES) {{
    var q = encodeURIComponent(MC_SS_QUERIES[dom]);
    var _mOff = _mcNextOffset('DOM_' + dom);
    var url = baseUrl + '?query=' + q + '&offset=' + _mOff + '&limit=5&fields=title,year,externalIds';
    try {{
      var r = await mcFetchRetry(url, 14000, 1);
      if (r && r.ok) {{
        var d = await r.json();
        results[dom] = (d.data || []).length;
        ok++;
      }} else {{
        results[dom] = 0;
      }}
    }} catch(e) {{ results[dom] = 0; }}
    await new Promise(function(rv){{ setTimeout(rv, 400); }});
  }}
  var ts = new Date().toLocaleTimeString('es-MX',{{hour:'2-digit',minute:'2-digit'}});
  if (ok === 0) {{
    mcShowStatus('mc-minerva-status', '\u26a0 No se pudo contactar Semantic Scholar \u00b7 ' + ts + ' — verifica conexión o intenta más tarde.', '#ff3d5a');
  }} else {{
    var summary = Object.keys(results).map(function(k){{ return k+':'+results[k]; }}).join(' · ');
    mcShowStatus('mc-minerva-status', '\u2713 SS consultado \u00b7 ' + ts + ' \u00b7 ' + summary, '#00ff88');
    var _mcEntrada = {{
      timestamp: new Date().toISOString(),
      source: 'live_mapa',
      total_papers: Object.values(results).reduce(function(a,b){{return a+b;}},0),
      dominios: Object.fromEntries(Object.keys(results).map(function(k){{
        return [k, {{p_sintetico:0, semaforo:'N/A', n_papers_ss:results[k], score_ss:0}}];
      }}))
    }};
    // 1. localStorage (persiste sin Flask)
    _mcLsSave(_MC_LS_MINERVA, _mcEntrada);
    // 2. Flask (silencioso)
    try {{ fetch('http://localhost:5050/api/minerva_historial', {{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(_mcEntrada)}}).catch(function(){{}}); }} catch(e) {{}}
    // 3. Actualizar panel
    var panel = document.getElementById('mc-minerva-historial');
    if (panel) _mcRenderMinHist(panel, _mcLsLoad(_MC_LS_MINERVA));
  }}
  mcSetBtn('mc-btn-minerva', false, '🔍 Buscar en SS');
  _mcSearching = false;
}}

// ── VERIFICAR CLÁSICOS EN SEMANTIC SCHOLAR ────────────────────────────────────
var _mcClSearching = false;
var _mcClLastAt = 0;
var MC_CL_QUERIES = {{
  'EUCLID_ELEMENTOS':  'Euclid Elements geometry axiomatic formal',
  'NEWTON_PRINCIPIA':  'Newton Principia Mathematica natural philosophy mechanics',
  'BUENO_TCC':         'Bueno teoria cierre categorial materialismo filosofico',
  'FREGE_BEGRIF':      'Frege Begriffsschrift formal logic predicate calculus',
  'MAXWELL_ECUACIONES':'Maxwell equations electromagnetism field theory',
  'DARWIN_ORIGEN':     'Darwin origin of species natural selection evolution',
  'ARISTOTELES_ORGANON':'Aristotle Organon logic syllogism categories',
  'KANT_KRV':          'Kant Critique of Pure Reason transcendental idealism',
  'BUENO_ANIMAL_DIVINO':'Bueno El animal divino religion philosophy materialism',
  'MARX_CAPITAL':      'Marx Capital political economy commodity labour value',
  'SAUSSURE_CLG':      'Saussure cours linguistique generale structural linguistics',
  'FREUD_SUENOS':      'Freud interpretation of dreams psychoanalysis unconscious',
  'HEGEL_FENOMENOLOGIA':'Hegel Phenomenology of Spirit dialectic absolute idealism',
  'NIETZSCHE_ZARATHUSTRA':'Nietzsche Thus Spoke Zarathustra nihilism will to power'
}};
async function mcBuscarClasicos() {{
  if (_mcClSearching) return;
  var now = Date.now();
  if (now - _mcClLastAt < 30000) {{
    mcShowStatus('mc-cl-status', '⏳ Cooldown — espera ' + Math.ceil((30000-(now-_mcClLastAt))/1000) + ' s', '#ffd54f');
    return;
  }}
  _mcClSearching = true;
  _mcClLastAt = now;
  mcSetBtn('mc-btn-clasicos', true, '📚 Verificando…');
  mcShowStatus('mc-cl-status', '⏳ Consultando Semantic Scholar (14 obras)…', '#ffd54f');
  var baseUrl = 'https://api.semanticscholar.org/graph/v1/paper/search';
  var totalFound = 0;
  var hitsCount = 0;
  var ok = 0;
  var obrasCounts = {{}};  // rastrea counts directamente (badge DOM no existe en mapa)
  for (var key in MC_CL_QUERIES) {{
    var q = encodeURIComponent(MC_CL_QUERIES[key]);
    var _cOff = _mcNextOffset('CL_' + key);
    var url = baseUrl + '?query=' + q + '&offset=' + _cOff + '&limit=4&fields=title,year';
    obrasCounts[key] = 0;
    try {{
      var r = await mcFetchRetry(url, 13000, 1);
      if (r && r.ok) {{
        var d = await r.json();
        var n = (d.data || []).length;
        obrasCounts[key] = n;
        totalFound += n;
        if (n > 0) hitsCount++;
        ok++;
      }}
    }} catch(e) {{ /* sin resultado para esta obra */ }}
    await new Promise(function(rv){{ setTimeout(rv, 350); }});
  }}
  var ts = new Date().toLocaleTimeString('es-MX',{{hour:'2-digit',minute:'2-digit'}});
  if (ok === 0) {{
    mcShowStatus('mc-cl-status', '\u26a0 No se pudo contactar Semantic Scholar \u00b7 ' + ts, '#ff3d5a');
  }} else {{
    mcShowStatus('mc-cl-status',
      '\u2713 Verificación completa \u00b7 ' + ts + ' \u00b7 '
      + hitsCount + '/14 obras con resultados \u00b7 ' + totalFound + ' papers total', '#00ff88');
    var _mcClEntrada = {{
      timestamp: new Date().toISOString(),
      total_papers: totalFound,
      total_papers_found: totalFound,
      obras_con_resultados: hitsCount,
      source: 'live_mapa',
      obras: Object.fromEntries(Object.keys(MC_CL_QUERIES).map(function(k){{
        return [k, {{n_papers: obrasCounts[k]||0}}];
      }}))
    }};
    // 1. localStorage (persiste sin Flask)
    _mcLsSave(_MC_LS_CLASICOS, _mcClEntrada);
    // 2. Flask (silencioso)
    try {{ fetch('http://localhost:5050/api/clasicos_historial', {{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(_mcClEntrada)}}).catch(function(){{}}); }} catch(e) {{}}
    // 3. Actualizar panel
    var panel = document.getElementById('mc-cl-historial');
    if (panel) _mcRenderClHist(panel, _mcLsLoad(_MC_LS_CLASICOS));
  }}
  mcSetBtn('mc-btn-clasicos', false, '📚 Verificar en SS');
  _mcClSearching = false;
}}

// ── AUTO-RELOAD via sentinel lum_build_mapa.txt (funciona con file://) ───────
var _BUILD_TS = '{now_str}';
(function() {{
  var _arKnown = _BUILD_TS.trim(), _arNotif = null;
  var _arSentinel = location.href.replace(/[^/\\\\]*$/, 'lum_build_mapa.txt');
  function _arCheck() {{
    fetch(_arSentinel + '?_=' + Date.now())
      .then(function(r) {{ return r.text(); }})
      .then(function(txt) {{
        txt = txt.trim();
        if (!txt) return;
        if (_arKnown && txt !== _arKnown) {{
          if (_arNotif) return;
          _arKnown = txt;
          _arNotif = document.createElement('div');
          _arNotif.innerHTML = '🔄 Mapa actualizado — recargando en <b id="_ar_cnt_mc">5</b>s &nbsp;<span style="cursor:pointer;color:#3a6080;" onclick="this.parentElement.remove();">✕</span>';
          _arNotif.style.cssText = 'position:fixed;top:12px;right:12px;background:#0a1a2a;border:1px solid #00e5ff66;color:#00e5ffcc;padding:10px 16px;border-radius:6px;font-size:.72rem;z-index:99999;font-family:monospace;box-shadow:0 4px 20px #000a;';
          document.body.appendChild(_arNotif);
          var cnt = 5;
          var tick = setInterval(function() {{
            cnt--;
            var el = document.getElementById('_ar_cnt_mc');
            if (el) el.textContent = cnt;
            if (cnt <= 0) {{ clearInterval(tick); location.reload(); }}
          }}, 1000);
        }}
        if (!_arKnown) _arKnown = txt;
      }}).catch(function() {{}});
  }}
  setTimeout(_arCheck, 2000);
  setInterval(_arCheck, 10000);
}})();
</script>

<!-- ═══════════════════════════════════════════════════════════════════
     ARCHIVO DE EVIDENCIA POR SEMÁFORO
     Todos los papers clasificados por nivel de cierre y dominio.
     Se actualiza automáticamente cada vez que MINERVA explora.
     ═══════════════════════════════════════════════════════════════════ -->
<div style="max-width:1400px;margin:32px auto 0;padding:0 24px 48px;">

  <div style="font-size:.62rem;color:var(--dim);letter-spacing:3px;text-transform:uppercase;
               font-family:'Courier New',monospace;margin-bottom:20px;
               border-top:1px solid var(--border);padding-top:20px;
               display:flex;align-items:center;gap:12px;">
    <span>◈ ARCHIVO DE EVIDENCIA — clasificado por semáforo y dominio</span>
    <span style="color:#1a3a5a;font-size:.57rem;">Se actualiza con cada exploración MINERVA · {explo}</span>
  </div>

  {archivo_semaforo if archivo_semaforo else
   '<div style="font-size:.7rem;color:#2a4a6a;padding:16px;background:rgba(0,0,0,.2);border-radius:8px;">Sin evidencia bibliográfica aún — corre la tarea lum-minerva-exploracion para poblar el archivo.</div>'}

  <div style="text-align:center;margin-top:32px;font-size:.57rem;color:var(--dim);letter-spacing:2px;">
    ALFA LUM-vitae vΩ.4 · LUM-PE vΩ.2026-02 · Materialismo Filosófico · Gustavo Bueno + Luminomática<br>
    Proyecto MINERVA · DOI 10.5281/zenodo.19142481
  </div>

</div>
</body>
</html>"""

    OUT_HTML.write_text(page, encoding="utf-8")
    # Sentinel PROPIO del mapa (evita conflicto con el del dashboard)
    sentinel = OUT_HTML.parent / "lum_build_mapa.txt"
    sentinel.write_text(now_str, encoding="utf-8")
    print(f"[OK] Dashboard HTML generado → {OUT_HTML}")
# ─── ENTRY POINT ─────────────────────────────────────────────────────────────

def generar():
    """Función importable: regenera HTML desde el JSON existente (sin tocar el JSON)."""
    if OUT_JSON.exists():
        data = json.loads(OUT_JSON.read_text())
        generar_html(data)
    else:
        print(f"[WARN] {OUT_JSON} no existe. Corre sin --html-only para generarlo.")

if __name__ == "__main__":
    if MODO_HTML_ONLY:
        # Solo regenerar HTML desde el JSON cacheado — no toca el JSON
        calcular_clasicos()   # siempre actualiza clásicos (son estáticos)
        generar()
        print("\n✓ HTML regenerado desde caché.")
    else:
        calcular_clasicos()
        data = calcular_mapa()
        generar_html(data)
        print("\n✓ Todo listo.")
