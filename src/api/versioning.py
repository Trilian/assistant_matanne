"""
API Versioning - Mécanisme central de versioning pour l'API REST.

Permet de gérer plusieurs versions d'API (v1, v2, etc.) avec:
- Router préfixé centralisé
- Déprécation avec headers Deprecation/Sunset
- Detection de version dans l'URL ou header Accept-Version

Usage:
    from src.api.versioning import creer_router_versionne, API_V1_PREFIX

    router = creer_router_versionne("v1", "Courses")

    # Pour v2 avec breaking changes:
    router_v2 = creer_router_versionne("v2", "Courses")
"""

from datetime import datetime
from enum import StrEnum
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# ═══════════════════════════════════════════════════════════
# CONFIGURATION VERSIONING
# ═══════════════════════════════════════════════════════════


class VersionAPI(StrEnum):
    """Versions supportées de l'API."""

    V1 = "v1"
    V2 = "v2"


# Préfixes centralisés
API_VERSION_ACTUELLE = VersionAPI.V1
API_V1_PREFIX = "/api/v1"
API_V2_PREFIX = "/api/v2"

# Configuration de déprécation (dates futures pour v1)
DEPRECATION_CONFIG: dict[VersionAPI, dict[str, Any]] = {
    VersionAPI.V1: {
        "deprecated": False,
        "sunset_date": None,  # Pas de date de fin pour v1 actuellement
    },
    VersionAPI.V2: {
        "deprecated": False,
        "sunset_date": None,
    },
}

# Versions supportées (ordre: plus récente en premier)
VERSIONS_SUPPORTEES = [VersionAPI.V2, VersionAPI.V1]


# ═══════════════════════════════════════════════════════════
# FACTORY ROUTER
# ═══════════════════════════════════════════════════════════


def creer_router_versionne(
    version: str,
    tag: str,
    domaine: str = "",
) -> APIRouter:
    """
    Crée un router API avec le préfixe de version approprié.

    Args:
        version: Version API ("v1", "v2")
        tag: Tag OpenAPI pour grouper les endpoints
        domaine: Sous-chemin du domaine (ex: "recettes", "courses")

    Returns:
        APIRouter configuré avec le bon préfixe

    Example:
        router = creer_router_versionne("v1", "Courses", "courses")
        # Crée un router avec prefix="/api/v1/courses"
    """
    prefix = f"/api/{version}"
    if domaine:
        prefix = f"{prefix}/{domaine}"

    return APIRouter(prefix=prefix, tags=[tag])


def obtenir_prefix_version(version: VersionAPI | str) -> str:
    """Retourne le préfixe pour une version donnée."""
    if isinstance(version, str):
        version = VersionAPI(version)
    return f"/api/{version.value}"


# ═══════════════════════════════════════════════════════════
# MIDDLEWARE DE VERSION
# ═══════════════════════════════════════════════════════════


class VersionMiddleware(BaseHTTPMiddleware):
    """
    Middleware pour gérer le versioning d'API.

    Fonctionnalités:
    - Détecte la version depuis l'URL ou le header Accept-Version
    - Ajoute les headers de déprécation si nécessaire
    - Refuse les versions non supportées
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path

        # Extraire la version de l'URL
        version = None
        for v in VERSIONS_SUPPORTEES:
            if path.startswith(f"/api/{v.value}"):
                version = v
                break

        # Alternative: header Accept-Version
        if not version:
            header_version = request.headers.get("Accept-Version", "").lower()
            if header_version.startswith("v"):
                try:
                    version = VersionAPI(header_version)
                except ValueError:
                    pass

        # Vérifier si version supportée
        if version and version not in VERSIONS_SUPPORTEES:
            return Response(
                content=f'{{"detail": "Version API \'{version.value}\' non supportée. Utilisez l\'une des versions: {", ".join(v.value for v in VERSIONS_SUPPORTEES)}"}}',
                status_code=400,
                media_type="application/json",
            )

        response = await call_next(request)

        # Ajouter les headers de versioning
        if version:
            response.headers["X-API-Version"] = version.value

            # Headers de déprécation si applicable
            config = DEPRECATION_CONFIG.get(version, {})
            if config.get("deprecated"):
                response.headers["Deprecation"] = "true"
                if sunset := config.get("sunset_date"):
                    response.headers["Sunset"] = (
                        sunset.isoformat() if isinstance(sunset, datetime) else str(sunset)
                    )

        # Header indiquant les versions disponibles
        response.headers["X-API-Versions-Available"] = ", ".join(
            v.value for v in VERSIONS_SUPPORTEES
        )

        return response


# ═══════════════════════════════════════════════════════════
# DEPENDENCY INJECTION
# ═══════════════════════════════════════════════════════════


async def get_api_version(
    request: Request,
    accept_version: str | None = Header(None, alias="Accept-Version"),
) -> VersionAPI:
    """
    Dependency pour obtenir la version API demandée.

    Cherche dans l'ordre:
    1. URL path (/api/v1/, /api/v2/)
    2. Header Accept-Version: v1, v2
    3. Défaut: version actuelle

    Usage:
        @router.get("/items")
        async def get_items(version: VersionAPI = Depends(get_api_version)):
            if version == VersionAPI.V2:
                return {"format": "v2", ...}
            return {"format": "v1", ...}
    """
    path = request.url.path

    # Chercher dans l'URL
    for v in VERSIONS_SUPPORTEES:
        if path.startswith(f"/api/{v.value}"):
            return v

    # Chercher dans le header
    if accept_version:
        clean_version = accept_version.lower().strip()
        if not clean_version.startswith("v"):
            clean_version = f"v{clean_version}"
        try:
            return VersionAPI(clean_version)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Version '{accept_version}' non supportée. Versions disponibles: {', '.join(v.value for v in VERSIONS_SUPPORTEES)}",
            )

    # Défaut
    return API_VERSION_ACTUELLE


# ═══════════════════════════════════════════════════════════
# UTILITAIRES
# ═══════════════════════════════════════════════════════════


def deprecier_version(version: VersionAPI, sunset_date: datetime | None = None) -> None:
    """
    Marque une version comme dépréciée.

    Args:
        version: Version à déprécier
        sunset_date: Date à laquelle la version sera supprimée
    """
    if version in DEPRECATION_CONFIG:
        DEPRECATION_CONFIG[version]["deprecated"] = True
        DEPRECATION_CONFIG[version]["sunset_date"] = sunset_date


def est_version_deprecated(version: VersionAPI) -> bool:
    """Vérifie si une version est dépréciée."""
    return DEPRECATION_CONFIG.get(version, {}).get("deprecated", False)
