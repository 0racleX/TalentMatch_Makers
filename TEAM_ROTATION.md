# Team Rotation — TalentMatch AI

Objetivo: que todos entiendan todo el sistema, no que cada persona quede encerrada en una parte.
Equipo: **Dylan Mejía** & **Manuela Echeverrí**

## Rotación de Roles

| Rol temporal | Responsable | Qué lidera | Quién debe poder explicarlo |
|---|---|---|---|
| **Build Owner** | Dylan Mejía | Pipeline multiagente (`agent.py`), API FastAPI (`api/main.py`), capa de persistencia y simulador de brechas | Manuela Echeverrí |
| **Evaluate Owner** | Manuela Echeverrí | Suite de evals (`api/eval_runner.py`), auditoría de sesgo/fairness, baseline en `results.md` y tests unitarios | Dylan Mejía |
| **Explain & Product Owner** | Dylan Mejía & Manuela Echeverrí | Diferenciación vs LinkedIn/Magneto, Trust Center, documentación, README y demo técnica | Ambos |

## Reglas de Operación

- El owner lidera la implementación, pero no trabaja aislado.
- Cada cambio debe ser revisado y poder ser explicado en detalle por la otra persona del equipo.
- Cada integrante debe tener contribuciones y commits visibles en el repositorio.
- No se cambia todo a la vez: una hipótesis clara, una implementación resiliente, una medición contrastada con evals y tests unitarios.

## Checklist Semanal

- [x] Todos entienden el flujo del pipeline de 5 agentes y su orquestación.
- [x] Todos entienden la suite de evals, el cache y los criterios de evaluación.
- [x] Se cuenta con tests unitarios deterministas (`python -m unittest discover tests -v`) sin costo de API (25 pruebas).
- [x] El simulador interactivo de Camino a la Vacante y el Modo Recruiter están integrados.
- [x] Sistema de Validación de Autenticidad de Documentos (previene que guías de laboratorio o tareas académicas sean procesadas como perfiles de candidatos).
- [x] Todos saben cómo funciona la auditoría de sesgo y la tasa de alucinación cero.
- [x] Cada integrante dejó evidencia verificable en el código.

## Preguntas Clave para el Equipo

1. **¿Qué cambió esta semana?**
   - Se completó el backlog de confiabilidad (retry con backoff exponencial, logging estructurado en JSON, suite de tests unitarios deterministas con 25 pruebas, cache determinista de evals).
   - Se aplicó hardening de API (límite server-side de longitud de CV, detector heurístico de prompt injection, rate limiting por IP, CORS configurable, auth por API Key).
   - Se integró el clasificador de autenticidad documental de dos niveles (heurístico de latencia cero + semántico LLM) que rechaza guías de laboratorio, tareas escolares, manuales o facturas con `modo: "documento_invalido"`, impidiendo recomendaciones ficticias.
   - Se migró a persistencia con base de datos (SQLite/PostgreSQL vía SQLAlchemy) con siembra automática de vacantes y catálogo curado de formación.
   - Se implementaron los diferenciadores estratégicos contra LinkedIn y Magneto: **Camino a la Vacante con Simulador Interactivo de Brechas**, **Modo Recruiter B2B sin sesgos**, **Trust Center público con auditoría de equidad** y **Transparencia salarial obligatoria**.
   - Se añadió contenedorización Docker + docker-compose y CI con GitHub Actions.

2. **¿Por qué ese cambio importa?**
   - Elimina la variabilidad y fragilidad técnica, protegiendo el budget de Groq contra rate-limits e inyecciones.
   - Protege la integridad del sistema: ya no procesa ciegamente PDFs como si todo fuera un candidato (ej. una práctica de laboratorio de redes o una tarea de Kubernetes).
   - Transforma el producto de un simple "analizador de CV" a una plataforma que ataca el dolor #1 de los candidatos (el silencio y el rechazo sin ruta de crecimiento) y de las empresas (candidatos evaluados con evidencia auditable en vez de sesgos de keyword/nombre).

3. **¿Cómo sabemos si mejoró?**
   - 25 tests unitarios deterministas pasando en < 2.5 segundos.
   - Validación heurística que rechaza guías y tareas en < 5ms sin consumir cuota de tokens.
   - Suite de evals con baselines estables gracias al cache y reintentos.
   - Auditoría de sesgo matemática demostrando paridad en el Trust Center.

4. **¿Qué caso sigue requiriendo atención?**
   - Ampliar la conexión de ingesta hacia APIs externas de agregadores de empleo en tiempo real.

5. **¿Qué haremos después?**
   - Extender el parseo automático de repositorios de GitHub para verificar commits y lenguajes reales en perfiles técnicos avanzados.
