import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from api.models import MatchRequest, MatchResponse, TalentMatchOutput
from api.security import validate_cv_text, check_rate_limit
from api.dependencies import get_agent, get_pdf_parser
from agent import AgentError

logger = logging.getLogger("talentmatch.routers.matching")
router = APIRouter(tags=["Matching"])


@router.post("/match", response_model=MatchResponse, dependencies=[Depends(check_rate_limit)])
def match_cv(request: MatchRequest, agente=Depends(get_agent)):
    """Analiza un CV en texto plano contra la BD de vacantes."""
    logger.info("Recibida petición de matching (/match), longitud texto: %d", len(request.cv_text))
    texto_limpio = validate_cv_text(request.cv_text, truncate_if_too_long=True)

    try:
        resultado: TalentMatchOutput = agente.run(texto_limpio)
        return MatchResponse(
            success=True,
            data=resultado,
            mensaje=f"Procesado exitosamente en modo: {resultado.modo}"
        )
    except AgentError as e:
        logger.error("Error en agente (/match): %s", e)
        return MatchResponse(
            success=False,
            error=str(e),
            data=TalentMatchOutput(
                recomendaciones=[],
                perfil_candidato=None,
                modo="sin_datos",
                total_vacantes_evaluadas=len(agente.vacantes)
            )
        )
    except Exception as e:
        logger.error("Error no controlado en /match: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error interno procesando el CV: {str(e)}")


@router.post("/match/pdf", response_model=MatchResponse, dependencies=[Depends(check_rate_limit)])
async def match_pdf(
    file: UploadFile = File(...),
    agente=Depends(get_agent),
    pdf_parser=Depends(get_pdf_parser)
):
    """Extrae texto de un archivo PDF subido y ejecuta el pipeline de matching."""
    logger.info("Recibida petición de matching con archivo: %s (%s)", file.filename, file.content_type)

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Solo se aceptan archivos en formato PDF (.pdf)"
        )

    try:
        contenido = await file.read()
        texto_extraido = pdf_parser.extract_text_from_bytes(contenido)
    except Exception as e:
        logger.error("Error al extraer texto del PDF '%s': %s", file.filename, e)
        raise HTTPException(status_code=400, detail=f"No se pudo leer el archivo PDF: {str(e)}")

    logger.info("PDF procesado exitosamente: %d caracteres extraídos", len(texto_extraido))
    texto_limpio = validate_cv_text(texto_extraido, truncate_if_too_long=True)

    try:
        resultado: TalentMatchOutput = agente.run(texto_limpio)
        return MatchResponse(
            success=True,
            data=resultado,
            mensaje=f"PDF procesado exitosamente en modo: {resultado.modo}"
        )
    except AgentError as e:
        logger.error("Error en agente (/match/pdf): %s", e)
        return MatchResponse(
            success=False,
            error=str(e),
            data=TalentMatchOutput(
                recomendaciones=[],
                perfil_candidato=None,
                modo="sin_datos",
                total_vacantes_evaluadas=len(agente.vacantes)
            )
        )
    except Exception as e:
        logger.error("Error no controlado en /match/pdf: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error interno procesando el PDF: {str(e)}")
