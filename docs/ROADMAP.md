# Roadmap — TalentMatch AI

Este documento tiene dos partes:

- **Parte A** — cerrar lo que falta de lo ya declarado (arquitectura, evals, confiabilidad, seguridad y producción). Backlog técnico.
- **Parte B** — diferenciadores estratégicos radicales frente a Magneto y LinkedIn: transparencia radical, evidencias auditables, camino a la vacante con simulador y modo recruiter sin sesgos.

---

## Parte A — Roadmap técnico (Ejecutado a Cabalidad)

### Fase 0 — Confiabilidad del pipeline

| Ítem | Por qué | Esfuerzo | Estado |
|---|---|---|---|
| Excepciones silenciosas en `agent.py` | Fallas de API se disfrazaban de "no match" | S | ✅ Hecho (2026-09-19) — `AgentError` dedicado |
| Retry con backoff exponencial en Groq | Rate-limits puntuales (429) o microcortes tumbaban corridas | S | ✅ Hecho (2026-09-19) — `api/retry.py` con backoff y jitter aleatorio |
| Logging estructurado (JSON) | Correlacionar fallas y eventos en producción | S | ✅ Hecho (2026-09-19) — `api/logging_config.py` con `JSONFormatter` |
| Tests unitarios deterministas | Probar sin gastar cuota ni depender de red/LLM | M | ✅ Hecho (2026-09-19) — 18 tests en `tests/` ejecutados en 1s (`python -m unittest discover tests -v`) |
| Cache de resultados de evals | Evita re-pagar llamadas repetidas a Groq; baselines estables | S | ✅ Hecho (2026-09-19) — `api/cache.py` determinista por hash SHA-256 |

### Fase 1 — Seguridad y hardening de API

| Ítem | Por qué | Esfuerzo | Estado |
|---|---|---|---|
| Auth en la API (API Key / Bearer) | Prevenir abuso de cuota de Groq | S | ✅ Hecho (2026-09-19) — Header `X-API-Key` y Bearer token configurable vía `TALENTMATCH_API_KEY` |
| Rate limiting a nivel API | Prevenir DoS y agotamiento de budget | S | ✅ Hecho (2026-09-19) — `InMemoryRateLimiter` sliding window en `api/security.py` |
| CORS restringido y configurable | Seguridad de orígenes en producción | XS | ✅ Hecho (2026-09-19) — Configurable vía `ALLOWED_ORIGINS` |
| Límite de tamaño server-side en `/match` | Validación estricta min 10 / max 15,000 caracteres | XS | ✅ Hecho (2026-09-19) — `validate_cv_text()` en `api/security.py` |
| Capa explícita de detección de prompt injection | Defensa en profundidad antes de tocar el LLM | M | ✅ Hecho (2026-09-19) — `detect_prompt_injection()` con regex heurístico y flag auditada |

### Fase 2 — Datos reales y persistencia

| Ítem | Por qué | Esfuerzo | Estado |
|---|---|---|---|
| Migrar vacantes a base de datos | Salir del archivo estático y permitir mutabilidad | M | ✅ Hecho (2026-09-19) — SQLite/PostgreSQL vía SQLAlchemy en `db/` |
| Diseñar schema relacional | Vacantes, empresas, recursos y auditorías | M | ✅ Hecho (2026-09-19) — Modelos ORM en `db/models.py` |
| Ingesta y catálogo curado de formación | Conectar brechas con cursos y becas reales | L | ✅ Hecho (2026-09-19) — Sembrado automático en `db/seed.py` (CodeRise, Docker, Fast.ai, React, etc.) |
| Endpoints dinámicos de vacantes | Crear y consultar vacantes sin redeploy | S | ✅ Hecho (2026-09-19) — `POST /vacantes`, `GET /vacantes/{id}` |

### Fase 3 — Infraestructura declarada

| Ítem | Declarado como | Esfuerzo | Estado |
|---|---|---|---|
| Dockerfile optimizado | Contenedor de producción con usuario no-root | S | ✅ Hecho (2026-09-19) — Multi-stage con Python 3.13-slim y healthcheck |
| docker-compose (API + Frontend Nginx) | Orquestación completa de servicios | S | ✅ Hecho (2026-09-19) — `docker-compose.yml` + `nginx.conf` |
| CI (GitHub Actions) | Pruebas deterministas continuas | S | ✅ Hecho (2026-09-19) — `.github/workflows/ci.yml` |
| Múltiples workers de concurrencia | Concurrencia de producción declarada | S | ✅ Hecho (2026-09-19) — Uvicorn multi-worker (`--workers 2`) |
| Endpoint de métricas para observabilidad | Monitoreo y métricas de confianza | M | ✅ Hecho (2026-09-19) — `GET /metrics` |

### Fase 4 — Housekeeping

| Ítem | Por qué | Esfuerzo | Estado |
|---|---|---|---|
| Archivar notebook legacy | Ya no representa el sistema multiagente actual | XS | ✅ Hecho (2026-09-19) — Movido a `archive/` con documentación explicativa |
| Llenar `TEAM_ROTATION.md` | Roles asignados y checklist activo | XS | ✅ Hecho (2026-09-19) — Roles de Dylan Mejía y Manuela Echeverrí formalizados |

---

## Parte B — Diferenciación estratégica vs. Magneto y LinkedIn

### El diagnóstico

Ni Magneto ni LinkedIn tienen un problema de *cobertura* (tienen millones de usuarios). Tienen un problema de **confianza, silencio y conflicto de incentivos**:
1. **El Candidato**: Manda su CV a una caja negra algorítmica. O recibe ghosting absoluto o un rechazo estandarizado que no le dice qué habilidad le faltó ni cómo conseguirla.
2. **El Algoritmo**: LinkedIn optimiza para engagement ("Easy Apply" masivo, vanity metrics de scroll). Esto produce una avalancha de 800 CVs por vacante donde los recruiters terminan usando filtros ciegos por palabras clave o universidades de prestigio, descartando talento autodidacta o en transición.
3. **Falta de Transparencia Salarial**: En ambas plataformas, la mayoría de ofertas ocultan el rango de compensación ("A convenir"), generando pérdida de tiempo y desigualdad.

TalentMatch AI se posiciona en el polo opuesto: **cada recomendación está anclada en evidencia auditable, no hay alucinaciones, el salario es 100% visible, y cuando hay brechas, te damos la ruta formativa con simulación de crecimiento**.

### Apuestas implementadas y diferenciales

| # | Feature Diferenciador | Qué debilidad de LinkedIn/Magneto destruye | Implementación en TalentMatch | Impacto |
|---|---|---|---|---|
| 1 | **Camino a la vacante + Simulador de Brechas** | En LinkedIn el rechazo es un callejón sin salida; te descartan y te dejan en silencio. | Cada brecha se vincula a un recurso concreto (CodeRise, freeCodeCamp, docs). El usuario presiona *"Simular impacto"* y ve en tiempo real cómo su score sube (ej: de 55% a 82%) al adquirir la habilidad. | **Masivo** |
| 2 | **Modo Recruiter Inverso y sin Sesgos** | En los portales tradicionales el recruiter filtra por nombres, fotos, universidades o keywords tontas. | Endpoint `POST /recruiter/match` e interfaz B2B dedicada: evalúa un pool de candidatos frente a una vacante con perfil anonimizado, evaluando puramente evidencia técnica y brechas. | **Alto (B2B)** |
| 3 | **Trust Center Público & Tasa 0% de Alucinación** | Los ATS tradicionales esconden sus criterios. Nadie publica sus tasas de fallo. | Sección pública del Trust Center con métricas de salud en vivo, 0% links falsos garantizados por arquitectura y ejecución de 12 evals auditables. | **Alto** |
| 4 | **Auditoría de Sesgo en Vivo (Fairness)** | El screening con IA genera desconfianza y sesgos de género/origen. | Endpoint `GET /fairness/audit` que evalúa pares idénticos variando nombres, género o procedencia, demostrando paridad matemática (diferencia <= 5%). | **Alto** |
| 5 | **Transparencia Salarial Radical** | En LinkedIn/Magneto el 70% de avisos ocultan el sueldo ("A convenir"). | Política de plataforma: 100% de vacantes con rango salarial visible en base de datos y tarjetas destacadas con badge verde. | **Medio-Alto** |
| 6 | **Unificación de Oportunidades como "Próximo Paso"** | Cursos, eventos, pasantías y empleos se tratan como silos comerciales separados. | La BD y el pipeline unifican empleo, pasantía, hackathon y beca como aceleradores secuenciales de carrera en un solo flujo. | **Medio** |
