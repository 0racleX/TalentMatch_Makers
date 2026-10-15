# Guía de Pitch para Demo Day 1 — TalentMatch AI

> **Duración Total:** 6 minutos exactos  
> **Presentadores:** Dylan Mejía & Manuela Echeverrí  
> **Formato:** Web App en vivo (`http://localhost:8000/`) + Diapositivas de Arquitectura / Métricas  
> **Objetivo:** Demostrar cumplimiento de evals (100%), arquitectura hexagonal (Ports & Adapters), gates superados, flujo AI-native visible y diferenciación radical frente a LinkedIn y Magneto.

---

## Estructura Minuto a Minuto (Cronómetro 6:00)

```
[0:00 - 1:00]  Minuto 1: El Gancho y el Problema Roto (LinkedIn & Magneto)
[1:00 - 2:00]  Minuto 2: Elección de Presentación y Arquitectura Hexagonal
[2:00 - 3:15]  Minuto 3: Demo en Vivo — Flujo AI-Native Candidato y Camino a la Vacante
[3:15 - 4:15]  Minuto 4: Demo en Vivo — Modo Reclutador (Screening Inverso B2B)
[4:15 - 5:15]  Minuto 5: Gates Superados, Evals (12/12) y Auditoría de Sesgo (Trust Center)
[5:15 - 6:00]  Minuto 6: Modelo B2B/B2C, Escalabilidad y Cierre de Impacto
```

---

### Minuto 1: El Gancho y el Problema Roto (0:00 - 1:00)
**Voz principal:** Manuela (o Dylan)  
**Apoyo visual:** Pantalla inicial del Hero con el efecto de escritura dinámico (*"no en el silencio de Magneto, no en algoritmos opacos de LinkedIn"*).

> *"Buenos días a todos. Todos los presentes en esta sala hemos experimentado la frustración de postular a un empleo en plataformas como LinkedIn o Magneto para recibir una de dos cosas: un rechazo genérico automatizado de tres líneas semanas después, o el silencio absoluto: el ghosting.*
> 
> *Peor aún: más del 70% de las vacantes en esas plataformas ocultan el sueldo con la frase 'A convenir' y sus algoritmos son cajas negras cerradas que filtran a ciegas por palabras clave.*
> 
> *Hoy les presentamos **TalentMatch AI**, la alternativa transparente y auditable donde:*
> 1. *El ghosting está prohibido: si no encajas, te mostramos con evidencia por qué y te trazamos tu **Camino a la Vacante** con recursos reales y simulador interactivo.*
> 2. *El 100% de las vacantes tienen salarios públicos desde el primer segundo.*
> 3. *Garantizamos cero alucinaciones de ofertas mediante arquitectura."*

---

### Minuto 2: Elección de Presentación y Arquitectura Hexagonal (1:00 - 2:00)
**Voz principal:** Dylan  
**Apoyo visual:** Diagrama de Arquitectura Hexagonal en [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) o [`docs/ArquitecturaTalentMatch.png`](ArquitecturaTalentMatch.png).

> *"Para la presentación elegimos una **Web App Single Page Application (SPA)** reactiva con tema Glassmorphism Dark Mode y un Router en el cliente que permite alternar instantáneamente entre cuatro espacios: Candidato, Reclutador, Vacantes y Trust Center.*
> 
> *A nivel técnico, implementamos un **Monolito Modular con Arquitectura Hexagonal (Puertos y Adaptadores)**. ¿Por qué no microservicios distribuidos? Porque fragmentar un pipeline de inferencia de LLMs en microservicios HTTP generaría latencias de red innecesarias y fragilidad distribuida. Con la arquitectura hexagonal obtenemos exactamente los mismos beneficios de desacoplamiento:*
> - *Puertos de Entrada (Driving): `TalentMatchServicePort` y `RecruiterServicePort`, que desacoplan la API FastAPI del dominio.*
> - *Puertos de Salida (Driven): `LLMProviderPort`, `DocumentParserPort` y `VacanteRepositoryPort`.*
> 
> *Gracias a esta inversión de dependencias, nuestra suite de **33 pruebas unitarias deterministas** corre completa en solo 2.5 segundos con cero costo de API y cero llamadas de red externas."*

---

### Minuto 3: Demo en Vivo — Flujo AI-Native Candidato y Camino a la Vacante (2:00 - 3:15)
**Voz principal:** Manuela (operando la pantalla)  
**Acción en vivo:**
1. En la vista **Candidato**, subir un CV o hacer clic en una muestra de texto.
2. Hacer clic en **"Analizar con Evidencia"**.
3. Señalar el **Pipeline Visual sincronizado de 5 agentes** y abrir el **Thought Stream Console** (Consola de Razonamiento en vivo).

> *"Veamos el flujo AI-Native en acción. Al enviar el CV, primero actúa nuestra capa de seguridad y Gatekeeper, que neutraliza prompt injections y descarta automáticamente si alguien intenta subir una práctica de laboratorio universitaria o una factura.*
> 
> *Aquí pueden ver el pipeline en tiempo real: Agente 1 extrae habilidades estructuradas; Agente 2 realiza búsqueda semántica comprendiendo equivalencias como NLP y procesamiento de lenguaje; Agente 3 calcula afinidad objetiva y Agente 5 formatea los resultados.*
> 
> *Observen el resultado: cada tarjeta no solo da un porcentaje, sino la **evidencia textual exacta** de por qué encaja. Y aquí está nuestro mayor diferenciador: el **Camino a la Vacante**. Si el candidato tiene brechas como Docker o AWS, el sistema le entrega cursos curados y verificados de plataformas como CodeRise o freeCodeCamp.*
> 
> *Miren este botón: **'Simular +15%'**. El candidato puede simular interactivamente su crecimiento. Si da clic, el motor recalcula el match en vivo y le muestra cómo aumentaría su perfil al completar esa habilidad. Cero callejones sin salida."*

---

### Minuto 4: Demo en Vivo — Modo Reclutador (Screening Inverso B2B) (3:15 - 4:15)
**Voz principal:** Dylan  
**Acción en vivo:**
1. Clic en **"Modo Reclutador"** en el navbar o Hero.
2. Seleccionar la vacante curada *"Senior Python / FastAPI Developer"* del desplegable.
3. Clic en **"Cargar Candidatos de Prueba"** (pool de perfiles anonimizados).
4. Clic en **"Evaluar & Rankear con Evidencia"**.

> *"El problema de la contratación no es solo de los candidatos; los equipos de talento humano reciben cientos de hojas de vida y usan filtros por palabras clave que descartan a grandes ingenieros o introducen sesgos inconscientes por nombres o universidades.*
> 
> *En nuestro **Modo Reclutador B2B**, invertimos el pipeline: el reclutador pega la descripción del puesto y evalúa un pool de candidatos anonimizados. El sistema oculta identidades y genera un ranking técnico objetivo anclado 100% en evidencia comprobable de habilidades y proyectos reales.*
> 
> *Observen el ranking en pantalla: cada perfil tiene su puntaje justificado con evidencia y brechas detectadas. Así garantizamos un proceso de contratación ciego, justo y ultra-rápido."*

---

### Minuto 5: Gates Superados, Evals (12/12) y Auditoría de Sesgo (Trust Center) (4:15 - 5:15)
**Voz principal:** Manuela  
**Acción en vivo:**
1. Navegar a la pestaña **"Trust Center"**.
2. Clic en el botón **"Correr Auditoría de Sesgo en Vivo"**.
3. Clic en **"Correr Evals (Cache Inteligente)"** para ejecutar la suite de 12 casos.

> *"Para superar los gates de evaluación más exigentes de la industria, construimos nuestro **Trust Center Público**:*
> 1. *Garantía de Cero Alucinación (0% links rotos o falsos): los agentes solo recomiendan vacantes y recursos validados en la base de datos interna.*
> 2. *Auditoría de Equidad (Fairness Audit) en vivo: al presionar este botón, el sistema evalúa pares demográficos con exactamente las mismas habilidades técnicas pero variando género o procedencia. Como ven en el resultado: **100% de paridad matemática**, con variaciones menores al 5%. Demostramos equidad con datos, no con promesas.*
> 3. *Dashboard de Evals: ejecutamos los 12 casos de prueba automatizados que incluyen ataques adversariales de prompt injection, perfiles junior que deben activar perfilamiento y happy paths. **Puntaje perfecto: 12 de 12 aprobados (100%)**."*

---

### Minuto 6: Modelo B2B/B2C, Escalabilidad y Cierre (5:15 - 6:00)
**Voz principal:** Dylan & Manuela (Cierre conjunto)

> *"TalentMatch AI no es un prototipo escolar; es una plataforma de producción con arquitectura modular, reintentos exponenciales con jitter para tolerancia a fallas en Groq, rate limiting por IP, logging estructurado y persistencia con SQLAlchemy.*
> 
> *Nuestro modelo de negocio combina:*
> - *SaaS B2B para empresas que quieren hacer screening técnico ciego y reducir su tiempo de contratación en un 80%.*
> - *B2C / Alianzas educativas conectando candidatos con bootcamps y plataformas de formación para monetizar el cierre de brechas.*
> 
> *En TalentMatch AI transformamos el ghosting y los algoritmos ciegos en crecimiento profesional medible y contratación justa.*
> 
> *Muchas gracias. Quedamos a disposición del jurado para cualquier pregunta técnica o de producto."*

---

## Guía Rápida para Responder Preguntas del Jurado (FAQ Técnico)

| Pregunta Típica del Jurado | Respuesta Clave |
| :--- | :--- |
| **¿Por qué dicen que hay 0% alucinación en ofertas?** | *Porque el agente de formateo tiene prohibido generar URLs libres. Los enlaces de postulación se inyectan directamente desde los registros verificados de la base de datos SQL / JSON curada mediante IDs inmutables.* |
| **¿Qué pasa si Groq agota su cuota de tokens (TPD)?** | *Implementamos una estrategia de fallback en `GroqLLMAdapter`: conmuta automáticamente a modelos alternativos (`qwen/qwen3.8-27b`, `openai/gpt-oss-120b`) y usa backoff exponencial con jitter para recuperarse sin interrumpir al usuario.* |
| **¿Cómo garantizan que la auditoría de equidad sea justa?** | *Usamos pares controlados en `eval_runner.py` con CVs idénticos palabra por palabra donde solo cambia el nombre ("Carlos" vs. "Laura Valentina") o el origen ("Bogotá" vs. "Extranjero residente"). Si la diferencia de score excede el 5%, la prueba falla.* |
| **¿Cómo aíslan el dominio de los frameworks?** | *Mediante los puertos inbound `TalentMatchServicePort` y `RecruiterServicePort`. Si mañana reemplazamos FastAPI por gRPC o Groq por Ollama/Claude, el núcleo de los 5 agentes y sus reglas de negocio permanecen 100% inalterados.* |
