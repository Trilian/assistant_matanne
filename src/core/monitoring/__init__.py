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
from .rerun_profiler import (
    RerunProfiler,
    RerunRecord,
    obtenir_stats_rerun,
    profiler_rerun,
    reset_profiler,
)
from .sentry import (
    ajouter_breadcrumb,
    capturer_exception,
    capturer_message,
    definir_utilisateur,
    est_sentry_actif,
    initialiser_sentry,
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
    # Rerun Profiler
    "RerunProfiler",
    "RerunRecord",
    "obtenir_stats_rerun",
    "profiler_rerun",
    "reset_profiler",
    # Sentry
    "ajouter_breadcrumb",
    "capturer_exception",
    "capturer_message",
    "definir_utilisateur",
    "est_sentry_actif",
    "initialiser_sentry",
]
