"""
Services Maison - Gestion intelligente de la maison et du jardin.

Ce package regroupe tous les services pour:
- Jardin: conseils IA, météo, arrosage intelligent
- Entretien: routines ménage, planification IA
- Projets: estimation, pipeline achats/budget
- Énergie: analyse conso, éco-score gamifié
- Inventaire: pièces, objets, recherche "où est..."
- Assistant: briefing quotidien, orchestration

Architecture:
    services/maison/
    ├── schemas.py          # Pydantic models
    ├── jardin_service.py   # JardinService + JardinierIA
    ├── entretien_service.py # EntretienService + CalendrierIA
    ├── projets_service.py  # ProjetsService + EstimateurIA
    ├── energie_service.py  # EnergieService + EcoScore
    ├── inventaire_service.py # InventaireMaisonService
    ├── plan_jardin_service.py # PlanJardinService
    ├── assistant_ia.py     # MaisonAssistantIA (orchestrateur)
    └── integration_service.py # Pipelines inter-modules
"""

from typing import TYPE_CHECKING

# ═══════════════════════════════════════════════════════════
# LAZY LOADING pour performance au démarrage
# ═══════════════════════════════════════════════════════════

_SERVICES = {
    # Services principaux
    "JardinService": "jardin_service",
    "EntretienService": "entretien_service",
    "ProjetsService": "projets_service",
    "EnergieService": "energie_service",
    "InventaireMaisonService": "inventaire_service",
    "PlanJardinService": "plan_jardin_service",
    "MaisonAssistantIA": "assistant_ia",
    "TempsEntretienService": "temps_entretien_service",
    # Factories (anglais)
    "get_jardin_service": "jardin_service",
    "get_entretien_service": "entretien_service",
    "get_projets_service": "projets_service",
    "get_energie_service": "energie_service",
    "get_inventaire_service": "inventaire_service",
    "get_plan_jardin_service": "plan_jardin_service",
    "get_maison_assistant": "assistant_ia",
    "get_temps_entretien_service": "temps_entretien_service",
    # Factories (français)
    "obtenir_service_jardin": "jardin_service",
    "obtenir_service_entretien": "entretien_service",
    "obtenir_service_projets": "projets_service",
    "obtenir_service_energie": "energie_service",
    "obtenir_service_inventaire_maison": "inventaire_service",
    "obtenir_service_plan_jardin": "plan_jardin_service",
    "obtenir_service_temps_entretien": "temps_entretien_service",
}

_SCHEMAS = {
    # Schemas Pydantic
    "BriefingMaison": "schemas",
    "AlerteMaison": "schemas",
    "ConseilJardin": "schemas",
    "PlanArrosage": "schemas",
    "RoutineCreate": "schemas",
    "ProjetCreate": "schemas",
    "ProjetEstimation": "schemas",
    "EcoScoreResult": "schemas",
    "PieceCreate": "schemas",
    "ObjetCreate": "schemas",
    "ZoneJardinCreate": "schemas",
    "PlanteCreate": "schemas",
    "ResultatRecherche": "schemas",
}


def __getattr__(name: str):
    """Lazy loading des services et schemas."""
    if name in _SERVICES:
        module_name = _SERVICES[name]
        module = __import__(f"src.services.maison.{module_name}", fromlist=[name])
        return getattr(module, name)

    if name in _SCHEMAS:
        module_name = _SCHEMAS[name]
        module = __import__(f"src.services.maison.{module_name}", fromlist=[name])
        return getattr(module, name)

    raise AttributeError(f"module 'src.services.maison' has no attribute '{name}'")


def __dir__():
    """Liste tous les exports disponibles."""
    return list(_SERVICES.keys()) + list(_SCHEMAS.keys())


# Type hints pour IDE sans charger les modules
if TYPE_CHECKING:
    from .assistant_ia import MaisonAssistantIA, get_maison_assistant
    from .energie_service import EnergieService, get_energie_service, obtenir_service_energie
    from .entretien_service import (
        EntretienService,
        get_entretien_service,
        obtenir_service_entretien,
    )
    from .inventaire_service import (
        InventaireMaisonService,
        get_inventaire_service,
        obtenir_service_inventaire_maison,
    )
    from .jardin_service import JardinService, get_jardin_service, obtenir_service_jardin
    from .plan_jardin_service import (
        PlanJardinService,
        get_plan_jardin_service,
        obtenir_service_plan_jardin,
    )
    from .projets_service import ProjetsService, get_projets_service, obtenir_service_projets
    from .schemas import (
        AlerteMaison,
        BriefingMaison,
        ConseilJardin,
        EcoScoreResult,
        ObjetCreate,
        PieceCreate,
        PlanArrosage,
        PlanteCreate,
        ProjetCreate,
        ProjetEstimation,
        ResultatRecherche,
        RoutineCreate,
        ZoneJardinCreate,
    )
    from .temps_entretien_service import (
        TempsEntretienService,
        get_temps_entretien_service,
        obtenir_service_temps_entretien,
    )

__all__ = [
    # Services
    "JardinService",
    "EntretienService",
    "ProjetsService",
    "EnergieService",
    "InventaireMaisonService",
    "PlanJardinService",
    "MaisonAssistantIA",
    "TempsEntretienService",
    # Factories (anglais)
    "get_jardin_service",
    "get_entretien_service",
    "get_projets_service",
    "get_energie_service",
    "get_inventaire_service",
    "get_plan_jardin_service",
    "get_maison_assistant",
    "get_temps_entretien_service",
    # Factories (français)
    "obtenir_service_jardin",
    "obtenir_service_entretien",
    "obtenir_service_projets",
    "obtenir_service_energie",
    "obtenir_service_inventaire_maison",
    "obtenir_service_plan_jardin",
    "obtenir_service_temps_entretien",
    # Schemas
    "BriefingMaison",
    "AlerteMaison",
    "ConseilJardin",
    "PlanArrosage",
    "RoutineCreate",
    "ProjetCreate",
    "ProjetEstimation",
    "EcoScoreResult",
    "PieceCreate",
    "ObjetCreate",
    "ZoneJardinCreate",
    "PlanteCreate",
    "ResultatRecherche",
]
