"""
Memory - Monitoring mémoire avec tracking et cleanup.

Fonctionnalités:
- Tracking de l'utilisation mémoire
- Snapshots pour analyse
- Nettoyage automatique (garbage collection)
"""

import gc
import logging
import tracemalloc
from collections import defaultdict
from datetime import datetime

import streamlit as st

logger = logging.getLogger(__name__)


class MoniteurMemoire:
    """
    Moniteur de mémoire avec tracking et cleanup.
    """

    SESSION_KEY = "_memory_snapshots"
    _tracking_active = False

    @classmethod
    def demarrer_suivi(cls) -> None:
        """Démarre le tracking mémoire."""
        if not cls._tracking_active:
            tracemalloc.start()
            cls._tracking_active = True
            logger.info("📊 Tracking mémoire démarré")

    @classmethod
    def arreter_suivi(cls) -> None:
        """Arrête le tracking mémoire."""
        if cls._tracking_active:
            tracemalloc.stop()
            cls._tracking_active = False
            logger.info("📊 Tracking mémoire arrêté")

    @classmethod
    def obtenir_utilisation_courante(cls) -> dict:
        """
        Retourne l'utilisation mémoire actuelle.

        Returns:
            Dict avec current_mb, peak_mb, objects_count
        """

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
            "top_types": dict(sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
        }

    @classmethod
    def prendre_instantane(cls, label: str = "snapshot") -> dict:
        """Prend un snapshot mémoire."""
        usage = cls.obtenir_utilisation_courante()
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
    def obtenir_instantanes(cls) -> list[dict]:
        """Retourne tous les snapshots."""
        return st.session_state.get(cls.SESSION_KEY, [])

    @classmethod
    def forcer_nettoyage(cls) -> dict:
        """
        Force un nettoyage mémoire.

        Returns:
            Dict avec objets collectés et mémoire libérée
        """
        before = cls.obtenir_utilisation_courante()

        # Forcer garbage collection
        collected = gc.collect()

        # Nettoyer caches Streamlit si très gros
        try:
            if hasattr(st, "cache_data"):
                # Clear des caches expirés seulement
                pass  # Streamlit gère automatiquement
        except Exception:
            pass

        after = cls.obtenir_utilisation_courante()

        freed_mb = before["current_mb"] - after["current_mb"]

        logger.info(f"🧹 Cleanup: {collected} objets collectés, {freed_mb:.2f}MB libérés")

        return {
            "objects_collected": collected,
            "memory_freed_mb": round(freed_mb, 2),
            "before_mb": before["current_mb"],
            "after_mb": after["current_mb"],
        }
