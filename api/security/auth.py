import os
import logging
from fastapi import Request, HTTPException, Security, status
from fastapi.security import APIKeyHeader

logger = logging.getLogger("talentmatch.security.auth")

MIN_CV_LENGTH = 10
MAX_CV_LENGTH = 15000

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


def validate_cv_text(text: str, truncate_if_too_long: bool = False) -> str:
    """Valida límites de longitud del texto."""
    cleaned = (text or "").strip()
    if len(cleaned) < MIN_CV_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"El texto extraído es demasiado corto ({len(cleaned)} caracteres, mínimo requerido: {MIN_CV_LENGTH}). "
                "Si subiste un archivo PDF, asegúrate de que contenga texto digital legible y no sea un archivo gráfico, afiche o escaneo sin capa de texto."
            )
        )
    if len(cleaned) > MAX_CV_LENGTH:
        if truncate_if_too_long:
            logger.info("El texto supera el límite de %d caracteres. Truncando de manera segura a %d...", MAX_CV_LENGTH, MAX_CV_LENGTH)
            return cleaned[:MAX_CV_LENGTH]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El texto del CV supera el límite máximo permitido ({MAX_CV_LENGTH} caracteres)."
        )
    return cleaned


def verify_api_auth(request: Request, api_key: str = Security(API_KEY_HEADER)):
    """
    Verifica API Key si la variable de entorno `TALENTMATCH_API_KEY` está configurada.
    Si no está configurada, se permite el acceso libre (modo local/desarrollo).
    """
    required_key = os.getenv("TALENTMATCH_API_KEY", "").strip()
    if not required_key:
        return True

    auth_header = request.headers.get("Authorization", "")
    bearer_token = ""
    if auth_header.startswith("Bearer "):
        bearer_token = auth_header[7:].strip()

    token = api_key or bearer_token
    if token != required_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida o no proporcionada en header 'X-API-Key' o 'Authorization: Bearer <key>'"
        )
    return True
