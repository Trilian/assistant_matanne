"""
Helpers et fonctions utilitaires pour le module Famille.

REFACTORISÉ: Les requêtes DB sont déléguées aux services dédiés:
- ``src.services.famille.jules.ServiceJules`` (profil enfant, jalons)
- ``src.services.famille.sante.ServiceSante`` (objectifs, routines, stats, budget)

Ce module conserve les fonctions publiques pour compatibilité ascendante,
mais agit comme une façade mince devant les services.
"""

from __future__ import annotations

import logging
from datetime import date

from src.core.date_utils import formater_date_fr
from src.modules.famille.age_utils import get_age_jules

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# LAZY SERVICE ACCESSORS
# ═══════════════════════════════════════════════════════════

_service_jules = None
_service_sante = None


def _get_service_jules():
    """Accès lazy au ServiceJules."""
    global _service_jules
    if _service_jules is None:
        from src.services.famille.jules import obtenir_service_jules

        _service_jules = obtenir_service_jules()
    return _service_jules


def _get_service_sante():
    """Accès lazy au ServiceSante."""
    global _service_sante
    if _service_sante is None:
        from src.services.famille.sante import obtenir_service_sante

        _service_sante = obtenir_service_sante()
    return _service_sante


# ═══════════════════════════════════════════════════════════
# CHILD PROFILE HELPERS
# ═══════════════════════════════════════════════════════════


def get_or_create_jules() -> int:
    """Récupère ou crée le profil Jules, retourne son ID.

    Note: N'est plus décoré avec @st.cache_data car cette
    fonction effectue potentiellement un INSERT en base.
    """
    return _get_service_jules().get_or_create_jules()


def calculer_age_jules() -> dict:
    """Calcule l'âge de Jules (délègue à age_utils)."""
    return get_age_jules()


# ═══════════════════════════════════════════════════════════
# MILESTONE HELPERS
# ═══════════════════════════════════════════════════════════


def get_milestones_by_category(child_id: int) -> dict:
    """Récupère les jalons groupés par catégorie."""
    try:
        return _get_service_jules().get_milestones_by_category(child_id)
    except Exception as e:
        logger.error("Erreur lecture jalons: %s", e)
        return {}


def count_milestones_by_category(child_id: int) -> dict:
    """Compte les jalons par catégorie."""
    try:
        return _get_service_jules().count_milestones_by_category(child_id)
    except Exception as e:
        logger.error("Erreur comptage jalons: %s", e)
        return {}


# ═══════════════════════════════════════════════════════════
# HEALTH OBJECTIVE HELPERS
# ═══════════════════════════════════════════════════════════


def calculer_progression_objectif(objective) -> float:
    """Calcule le % de progression d'un objectif santé.

    Délègue au service santé via factory registry.
    """
    from src.services.famille.sante import obtenir_service_sante

    return obtenir_service_sante().calculer_progression_objectif(objective)


def get_objectives_actifs() -> list:
    """Récupère tous les objectifs en cours avec progression."""
    try:
        return _get_service_sante().get_objectives_actifs()
    except Exception as e:
        logger.error("Erreur lecture objectifs: %s", e)
        return []


# ═══════════════════════════════════════════════════════════
# BUDGET HELPERS
# ═══════════════════════════════════════════════════════════


def get_budget_par_period(period: str = "month") -> dict:
    """Récupère le budget par période (day, week, month)."""
    try:
        return _get_service_sante().get_budget_par_period(period)
    except Exception as e:
        logger.error("Erreur lecture budget: %s", e)
        return {}


def get_budget_mois_dernier() -> float:
    """Récupère le budget total du mois dernier."""
    try:
        return _get_service_sante().get_budget_mois_dernier()
    except Exception as e:
        logger.error("Erreur calcul budget mois dernier: %s", e)
        return 0.0


# ═══════════════════════════════════════════════════════════
# ACTIVITY HELPERS
# ═══════════════════════════════════════════════════════════


def get_activites_semaine() -> list:
    """Récupère les activités de cette semaine."""
    try:
        return _get_service_sante().get_activites_semaine()
    except Exception as e:
        logger.error("Erreur lecture activités: %s", e)
        return []


def get_budget_activites_mois() -> float:
    """Récupère les dépenses en activités ce mois."""
    try:
        return _get_service_sante().get_budget_activites_mois()
    except Exception as e:
        logger.error("Erreur budget activités: %s", e)
        return 0.0


# ═══════════════════════════════════════════════════════════
# HEALTH ROUTINE HELPERS
# ═══════════════════════════════════════════════════════════


def get_routines_actives() -> list:
    """Récupère les routines de santé actives."""
    try:
        return _get_service_sante().get_routines_actives()
    except Exception as e:
        logger.error("Erreur lecture routines: %s", e)
        return []


def get_stats_sante_semaine() -> dict:
    """Calcule les stats de santé pour cette semaine."""
    try:
        return _get_service_sante().get_stats_sante_semaine()
    except Exception as e:
        logger.error("Erreur stats santé: %s", e)
        return {
            "nb_seances": 0,
            "total_minutes": 0,
            "total_calories": 0,
            "energie_moyenne": 0,
            "moral_moyen": 0,
        }


# ═══════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════


def clear_famille_cache():
    """Vide le cache des fonctions famille.

    CORRIGÉ: N'efface plus le cache global de l'application.
    Invalide uniquement les caches liés au module famille.
    """
    logger.debug("Invalidation du cache famille")
    # Les services utilisent @avec_session_db sans cache Streamlit.
    # Rien à invalider côté cache — les données sont fraîches à chaque appel.


def format_date_fr(d: date) -> str:
    """Formate une date en français.

    Délègue à ``src.core.date_utils.formater_date_fr`` pour éviter la duplication.
    """
    return formater_date_fr(d)
