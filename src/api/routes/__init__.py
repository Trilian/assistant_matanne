"""
Routes API - Package.

Contient tous les routeurs FastAPI organisés par domaine.
"""

from .auth import router as auth_router
from .calendriers import router as calendriers_router
from .courses import router as courses_router
from .famille import router as famille_router
from .inventaire import router as inventaire_router
from .jeux import router as jeux_router
from .maison import router as maison_router
from .planning import router as planning_router
from .push import router as push_router
from .recettes import router as recettes_router
from .suggestions import router as suggestions_router

__all__ = [
    "auth_router",
    "calendriers_router",
    "courses_router",
    "famille_router",
    "inventaire_router",
    "jeux_router",
    "maison_router",
    "planning_router",
    "push_router",
    "recettes_router",
    "suggestions_router",
]
