"""Utilitaires partagés pour les routeurs d'innovations."""

from __future__ import annotations

from typing import Any, cast

from fastapi import APIRouter

from src.api.schemas.errors import REPONSES_IA

RESPONSES_IA_TYPED = cast(dict[int | str, dict[str, Any]], REPONSES_IA)


def creer_router_innovations(*tags: str) -> APIRouter:
    """Construit un routeur FastAPI standardisé pour les innovations."""
    return APIRouter(prefix="/api/v1/innovations", tags=list(tags) or ["Innovations"])


def get_innovations_service():
    """Charge paresseusement le service d'innovations pour éviter les imports coûteux."""
    from src.services.experimental import get_innovations_service

    return get_innovations_service()
