"""Package famille - Services calendrier, budget, routines, activités, achats, weekend, suivi perso, jules et santé.

Imports paresseux pour éviter les imports circulaires.
Importez directement depuis les sous-packages:

    from src.services.famille.calendrier import get_calendar_sync_service
    from src.services.famille.budget import CategorieDepense
    from src.services.famille.routines import obtenir_service_routines
    from src.services.famille.activites import obtenir_service_activites
    from src.services.famille.achats import obtenir_service_achats_famille
    from src.services.famille.weekend import obtenir_service_weekend
    from src.services.famille.suivi_perso import obtenir_service_suivi_perso
    from src.services.famille.jules import obtenir_service_jules
    from src.services.famille.sante import obtenir_service_sante
"""

__all__ = [
    "calendrier",
    "budget",
    "routines",
    "activites",
    "achats",
    "weekend",
    "suivi_perso",
    "jules",
    "sante",
    "calendrier_planning",
]


def __getattr__(name: str):
    """Lazy import pour éviter les imports circulaires."""
    if name == "get_calendar_sync_service":
        from src.services.famille.calendrier import get_calendar_sync_service

        return get_calendar_sync_service
    if name == "CategorieDepense":
        from src.services.famille.budget import CategorieDepense

        return CategorieDepense
    if name in ("obtenir_service_routines", "get_routines_service"):
        from src.services.famille.routines import obtenir_service_routines

        return obtenir_service_routines
    if name in ("obtenir_service_activites", "get_activites_service"):
        from src.services.famille.activites import obtenir_service_activites

        return obtenir_service_activites
    if name in ("obtenir_service_achats_famille", "get_achats_famille_service"):
        from src.services.famille.achats import obtenir_service_achats_famille

        return obtenir_service_achats_famille
    if name in ("obtenir_service_weekend", "get_weekend_service"):
        from src.services.famille.weekend import obtenir_service_weekend

        return obtenir_service_weekend
    if name in ("obtenir_service_suivi_perso", "get_suivi_perso_service"):
        from src.services.famille.suivi_perso import obtenir_service_suivi_perso

        return obtenir_service_suivi_perso
    if name in ("obtenir_service_jules", "get_jules_service"):
        from src.services.famille.jules import obtenir_service_jules

        return obtenir_service_jules
    if name in ("obtenir_service_sante", "get_sante_service"):
        from src.services.famille.sante import obtenir_service_sante

        return obtenir_service_sante
    if name in ("obtenir_service_calendrier_planning", "get_calendrier_planning_service"):
        from src.services.famille.calendrier_planning import (
            obtenir_service_calendrier_planning,
        )

        return obtenir_service_calendrier_planning
    raise AttributeError(f"module 'src.services.famille' has no attribute '{name}'")
