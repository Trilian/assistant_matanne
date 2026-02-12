"""
Services Base - Classes et types de base pour les services

Ce package regroupe les classes fondamentales des services:
- BaseAIService: Service IA avec rate limiting et cache automatiques
- BaseService: Service CRUD générique avec ORM
- IOService: Import/Export universel (CSV, JSON)
- Mixins IA: RecipeAIMixin, PlanningAIMixin, InventoryAIMixin
"""

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# BASE AI SERVICE (avec mixins spécialisés)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
from .ai_service import (
    BaseAIService,
    RecipeAIMixin,
    PlanningAIMixin,
    InventoryAIMixin,
    create_base_ai_service,
)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# BASE SERVICE (CRUD générique)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
from .types import BaseService, T

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# IO SERVICE (Import/Export)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
from .io_service import (
    IOService,
    RECETTE_FIELD_MAPPING,
    INVENTAIRE_FIELD_MAPPING,
    COURSES_FIELD_MAPPING,
)

__all__ = [
    # AI Service
    "BaseAIService",
    "RecipeAIMixin",
    "PlanningAIMixin",
    "InventoryAIMixin",
    "create_base_ai_service",
    # CRUD Service
    "BaseService",
    "T",
    # IO Service
    "IOService",
    "RECETTE_FIELD_MAPPING",
    "INVENTAIRE_FIELD_MAPPING",
    "COURSES_FIELD_MAPPING",
]
