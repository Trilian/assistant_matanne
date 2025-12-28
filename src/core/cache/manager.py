"""
Gestionnaire de Cache Unifié
Remplace SmartCache + ai_cache.py + cache.py
"""
import streamlit as st
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Optional, Callable
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


class Cache:
    """
    Cache unifié multi-niveau

    Niveaux:
    - Mémoire (session Streamlit)
    - Stats de performance
    """

    @staticmethod
    def _init():
        """Initialise le cache dans session_state"""
        if "cache_data" not in st.session_state:
            st.session_state.cache_data = {}

        if "cache_timestamps" not in st.session_state:
            st.session_state.cache_timestamps = {}

        if "cache_stats" not in st.session_state:
            st.session_state.cache_stats = {
                "hits": 0,
                "misses": 0
            }

    @staticmethod
    def get(key: str, ttl: int = 300) -> Optional[Any]:
        """
        Récupère du cache avec TTL

        Args:
            key: Clé cache
            ttl: Time to live (secondes)

        Returns:
            Valeur ou None si expiré/absent
        """
        Cache._init()

        if key not in st.session_state.cache_data:
            st.session_state.cache_stats["misses"] += 1
            return None

        # Vérifier expiration
        if key in st.session_state.cache_timestamps:
            age = (datetime.now() - st.session_state.cache_timestamps[key]).seconds

            if age > ttl:
                del st.session_state.cache_data[key]
                del st.session_state.cache_timestamps[key]
                st.session_state.cache_stats["misses"] += 1
                return None

        st.session_state.cache_stats["hits"] += 1
        return st.session_state.cache_data[key]

    @staticmethod
    def set(key: str, value: Any, ttl: int = 300):
        """
        Sauvegarde en cache

        Args:
            key: Clé
            value: Valeur
            ttl: Time to live (secondes)
        """
        Cache._init()

        st.session_state.cache_data[key] = value
        st.session_state.cache_timestamps[key] = datetime.now()

        logger.debug(f"Cache SET: {key} (TTL={ttl}s)")

    @staticmethod
    def invalidate(pattern: str):
        """
        Invalide toutes les clés contenant le pattern

        Args:
            pattern: Pattern à matcher (ex: "recette")
        """
        Cache._init()

        to_remove = [
            k for k in st.session_state.cache_data.keys()
            if pattern in k
        ]

        count = 0
        for k in to_remove:
            del st.session_state.cache_data[k]
            if k in st.session_state.cache_timestamps:
                del st.session_state.cache_timestamps[k]
            count += 1

        logger.info(f"Cache invalidated: {count} keys matching '{pattern}'")

    @staticmethod
    def clear_all():
        """Vide tout le cache"""
        Cache._init()

        count = len(st.session_state.cache_data)
        st.session_state.cache_data = {}
        st.session_state.cache_timestamps = {}

        logger.info(f"Cache cleared: {count} keys removed")

    @staticmethod
    def cached(ttl: int = 300, key: Optional[str] = None):
        """
        Decorator pour cacher le résultat d'une fonction

        Usage:
            @Cache.cached(ttl=600)
            def expensive_function(param):
                return compute_something(param)
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Générer clé unique
                cache_key = key or f"{func.__module__}.{func.__name__}"

                # Inclure params dans la clé
                if args or kwargs:
                    params_str = json.dumps({
                        "args": str(args),
                        "kwargs": str(sorted(kwargs.items()))
                    }, sort_keys=True)
                    params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
                    cache_key = f"{cache_key}_{params_hash}"

                # Chercher en cache
                cached = Cache.get(cache_key, ttl)
                if cached is not None:
                    return cached

                # Calculer
                result = func(*args, **kwargs)

                # Cacher
                Cache.set(cache_key, result, ttl)

                return result

            return wrapper
        return decorator

    @staticmethod
    def get_stats() -> dict:
        """
        Statistiques du cache

        Returns:
            Dict avec métriques
        """
        Cache._init()

        total_requests = st.session_state.cache_stats["hits"] + st.session_state.cache_stats["misses"]
        hit_rate = (
            st.session_state.cache_stats["hits"] / total_requests * 100
            if total_requests > 0 else 0
        )

        return {
            "hits": st.session_state.cache_stats["hits"],
            "misses": st.session_state.cache_stats["misses"],
            "hit_rate": round(hit_rate, 2),
            "total_keys": len(st.session_state.cache_data)
        }


class RateLimit:
    """
    Rate limiting pour API IA
    """

    DAILY_LIMIT = 100
    HOURLY_LIMIT = 30

    @staticmethod
    def _init():
        """Initialise le rate limiter"""
        if "rate_limit" not in st.session_state:
            st.session_state.rate_limit = {
                "calls_today": 0,
                "calls_hour": 0,
                "last_reset": datetime.now().date(),
                "last_hour_reset": datetime.now().replace(minute=0, second=0, microsecond=0)
            }

    @staticmethod
    def can_call() -> tuple[bool, str]:
        """
        Vérifie si un appel IA est possible

        Returns:
            (can_call: bool, error_message: str)
        """
        RateLimit._init()

        # Reset quotidien
        today = datetime.now().date()
        if st.session_state.rate_limit["last_reset"] != today:
            st.session_state.rate_limit["calls_today"] = 0
            st.session_state.rate_limit["last_reset"] = today

        # Reset horaire
        current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
        if st.session_state.rate_limit["last_hour_reset"] != current_hour:
            st.session_state.rate_limit["calls_hour"] = 0
            st.session_state.rate_limit["last_hour_reset"] = current_hour

        # Vérifier limites
        calls_today = st.session_state.rate_limit["calls_today"]
        if calls_today >= RateLimit.DAILY_LIMIT:
            return False, f"⏳ Limite quotidienne atteinte ({RateLimit.DAILY_LIMIT} appels/jour)"

        calls_hour = st.session_state.rate_limit["calls_hour"]
        if calls_hour >= RateLimit.HOURLY_LIMIT:
            return False, f"⏳ Limite horaire atteinte ({RateLimit.HOURLY_LIMIT} appels/heure)"

        return True, ""

    @staticmethod
    def record_call():
        """Enregistre un appel IA"""
        RateLimit._init()

        st.session_state.rate_limit["calls_today"] += 1
        st.session_state.rate_limit["calls_hour"] += 1

    @staticmethod
    def get_usage() -> dict:
        """
        Statistiques d'utilisation

        Returns:
            Dict avec usage
        """
        RateLimit._init()

        return {
            "calls_today": st.session_state.rate_limit["calls_today"],
            "calls_hour": st.session_state.rate_limit["calls_hour"],
            "daily_limit": RateLimit.DAILY_LIMIT,
            "hourly_limit": RateLimit.HOURLY_LIMIT,
            "remaining_today": max(0, RateLimit.DAILY_LIMIT - st.session_state.rate_limit["calls_today"]),
            "remaining_hour": max(0, RateLimit.HOURLY_LIMIT - st.session_state.rate_limit["calls_hour"])
        }


def render_cache_stats(key_prefix: str = "cache"):
    """
    Widget Streamlit pour afficher les stats de cache

    Usage (dans sidebar):
        with st.sidebar:
            render_cache_stats()
    """
    stats = Cache.get_stats()
    usage = RateLimit.get_usage()

    with st.expander("📊 Cache & IA", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Cache Hits", stats["hits"])
            st.metric("Hit Rate", f"{stats['hit_rate']}%")

        with col2:
            st.metric("Cache Keys", stats["total_keys"])
            st.metric("IA Restants", usage["remaining_today"])

        if st.button("🗑️ Vider Cache", key=f"{key_prefix}_clear"):
            Cache.clear_all()
            st.success("Cache vidé !")
            st.rerun()