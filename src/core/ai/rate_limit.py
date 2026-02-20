"""
Rate Limiting IA - Gestion des quotas API Mistral

Ce module gère le rate limiting spécifique aux appels IA :
- Quotas journaliers et horaires
- Reset automatique
- Statistiques d'utilisation

Utilise ``SessionStorage`` pour le stockage des compteurs,
ce qui permet de tester sans Streamlit.
"""

import logging
from datetime import datetime

from ..constants import AI_RATE_LIMIT_DAILY, AI_RATE_LIMIT_HOURLY
from ..storage import obtenir_storage

logger = logging.getLogger(__name__)


class RateLimitIA:
    """
    Rate limiting spécifique pour les appels IA.

    Gère les quotas API Mistral avec reset automatique.
    Découplé de ``st.session_state`` via ``SessionStorage``.
    """

    CLE_RATE_LIMIT = "rate_limit_ia"
    """Clé session state."""

    @staticmethod
    def _obtenir_storage():
        """Retourne le backend de stockage."""
        return obtenir_storage()

    @staticmethod
    def _initialiser():
        """Initialise les compteurs dans le storage."""
        storage = RateLimitIA._obtenir_storage()
        if not storage.contains(RateLimitIA.CLE_RATE_LIMIT):
            storage.set(
                RateLimitIA.CLE_RATE_LIMIT,
                {
                    "appels_jour": 0,
                    "appels_heure": 0,
                    "dernier_reset_jour": datetime.now().date(),
                    "dernier_reset_heure": datetime.now().replace(
                        minute=0, second=0, microsecond=0
                    ),
                    "historique": [],
                },
            )

    @staticmethod
    def _obtenir_data() -> dict:
        """Retourne les données de rate limiting."""
        storage = RateLimitIA._obtenir_storage()
        return storage.get(RateLimitIA.CLE_RATE_LIMIT, {})

    @staticmethod
    def _sauvegarder_data(data: dict):
        """Sauvegarde les données de rate limiting."""
        storage = RateLimitIA._obtenir_storage()
        storage.set(RateLimitIA.CLE_RATE_LIMIT, data)

    @staticmethod
    def peut_appeler() -> tuple[bool, str]:
        """
        Vérifie si un appel IA est autorisé.

        Returns:
            Tuple (autorisé, message_erreur)
        """
        RateLimitIA._initialiser()
        data = RateLimitIA._obtenir_data()

        # Reset quotidien
        aujourd_hui = datetime.now().date()
        if data["dernier_reset_jour"] != aujourd_hui:
            data["appels_jour"] = 0
            data["dernier_reset_jour"] = aujourd_hui
            logger.info("🔄 Reset quota journalier")

        # Reset horaire
        heure_actuelle = datetime.now().replace(minute=0, second=0, microsecond=0)
        if data["dernier_reset_heure"] != heure_actuelle:
            data["appels_heure"] = 0
            data["dernier_reset_heure"] = heure_actuelle
            logger.info("🔄 Reset quota horaire")

        RateLimitIA._sauvegarder_data(data)

        # Vérifier limites
        if data["appels_jour"] >= AI_RATE_LIMIT_DAILY:
            return False, f"⏳ Limite quotidienne atteinte ({AI_RATE_LIMIT_DAILY} appels/jour)"

        if data["appels_heure"] >= AI_RATE_LIMIT_HOURLY:
            return False, f"⏳ Limite horaire atteinte ({AI_RATE_LIMIT_HOURLY} appels/heure)"

        return True, ""

    @staticmethod
    def enregistrer_appel(service: str = "unknown", tokens_utilises: int = 0):
        """
        Enregistre un appel IA.

        Args:
            service: Nom du service appelant
            tokens_utilises: Nombre de tokens utilisés
        """
        RateLimitIA._initialiser()
        data = RateLimitIA._obtenir_data()

        data["appels_jour"] += 1
        data["appels_heure"] += 1

        # Historique pour analytics
        data["historique"].append(
            {"timestamp": datetime.now(), "service": service, "tokens": tokens_utilises}
        )

        # Limiter historique (garder 100 derniers appels)
        if len(data["historique"]) > 100:
            data["historique"] = data["historique"][-100:]

        RateLimitIA._sauvegarder_data(data)
        logger.debug(f"[OK] Appel IA enregistré ({service})")

    @staticmethod
    def obtenir_statistiques() -> dict:
        """
        Retourne les statistiques de rate limiting.

        Returns:
            Dict avec compteurs et métriques
        """
        RateLimitIA._initialiser()
        data = RateLimitIA._obtenir_data()

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
        data = RateLimitIA._obtenir_data()
        data["appels_jour"] = 0
        data["appels_heure"] = 0
        RateLimitIA._sauvegarder_data(data)
        logger.warning("[!] Reset manuel des quotas IA")


# ═══════════════════════════════════════════════════════════
# ALIAS COMPATIBILITÉ (pour imports existants)
# ═══════════════════════════════════════════════════════════

# Permet d'importer depuis cache.py OU ai/rate_limit.py
LimiteDebit = RateLimitIA

__all__ = ["RateLimitIA", "LimiteDebit"]
