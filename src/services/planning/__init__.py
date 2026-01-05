"""
Services Planning - Point d'Entrée Module COMPLET

Regroupe tous les services liés au planning hebdomadaire :
- CRUD planning
- CRUD repas
- IA (génération intelligente)
- Constantes métier
"""

# Services CRUD
from .planning_service import (
    PlanningService,
    planning_service,
    JOURS_SEMAINE,
)

from .repas_service import (
    RepasService,
    repas_service,
)

# Service IA Génération
from .planning_generation_service import (
    PlanningGenerationService,
    create_planning_generation_service,
)

__all__ = [
    # Classes CRUD
    "PlanningService",
    "RepasService",

    # Instances CRUD
    "planning_service",
    "repas_service",

    # Classe IA
    "PlanningGenerationService",

    # Factory IA
    "create_planning_generation_service",

    # Constantes métier
    "JOURS_SEMAINE",
]