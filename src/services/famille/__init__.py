"""Package famille - Services calendrier, budget, routines, activités, achats, weekend, suivi perso, jules, santé,
carnet_sante, contacts, anniversaires, evenements, voyage, documents, soiree_ai.

Imports paresseux pour éviter les imports circulaires.
Importez directement depuis les sous-packages:

    from src.services.famille.calendrier import obtenir_calendar_sync_service
    from src.services.famille.budget import CategorieDepense
    from src.services.famille.routines import obtenir_service_routines
    from src.services.famille.activites import obtenir_service_activites
    from src.services.famille.achats import obtenir_service_achats_famille
    from src.services.famille.weekend import obtenir_service_weekend
    from src.services.famille.suivi_perso import obtenir_service_suivi_perso
    from src.services.famille.jules import obtenir_service_jules
    from src.services.famille.sante import obtenir_service_sante
    from src.services.famille.carnet_sante import obtenir_service_carnet_sante
    from src.services.famille.contacts import obtenir_service_contacts
    from src.services.famille.anniversaires import obtenir_service_anniversaires
    from src.services.famille.evenements import obtenir_service_evenements
    from src.services.famille.voyage import obtenir_service_voyage
    from src.services.famille.documents import obtenir_service_documents
    from src.services.famille.soiree_ai import obtenir_service_soiree_ai
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
    "jules_ai",
    "weekend_ai",
    "carnet_sante",
    "contacts",
    "anniversaires",
    "evenements",
    "voyage",
    "documents",
    "soiree_ai",
    "contexte",
    "rappels",
    "achats_ia",
    "checklists_anniversaire",
    "service_ia",
]


def __getattr__(name: str):
    """Lazy import pour éviter les imports circulaires."""
    if name == "obtenir_calendar_sync_service":
        from src.services.famille.calendrier import obtenir_calendar_sync_service

        return obtenir_calendar_sync_service
    if name == "CategorieDepense":
        from src.services.famille.budget import CategorieDepense

        return CategorieDepense
    if name in ("obtenir_service_routines", "obtenir_service_routines"):
        from src.services.famille.routines import obtenir_service_routines

        return obtenir_service_routines
    if name in ("obtenir_service_activites", "obtenir_service_activites"):
        from src.services.famille.activites import obtenir_service_activites

        return obtenir_service_activites
    if name in ("obtenir_service_achats_famille", "obtenir_service_achats_famille"):
        from src.services.famille.achats import obtenir_service_achats_famille

        return obtenir_service_achats_famille
    if name in ("obtenir_service_weekend", "obtenir_service_weekend"):
        from src.services.famille.weekend import obtenir_service_weekend

        return obtenir_service_weekend
    if name in ("obtenir_service_suivi_perso", "obtenir_service_suivi_perso"):
        from src.services.famille.suivi_perso import obtenir_service_suivi_perso

        return obtenir_service_suivi_perso
    if name in ("obtenir_service_jules", "obtenir_service_jules"):
        from src.services.famille.jules import obtenir_service_jules

        return obtenir_service_jules
    if name in ("obtenir_service_sante", "obtenir_service_sante"):
        from src.services.famille.sante import obtenir_service_sante

        return obtenir_service_sante
    if name in ("obtenir_service_calendrier_planning", "obtenir_calendrier_planning_service"):
        from src.services.famille.calendrier_planning import (
            obtenir_service_calendrier_planning,
        )

        return obtenir_service_calendrier_planning
    if name in ("obtenir_service_carnet_sante", "obtenir_service_carnet_sante"):
        from src.services.famille.carnet_sante import obtenir_service_carnet_sante

        return obtenir_service_carnet_sante
    if name in ("obtenir_service_contacts", "obtenir_service_contacts"):
        from src.services.famille.contacts import obtenir_service_contacts

        return obtenir_service_contacts
    if name in ("obtenir_service_anniversaires", "obtenir_service_anniversaires"):
        from src.services.famille.anniversaires import obtenir_service_anniversaires

        return obtenir_service_anniversaires
    if name in ("obtenir_service_evenements", "obtenir_service_evenements"):
        from src.services.famille.evenements import obtenir_service_evenements

        return obtenir_service_evenements
    if name in ("obtenir_service_voyage", "obtenir_service_voyage"):
        from src.services.famille.voyage import obtenir_service_voyage

        return obtenir_service_voyage
    if name in ("obtenir_service_documents", "obtenir_service_documents"):
        from src.services.famille.documents import obtenir_service_documents

        return obtenir_service_documents
    if name in ("obtenir_service_soiree_ai", "obtenir_service_soiree_ai"):
        from src.services.famille.soiree_ai import obtenir_service_soiree_ai

        return obtenir_service_soiree_ai
    if name == "obtenir_service_innovations_famille":
        from src.services.famille.service_ia import obtenir_service_innovations_famille

        return obtenir_service_innovations_famille
    if name in ("obtenir_service_contexte_familial", "obtenir_service_contexte_familial"):
        from src.services.famille.contexte import obtenir_service_contexte_familial

        return obtenir_service_contexte_familial
    if name in ("obtenir_service_rappels_famille", "obtenir_service_rappels_famille"):
        from src.services.famille.rappels import obtenir_service_rappels_famille

        return obtenir_service_rappels_famille
    if name in ("obtenir_service_achats_ia", "obtenir_service_achats_ia"):
        from src.services.famille.achats_ia import obtenir_service_achats_ia

        return obtenir_service_achats_ia
    if name in ("obtenir_service_checklists_anniversaire", "get_checklists_anniversaire_service"):
        from src.services.famille.checklists_anniversaire import (
            obtenir_service_checklists_anniversaire,
        )

        return obtenir_service_checklists_anniversaire
    if name == "obtenir_service_documents_notifications":
        from src.services.famille.inter_module_documents_notifications import (
            obtenir_service_documents_notifications,
        )

        return obtenir_service_documents_notifications
    if name == "obtenir_service_anniversaires_budget_interaction":
        from src.services.famille.inter_module_anniversaires_budget import (
            obtenir_service_anniversaires_budget_interaction,
        )

        return obtenir_service_anniversaires_budget_interaction
    if name == "obtenir_service_voyages_budget_interaction":
        from src.services.famille.inter_module_voyages_budget import (
            obtenir_service_voyages_budget_interaction,
        )

        return obtenir_service_voyages_budget_interaction
    if name == "obtenir_service_meteo_activites_interaction":
        from src.services.famille.inter_module_meteo_activites import (
            obtenir_service_meteo_activites_interaction,
        )

        return obtenir_service_meteo_activites_interaction
    if name == "obtenir_service_weekend_courses_interaction":
        from src.services.famille.inter_module_weekend_courses import (
            obtenir_service_weekend_courses_interaction,
        )

        return obtenir_service_weekend_courses_interaction
    if name == "obtenir_service_documents_calendrier_interaction":
        from src.services.famille.inter_module_documents_calendrier import (
            obtenir_service_documents_calendrier_interaction,
        )

        return obtenir_service_documents_calendrier_interaction
    raise AttributeError(f"module 'src.services.famille' has no attribute '{name}'")

