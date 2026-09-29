import logging
from fastapi import APIRouter, HTTPException, Depends
from api.models import RecruiterMatchRequest, RecruiterMatchResponse, CandidatoRankeado
from api.security import check_rate_limit
from api.dependencies import get_agent

logger = logging.getLogger("talentmatch.routers.recruiter")
router = APIRouter(tags=["Recruiter"])


@router.post("/recruiter/match", response_model=RecruiterMatchResponse, dependencies=[Depends(check_rate_limit)])
def recruiter_matching(request: RecruiterMatchRequest, agente=Depends(get_agent)):
    """Modo Recruiter: Matching Invertido B2B sin sesgos."""
    if not request.candidatos:
        raise HTTPException(status_code=400, detail="El pool de candidatos no puede estar vacío.")

    candidatos_payload = [{"id": c.id, "cv_text": c.cv_text} for c in request.candidatos]
    try:
        ranking_raw = agente.recruiter_matching(
            descripcion_vacante=request.descripcion_vacante,
            candidatos=candidatos_payload
        )
        ranking_modelos = [CandidatoRankeado(**c) for c in ranking_raw]
        return RecruiterMatchResponse(
            success=True,
            total_evaluados=len(request.candidatos),
            ranking=ranking_modelos,
            mensaje="Matching B2B completado con imparcialidad."
        )
    except Exception as e:
        logger.error("Error en /recruiter/match: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
