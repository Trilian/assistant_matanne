"""
Cache - Système de cache simplifié basé sur session Streamlit.

Ce module fournit un cache en mémoire avec :
- TTL automatique
- Invalidations granulaires par tags/patterns
- Statistiques en temps réel
- Auto-cleanup des entrées expirées

Note:
    Pour le cache multi-niveaux (L1/L2/L3), utiliser :func:`CacheMultiNiveau`
    via le décorateur :func:`@avec_cache` de ``src.core.decorators``.
"""

import logging
from datetime import datetime
from typing import Any

import streamlit as st

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CACHE PRINCIPAL
# ═══════════════════════════════════════════════════════════


class Cache:
    """
    Cache simple et efficace en mémoire (Streamlit session).

    Fonctionnalités :
    - Stockage en session Streamlit
    - TTL automatique
    - Invalidations par tags ou patterns
    - Statistiques temps réel
    - Auto-cleanup périodique
    """

    CLE_DONNEES = "cache_donnees"
    """Clé pour stocker les données."""

    CLE_TIMESTAMPS = "cache_timestamps"
    """Clé pour stocker les timestamps."""

    CLE_DEPENDANCES = "cache_dependances"
    """Clé pour stocker les dépendances (tags)."""

    CLE_STATS = "cache_statistiques"
    """Clé pour stocker les statistiques."""

    @staticmethod
    def _initialiser():
        """
        Initialise les structures de cache dans session state.
        """
        if Cache.CLE_DONNEES not in st.session_state:
            st.session_state[Cache.CLE_DONNEES] = {}

        if Cache.CLE_TIMESTAMPS not in st.session_state:
            st.session_state[Cache.CLE_TIMESTAMPS] = {}

        if Cache.CLE_DEPENDANCES not in st.session_state:
            st.session_state[Cache.CLE_DEPENDANCES] = {}

        if Cache.CLE_STATS not in st.session_state:
            st.session_state[Cache.CLE_STATS] = {
                "hits": 0,
                "misses": 0,
                "invalidations": 0,
                "taille_octets": 0,
            }

    @staticmethod
    def obtenir(cle: str, ttl: int = 300, sentinelle: Any = None) -> Any | None:
        """
        Récupère une valeur du cache.

        Args:
            cle: Clé de cache
            ttl: Durée de vie en secondes
            sentinelle: Valeur retournée si clé non trouvée (défaut: None)

        Returns:
            Valeur ou sentinelle si expiré/absent

        Example:
            >>> valeur = Cache.obtenir("recettes_liste", ttl=600)
        """
        Cache._initialiser()

        if cle not in st.session_state[Cache.CLE_DONNEES]:
            st.session_state[Cache.CLE_STATS]["misses"] += 1
            return sentinelle

        # Vérifier TTL
        if cle in st.session_state[Cache.CLE_TIMESTAMPS]:
            age = (datetime.now() - st.session_state[Cache.CLE_TIMESTAMPS][cle]).total_seconds()
            if age > ttl:
                Cache._supprimer(cle)
                st.session_state[Cache.CLE_STATS]["misses"] += 1
                return sentinelle

        st.session_state[Cache.CLE_STATS]["hits"] += 1
        return st.session_state[Cache.CLE_DONNEES][cle]

    @staticmethod
    def definir(cle: str, valeur: Any, ttl: int = 300, dependencies: list[str] | None = None):
        """
        Sauvegarde une valeur dans le cache.

        Args:
            cle: Clé de cache
            valeur: Valeur à cacher
            ttl: Durée de vie en secondes
            dependencies: Tags pour invalidations (ex: ["recettes", "recette_42"])

        Example:
            >>> Cache.definir(
            >>>     "recettes_liste",
            >>>     recettes,
            >>>     ttl=600,
            >>>     dependencies=["recettes"]
            >>> )
        """
        Cache._initialiser()

        st.session_state[Cache.CLE_DONNEES][cle] = valeur
        st.session_state[Cache.CLE_TIMESTAMPS][cle] = datetime.now()

        # Enregistrer dépendances pour invalidations ciblées
        if dependencies:
            for dep in dependencies:
                if dep not in st.session_state[Cache.CLE_DEPENDANCES]:
                    st.session_state[Cache.CLE_DEPENDANCES][dep] = []
                if cle not in st.session_state[Cache.CLE_DEPENDANCES][dep]:
                    st.session_state[Cache.CLE_DEPENDANCES][dep].append(cle)

        Cache._mettre_a_jour_taille()

    @staticmethod
    def clear():
        """
        Clear tous le cache.

        Useful for testing to ensure clean state between tests.
        Safe to call outside Streamlit context.
        """
        try:
            Cache._initialiser()
            st.session_state[Cache.CLE_DONNEES] = {}
            st.session_state[Cache.CLE_TIMESTAMPS] = {}
            st.session_state[Cache.CLE_DEPENDANCES] = {}
            st.session_state[Cache.CLE_STATS] = {
                "hits": 0,
                "misses": 0,
                "invalidations": 0,
                "taille_octets": 0,
            }
            logger.info("Cache cleared")
        except Exception:
            # Ignore errors when running outside Streamlit context
            pass

    @staticmethod
    def invalider(pattern: str | None = None, dependencies: list[str] | None = None):
        """
        Invalide le cache selon pattern ou dépendances.

        Args:
            pattern: Pattern dans la clé (ex: "recettes")
            dependencies: Tags spécifiques (ex: ["recette_42"])

        Example:
            >>> # Invalider toutes les recettes
            >>> Cache.invalider(pattern="recettes")
            >>>
            >>> # Invalider une recette spécifique
            >>> Cache.invalider(dependencies=["recette_42"])
        """
        Cache._initialiser()

        cles_a_supprimer = set()

        # Par pattern
        if pattern:
            cles_a_supprimer.update(
                [k for k in st.session_state[Cache.CLE_DONNEES].keys() if pattern in k]
            )

        # Par dépendances
        if dependencies:
            for dep in dependencies:
                if dep in st.session_state[Cache.CLE_DEPENDANCES]:
                    cles_a_supprimer.update(st.session_state[Cache.CLE_DEPENDANCES][dep])
                    del st.session_state[Cache.CLE_DEPENDANCES][dep]

        # Supprimer
        for cle in cles_a_supprimer:
            Cache._supprimer(cle)
            st.session_state[Cache.CLE_STATS]["invalidations"] += 1

        if cles_a_supprimer:
            logger.info(f"Cache invalidé : {len(cles_a_supprimer)} clé(s)")

    @staticmethod
    def nettoyer_expires(age_max_secondes: int = 3600):
        """
        Nettoie les entrées expirées.

        Args:
            age_max_secondes: Âge maximum en secondes
        """
        Cache._initialiser()

        maintenant = datetime.now()
        expirees = []

        for cle, timestamp in st.session_state[Cache.CLE_TIMESTAMPS].items():
            age = (maintenant - timestamp).total_seconds()
            if age > age_max_secondes:
                expirees.append(cle)

        for cle in expirees:
            Cache._supprimer(cle)

        if expirees:
            logger.info(f"Cleanup : {len(expirees)} entrée(s) supprimée(s)")

    @staticmethod
    def vider():
        """
        Vide complètement le cache.
        """
        Cache._initialiser()
        st.session_state[Cache.CLE_DONNEES] = {}
        st.session_state[Cache.CLE_TIMESTAMPS] = {}
        st.session_state[Cache.CLE_DEPENDANCES] = {}
        st.session_state[Cache.CLE_STATS]["invalidations"] += 1
        logger.info("Cache complètement vidé")

    @staticmethod
    def obtenir_statistiques() -> dict:
        """
        Retourne les statistiques du cache.

        Returns:
            Dictionnaire avec métriques
        """
        Cache._initialiser()
        Cache._mettre_a_jour_taille()

        stats = st.session_state[Cache.CLE_STATS].copy()
        stats.update(
            {
                "entrees": len(st.session_state[Cache.CLE_DONNEES]),
                "dependances": len(st.session_state[Cache.CLE_DEPENDANCES]),
                "taille_mo": stats["taille_octets"] / (1024 * 1024),
            }
        )

        # Taux de hit
        total = stats["hits"] + stats["misses"]
        stats["taux_hit"] = (stats["hits"] / total * 100) if total > 0 else 0

        return stats

    @staticmethod
    def _supprimer(cle: str):
        """
        Supprime une clé du cache.

        Args:
            cle: Clé à supprimer
        """
        if cle in st.session_state[Cache.CLE_DONNEES]:
            del st.session_state[Cache.CLE_DONNEES][cle]
        if cle in st.session_state[Cache.CLE_TIMESTAMPS]:
            del st.session_state[Cache.CLE_TIMESTAMPS][cle]

    @staticmethod
    def _mettre_a_jour_taille():
        """
        Calcule la taille approximative du cache.
        """
        try:
            import sys

            taille = sum(sys.getsizeof(v) for v in st.session_state[Cache.CLE_DONNEES].values())
            st.session_state[Cache.CLE_STATS]["taille_octets"] = taille
        except Exception:
            logger.debug("Impossible de calculer la taille du cache (sys.getsizeof échoué)")
