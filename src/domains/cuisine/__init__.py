"""Domaine Cuisine - Gestion recettes, planning repas, inventaire et courses."""

# UI
from .ui import recettes, planning, inventaire, courses, recettes_import

# Logic
from .logic import recettes_logic, planning_logic, inventaire_logic, courses_logic

# Exports principaux
__all__ = [
    # UI
    "recettes",
    "planning",
    "inventaire", 
    "courses",
    "recettes_import",
    # Logic
    "recettes_logic",
    "planning_logic",
    "inventaire_logic",
    "courses_logic",
]

