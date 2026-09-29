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
| Agente `openai/gpt-oss-20b` | 3 | 96.7 % | 90.0 % ± 8.2 % | 100 % | 0 % | 100 % | 83.3 % |

Detalle del baseline: `resultados/2026-09-29_0911_baseline_keywords.md`.
Detalle del agente: `resultados/2026-09-29_1337_agente_openai-gpt-oss-20b.md`.

### Lectura del resultado (corrida real, 3 corridas)

- **El LLM gana en calibración, no en orden.** `hit@1` sube de 10 % (baseline) a 90 %: el agente pone la vacante correcta de primera *y* con un score que supera el umbral. En `rank@1` el baseline (100 %) no pierde contra el agente (96.7 %): en este dataset ordenar por palabras clave ya funciona.
- **Lo que sí se sostiene en las 3 corridas:** grounding 100 % (nada inventado), 0 % falsos positivos, y los dos casos sin match (enfermera e inyección) terminaron sin recomendaciones.
- **La métrica NO es estable** según el criterio definido: estabilidad del top-1 83.3 % (< 90 %) y desviación de `hit@1` 8.2 % (> 5 %). El score top-1 varía en promedio 15 puntos entre corridas.
- **De dónde sale la inestabilidad:** 2 de 12 casos.
  - `gt_c02_analitica_datos`: en la corrida 2 el top-1 bajó a 30 % y el sistema pasó a perfilamiento; en las corridas 1 y 3 dio 70 % y 85 %.
  - `gt_c05_ingenieria_datos`: 40 % / 30 % / 80 %, y en la corrida 3 el top-1 cambió a gt07 (aceptable, no relevante). En la corrida 1 quedó justo en el umbral.
  - En la corrida 2 esos dos casos tardaron ~30 s contra ~4-7 s de las otras, lo que sugiere reintentos por rate limit y posible cambio al modelo de respaldo (`FALLBACK_MODELS`). La corrida no registra qué modelo respondió, así que esto es una hipótesis, no un hallazgo.

## Known failures / límites conocidos

- **El dataset es fácil para ordenar:** el baseline por palabras clave acierta el orden en 10/10 casos. Por eso `rank@1` no separa todavía al LLM del baseline; la diferencia hay que buscarla en `hit@1` (calibración del score), `rechazo_correcto` y el caso de inyección.
- **Una sola empresa (Sezzle):** las 13 vacantes vienen del mismo tablero. Sirve como primer ground truth real, pero no mide sesgos entre empresas.
- **Las publicaciones se cierran:** el dataset queda congelado con `fecha_consulta` y `greenhouse_id`; los links pueden dejar de funcionar.
- **Etiquetas de una persona:** las etiquetas las hizo una sola persona; falta que otra persona (Dylan o el tutor) etiquete sin ver las etiquetas y medir el acuerdo entre ambas.

## Next hypothesis

1. Agregar casos donde el CV y la vacante no comparten palabras (sinónimos en español vs requisitos en inglés). Ahí es donde el baseline debería fallar y el LLM demostrar su ventaja semántica.
2. **Inestabilidad (medida: 83.3 % < 90 %).** Cambiar una sola cosa y volver a correr 3 veces: registrar qué modelo respondió cada llamada y desactivar el fallback de modelos durante los evals. Si la estabilidad sube a ≥ 90 %, la causa era el cambio de modelo; si no, probar después una rúbrica de score más explícita en el prompt de ranking.
3. Los casos que quedan cerca del umbral (40 %) son los que más cambian de resultado; vale la pena reportar cuántos casos quedan a menos de 10 puntos del umbral.
