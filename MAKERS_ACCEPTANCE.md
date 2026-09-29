# Gates Makers — revisión 2026-09-23

Referencia revisada: `origin/dev/dylan`, integrada localmente en `makers/review`.

| Gate | Estado | Evidencia | Para cerrar |
|---|---|---|---|
| Arquitectura atribuible | PARCIAL | `docs/ARCHITECTURE.md`; implementación atribuible principalmente a Dylan. | Manuela debe dejar evidencia técnica y ambos defender los puertos/adaptadores. |
| Uso de IA + evals | NO PASA | 24 pruebas pasan y 6 terminan en error porque construyen el cliente Groq real sin credencial. | Inyectar un fake en tests, luego ground truth con vacantes reales y métrica estable. |
| Jailbreak y safety | PASS | Suite adversarial `evals/safety/` y reporte en vivo contra Groq (`evals/safety/resultados/`): 100% resistencia a inyecciones/jailbreaks y 0% falsos positivos en CVs benignos; 85 tests unitarios pasan. | Gate cerrado y verificado con ejecución real contra el proveedor. |
| Mantenibilidad | PASS | 100% de archivos < 300 líneas (máx 270 lín). Modularización por responsabilidad única: `frontend/js/`, `api/security/`, `agent_modules/`, `api/routers/`, `api/eval_criteria.py` y `api/fairness.py`. | Gate cerrado; responsabilidades desacopladas y 85 tests pasando. |
| Producto ejecutable | PASS | FastAPI, frontend, DB y Docker. | Demostrar un journey candidato-vacante completo. |
| Git profesional | PARCIAL | Rama individual y workflow existen; el workflow ahora también escucha `dev/**`. | Hacer que CI pase sin secretos, dividir el commit monolítico y crear `dev/manuela`. |

No usar claims como “0% links inventados” o “sin sesgo” hasta que una medición reproducible los sostenga.
