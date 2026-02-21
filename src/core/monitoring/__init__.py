"""
Package monitoring — Collecte centralisée de métriques & observabilité.

Expose un collecteur global thread-safe qui agrège les métriques de
tous les sous-systèmes (IA, cache, base de données, modules).

Usage::

    from src.core.monitoring import collecteur, enregistrer_metrique, MetriqueType

    # Enregistrer un appel IA
    enregistrer_metrique("ia.appel", 1, MetriqueType.COMPTEUR, labels={"service": "recettes"})

    # Enregistrer une latence
    enregistrer_metrique("ia.latence_ms", 342.5, MetriqueType.HISTOGRAMME)

    # Décorateur de timing automatique
    from src.core.monitoring import chronometre

    @chronometre("recettes.generation")
    def generer_recettes():
        ...

    # Snapshot complet
    snapshot = collecteur.snapshot()
"""

from .collector import (
    CollecteurMetriques,
    MetriqueType,
    PointMetrique,
    collecteur,
    enregistrer_metrique,
    obtenir_snapshot,
    reinitialiser_collecteur,
)
from .decorators import chronometre
from .health import (
    SanteSysteme,
    TypeVerification,
    verifier_liveness,
    verifier_readiness,
    verifier_sante_globale,
    verifier_startup,
)

__all__ = [
    "CollecteurMetriques",
    "MetriqueType",
    "PointMetrique",
    "SanteSysteme",
    "TypeVerification",
    "chronometre",
    "collecteur",
    "enregistrer_metrique",
    "obtenir_snapshot",
    "reinitialiser_collecteur",
    "verifier_liveness",
    "verifier_readiness",
    "verifier_sante_globale",
    "verifier_startup",
]
