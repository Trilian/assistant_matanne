"""
Services Maison - Gestion intelligente de la maison et du jardin.

Ce package regroupe tous les services pour:
- Jardin: conseils IA, météo, arrosage intelligent
- Entretien: routines ménage, planification IA
- Projets: estimation, pipeline achats/budget

Architecture:
    services/maison/
    +-- schemas.py              # Pydantic models
    +-- jardin_service.py       # JardinService + JardinierIA
    +-- entretien_service.py    # EntretienService + CalendrierIA
    +-- projets_service.py      # ProjetsService + EstimateurIA
    +-- crud/                   # Services CRUD autonomes
    +-- ia/                     # Services IA spécialisés
    +-- inter_modules/          # Bridges inter-modules
"""

from typing import TYPE_CHECKING

# -----------------------------------------------------------
# LAZY LOADING pour performance au démarrage
# -----------------------------------------------------------

_SERVICES = {
    # Services principaux
    "JardinService": "jardin_service",
    "EntretienService": "entretien_service",
    "ProjetsService": "projets_service",
    # Factories (anglais)
    "obtenir_jardin_service": "jardin_service",
    "obtenir_entretien_service": "entretien_service",
    "obtenir_projets_service": "projets_service",
    # Factories (français)
    "obtenir_service_jardin": "jardin_service",
    "obtenir_service_entretien": "entretien_service",
    "obtenir_service_projets": "projets_service",
    # CRUD services → crud/
    "DepensesCrudService": "crud.depenses_crud_service",
    "obtenir_depenses_crud_service": "crud.depenses_crud_service",
    "obtenir_depenses_crud_service": "crud.depenses_crud_service",
    "obtenir_service_depenses_crud": "crud.depenses_crud_service",
    "HubDataService": "hub_data_service",
    "obtenir_hub_data_service": "hub_data_service",
    "obtenir_service_hub_data": "hub_data_service",
    # Meubles CRUD service → crud/
    "MeublesCrudService": "crud.meubles_crud_service",
    "obtenir_meubles_crud_service": "crud.meubles_crud_service",
    "obtenir_service_meubles_crud": "crud.meubles_crud_service",
    # Eco Tips CRUD service → crud/
    "EcoTipsCrudService": "crud.eco_tips_crud_service",
    "obtenir_eco_tips_crud_service": "crud.eco_tips_crud_service",
    "obtenir_service_eco_tips_crud": "crud.eco_tips_crud_service",
    # Artisans CRUD service → crud/
    "ArtisansCrudService": "crud.artisans_crud_service",
    "obtenir_artisans_crud_service": "crud.artisans_crud_service",
    "obtenir_service_artisans_crud": "crud.artisans_crud_service",
    # Cellier CRUD service → crud/
    "CellierCrudService": "crud.cellier_crud_service",
    "obtenir_cellier_crud_service": "crud.cellier_crud_service",
    "obtenir_service_cellier_crud": "crud.cellier_crud_service",
    # Checklists CRUD service → crud/
    "ChecklistsCrudService": "crud.checklists_crud_service",
    "get_checklists_service": "crud.checklists_crud_service",
    # Diagnostics & Estimations CRUD services → crud/
    "DiagnosticsCrudService": "crud.diagnostics_crud_service",
    "obtenir_diagnostics_crud_service": "crud.diagnostics_crud_service",
    "obtenir_service_diagnostics_crud": "crud.diagnostics_crud_service",
    "EstimationsCrudService": "crud.diagnostics_crud_service",
    "obtenir_estimations_crud_service": "crud.diagnostics_crud_service",
    "obtenir_service_estimations_crud": "crud.diagnostics_crud_service",
    # Extensions CRUD services (nuisibles, devis, entretien saisonnier, relevés) → crud/
    "NuisiblesCrudService": "crud.extensions_crud_service",
    "obtenir_nuisibles_crud_service": "crud.extensions_crud_service",
    "DevisCrudService": "crud.extensions_crud_service",
    "obtenir_devis_crud_service": "crud.extensions_crud_service",
    "EntretienSaisonnierCrudService": "crud.extensions_crud_service",
    "obtenir_entretien_saisonnier_crud_service": "crud.extensions_crud_service",
    "RelevesCrudService": "crud.extensions_crud_service",
    "obtenir_releves_crud_service": "crud.extensions_crud_service",
    # Visualisation service
    "VisualisationService": "visualisation_service",
    "obtenir_visualisation_service": "visualisation_service",
    "obtenir_service_visualisation": "visualisation_service",
    # Contexte Maison service (briefing quotidien)
    "ContexteMaisonService": "contexte_maison_service",
    "obtenir_contexte_maison_service": "contexte_maison_service",
    "obtenir_service_contexte_maison": "contexte_maison_service",
    # Catalogue Entretien service (sync JSON → tâches DB)
    "CatalogueEntretienService": "catalogue_entretien_service",
    "obtenir_catalogue_entretien_service": "catalogue_entretien_service",
    "obtenir_service_catalogue_entretien": "catalogue_entretien_service",
    # Notifications Maison service (rappels push)
    "NotificationsMaisonService": "notifications_maison",
    "obtenir_notifications_maison_service": "notifications_maison",
    "obtenir_service_notifications_maison": "notifications_maison",
    # Innovations maison / énergie consolidées → ia/
    "ServiceInnovationsMaison": "ia.service_ia",
    "obtenir_service_innovations_maison": "ia.service_ia",
    # Fiche Tâche service (catalogue + IA fallback)
    "FicheTacheService": "fiche_tache_service",
    "obtenir_fiche_tache_service": "fiche_tache_service",
    "obtenir_service_fiche_tache": "fiche_tache_service",
    # Catalogue Enrichissement service (IA enrichissement JSON) → ia/
    "CatalogueEnrichissementService": "ia.catalogue_enrichissement_service",
    "obtenir_catalogue_enrichissement_service": "ia.catalogue_enrichissement_service",
    # Bridges inter-modules → bridges/
    "ChargesEnergieInteractionService": "inter_modules.inter_module_charges_energie",
    "obtenir_service_charges_energie_interaction": "inter_modules.inter_module_charges_energie",
    "EntretienCoursesInteractionService": "inter_modules.inter_module_entretien_courses",
    "obtenir_service_entretien_courses_interaction": "inter_modules.inter_module_entretien_courses",
    "JardinEntretienInteractionService": "inter_modules.inter_module_jardin_entretien",
    "obtenir_service_jardin_entretien_interaction": "inter_modules.inter_module_jardin_entretien",
    "GarantiesDocumentsInteractionService": "inter_modules.inter_module_garanties_documents",
    "obtenir_service_garanties_documents_interaction": "inter_modules.inter_module_garanties_documents",
}

_SCHEMAS = {
    # Schemas Pydantic
    "BriefingMaison": "schemas",
    "AlerteMaison": "schemas",
    "TacheJour": "schemas",
    "MeteoResume": "schemas",
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
    from .crud.artisans_crud_service import ArtisansCrudService, obtenir_artisans_crud_service
    from .crud.cellier_crud_service import CellierCrudService, obtenir_cellier_crud_service
    from .crud.depenses_crud_service import obtenir_depenses_crud_service
    from .crud.diagnostics_crud_service import (
        DiagnosticsCrudService,
        EstimationsCrudService,
        obtenir_diagnostics_crud_service,
        obtenir_estimations_crud_service,
    )
    from .crud.eco_tips_crud_service import (
        EcoTipsCrudService,
        obtenir_eco_tips_crud_service,
        obtenir_service_eco_tips_crud,
    )
    from .entretien_service import (
        EntretienService,
        obtenir_entretien_service,
        obtenir_service_entretien,
    )
    from .crud.extensions_crud_service import (
        DevisCrudService,
        EntretienSaisonnierCrudService,
        NuisiblesCrudService,
        RelevesCrudService,
        obtenir_devis_crud_service,
        obtenir_entretien_saisonnier_crud_service,
        obtenir_nuisibles_crud_service,
        obtenir_releves_crud_service,
    )
    from .jardin_service import JardinService, obtenir_jardin_service, obtenir_service_jardin
    from .crud.meubles_crud_service import (
        MeublesCrudService,
        obtenir_meubles_crud_service,
        obtenir_service_meubles_crud,
    )
    from .projets_service import ProjetsService, obtenir_projets_service, obtenir_service_projets
    from .visualisation_service import VisualisationService, obtenir_visualisation_service
    from .ia.catalogue_enrichissement_service import (
        CatalogueEnrichissementService,
        obtenir_catalogue_enrichissement_service,
    )
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
    "obtenir_jardin_service",
    "obtenir_entretien_service",
    "obtenir_projets_service",
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
    # CRUD services
    "DepensesCrudService",
    "obtenir_depenses_crud_service",
    "obtenir_depenses_crud_service",
    "obtenir_service_depenses_crud",
    "HubDataService",
    "obtenir_hub_data_service",
    "obtenir_service_hub_data",
    # NEW: Meubles CRUD service
    "MeublesCrudService",
    "obtenir_meubles_crud_service",
    "obtenir_service_meubles_crud",
    # NEW: Eco Tips CRUD service
    "EcoTipsCrudService",
    "obtenir_eco_tips_crud_service",
    "obtenir_service_eco_tips_crud",
    # Artisans, Cellier, Checklists
    "ArtisansCrudService",
    "obtenir_artisans_crud_service",
    "CellierCrudService",
    "obtenir_cellier_crud_service",
    "ChecklistsCrudService",
    "get_checklists_service",
    # NEW: Diagnostics & Estimations
    "DiagnosticsCrudService",
    "obtenir_diagnostics_crud_service",
    "EstimationsCrudService",
    "obtenir_estimations_crud_service",
    # NEW: Extensions (nuisibles, devis, entretien saisonnier, releves)
    "NuisiblesCrudService",
    "obtenir_nuisibles_crud_service",
    "DevisCrudService",
    "obtenir_devis_crud_service",
    "EntretienSaisonnierCrudService",
    "obtenir_entretien_saisonnier_crud_service",
    "RelevesCrudService",
    "obtenir_releves_crud_service",
    # Visualisation
    "VisualisationService",
    "obtenir_visualisation_service",
    # Bridges inter-modules
    "ChargesEnergieInteractionService",
    "obtenir_service_charges_energie_interaction",
    "EntretienCoursesInteractionService",
    "obtenir_service_entretien_courses_interaction",
    "JardinEntretienInteractionService",
    "obtenir_service_jardin_entretien_interaction",
]

