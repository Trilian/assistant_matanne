"""
Système de Cache pour Réponses IA
Clés Streamlit uniques pour éviter les conflits
"""
import hashlib
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import streamlit as st
import logging

logger = logging.getLogger(__name__)


class AICache:
    """Cache en mémoire pour réponses IA"""

    DEFAULT_TTL = 3600
    MAX_CACHE_SIZE = 100

    @staticmethod
    def _init_cache():
        """Initialise le cache si nécessaire"""
        if "ai_cache" not in st.session_state:
            st.session_state.ai_cache = {}
            logger.info("Cache IA initialisé")

    @staticmethod
    def _make_key(prompt: str, params: Dict[str, Any]) -> str:
        """Génère une clé unique pour le cache"""
        data = {"prompt": prompt, "params": params}
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.md5(serialized.encode()).hexdigest()

    @staticmethod
    def get(prompt: str, params: Dict[str, Any] = None) -> Optional[str]:
        """Récupère une réponse du cache"""
        AICache._init_cache()

        params = params or {}
        key = AICache._make_key(prompt, params)

        if key not in st.session_state.ai_cache:
            logger.debug(f"Cache MISS: {key[:8]}...")
            return None

        entry = st.session_state.ai_cache[key]

        now = datetime.now()
        expires_at = entry["timestamp"] + timedelta(seconds=entry["ttl"])

        if now > expires_at:
            del st.session_state.ai_cache[key]
            logger.debug(f"Cache EXPIRED: {key[:8]}...")
            return None

        logger.info(f"Cache HIT: {key[:8]}...")
        entry["hits"] = entry.get("hits", 0) + 1

        return entry["response"]

    @staticmethod
    def set(prompt: str, params: Dict[str, Any], response: str, ttl: int = DEFAULT_TTL):
        """Sauvegarde une réponse dans le cache"""
        AICache._init_cache()

        params = params or {}
        key = AICache._make_key(prompt, params)

        if len(st.session_state.ai_cache) >= AICache.MAX_CACHE_SIZE:
            AICache._evict_oldest()

        st.session_state.ai_cache[key] = {
            "prompt": prompt[:100],
            "response": response,
            "timestamp": datetime.now(),
            "ttl": ttl,
            "hits": 0,
        }

        logger.info(f"Cache SET: {key[:8]}... (TTL: {ttl}s)")

    @staticmethod
    def _evict_oldest():
        """Supprime les entrées les plus anciennes"""
        if "ai_cache" not in st.session_state or not st.session_state.ai_cache:
            return

        sorted_entries = sorted(st.session_state.ai_cache.items(), key=lambda x: x[1]["timestamp"])

        to_remove = max(1, len(sorted_entries) // 10)

        for key, _ in sorted_entries[:to_remove]:
            del st.session_state.ai_cache[key]

        logger.info(f"Cache eviction: {to_remove} entrées supprimées")

    @staticmethod
    def clear():
        """Vide tout le cache"""
        if "ai_cache" in st.session_state:
            count = len(st.session_state.ai_cache)
            st.session_state.ai_cache = {}
            logger.info(f"Cache cleared: {count} entrées supprimées")

    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """Retourne les statistiques du cache"""
        AICache._init_cache()

        cache = st.session_state.ai_cache

        if not cache:
            return {
                "size": 0,
                "max_size": AICache.MAX_CACHE_SIZE,
                "total_hits": 0,
                "oldest_entry": None,
                "newest_entry": None,
                "avg_hits": 0,
            }

        total_hits = sum(entry.get("hits", 0) for entry in cache.values())

        timestamps = [entry["timestamp"] for entry in cache.values()]
        oldest = min(timestamps) if timestamps else None
        newest = max(timestamps) if timestamps else None

        return {
            "size": len(cache),
            "max_size": AICache.MAX_CACHE_SIZE,
            "total_hits": total_hits,
            "oldest_entry": oldest,
            "newest_entry": newest,
            "avg_hits": round(total_hits / len(cache), 1) if cache else 0,
        }

    @staticmethod
    def invalidate_pattern(pattern: str):
        """Invalide toutes les entrées contenant un pattern"""
        AICache._init_cache()

        to_remove = []

        for key, entry in st.session_state.ai_cache.items():
            if pattern.lower() in entry["prompt"].lower():
                to_remove.append(key)

        for key in to_remove:
            del st.session_state.ai_cache[key]

        logger.info(f"Invalidé {len(to_remove)} entrées avec pattern: {pattern}")


# ===================================
# RATE LIMITER
# ===================================


class RateLimiter:
    """Limite le nombre d'appels IA par période"""

    MAX_CALLS_PER_HOUR = 30
    MAX_CALLS_PER_DAY = 100

    @staticmethod
    def _init_limiter():
        """Initialise le rate limiter"""
        if "ai_calls" not in st.session_state:
            st.session_state.ai_calls = []

    @staticmethod
    def can_call() -> tuple[bool, str]:
        """Vérifie si un appel IA est autorisé"""
        RateLimiter._init_limiter()

        now = datetime.now()

        st.session_state.ai_calls = [
            timestamp
            for timestamp in st.session_state.ai_calls
            if now - timestamp < timedelta(hours=24)
        ]

        hour_ago = now - timedelta(hours=1)
        calls_last_hour = sum(1 for ts in st.session_state.ai_calls if ts >= hour_ago)

        if calls_last_hour >= RateLimiter.MAX_CALLS_PER_HOUR:
            oldest_in_hour = min(
                (ts for ts in st.session_state.ai_calls if ts >= hour_ago), default=None
            )

            if oldest_in_hour:
                wait_time = timedelta(hours=1) - (now - oldest_in_hour)
                minutes = wait_time.seconds // 60

                return (
                    False,
                    f"⏳ Limite horaire atteinte ({calls_last_hour}/{RateLimiter.MAX_CALLS_PER_HOUR}). Réessaye dans {minutes} min",
                )

        calls_today = len(st.session_state.ai_calls)

        if calls_today >= RateLimiter.MAX_CALLS_PER_DAY:
            return (
                False,
                f"⏳ Limite journalière atteinte ({calls_today}/{RateLimiter.MAX_CALLS_PER_DAY})",
            )

        return True, ""

    @staticmethod
    def record_call():
        """Enregistre un appel IA"""
        RateLimiter._init_limiter()
        st.session_state.ai_calls.append(datetime.now())

        logger.info(f"Appel IA enregistré (total aujourd'hui: {len(st.session_state.ai_calls)})")

    @staticmethod
    def get_usage() -> Dict[str, Any]:
        """Retourne les stats d'utilisation"""
        RateLimiter._init_limiter()

        now = datetime.now()
        hour_ago = now - timedelta(hours=1)

        calls_last_hour = sum(1 for ts in st.session_state.ai_calls if ts >= hour_ago)

        calls_today = len(st.session_state.ai_calls)

        return {
            "calls_last_hour": calls_last_hour,
            "limit_hourly": RateLimiter.MAX_CALLS_PER_HOUR,
            "remaining_hourly": max(0, RateLimiter.MAX_CALLS_PER_HOUR - calls_last_hour),
            "calls_today": calls_today,
            "limit_daily": RateLimiter.MAX_CALLS_PER_DAY,
            "remaining_daily": max(0, RateLimiter.MAX_CALLS_PER_DAY - calls_today),
            "percentage_used": (calls_today / RateLimiter.MAX_CALLS_PER_DAY) * 100,
        }

    @staticmethod
    def reset():
        """Reset le compteur (dev uniquement)"""
        if "ai_calls" in st.session_state:
            st.session_state.ai_calls = []
            logger.warning("Rate limiter reset (dev mode)")


# ===================================
# HELPER UI AVEC CLÉS UNIQUES
# ===================================


def render_cache_stats(key_prefix: str = "default"):
    """
    Affiche les stats du cache (pour debug)

    Args:
        key_prefix: Préfixe unique pour éviter les conflits de clés
                   Ex: "recettes", "courses", "sidebar"
    """
    import streamlit as st

    stats = AICache.get_stats()
    usage = RateLimiter.get_usage()

    with st.expander("🤖 Stats IA & Cache", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Cache**")
            st.metric("Entrées", f"{stats['size']}/{stats['max_size']}")
            st.metric("Hits totaux", stats["total_hits"])

            if stats["oldest_entry"]:
                age = (datetime.now() - stats["oldest_entry"]).seconds // 60
                st.caption(f"Plus vieille: {age} min")

        with col2:
            st.markdown("**Rate Limiting**")
            st.metric("Appels (1h)", f"{usage['calls_last_hour']}/{usage['limit_hourly']}")
            st.metric("Appels (24h)", f"{usage['calls_today']}/{usage['limit_daily']}")

            st.progress(usage["percentage_used"] / 100)

        # Actions avec clés UNIQUES
        col_a1, col_a2 = st.columns(2)

        with col_a1:
            if st.button(
                "🗑️ Vider cache",
                key=f"clear_cache_btn_{key_prefix}",  # ✅ CLÉ UNIQUE
                use_container_width=True,
            ):
                AICache.clear()
                st.success("Cache vidé")
                st.rerun()

        with col_a2:
            if st.button(
                "🔄 Reset limites",
                key=f"reset_limits_btn_{key_prefix}",  # ✅ CLÉ UNIQUE
                use_container_width=True,
            ):
                RateLimiter.reset()
                st.success("Limites reset")
                st.rerun()
