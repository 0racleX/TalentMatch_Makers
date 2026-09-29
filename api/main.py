import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.logging_config import setup_logging
from api.dependencies import agente
from api.routers import (
    vacantes_router, matching_router, pathway_router,
    recruiter_router, audit_router
)

logger = setup_logging()

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

# ── Routers Modulares por Dominio ───────────────────────────────────────────
app.include_router(vacantes_router)
app.include_router(matching_router)
app.include_router(pathway_router)
app.include_router(recruiter_router)
app.include_router(audit_router)

# ── Servir Frontend Estático ─────────────────────────────────────────────────
FRONTEND_PATH = Path(__file__).parent.parent / "frontend"
if FRONTEND_PATH.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_PATH), html=True), name="frontend")
