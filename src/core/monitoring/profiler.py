"""
Profiler - Profiling des fonctions et décorateurs de performance.

Fonctionnalités:
- Profiling automatique des fonctions
- Mesure du temps d'exécution
- Statistiques détaillées par fonction
- Décorateurs utilitaires (debounce, throttle)
"""

import functools
import logging
import threading
import time
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime

import streamlit as st

logger = logging.getLogger(__name__)


@dataclass
class MetriquePerformance:
    """Métrique de performance individuelle."""

    name: str
    duration_ms: float
    timestamp: datetime = field(default_factory=datetime.now)
    memory_delta_kb: float = 0
    metadata: dict = field(default_factory=dict)


@dataclass
class StatistiquesFonction:
    """Statistiques d'une fonction."""

    call_count: int = 0
    total_time_ms: float = 0
    min_time_ms: float = float("inf")
    max_time_ms: float = 0
    avg_time_ms: float = 0
    last_call: datetime | None = None
    errors: int = 0


class ProfileurFonction:
    """
    Profiler pour mesurer les performances des fonctions.

    Collecte automatiquement:
    - Temps d'exécution
    - Nombre d'appels
    - Min/Max/Moyenne
    - Erreurs
    """

    SESSION_KEY = "_function_profiler_stats"

    @classmethod
    def _get_stats(cls) -> dict[str, StatistiquesFonction]:
        """Récupère les stats depuis session."""
        if cls.SESSION_KEY not in st.session_state:
            st.session_state[cls.SESSION_KEY] = {}
        return st.session_state[cls.SESSION_KEY]

    @classmethod
    def enregistrer(cls, func_name: str, duration_ms: float, error: bool = False) -> None:
        """Enregistre une exécution."""
        stats = cls._get_stats()

        if func_name not in stats:
            stats[func_name] = StatistiquesFonction()

        s = stats[func_name]
        s.call_count += 1
        s.total_time_ms += duration_ms
        s.min_time_ms = min(s.min_time_ms, duration_ms)
        s.max_time_ms = max(s.max_time_ms, duration_ms)
        s.avg_time_ms = s.total_time_ms / s.call_count
        s.last_call = datetime.now()

        if error:
            s.errors += 1

    @classmethod
    def obtenir_toutes_stats(cls) -> dict[str, StatistiquesFonction]:
        """Retourne toutes les stats."""
        return cls._get_stats()

    @classmethod
    def obtenir_plus_lentes(cls, n: int = 5) -> list[tuple[str, StatistiquesFonction]]:
        """Retourne les N fonctions les plus lentes."""
        stats = cls._get_stats()
        sorted_stats = sorted(stats.items(), key=lambda x: x[1].avg_time_ms, reverse=True)
        return sorted_stats[:n]

    @classmethod
    def obtenir_plus_appelees(cls, n: int = 5) -> list[tuple[str, StatistiquesFonction]]:
        """Retourne les N fonctions les plus appelées."""
        stats = cls._get_stats()
        sorted_stats = sorted(stats.items(), key=lambda x: x[1].call_count, reverse=True)
        return sorted_stats[:n]

    @classmethod
    def effacer(cls) -> None:
        """Réinitialise les stats."""
        st.session_state[cls.SESSION_KEY] = {}


def profiler(func: Callable = None, *, name: str = None):
    """
    Décorateur pour profiler une fonction.

    Args:
        func: Fonction à profiler
        name: Nom personnalisé (défaut: nom de la fonction)

    Example:
        >>> @profiler
        >>> def ma_fonction():
        >>>     # code
        >>>
        >>> @profiler(name="traitement_lourd")
        >>> def process():
        >>>     # code
    """

    def decorator(fn: Callable):
        func_name = name or f"{fn.__module__}.{fn.__name__}"

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            error = False

            try:
                return fn(*args, **kwargs)
            except Exception:
                error = True
                raise
            finally:
                duration_ms = (time.perf_counter() - start) * 1000
                ProfileurFonction.enregistrer(func_name, duration_ms, error)

        return wrapper

    if func is not None:
        return decorator(func)
    return decorator


@contextmanager
def mesurer_temps(name: str):
    """
    Context manager pour mesurer le temps d'un bloc.

    Example:
        >>> with mesurer_temps("chargement_données"):
        >>>     data = load_data()
    """
    start = time.perf_counter()
    error = False

    try:
        yield
    except Exception:
        error = True
        raise
    finally:
        duration_ms = (time.perf_counter() - start) * 1000
        ProfileurFonction.enregistrer(name, duration_ms, error)
        logger.debug(f"⏱️ {name}: {duration_ms:.1f}ms")


class ChargeurComposant:
    """
    Lazy loader avancé pour composants UI Streamlit.

    Charge les composants uniquement quand ils sont visibles.
    """

    _loaded: set = set()

    @classmethod
    def composant_differe(
        cls,
        component_id: str,
        loader_func: Callable,
        placeholder_text: str = "Chargement...",
    ):
        """
        Charge un composant de manière lazy.

        Args:
            component_id: ID unique du composant
            loader_func: Fonction qui rend le composant
            placeholder_text: Texte pendant le chargement
        """
        # Vérifier si déjà chargé
        if component_id in cls._loaded:
            with mesurer_temps(f"component_{component_id}"):
                loader_func()
            return

        # Premier rendu - charger avec feedback
        with st.spinner(placeholder_text):
            with mesurer_temps(f"component_{component_id}_initial"):
                loader_func()

        cls._loaded.add(component_id)

    @classmethod
    def reset(cls):
        """Reset le tracker de composants."""
        cls._loaded.clear()


def antirrebond(wait_ms: int = 300):
    """
    Décorateur pour debouncer les appels fréquents.

    Utile pour les callbacks de recherche, filtres, etc.

    Args:
        wait_ms: Délai minimum entre appels

    Example:
        >>> @antirrebond(wait_ms=500)
        >>> def search(query: str):
        >>>     # Recherche exécutée max 1x/500ms
    """

    def decorator(func: Callable):
        last_call = {"time": 0}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time() * 1000

            if current_time - last_call["time"] < wait_ms:
                return None

            last_call["time"] = current_time
            return func(*args, **kwargs)

        return wrapper

    return decorator


def limiter_debit(max_calls: int = 10, period_seconds: int = 60):
    """
    Décorateur pour limiter le nombre d'appels par période.

    Args:
        max_calls: Nombre max d'appels
        period_seconds: Période en secondes

    Example:
        >>> @limiter_debit(max_calls=5, period_seconds=60)
        >>> def api_call():
        >>>     # Max 5 appels par minute
    """

    def decorator(func: Callable):
        calls = []
        lock = threading.Lock()

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal calls
            current_time = time.time()

            with lock:
                # Nettoyer anciens appels
                calls = [t for t in calls if current_time - t < period_seconds]

                if len(calls) >= max_calls:
                    logger.warning(f"Throttle: {func.__name__} rate limit atteint")
                    return None

                calls.append(current_time)

            return func(*args, **kwargs)

        return wrapper

    return decorator
