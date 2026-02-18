"""
Services Base - Classes et types de base pour les services

Ce package regroupe les classes fondamentales des services:
- BaseAIService: Service IA avec rate limiting et cache automatiques
- BaseService: Service CRUD générique avec ORM
- IOService: Import/Export universel (CSV, JSON)
- Mixins IA: RecipeAIMixin, PlanningAIMixin, InventoryAIMixin
- Async utils: sync_wrapper pour conversion async→sync
"""

# ═══════════════════════════════════════════════════════════
# UTILITAIRES ASYNC
# ═══════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════
# BASE AI SERVICE (avec mixins spécialisés)
# ═══════════════════════════════════════════════════════════
from .ai_service import (
    BaseAIService,
    InventoryAIMixin,
    PlanningAIMixin,
    RecipeAIMixin,
    create_base_ai_service,
)
from .async_utils import make_sync_alias, sync_wrapper

# ═══════════════════════════════════════════════════════════
# IO SERVICE (Import/Export)
# ═══════════════════════════════════════════════════════════
from .io_service import (
    COURSES_FIELD_MAPPING,
    INVENTAIRE_FIELD_MAPPING,
    RECETTE_FIELD_MAPPING,
    IOService,
)

# ═══════════════════════════════════════════════════════════
# BASE SERVICE (CRUD générique)
# ═══════════════════════════════════════════════════════════
from .types import BaseService, T

__all__ = [
    # Async utils
    "sync_wrapper",
    "make_sync_alias",
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
