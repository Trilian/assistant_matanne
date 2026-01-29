"""
Rate Limiting IA - Gestion des quotas API Mistral

Ce module gère le rate limiting spécifique aux appels IA :
- Quotas journaliers et horaires
- Reset automatique
- Statistiques d'utilisation
"""

import logging
from datetime import datetime

import streamlit as st

from ..constants import AI_RATE_LIMIT_DAILY, AI_RATE_LIMIT_HOURLY

logger = logging.getLogger(__name__)


class RateLimitIA:
    """
    Rate limiting spécifique pour les appels IA.

    Gère les quotas API Mistral avec reset automatique.
    """

    CLE_RATE_LIMIT = "rate_limit_ia"
    """Clé session state."""

    @staticmethod
    def _initialiser():
        """Initialise les compteurs dans session_state."""
        if RateLimitIA.CLE_RATE_LIMIT not in st.session_state:
            st.session_state[RateLimitIA.CLE_RATE_LIMIT] = {
                "appels_jour": 0,
                "appels_heure": 0,
                "dernier_reset_jour": datetime.now().date(),
                "dernier_reset_heure": datetime.now().replace(minute=0, second=0, microsecond=0),
                "historique": [],  # Pour analytics
            }

    @staticmethod
    def peut_appeler() -> tuple[bool, str]:
        """
        Vérifie si un appel IA est autorisé.

        Returns:
            Tuple (autorisé, message_erreur)

        Example:
            >>> autorise, erreur = RateLimitIA.peut_appeler()
            >>> if not autorise:
            >>>     st.warning(erreur)
        """
        RateLimitIA._initialiser()

        # Reset quotidien
        aujourd_hui = datetime.now().date()
        if st.session_state[RateLimitIA.CLE_RATE_LIMIT]["dernier_reset_jour"] != aujourd_hui:
            st.session_state[RateLimitIA.CLE_RATE_LIMIT]["appels_jour"] = 0
            st.session_state[RateLimitIA.CLE_RATE_LIMIT]["dernier_reset_jour"] = aujourd_hui
            logger.info("🔄 Reset quota journalier")

        # Reset horaire
        heure_actuelle = datetime.now().replace(minute=0, second=0, microsecond=0)
        if st.session_state[RateLimitIA.CLE_RATE_LIMIT]["dernier_reset_heure"] != heure_actuelle:
            st.session_state[RateLimitIA.CLE_RATE_LIMIT]["appels_heure"] = 0
            st.session_state[RateLimitIA.CLE_RATE_LIMIT]["dernier_reset_heure"] = heure_actuelle
            logger.info("🔄 Reset quota horaire")

        # Vérifier limites
        appels_jour = st.session_state[RateLimitIA.CLE_RATE_LIMIT]["appels_jour"]
        appels_heure = st.session_state[RateLimitIA.CLE_RATE_LIMIT]["appels_heure"]

        if appels_jour >= AI_RATE_LIMIT_DAILY:
            return False, f"⏳ Limite quotidienne atteinte ({AI_RATE_LIMIT_DAILY} appels/jour)"

        if appels_heure >= AI_RATE_LIMIT_HOURLY:
            return False, f"⏳ Limite horaire atteinte ({AI_RATE_LIMIT_HOURLY} appels/heure)"

        return True, ""

    @staticmethod
    def enregistrer_appel(service: str = "unknown", tokens_utilises: int = 0):
        """
        Enregistre un appel IA.

        Args:
            service: Nom du service appelant (recettes, inventaire, etc.)
            tokens_utilises: Nombre de tokens utilisés (si disponible)
        """
        RateLimitIA._initialiser()

        st.session_state[RateLimitIA.CLE_RATE_LIMIT]["appels_jour"] += 1
        st.session_state[RateLimitIA.CLE_RATE_LIMIT]["appels_heure"] += 1

        # Historique pour analytics
        st.session_state[RateLimitIA.CLE_RATE_LIMIT]["historique"].append(
            {"timestamp": datetime.now(), "service": service, "tokens": tokens_utilises}
        )

        # Limiter historique (garder 100 derniers appels)
        if len(st.session_state[RateLimitIA.CLE_RATE_LIMIT]["historique"]) > 100:
            st.session_state[RateLimitIA.CLE_RATE_LIMIT]["historique"] = st.session_state[
                RateLimitIA.CLE_RATE_LIMIT
            ]["historique"][-100:]

        logger.debug(f"[OK] Appel IA enregistré ({service})")

    @staticmethod
    def obtenir_statistiques() -> dict:
        """
        Retourne les statistiques de rate limiting.

        Returns:
            Dict avec compteurs et métriques

        Example:
            >>> stats = RateLimitIA.obtenir_statistiques()
            >>> st.metric("Appels aujourd'hui", stats["appels_jour"])
        """
        RateLimitIA._initialiser()

        data = st.session_state[RateLimitIA.CLE_RATE_LIMIT]

        # Calcul répartition par service
        services_usage = {}
        for appel in data["historique"]:
            service = appel["service"]
            services_usage[service] = services_usage.get(service, 0) + 1

        return {
            "appels_jour": data["appels_jour"],
            "limite_jour": AI_RATE_LIMIT_DAILY,
            "restant_jour": AI_RATE_LIMIT_DAILY - data["appels_jour"],
            "pourcentage_jour": (data["appels_jour"] / AI_RATE_LIMIT_DAILY * 100),
            "appels_heure": data["appels_heure"],
            "limite_heure": AI_RATE_LIMIT_HOURLY,
            "restant_heure": AI_RATE_LIMIT_HOURLY - data["appels_heure"],
            "pourcentage_heure": (data["appels_heure"] / AI_RATE_LIMIT_HOURLY * 100),
            "par_service": services_usage,
            "total_historique": len(data["historique"]),
        }

    @staticmethod
    def reset_quotas():
        """Reset manuel des quotas (debug/admin)."""
        RateLimitIA._initialiser()
        st.session_state[RateLimitIA.CLE_RATE_LIMIT]["appels_jour"] = 0
        st.session_state[RateLimitIA.CLE_RATE_LIMIT]["appels_heure"] = 0
        logger.warning("[!] Reset manuel des quotas IA")


# ═══════════════════════════════════════════════════════════
# ALIAS COMPATIBILITÉ (pour imports existants)
# ═══════════════════════════════════════════════════════════

# Permet d'importer depuis cache.py OU ai/rate_limit.py
LimiteDebit = RateLimitIA

__all__ = ["RateLimitIA", "LimiteDebit"]
