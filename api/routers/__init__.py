"""
Routers modulares para TalentMatch AI API.
"""
from api.routers.vacantes import router as vacantes_router
from api.routers.matching import router as matching_router
from api.routers.pathway import router as pathway_router
from api.routers.recruiter import router as recruiter_router
from api.routers.audit import router as audit_router

__all__ = [
    "vacantes_router",
    "matching_router",
    "pathway_router",
    "recruiter_router",
    "audit_router",
]
