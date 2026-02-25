"""
Events - Bus d'événements domaine pour découplage inter-services.

Bus synchrone in-process adapté à une app Streamlit mono-processus.
Les services publient des événements au lieu de s'appeler entre eux.

Architecture:
    ServicePlanning → publie RecettePlanifiee → ServiceCourses écoute
    ServiceInventaire → publie StockModifie → Notifications écoute

Usage:
    from src.services.core.events import obtenir_bus, EvenementDomaine

    # Souscrire
    bus = obtenir_bus()
    bus.souscrire("recette.planifiee", on_recette_planifiee)

    # Émettre
    bus.emettre("recette.planifiee", {"recette_id": 42, "date": "2026-02-20"})
"""

from .bus import (
    BusEvenements,
    EvenementDomaine,
    HandlerEvenement,
    obtenir_bus,
)
from .events import (
    # Événements métier
    EvenementBatchCookingTermine,
    EvenementBudgetModifie,
    EvenementCoursesGenerees,
    EvenementErreurService,
    EvenementLotoModifie,
    EvenementParisModifie,
    EvenementRecetteImportee,
    EvenementRecettePlanifiee,
    EvenementSanteModifie,
    EvenementStockModifie,
)
from .subscribers import enregistrer_subscribers

__all__ = [
    # Bus
    "BusEvenements",
    "EvenementDomaine",
    "HandlerEvenement",
    "obtenir_bus",
    # Événements
    "EvenementRecettePlanifiee",
    "EvenementStockModifie",
    "EvenementCoursesGenerees",
    "EvenementRecetteImportee",
    "EvenementBatchCookingTermine",
    "EvenementBudgetModifie",
    "EvenementSanteModifie",
    "EvenementLotoModifie",
    "EvenementParisModifie",
    "EvenementErreurService",
    # Subscribers
    "enregistrer_subscribers",
]
