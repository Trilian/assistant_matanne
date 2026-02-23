"""
Package de Limitation de Débit pour l'API REST.

Implémente la limitation de débit avec:
- Limites par IP
- Limites par utilisateur authentifié
- Limites par endpoint
- Stockage en mémoire ou Redis
"""

# Configuration
from .config import (
    ConfigLimitationDebit,
    StrategieLimitationDebit,
    config_limitation_debit,
)

# Dépendances FastAPI
from .dependencies import (
    verifier_limite_debit,
    verifier_limite_debit_ia,
)

# Limiteur principal
from .limiter import (
    LimiteurDebit,
    limiteur_debit,
)

# Middleware
from .middleware import MiddlewareLimitationDebit

# Stockage Redis (production)
from .redis_storage import (
    StockageRedis,
    obtenir_stockage_optimal,
)

# Stockage
from .storage import (
    StockageLimitationDebit,
    _stockage,
)

# Utilitaires
from .utils import (
    configurer_limites,
    obtenir_stats_limitation,
    reinitialiser_limites,
)

__all__ = [
    # Config
    "StrategieLimitationDebit",
    "ConfigLimitationDebit",
    "config_limitation_debit",
    # Storage
    "StockageLimitationDebit",
    "_stockage",
    "StockageRedis",
    "obtenir_stockage_optimal",
    # Limiter
    "LimiteurDebit",
    "limiteur_debit",
    # Middleware
    "MiddlewareLimitationDebit",
    # Dependencies
    "verifier_limite_debit",
    "verifier_limite_debit_ia",
    # Utils
    "obtenir_stats_limitation",
    "reinitialiser_limites",
    "configurer_limites",
]
