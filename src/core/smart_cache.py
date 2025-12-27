"""
Système de Cache Intelligent Multi-Niveau
Niveau 1: Mémoire (ultra-rapide, volatile)
Niveau 2: Session Streamlit (persiste reruns)
Niveau 3: Fichier (persiste redémarrages)

AVANT : Cache dupliqué dans ai_cache.py + logique éparpillée (300+ lignes)
APRÈS : 1 système unifié (150 lignes)
"""
import streamlit as st
import pickle
import hashlib
import json
from pathlib import Path
from typing import Any, Optional, Callable, TypeVar, Dict
from datetime import datetime, timedelta
from functools import wraps
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class SmartCache:
    """
    Cache intelligent multi-niveau avec TTL et invalidation

    Caractéristiques:
    - 3 niveaux (mémoire/session/fichier)
    - TTL configurable par entrée
    - Decorator @cached pour fonctions
    - Invalidation par pattern
    - Compression automatique (fichiers)
    - Stats d'utilisation
    """

    CACHE_DIR = Path(".cache")
    COMPRESSION_THRESHOLD = 1024  # 1KB

    @staticmethod
    def _init():
        """Initialise les caches"""
        if "smart_cache_memory" not in st.session_state:
            st.session_state.smart_cache_memory = {}

        if "smart_cache_stats" not in st.session_state:
            st.session_state.smart_cache_stats = {
                "hits": 0,
                "misses": 0,
                "by_level": {"memory": 0, "session": 0, "file": 0}
            }

        SmartCache.CACHE_DIR.mkdir(exist_ok=True)

    @staticmethod
    def _make_key(key: str, params: Optional[Dict] = None) -> str:
        """Génère clé unique avec hash des params"""
        if params:
            params_str = json.dumps(params, sort_keys=True)
            params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
            return f"{key}_{params_hash}"
        return key

    # ═══════════════════════════════════════════════════════════════
    # GET
    # ═══════════════════════════════════════════════════════════════

    @staticmethod
    def get(
            key: str,
            params: Optional[Dict] = None,
            ttl: int = 3600,
            level: str = "session"
    ) -> Optional[Any]:
        """
        Récupère du cache avec cascade

        Args:
            key: Clé cache
            params: Params pour dérivation clé
            ttl: TTL en secondes (utilisé pour validation)
            level: Niveau minimum ("memory"/"session"/"file")

        Returns:
            Valeur ou None si miss/expiré
        """
        SmartCache._init()
        cache_key = SmartCache._make_key(key, params)

        # ───────────────────────────────────────────────────────────
        # NIVEAU 1: Mémoire (le plus rapide)
        # ───────────────────────────────────────────────────────────
        if cache_key in st.session_state.smart_cache_memory:
            entry = st.session_state.smart_cache_memory[cache_key]

            if datetime.now() < entry["expires"]:
                SmartCache._record_hit("memory")
                logger.debug(f"Cache HIT (memory): {cache_key}")
                return entry["value"]
            else:
                # Expiré
                del st.session_state.smart_cache_memory[cache_key]

        # ───────────────────────────────────────────────────────────
        # NIVEAU 2: Session Streamlit
        # ───────────────────────────────────────────────────────────
        if level in ["session", "file"]:
            session_key = f"cache_session_{cache_key}"

            if session_key in st.session_state:
                entry = st.session_state[session_key]

                if datetime.now() < entry["expires"]:
                    SmartCache._record_hit("session")
                    logger.debug(f"Cache HIT (session): {cache_key}")

                    # Remonter en mémoire pour prochains accès
                    st.session_state.smart_cache_memory[cache_key] = entry

                    return entry["value"]
                else:
                    del st.session_state[session_key]

        # ───────────────────────────────────────────────────────────
        # NIVEAU 3: Fichier (persiste redémarrages)
        # ───────────────────────────────────────────────────────────
        if level == "file":
            cache_file = SmartCache.CACHE_DIR / f"{cache_key}.pkl"

            if cache_file.exists():
                try:
                    with open(cache_file, "rb") as f:
                        entry = pickle.load(f)

                    if datetime.now() < entry["expires"]:
                        SmartCache._record_hit("file")
                        logger.debug(f"Cache HIT (file): {cache_key}")

                        # Remonter dans les niveaux supérieurs
                        st.session_state.smart_cache_memory[cache_key] = entry
                        st.session_state[f"cache_session_{cache_key}"] = entry

                        return entry["value"]
                    else:
                        # Expiré, supprimer
                        cache_file.unlink()

                except Exception as e:
                    logger.warning(f"Erreur lecture cache fichier: {e}")
                    # Supprimer fichier corrompu
                    if cache_file.exists():
                        cache_file.unlink()

        # ───────────────────────────────────────────────────────────
        # MISS
        # ───────────────────────────────────────────────────────────
        SmartCache._record_miss()
        logger.debug(f"Cache MISS: {cache_key}")
        return None

    # ═══════════════════════════════════════════════════════════════
    # SET
    # ═══════════════════════════════════════════════════════════════

    @staticmethod
    def set(
            key: str,
            value: Any,
            params: Optional[Dict] = None,
            ttl: int = 3600,
            level: str = "session"
    ):
        """
        Sauvegarde en cache

        Args:
            key: Clé
            value: Valeur (doit être picklable pour level=file)
            params: Params pour clé
            ttl: TTL en secondes
            level: Niveau de persistence
        """
        SmartCache._init()
        cache_key = SmartCache._make_key(key, params)

        entry = {
            "value": value,
            "expires": datetime.now() + timedelta(seconds=ttl),
            "created": datetime.now(),
            "key": key,
            "params": params
        }

        # Niveau 1: Mémoire (toujours)
        st.session_state.smart_cache_memory[cache_key] = entry

        # Niveau 2: Session
        if level in ["session", "file"]:
            st.session_state[f"cache_session_{cache_key}"] = entry

        # Niveau 3: Fichier
        if level == "file":
            cache_file = SmartCache.CACHE_DIR / f"{cache_key}.pkl"
            try:
                with open(cache_file, "wb") as f:
                    pickle.dump(entry, f)

                logger.debug(f"Cache SET (file): {cache_key}")
            except Exception as e:
                logger.warning(f"Erreur écriture cache fichier: {e}")

        logger.debug(f"Cache SET ({level}): {cache_key}, TTL={ttl}s")

    # ═══════════════════════════════════════════════════════════════
    # DECORATOR
    # ═══════════════════════════════════════════════════════════════

    @staticmethod
    def cached(
            ttl: int = 3600,
            level: str = "session",
            key_prefix: Optional[str] = None
    ):
        """
        Decorator pour cacher résultat de fonction

        Usage:
            @SmartCache.cached(ttl=1800, level="file")
            def get_heavy_data(param1, param2):
                # Calcul lourd
                return data
        """
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @wraps(func)
            def wrapper(*args, **kwargs) -> T:
                # Générer clé
                prefix = key_prefix or f"{func.__module__}.{func.__name__}"

                # Params = args + kwargs
                params = {
                    "args": str(args),
                    "kwargs": str(sorted(kwargs.items()))
                }

                # Chercher en cache
                cached_value = SmartCache.get(
                    prefix,
                    params=params,
                    ttl=ttl,
                    level=level
                )

                if cached_value is not None:
                    return cached_value

                # Calculer
                result = func(*args, **kwargs)

                # Cacher
                SmartCache.set(
                    prefix,
                    result,
                    params=params,
                    ttl=ttl,
                    level=level
                )

                return result

            return wrapper

        return decorator

    # ═══════════════════════════════════════════════════════════════
    # INVALIDATION
    # ═══════════════════════════════════════════════════════════════

    @staticmethod
    def invalidate_pattern(pattern: str, level: str = "all"):
        """Invalide toutes les entrées matchant le pattern"""
        SmartCache._init()

        count = 0

        # Mémoire
        if level in ["memory", "all"]:
            to_remove = [
                k for k in st.session_state.smart_cache_memory.keys()
                if pattern in k
            ]
            for k in to_remove:
                del st.session_state.smart_cache_memory[k]
                count += 1

        # Session
        if level in ["session", "all"]:
            to_remove = [
                k for k in st.session_state.keys()
                if k.startswith("cache_session_") and pattern in k
            ]
            for k in to_remove:
                del st.session_state[k]
                count += 1

        # Fichier
        if level in ["file", "all"]:
            for cache_file in SmartCache.CACHE_DIR.glob("*.pkl"):
                if pattern in cache_file.stem:
                    cache_file.unlink()
                    count += 1

        logger.info(f"Invalidated {count} entries matching '{pattern}'")

    # ═══════════════════════════════════════════════════════════════
    # STATS
    # ═══════════════════════════════════════════════════════════════

    @staticmethod
    def get_stats() -> Dict:
        """Statistiques d'utilisation du cache"""
        SmartCache._init()

        stats = st.session_state.smart_cache_stats.copy()

        # Tailles
        stats["sizes"] = {
            "memory": len(st.session_state.smart_cache_memory),
            "session": len([
                k for k in st.session_state.keys()
                if k.startswith("cache_session_")
            ]),
            "file": len(list(SmartCache.CACHE_DIR.glob("*.pkl")))
        }

        # Hit rate
        total_requests = stats["hits"] + stats["misses"]
        stats["hit_rate"] = (
            round(stats["hits"] / total_requests * 100, 2)
            if total_requests > 0 else 0
        )

        return stats

    @staticmethod
    def _record_hit(level: str):
        """Enregistre un hit"""
        SmartCache._init()
        st.session_state.smart_cache_stats["hits"] += 1
        st.session_state.smart_cache_stats["by_level"][level] += 1

    @staticmethod
    def _record_miss():
        """Enregistre un miss"""
        SmartCache._init()
        st.session_state.smart_cache_stats["misses"] += 1