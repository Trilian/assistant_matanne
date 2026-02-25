"""
Resilience - Politiques de résilience composables.

Fournit des stratégies réutilisables :
- RetryPolicy: Retentatives avec backoff
- TimeoutPolicy: Timeouts configurables
- BulkheadPolicy: Isolation des ressources
- FallbackPolicy: Valeurs de repli

Toutes les policies sont composables via l'opérateur ``+``

Usage::
    from src.core.resilience import RetryPolicy, TimeoutPolicy

    # Policy simple
    policy = RetryPolicy(max_tentatives=3, delai_base=1.0)
    result = policy.executer(lambda: api.call())

    # Policies composées
    policy = TimeoutPolicy(30) + RetryPolicy(3) + BulkheadPolicy(5)
    result = policy.executer(lambda: api.call())

Note: ``executer()`` retourne directement le résultat (T) ou lève une exception.
"""

from .policies import (
    BulkheadPolicy,
    FallbackPolicy,
    Policy,
    PolicyComposee,
    RetryPolicy,
    TimeoutPolicy,
)

__all__ = [
    "Policy",
    "RetryPolicy",
    "TimeoutPolicy",
    "BulkheadPolicy",
    "FallbackPolicy",
    "PolicyComposee",
]
