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
    limiter_module.limiteur_debit = LimiteurDebit()


def configurer_limites(config: ConfigLimitationDebit):
    """Configure les limites globales."""
    from . import config as config_module
    from . import limiter as limiter_module

    config_module.config_limitation_debit = config
    limiter_module.limiteur_debit = LimiteurDebit(config=config)
