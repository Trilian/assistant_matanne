"""
Cache Optimisé - Invalidations Fines + Monitoring
✅ Invalidations granulaires
✅ Stats temps réel
✅ Auto-cleanup
"""
import streamlit as st
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Optional, Callable, Dict, List
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


class CacheOptimized:
    """Cache avec invalidations fines et monitoring"""

    @staticmethod
    def _init():
        """Init state"""
        if "cache_data" not in st.session_state:
            st.session_state.cache_data = {}
        if "cache_timestamps" not in st.session_state:
            st.session_state.cache_timestamps = {}
        if "cache_stats" not in st.session_state:
            st.session_state.cache_stats = {
                "hits": 0,
                "misses": 0,
                "invalidations": 0,
                "size_bytes": 0
            }
        if "cache_dependencies" not in st.session_state:
            st.session_state.cache_dependencies = {}

    # ═══════════════════════════════════════════════════════════
    # CORE OPERATIONS
    # ═══════════════════════════════════════════════════════════

    @staticmethod
    def get(key: str, ttl: int = 300) -> Optional[Any]:
        """Récupère avec vérification TTL"""
        CacheOptimized._init()

        if key not in st.session_state.cache_data:
            st.session_state.cache_stats["misses"] += 1
            return None

        # Vérifier TTL
        if key in st.session_state.cache_timestamps:
            age = (datetime.now() - st.session_state.cache_timestamps[key]).seconds
            if age > ttl:
                CacheOptimized._remove(key)
                st.session_state.cache_stats["misses"] += 1
                return None

        st.session_state.cache_stats["hits"] += 1
        return st.session_state.cache_data[key]

    @staticmethod
    def set(key: str, value: Any, ttl: int = 300, dependencies: List[str] = None):
        """
        Sauvegarde avec dépendances

        Args:
            key: Clé cache
            value: Valeur
            ttl: TTL en secondes
            dependencies: Liste de tags pour invalidations (ex: ["recettes", "recette_42"])
        """
        CacheOptimized._init()

        st.session_state.cache_data[key] = value
        st.session_state.cache_timestamps[key] = datetime.now()

        # Enregistrer dépendances pour invalidations fines
        if dependencies:
            for dep in dependencies:
                if dep not in st.session_state.cache_dependencies:
                    st.session_state.cache_dependencies[dep] = []
                st.session_state.cache_dependencies[dep].append(key)

        # Mettre à jour taille
        CacheOptimized._update_size()

    @staticmethod
    def invalidate(pattern: str = None, dependencies: List[str] = None):
        """
        Invalidation fine

        Args:
            pattern: Pattern dans la clé (ex: "recettes")
            dependencies: Tags spécifiques (ex: ["recette_42"])
        """
        CacheOptimized._init()

        keys_to_remove = set()

        # Invalidation par pattern
        if pattern:
            keys_to_remove.update([
                k for k in st.session_state.cache_data.keys()
                if pattern in k
            ])

        # Invalidation par dépendances
        if dependencies:
            for dep in dependencies:
                if dep in st.session_state.cache_dependencies:
                    keys_to_remove.update(st.session_state.cache_dependencies[dep])
                    del st.session_state.cache_dependencies[dep]

        # Supprimer
        for key in keys_to_remove:
            CacheOptimized._remove(key)
            st.session_state.cache_stats["invalidations"] += 1

        logger.info(f"Cache invalidé: {len(keys_to_remove)} clés ({pattern or dependencies})")

    @staticmethod
    def _remove(key: str):
        """Supprime une clé"""
        if key in st.session_state.cache_data:
            del st.session_state.cache_data[key]
        if key in st.session_state.cache_timestamps:
            del st.session_state.cache_timestamps[key]

    @staticmethod
    def clear_all():
        """Vide tout"""
        CacheOptimized._init()
        st.session_state.cache_data = {}
        st.session_state.cache_timestamps = {}
        st.session_state.cache_dependencies = {}
        st.session_state.cache_stats["invalidations"] += 1
        logger.info("Cache complètement vidé")

    @staticmethod
    def _update_size():
        """Calcule taille cache"""
        try:
            import sys
            size = sum(
                sys.getsizeof(v)
                for v in st.session_state.cache_data.values()
            )
            st.session_state.cache_stats["size_bytes"] = size
        except:
            pass

    # ═══════════════════════════════════════════════════════════
    # AUTO-CLEANUP
    # ═══════════════════════════════════════════════════════════

    @staticmethod
    def cleanup_expired(max_age_seconds: int = 3600):
        """
        Nettoie les entrées expirées

        Args:
            max_age_seconds: Âge max en secondes
        """
        CacheOptimized._init()

        now = datetime.now()
        expired = []

        for key, timestamp in st.session_state.cache_timestamps.items():
            age = (now - timestamp).seconds
            if age > max_age_seconds:
                expired.append(key)

        for key in expired:
            CacheOptimized._remove(key)

        if expired:
            logger.info(f"Cleanup: {len(expired)} entrées expirées supprimées")

    # ═══════════════════════════════════════════════════════════
    # STATS & MONITORING
    # ═══════════════════════════════════════════════════════════

    @staticmethod
    def get_stats() -> Dict:
        """Retourne stats détaillées"""
        CacheOptimized._init()
        CacheOptimized._update_size()

        stats = st.session_state.cache_stats.copy()
        stats.update({
            "entries": len(st.session_state.cache_data),
            "dependencies": len(st.session_state.cache_dependencies),
            "size_mb": stats["size_bytes"] / (1024 * 1024),
        })

        # Hit rate
        total = stats["hits"] + stats["misses"]
        stats["hit_rate"] = (stats["hits"] / total * 100) if total > 0 else 0

        return stats

    @staticmethod
    def get_top_keys(limit: int = 10) -> List[tuple]:
        """Retourne top clés par taille"""
        CacheOptimized._init()

        import sys
        sizes = [
            (key, sys.getsizeof(value))
            for key, value in st.session_state.cache_data.items()
        ]

        return sorted(sizes, key=lambda x: x[1], reverse=True)[:limit]


# ═══════════════════════════════════════════════════════════
# AI CACHE (inchangé mais utilise CacheOptimized)
# ═══════════════════════════════════════════════════════════

class AICache:
    """Cache spécialisé pour réponses IA"""

    @staticmethod
    def generate_key(prompt: str, system: str = "", temperature: float = 0.7) -> str:
        cache_data = {
            "prompt": prompt.strip(),
            "system": system.strip(),
            "temperature": temperature
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return f"ai_{hashlib.md5(cache_str.encode()).hexdigest()}"

    @staticmethod
    def get(key: str, ttl: int = 1800) -> Optional[str]:
        return CacheOptimized.get(key, ttl)

    @staticmethod
    def set(key: str, value: str, ttl: int = 1800):
        CacheOptimized.set(key, value, ttl, dependencies=["ai"])


# ═══════════════════════════════════════════════════════════
# RATE LIMIT (inchangé)
# ═══════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════
# COMPATIBILITÉ (alias)
# ═══════════════════════════════════════════════════════════

# Pour compatibilité avec ancien code
Cache = CacheOptimized


# ═══════════════════════════════════════════════════════════
# UI COMPONENT
# ═══════════════════════════════════════════════════════════

def render_cache_stats(key_prefix: str = "cache"):
    """Widget stats cache pour sidebar"""
    import streamlit as st

    stats = CacheOptimized.get_stats()

    with st.expander("💾 Cache Stats"):
        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Entrées",
                stats["entries"],
                help="Nombre d'entrées en cache"
            )
            st.metric(
                "Hit Rate",
                f"{stats['hit_rate']:.1f}%",
                help="Taux de succès cache"
            )

        with col2:
            st.metric(
                "Taille",
                f"{stats['size_mb']:.2f} MB",
                help="Taille totale du cache"
            )
            st.metric(
                "Invalidations",
                stats["invalidations"],
                help="Nombre d'invalidations"
            )

        # Actions
        col3, col4 = st.columns(2)

        with col3:
            if st.button("🧹 Cleanup", key=f"{key_prefix}_cleanup", use_container_width=True):
                CacheOptimized.cleanup_expired()
                st.success("Cleanup effectué !")

        with col4:
            if st.button("🗑️ Vider", key=f"{key_prefix}_clear", use_container_width=True):
                CacheOptimized.clear_all()
                st.success("Cache vidé !")

        # Top keys
        if st.checkbox("Voir détails", key=f"{key_prefix}_details"):
            top_keys = CacheOptimized.get_top_keys(5)

            st.caption("Top 5 clés par taille:")
            for key, size in top_keys:
                st.caption(f"• {key[:50]}... ({size/1024:.1f} KB)")