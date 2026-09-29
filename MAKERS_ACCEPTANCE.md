# Gates Makers — revisión 2026-09-23

Referencia revisada: `origin/dev/dylan`, integrada localmente en `makers/review`.

| Gate | Estado | Evidencia | Para cerrar |
|---|---|---|---|
| Arquitectura atribuible | PARCIAL | `docs/ARCHITECTURE.md`; implementación atribuible principalmente a Dylan. | Manuela debe dejar evidencia técnica y ambos defender los puertos/adaptadores. |
| Uso de IA + evals | NO PASA | 24 pruebas pasan y 6 terminan en error porque construyen el cliente Groq real sin credencial. | Inyectar un fake en tests, luego ground truth con vacantes reales y métrica estable. |
| Jailbreak y safety | PARCIAL | `tests/test_security.py` y filtros de input/output. | Ejecutar adversariales contra el proveedor real y guardar resultados. |
| Mantenibilidad | NO PASA | `frontend/app.js` tiene 1.048 líneas; `agent.py`, `api/main.py`, `api/security.py` y `api/eval_runner.py` superan 300. | Separar por responsabilidad antes de sumar features. |
| Producto ejecutable | PASS | FastAPI, frontend, DB y Docker. | Demostrar un journey candidato-vacante completo. |
| Git profesional | PARCIAL | Rama individual y workflow existen; el workflow ahora también escucha `dev/**`. | Hacer que CI pase sin secretos, dividir el commit monolítico y crear `dev/manuela`. |

No usar claims como “0% links inventados” o “sin sesgo” hasta que una medición reproducible los sostenga.
