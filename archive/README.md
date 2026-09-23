# Archivo Histórico — Prototipo Inicial (Google Colab)

Este directorio conserva artefactos del prototipo conceptual inicial del proyecto.

- `TalentMatch_Use_Case_Groq (1).ipynb`: Prototipo de un solo agente sobre `llama-3.3-70b-versatile`, diseñado originalmente para Google Colab con el baseline histórico de 5 evals.

### Sistema de Producción Actual

El sistema actual ha evolucionado a una arquitectura multiagente de grado de producción:
- Pipeline orquestado de 5 agentes especializados (`agent.py`)
- Modelo de inferencia sobre Groq con retry exponencial con jitter
- Backend FastAPI con rate limiting, persistencia SQLAlchemy y endpoints B2B
- Frontend interactivo con **Camino a la Vacante**, **Modo Recruiter** y **Trust Center**
- Suite ampliada de 12 evals, auditoría de sesgo y tests deterministas (`tests/`)

No modifiques este notebook para desarrollo activo; consulta [`agent.py`](../agent.py) y [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md).
