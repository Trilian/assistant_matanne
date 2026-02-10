"""
Package Cuisine UI - Modules séparés pour une meilleure organisation

Structure:
- recettes.py: Gestion des recettes
- inventaire.py: Gestion du stock
- planificateur_repas.py: Planning hebdomadaire intelligent
- courses.py: Liste de courses

Pour éviter les imports circulaires, les modules sont chargés à la demande.
"""

__all__ = [
    "recettes",
    "inventaire",
    "planificateur_repas",
    "courses",
    "recettes_import",
]


def __getattr__(name: str):
    """Import différé pour éviter les imports circulaires."""
    if name == "recettes":
        from . import recettes as mod
        return mod
    elif name == "inventaire":
        from . import inventaire as mod
        return mod
    elif name == "planificateur_repas":
        from . import planificateur_repas as mod
        return mod
    elif name == "courses":
        from . import courses as mod
        return mod
    elif name == "recettes_import":
        from . import recettes_import as mod
        return mod
    raise AttributeError(f"module 'src.domains.cuisine.ui' has no attribute '{name}'")

