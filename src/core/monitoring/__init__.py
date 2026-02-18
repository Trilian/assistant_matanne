"""
Monitoring - Module de métriques et performance.

Ce module fournit:
- Profiling des fonctions
- Monitoring mémoire
- Tracking des requêtes SQL
- Dashboard de performance UI
"""

from .dashboard import (
    TableauBordPerformance,
    afficher_badge_mini_performance,
    afficher_panneau_performance,
)
from .memory import MoniteurMemoire
from .profiler import (
    ChargeurComposant,
    MetriquePerformance,
    ProfileurFonction,
    StatistiquesFonction,
    antirrebond,
    limiter_debit,
    mesurer_temps,
    profiler,
)
from .sql import OptimiseurSQL, suivre_requete

__all__ = [
    # Types
    "MetriquePerformance",
    "StatistiquesFonction",
    # Classes
    "ProfileurFonction",
    "MoniteurMemoire",
    "OptimiseurSQL",
    "TableauBordPerformance",
    "ChargeurComposant",
    # Décorateurs
    "profiler",
    "antirrebond",
    "limiter_debit",
    # Context managers
    "mesurer_temps",
    "suivre_requete",
    # UI
    "afficher_panneau_performance",
    "afficher_badge_mini_performance",
]
