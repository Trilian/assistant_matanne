"""
Module Accueil - Dashboard Central
Vue d'ensemble de l'application avec stats, alertes, widgets enrichis et raccourcis.

Sous-modules:
- dashboard.py: Point d'entrée app() et layout principal
- alerts.py, stats.py, summaries.py, utils.py: Fonctions historiques
- resume_hebdo.py: Résumé hebdomadaire IA
- widget_meteo.py: Météo + impact activités
- resume_matinal.py: Résumé matinal IA personnalisé
- widget_ce_soir.py: "Ce soir on mange..." suggestion
- rappels_contextuels.py: Rappels intelligents multi-source
- mini_calendrier.py: Mini-calendrier semaine
- widget_economies.py: Économies du mois
- widget_photo.py: Photo souvenir du jour
- widget_sante.py: Santé / Garmin fitness
- widget_conseil_jules.py: Conseil Jules IA
- widget_gamification.py: Gamification familiale
- widget_jardin.py: Aperçu jardin
- widget_maison.py: Résumé maison / entretien
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
from src.modules.accueil.mini_calendrier import afficher_mini_calendrier
from src.modules.accueil.rappels_contextuels import afficher_rappels_contextuels
from src.modules.accueil.resume_hebdo import afficher_resume_hebdomadaire
from src.modules.accueil.resume_matinal import afficher_resume_matinal
from src.modules.accueil.widget_ce_soir import afficher_widget_ce_soir
from src.modules.accueil.widget_conseil_jules import afficher_conseil_jules
from src.modules.accueil.widget_economies import afficher_widget_economies
from src.modules.accueil.widget_gamification import afficher_widget_gamification
from src.modules.accueil.widget_jardin import afficher_widget_jardin
from src.modules.accueil.widget_maison import afficher_widget_maison
from src.modules.accueil.widget_meteo import afficher_widget_meteo
from src.modules.accueil.widget_photo import afficher_photo_souvenir
from src.modules.accueil.widget_sante import afficher_widget_sante

__all__ = [
    "app",
    # Dashboard historique
    "afficher_critical_alerts",
    "afficher_global_stats",
    "afficher_quick_actions",
    "afficher_graphiques_enrichis",
    "afficher_cuisine_summary",
    "afficher_inventaire_summary",
    "afficher_courses_summary",
    "afficher_planning_summary",
    "afficher_resume_hebdomadaire",
    # Nouveaux widgets enrichis
    "afficher_widget_meteo",
    "afficher_resume_matinal",
    "afficher_widget_ce_soir",
    "afficher_rappels_contextuels",
    "afficher_mini_calendrier",
    "afficher_widget_economies",
    "afficher_photo_souvenir",
    "afficher_widget_sante",
    "afficher_conseil_jules",
    "afficher_widget_gamification",
    "afficher_widget_jardin",
    "afficher_widget_maison",
]
