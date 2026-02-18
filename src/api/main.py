"""
API REST FastAPI pour l'Assistant Matanne - Version Refactorée.

Point d'entrée principal de l'API avec les middlewares et routers.
"""

import logging
import os
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.api.rate_limiting import MiddlewareLimitationDebit
from src.api.routes import (
    courses_router,
    inventaire_router,
    planning_router,
    recettes_router,
    suggestions_router,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# APPLICATION FASTAPI
# ═══════════════════════════════════════════════════════════


app = FastAPI(
    title="Assistant Matanne API",
    description="API REST pour la gestion familiale",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS sécurisé
_cors_origins = os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else []
_default_origins = [
    "http://localhost:8501",  # Streamlit local
    "http://localhost:8000",  # API local
    "http://127.0.0.1:8501",
    "http://127.0.0.1:8000",
    "https://matanne.streamlit.app",  # Production Streamlit Cloud
]
_allowed_origins = _cors_origins if _cors_origins else _default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

app.add_middleware(MiddlewareLimitationDebit)


# ═══════════════════════════════════════════════════════════
# SCHÉMAS COMMUNS
# ═══════════════════════════════════════════════════════════


class HealthResponse(BaseModel):
    """Réponse du health check."""

    status: str
    version: str
    database: str
    timestamp: datetime


# ═══════════════════════════════════════════════════════════
# ENDPOINTS SANTÉ
# ═══════════════════════════════════════════════════════════


@app.get("/", tags=["Santé"])
async def root():
    """Point d'entrée racine."""
    return {"message": "API Assistant Matanne", "docs": "/docs", "version": "1.0.0"}


@app.get("/health", response_model=HealthResponse, tags=["Santé"])
async def health_check():
    """Vérifie l'état de l'API et de la base de données."""
    db_status = "ok"

    try:
        from sqlalchemy import text

        from src.core.db import obtenir_contexte_db

        with obtenir_contexte_db() as session:
            session.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {e}"

    return HealthResponse(
        status="healthy" if db_status == "ok" else "degraded",
        version="1.0.0",
        database=db_status,
        timestamp=datetime.now(),
    )


# ═══════════════════════════════════════════════════════════
# ENREGISTREMENT DES ROUTERS
# ═══════════════════════════════════════════════════════════


app.include_router(recettes_router)
app.include_router(inventaire_router)
app.include_router(courses_router)
app.include_router(planning_router)
app.include_router(suggestions_router)
