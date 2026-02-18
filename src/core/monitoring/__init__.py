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
    afficher_statistiques_cache,
    afficher_statistiques_rate_limit,
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
from .sql_optimizer import (
    ChargeurParLots,
    ConstructeurRequeteOptimisee,
    DetecteurN1,
    EcouteurSQLAlchemy,
    afficher_analyse_sql,
)

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
    # SQL Optimizer
    "EcouteurSQLAlchemy",
    "DetecteurN1",
    "ChargeurParLots",
    "ConstructeurRequeteOptimisee",
    "afficher_analyse_sql",
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
    "afficher_statistiques_cache",
    "afficher_statistiques_rate_limit",
]
