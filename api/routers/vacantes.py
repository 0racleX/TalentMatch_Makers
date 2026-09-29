import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from api.security import verify_api_auth
from db.repository import get_all_vacantes, get_vacante_by_id
from db.database import SessionLocal
from db.models import VacanteModel

logger = logging.getLogger("talentmatch.routers.vacantes")
router = APIRouter(tags=["Vacantes"])


@router.get("/vacantes")
def listar_vacantes():
    """Retorna la BD interna de vacantes para transparencia radical."""
    vacantes = get_all_vacantes()
    return {"total": len(vacantes), "vacantes": vacantes}


@router.get("/vacantes/{vacante_id}")
def obtener_vacante(vacante_id: str):
    """Retorna los detalles de una vacante específica por ID."""
    vacante = get_vacante_by_id(vacante_id)
    if not vacante:
        raise HTTPException(status_code=404, detail="Vacante no encontrada")
    return vacante


@router.post("/vacantes", dependencies=[Depends(verify_api_auth)])
def crear_vacante(vacante_data: dict):
    """Crea una nueva vacante en la BD. Requiere autenticación de API."""
    required = ["id", "titulo", "empresa", "tipo_empresa", "nivel", "area", "tipo", "requisitos", "descripcion"]
    missing = [f for f in required if f not in vacante_data]
    if missing:
        raise HTTPException(status_code=400, detail=f"Faltan campos obligatorios: {missing}")

    db = SessionLocal()
    try:
        if db.query(VacanteModel).filter_by(id=vacante_data["id"]).first():
            raise HTTPException(status_code=409, detail=f"Ya existe una vacante con ID '{vacante_data['id']}'")
        nueva = VacanteModel(**vacante_data)
        db.add(nueva)
        db.commit()
        return {"success": True, "message": f"Vacante '{vacante_data['titulo']}' creada exitosamente", "id": vacante_data["id"]}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creando vacante: {e}")
    finally:
        db.close()
