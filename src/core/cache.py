"""
Cache - Système de cache simplifié et performant.

Ce module fournit un cache en mémoire avec :
- TTL automatique
- Invalidations granulaires par tags/patterns
- Statistiques en temps réel
- Auto-cleanup des entrées expirées
- Rate limiting pour API IA
"""
import streamlit as st
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Optional, Callable, Dict, List
import hashlib
import json
import logging

from .constants import (
    CACHE_MAX_SIZE,
    AI_RATE_LIMIT_DAILY,
    AI_RATE_LIMIT_HOURLY
)

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
                "taille_octets": 0
            }

    @staticmethod
    def obtenir(cle: str, ttl: int = 300) -> Optional[Any]:
        """
        Récupère une valeur du cache.

        Args:
            cle: Clé de cache
            ttl: Durée de vie en secondes

        Returns:
            Valeur ou None si expiré/absent

        Example:
            >>> valeur = Cache.obtenir("recettes_liste", ttl=600)
        """
        Cache._initialiser()

        if cle not in st.session_state[Cache.CLE_DONNEES]:
            st.session_state[Cache.CLE_STATS]["misses"] += 1
            return None

        # Vérifier TTL
        if cle in st.session_state[Cache.CLE_TIMESTAMPS]:
            age = (datetime.now() - st.session_state[Cache.CLE_TIMESTAMPS][cle]).total_seconds()
            if age > ttl:
                Cache._supprimer(cle)
                st.session_state[Cache.CLE_STATS]["misses"] += 1
                return None

        st.session_state[Cache.CLE_STATS]["hits"] += 1
        return st.session_state[Cache.CLE_DONNEES][cle]

    @staticmethod
    def definir(
            cle: str,
            valeur: Any,
            ttl: int = 300,
            dependencies: Optional[List[str]] = None
    ):
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
    def invalider(pattern: Optional[str] = None, dependencies: Optional[List[str]] = None):
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
            cles_a_supprimer.update([
                k for k in st.session_state[Cache.CLE_DONNEES].keys()
                if pattern in k
            ])

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
    def obtenir_statistiques() -> Dict:
        """
        Retourne les statistiques du cache.

        Returns:
            Dictionnaire avec métriques
        """
        Cache._initialiser()
        Cache._mettre_a_jour_taille()

        stats = st.session_state[Cache.CLE_STATS].copy()
        stats.update({
            "entrees": len(st.session_state[Cache.CLE_DONNEES]),
            "dependances": len(st.session_state[Cache.CLE_DEPENDANCES]),
            "taille_mo": stats["taille_octets"] / (1024 * 1024),
        })

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
            taille = sum(
                sys.getsizeof(v)
                for v in st.session_state[Cache.CLE_DONNEES].values()
            )
            st.session_state[Cache.CLE_STATS]["taille_octets"] = taille
        except:
            pass


# Alias pour compatibilité
clear_all = Cache.vider


# ═══════════════════════════════════════════════════════════
# DÉCORATEUR CACHE
# ═══════════════════════════════════════════════════════════

def cached(ttl: int = 300, cle: Optional[str] = None, dependencies: Optional[List[str]] = None):
    """
    Décorateur pour cacher les résultats d'une fonction.

    Args:
        ttl: Durée de vie en secondes
        cle: Clé personnalisée (sinon auto-générée)
        dependencies: Tags pour invalidations

    Returns:
        Décorateur de fonction

    Example:
        >>> @cached(ttl=600, dependencies=["recettes"])
        >>> def obtenir_recettes():
        >>>     return recette_service.get_all()
    """
    def decorateur(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Générer clé cache
            if cle:
                cle_cache = cle
            else:
                cle_data = {
                    "fonction": func.__name__,
                    "args": str(args),
                    "kwargs": str(kwargs)
                }
                cle_cache = hashlib.md5(
                    json.dumps(cle_data, sort_keys=True).encode()
                ).hexdigest()

            # Vérifier cache
            resultat = Cache.obtenir(cle_cache, ttl)
            if resultat is not None:
                logger.debug(f"Cache HIT : {func.__name__}")
                return resultat

            # Exécuter fonction
            resultat = func(*args, **kwargs)

            # Cacher résultat
            Cache.definir(cle_cache, resultat, ttl, dependencies)
            logger.debug(f"Cache SET : {func.__name__}")

            return resultat

        return wrapper
    return decorateur


# ═══════════════════════════════════════════════════════════
# RATE LIMITING
# ═══════════════════════════════════════════════════════════

class LimiteDebit:
    """
    Rate limiting pour contrôler les appels API IA.

    Limite le nombre d'appels par jour et par heure
    pour éviter de dépasser les quotas.
    """

    CLE_RATE_LIMIT = "limite_debit"
    """Clé pour stocker les compteurs."""

    @staticmethod
    def _initialiser():
        """
        Initialise les compteurs de rate limit.
        """
        if LimiteDebit.CLE_RATE_LIMIT not in st.session_state:
            st.session_state[LimiteDebit.CLE_RATE_LIMIT] = {
                "appels_jour": 0,
                "appels_heure": 0,
                "dernier_reset": datetime.now().date(),
                "dernier_reset_heure": datetime.now().replace(
                    minute=0, second=0, microsecond=0
                )
            }

    @staticmethod
    def peut_appeler() -> tuple[bool, str]:
        """
        Vérifie si un appel API est autorisé.

        Returns:
            Tuple (autorisé, message_erreur)

        Example:
            >>> autorise, erreur = LimiteDebit.peut_appeler()
            >>> if not autorise:
            >>>     st.warning(erreur)
        """
        LimiteDebit._initialiser()

        # Reset quotidien
        aujourd_hui = datetime.now().date()
        if st.session_state[LimiteDebit.CLE_RATE_LIMIT]["dernier_reset"] != aujourd_hui:
            st.session_state[LimiteDebit.CLE_RATE_LIMIT]["appels_jour"] = 0
            st.session_state[LimiteDebit.CLE_RATE_LIMIT]["dernier_reset"] = aujourd_hui

        # Reset horaire
        heure_actuelle = datetime.now().replace(minute=0, second=0, microsecond=0)
        if st.session_state[LimiteDebit.CLE_RATE_LIMIT]["dernier_reset_heure"] != heure_actuelle:
            st.session_state[LimiteDebit.CLE_RATE_LIMIT]["appels_heure"] = 0
            st.session_state[LimiteDebit.CLE_RATE_LIMIT]["dernier_reset_heure"] = heure_actuelle

        # Vérifier limites
        if st.session_state[LimiteDebit.CLE_RATE_LIMIT]["appels_jour"] >= AI_RATE_LIMIT_DAILY:
            return False, "⏳ Limite quotidienne d'appels IA atteinte"

        if st.session_state[LimiteDebit.CLE_RATE_LIMIT]["appels_heure"] >= AI_RATE_LIMIT_HOURLY:
            return False, "⏳ Limite horaire d'appels IA atteinte"

        return True, ""

    @staticmethod
    def enregistrer_appel():
        """
        Enregistre un appel API.
        """
        LimiteDebit._initialiser()
        st.session_state[LimiteDebit.CLE_RATE_LIMIT]["appels_jour"] += 1
        st.session_state[LimiteDebit.CLE_RATE_LIMIT]["appels_heure"] += 1

    @staticmethod
    def obtenir_statistiques() -> Dict:
        """
        Retourne les statistiques de rate limiting.

        Returns:
            Dictionnaire avec compteurs
        """
        LimiteDebit._initialiser()
        return {
            "appels_jour": st.session_state[LimiteDebit.CLE_RATE_LIMIT]["appels_jour"],
            "limite_jour": AI_RATE_LIMIT_DAILY,
            "appels_heure": st.session_state[LimiteDebit.CLE_RATE_LIMIT]["appels_heure"],
            "limite_heure": AI_RATE_LIMIT_HOURLY,
            "restant_jour": AI_RATE_LIMIT_DAILY - st.session_state[LimiteDebit.CLE_RATE_LIMIT]["appels_jour"],
            "restant_heure": AI_RATE_LIMIT_HOURLY - st.session_state[LimiteDebit.CLE_RATE_LIMIT]["appels_heure"],
        }


# Alias pour compatibilité
RateLimit = LimiteDebit


# ═══════════════════════════════════════════════════════════
# UI COMPONENTS (Affichage stats)
# ═══════════════════════════════════════════════════════════

def afficher_statistiques_cache(prefixe_cle: str = "cache"):
    """
    Widget Streamlit pour afficher les stats cache dans la sidebar.

    Args:
        prefixe_cle: Préfixe pour les clés Streamlit (évite collisions)

    Example:
        >>> with st.sidebar:
        >>>     afficher_statistiques_cache()
    """
    import streamlit as st

    stats = Cache.obtenir_statistiques()

    with st.expander("💾 Cache Stats"):
        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Entrées",
                stats["entrees"],
                help="Nombre d'entrées en cache"
            )
            st.metric(
                "Taux Hit",
                f"{stats['taux_hit']:.1f}%",
                help="Taux de succès du cache"
            )

        with col2:
            st.metric(
                "Taille",
                f"{stats['taille_mo']:.2f} MB",
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
            if st.button(
                    "🧹 Nettoyer",
                    key=f"{prefixe_cle}_nettoyer",
                    use_container_width=True
            ):
                Cache.nettoyer_expires()
                st.success("Nettoyage effectué !")
                st.rerun()

        with col4:
            if st.button(
                    "🗑️ Vider",
                    key=f"{prefixe_cle}_vider",
                    use_container_width=True
            ):
                Cache.vider()
                st.success("Cache vidé !")
                st.rerun()


def afficher_statistiques_rate_limit():
    """
    Widget Streamlit pour afficher les stats de rate limiting.

    Example:
        >>> with st.sidebar:
        >>>     afficher_statistiques_rate_limit()
    """
    import streamlit as st

    stats = LimiteDebit.obtenir_statistiques()

    with st.expander("⏳ Rate Limit IA"):
        st.metric(
            "Appels aujourd'hui",
            f"{stats['appels_jour']} / {stats['limite_jour']}",
            delta=f"{stats['restant_jour']} restants"
        )

        st.metric(
            "Appels cette heure",
            f"{stats['appels_heure']} / {stats['limite_heure']}",
            delta=f"{stats['restant_heure']} restants"
        )

        # Progress bars
        st.progress(stats['appels_jour'] / stats['limite_jour'])
        st.caption("Quota journalier")