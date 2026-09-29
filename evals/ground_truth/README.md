# Ground truth con vacantes reales

Responde al gate **"Uso de IA + evals"** de la revisión Makers (2026-09-23):
*"Inyectar un fake en tests, luego ground truth con vacantes reales y métrica estable."*

Autora: Manuela Echeverri.

## Qué hay aquí

| Archivo | Qué es |
|---|---|
| `vacantes_reales.json` | 13 vacantes publicadas en Colombia (tablero público de Greenhouse de Sezzle, consultado 2026-09-29). Bullets originales, link y `greenhouse_id`. Incluye roles senior y no-tech como controles negativos. |
| `casos_etiquetados.json` | 12 CVs con etiquetas: `relevantes` (top-1 esperado), `aceptables` (top-3 razonable), `no_relevantes` (no deben salir como match) y una justificación por caso. |
| `metrics.py` | Métricas puras (sin modelo). |
| `baseline_keywords.py` | Baseline sin IA por palabras clave, para comparar. |
| `run_ground_truth.py` | Runner: N corridas, resultados en `resultados/`. |

Las vacantes del producto (`data/vacantes.json`) siguen siendo las de demo; el ground truth usa este dataset aparte a través de `JsonRepositoryAdapter`, así que no toca SQLite ni el Trust Center.

## Cómo correrlo

```bash
# Agente real (necesita GROQ_API_KEY en .env). 12 casos x 3 corridas.
python -m evals.ground_truth.run_ground_truth --runs 3

# Si Groq devuelve rate limit: más pausa, o menos corridas
python -m evals.ground_truth.run_ground_truth --runs 3 --pausa 6

# Baseline sin IA (sin key)
python -m evals.ground_truth.run_ground_truth --predictor baseline --runs 1
```

Cada corrida deja `resultados/<fecha>_<predictor>_<modelo>.md` (resumen) y `.json` (detalle con la razón del match de cada recomendación). Mientras corre, un `.parcial.json` guarda lo avanzado por si se corta.

## Métricas

| Métrica | Qué responde |
|---|---|
| `rank@1` | ¿La vacante correcta quedó de primera? (solo orden) |
| `hit@1` | ¿Quedó de primera **y** con score ≥ 40 %? Es lo que ve el candidato. |
| `hit@3` | ¿Hay una vacante correcta con score ≥ 40 % en el top-3? |
| `rechazo_correcto` | En CVs sin vacante adecuada, ¿el sistema evitó forzar un match? |
| `falsos_positivos` | % de casos donde una vacante `no_relevante` salió con score ≥ 40 % |
| `grounding` | % de casos donde todo lo recomendado existe literalmente (título + link) en el dataset |
| `estabilidad_top1` | % de casos con el mismo top-1 en todas las corridas |

**Métrica estable** = `estabilidad_top1 ≥ 90 %` y desviación de `hit@1 ≤ 5 %` entre corridas. Se mide en cada ejecución; no se asume.

## Resultados

| Predictor | Corridas | rank@1 | hit@1 | rechazo correcto | falsos positivos | grounding | estabilidad top-1 |
|---|---|---|---|---|---|---|---|
| Baseline palabras clave | 1 | 100 % | 10 % | 100 % | 0 % | 100 % | 100 % (determinista) |
| Agente `openai/gpt-oss-20b` | 3 | pendiente | pendiente | pendiente | pendiente | pendiente | pendiente |

Detalle del baseline: `resultados/2026-09-29_0911_baseline_keywords.md`.

## Known failures / límites conocidos

- **El dataset es fácil para ordenar:** el baseline por palabras clave acierta el orden en 10/10 casos. Por eso `rank@1` no separa todavía al LLM del baseline; la diferencia hay que buscarla en `hit@1` (calibración del score), `rechazo_correcto` y el caso de inyección.
- **Una sola empresa (Sezzle):** las 13 vacantes vienen del mismo tablero. Sirve como primer ground truth real, pero no mide sesgos entre empresas.
- **Las publicaciones se cierran:** el dataset queda congelado con `fecha_consulta` y `greenhouse_id`; los links pueden dejar de funcionar.
- **Etiquetas de una persona:** las etiquetas las hizo una sola persona; falta que otra persona (Dylan o el tutor) etiquete sin ver las etiquetas y medir el acuerdo entre ambas.

## Next hypothesis

1. Agregar casos donde el CV y la vacante no comparten palabras (sinónimos en español vs requisitos en inglés). Ahí es donde el baseline debería fallar y el LLM demostrar su ventaja semántica.
2. Si `estabilidad_top1 < 90 %`, cambiar una sola cosa (por ejemplo fijar `seed` o quitar el fallback de modelos durante los evals) y comparar antes/después.
