"""
Routes API - Package.

Contient tous les routeurs FastAPI organisés par domaine.
"""

from .auth import router as auth_router
from .base import CRUDRouter
from .courses import router as courses_router
from .inventaire import router as inventaire_router
from .planning import router as planning_router
from .recettes import router as recettes_router
from .suggestions import router as suggestions_router

__all__ = [
    "CRUDRouter",
    "auth_router",
    "recettes_router",
    "inventaire_router",
    "courses_router",
    "planning_router",
    "suggestions_router",
]
