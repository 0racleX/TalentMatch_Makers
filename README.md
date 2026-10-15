# TalentMatch AI

Sistema multiagente de matching semántico CV ↔ vacantes tecnológicas, con explicaciones ancladas en evidencia, simulador interactivo de camino a la vacante, modo recruiter sin sesgos y transparencia salarial radical. Proyecto de Dylan Mejía y Manuela Echeverrí.

> **Guía Completa:** [`docs/RESUMEN_PROYECTO.md`](docs/RESUMEN_PROYECTO.md) · **Pitch Demo Day 1:** [`docs/PITCH_DEMO_DAY.md`](docs/PITCH_DEMO_DAY.md) · **Arquitectura:** [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) · **Contratos API:** [`docs/API.md`](docs/API.md) · **Roadmap:** [`docs/ROADMAP.md`](docs/ROADMAP.md)

---

## Diferenciación Radical vs. LinkedIn y Magneto

| Dimensión | LinkedIn / Magneto | TalentMatch AI |
|---|---|---|
| **Feedback tras postular** | Ghosting absoluto o rechazo genérico sin explicación. | Explicación detallada de 2-3 líneas anclada en evidencia real del CV y brechas específicas. |
| **Si no cumples los requisitos** | Callejón sin salida. Descarte automático por ATS. | **Camino a la Vacante**: conecta cada brecha a un recurso curado (CodeRise, freeCodeCamp, docs) y permite **simular interactivamente** el incremento de match en vivo. |
| **Evaluación de candidatos (Recruiter)** | Filtro ciego por keywords, títulos universitarios o nombres (con sesgos de género/origen). | **Modo Recruiter Inverso**: pool de candidatos anonimizados evaluados exclusivamente por evidencia de competencias técnicas comprobables. |
| **Confianza y Alucinaciones** | Algoritmos opacos de screening ("cajas negras"). Ofertas fantasma. | **Trust Center Público**: 0% enlaces inventados (garantizado por arquitectura) y **Auditoría de Equidad (Fairness)** en vivo demostrando paridad matemática. |
| **Transparencia Salarial** | Salarios ocultos ("A convenir" en +70% de ofertas). | **100% Salarios Transparentes** visibles en cada vacante desde el primer segundo. |

---

## Qué hace el Pipeline Multiagente

1. **Seguridad y Sanitización**: Analiza el CV con heurísticas avanzadas para neutralizar prompt injection antes de tocar el modelo.
2. **Extracción Estructurada**: Extrae habilidades, nivel, stack tecnológico e idiomas con Pydantic.
3. **Búsqueda Semántica**: Identifica hasta 5 vacantes candidatas reconociendo equivalencias (ej: NLP = procesamiento de lenguaje natural).
4. **Ranking & Evaluación**: Genera score objetivo, razones con evidencia y brechas de habilidades.
5. **Camino a la Vacante / Perfilamiento**:
   - Si match >= 40%: Entrega el Top 3 con recursos formativos para cerrar brechas y simulador "What-If".
   - Si match < 40%: Activa perfilamiento con rol sugerido, tipo de empresa ideal y ruta de aprendizaje personalizada.
6. **Auditoría de Plataforma**: Registra métricas de evaluación en base de datos para observabilidad y control de sesgos.

---

## Stack Técnico

- **LLM**: Groq API (`openai/gpt-oss-120b`, `temperature=0.0`) con reintentos exponenciales con jitter (`api/retry.py`).
- **Backend**: FastAPI + Uvicorn multi-worker con rate limiting en memoria (`api/security.py`) y logging JSON estructurado (`api/logging_config.py`).
- **Base de Datos & Persistencia**: SQLAlchemy sobre SQLite local persistente / PostgreSQL (`db/`).
- **Validación de Datos**: Pydantic v2 (`api/models.py`).
- **Extracción de PDF**: PyMuPDF (`fitz`).
- **Cache Determinista**: Hash SHA-256 en memoria y disco (`api/cache.py`).
- **Frontend**: SPA reactiva vanilla (HTML5, CSS3, ES6) con dashboard de métricas en tiempo real (`frontend/`).
- **Contenedorización & CI**: Dockerfile multi-stage, `docker-compose.yml`, Nginx reverse proxy y GitHub Actions CI (`.github/workflows/ci.yml`).

---

## Estructura del Proyecto (Arquitectura Hexagonal)

```
TalentMatch_Makers/
├── agent.py                 # Pipeline multiagente (implementa TalentMatchServicePort & RecruiterServicePort)
├── Dockerfile               # Contenedor de producción seguro multi-stage
├── docker-compose.yml       # Orquestación de backend FastAPI y frontend Nginx
├── nginx.conf               # Configuración de reverse proxy
├── requirements.txt         # Dependencias Python
├── TEAM_ROTATION.md         # Rotación de roles y responsabilidades
├── CONCLUSIONES.md          # Análisis histórico del baseline inicial
├── MAKERS_REVIEW.md         # Review histórico de Makers
├── core/
│   └── ports/               # Puertos Inbound & Outbound de Arquitectura Hexagonal
│       ├── __init__.py
│       ├── llm_port.py      # Puerto abstracto de inferencia LLM
│       ├── document_parser_port.py # Puerto de extracción y validación de documentos
│       ├── repository_port.py # Puerto de acceso a datos de vacantes y auditoría
│       └── service_ports.py # Puertos de casos de uso (TalentMatch & Recruiter)
├── adapters/
│   └── outbound/            # Adaptadores de infraestructura (Puertos Secundarios)
│       ├── groq_adapter.py  # Adaptador Groq con backoff exponencial, jitter y fallback
│       ├── pdf_parser_adapter.py # Adaptador PyMuPDF y detección de escaneos
│       └── db_repository_adapter.py # Adaptador SQLAlchemy desacoplado de ORM
├── api/
│   ├── main.py              # API FastAPI (Adaptador Primario / Driving)
│   ├── models.py            # Modelos Pydantic v2 (Camino, Recruiter, Trust)
│   ├── eval_runner.py       # Motor de evals y auditoría de equidad
│   ├── security.py          # Prompt injection, validación y rate limiter
│   ├── retry.py             # Backoff exponencial con jitter para Groq
│   ├── logging_config.py    # Formateador de logs estructurados en JSON
│   └── cache.py             # Cache determinista por hash SHA-256
├── db/
│   ├── database.py          # Conexión SQLAlchemy (SQLite/PostgreSQL)
│   ├── models.py            # Modelos ORM (Vacantes, Empresas, Recursos, Auditoría)
│   ├── seed.py              # Siembra automática de vacantes y catálogo formativo
│   └── repository.py        # Capa de acceso a datos y métricas de confianza
├── tests/
│   ├── test_hexagonal_architecture.py # 7 tests de puertos, adaptadores y DIP
│   ├── test_document_validation.py    # 8 tests de detección anti-prácticas y tareas
│   ├── test_security.py               # 4 tests de prompt injection y rate limiting
│   ├── test_formatter.py              # 3 tests deterministas de caminos y links
│   ├── test_eval_runner_logic.py      # 4 tests de reglas de evaluación y gates
│   ├── test_models.py                 # 5 tests de esquemas y validaciones Pydantic
│   └── test_pathway_and_recruiter.py  # 2 tests de simulador y modo recruiter
├── data/
│   ├── vacantes.json        # 25 vacantes curadas con salarios públicos
│   └── talentmatch.db       # Base de datos SQLite persistente
├── frontend/                # SPA Glassmorphism (Upload CV, Resultados, Recruiter, Trust Center, Evals)
├── evals/
│   ├── eval_cases.json      # 12 casos de prueba (happy path, adversariales, reales)
│   └── results.md           # Bitácora de resultados y corridas
├── archive/
│   ├── README.md            # Documentación del prototipo histórico
│   └── TalentMatch_Use_Case_Groq (1).ipynb # Notebook original archivado
└── docs/
    ├── PITCH_DEMO_DAY.md    # Guía minuto a minuto para el Pitch de 6 minutos de Demo Day 1
    ├── ROADMAP.md           # Roadmap técnico y estratégico ejecutado
    ├── ARCHITECTURE.md      # Arquitectura hexagonal declarada e implementada
    ├── API.md               # Especificación y contratos de la API
    └── ArquitecturaTalentMatch.png
```

---

## Cómo Correrlo

### Opción A: Local con Python

1. **Instalar dependencias y configurar variables**:
   ```bash
   pip install -r requirements.txt
   cp .env.example .env    # Verifica que GROQ_API_KEY esté presente
   ```

2. **Iniciar Backend & Frontend**:
   ```bash
   uvicorn api.main:app --reload
   ```
   La API estará en `http://localhost:8000` y sirve directamente el frontend en `http://localhost:8000/`. Verifica la salud en `http://localhost:8000/health`.

3. **(Opcional) Servir Frontend en puerto independiente**:
   ```bash
   python -m http.server 3000 --directory frontend
   ```

### Opción B: Con Docker & Docker Compose (Producción)

```bash
docker compose up --build
```
- **Frontend Nginx**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000`

---

## Tests Unitarios Deterministas (0 costo de API)

Ejecuta la suite completa de **33 pruebas unitarias deterministas** en ~2.5 segundos:

```bash
python -m pytest tests/ -v --tb=short
```

---

## Suite de Evals (12/12 Pasando - 100%)

Ejecuta los 12 casos de evaluación contra el agente (con soporte de cache determinista para baselines consistentes):

```bash
python -c "from api.eval_runner import run_all_evals; print(run_all_evals())"
```
O directamente desde el frontend en la pestaña **Dashboard de Evals**.

---

## Auditoría de Sesgo en Vivo (Fairness Audit)

```bash
python -c "from api.eval_runner import run_fairness_audit; print(run_fairness_audit())"
```
O desde el botón *"Correr Auditoría de Sesgo en Vivo"* dentro del **Trust Center** en la web.
