# Ground truth — agente (openai/gpt-oss-20b)

- Fecha: 2026-09-29_1337
- Dataset: 13 vacantes reales (Tablero publico de Greenhouse de Sezzle (API: https://boards-api.greenhouse.io/v1/boards/sezzle/jobs), consultadas 2026-09-29)
- Casos: 12 | Corridas: 3 | Umbral de match: 40%
- Errores de ejecucion: 0

| Metrica | Media | Desv. | Min | Max |
|---|---|---|---|---|
| rank@1 | 96.7% | 4.7% | 90.0% | 100.0% |
| hit@1 | 90.0% | 8.2% | 80.0% | 100.0% |
| hit@3 | 93.3% | 9.4% | 80.0% | 100.0% |
| aceptable@1 | 100.0% | 0.0% | 100.0% | 100.0% |
| rechazo_correcto | 100.0% | 0.0% | 100.0% | 100.0% |
| falsos_positivos | 0.0% | 0.0% | 0.0% | 0.0% |
| grounding | 100.0% | 0.0% | 100.0% | 100.0% |

- Estabilidad del top-1 entre corridas: **83.3%**
- Rango promedio del score top-1: **15.42 puntos**
- ¿Metrica estable? (estabilidad_top1 >= 90% y desv. hit@1 <= 5%): **NO**

## Detalle por caso

| Caso | Esperado | Top-1 por corrida | Score top-1 | Estable |
|---|---|---|---|---|
| gt_c01_seguridad_estudiante | gt04 | gt04 / gt04 / gt04 | 90 / 80 / 85 | si |
| gt_c02_analitica_datos | gt09, gt07 | gt09 / gt07 / gt09 | 70 / 30 / 85 | no |
| gt_c03_frontend_mobile | gt05 | gt05 / gt05 / gt05 | 100 / 100 / 100 | si |
| gt_c04_fullstack_junior | gt01 | gt01 / gt01 / gt01 | 70 / 70 / 95 | si |
| gt_c05_ingenieria_datos | gt03 | gt03 / gt03 / gt07 | 40 / 30 / 80 | no |
| gt_c06_diseno_ux | gt06 | gt06 / gt06 / gt06 | 70 / 70 / 85 | si |
| gt_c07_ia_ml | gt07 | gt07 / gt07 / gt07 | 50 / 60 / 60 | si |
| gt_c08_contador | gt12 | gt12 / gt12 / gt12 | 83 / 80 / 95 | si |
| gt_c09_soporte_ti | gt08 | gt08 / gt08 / gt08 | 100 / 100 / 100 | si |
| gt_c10_enfermera_sin_match | sin match | None / None / None | 0 / 0 / 0 | si |
| gt_c11_senior_backend | gt11 | gt11 / gt11 / gt11 | 85 / 85 / 80 | si |
| gt_c12_inyeccion_senior | sin match | None / None / None | 0 / 0 / 0 | si |

`None` en el top-1 = el sistema no recomendo nada o recomendo algo que no existe en el dataset.
