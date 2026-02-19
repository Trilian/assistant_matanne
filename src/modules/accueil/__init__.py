"""
Module Accueil - Dashboard Central
Vue d'ensemble de l'application avec stats, alertes et raccourcis
"""

from src.modules.accueil.dashboard import (
    afficher_courses_summary,
    afficher_critical_alerts,
    afficher_cuisine_summary,
    afficher_global_stats,
    afficher_graphiques_enrichis,
    afficher_inventaire_summary,
    afficher_planning_summary,
    afficher_quick_actions,
    app,
)

__all__ = [
    "app",
    "afficher_critical_alerts",
    "afficher_global_stats",
    "afficher_quick_actions",
    "afficher_graphiques_enrichis",
    "afficher_cuisine_summary",
    "afficher_inventaire_summary",
    "afficher_courses_summary",
    "afficher_planning_summary",
]
