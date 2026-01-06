"""
Modules Cuisine Core - Point d'entrée
Base abstraite + Mixins réutilisables
"""

from .base_module import BaseModuleCuisine
from .mixins import (
    AIGenerationMixin,
    ExportMixin,
    SearchMixin,
    StatsMixin,
    ValidationMixin
)

__all__ = [
    "BaseModuleCuisine",
    "AIGenerationMixin",
    "ExportMixin",
    "SearchMixin",
    "StatsMixin",
    "ValidationMixin"
]