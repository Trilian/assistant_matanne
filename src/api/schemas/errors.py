"""
Constantes de réponses d'erreur OpenAPI.

Dictionnaires réutilisables pour documenter les erreurs 4xx/5xx
dans les décorateurs de routes FastAPI via le paramètre `responses=`.

Usage:
    from src.api.schemas.errors import REPONSES_AUTH, REPONSES_NOT_FOUND, combiner_reponses

    @router.get("/{id}", responses=combiner_reponses(REPONSES_AUTH, REPONSES_NOT_FOUND))
    async def get_item(id: int): ...
"""

from __future__ import annotations

from typing import Any

from .common import ErrorResponse

# ═══════════════════════════════════════════════════════════
# RÉPONSES D'ERREUR RÉUTILISABLES
# ═══════════════════════════════════════════════════════════

REPONSE_401: dict[int, dict[str, Any]] = {
    401: {
        "description": "Non authentifié — Token JWT manquant ou invalide",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {"detail": "Token invalide ou expiré"},
            }
        },
    },
}

REPONSE_403: dict[int, dict[str, Any]] = {
    403: {
        "description": "Accès interdit — Rôle insuffisant",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {"detail": "Rôle 'admin' requis"},
            }
        },
    },
}

REPONSE_404: dict[int, dict[str, Any]] = {
    404: {
        "description": "Ressource non trouvée",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {"detail": "Ressource non trouvée"},
            }
        },
    },
}

REPONSE_422: dict[int, dict[str, Any]] = {
    422: {
        "description": "Données invalides — Erreur de validation",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {"detail": "Aucun champ à mettre à jour fourni"},
            }
        },
    },
}

REPONSE_429: dict[int, dict[str, Any]] = {
    429: {
        "description": "Trop de requêtes — Limitation de débit dépassée",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {"detail": "Trop de tentatives. Réessayez plus tard."},
            }
        },
    },
}

REPONSE_500: dict[int, dict[str, Any]] = {
    500: {
        "description": "Erreur interne du serveur",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {"detail": "Une erreur interne est survenue. Veuillez réessayer."},
            }
        },
    },
}

REPONSE_503: dict[int, dict[str, Any]] = {
    503: {
        "description": "Service temporairement indisponible",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {"detail": "Service temporairement indisponible"},
            }
        },
    },
}


# ═══════════════════════════════════════════════════════════
# COMBINAISONS COURANTES
# ═══════════════════════════════════════════════════════════

REPONSES_AUTH = {**REPONSE_401}
"""Endpoints nécessitant une authentification."""

REPONSES_AUTH_ADMIN = {**REPONSE_401, **REPONSE_403}
"""Endpoints nécessitant un rôle admin."""

REPONSES_CRUD_LECTURE = {**REPONSE_401, **REPONSE_404}
"""Endpoints GET sur une ressource unique (auth + 404)."""

REPONSES_CRUD_ECRITURE = {**REPONSE_401, **REPONSE_404, **REPONSE_422}
"""Endpoints PUT/PATCH sur une ressource (auth + 404 + validation)."""

REPONSES_CRUD_CREATION = {**REPONSE_401, **REPONSE_422}
"""Endpoints POST de création (auth + validation)."""

REPONSES_CRUD_SUPPRESSION = {**REPONSE_401, **REPONSE_404}
"""Endpoints DELETE (auth + 404)."""

REPONSES_LISTE = {**REPONSE_401}
"""Endpoints GET de listing paginé (auth seulement)."""

REPONSES_IA = {**REPONSE_401, **REPONSE_429, **REPONSE_503}
"""Endpoints IA avec rate limiting et dépendance externe."""

REPONSES_AUTH_LOGIN = {**REPONSE_401, **REPONSE_429, **REPONSE_503}
"""Endpoint login (brute-force protection + Supabase)."""


def combiner_reponses(*dicts: dict[int, dict[str, Any]]) -> dict[int, dict[str, Any]]:
    """Combine plusieurs dictionnaires de réponses d'erreur.

    Args:
        *dicts: Dictionnaires de réponses à fusionner.

    Returns:
        Dictionnaire combiné avec tous les status codes.

    Example:
        >>> combiner_reponses(REPONSES_AUTH, REPONSE_404, REPONSE_429)
        {401: {...}, 404: {...}, 429: {...}}
    """
    result: dict[int, dict[str, Any]] = {}
    for d in dicts:
        result.update(d)
    return result
