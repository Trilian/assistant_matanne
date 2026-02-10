"""
Cache IA - Wrapper spécifique pour réponses Mistral.

Ce module fournit un cache dédié aux réponses IA avec :
- Préfixage automatique des clés
- TTL optimisé pour les réponses IA
- Invalidations ciblées
- Statistiques de performance
"""

import hashlib
import json
import logging
from typing import Any

from ..cache import Cache
from ..constants import CACHE_TTL_IA

logger = logging.getLogger(__name__)


class CacheIA:
    """
    Cache spécifique pour réponses IA.

    Wrapper léger au-dessus du cache général avec préfixage
    et fonctionnalités spécifiques aux appels Mistral.
    """

    PREFIXE = "ia_"
    """Préfixe pour toutes les clés cache IA."""

    TTL_PAR_DEFAUT = CACHE_TTL_IA
    """TTL par défaut pour réponses IA (1h)."""

    @staticmethod
    def generer_cle(
        prompt: str, systeme: str = "", temperature: float = 0.7, modele: str = ""
    ) -> str:
        """
        Génère une clé de cache unique basée sur les paramètres.

        Args:
            prompt: Prompt utilisateur
            systeme: Prompt système
            temperature: Température
            modele: Nom du modèle

        Returns:
            Clé de cache hashée

        Example:
            >>> cle = CacheIA.generer_cle("Génère une recette", temperature=0.8)
            >>> "ia_a1b2c3d4..."
        """
        donnees = {
            "prompt": prompt,
            "systeme": systeme,
            "temperature": temperature,
            "modele": modele,
        }

        chaine = json.dumps(donnees, sort_keys=True)
        hash_md5 = hashlib.md5(chaine.encode()).hexdigest()

        return f"{CacheIA.PREFIXE}{hash_md5}"

    @staticmethod
    def obtenir(
        prompt: str,
        systeme: str = "",
        temperature: float = 0.7,
        modele: str = "",
        ttl: int | None = None,
    ) -> str | None:
        """
        Récupère une réponse du cache.

        Args:
            prompt: Prompt utilisateur
            systeme: Prompt système
            temperature: Température
            modele: Nom du modèle
            ttl: TTL personnalisé (sinon utilise défaut)

        Returns:
            Réponse cachée ou None

        Example:
            >>> reponse = CacheIA.obtenir("Génère une recette")
            >>> if reponse:
            >>>     logger.debug("Cache HIT!")
        """
        cle = CacheIA.generer_cle(prompt, systeme, temperature, modele)
        ttl_final = ttl or CacheIA.TTL_PAR_DEFAUT

        resultat = Cache.obtenir(cle, ttl=ttl_final)

        if resultat:
            logger.debug(f"Cache IA HIT: {cle[:16]}...")

        return resultat

    @staticmethod
    def definir(
        prompt: str,
        reponse: str,
        systeme: str = "",
        temperature: float = 0.7,
        modele: str = "",
        ttl: int | None = None,
    ):
        """
        Sauvegarde une réponse dans le cache.

        Args:
            prompt: Prompt utilisateur
            reponse: Réponse de l'IA
            systeme: Prompt système
            temperature: Température
            modele: Nom du modèle
            ttl: TTL personnalisé

        Example:
            >>> CacheIA.definir(
            >>>     "Génère une recette",
            >>>     "Voici une recette...",
            >>>     ttl=7200
            >>> )
        """
        cle = CacheIA.generer_cle(prompt, systeme, temperature, modele)
        ttl_final = ttl or CacheIA.TTL_PAR_DEFAUT

        Cache.definir(cle, reponse, ttl=ttl_final, dependencies=["ia", "mistral"])

        logger.debug(f"Cache IA SET: {cle[:16]}...")

    @staticmethod
    def invalider_tout():
        """
        Invalide toutes les réponses IA du cache.

        Utile pour forcer un rafraîchissement complet
        ou après modification du modèle.

        Example:
            >>> CacheIA.invalider_tout()
            >>> # Toutes les réponses IA seront recalculées
        """
        Cache.invalider(pattern=CacheIA.PREFIXE)
        logger.info("Cache IA complètement invalidé")

    @staticmethod
    def obtenir_statistiques() -> dict[str, Any]:
        """
        Retourne les statistiques du cache IA.

        Returns:
            Dictionnaire avec métriques spécifiques IA

        Example:
            >>> stats = CacheIA.obtenir_statistiques()
            >>> logger.debug(f"Entrées IA: {stats['entrees_ia']}")
        """
        stats_globales = Cache.obtenir_statistiques()

        # Compter uniquement les entrées IA
        import streamlit as st

        donnees_cache = st.session_state.get(Cache.CLE_DONNEES, {})

        entrees_ia = sum(1 for cle in donnees_cache.keys() if cle.startswith(CacheIA.PREFIXE))

        return {
            "entrees_ia": entrees_ia,
            "entrees_totales": stats_globales["entrees"],
            "taux_hit": stats_globales["taux_hit"],
            "taille_mo": stats_globales["taille_mo"],
            "ttl_defaut": CacheIA.TTL_PAR_DEFAUT,
        }

    @staticmethod
    def nettoyer_expires(age_max_secondes: int = 7200):
        """
        Nettoie les réponses IA expirées.

        Args:
            age_max_secondes: Âge maximum (défaut: 2h)

        Example:
            >>> # Nettoyer réponses > 2h
            >>> CacheIA.nettoyer_expires()
        """
        Cache.nettoyer_expires(age_max_secondes)
        logger.info(f"Nettoyage cache IA (âge max: {age_max_secondes}s)")


# ═══════════════════════════════════════════════════════════
# HELPERS POUR STREAMLIT
# ═══════════════════════════════════════════════════════════


def afficher_statistiques_cache_ia():
    """
    Widget Streamlit pour afficher les stats cache IA.

    Example:
        >>> with st.sidebar:
        >>>     afficher_statistiques_cache_ia()
    """
    import streamlit as st

    stats = CacheIA.obtenir_statistiques()

    with st.expander("🤖 Cache IA"):
        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Réponses cachées", stats["entrees_ia"], help="Nombre de réponses IA en cache"
            )

        with col2:
            st.metric("TTL défaut", f"{stats['ttl_defaut']}s", help="Durée de vie par défaut")

        # Actions
        col3, col4 = st.columns(2)

        with col3:
            if st.button("🧹 Nettoyer", key="cache_ia_nettoyer", use_container_width=True):
                CacheIA.nettoyer_expires()
                st.success("Nettoyage effectué!")
                st.rerun()

        with col4:
            if st.button("🗑️ Vider", key="cache_ia_vider", use_container_width=True):
                CacheIA.invalider_tout()
                st.success("Cache IA vidé!")
                st.rerun()
