"""Domaine Cuisine - Gestion recettes, planning repas, inventaire et courses.

Modules disponibles (chargement différé via OptimizedRouter):
- recettes: Gestion des recettes
- inventaire: Gestion du stock
- planificateur_repas: Planning hebdomadaire intelligent
- courses: Liste de courses
- recettes_import: Import de recettes

Pour éviter les imports circulaires, les modules sont chargés à la demande.
"""

# Exports principaux - imports différés via __getattr__
__all__ = [
    # UI
    "recettes",
    "planificateur_repas",
    "inventaire", 
    "courses",
    "recettes_import",
    # Logic
    "recettes_logic",
    "planning_logic",
    "inventaire_logic",
    "courses_logic",
]


def __getattr__(name: str):
    """Import différé pour éviter les imports circulaires."""
    if name in ("recettes", "inventaire", "courses", "recettes_import", "planificateur_repas"):
        from . import ui
        return getattr(ui, name)
    elif name in ("recettes_logic", "planning_logic", "inventaire_logic", "courses_logic"):
        from . import logic
        return getattr(logic, name)
    raise AttributeError(f"module 'src.domains.cuisine' has no attribute '{name}'")

