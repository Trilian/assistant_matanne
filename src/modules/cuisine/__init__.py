"""
Module Cuisine - Point d'Entrée Unifié
Architecture Optimisée avec BaseModuleUI
"""

# Configs
from .configs import (
    get_recettes_config,
    get_inventaire_config,
    get_courses_config,
    get_planning_config
)

# Modules (auto-expose les app() functions)
from . import recettes
from . import inventaire
from . import courses
from . import planning_semaine

__all__ = [
    # Configs
    "get_recettes_config",
    "get_inventaire_config",
    "get_courses_config",
    "get_planning_config",

    # Modules
    "recettes",
    "inventaire",
    "courses",
    "planning_semaine"
]