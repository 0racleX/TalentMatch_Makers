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

<!-- MAKERS_REVIEW_2026_08_27_START -->
## Revision docente - 2026-08-27

### Lo que vimos

- Dylan corrio evals y encontro un avance inicial: 4/5, con falla clara en vacantes vacias.
- Manuela hizo un avance muy fuerte: automatizo validadores, corrigio el prompt que ordenaba inventar URL y agrego control negativo 0/5.
- El hallazgo mas importante: un score 5/5 puede ser falso si el eval no mide lo que importa.
- El riesgo principal del producto es inventar vacantes, links o habilidades que el candidato no tiene.
- Ahora el equipo debe integrar criterio: no duplicar esfuerzos, sino unificar la mejor version.

### Reto de hoy

Conviertan TalentMatch en un sistema que no inventa:

1. Agregar un caso acante_sin_link.
2. Ajustar el expected para que mpty_jobs exija explicacion util, no solo lista vacia.
3. Dejar en README.md: Current score, Known failures y Next hypothesis.

### Tarea obligatoria: diagrama de arquitectura

Crear docs/arquitectura.md con un diagrama Mermaid que muestre:

`mermaid
flowchart LR
  CV --> PromptMatching
  Vacantes --> PromptMatching
  PromptMatching --> Modelo
  Modelo --> ValidadorGrounding
  ValidadorGrounding --> Recomendaciones
  ValidadorGrounding --> SinMatchExplicado
  Evals --> ValidadorGrounding
`

Debe quedar claro de donde salen las vacantes, como se evita inventar links y como se valida que el match este anclado en el input.

### Criterio de aceptacion

No cuenta decir que el modelo "entiende semanticamente". Cuenta demostrar que no inventa vacantes ni habilidades.
<!-- MAKERS_REVIEW_2026_08_27_END -->


<!-- MAKERS_CODE_ARCH_REVIEW_2026_09_01_START -->
## Revision de codigo y arquitectura - 2026-09-01

### Lectura docente

- Manuela hizo un avance fuerte: validadores, tests, control negativo y deteccion de evals debiles.
- Dylan hizo ajustes de README, pero falta un aporte tecnico mas conectado a la falla central del sistema.
- No se detecto docs/arquitectura.md.
- El riesgo principal sigue siendo inventar vacantes, links o habilidades del candidato.

### Revision de principios

- Bien: ya aparece el concepto correcto de grounding.
- Muy bien: detectar que un 5/5 puede mentir si el eval no mide lo importante.
- Falta: integrar el trabajo de ramas en una version de equipo y dejar arquitectura clara.

### Pendiente de equipo

Crear docs/arquitectura.md y consolidar en README que parte valida existencia de vacantes, links y habilidades.

### Pendiente por poca evidencia individual

Dylan debe dejar un commit tecnico: caso acante_sin_link, mejora de validador, o correccion del comportamiento cuando no hay vacantes.
<!-- MAKERS_CODE_ARCH_REVIEW_2026_09_01_END -->

