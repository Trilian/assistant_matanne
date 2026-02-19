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


# Tags pour organiser la documentation OpenAPI
tags_metadata = [
    {
        "name": "Authentification",
        "description": "Inscription, connexion et gestion des tokens JWT",
    },
    {
        "name": "Santé",
        "description": "Endpoints de vérification de l'état de l'API",
    },
    {
        "name": "Recettes",
        "description": "Gestion des recettes de cuisine - CRUD complet",
    },
    {
        "name": "Inventaire",
        "description": "Gestion du stock alimentaire et des articles",
    },
    {
        "name": "Courses",
        "description": "Listes de courses et articles à acheter",
    },
    {
        "name": "Planning",
        "description": "Planning des repas de la semaine",
    },
    {
        "name": "IA",
        "description": "Suggestions intelligentes via Mistral AI",
    },
]

app = FastAPI(
    title="Assistant Matanne API",
    description="""
## API REST pour la gestion familiale

Cette API permet d'accéder aux fonctionnalités de l'Assistant Matanne:

- 🍽️ **Recettes**: CRUD complet pour gérer les recettes
- 📦 **Inventaire**: Suivi du stock alimentaire
- 🛒 **Courses**: Gestion des listes de courses
- 📅 **Planning**: Planification des repas
- 🤖 **IA**: Suggestions intelligentes

### Authentification

L'API utilise des tokens JWT Bearer. Obtenez un token via `POST /api/v1/auth/login`.
En mode développement, un utilisateur dev est utilisé par défaut.

### Rate Limiting

Les endpoints sont protégés par une limitation de débit:
- Endpoints standards: 60 req/min
- Endpoints IA: 10 req/min
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=tags_metadata,
    contact={
        "name": "Assistant Matanne",
        "url": "https://github.com/Trilian/assistant_matanne",
    },
    license_info={
        "name": "MIT",
    },
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

# Middleware de métriques
from src.api.utils import MetricsMiddleware

app.add_middleware(MetricsMiddleware)


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


@app.get("/metrics", tags=["Santé"])
async def get_api_metrics():
    """Retourne les métriques de l'API (latence, requêtes, rate limiting)."""
    from src.api.utils import get_metrics

    return get_metrics()


# ═══════════════════════════════════════════════════════════
# ENREGISTREMENT DES ROUTERS
# ═══════════════════════════════════════════════════════════


from src.api.routes.auth import router as auth_router

app.include_router(auth_router)
app.include_router(recettes_router)
app.include_router(inventaire_router)
app.include_router(courses_router)
app.include_router(planning_router)
app.include_router(suggestions_router)
