"""
Services Maison - Gestion intelligente de la maison et du jardin.

Ce package regroupe tous les services pour:
- Jardin: conseils IA, météo, arrosage intelligent
- Entretien: routines ménage, planification IA
- Projets: estimation, pipeline achats/budget

Architecture:
    services/maison/
    ├── schemas.py              # Pydantic models
    ├── jardin_service.py       # JardinService + JardinierIA
    ├── entretien_service.py    # EntretienService + CalendrierIA
    └── projets_service.py      # ProjetsService + EstimateurIA
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
    # Factories (anglais)
    "get_jardin_service": "jardin_service",
    "get_entretien_service": "entretien_service",
    "get_projets_service": "projets_service",
    # Factories (français)
    "obtenir_service_jardin": "jardin_service",
    "obtenir_service_entretien": "entretien_service",
    "obtenir_service_projets": "projets_service",
    # Constantes gamification
    "BADGES_JARDIN": "jardin_gamification_mixin",
    "BADGES_ENTRETIEN": "entretien_gamification_mixin",
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
    "ZoneJardinCreate": "schemas",
    "PlanteCreate": "schemas",
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
    from .entretien_service import (
        EntretienService,
        get_entretien_service,
        obtenir_service_entretien,
    )
    from .jardin_service import JardinService, get_jardin_service, obtenir_service_jardin
    from .projets_service import ProjetsService, get_projets_service, obtenir_service_projets
    from .schemas import (
        AlerteMaison,
        BriefingMaison,
        ConseilJardin,
        PlanArrosage,
        PlanteCreate,
        ProjetCreate,
        ProjetEstimation,
        RoutineCreate,
        ZoneJardinCreate,
    )

__all__ = [
    # Services
    "JardinService",
    "EntretienService",
    "ProjetsService",
    # Factories (anglais)
    "get_jardin_service",
    "get_entretien_service",
    "get_projets_service",
    # Factories (français)
    "obtenir_service_jardin",
    "obtenir_service_entretien",
    "obtenir_service_projets",
    # Schemas
    "BriefingMaison",
    "AlerteMaison",
    "ConseilJardin",
    "PlanArrosage",
    "RoutineCreate",
    "ProjetCreate",
    "ProjetEstimation",
    "ZoneJardinCreate",
    "PlanteCreate",
    # Constantes
    "BADGES_JARDIN",
    "BADGES_ENTRETIEN",
]
