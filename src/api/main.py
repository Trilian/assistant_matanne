"""
API REST FastAPI pour l'Assistant Matanne - Version Refactorée.

Point d'entrée principal de l'API avec les middlewares et routers.
"""

import logging
import os
import time
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# ═══════════════════════════════════════════════════════════
# SENTRY (Error Tracking)
# ═══════════════════════════════════════════════════════════

_sentry_dsn = os.getenv("SENTRY_DSN")
if _sentry_dsn:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        from sentry_sdk.integrations.starlette import StarletteIntegration

        sentry_sdk.init(
            dsn=_sentry_dsn,
            environment=os.getenv("ENVIRONMENT", "development"),
            traces_sample_rate=0.1,
            profiles_sample_rate=0.1,
            integrations=[
                StarletteIntegration(transaction_style="url"),
                FastApiIntegration(transaction_style="url"),
                SqlalchemyIntegration(),
                LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
            ],
            # Ne pas envoyer les données personnelles
            send_default_pii=False,
        )
        logging.info("Sentry initialized: FastAPI + SQLAlchemy + Logging integrations actives")
    except ImportError:
        logging.warning("Sentry DSN configuré mais sentry-sdk[fastapi] non installé")
else:
    logging.info("Sentry DSN non configuré, error tracking désactivé")


from src.api.dependencies import require_role
from src.api.prometheus import prometheus_router
from src.api.rate_limiting import MiddlewareLimitationDebit
from src.api.routes import (
    assistant_router,
    admin_router,
    anti_gaspillage_router,
    automations_router,
    batch_cooking_router,
    calendriers_router,
    courses_router,
    dashboard_router,
    documents_router,
    export_router,
    famille_router,
    habitat_router,
    garmin_router,
    ia_avancee_router,
    ia_sprint13_router,
    fonctionnalites_avancees_router,
    inventaire_router,
    jeux_router,
    maison_router,
    partage_router,
    planning_router,
    preferences_router,
    recettes_router,
    recherche_router,
    rgpd_router,
    suggestions_router,
    upload_router,
    utilitaires_router,
    voyages_router,
    webhooks_router,
    predictions_router,
    ia_bridges_router,
    bridges_router,
    intra_flux_router,
)
from src.api.routes.auth import router as auth_router
from src.api.routes.push import router as push_router
from src.api.routes.webhooks_whatsapp import router as whatsapp_router
from src.api.schemas.errors import REPONSE_500, REPONSES_AUTH_ADMIN
from src.api.utils import (
    ETagMiddleware,
    MetricsMiddleware,
    SecurityHeadersMiddleware,
    get_metrics,
)
from src.api.versioning import VersionMiddleware
from src.api.websocket import ws_notes_router, ws_planning_router, ws_projets_router
from src.api.websocket.admin_logs import router as ws_admin_logs_router
from src.api.websocket_courses import router as websocket_router
from src.core.monitoring.health import StatutSante, verifier_sante_globale

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# LIFESPAN — démarrage/arrêt propre (cron, etc.)
# ═══════════════════════════════════════════════════════════


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    """Gère le démarrage et l'arrêt de l'application FastAPI."""
    # ── Démarrage ───────────────────────────────────────────
    try:
        from src.core.caching.invalidation_listener import (
            demarrer_listener_invalidation_cache,
        )

        demarrer_listener_invalidation_cache()
    except Exception:
        logger.warning("Listener invalidation cache non démarré", exc_info=True)

    try:
        from src.services.core.cron import demarrer_scheduler

        demarrer_scheduler()
    except Exception:
        logger.warning("Scheduler cron non démarré (module indisponible)", exc_info=True)

    yield

    # ── Arrêt ────────────────────────────────────────────────
    try:
        from src.services.core.cron import arreter_scheduler

        arreter_scheduler()
    except Exception:
        logger.debug("Scheduler cron déjà arrêté ou non initialisé")

    try:
        from src.core.caching.invalidation_listener import (
            arreter_listener_invalidation_cache,
        )

        arreter_listener_invalidation_cache()
    except Exception:
        logger.debug("Listener invalidation cache déjà arrêté ou non initialisé")



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
    {
        "name": "Famille",
        "description": "Suivi enfant, activités, budget et shopping familial",
    },
    {
        "name": "Maison",
        "description": "Projets, routines, entretien, jardin et stocks maison",
    },
    {
        "name": "Habitat",
        "description": "Scenarios, veille immo, plans, deco et paysagisme",
    },
    {
        "name": "Jeux",
        "description": "Paris sportifs et tirages Loto",
    },
    {
        "name": "Calendriers",
        "description": "Synchronisation calendriers externes et événements",
    },
    {
        "name": "WebSocket",
        "description": "Collaboration temps réel sur les listes de courses",
    },
    {
        "name": "WebSocket Planning",
        "description": "Collaboration temps réel sur le planning repas",
    },
    {
        "name": "WebSocket Notes",
        "description": "Édition collaborative de notes en temps réel",
    },
    {
        "name": "WebSocket Projets",
        "description": "Collaboration temps réel sur les projets Kanban",
    },
    {
        "name": "Webhooks",
        "description": "Gestion des webhooks sortants pour notifications externes",
    },
    {
        "name": "Tableau de bord",
        "description": "Dashboard agrégé avec métriques familiales",
    },
    {
        "name": "Batch Cooking",
        "description": "Sessions de batch cooking et préparations",
    },
    {
        "name": "Préférences",
        "description": "Préférences utilisateur (alimentation, robots, magasins)",
    },
    {
        "name": "Anti-Gaspillage",
        "description": "Score anti-gaspillage et recettes de sauvetage",
    },
    {
        "name": "Export",
        "description": "Export PDF de données (courses, planning, recettes, budget)",
    },
    {
        "name": "Utilitaires",
        "description": "Notes, journal, contacts, liens, mots de passe, énergie",
    },
    {
        "name": "Recherche",
        "description": "Recherche globale multi-entités (recettes, projets, activités, notes, contacts)",
    },
    {
        "name": "Documents",
        "description": "Documents familiaux (carnet de santé, assurance, etc.)",
    },
    {
        "name": "Upload",
        "description": "Upload de fichiers vers Supabase Storage",
    },
    {
        "name": "Export Backup",
        "description": "Export de données personnelles (backup) et suppression de compte",
    },
]

app = FastAPI(
    title="Assistant Matanne API",
    lifespan=lifespan,
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
# En production, CORS_ORIGINS DOIT être défini (ex: https://assistant-matanne.vercel.app)
_cors_origins = [
    o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()
]
_default_origins = [
    "http://localhost:3000",  # Next.js dev
    "http://localhost:8000",  # API local
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]
_environment = os.getenv("ENVIRONMENT", "development").lower()

if _cors_origins:
    _allowed_origins = _cors_origins
elif _environment in ("production", "staging"):
    # Fail-fast — refuser de démarrer sans CORS_ORIGINS en prod/staging
    raise RuntimeError(
        f"CORS_ORIGINS non défini en {_environment}. L'application refuse de démarrer. "
        "Définir CORS_ORIGINS avec l'URL du frontend "
        "(ex: CORS_ORIGINS=https://assistant-matanne.vercel.app)."
    )
else:
    _allowed_origins = _default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

app.add_middleware(MiddlewareLimitationDebit)

# Middleware API Versioning
app.add_middleware(VersionMiddleware)

# Middleware ETag pour cache HTTP
app.add_middleware(ETagMiddleware)

# Middleware de métriques
app.add_middleware(MetricsMiddleware)

# Middleware de sécurité HTTP (CSP, HSTS, X-Content-Type-Options, etc.)
app.add_middleware(SecurityHeadersMiddleware)


# Flag atomique in-process pour activation instantanée du mode maintenance.
# Mis à jour directement par l'endpoint admin (pas de délai de cache).
# Le flag DB reste la source de vérité au démarrage / entre redémarrages.
_maintenance_flag: bool = False
_maintenance_loaded: bool = False


def activer_maintenance(enabled: bool) -> None:
    """Active/désactive le mode maintenance instantanément (in-process)."""
    global _maintenance_flag
    _maintenance_flag = enabled


def _lire_mode_maintenance() -> bool:
    """Lit le mode maintenance (flag atomique in-process, chargé depuis DB au premier appel)."""
    global _maintenance_flag, _maintenance_loaded
    if _maintenance_loaded:
        return _maintenance_flag

    # Premier appel : charger depuis la DB
    try:
        from src.api.utils import executer_avec_session
        from src.core.models import EtatPersistantDB

        with executer_avec_session() as session:
            row = (
                session.query(EtatPersistantDB)
                .filter(
                    EtatPersistantDB.namespace == "admin_feature_flags",
                    EtatPersistantDB.user_id == "global",
                )
                .first()
            )
            flags = row.data if row and isinstance(row.data, dict) else {}
            _maintenance_flag = bool(flags.get("admin.maintenance_mode", False))
    except Exception:
        _maintenance_flag = False

    _maintenance_loaded = True
    return _maintenance_flag


@app.middleware("http")
async def maintenance_mode_middleware(request: Request, call_next):
    """Bloque les routes non-admin en mode maintenance avec réponse 503."""
    path = request.url.path
    if request.method == "OPTIONS":
        return await call_next(request)

    prefixes_autorises = (
        "/api/v1/admin",
        "/api/v1/auth",
        "/api/v1/health",
        "/api/v1/status",
        "/api/v1/metrics",
        "/api/v1/prometheus",
        "/docs",
        "/redoc",
        "/openapi.json",
    )
    if any(path.startswith(prefix) for prefix in prefixes_autorises):
        return await call_next(request)

    if path.startswith("/api/") and _lire_mode_maintenance():
        return JSONResponse(
            status_code=503,
            content={"detail": "Maintenance en cours. Veuillez réessayer plus tard."},
        )

    return await call_next(request)


# ═══════════════════════════════════════════════════════════
# GESTIONNAIRE D'EXCEPTIONS GLOBAL
# ═══════════════════════════════════════════════════════════


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Gestionnaire global qui empêche les fuites d'erreurs internes."""
    logger.error(
        f"Exception non gérée sur {request.method} {request.url.path}: {exc}", exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Une erreur interne est survenue. Veuillez réessayer."},
    )


try:
    from fastapi.exceptions import ResponseValidationError

    @app.exception_handler(ResponseValidationError)
    async def response_validation_error_handler(request: Request, exc: ResponseValidationError):
        """Capture les erreurs de sérialisation de réponse (ORM non sérialisé, etc.)"""
        erreurs: list[dict[str, Any]] = []
        try:
            erreurs = list(exc.errors())
        except Exception:
            erreurs = []

        premiere_erreur: dict[str, Any] = erreurs[0] if erreurs else {}
        logger.error(
            (
                "Erreur de validation de réponse sur "
                f"{request.method} {request.url.path} | "
                f"nb_erreurs={len(erreurs)} | premiere_erreur={premiere_erreur}"
            ),
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Erreur de sérialisation de la réponse."},
        )
except ImportError:
    pass


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


@app.get("/health", response_model=HealthResponse, tags=["Santé"], responses=REPONSE_500)
async def health_check():
    """
    Vérifie l'état de l'API et de toutes ses dépendances.

    Utilise SanteSysteme (core/monitoring/health.py) comme source de vérité unique
    pour les health checks (DB, cache, IA, métriques, + checks enregistrés).

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
    # Utiliser SanteSysteme comme source de vérité unique
    rapport = verifier_sante_globale(inclure_db=True)

    # Convertir SanteComposant → ServiceStatus pour le schéma API
    services: dict[str, ServiceStatus] = {}
    _statut_map = {
        StatutSante.SAIN: "ok",
        StatutSante.DEGRADE: "warning",
        StatutSante.CRITIQUE: "error",
        StatutSante.INCONNU: "unknown",
    }

    for nom, composant in rapport.composants.items():
        services[nom] = ServiceStatus(
            status=_statut_map.get(composant.statut, "unknown"),
            latency_ms=round(composant.duree_verification_ms, 2),
            details=composant.message or None,
        )

    # Déterminer le statut global
    if rapport.sain:
        has_degraded = any(c.statut == StatutSante.DEGRADE for c in rapport.composants.values())
        overall = "degraded" if has_degraded else "healthy"
    else:
        overall = "unhealthy"

    uptime = (datetime.now(UTC) - _START_TIME).total_seconds()

    return HealthResponse(
        status=overall,
        version="1.0.0",
        timestamp=datetime.now(UTC),
        services=services,
        uptime_seconds=round(uptime, 1),
    )


@app.get("/status", response_model=HealthResponse, tags=["Santé"], responses=REPONSE_500)
async def status_public():
    """Alias public de `/health` pour les status pages et checks externes."""
    return await health_check()


@app.get("/metrics", tags=["Santé"], responses=REPONSES_AUTH_ADMIN)
async def get_api_metrics(user: dict = Depends(require_role("admin"))):
    """Retourne les métriques de l'API (latence, requêtes, rate limiting).

    Nécessite le rôle admin. Pour le format Prometheus, voir /metrics/prometheus.

    Returns:
        Dict structuré avec uptime, requests, latency, rate_limiting et ai.
    """
    return get_metrics()


# ═══════════════════════════════════════════════════════════
# ENREGISTREMENT DES ROUTERS
# ═══════════════════════════════════════════════════════════


app.include_router(auth_router)
app.include_router(recettes_router)
app.include_router(partage_router)
app.include_router(inventaire_router)
app.include_router(courses_router)
app.include_router(planning_router)
app.include_router(push_router)
app.include_router(webhooks_router)
app.include_router(whatsapp_router)
app.include_router(suggestions_router)

# Nouveaux routers - famille, maison, jeux, calendriers
app.include_router(famille_router)
app.include_router(maison_router)
app.include_router(habitat_router)
app.include_router(assistant_router)
app.include_router(jeux_router)
app.include_router(calendriers_router)

# Nouveaux routers - Phase 2
app.include_router(dashboard_router)
app.include_router(batch_cooking_router)
app.include_router(preferences_router)
app.include_router(automations_router)
app.include_router(anti_gaspillage_router)
app.include_router(ia_avancee_router)
app.include_router(ia_sprint13_router)
app.include_router(fonctionnalites_avancees_router)
app.include_router(export_router)
app.include_router(utilitaires_router)
app.include_router(recherche_router)
app.include_router(voyages_router)
app.include_router(garmin_router)
app.include_router(documents_router)
app.include_router(upload_router)
app.include_router(rgpd_router)

# Prometheus et WebSocket
app.include_router(prometheus_router)
app.include_router(websocket_router)
app.include_router(ws_planning_router)
app.include_router(ws_notes_router)
app.include_router(ws_projets_router)
app.include_router(ws_admin_logs_router)
app.include_router(admin_router)

# IA, Prédictions, Bridges
app.include_router(predictions_router)
app.include_router(ia_bridges_router)
app.include_router(bridges_router)
app.include_router(intra_flux_router)
