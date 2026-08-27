# Respuestas — Manuela Echeverri

Rama: `dev/Manuela`
Fecha: 2026-08-27

Todo lo que afirmo acá es reproducible corriendo:

```bash
python evals/test_validators.py                                        # 39/39
python evals/run_evals.py --replay                                     # 5/5
python evals/run_evals.py --replay --input evals/adversarial_outputs.json   # 0/5
```

---

## 1. ¿Qué cambió Makers?

Makers no tocó el agente. No cambió el prompt, ni el modelo, ni la lógica de
matching. Lo que agregó fue **la capacidad de saber si el agente funciona**:

- `evals/eval_cases.json` — 5 casos con un bloque `expected` verificable: happy path
  de seguridad/Python, CV incompleto, vacantes vacías, prompt injection, y
  equivalencias semánticas NLP/PLN.
- `evals/results.md` — plantilla para registrar baseline y comparar before/after.
- `MAKERS_REVIEW.md` — el diagnóstico y tres retos escalonados.
- `TEAM_ROTATION.md` — rotación de roles para que nadie quede encerrado en una parte.

El cambio de fondo es de criterio, no de código: pasar de *"el output se ve bien"*
a *"el output cumple un contrato que escribimos antes de mirarlo"*. Sin eso, cada
cambio en el prompt es una apuesta sin forma de saber si mejoró o empeoró algo.

---

## 2. ¿Qué riesgo técnico encontró?

Makers lo enunció así: **"Un output puede ser JSON válido y aun así ser falso."**

El notebook valida con Pydantic que existan los campos y que sean strings. Eso
verifica la **forma**, no el **contenido**. Nada impedía que el agente devolviera
una vacante que no existe, con un link que no existe, perfectamente formateada.

Cuando fui a buscar dónde podía materializarse ese riesgo, lo encontré escrito en
el código. `agent.py`, dentro del `system_prompt`, en `main` y en `dev/dylan`:

```python
"link": "URL falsa para el ejemplo"
```

**El prompt le está ordenando al modelo inventar una URL.** El riesgo #1 que
señaló Makers no era una posibilidad teórica del modelo: era una instrucción del
producto.

Vale la pena ser precisa sobre por qué no explotó en el baseline: en los 5 casos
las vacantes mock traen links visibles y el modelo prefirió copiarlos en vez de
inventar. **Pasamos por suerte, no por diseño.** El escenario donde esto revienta
es una vacante sin link, o con el link enterrado en un texto largo — y no
teníamos ese caso.

En un producto real el daño es concreto: un estudiante aplica a una vacante que no
existe. Pierde tiempo, y deja de confiar en la herramienta. Y como el score de
match viene con una justificación bien escrita, el error es difícil de detectar
justo para el usuario menos experimentado, que es nuestro usuario objetivo.

---

## 3. ¿Qué eval falla o falta?

### Lo que hice primero

Automaticé el baseline. Antes se evaluaba leyendo el output y anotando pass/fail a
mano; ahora `run_evals.py` + `validators.py` producen el mismo score cada vez.

**Baseline automático: 5/5.** La evaluación manual anterior daba 4/5.

### La diferencia es el hallazgo

`talentmatch_empty_jobs` se había marcado Fail porque el agente devuelve
`{"recomendaciones": []}` sin explicar nada. Ese juicio de producto es correcto: un
JSON vacío no le comunica nada a un usuario. Pero el `expected` dice:

```json
"must_return_no_matches_or_explain": true
```

Es un OR. Devolver cero recomendaciones ya lo cumple. El eval **no exige** la
explicación. El caso pasa contra el eval y falla contra el criterio de producto.

De ahí sale lo que me parece la conclusión importante de todo esto:

> **El score subió de 4/5 a 5/5 y el sistema no es ni un poco más confiable.**
> El eval no estaba midiendo lo que importaba.

### Evals decorativos

`run_evals.py` reporta automáticamente las aserciones que **ningún check
determinista puede verificar**. Son 3 de 11:

| Caso | Aserción | Por qué no se puede medir |
|---|---|---|
| happy_path | `must_not_include: ["React como habilidad del candidato"]` | Prosa, no un token buscable |
| prompt_injection | `must_not_claim_missing_skills: true` | Booleano sin lista de cuáles |
| equivalent_skill | `must_not_penalize_language_variation: true` | Sin definición operativa de "penalizar" |

Un eval que no se puede verificar pasa siempre. No protege de nada, pero sí infla
el score. Arreglar estos tres es más urgente que agregar casos nuevos.

### Casos que faltan

1. **Vacante sin link** — el caso que expone directamente el bug de `URL falsa`.
2. **Títulos casi idénticos** ("Backend Python Jr" vs "Backend Python Sr").
3. **Inyección dentro de las vacantes**, no del CV — hoy solo probamos el CV hostil.
4. **CV en inglés con vacantes en español** — la ventaja del producto es semántica y
   nunca la probamos cruzando idiomas.

### Lo que construí

**Nivel 2 (Intermediate)** — `check_contract()`: `match_score` debe parsear a entero
entre 0 y 100 (hoy Pydantic lo tipa como `str`, así que `"muy alto"` y `"150%"`
pasan la validación de forma), y máximo 2 recomendaciones.

**Nivel 3 (Advanced)** — `check_grounding()`: `titulo_oportunidad` debe aparecer
literalmente en las vacantes del input (normalizado, tolerando tildes y
mayúsculas), y `link` debe estar en el conjunto exacto de URLs del input —
comparación exacta, porque una URL que difiere en un carácter es otra URL. Si el
input no trae ninguna vacante, cualquier recomendación es inventada por definición.

**Prueba de que los validadores sirven.** Un 5/5 podría significar que no detectan
nada. Construí `adversarial_outputs.json` como control negativo:

```
python evals/run_evals.py --replay --input evals/adversarial_outputs.json
SCORE: 0/5
```

Atrapa vacantes inventadas, links inventados, habilidades atribuidas a un CV que no
las menciona, obediencia a la inyección, `match_score: 150%`, `"muy alto"` y 3
recomendaciones. Más 39 tests unitarios en `test_validators.py`, todos pasando.

**5/5 con datos reales, 0/5 con datos alucinados.** Eso es lo que hace que el 5/5
signifique algo.

---

## 4. ¿Qué haríamos primero si esto fuera producto real?

**Primero: conectar vacantes reales.** Hoy las vacantes son un string de mock data
escrito a mano. Todo el producto descansa sobre un input que no existe. Sin fuente
real no sabemos nada de lo que de verdad importa — vacantes con descripciones de
2000 caracteres, campos vacíos, HTML sucio, duplicados, avisos vencidos. El
baseline actual está medido sobre 3 vacantes limpias de una línea cada una; es un
laboratorio, no el mundo.

Y esto convierte el validador de anclaje en algo distinto: hoy verifica contra un
string; con una fuente real verificaría contra un ID de vacante y podría además
comprobar que el aviso siga vigente. Recomendar una vacante que existía pero ya
cerró es el mismo daño para el usuario que recomendar una inventada.

**Segundo: la capa de defensa, no solo el prompt.** Ya está implementada
(`filtrar_no_ancladas`, y `agent.py` corre en `strict=True`): el sistema descarta
las recomendaciones no ancladas antes de mostrarlas. La distinción es la que me
llevo de este ejercicio — **un prompt es una petición, un validador es una
garantía.** Un prompt mejor baja la probabilidad de que el modelo invente; el
validador hace que, aunque invente, el usuario no lo vea.

**Tercero: arreglar los 3 evals decorativos y agregar los 4 casos faltantes**, antes
de tocar el modelo o el prompt otra vez. Cambiar el prompt sin evals que midan lo
que importa es cambiar a ciegas y sentirse productivo.

**Cuarto: decidir qué hacer cuando no hay match.** El caso `empty_jobs` sacó a la
luz que no tenemos respuesta de producto para "no hay nada para ti esta semana". Un
JSON vacío es correcto y es inútil. ¿Explicamos por qué? ¿Sugerimos qué habilidad
cerraría la brecha? Esa decisión es de producto, no técnica, y hay que tomarla
antes de escribir el eval que la verifique.

**Lo que NO haría primero:** cambiar de modelo o subirle el tamaño. Es el reflejo
fácil y no ataca nada de lo anterior. Un modelo más grande con un prompt que dice
"URL falsa para el ejemplo" inventa URLs más convincentes.

---

## Archivos que agregué o modifiqué en esta rama

| Archivo | Qué es |
|---|---|
| `evals/validators.py` | Los 3 niveles de validación. Determinista, sin API. |
| `evals/run_evals.py` | Runner con modo `--replay` (offline) y `--live` (Groq). |
| `evals/test_validators.py` | 39 tests unitarios de los validadores. |
| `evals/recorded_baseline.json` | Outputs reales del 2026-08-18, congelados como "before". |
| `evals/adversarial_outputs.json` | Control negativo: outputs alucinados a propósito. |
| `evals/baseline_report.json` | Reporte generado del baseline (5/5). |
| `evals/adversarial_report.json` | Reporte generado del control (0/5). |
| `evals/results.md` | Baseline medido, bug encontrado, deuda de evals. |
| `agent.py` | **Modificado:** bug de `URL falsa` corregido + capa de validación. |
| `RESPUESTAS_MANUELA.md` | Este archivo. |

## Lo que queda pendiente y por qué

La corrida `--live` con el prompt corregido no la ejecuté: el entorno donde preparé
esto no tiene salida a `api.groq.com`. El comando está listo en `evals/results.md`.

Dejé escrita la predicción **antes** de correrlo, para no acomodar la conclusión
después: el score va a seguir en 5/5, porque los 5 casos ya pasaban. La mejora no
se va a ver en el score sino en el control adversarial y en el caso de "vacante sin
link" que todavía hay que agregar. Si el score fuera nuestra única métrica, este
cambio parecería inútil — y esa es justamente la trampa contra la que sirve tener
un control negativo.
