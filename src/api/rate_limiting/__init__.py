"""
Package de Limitation de Débit pour l'API REST.

Implémente la limitation de débit avec:
- Limites par IP
- Limites par utilisateur authentifié
- Limites par endpoint
- Stockage en mémoire ou Redis

Noms français avec alias anglais pour compatibilité.
"""

# Configuration
from .config import (
    ConfigLimitationDebit,
    RateLimitConfig,
    RateLimitStrategy,
    StrategieLimitationDebit,
    config_limitation_debit,
    rate_limit_config,
)

# Décorateurs
from .decorators import (
    limite_debit,
    rate_limit,
)

# Dépendances FastAPI
from .dependencies import (
    check_ai_rate_limit,
    check_rate_limit,
    verifier_limite_debit,
    verifier_limite_debit_ia,
)

# Limiteur principal
from .limiter import (
    LimiteurDebit,
    RateLimiter,
    limiteur_debit,
    rate_limiter,
)

# Middleware
from .middleware import (
    MiddlewareLimitationDebit,
    RateLimitMiddleware,
)

# Stockage
from .storage import (
    RateLimitStore,
    StockageLimitationDebit,
    _stockage,
    _store,
)

# Utilitaires
from .utils import (
    configure_rate_limits,
    configurer_limites,
    get_rate_limit_stats,
    obtenir_stats_limitation,
    reinitialiser_limites,
    reset_rate_limits,
)

__all__ = [
    # Config
    "StrategieLimitationDebit",
    "RateLimitStrategy",
    "ConfigLimitationDebit",
    "RateLimitConfig",
    "config_limitation_debit",
    "rate_limit_config",
    # Storage
    "StockageLimitationDebit",
    "RateLimitStore",
    "_stockage",
    "_store",
    # Limiter
    "LimiteurDebit",
    "RateLimiter",
    "limiteur_debit",
    "rate_limiter",
    # Middleware
    "MiddlewareLimitationDebit",
    "RateLimitMiddleware",
    # Decorators
    "limite_debit",
    "rate_limit",
    # Dependencies
    "verifier_limite_debit",
    "verifier_limite_debit_ia",
    "check_rate_limit",
    "check_ai_rate_limit",
    # Utils
    "obtenir_stats_limitation",
    "reinitialiser_limites",
    "configurer_limites",
    "get_rate_limit_stats",
    "reset_rate_limits",
    "configure_rate_limits",
]
