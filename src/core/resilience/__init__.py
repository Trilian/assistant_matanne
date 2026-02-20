"""
Resilience - Politiques de résilience composables.

Fournit des stratégies réutilisables :
- RetryPolicy: Retentatives avec backoff
- TimeoutPolicy: Timeouts configurables
- BulkheadPolicy: Isolation des ressources
- FallbackPolicy: Valeurs de repli

Toutes les policies sont composables via l'opérateur ``+``

Usage::
    from src.core.resilience import RetryPolicy, TimeoutPolicy, politique_api_externe

    # Policy simple
    policy = RetryPolicy(max_tentatives=3, delai_base=1.0)
    result = policy.executer(lambda: api.call())

    # Policies composées
    policy = TimeoutPolicy(30) + RetryPolicy(3) + BulkheadPolicy(5)
    result = policy.executer(lambda: api.call())

    # Factory pré-configurée
    result = politique_api_externe().executer(lambda: api.call())
"""

from .policies import (
    BulkheadPolicy,
    FallbackPolicy,
    Policy,
    PolicyComposee,
    RetryPolicy,
    TimeoutPolicy,
    politique_api_externe,
    politique_base_de_donnees,
    politique_cache,
    politique_ia,
)

__all__ = [
    "Policy",
    "RetryPolicy",
    "TimeoutPolicy",
    "BulkheadPolicy",
    "FallbackPolicy",
    "PolicyComposee",
    "politique_api_externe",
    "politique_base_de_donnees",
    "politique_cache",
    "politique_ia",
]
