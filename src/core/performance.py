"""
Performance - Module de retrocompatibilite.

DEPRECATED: Importer depuis src.core.monitoring a la place.
Ce fichier existe uniquement pour la retrocompatibilite.

Exemple de migration:
    # Ancien import (toujours supporte)
    from src.core.performance import ProfileurFonction

    # Nouvel import (recommande)
    from src.core.monitoring import ProfileurFonction
    # ou
    from src.core import ProfileurFonction
"""

# Re-exports depuis le nouveau module
from .monitoring import (
    ChargeurComposant,
    MetriquePerformance,
    MoniteurMemoire,
    OptimiseurSQL,
    ProfileurFonction,
    StatistiquesFonction,
    TableauBordPerformance,
    afficher_badge_mini_performance,
    afficher_panneau_performance,
    antirrebond,
    limiter_debit,
    mesurer_temps,
    profiler,
    suivre_requete,
)

__all__ = [
    "MetriquePerformance",
    "StatistiquesFonction",
    "ProfileurFonction",
    "MoniteurMemoire",
    "OptimiseurSQL",
    "TableauBordPerformance",
    "ChargeurComposant",
    "profiler",
    "antirrebond",
    "limiter_debit",
    "mesurer_temps",
    "suivre_requete",
    "afficher_panneau_performance",
    "afficher_badge_mini_performance",
]
