"""
Rate Limiting IA - Gestion des quotas API Mistral

Ce module gère le rate limiting spécifique aux appels IA :
- Quotas journaliers et horaires par utilisateur
- Quotas globaux (protection API Mistral)
- Reset automatique
- Statistiques d'utilisation

Utilise un dict en mémoire pour le stockage des compteurs.
"""

import logging
from datetime import datetime
from typing import Any

from ..constants import AI_RATE_LIMIT_DAILY, AI_RATE_LIMIT_HOURLY

logger = logging.getLogger(__name__)

# Stockage en mémoire pour les compteurs de rate limiting
_rate_limit_store: dict[str, Any] = {}

# Tracking granulaire par service (tokens + appels)
_service_tracking: dict[str, dict[str, Any]] = {}

# Quotas par utilisateur (fraction du quota global)
_USER_DAILY_LIMIT = max(AI_RATE_LIMIT_DAILY // 5, 10)
_USER_HOURLY_LIMIT = max(AI_RATE_LIMIT_HOURLY // 5, 5)


def _obtenir_cle_user(user_id: str) -> str:
    """Retourne la clé de stockage pour un utilisateur."""
    return f"rate_limit_ia_user:{user_id}"


class RateLimitIA:
    """
    Rate limiting spécifique pour les appels IA.

    Gère les quotas API Mistral avec reset automatique.
    Supporte les quotas par utilisateur et globaux.
    """

    CLE_RATE_LIMIT = "rate_limit_ia"
    """Clé de stockage global."""

    @staticmethod
    def _obtenir_storage():
        """Retourne le backend de stockage."""
        return _rate_limit_store

    @staticmethod
    def _initialiser(cle: str | None = None):
        """Initialise les compteurs dans le storage."""
        storage = RateLimitIA._obtenir_storage()
        target_key = cle or RateLimitIA.CLE_RATE_LIMIT
        if target_key not in storage:
            storage[target_key] = {
                "appels_jour": 0,
                "appels_heure": 0,
                "dernier_reset_jour": datetime.now().date(),
                "dernier_reset_heure": datetime.now().replace(minute=0, second=0, microsecond=0),
                "historique": [],
            }

    @staticmethod
    def _obtenir_data(cle: str | None = None) -> dict:
        """Retourne les données de rate limiting."""
        storage = RateLimitIA._obtenir_storage()
        target_key = cle or RateLimitIA.CLE_RATE_LIMIT
        return storage.get(target_key, {})

    @staticmethod
    def _sauvegarder_data(data: dict, cle: str | None = None):
        """Sauvegarde les données de rate limiting."""
        storage = RateLimitIA._obtenir_storage()
        target_key = cle or RateLimitIA.CLE_RATE_LIMIT
        storage[target_key] = data

    @staticmethod
    def _reset_si_necessaire(data: dict) -> None:
        """Reset les compteurs si la période a changé."""
        aujourd_hui = datetime.now().date()
        if data["dernier_reset_jour"] != aujourd_hui:
            data["appels_jour"] = 0
            data["dernier_reset_jour"] = aujourd_hui

        heure_actuelle = datetime.now().replace(minute=0, second=0, microsecond=0)
        if data["dernier_reset_heure"] != heure_actuelle:
            data["appels_heure"] = 0
            data["dernier_reset_heure"] = heure_actuelle

    @staticmethod
    def peut_appeler(user_id: str | None = None) -> tuple[bool, str]:
        """
        Vérifie si un appel IA est autorisé.

        Args:
            user_id: ID utilisateur pour le quota per-user. Si None, vérifie uniquement le quota global.

        Returns:
            Tuple (autorisé, message_erreur)
        """
        # Vérification quota global
        RateLimitIA._initialiser()
        data = RateLimitIA._obtenir_data()
        RateLimitIA._reset_si_necessaire(data)
        RateLimitIA._sauvegarder_data(data)

        if data["appels_jour"] >= AI_RATE_LIMIT_DAILY:
            return (
                False,
                f"⏳ Limite quotidienne globale atteinte ({AI_RATE_LIMIT_DAILY} appels/jour)",
            )

        if data["appels_heure"] >= AI_RATE_LIMIT_HOURLY:
            return (
                False,
                f"⏳ Limite horaire globale atteinte ({AI_RATE_LIMIT_HOURLY} appels/heure)",
            )

        # Vérification quota per-user
        if user_id:
            cle_user = _obtenir_cle_user(user_id)
            RateLimitIA._initialiser(cle_user)
            data_user = RateLimitIA._obtenir_data(cle_user)
            RateLimitIA._reset_si_necessaire(data_user)
            RateLimitIA._sauvegarder_data(data_user, cle_user)

            if data_user["appels_jour"] >= _USER_DAILY_LIMIT:
                return (
                    False,
                    f"⏳ Votre limite quotidienne IA atteinte ({_USER_DAILY_LIMIT} appels/jour)",
                )

            if data_user["appels_heure"] >= _USER_HOURLY_LIMIT:
                return (
                    False,
                    f"⏳ Votre limite horaire IA atteinte ({_USER_HOURLY_LIMIT} appels/heure)",
                )

        return True, ""

    @staticmethod
    def enregistrer_appel(
        service: str = "unknown", tokens_utilises: int = 0, user_id: str | None = None
    ):
        """
        Enregistre un appel IA.

        Args:
            service: Nom du service appelant
            tokens_utilises: Nombre de tokens utilisés
            user_id: ID utilisateur pour le compteur per-user
        """
        # Compteur global
        RateLimitIA._initialiser()
        data = RateLimitIA._obtenir_data()

        data["appels_jour"] += 1
        data["appels_heure"] += 1

        # Historique pour analytics
        entry = {"timestamp": datetime.now(), "service": service, "tokens": tokens_utilises}
        if user_id:
            entry["user_id"] = user_id
        data["historique"].append(entry)

        # Limiter historique (garder 100 derniers appels)
        if len(data["historique"]) > 100:
            data["historique"] = data["historique"][-100:]

        RateLimitIA._sauvegarder_data(data)

        # Compteur per-user
        if user_id:
            cle_user = _obtenir_cle_user(user_id)
            RateLimitIA._initialiser(cle_user)
            data_user = RateLimitIA._obtenir_data(cle_user)
            data_user["appels_jour"] += 1
            data_user["appels_heure"] += 1
            data_user["historique"].append(entry)
            if len(data_user["historique"]) > 50:
                data_user["historique"] = data_user["historique"][-50:]
            RateLimitIA._sauvegarder_data(data_user, cle_user)

        logger.debug(f"[OK] Appel IA enregistré ({service}, user={user_id})")

        # Tracking granulaire par service
        RateLimitIA._tracker_service(service, tokens_utilises)

    @staticmethod
    def _tracker_service(service: str, tokens: int) -> None:
        """Met à jour le compteur granulaire pour un service donné."""
        aujourd_hui = datetime.now().date().isoformat()
        if service not in _service_tracking:
            _service_tracking[service] = {
                "total_appels": 0,
                "total_tokens": 0,
                "par_jour": {},
            }
        st = _service_tracking[service]
        st["total_appels"] += 1
        st["total_tokens"] += tokens
        jour = st["par_jour"].setdefault(aujourd_hui, {"appels": 0, "tokens": 0})
        jour["appels"] += 1
        jour["tokens"] += tokens
        # Garder 30 jours max
        if len(st["par_jour"]) > 30:
            cles_triees = sorted(st["par_jour"].keys())
            for cle in cles_triees[:-30]:
                del st["par_jour"][cle]

    @staticmethod
    def obtenir_stats_par_service() -> dict[str, Any]:
        """Retourne les stats granulaires de consommation IA par service.

        Returns:
            Dict {service_name: {total_appels, total_tokens, par_jour: {date: {appels, tokens}}}}
        """
        return dict(_service_tracking)

    @staticmethod
    def obtenir_classement_services() -> list[dict[str, Any]]:
        """Retourne les services classés par consommation de tokens (desc).

        Returns:
            Liste de dicts triés par total_tokens décroissant.
        """
        classement = []
        for service, data in _service_tracking.items():
            classement.append(
                {
                    "service": service,
                    "total_appels": data["total_appels"],
                    "total_tokens": data["total_tokens"],
                    "tokens_moyen": (
                        data["total_tokens"] // data["total_appels"]
                        if data["total_appels"] > 0
                        else 0
                    ),
                }
            )
        classement.sort(key=lambda x: x["total_tokens"], reverse=True)
        return classement

    @staticmethod
    def obtenir_statistiques(user_id: str | None = None) -> dict:
        """
        Retourne les statistiques de rate limiting.

        Args:
            user_id: Si fourni, inclut les stats per-user.

        Returns:
            Dict avec compteurs et métriques
        """
        RateLimitIA._initialiser()
        data = RateLimitIA._obtenir_data()

        # Calcul répartition par service
        services_usage: dict[str, int] = {}
        for appel in data["historique"]:
            service = appel["service"]
            services_usage[service] = services_usage.get(service, 0) + 1

        stats = {
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
            "tokens_par_service": {svc: d["total_tokens"] for svc, d in _service_tracking.items()},
            "classement_services": RateLimitIA.obtenir_classement_services()[:10],
        }

        # Stats per-user si demandé
        if user_id:
            cle_user = _obtenir_cle_user(user_id)
            RateLimitIA._initialiser(cle_user)
            data_user = RateLimitIA._obtenir_data(cle_user)
            RateLimitIA._reset_si_necessaire(data_user)
            stats["utilisateur"] = {
                "user_id": user_id,
                "appels_jour": data_user["appels_jour"],
                "limite_jour": _USER_DAILY_LIMIT,
                "restant_jour": _USER_DAILY_LIMIT - data_user["appels_jour"],
                "appels_heure": data_user["appels_heure"],
                "limite_heure": _USER_HOURLY_LIMIT,
                "restant_heure": _USER_HOURLY_LIMIT - data_user["appels_heure"],
            }

        return stats

    @staticmethod
    def reset_quotas(user_id: str | None = None):
        """Reset manuel des quotas (debug/admin). Si user_id, reset uniquement cet utilisateur."""
        if user_id:
            cle_user = _obtenir_cle_user(user_id)
            RateLimitIA._initialiser(cle_user)
            data_user = RateLimitIA._obtenir_data(cle_user)
            data_user["appels_jour"] = 0
            data_user["appels_heure"] = 0
            RateLimitIA._sauvegarder_data(data_user, cle_user)
            logger.warning("[!] Reset manuel des quotas IA pour l'utilisateur %s", user_id)
        else:
            RateLimitIA._initialiser()
            data = RateLimitIA._obtenir_data()
            data["appels_jour"] = 0
            data["appels_heure"] = 0
            RateLimitIA._sauvegarder_data(data)
            logger.warning("[!] Reset manuel des quotas IA globaux")


# ═══════════════════════════════════════════════════════════
# ALIAS COMPATIBILITÉ (pour imports existants)
# ═══════════════════════════════════════════════════════════

# Permet d'importer depuis cache.py OU ai/rate_limit.py
LimiteDebit = RateLimitIA

__all__ = ["RateLimitIA", "LimiteDebit"]
