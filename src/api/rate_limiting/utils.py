"""
Utilitaires pour la limitation de débit.
"""

from typing import Any

from .config import ConfigLimitationDebit, config_limitation_debit
from .limiter import LimiteurDebit
from .storage import StockageLimitationDebit, _stockage


def obtenir_stats_limitation() -> dict[str, Any]:
    """Retourne les statistiques de limitation de débit."""
    return {
        "cles_actives": len(_stockage._store),
        "cles_bloquees": len(_stockage._lock_store),
        "configuration": {
            "requetes_par_minute": config_limitation_debit.requetes_par_minute,
            "requetes_par_heure": config_limitation_debit.requetes_par_heure,
            "requetes_ia_par_minute": config_limitation_debit.requetes_ia_par_minute,
        },
    }


def reinitialiser_limites():
    """Réinitialise tous les compteurs (pour les tests)."""
    from . import limiter as limiter_module
    from . import storage

    storage._stockage = StockageLimitationDebit()
    storage._store = storage._stockage
    limiter_module.limiteur_debit = LimiteurDebit()
    limiter_module.rate_limiter = limiter_module.limiteur_debit


def configurer_limites(config: ConfigLimitationDebit):
    """Configure les limites globales."""
    from . import config as config_module
    from . import limiter as limiter_module

    config_module.config_limitation_debit = config
    config_module.rate_limit_config = config
    limiter_module.limiteur_debit = LimiteurDebit(config=config)
    limiter_module.rate_limiter = limiter_module.limiteur_debit


# Alias anglais
def get_rate_limit_stats() -> dict[str, Any]:
    return obtenir_stats_limitation()


def reset_rate_limits():
    return reinitialiser_limites()


def configure_rate_limits(config: ConfigLimitationDebit):
    return configurer_limites(config)
