"""Domaines organisés par contexte métier.

Architecture:
- cuisine: Recettes, planning repas, inventaire, courses
- famille: Jules, santé, activités, shopping
- planning: Calendrier, routines, planification
- maison: Entretien, projets, jardin, zones
- utils: Accueil, paramètres, rapports, barcode
- jeux: Paris sportifs, loto

Pour éviter les imports circulaires, les domaines sont chargés à la demande.
"""

__all__ = ["cuisine", "famille", "planning", "maison", "utils", "jeux"]


def __getattr__(name: str):
    """Import différé pour éviter les imports circulaires."""
    if name == "cuisine":
        from . import cuisine as mod
        return mod
    elif name == "famille":
        from . import famille as mod
        return mod
    elif name == "planning":
        from . import planning as mod
        return mod
    elif name == "maison":
        from . import maison as mod
        return mod
    elif name == "utils":
        from . import utils as mod
        return mod
    elif name == "jeux":
        from . import jeux as mod
        return mod
    raise AttributeError(f"module 'src.domains' has no attribute '{name}'")
