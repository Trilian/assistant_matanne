"""
Rerun Profiler — Analyse des reruns Streamlit et de leurs déclencheurs.

Streamlit re-exécute le script entier à chaque interaction widget.
Ce profiler trace les reruns, mesure leur durée et identifie les
déclencheurs (changements de session_state, interactions widget).

Intégré au ``CollecteurMetriques`` existant pour une observabilité unifiée.

Usage::

    from src.core.monitoring.rerun_profiler import profiler_rerun

    # Décorateur sur le point d'entrée du module
    @profiler_rerun("recettes")
    def app():
        st.title("Recettes")
        ...

    # Accès aux statistiques
    from src.core.monitoring.rerun_profiler import obtenir_stats_rerun
    stats = obtenir_stats_rerun()
    print(stats)  # {"total_reruns": 42, "duree_moyenne_ms": 85.3, ...}
"""

from __future__ import annotations

import logging
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable, TypeVar

from .collector import MetriqueType, enregistrer_metrique

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])

# Historique par défaut
_TAILLE_HISTORIQUE = 200


@dataclass(slots=True)
class RerunRecord:
    """Enregistrement d'un rerun Streamlit."""

    module: str
    timestamp: float
    duree_ms: float
    state_changes: list[str] = field(default_factory=list)


class RerunProfiler:
    """Profileur de reruns Streamlit avec métriques intégrées.

    Suit chaque rerun, mesure sa durée, détecte les changements
    de ``st.session_state`` qui l'ont déclenché.

    Thread-safe pour les accès concurrents.
    """

    def __init__(self, taille_historique: int = _TAILLE_HISTORIQUE) -> None:
        self._historique: deque[RerunRecord] = deque(maxlen=taille_historique)
        self._lock = threading.Lock()
        self._total_reruns: int = 0
        self._duree_totale_ms: float = 0.0

    def enregistrer(self, record: RerunRecord) -> None:
        """Enregistre un rerun dans l'historique.

        Émet aussi les métriques vers le collecteur global.
        """
        with self._lock:
            self._historique.append(record)
            self._total_reruns += 1
            self._duree_totale_ms += record.duree_ms

        # Métriques vers le collecteur global
        enregistrer_metrique(
            "rerun.count",
            1,
            MetriqueType.COMPTEUR,
            labels={"module": record.module},
        )
        enregistrer_metrique(
            "rerun.duree_ms",
            record.duree_ms,
            MetriqueType.HISTOGRAMME,
            labels={"module": record.module},
        )

        if record.duree_ms > 500:
            logger.warning(
                "Rerun lent: module=%s, durée=%.1fms, changes=%s",
                record.module,
                record.duree_ms,
                record.state_changes,
            )

    def stats(self) -> dict[str, Any]:
        """Retourne les statistiques agrégées des reruns.

        Returns:
            Dict avec total_reruns, duree_moyenne_ms, dernier_rerun,
            reruns_par_module, reruns_lents (>500ms)
        """
        with self._lock:
            if not self._historique:
                return {
                    "total_reruns": 0,
                    "duree_moyenne_ms": 0.0,
                    "dernier_rerun": None,
                    "reruns_par_module": {},
                    "reruns_lents": 0,
                }

            par_module: dict[str, int] = {}
            lents = 0
            for r in self._historique:
                par_module[r.module] = par_module.get(r.module, 0) + 1
                if r.duree_ms > 500:
                    lents += 1

            dernier = self._historique[-1]

            return {
                "total_reruns": self._total_reruns,
                "duree_moyenne_ms": round(self._duree_totale_ms / self._total_reruns, 1),
                "dernier_rerun": {
                    "module": dernier.module,
                    "duree_ms": round(dernier.duree_ms, 1),
                    "state_changes": dernier.state_changes,
                },
                "reruns_par_module": par_module,
                "reruns_lents": lents,
            }

    def reset(self) -> None:
        """Réinitialise l'historique et les compteurs."""
        with self._lock:
            self._historique.clear()
            self._total_reruns = 0
            self._duree_totale_ms = 0.0


# ═══════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════

_profiler = RerunProfiler()


# ═══════════════════════════════════════════════════════════
# API PUBLIQUE
# ═══════════════════════════════════════════════════════════


def profiler_rerun(module_name: str) -> Callable[[F], F]:
    """Décorateur qui profile les reruns d'un module Streamlit.

    Mesure la durée d'exécution et détecte les changements de
    ``st.session_state`` entre les reruns.

    Args:
        module_name: Nom du module (ex: "recettes", "planning")

    Usage::

        @profiler_rerun("recettes")
        def app():
            st.title("Recettes")
            ...
    """
    import functools

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Capturer l'état avant
            state_before = _capture_state_keys()

            start = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                duree_ms = (time.perf_counter() - start) * 1000

                # Détecter les changements de state
                state_after = _capture_state_keys()
                changes = list(state_after - state_before)

                record = RerunRecord(
                    module=module_name,
                    timestamp=time.time(),
                    duree_ms=duree_ms,
                    state_changes=changes,
                )
                _profiler.enregistrer(record)

        return wrapper  # type: ignore[return-value]

    return decorator


def _capture_state_keys() -> set[str]:
    """Capture les clés actuelles de st.session_state.

    Retourne un set vide si Streamlit n'est pas actif
    (ex: pendant les tests).
    """
    try:
        import streamlit as st

        return set(st.session_state.keys())
    except Exception:
        return set()


def obtenir_stats_rerun() -> dict[str, Any]:
    """Retourne les statistiques du profiler de reruns."""
    return _profiler.stats()


def reset_profiler() -> None:
    """Réinitialise le profiler (utile pour les tests)."""
    _profiler.reset()
