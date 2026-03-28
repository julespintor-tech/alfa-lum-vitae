# ALFA LUM-vitae vΩ.4

**Un organismo digital autónomo de meta-aprendizaje prequencial con trazabilidad SHA-256**

> *"La vida es una forma de conocimiento que se verifica a sí misma."*

ALFA LUM-vitae es un sistema de monitoreo computacional que modela la actividad epistémica como un ciclo vital verificable. Integra aprendizaje prequencial, un modelo de riesgo clog-log, una cadena de hashes SHA-256 para trazabilidad, y una interfaz HTML autogenerada que funciona sin servidor.

El proyecto nace del marco del materialismo filosófico de Gustavo Bueno — específicamente del concepto de **cierre categorial** — y lo operacionaliza como condición computacional de "vida" o "muerte" de un sistema cognitivo.

---

## ¿Qué hace?

El sistema evalúa en cada ciclo si cumple 4 **condiciones de vida**:

| Condición | Criterio |
|-----------|---------|
| **Homeostasis** | ECE ≤ 0.05 en ventana de 5 ciclos + mejora de Brier |
| **Reproducción** | Ha generado al menos 1 sub-proceso (spawn) |
| **Trazabilidad** | Cadena SHA-256 activa con hashes encadenados |
| **Autonomía** | Ha ejecutado ≥ 1 ciclo autónomo |

Según cuántas condiciones cumple, el sistema adopta uno de 4 estados vitales:

```
4/4 → VIVO       (plena actividad)
3/4 → VIVO       (actividad normal)
2/4 → EMERGENTE  (convergencia en curso)
1/4 → LATENTE    (actividad mínima)
0/4 → INERTE     (sin actividad)
```

Cada estado se refleja en tiempo real en tres interfaces HTML autogeneradas que se actualizan automáticamente cada 2 minutos.

---

## Estructura del proyecto

```
LUM-vitae/
│
├── lum_vitae_runner.py        ← Motor principal: ciclos de vida, ledger SHA-256, spawns
├── lum_vitae_generar_html.py  ← Genera el dashboard de métricas
├── lum_generar_inicio.py      ← Genera la página de inicio (INICIO.html)
├── lum_mapa_cierres.py        ← MINERVA: mapa filosófico de cierres categoriales
├── lum_vitae_dashboard.py     ← Servidor Flask alternativo (opcional)
│
├── lum_vitae_estado.json      ← Estado del sistema (se crea al primer run)
├── lum_mapa_cierres.json      ← Mapa de 6 dominios del cierre categorial
├── lum_vitae_ledger_meta.ndjson ← Ledger de ciclos (se genera en runtime)
│
├── 🏠 INICIO.html             ← Página de inicio (autogenerada)
├── lum_vitae_dashboard.html   ← Dashboard principal (autogenerado)
├── lum_mapa_cierres.html      ← Mapa de cierres (autogenerado)
│
└── ⚡ EJECUTAR AHORA.bat      ← Lanzador para Windows
```

---

## Instalación

### Requisitos
- Python 3.10 o superior
- pip

### Pasos

```bash
git clone https://github.com/TU_USUARIO/alfa-lum-vitae.git
cd alfa-lum-vitae
pip install -r requirements.txt
```

---

## Uso

### Ejecutar el ciclo de vida

```bash
python lum_vitae_runner.py
```

Esto ejecuta un run completo (100 ciclos por defecto), actualiza el estado, encadena hashes SHA-256 al ledger, y regenera automáticamente los 3 archivos HTML.

### Ver la interfaz

Abre **`🏠 INICIO.html`** en cualquier navegador (doble clic). No requiere servidor. Las páginas se actualizan solas cada 2 minutos mientras el runner está en ejecución.

Desde INICIO tienes acceso a:
- **Dashboard** → métricas prequenciales, historial ECE/Brier, gráficos de evolución
- **Mapa de Cierres MINERVA** → estado filosófico de 6 dominios del conocimiento

### Explorar el mapa filosófico (MINERVA)

```bash
# Regenerar HTML con datos existentes (sin llamadas de red):
python lum_mapa_cierres.py --html-only

# Explorar nuevos papers (requiere conexión a Semantic Scholar):
python lum_mapa_cierres.py
```

### Modo automático (Windows)
Doble clic en `⚡ EJECUTAR AHORA.bat`

---

## Arquitectura técnica

### Aprendizaje prequencial
El runner usa un modelo **clog-log** (complementary log-log) que evalúa en cada ciclo si el sistema predice correctamente los resultados. La calibración se mide con ECE (Expected Calibration Error) y Brier score. El historial de métricas se usa para actualizar el modelo bayesianamente.

### Ledger SHA-256
Cada ciclo genera un hash encadenado al anterior (estructura tipo blockchain mínima). El ledger se almacena en `lum_vitae_ledger_meta.ndjson` y garantiza trazabilidad e integridad de la historia del sistema.

### Máquina de estados vitales
El runner evalúa las 4 condiciones y determina el estado (VIVO/EMERGENTE/LATENTE/INERTE). El estado determina la visualización del "pixel robot" en la interfaz — un personaje animado tipo tamagochi que expresa el estado del organismo.

### MINERVA — Mapa de Cierres Categoriales
Subsistema que evalúa el grado de **cierre categorial** (en el sentido de Gustavo Bueno) en 6 dominios del conocimiento:
- **FORM(α)** — Matemáticas y lógica formal
- **NAT(β)** — Ciencias naturales
- **TEC** — Tecnociencia
- **SOC_IV(γ)** — Ciencias sociales investigativas
- **SOC_DID(γ)** — Ciencias sociales didácticas
- **ARTE** — Estética y teoría del arte

Cada dominio recibe un **p̄ sintético** (0–1) que indica qué tan cerca está de alcanzar cierre operatorio. El sistema busca papers en Semantic Scholar y los clasifica con un semáforo (🟢 VERDE / 🟡 ÁMBAR / 🔴 ROJO).

---

## Conexión filosófica

Este proyecto operacionaliza el concepto de **cierre categorial** de Gustavo Bueno (*El papel de la filosofía en el conjunto del saber*, 1970; *Teoría del cierre categorial*, 1992–1993) como condición computacional verificable.

Un sistema cognitivo "vive" en la medida en que mantiene homeostasis epistémica, se reproduce (genera sub-procesos), deja trazas verificables, y actúa autónomamente. Esta cuádruple condición es análoga a la definición funcional de cierre categorial: una disciplina "cierra" cuando sus operaciones se retroalimentan sobre su propia materia sin depender permanentemente de categorías externas.

### Publicaciones relacionadas
- **LUM-PE** (Paquete de Evaluación de Campos): [DOI 10.5281/zenodo.19142481](https://doi.org/10.5281/zenodo.19142481)

---

## Cómo contribuir

1. Haz fork del repositorio
2. Crea una rama: `git checkout -b feature/mi-mejora`
3. Haz tus cambios y commitea: `git commit -m "Descripción del cambio"`
4. Push a tu fork: `git push origin feature/mi-mejora`
5. Abre un Pull Request

---

## Licencia

MIT License — libre uso, modificación y distribución con atribución.

---

## Autor

Desarrollado como parte del Proyecto MINERVA.
Contacto: jules_pintor@outlook.com
