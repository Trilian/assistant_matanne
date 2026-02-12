"""
Routes API - Package.

Contient tous les routeurs FastAPI organisés par domaine.
"""

from .recettes import router as recettes_router
from .inventaire import router as inventaire_router
from .courses import router as courses_router
from .planning import router as planning_router

__all__ = [
    "recettes_router",
    "inventaire_router",
    "courses_router",
    "planning_router",
]
