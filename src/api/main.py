"""
API REST FastAPI pour l'Assistant Matanne - Version Refactorée.

Point d'entrée principal de l'API avec les middlewares et routers.
"""

import logging
import os
from datetime import UTC, datetime

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.api.dependencies import require_role
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
        "name": "Notifications Push",
        "description": "Gestion des abonnements Web Push pour notifications",
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
    swagger_ui_parameters={
        "persistAuthorization": True,
        "displayRequestDuration": True,
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

# Middleware ETag pour cache HTTP
from src.api.utils import ETagMiddleware

app.add_middleware(ETagMiddleware)

# Middleware de métriques
from src.api.utils import MetricsMiddleware

app.add_middleware(MetricsMiddleware)

# Middleware de sécurité HTTP (CSP, HSTS, X-Content-Type-Options, etc.)
from src.api.utils import SecurityHeadersMiddleware

app.add_middleware(SecurityHeadersMiddleware)


# ═══════════════════════════════════════════════════════════
# GESTIONNAIRE D'EXCEPTIONS GLOBAL
# ═══════════════════════════════════════════════════════════


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Gestionnaire global qui empêche les fuites d'erreurs internes."""
    from fastapi.responses import JSONResponse

    logger.error(
        f"Exception non gérée sur {request.method} {request.url.path}: {exc}", exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Une erreur interne est survenue. Veuillez réessayer."},
    )


# ═══════════════════════════════════════════════════════════
# SCHÉMAS COMMUNS
# ═══════════════════════════════════════════════════════════


class ServiceStatus(BaseModel):
    """Statut d'un service."""

    status: str
    latency_ms: float | None = None
    details: str | None = None


class HealthResponse(BaseModel):
    """Réponse du health check détaillé.

    Example:
        ```json
        {
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": "2026-02-19T14:30:00",
            "services": {
                "database": {"status": "ok", "latency_ms": 12.5},
                "cache": {"status": "ok", "latency_ms": 0.8},
                "ai": {"status": "ok", "details": "Mistral API accessible"}
            },
            "uptime_seconds": 3600
        }
        ```
    """

    status: str
    version: str
    timestamp: datetime
    services: dict[str, ServiceStatus]
    uptime_seconds: float


# Heure de démarrage pour calculer l'uptime
_START_TIME = datetime.now(UTC)


# ═══════════════════════════════════════════════════════════
# ENDPOINTS SANTÉ
# ═══════════════════════════════════════════════════════════


@app.get("/", tags=["Santé"])
async def root():
    """
    Point d'entrée racine de l'API.

    Returns:
        Message de bienvenue avec liens utiles.

    Example:
        ```json
        {
            "message": "API Assistant Matanne",
            "docs": "/docs",
            "version": "1.0.0"
        }
        ```
    """
    return {"message": "API Assistant Matanne", "docs": "/docs", "version": "1.0.0"}


@app.get("/health", response_model=HealthResponse, tags=["Santé"])
async def health_check():
    """
    Vérifie l'état de l'API et de toutes ses dépendances.

    Checks effectués:
    - **Database**: Connexion PostgreSQL via SQLAlchemy
    - **Cache**: Système de cache multi-niveaux
    - **AI**: Disponibilité de l'API Mistral (si configurée)

    Returns:
        - `status`: "healthy" | "degraded" | "unhealthy"
        - `services`: Détail par service avec latence
        - `uptime_seconds`: Temps depuis le démarrage

    Example:
        ```json
        {
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": "2026-02-19T14:30:00",
            "services": {
                "database": {"status": "ok", "latency_ms": 12.5},
                "cache": {"status": "ok", "latency_ms": 0.8}
            },
            "uptime_seconds": 3600
        }
        ```
    """
    import time

    services: dict[str, ServiceStatus] = {}

    # Check Database
    try:
        from sqlalchemy import text

        from src.core.db import obtenir_contexte_db

        start = time.perf_counter()
        with obtenir_contexte_db() as session:
            session.execute(text("SELECT 1"))
        latency = (time.perf_counter() - start) * 1000
        services["database"] = ServiceStatus(status="ok", latency_ms=round(latency, 2))
    except Exception as e:
        logger.error(f"Health check DB error: {e}")
        services["database"] = ServiceStatus(status="error", details="Connexion impossible")

    # Check Cache
    try:
        from src.core.caching import obtenir_cache

        start = time.perf_counter()
        cache = obtenir_cache()
        cache.get("_health_check_test")
        latency = (time.perf_counter() - start) * 1000
        services["cache"] = ServiceStatus(status="ok", latency_ms=round(latency, 2))
    except Exception as e:
        logger.error(f"Health check cache error: {e}")
        services["cache"] = ServiceStatus(status="error", details="Cache indisponible")

    # Check AI (optionnel - ne bloque pas si non configuré)
    try:
        import os

        if os.getenv("MISTRAL_API_KEY"):
            services["ai"] = ServiceStatus(status="ok", details="Mistral API configured")
        else:
            services["ai"] = ServiceStatus(status="warning", details="No API key configured")
    except Exception as e:
        logger.error(f"Health check AI error: {e}")
        services["ai"] = ServiceStatus(status="error", details="Service IA indisponible")

    # Déterminer le statut global
    statuses = [s.status for s in services.values()]
    if all(s == "ok" for s in statuses):
        overall = "healthy"
    elif "error" in statuses:
        overall = "unhealthy" if statuses.count("error") > 1 else "degraded"
    else:
        overall = "degraded"

    uptime = (datetime.now(UTC) - _START_TIME).total_seconds()

    return HealthResponse(
        status=overall,
        version="1.0.0",
        timestamp=datetime.now(UTC),
        services=services,
        uptime_seconds=round(uptime, 1),
    )


@app.get("/metrics", tags=["Santé"])
async def get_api_metrics(user: dict = Depends(require_role("admin"))):
    """Retourne les métriques de l'API (latence, requêtes, rate limiting)."""
    from src.api.utils import get_metrics

    return get_metrics()


# ═══════════════════════════════════════════════════════════
# ENREGISTREMENT DES ROUTERS
# ═══════════════════════════════════════════════════════════


from src.api.routes.auth import router as auth_router
from src.api.routes.push import router as push_router

app.include_router(auth_router)
app.include_router(recettes_router)
app.include_router(inventaire_router)
app.include_router(courses_router)
app.include_router(planning_router)
app.include_router(push_router)
app.include_router(suggestions_router)
