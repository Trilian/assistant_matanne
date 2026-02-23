"""
Vérification de santé globale du système.

Agrège la santé de tous les sous-systèmes (base de données, cache, IA,
event bus) dans un rapport unifié.

Trois niveaux de probes (style Kubernetes) :

- **Liveness**: Le processus est-il vivant ? (rapide, ~1 ms)
- **Readiness**: Peut-il servir du trafic ? (vérifie DB + cache, ~100 ms)
- **Startup**: A-t-il fini de s'initialiser ? (vérifie config + migrations)

Usage::

    from src.core.monitoring import verifier_sante_globale
    from src.core.monitoring.health import verifier_liveness, verifier_readiness

    # Kubernetes-style probes
    liveness = verifier_liveness()     # {"vivant": True}
    readiness = verifier_readiness()   # {"pret": True, "composants": {...}}

    # Full health check (dashboard)
    rapport = verifier_sante_globale()
    # {"sain": True, "composants": {"db": {...}, "cache": {...}, ...}}
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable

logger = logging.getLogger(__name__)


# ───────────────────────────────────────────────────────────
# TYPES
# ───────────────────────────────────────────────────────────


class StatutSante(Enum):
    """États de santé d'un composant."""

    SAIN = auto()
    DEGRADE = auto()
    CRITIQUE = auto()
    INCONNU = auto()


@dataclass
class SanteComposant:
    """Rapport de santé pour un composant."""

    nom: str
    statut: StatutSante
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    duree_verification_ms: float = 0.0


@dataclass
class SanteSysteme:
    """Rapport de santé global du système."""

    sain: bool
    timestamp: float = field(default_factory=time.time)
    composants: dict[str, SanteComposant] = field(default_factory=dict)

    def vers_dict(self) -> dict[str, Any]:
        """Convertit en dictionnaire pour sérialisation."""
        return {
            "sain": self.sain,
            "timestamp": self.timestamp,
            "composants": {
                nom: {
                    "statut": comp.statut.name,
                    "message": comp.message,
                    "details": comp.details,
                    "duree_ms": comp.duree_verification_ms,
                }
                for nom, comp in self.composants.items()
            },
        }


# ───────────────────────────────────────────────────────────
# REGISTRY DES VÉRIFICATIONS
# ───────────────────────────────────────────────────────────

_verifications: dict[str, Callable[[], SanteComposant]] = {}


def enregistrer_verification(nom: str, fn: Callable[[], SanteComposant]) -> None:
    """Enregistre une fonction de vérification de santé."""
    _verifications[nom] = fn


# ───────────────────────────────────────────────────────────
# VÉRIFICATIONS BUILT-IN
# ───────────────────────────────────────────────────────────


def _verifier_db() -> SanteComposant:
    """Vérifie la santé de la base de données."""
    start = time.perf_counter()
    try:
        from src.core.db import verifier_connexion

        ok, message = verifier_connexion()
        duree = (time.perf_counter() - start) * 1000

        return SanteComposant(
            nom="database",
            statut=StatutSante.SAIN if ok else StatutSante.CRITIQUE,
            message=message,
            duree_verification_ms=duree,
        )
    except Exception as e:
        duree = (time.perf_counter() - start) * 1000
        return SanteComposant(
            nom="database",
            statut=StatutSante.CRITIQUE,
            message=f"Erreur: {e}",
            duree_verification_ms=duree,
        )


def _verifier_cache() -> SanteComposant:
    """Vérifie la santé du cache multi-niveaux."""
    start = time.perf_counter()
    try:
        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        stats = cache.obtenir_statistiques()
        duree = (time.perf_counter() - start) * 1000

        hit_rate = stats.get("hit_rate", 0)
        statut = StatutSante.SAIN
        if hit_rate < 0.3 and stats.get("total_requetes", 0) > 100:
            statut = StatutSante.DEGRADE

        return SanteComposant(
            nom="cache",
            statut=statut,
            message=f"Hit rate: {hit_rate:.1%}",
            details=stats,
            duree_verification_ms=duree,
        )
    except Exception as e:
        duree = (time.perf_counter() - start) * 1000
        return SanteComposant(
            nom="cache",
            statut=StatutSante.DEGRADE,
            message=f"Erreur: {e}",
            duree_verification_ms=duree,
        )


def _verifier_ia() -> SanteComposant:
    """Vérifie l'état du rate limiter IA."""
    start = time.perf_counter()
    try:
        from src.core.ai.rate_limit import RateLimitIA

        limiter = RateLimitIA()
        stats = limiter.obtenir_statistiques()
        duree = (time.perf_counter() - start) * 1000

        appels_jour = stats.get("appels_jour", 0)
        limite_jour = stats.get("limite_jour", 100)
        ratio = appels_jour / max(limite_jour, 1)

        statut = StatutSante.SAIN
        if ratio > 0.9:
            statut = StatutSante.CRITIQUE
        elif ratio > 0.7:
            statut = StatutSante.DEGRADE

        return SanteComposant(
            nom="ia",
            statut=statut,
            message=f"Appels: {appels_jour}/{limite_jour}",
            details=stats,
            duree_verification_ms=duree,
        )
    except Exception as e:
        duree = (time.perf_counter() - start) * 1000
        return SanteComposant(
            nom="ia",
            statut=StatutSante.INCONNU,
            message=f"Erreur: {e}",
            duree_verification_ms=duree,
        )


def _verifier_metriques() -> SanteComposant:
    """Vérifie l'état du collecteur de métriques."""
    start = time.perf_counter()
    try:
        from .collector import collecteur

        snap = collecteur.snapshot()
        duree = (time.perf_counter() - start) * 1000

        nb_metriques = len(snap.get("metriques", {}))
        uptime = snap.get("uptime_seconds", 0)

        return SanteComposant(
            nom="metriques",
            statut=StatutSante.SAIN,
            message=f"{nb_metriques} métriques, uptime {uptime:.0f}s",
            details={"nb_metriques": nb_metriques, "uptime_seconds": uptime},
            duree_verification_ms=duree,
        )
    except Exception as e:
        duree = (time.perf_counter() - start) * 1000
        return SanteComposant(
            nom="metriques",
            statut=StatutSante.DEGRADE,
            message=f"Erreur: {e}",
            duree_verification_ms=duree,
        )


# ───────────────────────────────────────────────────────────
# VÉRIFICATION GLOBALE
# ───────────────────────────────────────────────────────────


def verifier_sante_globale(inclure_db: bool = True) -> SanteSysteme:
    """Exécute toutes les vérifications de santé et retourne un rapport.

    Parameters
    ----------
    inclure_db : bool
        Si True, inclut la vérification de la base de données
        (peut être lent en cas de timeout réseau).

    Returns
    -------
    SanteSysteme
        Rapport global avec le statut de chaque composant.
    """
    composants: dict[str, SanteComposant] = {}

    # Built-in checks
    checks: dict[str, Callable[[], SanteComposant]] = {
        "cache": _verifier_cache,
        "ia": _verifier_ia,
        "metriques": _verifier_metriques,
    }
    if inclure_db:
        checks["database"] = _verifier_db

    # Custom registered checks
    checks.update(_verifications)

    for nom, fn in checks.items():
        try:
            composants[nom] = fn()
        except Exception as e:
            logger.error("Erreur vérification santé '%s': %s", nom, e)
            composants[nom] = SanteComposant(
                nom=nom,
                statut=StatutSante.INCONNU,
                message=f"Erreur inattendue: {e}",
            )

    # Le système est sain si aucun composant n'est CRITIQUE
    sain = all(c.statut != StatutSante.CRITIQUE for c in composants.values())

    return SanteSysteme(sain=sain, composants=composants)


# ───────────────────────────────────────────────────────────
# PROBES KUBERNETES-STYLE
# ───────────────────────────────────────────────────────────


class TypeVerification(Enum):
    """Types de probes de santé."""

    LIVENESS = auto()
    READINESS = auto()
    STARTUP = auto()


def verifier_liveness() -> dict[str, Any]:
    """Probe *liveness* — le processus est-il vivant ?

    Très rapide (~1 ms). Vérifie uniquement que l'interpréteur Python
    fonctionne et que le module applicatif est importable.

    Returns:
        ``{"vivant": True, "pid": <pid>}``
    """
    import os

    return {"vivant": True, "pid": os.getpid()}


def verifier_readiness() -> dict[str, Any]:
    """Probe *readiness* — l'application peut-elle servir du trafic ?

    Vérifie les dépendances critiques (DB, cache) sans inclure les
    composants optionnels (IA, métriques).

    Returns:
        ``{"pret": bool, "composants": {...}}``
    """
    composants: dict[str, SanteComposant] = {}

    for nom, fn in [("database", _verifier_db), ("cache", _verifier_cache)]:
        try:
            composants[nom] = fn()
        except Exception as e:
            composants[nom] = SanteComposant(
                nom=nom,
                statut=StatutSante.CRITIQUE,
                message=str(e),
            )

    pret = all(c.statut != StatutSante.CRITIQUE for c in composants.values())
    return {
        "pret": pret,
        "composants": {
            nom: {"statut": c.statut.name, "message": c.message} for nom, c in composants.items()
        },
    }


def verifier_startup() -> dict[str, Any]:
    """Probe *startup* — l'application a-t-elle fini de s'initialiser ?

    Vérifie que la configuration est chargée et que la base de données
    est accessible.

    Returns:
        ``{"initialise": bool, "details": {...}}``
    """
    details: dict[str, bool] = {}

    # Config chargée ?
    try:
        from src.core.config import obtenir_parametres

        params = obtenir_parametres()
        details["config"] = params is not None
    except Exception:
        details["config"] = False

    # DB accessible ?
    try:
        from src.core.db import verifier_connexion

        ok, _ = verifier_connexion()
        details["database"] = ok
    except Exception:
        details["database"] = False

    return {
        "initialise": all(details.values()),
        "details": details,
    }
