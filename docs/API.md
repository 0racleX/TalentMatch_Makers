# API Reference — TalentMatch AI

Base URL local: `http://localhost:8000` (o `http://localhost:3000` a través de Nginx en Docker).

## Autenticación y Seguridad

- **API Key (Opcional)**: Si se configura `TALENTMATCH_API_KEY` en `.env`, se debe enviar el header `X-API-Key: <tu_clave>` o `Authorization: Bearer <tu_clave>`.
- **Rate Limiting**: 40 req/min para endpoints estándar, 10 req/min para evals. Cabecera `Retry-After` en caso de exceder el límite (HTTP 429).
- **Límites de Texto**: `cv_text` mínimo 10 caracteres, máximo 15,000 caracteres.
- **Protección contra Prompt Injection**: Heurísticas activas para neutralizar instrucciones maliciosas en el CV.

---

## 1. Endpoints Base & Salud

### GET `/health`
Estado del servicio, versión, vacantes cargadas y base de datos.
```json
{
  "status": "ok",
  "version": "2.5.0",
  "vacantes_cargadas": 25,
  "auth_enabled": false,
  "database": "active"
}
```

### GET `/vacantes`
Lista completa de vacantes curadas con salario transparente y requisitos.
```json
{
  "total": 25,
  "vacantes": [
    {
      "id": "v001",
      "titulo": "Junior Penetration Tester",
      "empresa": "SecureNet Colombia",
      "salario_rango": "COP 3.5M - 5M",
      "tipo": "Empleo",
      "nivel": "Junior",
      "link": "https://securenet.co/careers/pentest-jr"
    }
  ]
}
```

### POST `/vacantes` (Requiere Auth)
Crea o actualiza una vacante dinámicamente en la base de datos sin necesidad de redeploy.

---

## 2. Matching de Candidato

### POST `/match`
Procesa el CV en texto plano a través del pipeline multiagente.
**Request**
```json
{
  "cv_text": "Desarrollador backend con 3 años en Python, FastAPI y PostgreSQL..."
}
```

**Response** (`success: true`)
```json
{
  "success": true,
  "data": {
    "recomendaciones": [
      {
        "titulo_oportunidad": "Backend Python Developer",
        "empresa": "FinPay SAS",
        "match_score": "88%",
        "razon_del_match": "Experiencia sólida en Python y APIs financieras...",
        "brechas_identificadas": "Docker, AWS",
        "link": "https://finpay.co/jobs/backend-python",
        "salario_rango": "COP 6M - 9M",
        "remoto": true,
        "recursos_recomendados": [
          {
            "id": "rec_docker_01",
            "habilidad": "Docker",
            "titulo": "Docker & Containers Fundamentals",
            "proveedor": "freeCodeCamp / Docker Docs",
            "costo": "Gratis",
            "url": "https://www.docker.com/101-tutorial/",
            "impacto_match_estimado": 20
          }
        ]
      }
    ],
    "perfil_candidato": null,
    "modo": "match",
    "total_vacantes_evaluadas": 25,
    "inyeccion_detectada": false
  },
  "error": null
}
```

### POST `/match/pdf`
Recibe un archivo `multipart/form-data` con campo `file` en formato PDF (máx 10MB).

---

## 3. Camino a la Vacante (Simulador Interactivo)

### POST `/pathway/simulate`
Simula el impacto de adquirir nuevas habilidades y proyecta el incremento de score.
**Request**
```json
{
  "cv_text": "Desarrollador con experiencia en Python y SQL",
  "vacante_id": "v002",
  "habilidades_aprendidas": ["Docker", "FastAPI"]
}
```

**Response**
```json
{
  "vacante_titulo": "Backend Python Developer",
  "empresa": "FinPay SAS",
  "score_original": "55%",
  "score_proyectado": "82%",
  "incremento_estimado": "+27%",
  "habilidades_aprendidas": ["Docker", "FastAPI"],
  "brechas_restantes": ["AWS"],
  "analisis_proyeccion": "Al dominar Docker y FastAPI, tu compatibilidad aumenta significativamente..."
}
```

---

## 4. Modo Recruiter (Matching B2B Libre de Sesgos)

### POST `/recruiter/match`
Evalúa un pool de candidatos frente a una vacante con perfiles anonimizados.
**Request**
```json
{
  "descripcion_vacante": "Buscamos Ingeniero DevOps con experiencia en Kubernetes y Docker...",
  "candidatos": [
    {
      "id": "c1",
      "nombre_anonimizado": "Candidato #1",
      "cv_text": "3 años en infraestructura cloud, Docker y pipelines CI/CD..."
    }
  ]
}
```

**Response**
```json
{
  "vacante_analizada": "Buscamos Ingeniero DevOps con experiencia en...",
  "total_candidatos": 1,
  "ranking": [
    {
      "candidato_id": "c1",
      "nombre_anonimizado": "Candidato #1",
      "match_score": "90%",
      "razon_del_match": "Evidencia concreta en Docker y pipelines CI/CD...",
      "brechas_detectadas": "Kubernetes avanzado",
      "habilidades_coincidentes": ["Docker", "Linux", "CI/CD"]
    }
  ]
}
```

---

## 5. Trust Center, Métricas y Auditoría de Sesgo

### GET `/metrics`
Métricas de confianza para el Trust Dashboard.
```json
{
  "total_evaluaciones": 32,
  "tasa_match_directo_pct": 84.4,
  "tasa_perfilamiento_pct": 15.6,
  "alucinaciones_links_detectadas": 0,
  "inyecciones_neutralizadas": 3,
  "politica_transparencia_salarial": "100% de vacantes con rango salarial visible"
}
```

### GET `/fairness/audit`
Ejecuta la prueba de equidad matemática comparando pares de perfiles idénticos con variaciones de género y origen.
```json
{
  "total_pruebas": 3,
  "pruebas_superadas": 3,
  "tasa_equidad_pct": 100.0,
  "veredicto": "Auditoría Aprobada: Algoritmo imparcial sin sesgo por género ni procedencia",
  "detalles": [ ... ]
}
```

### GET `/recursos`
Catálogo curado de recursos de formación, cursos y becas. Soporta filtro `?skill=Docker`.

### POST `/evals/run`
Ejecuta los 12 casos de prueba de evaluación. Soporta `?use_cache=true` (predeterminado) para respuestas inmediatas y consistentes.
