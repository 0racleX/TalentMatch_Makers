# Makers Review

## Que encontramos

- El proyecto compara CV contra vacantes usando Groq y devuelve recomendaciones estructuradas.
- El notebook ya usa Pydantic para validar la forma del output.
- La ventaja real del producto es matching semantico de habilidades, no busqueda por palabra clave.
- El riesgo principal es inventar habilidades, vacantes o links para justificar un match.
- Falta evidencia versionada de casos adversariales y casos de borde del dominio.

## Mejora aplicada

Agregue `evals/eval_cases.json` con 5 casos:

- match claro seguridad/Python;
- CV incompleto;
- vacantes vacias;
- prompt injection dentro del CV;
- equivalencias semanticas como NLP/procesamiento de lenguaje natural.

Tambien agregue `evals/results.md` para registrar baseline y siguientes cambios.

## Por que importa

Un output puede ser JSON valido y aun asi ser falso. En TalentMatch, la confiabilidad depende de que cada recomendacion este anclada en evidencia del CV y en una vacante real. El modelo recomienda; el sistema debe validar que no invente.

## Como probarlo

1. Ejecutar `agent.py` o el notebook con cada caso de `evals/eval_cases.json`.
2. Revisar si las recomendaciones cumplen `expected`.
3. Registrar pass/fail en `evals/results.md`.
4. Si falla, cambiar una sola cosa y comparar before/after.

## Tu reto

1. Core: completar baseline real para los 5 casos y reportar score `X/5`.
2. Intermediate: validar que `match_score` sea porcentaje entre 0 y 100 y que no haya mas de 2 recomendaciones.
3. Advanced: validar que `titulo_oportunidad` y `link` existan literalmente en las vacantes de entrada antes de mostrar la recomendacion.
