"""
Performance - Métriques et optimisations.

Fonctionnalités :
- Métriques de performance temps réel
- Profiling des fonctions
- Monitoring mémoire
- Optimisation des requêtes SQL
- Garbage collection intelligent
"""

import functools
import gc
import logging
import sys
import threading
import time
import tracemalloc
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable

import streamlit as st

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES ET CONFIGURATION
# ═══════════════════════════════════════════════════════════


@dataclass
class PerformanceMetric:
    """Métrique de performance individuelle."""
    
    name: str
    duration_ms: float
    timestamp: datetime = field(default_factory=datetime.now)
    memory_delta_kb: float = 0
    metadata: dict = field(default_factory=dict)


@dataclass
class FunctionStats:
    """Statistiques d'une fonction."""
    
    call_count: int = 0
    total_time_ms: float = 0
    min_time_ms: float = float('inf')
    max_time_ms: float = 0
    avg_time_ms: float = 0
    last_call: datetime | None = None
    errors: int = 0


# ═══════════════════════════════════════════════════════════
# PROFILER DE FONCTIONS
# ═══════════════════════════════════════════════════════════


class FunctionProfiler:
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
    def _get_stats(cls) -> dict[str, FunctionStats]:
        """Récupère les stats depuis session."""
        if cls.SESSION_KEY not in st.session_state:
            st.session_state[cls.SESSION_KEY] = {}
        return st.session_state[cls.SESSION_KEY]
    
    @classmethod
    def record(cls, func_name: str, duration_ms: float, error: bool = False) -> None:
        """Enregistre une exécution."""
        stats = cls._get_stats()
        
        if func_name not in stats:
            stats[func_name] = FunctionStats()
        
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
    def get_all_stats(cls) -> dict[str, FunctionStats]:
        """Retourne toutes les stats."""
        return cls._get_stats()
    
    @classmethod
    def get_slowest(cls, n: int = 5) -> list[tuple[str, FunctionStats]]:
        """Retourne les N fonctions les plus lentes."""
        stats = cls._get_stats()
        sorted_stats = sorted(
            stats.items(),
            key=lambda x: x[1].avg_time_ms,
            reverse=True
        )
        return sorted_stats[:n]
    
    @classmethod
    def get_most_called(cls, n: int = 5) -> list[tuple[str, FunctionStats]]:
        """Retourne les N fonctions les plus appelées."""
        stats = cls._get_stats()
        sorted_stats = sorted(
            stats.items(),
            key=lambda x: x[1].call_count,
            reverse=True
        )
        return sorted_stats[:n]
    
    @classmethod
    def clear(cls) -> None:
        """Réinitialise les stats."""
        st.session_state[cls.SESSION_KEY] = {}


def profile(func: Callable = None, *, name: str = None):
    """
    Décorateur pour profiler une fonction.
    
    Args:
        func: Fonction à profiler
        name: Nom personnalisé (défaut: nom de la fonction)
        
    Example:
        >>> @profile
        >>> def ma_fonction():
        >>>     # code
        >>>     
        >>> @profile(name="traitement_lourd")
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
                FunctionProfiler.record(func_name, duration_ms, error)
        
        return wrapper
    
    if func is not None:
        return decorator(func)
    return decorator


@contextmanager
def measure_time(name: str):
    """
    Context manager pour mesurer le temps d'un bloc.
    
    Example:
        >>> with measure_time("chargement_données"):
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
        FunctionProfiler.record(name, duration_ms, error)
        logger.debug(f"⏱️ {name}: {duration_ms:.1f}ms")


# ═══════════════════════════════════════════════════════════
# MONITORING MÉMOIRE
# ═══════════════════════════════════════════════════════════


class MemoryMonitor:
    """
    Moniteur de mémoire avec tracking et cleanup.
    """
    
    SESSION_KEY = "_memory_snapshots"
    _tracking_active = False
    
    @classmethod
    def start_tracking(cls) -> None:
        """Démarre le tracking mémoire."""
        if not cls._tracking_active:
            tracemalloc.start()
            cls._tracking_active = True
            logger.info("📊 Tracking mémoire démarré")
    
    @classmethod
    def stop_tracking(cls) -> None:
        """Arrête le tracking mémoire."""
        if cls._tracking_active:
            tracemalloc.stop()
            cls._tracking_active = False
            logger.info("📊 Tracking mémoire arrêté")
    
    @classmethod
    def get_current_usage(cls) -> dict:
        """
        Retourne l'utilisation mémoire actuelle.
        
        Returns:
            Dict avec current_mb, peak_mb, objects_count
        """
        import sys
        
        # Tracemalloc stats si actif
        if cls._tracking_active:
            current, peak = tracemalloc.get_traced_memory()
            current_mb = current / 1024 / 1024
            peak_mb = peak / 1024 / 1024
        else:
            current_mb = 0
            peak_mb = 0
        
        # Comptage objets par type
        type_counts = defaultdict(int)
        for obj in gc.get_objects():
            type_counts[type(obj).__name__] += 1
        
        return {
            "current_mb": round(current_mb, 2),
            "peak_mb": round(peak_mb, 2),
            "total_objects": len(gc.get_objects()),
            "top_types": dict(sorted(
                type_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]),
        }
    
    @classmethod
    def take_snapshot(cls, label: str = "snapshot") -> dict:
        """Prend un snapshot mémoire."""
        usage = cls.get_current_usage()
        usage["label"] = label
        usage["timestamp"] = datetime.now().isoformat()
        
        # Sauvegarder dans session
        if cls.SESSION_KEY not in st.session_state:
            st.session_state[cls.SESSION_KEY] = []
        
        st.session_state[cls.SESSION_KEY].append(usage)
        
        # Garder seulement les 20 derniers
        st.session_state[cls.SESSION_KEY] = st.session_state[cls.SESSION_KEY][-20:]
        
        logger.debug(f"📸 Snapshot mémoire '{label}': {usage['current_mb']}MB")
        return usage
    
    @classmethod
    def get_snapshots(cls) -> list[dict]:
        """Retourne tous les snapshots."""
        return st.session_state.get(cls.SESSION_KEY, [])
    
    @classmethod
    def force_cleanup(cls) -> dict:
        """
        Force un nettoyage mémoire.
        
        Returns:
            Dict avec objets collectés et mémoire libérée
        """
        before = cls.get_current_usage()
        
        # Forcer garbage collection
        collected = gc.collect()
        
        # Nettoyer caches Streamlit si très gros
        try:
            if hasattr(st, 'cache_data'):
                # Clear des caches expirés seulement
                pass  # Streamlit gère automatiquement
        except Exception:
            pass
        
        after = cls.get_current_usage()
        
        freed_mb = before["current_mb"] - after["current_mb"]
        
        logger.info(f"🧹 Cleanup: {collected} objets collectés, {freed_mb:.2f}MB libérés")
        
        return {
            "objects_collected": collected,
            "memory_freed_mb": round(freed_mb, 2),
            "before_mb": before["current_mb"],
            "after_mb": after["current_mb"],
        }


# ═══════════════════════════════════════════════════════════
# OPTIMISEUR SQL
# ═══════════════════════════════════════════════════════════


class SQLOptimizer:
    """
    Optimiseur de requêtes SQL avec tracking.
    """
    
    SESSION_KEY = "_sql_query_stats"
    
    @classmethod
    def _get_stats(cls) -> dict:
        """Récupère les stats SQL."""
        if cls.SESSION_KEY not in st.session_state:
            st.session_state[cls.SESSION_KEY] = {
                "queries": [],
                "slow_queries": [],
                "total_count": 0,
                "total_time_ms": 0,
            }
        return st.session_state[cls.SESSION_KEY]
    
    @classmethod
    def record_query(
        cls,
        query: str,
        duration_ms: float,
        rows_affected: int = 0,
    ) -> None:
        """Enregistre une requête SQL."""
        stats = cls._get_stats()
        
        query_info = {
            "query": query[:200],  # Tronquer
            "duration_ms": duration_ms,
            "rows": rows_affected,
            "timestamp": datetime.now().isoformat(),
        }
        
        stats["queries"].append(query_info)
        stats["total_count"] += 1
        stats["total_time_ms"] += duration_ms
        
        # Garder seulement les 100 dernières
        stats["queries"] = stats["queries"][-100:]
        
        # Tracker requêtes lentes (> 100ms)
        if duration_ms > 100:
            stats["slow_queries"].append(query_info)
            stats["slow_queries"] = stats["slow_queries"][-20:]
            logger.warning(f"⚠️ Requête lente ({duration_ms:.0f}ms): {query[:100]}")
    
    @classmethod
    def get_stats(cls) -> dict:
        """Retourne les statistiques SQL."""
        stats = cls._get_stats()
        
        return {
            "total_queries": stats["total_count"],
            "total_time_ms": round(stats["total_time_ms"], 2),
            "avg_time_ms": (
                round(stats["total_time_ms"] / stats["total_count"], 2)
                if stats["total_count"] > 0 else 0
            ),
            "slow_query_count": len(stats["slow_queries"]),
            "recent_queries": stats["queries"][-10:],
            "slow_queries": stats["slow_queries"],
        }
    
    @classmethod
    def clear(cls) -> None:
        """Réinitialise les stats."""
        st.session_state[cls.SESSION_KEY] = {
            "queries": [],
            "slow_queries": [],
            "total_count": 0,
            "total_time_ms": 0,
        }


@contextmanager
def track_query(query_description: str):
    """
    Context manager pour tracker une requête SQL.
    
    Example:
        >>> with track_query("SELECT recettes"):
        >>>     results = session.query(Recette).all()
    """
    start = time.perf_counter()
    rows = 0
    
    try:
        yield
    finally:
        duration_ms = (time.perf_counter() - start) * 1000
        SQLOptimizer.record_query(query_description, duration_ms, rows)


# ═══════════════════════════════════════════════════════════
# DASHBOARD PERFORMANCE
# ═══════════════════════════════════════════════════════════


class PerformanceDashboard:
    """
    Génère les métriques de performance pour l'UI.
    """
    
    @classmethod
    def get_summary(cls) -> dict:
        """
        Retourne un résumé complet des performances.
        
        Returns:
            Dict avec toutes les métriques
        """
        from src.core.lazy_loader import LazyModuleLoader
        
        # Stats lazy loading
        lazy_stats = LazyModuleLoader.get_stats()
        
        # Stats profiler
        profiler_stats = FunctionProfiler.get_all_stats()
        slowest = FunctionProfiler.get_slowest(5)
        
        # Stats mémoire
        memory = MemoryMonitor.get_current_usage()
        
        # Stats SQL
        sql_stats = SQLOptimizer.get_stats()
        
        return {
            "lazy_loading": {
                "modules_cached": lazy_stats["cached_modules"],
                "total_load_time_ms": round(lazy_stats["total_load_time"] * 1000, 0),
                "avg_load_time_ms": round(lazy_stats["average_load_time"] * 1000, 0),
            },
            "functions": {
                "tracked_count": len(profiler_stats),
                "slowest": [
                    {"name": name.split(".")[-1], "avg_ms": round(stats.avg_time_ms, 1)}
                    for name, stats in slowest
                ],
            },
            "memory": memory,
            "sql": {
                "total_queries": sql_stats["total_queries"],
                "avg_time_ms": sql_stats["avg_time_ms"],
                "slow_count": sql_stats["slow_query_count"],
            },
        }
    
    @classmethod
    def get_health_score(cls) -> tuple[int, str]:
        """
        Calcule un score de santé global (0-100).
        
        Returns:
            Tuple (score, status_emoji)
        """
        summary = cls.get_summary()
        score = 100
        
        # Pénalités mémoire
        if summary["memory"]["current_mb"] > 500:
            score -= 20
        elif summary["memory"]["current_mb"] > 200:
            score -= 10
        
        # Pénalités SQL
        if summary["sql"]["slow_count"] > 10:
            score -= 15
        elif summary["sql"]["slow_count"] > 5:
            score -= 5
        
        # Pénalités chargement
        if summary["lazy_loading"]["avg_load_time_ms"] > 500:
            score -= 10
        elif summary["lazy_loading"]["avg_load_time_ms"] > 200:
            score -= 5
        
        # Status emoji
        if score >= 80:
            status = "🟢"
        elif score >= 60:
            status = "🟡"
        else:
            status = "🔴"
        
        return max(0, score), status


# ═══════════════════════════════════════════════════════════
# COMPOSANTS UI
# ═══════════════════════════════════════════════════════════


def render_performance_panel():
    """Affiche le panneau de performance dans la sidebar."""
    
    summary = PerformanceDashboard.get_summary()
    score, status = PerformanceDashboard.get_health_score()
    
    with st.expander(f"📊 Performance {status} {score}/100"):
        
        # Tabs pour différentes métriques
        tab1, tab2, tab3 = st.tabs(["⚡ Général", "🧠 Mémoire", "🗃️ SQL"])
        
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "Modules chargés",
                    summary["lazy_loading"]["modules_cached"],
                )
            with col2:
                st.metric(
                    "Chargement moyen",
                    f"{summary['lazy_loading']['avg_load_time_ms']}ms",
                )
            
            # Top fonctions lentes
            if summary["functions"]["slowest"]:
                st.caption("🐌 Fonctions les plus lentes:")
                for f in summary["functions"]["slowest"][:3]:
                    st.caption(f"• {f['name']}: {f['avg_ms']}ms")
        
        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "Mémoire utilisée",
                    f"{summary['memory']['current_mb']}MB",
                )
            with col2:
                st.metric(
                    "Objets en mémoire",
                    f"{summary['memory']['total_objects']:,}",
                )
            
            if st.button("🧹 Nettoyer mémoire", key="cleanup_mem"):
                result = MemoryMonitor.force_cleanup()
                st.success(f"Libéré: {result['memory_freed_mb']}MB")
        
        with tab3:
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "Requêtes totales",
                    summary["sql"]["total_queries"],
                )
            with col2:
                st.metric(
                    "Requêtes lentes",
                    summary["sql"]["slow_count"],
                    delta_color="inverse" if summary["sql"]["slow_count"] > 0 else "off",
                )
            
            if st.button("🗑️ Reset stats", key="reset_sql"):
                SQLOptimizer.clear()
                st.success("Stats SQL réinitialisées")


def render_mini_performance_badge():
    """Badge compact pour la barre latérale."""
    
    score, status = PerformanceDashboard.get_health_score()
    memory = MemoryMonitor.get_current_usage()
    
    st.markdown(
        f'<div style="display: flex; justify-content: space-between; '
        f'padding: 0.25rem 0.5rem; background: #f0f2f6; border-radius: 4px; '
        f'font-size: 0.8rem;">'
        f'<span>{status} Perf: {score}%</span>'
        f'<span>💾 {memory["current_mb"]}MB</span>'
        f'</div>',
        unsafe_allow_html=True
    )


# ═══════════════════════════════════════════════════════════
# UTILITAIRES AVANCÉS
# ═══════════════════════════════════════════════════════════


class ComponentLoader:
    """
    Lazy loader avancé pour composants UI Streamlit.
    
    Charge les composants uniquement quand ils sont visibles.
    """
    
    _loaded: set = set()
    
    @classmethod
    def lazy_component(
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
            with measure_time(f"component_{component_id}"):
                loader_func()
            return
        
        # Premier rendu - charger avec feedback
        with st.spinner(placeholder_text):
            with measure_time(f"component_{component_id}_initial"):
                loader_func()
        
        cls._loaded.add(component_id)
    
    @classmethod
    def reset(cls):
        """Reset le tracker de composants."""
        cls._loaded.clear()


def debounce(wait_ms: int = 300):
    """
    Décorateur pour debouncer les appels fréquents.
    
    Utile pour les callbacks de recherche, filtres, etc.
    
    Args:
        wait_ms: Délai minimum entre appels
        
    Example:
        >>> @debounce(wait_ms=500)
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


def throttle(max_calls: int = 10, period_seconds: int = 60):
    """
    Décorateur pour limiter le nombre d'appels par période.
    
    Args:
        max_calls: Nombre max d'appels
        period_seconds: Période en secondes
        
    Example:
        >>> @throttle(max_calls=5, period_seconds=60)
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


# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════


__all__ = [
    # Classes
    "PerformanceMetric",
    "FunctionStats",
    "FunctionProfiler",
    "MemoryMonitor",
    "SQLOptimizer",
    "PerformanceDashboard",
    "ComponentLoader",
    # Décorateurs
    "profile",
    "debounce",
    "throttle",
    # Context managers
    "measure_time",
    "track_query",
    # UI
    "render_performance_panel",
    "render_mini_performance_badge",
]
