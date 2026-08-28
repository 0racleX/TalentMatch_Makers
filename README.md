# TalentMatch AI

Proyecto de Dylan Mejía y Manuela Echeverrí — sistema de matching semántico CV ↔ vacantes usando Groq.

---

## Current Score

| Evals totales | Pasados | Fallados | Score |
|---|---|---|---|
| 6 | 4 | 1 | 66% |


---

## Known Failures

**1. El sistema no da un buen output cuando hay vacantes sin link o sin nada en general y no sabe que hacer .**

**2. El sistema cuando no hay cv da un arreglo vacio**

---

## Next Hypothesis

**1. Modificar el agente para que cuando no haya vacantes devuelva cosas mas interesantes que una lista vacia**

**2. Empezar el modelo multiagente**

**3. Revisar validaciones para que maneje mejor contenido que no tiene campos necesarios como links**