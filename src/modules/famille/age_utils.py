"""
Calcul centralisé de l'âge de Jules.

Source de vérité unique pour éviter la duplication de la logique d'âge
et des dates de naissance incohérentes à travers le codebase.

Usage:
    from src.modules.famille.age_utils import get_age_jules, get_age_jules_mois

    age = get_age_jules()        # {"mois": 20, "semaines": 87, "jours": 608, ...}
    age_m = get_age_jules_mois() # 20
"""

import logging
from datetime import date

from src.core.constants import JULES_NAISSANCE

logger = logging.getLogger(__name__)


def get_age_jules() -> dict:
    """Récupère l'âge de Jules depuis la BD, avec fallback sur la constante.

    Returns:
        dict avec clés: mois, semaines, jours, date_naissance, texte
    """
    naissance = _obtenir_date_naissance()
    return _calculer_age(naissance)


def get_age_jules_mois() -> int:
    """Retourne l'âge de Jules en mois (int).

    Returns:
        Nombre de mois approximatif (jours // 30).
    """
    naissance = _obtenir_date_naissance()
    return (date.today() - naissance).days // 30


def calculer_age_jules() -> dict:
    """Alias pour compatibilité — identique à get_age_jules().

    Certains modules utilisent ce nom. Renvoie le même résultat.
    """
    return get_age_jules()


# ─── Fonctions internes ────────────────────────────────────


def _obtenir_date_naissance() -> date:
    """Interroge la BD pour la date de naissance, fallback JULES_NAISSANCE."""
    try:
        from src.services.famille.jules import obtenir_service_jules

        result = obtenir_service_jules().get_date_naissance_jules()
        if result:
            return result
    except Exception:
        logger.debug("BD indisponible pour l'âge de Jules, utilisation du fallback")

    return JULES_NAISSANCE


def _calculer_age(naissance: date) -> dict:
    """Calcule les métriques d'âge à partir d'une date de naissance."""
    today = date.today()
    delta = today - naissance
    jours = delta.days
    mois = jours // 30
    semaines = jours // 7
    jours_restants = jours % 30

    return {
        "mois": mois,
        "semaines": semaines,
        "jours": jours,
        "ans": jours // 365,
        "date_naissance": naissance,
        "texte": f"{mois} mois" + (f" et {jours_restants}j" if jours_restants > 0 else ""),
    }
