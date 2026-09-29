import logging
from typing import List
from fastapi import APIRouter, HTTPException, Depends, Query
from api.models import SimulacionBrechasRequest, SimulacionBrechasResponse, RecursoAprendizaje
from api.security import check_rate_limit
from api.dependencies import get_agent
from db.repository import get_recursos_para_brechas

logger = logging.getLogger("talentmatch.routers.pathway")
router = APIRouter(tags=["Camino a la Vacante"])


@router.post("/simular-brechas", response_model=SimulacionBrechasResponse, dependencies=[Depends(check_rate_limit)])
def simular_cierre_brechas(request: SimulacionBrechasRequest, agente=Depends(get_agent)):
    """Simulador 'What-if' (Camino a la Vacante). Proyecta el aumento en compatibilidad."""
    try:
        resultado = agente.simulate_gap_closure(
            cv_text=request.cv_text,
            vacante_id=request.vacante_id,
            habilidades_aprendidas=request.habilidades_aprendidas
        )
        return SimulacionBrechasResponse(
            success=True,
            simulacion=resultado,
            mensaje="Simulación proyectada exitosamente."
        )
    except Exception as e:
        logger.error("Error en /simular-brechas: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recursos-brechas", response_model=List[RecursoAprendizaje])
def obtener_recursos_para_brechas(habilidades: str = Query(..., description="Habilidades separadas por coma")):
    """Retorna los cursos, proyectos prácticos y certificaciones asociadas a las brechas."""
    recursos_db = get_recursos_para_brechas(habilidades)
    return [RecursoAprendizaje(**r) for r in recursos_db]
