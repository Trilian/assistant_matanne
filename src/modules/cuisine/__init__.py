"""
Module Cuisine - Point d'entrée unifié optimisé
Architecture avec BaseModuleCuisine + Mixins
"""

# Core
from .core import (
    BaseModuleCuisine,
    AIGenerationMixin,
    ExportMixin,
    SearchMixin,
    StatsMixin,
    ValidationMixin
)

# Modules
from . import recettes
from . import inventaire
from . import courses
from . import planning

__all__ = [
    # Core
    "BaseModuleCuisine",
    "AIGenerationMixin",
    "ExportMixin",
    "SearchMixin",
    "StatsMixin",
    "ValidationMixin",

    # Modules
    "recettes",
    "inventaire",
    "courses",
    "planning"
]