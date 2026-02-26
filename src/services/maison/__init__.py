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
    # CRUD services
    "DepensesCrudService": "depenses_crud_service",
    "get_depenses_crud_service": "depenses_crud_service",
    "obtenir_service_depenses_crud": "depenses_crud_service",
    "HubDataService": "hub_data_service",
    "get_hub_data_service": "hub_data_service",
    "obtenir_service_hub_data": "hub_data_service",
    # NEW: Meubles CRUD service
    "MeublesCrudService": "meubles_crud_service",
    "get_meubles_crud_service": "meubles_crud_service",
    "obtenir_service_meubles_crud": "meubles_crud_service",
    # NEW: Eco Tips CRUD service
    "EcoTipsCrudService": "eco_tips_crud_service",
    "get_eco_tips_crud_service": "eco_tips_crud_service",
    "obtenir_service_eco_tips_crud": "eco_tips_crud_service",
    # NEW: Contrats CRUD service
    "ContratsCrudService": "contrats_crud_service",
    "get_contrats_service": "contrats_crud_service",
    # NEW: Artisans CRUD service
    "ArtisansCrudService": "artisans_crud_service",
    "get_artisans_service": "artisans_crud_service",
    # NEW: Garanties CRUD service
    "GarantiesCrudService": "garanties_crud_service",
    "get_garanties_service": "garanties_crud_service",
    # NEW: Cellier CRUD service
    "CellierCrudService": "cellier_crud_service",
    "get_cellier_service": "cellier_crud_service",
    # NEW: Checklists CRUD service
    "ChecklistsCrudService": "checklists_crud_service",
    "get_checklists_service": "checklists_crud_service",
    # NEW: Diagnostics & Estimations CRUD services
    "DiagnosticsCrudService": "diagnostics_crud_service",
    "get_diagnostics_service": "diagnostics_crud_service",
    "EstimationsCrudService": "diagnostics_crud_service",
    "get_estimations_service": "diagnostics_crud_service",
    # NEW: Extensions CRUD services (nuisibles, devis, entretien saisonnier, relevés)
    "NuisiblesCrudService": "extensions_crud_service",
    "get_nuisibles_service": "extensions_crud_service",
    "DevisCrudService": "extensions_crud_service",
    "get_devis_service": "extensions_crud_service",
    "EntretienSaisonnierCrudService": "extensions_crud_service",
    "get_entretien_saisonnier_service": "extensions_crud_service",
    "RelevesCrudService": "extensions_crud_service",
    "get_releves_service": "extensions_crud_service",
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
    from .artisans_crud_service import ArtisansCrudService, get_artisans_service
    from .cellier_crud_service import CellierCrudService, get_cellier_service
    from .checklists_crud_service import ChecklistsCrudService, get_checklists_service
    from .contrats_crud_service import ContratsCrudService, get_contrats_service
    from .diagnostics_crud_service import (
        DiagnosticsCrudService,
        EstimationsCrudService,
        get_diagnostics_service,
        get_estimations_service,
    )
    from .eco_tips_crud_service import (
        EcoTipsCrudService,
        get_eco_tips_crud_service,
        obtenir_service_eco_tips_crud,
    )
    from .entretien_service import (
        EntretienService,
        get_entretien_service,
        obtenir_service_entretien,
    )
    from .extensions_crud_service import (
        DevisCrudService,
        EntretienSaisonnierCrudService,
        NuisiblesCrudService,
        RelevesCrudService,
        get_devis_service,
        get_entretien_saisonnier_service,
        get_nuisibles_service,
        get_releves_service,
    )
    from .jardin_service import JardinService, get_jardin_service, obtenir_service_jardin
    from .meubles_crud_service import (
        MeublesCrudService,
        get_meubles_crud_service,
        obtenir_service_meubles_crud,
    )
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
    # CRUD services
    "DepensesCrudService",
    "get_depenses_crud_service",
    "obtenir_service_depenses_crud",
    "HubDataService",
    "get_hub_data_service",
    "obtenir_service_hub_data",
    # NEW: Meubles CRUD service
    "MeublesCrudService",
    "get_meubles_crud_service",
    "obtenir_service_meubles_crud",
    # NEW: Eco Tips CRUD service
    "EcoTipsCrudService",
    "get_eco_tips_crud_service",
    "obtenir_service_eco_tips_crud",
    # NEW: Contrats, Artisans, Garanties, Cellier, Checklists
    "ContratsCrudService",
    "get_contrats_service",
    "ArtisansCrudService",
    "get_artisans_service",
    "GarantiesCrudService",
    "get_garanties_service",
    "CellierCrudService",
    "get_cellier_service",
    "ChecklistsCrudService",
    "get_checklists_service",
    # NEW: Diagnostics & Estimations
    "DiagnosticsCrudService",
    "get_diagnostics_service",
    "EstimationsCrudService",
    "get_estimations_service",
    # NEW: Extensions (nuisibles, devis, entretien saisonnier, releves)
    "NuisiblesCrudService",
    "get_nuisibles_service",
    "DevisCrudService",
    "get_devis_service",
    "EntretienSaisonnierCrudService",
    "get_entretien_saisonnier_service",
    "RelevesCrudService",
    "get_releves_service",
]
