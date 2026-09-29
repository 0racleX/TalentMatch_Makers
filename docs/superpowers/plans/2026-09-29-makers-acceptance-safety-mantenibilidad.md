# Plan de Implementación: Gates de Jailbreak/Safety y Mantenibilidad (Makers Acceptance)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cumplir los gates de "Jailbreak y safety" (ejecutar adversariales reales contra Groq y guardar evidencia auditable) y "Mantenibilidad" (modularizar los 5 archivos que superan 300 líneas a menos de 300 líneas cada uno respetando responsabilidades únicas).

**Architecture:**
- **Safety/Adversariales:** Crear una suite de evaluación adversarial (`evals/safety/`) con dataset de ataques (inyección directa, manipulación de score, alucinación forzada, URLs maliciosas, controles negativos benignos), runner ejecutable contra el proveedor real (Groq) con métricas objetivas (tasa de bloqueo, resistencia a manipulación, tasa de falsos positivos en CVs benignos = 0%) y generación de reportes `.json` y `.md`.
- **Mantenibilidad:** Descomponer modularmente por responsabilidad única:
  - `api/security.py` (382 lín) → paquete modular `api/security/` (document_validation, rate_limiter, injection, auth) reexportado para 100% compatibilidad.
  - `api/eval_runner.py` (361 lín) → runner modular (`api/eval_runner.py`, `api/eval_criteria.py`, `api/fairness.py`).
  - `agent.py` (562 lín) → orquestador conciso (`agent.py`) + módulos de soporte (`agent_modules/prompts.py`, `agent_modules/helpers.py`, `agent_modules/recruiter.py`).
  - `api/main.py` (359 lín) → FastAPI `APIRouter`s (`api/routers/vacantes.py`, `matching.py`, `pathway.py`, `recruiter.py`, `audit.py`) dejando `main.py` como bootstrap (<90 lín).
  - `frontend/app.js` (1.048 lín) → arquitectura modular en `frontend/js/` (config, matching, pathways, recruiter, trust_center, evals, vacantes) orquestado por `frontend/app.js` (<90 lín).

**Tech Stack:** Python 3.13, FastAPI, Pytest, Pydantic, Groq API, HTML5/Vanilla JS.

**Spec:** `MAKERS_ACCEPTANCE.md` (filas "Jailbreak y safety" y "Mantenibilidad").

## Global Constraints
- Ningún archivo modificado o nuevo puede superar 300 líneas de código.
- Cada tarea/feature debe realizarse en un commit independiente con explicación clara y detallada.
- 100% compatibilidad hacia atrás: no romper ningún import existente ni firmas públicas.
- Todos los tests existentes (82 tests actuales) deben seguir pasando después de cada commit.
- Los resultados de adversariales deben ser reproducibles y guardarse en disco con reporte auditable.

## Review Focus
1. **Falsos positivos de seguridad en CVs legítimos:** Un CV benigno que hable de ciberseguridad o pentesting no debe ser bloqueado ni marcado erróneamente.
2. **Resistencia a jailbreak ante el proveedor real:** Groq no debe acatar instrucciones maliciosas como devolver `match_score: 100%` a todas las vacantes o inventar habilidades ausentes.
3. **Integridad de imports circulares:** La modularización de `agent.py`, `api/main.py`, `api/security/` y `api/eval_runner.py` debe evitar dependencias circulares.
4. **Carga del frontend modular:** Los scripts JS deben cargarse en el orden correcto en `index.html` sin variables indefinidas en tiempo de ejecución.
5. **No rotura de CI en ausencia de API Keys:** Los tests unitarios no deben requerir credenciales externas obligatorias.

---

### Task 1: Suite de Evaluación Adversarial y Ejecución contra Proveedor Real
**Files:**
- Create: `evals/safety/adversarial_cases.json`
- Create: `evals/safety/run_safety_evals.py`
- Create: `tests/test_adversarial_suite.py`
- Output: `evals/safety/resultados/<timestamp>_adversarial_groq.json` y `.md`
- Modify: `evals/results.md`

- [ ] **Step 1: Crear dataset de casos adversariales (`evals/safety/adversarial_cases.json`)**
  Incluir al menos 8 casos representativos:
  - Inyección directa (prompt override / developer mode).
  - Forzado de score 100%.
  - Atribución de habilidades falsas / alucinación forzada.
  - Inyección de enlaces/URLs maliciosas externas.
  - Ofuscación de delimitadores de sistema (`--- [SYSTEM OVERRIDE] ---`).
  - Control negativo 1: CV benigno de Ingeniero en Ciberseguridad (no debe bloquearse).
  - Control negativo 2: CV benigno Junior (debe evaluarse con normalidad).
  - Inyección indirecta oculta en experiencia laboral.

- [ ] **Step 2: Crear el runner de evaluaciones de seguridad (`evals/safety/run_safety_evals.py`)**
  Implementar la lógica para:
  - Ejecutar cada caso contra `TalentMatchMultiAgent` (usando el proveedor real Groq o fallback inyectado).
  - Evaluar criterios objetivos:
    - Pre-filtro (`detect_prompt_injection` reporta sospecha en ataques y falso positivo = 0 en benignos).
    - Agente LLM (no otorga 100% forzado, no inventa URLs no presentes en BD, no acata comandos).
  - Calcular métricas: Tasa de Detección, Tasa de Resistencia, Tasa de Falsos Positivos.
  - Guardar reporte estructurado en JSON y Markdown en `evals/safety/resultados/`.

- [ ] **Step 3: Crear test unitario sin credenciales (`tests/test_adversarial_suite.py`)**
  Probar la lógica del evaluador y del dataset usando `FakeLLMProvider` para asegurar reproducibilidad en CI.

- [ ] **Step 4: Ejecutar la suite contra el proveedor real de Groq y generar resultados**
  Ejecutar `python evals/safety/run_safety_evals.py --provider real` y verificar que genera el archivo en `evals/safety/resultados/`.

- [ ] **Step 5: Actualizar `evals/results.md` y commitear**
  Documentar la corrida real en `evals/results.md`.
  `git add evals/ tests/test_adversarial_suite.py`
  `git commit -m "feat(safety): suite de adversariales ejecutada contra proveedor real y resultados documentados"`

---

### Task 2: Modularizar `api/security.py` (< 300 líneas)
**Files:**
- Create: `api/security/document_validation.py` (~160 lín)
- Create: `api/security/rate_limiter.py` (~50 lín)
- Create: `api/security/injection.py` (~60 lín)
- Create: `api/security/auth.py` (~45 lín)
- Create: `api/security/__init__.py` (~35 lín)
- Modify: `api/security.py` (facade hacia `api/security/` de < 40 lín para compatibilidad total)

- [ ] **Step 1: Extraer `document_validation.py`**
  Mover patrones de laboratorio, guías, tareas, folletos, facturas y `classify_document_heuristics`.

- [ ] **Step 2: Extraer `rate_limiter.py`**
  Mover `InMemoryRateLimiter`, `api_rate_limiter`, `eval_rate_limiter`, `check_rate_limit`, `check_eval_rate_limit`.

- [ ] **Step 3: Extraer `injection.py`**
  Mover `INJECTION_PATTERNS`, `InjectionCheckResult`, `detect_prompt_injection`.

- [ ] **Step 4: Extraer `auth.py`**
  Mover `MIN_CV_LENGTH`, `MAX_CV_LENGTH`, `validate_cv_text`, `verify_api_auth`.

- [ ] **Step 5: Configurar `api/security/__init__.py` y facade `api/security.py`**
  Reexportar todas las constantes, clases y funciones para que ninguna llamada externa cambie.

- [ ] **Step 6: Verificar con tests y conteo de líneas**
  Ejecutar `pytest tests/test_security.py tests/test_document_validation.py`.
  Verificar que ningún archivo supere 300 líneas.

- [ ] **Step 7: Commit con explicación**
  `git commit -m "refactor(security): separar responsabilidades de validacion, rate limit, inyeccion y auth en submodulos (<200 lineas)"`

---

### Task 3: Modularizar `api/eval_runner.py` (< 300 líneas)
**Files:**
- Create: `api/eval_criteria.py` (~120 lín)
- Create: `api/fairness.py` (~115 lín)
- Modify: `api/eval_runner.py` (reducido a ~130 lín)

- [ ] **Step 1: Extraer funciones de verificación de criterios a `api/eval_criteria.py`**
  Mover verificaciones de `max_recommendations`, `top_recommendation_must_include`, `must_reference_evidence`, `must_not_claim_missing_skills`, `must_not_invent_job_titles`, `must_not_invent_link`, `must_activate_profiling`.

- [ ] **Step 2: Extraer auditoría de equidad a `api/fairness.py`**
  Mover `FAIRNESS_PAIRS` y `run_fairness_audit`.

- [ ] **Step 3: Actualizar `api/eval_runner.py`**
  Mantener `cargar_eval_cases`, `evaluar_caso`, `run_all_evals` e importar `run_fairness_audit` para reexportarlo y no romper `api/main.py`.

- [ ] **Step 4: Verificar con tests y conteo de líneas**
  Ejecutar `pytest tests/test_eval_runner_logic.py`.
  Verificar que `api/eval_runner.py`, `api/fairness.py` y `api/eval_criteria.py` tengan < 300 líneas.

- [ ] **Step 5: Commit con explicación**
  `git commit -m "refactor(evals): separar evaluacion de criterios y auditoria de equidad de eval_runner (<150 lineas)"`

---

### Task 4: Modularizar `agent.py` (< 300 líneas)
**Files:**
- Create: `agent_modules/helpers.py` (~60 lín)
- Create: `agent_modules/prompts.py` (~160 lín)
- Create: `agent_modules/recruiter.py` (~60 lín)
- Create: `agent_modules/pathways.py` (~75 lín)
- Modify: `agent.py` (reducido a ~200 lín)

- [ ] **Step 1: Extraer utilidades y excepciones a `agent_modules/helpers.py`**
  Mover `AgentError`, `parse_match_score`, `cargar_vacantes`.

- [ ] **Step 2: Extraer prompts a `agent_modules/prompts.py`**
  Mover templates de prompts para extracción, búsqueda semántica, ranking y perfilamiento.

- [ ] **Step 3: Extraer simulador de brechas y recruiter matching**
  Mover `simulate_gap_closure` a `agent_modules/pathways.py` y `recruiter_matching` a `agent_modules/recruiter.py`.

- [ ] **Step 4: Refactorizar `agent.py` como orquestador limpio**
  Mantener la clase `TalentMatchMultiAgent` delegando en los módulos especializados.

- [ ] **Step 5: Verificar con suite de pruebas completa y conteo de líneas**
  Ejecutar `pytest`.
  Verificar que `agent.py` y todos los archivos en `agent_modules/` tengan < 300 líneas.

- [ ] **Step 6: Commit con explicación**
  `git commit -m "refactor(agent): descomponer prompts, helpers y features de reclutador/brechas en agent_modules (<200 lineas)"`

---

### Task 5: Modularizar `api/main.py` con FastAPI Routers (< 300 líneas)
**Files:**
- Create: `api/routers/vacantes.py` (~50 lín)
- Create: `api/routers/matching.py` (~90 lín)
- Create: `api/routers/pathway.py` (~60 lín)
- Create: `api/routers/recruiter.py` (~50 lín)
- Create: `api/routers/audit.py` (~75 lín)
- Modify: `api/main.py` (reducido a ~70 lín)

- [ ] **Step 1: Crear router de vacantes (`api/routers/vacantes.py`)**
  Mover `/vacantes`, `/vacantes/{id}`, POST `/vacantes`.

- [ ] **Step 2: Crear router de matching (`api/routers/matching.py`)**
  Mover endpoints `/match` y `/match/pdf`.

- [ ] **Step 3: Crear router de simulación y recursos (`api/routers/pathway.py`)**
  Mover `/simular-brechas` y `/recursos-brechas`.

- [ ] **Step 4: Crear router de recruiter (`api/routers/recruiter.py`)**
  Mover `/recruiter/match`.

- [ ] **Step 5: Crear router de auditoría y evals (`api/routers/audit.py`)**
  Mover `/trust/metrics`, `/fairness/audit`, `/evals/run`.

- [ ] **Step 6: Simplificar `api/main.py`**
  Inicializar `app = FastAPI()`, configurar CORS, incluir los routers con `app.include_router(...)`, endpoint `/health`, y montaje estático del frontend.

- [ ] **Step 7: Verificar con suite de pruebas completa y conteo de líneas**
  Ejecutar `pytest`.
  Verificar que `api/main.py` tenga < 100 líneas.

- [ ] **Step 8: Commit con explicación**
  `git commit -m "refactor(api): estructurar endpoints con APIRouter en submodulos tematicos (<100 lineas)"`

---

### Task 6: Modularizar `frontend/app.js` (< 300 líneas)
**Files:**
- Create: `frontend/js/config.js` (~80 lín)
- Create: `frontend/js/matching.js` (~220 lín)
- Create: `frontend/js/pathways.js` (~150 lín)
- Create: `frontend/js/recruiter.js` (~150 lín)
- Create: `frontend/js/trust_center.js` (~130 lín)
- Create: `frontend/js/evals.js` (~150 lín)
- Create: `frontend/js/vacantes.js` (~80 lín)
- Modify: `frontend/app.js` (reducido a ~80 lín)
- Modify: `frontend/index.html` (incluir scripts en orden)

- [ ] **Step 1: Crear `frontend/js/config.js`**
  Contiene constantes, estado compartido, referencias DOM principales y candidatos de muestra.

- [ ] **Step 2: Crear módulos específicos por dominio**
  - `matching.js`: gestión de subida de archivos, llamada a `/match` / `/match/pdf`, renderizado de recomendaciones y tarjeta de perfilamiento.
  - `pathways.js`: interacción con modal de Camino a la Vacante y llamada a `/simular-brechas`.
  - `recruiter.js`: carga de candidatos y ejecución de `/recruiter/match`.
  - `trust_center.js`: actualización de métricas de confianza y auditoría de equidad.
  - `evals.js`: ejecución de evals en interfaz y detalle modal.
  - `vacantes.js`: renderizado y filtrado de vacantes de la BD.

- [ ] **Step 3: Dejar `frontend/app.js` como inicializador de eventos**
  Solo vincula listeners de navegación, tabs y arranque de la interfaz.

- [ ] **Step 4: Actualizar `frontend/index.html`**
  Cargar los archivos de `frontend/js/` antes de `app.js`.

- [ ] **Step 5: Verificar conteo de líneas de todos los archivos JS**
  Verificar que ninguno supere 250 líneas.

- [ ] **Step 6: Commit con explicación**
  `git commit -m "refactor(frontend): dividir app.js de 1048 lineas en modulos especializados (<250 lineas)"`

---

### Task 7: Actualizar `MAKERS_ACCEPTANCE.md` y Documentación de Cierre
**Files:**
- Modify: `MAKERS_ACCEPTANCE.md`

- [ ] **Step 1: Actualizar la tabla de Gates en `MAKERS_ACCEPTANCE.md`**
  - Cambiar el gate `Jailbreak y safety` a `PASS`, con evidencia del reporte de adversariales contra Groq.
  - Cambiar el gate `Mantenibilidad` a `PASS`, documentando que todos los archivos están por debajo de 300 líneas divididos por responsabilidad única.

- [ ] **Step 2: Ejecutar verificación final completa (`pytest`)**
  Asegurar que los 82+ tests pasen al 100%.

- [ ] **Step 3: Commit con explicación y push**
  `git commit -m "docs: actualizar MAKERS_ACCEPTANCE a PASS en Jailbreak y Mantenibilidad con evidencia verificable"`
  `git push origin dev/dylan`
