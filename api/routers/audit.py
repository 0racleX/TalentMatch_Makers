import logging
from fastapi import APIRouter, HTTPException, Depends
from api.models import TrustMetricsResponse, FairnessAuditResponse, EvalRunResponse
from api.security import check_eval_rate_limit, verify_api_auth
from api.eval_runner import run_all_evals
from api.fairness import run_fairness_audit
from api.dependencies import get_agent
from db.repository import get_audit_metrics

logger = logging.getLogger("talentmatch.routers.audit")
router = APIRouter(tags=["Auditoría y Confianza"])


@router.get("/trust/metrics", response_model=TrustMetricsResponse)
def metricas_confianza():
    """Métricas operativas del Trust Center desde la BD de auditoría."""
    raw = get_audit_metrics()
    return TrustMetricsResponse(
        total_evaluaciones=raw["total_evaluaciones"],
        match_rate_pct=raw["match_rate_pct"],
        profiling_rate_pct=raw["profiling_rate_pct"],
        inyecciones_bloqueadas=raw["inyecciones_bloqueadas"],
        score_promedio=raw["score_promedio"],
        ultima_actualizacion=raw["ultima_actualizacion"]
    )


@router.get("/fairness/audit", response_model=FairnessAuditResponse, dependencies=[Depends(check_eval_rate_limit)])
def auditoria_sesgo(use_cache: bool = True, agente=Depends(get_agent)):
    """Auditoría de sesgo publicada en vivo."""
    try:
        reporte = run_fairness_audit(agente=agente, use_cache=use_cache)
        return FairnessAuditResponse(
            success=True,
            data=reporte,
            mensaje="Auditoría de imparcialidad completada exitosamente."
        )
    except Exception as e:
        logger.error("Error en /fairness/audit: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evals/run", response_model=EvalRunResponse, dependencies=[Depends(verify_api_auth), Depends(check_eval_rate_limit)])
def ejecutar_evaluaciones(use_cache: bool = True):
    """Ejecuta los casos de evaluación de la suite y retorna pass/fail detallado."""
    try:
        logger.info("Iniciando ejecución de evals (use_cache=%s)...", use_cache)
        resultado = run_all_evals(use_cache=use_cache)
        return EvalRunResponse(
            success=True,
            data=resultado,
            mensaje=f"Evals completados: {resultado['passed']}/{resultado['total']} pasaron ({resultado['score_pct']}%)"
        )
    except Exception as e:
        logger.error("Error al ejecutar evals: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error ejecutando la suite de evals: {str(e)}")
