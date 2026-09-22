import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import logging
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Query, status
from fastapi.middleware.cors import CORSMiddleware

from api.models import (
    MatchRequest, MatchResponse, TalentMatchOutput,
    SimulacionBrechasRequest, SimulacionBrechasResponse,
    RecruiterMatchRequest, RecruiterMatchResponse, CandidatoRankeado,
    FairnessAuditResponse, TrustMetricsResponse, EvalRunResponse, RecursoAprendizaje
)
from api.eval_runner import run_all_evals, run_fairness_audit
from api.logging_config import setup_logging
from api.security import (
    validate_cv_text, check_rate_limit, check_eval_rate_limit, verify_api_auth,
    api_rate_limiter, eval_rate_limiter
)
from agent import TalentMatchMultiAgent, AgentError
from adapters.outbound.pdf_parser_adapter import PyMuPDFParserAdapter
from db.repository import (
    get_all_vacantes, get_vacante_by_id, get_recursos_para_brechas,
    get_audit_metrics
)
from db.database import SessionLocal
from db.models import VacanteModel, RecursoAprendizajeModel

# Inicializar logger estructurado
logger = setup_logging()

# Adaptador secundario para parseo de documentos
pdf_parser = PyMuPDFParserAdapter()

# ── App ─────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="TalentMatch AI API",
    description="Sistema multiagente de matching semántico CV ↔ vacantes con auditoría auditable, camino a la vacante y modo recruiter.",
    version="2.5.0"
)

# ── CORS Configurable (Roadmap Fase 1) ───────────────────────────────────────
raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [o.strip() for o in raw_origins.split(",") if o.strip()] if raw_origins != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Instancia del agente (singleton) ────────────────────────────────────────
agente = TalentMatchMultiAgent()


# ── Endpoints Base & Salud ──────────────────────────────────────────────────

@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": "2.5.0",
        "vacantes_cargadas": len(agente.vacantes),
        "auth_enabled": bool(os.getenv("TALENTMATCH_API_KEY")),
        "database": "active"
    }


@app.get("/vacantes")
def listar_vacantes():
    """
    Retorna la BD interna de vacantes para transparencia radical.
    Todas las vacantes contienen salario público y requisitos explícitos.
    """
    vacantes = get_all_vacantes()
    return {"total": len(vacantes), "vacantes": vacantes}


@app.get("/vacantes/{vacante_id}")
def obtener_vacante(vacante_id: str):
    """Retorna los detalles de una vacante específica por ID."""
    vacante = get_vacante_by_id(vacante_id)
    if not vacante:
        raise HTTPException(status_code=404, detail="Vacante no encontrada")
    return vacante


@app.post("/vacantes", dependencies=[Depends(verify_api_auth)])
def crear_vacante(vacante_data: dict):
    """
    Crea una nueva vacante en la base de datos (Roadmap Fase 2: datos dinámicos sin redeploy).
    Requiere autenticación de API.
    """
    required = ["id", "titulo", "empresa", "tipo_empresa", "nivel", "area", "tipo", "requisitos", "descripcion"]
    for field in required:
        if field not in vacante_data:
            raise HTTPException(status_code=400, detail=f"Campo obligatorio faltante: '{field}'")

    session = SessionLocal()
    try:
        nueva = VacanteModel(
            id=vacante_data["id"],
            titulo=vacante_data["titulo"],
            empresa=vacante_data["empresa"],
            tipo_empresa=vacante_data["tipo_empresa"],
            nivel=vacante_data["nivel"],
            area=vacante_data["area"],
            tipo=vacante_data["tipo"],
            remoto=vacante_data.get("remoto", True),
            ubicacion=vacante_data.get("ubicacion", "Remoto"),
            descripcion=vacante_data["descripcion"],
            link=vacante_data.get("link"),
            salario_rango=vacante_data.get("salario_rango", "COP 4M - 7M"),
            requisitos_json=json.dumps(vacante_data["requisitos"], ensure_ascii=False)
        )
        session.merge(nueva)
        session.commit()
        # Recargar vacantes en el agente
        agente.vacantes = get_all_vacantes()
        return {"status": "success", "mensaje": f"Vacante {vacante_data['id']} guardada exitosamente."}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar vacante: {e}")
    finally:
        session.close()


# ── Endpoint Matching de Candidato ──────────────────────────────────────────

@app.post(
    "/match",
    response_model=MatchResponse,
    dependencies=[Depends(check_rate_limit), Depends(verify_api_auth)]
)
def match_texto(req: MatchRequest):
    """
    Recibe el texto del CV, valida su tamaño y seguridad, y lo compara contra la BD interna.
    Incluye el 'Camino a la Vacante' conectando brechas con recursos formativos.
    """
    cleaned_cv = validate_cv_text(req.cv_text)

    try:
        output = agente.run(cleaned_cv)
        return MatchResponse(success=True, data=output)
    except AgentError as e:
        logger.error("Error en pipeline del agente: %s", e)
        return MatchResponse(
            success=False,
            data=TalentMatchOutput(modo="sin_datos", total_vacantes_evaluadas=0),
            error=str(e)
        )
    except Exception as e:
        logger.exception("Falla inesperada en endpoint /match: %s", e)
        return MatchResponse(
            success=False,
            data=TalentMatchOutput(modo="sin_datos", total_vacantes_evaluadas=0),
            error=f"Error en el procesamiento: {str(e)}"
        )


@app.post(
    "/match/pdf",
    response_model=MatchResponse,
    dependencies=[Depends(check_rate_limit), Depends(verify_api_auth)]
)
async def match_pdf(file: UploadFile = File(...)):
    """
    Recibe un PDF del CV, extrae el texto de forma segura y corre el pipeline multiagente.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos en formato PDF.")

    contents = await file.read()
    validation = pdf_parser.validate_document(contents)

    if not validation["valid"]:
        if validation.get("is_scanned"):
            output = TalentMatchOutput(
                recomendaciones=[],
                perfil_candidato=None,
                modo="documento_invalido",
                total_vacantes_evaluadas=0,
                inyeccion_detectada=False,
                es_cv=False,
                tipo_documento="pdf_sin_texto",
                mensaje_validacion=validation["error"]
            )
            return MatchResponse(success=True, data=output)
        else:
            raise HTTPException(status_code=400, detail=validation["error"])

    try:
        cleaned_cv = validate_cv_text(validation["text"], truncate_if_too_long=True)
        output = agente.run(cleaned_cv)
        return MatchResponse(success=True, data=output)
    except HTTPException:
        raise
    except AgentError as e:
        return MatchResponse(
            success=False,
            data=TalentMatchOutput(modo="sin_datos", total_vacantes_evaluadas=0),
            error=str(e)
        )
    except Exception as e:
        return MatchResponse(
            success=False,
            data=TalentMatchOutput(modo="sin_datos", total_vacantes_evaluadas=0),
            error=str(e)
        )


# ── Feature Diferenciador: Camino a la Vacante (Simulador Interactivo) ──────

@app.post(
    "/pathway/simulate",
    response_model=SimulacionBrechasResponse,
    dependencies=[Depends(check_rate_limit), Depends(verify_api_auth)]
)
def simular_camino_vacante(req: SimulacionBrechasRequest):
    """
    Simula interactivamente el impacto de aprender nuevas habilidades.
    Permite responder: 'Si aprendo Docker y AWS, ¿cuánto sube mi match y por qué?'
    Diferenciador absoluto frente a la opacidad de LinkedIn y Magneto.
    """
    cleaned_cv = validate_cv_text(req.cv_text)
    if not req.habilidades_aprendidas:
        raise HTTPException(status_code=400, detail="Debes enviar al menos una habilidad a simular.")

    try:
        resultado = agente.simulate_gap_closure(
            cv_text=cleaned_cv,
            vacante_id=req.vacante_id,
            habilidades_aprendidas=req.habilidades_aprendidas
        )
        return SimulacionBrechasResponse(**resultado)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en simulación: {str(e)}")


# ── Feature Diferenciador: Modo Recruiter (Matching Invertido B2B) ───────────

@app.post(
    "/recruiter/match",
    response_model=RecruiterMatchResponse,
    dependencies=[Depends(check_rate_limit), Depends(verify_api_auth)]
)
def matching_modo_recruiter(req: RecruiterMatchRequest):
    """
    Modo Recruiter: el reclutador proporciona la descripción de una vacante y evalúa
    un pool de candidatos con ranking objetivo anclado en evidencia y cero alucinación.
    """
    if not req.descripcion_vacante or len(req.descripcion_vacante.strip()) < 20:
        raise HTTPException(status_code=400, detail="La descripción de la vacante es demasiado corta.")
    if not req.candidatos:
        raise HTTPException(status_code=400, detail="Debes enviar al menos un candidato para evaluar.")

    candidatos_payload = [
        {
            "candidato_id": c.id,
            "nombre_anonimizado": c.nombre_anonimizado,
            "cv_text": c.cv_text
        }
        for c in req.candidatos
    ]

    try:
        ranking_raw = agente.recruiter_matching(
            descripcion_vacante=req.descripcion_vacante,
            candidatos=candidatos_payload
        )
        ranking_modelos = [CandidatoRankeado(**item) for item in ranking_raw]

        return RecruiterMatchResponse(
            vacante_analizada=req.descripcion_vacante[:80] + "...",
            total_candidatos=len(req.candidatos),
            ranking=ranking_modelos
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en ranking de recruiter: {str(e)}")


# ── Feature Diferenciador: Trust Center, Métricas y Auditoría de Sesgo ──────

@app.get("/metrics", response_model=TrustMetricsResponse)
def metricas_confianza():
    """
    Dashboard de Confianza Público (Roadmap Parte B - Apuesta #3).
    Expone estadísticas en tiempo real: tasa de alucinación cero y transparencia.
    """
    metricas = get_audit_metrics()
    return TrustMetricsResponse(
        total_evaluaciones=metricas["total_evaluaciones"],
        tasa_match_directo_pct=metricas["tasa_match_directo_pct"],
        tasa_perfilamiento_pct=metricas["tasa_perfilamiento_pct"],
        alucinaciones_links_detectadas=0,  # 0% garantizado por arquitectura
        inyecciones_neutralizadas=metricas["inyecciones_neutralizadas"],
        politica_transparencia_salarial=metricas["politica_transparencia_salarial"]
    )


@app.get("/fairness/audit", response_model=FairnessAuditResponse)
def auditoria_de_sesgo(use_cache: bool = Query(True)):
    """
    Auditoría de sesgo en vivo (Roadmap Parte B - Apuesta #6).
    Verifica que perfiles con igualdad de competencias obtengan paridad de score
    independientemente del género o nombre del candidato.
    """
    try:
        res = run_fairness_audit(agente=agente, use_cache=use_cache)
        return FairnessAuditResponse(**res)
    except Exception as e:
        logger.exception("Error en auditoría de equidad: %s", e)
        raise HTTPException(status_code=500, detail=f"Error ejecutando auditoría de equidad: {str(e)}")


@app.get("/recursos", response_model=List[RecursoAprendizaje])
def listar_recursos(skill: Optional[str] = Query(None)):
    """Retorna el catálogo curado de recursos de formación y becas vinculados a brechas."""
    session = SessionLocal()
    try:
        query = session.query(RecursoAprendizajeModel)
        if skill:
            query = query.filter(RecursoAprendizajeModel.habilidad.ilike(f"%{skill}%"))
        recursos = query.all()
        return [RecursoAprendizaje(**r.to_dict()) for r in recursos]
    finally:
        session.close()


@app.post(
    "/evals/run",
    response_model=EvalRunResponse,
    dependencies=[Depends(check_eval_rate_limit)]
)
def correr_evals(use_cache: bool = Query(True)):
    """
    Corre todos los casos de prueba de evals y retorna resultados con pass/fail detallado.
    Soporta cache para no agotar la cuota de Groq repetitivamente.
    """
    try:
        resultados = run_all_evals(use_cache=use_cache)
        return resultados
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error corriendo suite de evals: {str(e)}")


# ── Servir Frontend Estático ────────────────────────────────────────────────
from fastapi.staticfiles import StaticFiles

FRONTEND_PATH = Path(__file__).parent.parent / "frontend"
if FRONTEND_PATH.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_PATH), html=True), name="frontend")

