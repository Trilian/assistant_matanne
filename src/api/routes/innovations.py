"""Agrège les routeurs d'innovations comme couche de compatibilité rétrocompatible."""

from __future__ import annotations

from fastapi import APIRouter

from .innovations_cuisine import router as innovations_cuisine_router
from .innovations_energie import router as innovations_energie_router
from .innovations_famille import router as innovations_famille_router
from .innovations_intelligence import router as innovations_intelligence_router
from .innovations_pratiques import router as innovations_pratiques_router
from .innovations_rapports import router as innovations_rapports_router

router = APIRouter()

for sous_routeur in (
    innovations_cuisine_router,
    innovations_energie_router,
    innovations_famille_router,
    innovations_intelligence_router,
    innovations_pratiques_router,
    innovations_rapports_router,
):
    router.include_router(sous_routeur)
