"""Routes API - Package.

Les routeurs sont exposes de facon lazy pour eviter de charger tout le graphe
FastAPI lors de l'import d'un seul sous-module de routes.
"""

from __future__ import annotations

__all__ = [
    "assistant_router",
    "admin_router",
    "anti_gaspillage_router",
    "automations_router",
    "auth_router",
    "batch_cooking_router",
    "calendriers_router",
    "courses_router",
    "dashboard_router",
    "dashboard_accueil",
    "documents_router",
    "export_router",
    "rapports_router",
    "famille_router",
    "habitat_router",
    "garmin_router",
    "ia_avancee_router",
    "ia_modules_router",
    "fonctionnalites_avancees_router",
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
    "voyages_router",
    "webhooks_router",
    "predictions_router",
    "ia_bridges_router",
    "bridges_router",
    "intra_flux_router",
]


_MODULES = {
    "assistant_router": ".assistant",
    "admin_router": ".admin",
    "anti_gaspillage_router": ".anti_gaspillage",
    "automations_router": ".automations",
    "auth_router": ".auth",
    "batch_cooking_router": ".batch_cooking",
    "calendriers_router": ".calendriers",
    "courses_router": ".courses",
    "dashboard_router": ".dashboard",
    "documents_router": ".documents",
    "export_router": ".export",
    "rapports_router": ".rapports",
    "famille_router": ".famille",
    "habitat_router": ".habitat",
    "garmin_router": ".garmin",
    "ia_avancee_router": ".ia_avancee",
    "ia_modules_router": ".ia_modules",
    "fonctionnalites_avancees_router": ".innovations",
    "inventaire_router": ".inventaire",
    "jeux_router": ".jeux",
    "maison_router": ".maison",
    "planning_router": ".planning",
    "preferences_router": ".preferences",
    "push_router": ".push",
    "recettes_router": ".recettes",
    "recherche_router": ".recherche",
    "suggestions_router": ".suggestions",
    "upload_router": ".upload",
    "utilitaires_router": ".utilitaires",
    "voyages_router": ".voyages",
    "webhooks_router": ".webhooks",
    "predictions_router": ".predictions",
    "ia_bridges_router": ".ia_bridges",
    "bridges_router": ".bridges",
    "intra_flux_router": ".intra_flux",
}

_MODULE_ALIASES = {
    "dashboard_accueil": ".dashboard",
}


def __getattr__(name: str):
    if name in _MODULES:
        from importlib import import_module

        module = import_module(_MODULES[name], __name__)
        return module.router
    if name in _MODULE_ALIASES:
        from importlib import import_module

        return import_module(_MODULE_ALIASES[name], __name__)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
