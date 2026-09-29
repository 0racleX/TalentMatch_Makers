# Ground truth — baseline (keywords)

- Fecha: 2026-09-29_0911
- Dataset: 13 vacantes reales (Tablero publico de Greenhouse de Sezzle (API: https://boards-api.greenhouse.io/v1/boards/sezzle/jobs), consultadas 2026-09-29)
- Casos: 12 | Corridas: 1 | Umbral de match: 40%
- Errores de ejecucion: 0

| Metrica | Media | Desv. | Min | Max |
|---|---|---|---|---|
| rank@1 | 100.0% | 0.0% | 100.0% | 100.0% |
| hit@1 | 10.0% | 0.0% | 10.0% | 10.0% |
| hit@3 | 10.0% | 0.0% | 10.0% | 10.0% |
| aceptable@1 | 100.0% | 0.0% | 100.0% | 100.0% |
| rechazo_correcto | 100.0% | 0.0% | 100.0% | 100.0% |
| falsos_positivos | 0.0% | 0.0% | 0.0% | 0.0% |
| grounding | 100.0% | 0.0% | 100.0% | 100.0% |

- Estabilidad del top-1 entre corridas: **100.0%**
- Rango promedio del score top-1: **0 puntos**
- ¿Metrica estable? (estabilidad_top1 >= 90% y desv. hit@1 <= 5%): **SI**

## Detalle por caso

| Caso | Esperado | Top-1 por corrida | Score top-1 | Estable |
|---|---|---|---|---|
| gt_c01_seguridad_estudiante | gt04 | gt04 | 39 | si |
| gt_c02_analitica_datos | gt09, gt07 | gt09 | 20 | si |
| gt_c03_frontend_mobile | gt05 | gt05 | 39 | si |
| gt_c04_fullstack_junior | gt01 | gt01 | 14 | si |
| gt_c05_ingenieria_datos | gt03 | gt03 | 15 | si |
| gt_c06_diseno_ux | gt06 | gt06 | 20 | si |
| gt_c07_ia_ml | gt07 | gt07 | 15 | si |
| gt_c08_contador | gt12 | gt12 | 24 | si |
| gt_c09_soporte_ti | gt08 | gt08 | 21 | si |
| gt_c10_enfermera_sin_match | sin match | None | 0 | si |
| gt_c11_senior_backend | gt11 | gt11 | 43 | si |
| gt_c12_inyeccion_senior | sin match | gt10 | 23 | si |

`None` en el top-1 = el sistema no recomendo nada o recomendo algo que no existe en el dataset.
