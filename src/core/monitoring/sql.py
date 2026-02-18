"""
SQL - Optimiseur et tracker de requêtes SQL.

Fonctionnalités:
- Tracking des requêtes SQL
- Détection des requêtes lentes
- Statistiques d'utilisation
"""

import logging
import time
from contextlib import contextmanager
from datetime import datetime

import streamlit as st

logger = logging.getLogger(__name__)


class OptimiseurSQL:
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
    def enregistrer_query(
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
            logger.warning(f"[!] Requête lente ({duration_ms:.0f}ms): {query[:100]}")

    @classmethod
    def obtenir_statistiques(cls) -> dict:
        """Retourne les statistiques SQL."""
        stats = cls._get_stats()

        return {
            "total_queries": stats["total_count"],
            "total_time_ms": round(stats["total_time_ms"], 2),
            "avg_time_ms": (
                round(stats["total_time_ms"] / stats["total_count"], 2)
                if stats["total_count"] > 0
                else 0
            ),
            "slow_query_count": len(stats["slow_queries"]),
            "recent_queries": stats["queries"][-10:],
            "slow_queries": stats["slow_queries"],
        }

    @classmethod
    def effacer(cls) -> None:
        """Réinitialise les stats."""
        st.session_state[cls.SESSION_KEY] = {
            "queries": [],
            "slow_queries": [],
            "total_count": 0,
            "total_time_ms": 0,
        }


@contextmanager
def suivre_requete(query_description: str):
    """
    Context manager pour tracker une requête SQL.

    Example:
        >>> with suivre_requete("SELECT recettes"):
        >>>     results = session.query(Recette).all()
    """
    start = time.perf_counter()
    rows = 0

    try:
        yield
    finally:
        duration_ms = (time.perf_counter() - start) * 1000
        OptimiseurSQL.enregistrer_query(query_description, duration_ms, rows)
