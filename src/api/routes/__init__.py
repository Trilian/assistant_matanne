"""
Routes API - Package.

Contient tous les routeurs FastAPI organisés par domaine.
"""

from .anti_gaspillage import router as anti_gaspillage_router
from .auth import router as auth_router
from .batch_cooking import router as batch_cooking_router
from .calendriers import router as calendriers_router
from .courses import router as courses_router
from .dashboard import router as dashboard_router
from .documents import router as documents_router
from .export import router as export_router
from .famille import router as famille_router
from .inventaire import router as inventaire_router
from .jeux import router as jeux_router
from .maison import router as maison_router
from .planning import router as planning_router
from .preferences import router as preferences_router
from .push import router as push_router
from .recettes import router as recettes_router
from .recherche import router as recherche_router
from .suggestions import router as suggestions_router
from .upload import router as upload_router
from .utilitaires import router as utilitaires_router
from .webhooks import router as webhooks_router

__all__ = [
    "anti_gaspillage_router",
    "auth_router",
    "batch_cooking_router",
    "calendriers_router",
    "courses_router",
    "dashboard_router",
    "documents_router",
    "export_router",

    "famille_router",
    "inventaire_router",
    "jeux_router",
    "maison_router",
    "planning_router",
    "preferences_router",
    "push_router",
    "recettes_router",
    "recherche_router",
    "suggestions_router",
    "upload_router",
    "utilitaires_router",
    "webhooks_router",
]
