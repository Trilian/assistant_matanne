"""
Cache Unifié - Data + AI
Fusionne core/cache/manager.py + core/ai/cache.py
"""
import streamlit as st
from datetime import datetime
from functools import wraps
from typing import Any, Optional, Callable
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


class Cache:
    """Cache unifié multi-niveau"""

    @staticmethod
    def _init():
        if "cache_data" not in st.session_state:
            st.session_state.cache_data = {}
        if "cache_timestamps" not in st.session_state:
            st.session_state.cache_timestamps = {}
        if "cache_stats" not in st.session_state:
            st.session_state.cache_stats = {"hits": 0, "misses": 0}

    @staticmethod
    def get(key: str, ttl: int = 300) -> Optional[Any]:
        Cache._init()
        if key not in st.session_state.cache_data:
            st.session_state.cache_stats["misses"] += 1
            return None

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
        Cache._init()
        st.session_state.cache_data[key] = value
        st.session_state.cache_timestamps[key] = datetime.now()

    @staticmethod
    def invalidate(pattern: str):
        Cache._init()
        to_remove = [k for k in st.session_state.cache_data.keys() if pattern in k]
        for k in to_remove:
            del st.session_state.cache_data[k]
            if k in st.session_state.cache_timestamps:
                del st.session_state.cache_timestamps[k]

    @staticmethod
    def clear_all():
        Cache._init()
        st.session_state.cache_data = {}
        st.session_state.cache_timestamps = {}


class AICache:
    """Cache spécialisé pour réponses IA"""

    @staticmethod
    def generate_key(prompt: str, system: str = "", temperature: float = 0.7) -> str:
        cache_data = {"prompt": prompt.strip(), "system": system.strip(), "temperature": temperature}
        cache_str = json.dumps(cache_data, sort_keys=True)
        return f"ai_{hashlib.md5(cache_str.encode()).hexdigest()}"

    @staticmethod
    def get(key: str, ttl: int = 1800) -> Optional[str]:
        return Cache.get(key, ttl)

    @staticmethod
    def set(key: str, value: str, ttl: int = 1800):
        Cache.set(key, value, ttl)


class RateLimit:
    """Rate limiting pour API IA"""
    DAILY_LIMIT = 100
    HOURLY_LIMIT = 30

    @staticmethod
    def _init():
        if "rate_limit" not in st.session_state:
            st.session_state.rate_limit = {
                "calls_today": 0,
                "calls_hour": 0,
                "last_reset": datetime.now().date(),
                "last_hour_reset": datetime.now().replace(minute=0, second=0, microsecond=0)
            }

    @staticmethod
    def can_call() -> tuple[bool, str]:
        RateLimit._init()
        today = datetime.now().date()
        if st.session_state.rate_limit["last_reset"] != today:
            st.session_state.rate_limit["calls_today"] = 0
            st.session_state.rate_limit["last_reset"] = today

        current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
        if st.session_state.rate_limit["last_hour_reset"] != current_hour:
            st.session_state.rate_limit["calls_hour"] = 0
            st.session_state.rate_limit["last_hour_reset"] = current_hour

        if st.session_state.rate_limit["calls_today"] >= RateLimit.DAILY_LIMIT:
            return False, f"⏳ Limite quotidienne atteinte"
        if st.session_state.rate_limit["calls_hour"] >= RateLimit.HOURLY_LIMIT:
            return False, f"⏳ Limite horaire atteinte"
        return True, ""

    @staticmethod
    def record_call():
        RateLimit._init()
        st.session_state.rate_limit["calls_today"] += 1
        st.session_state.rate_limit["calls_hour"] += 1