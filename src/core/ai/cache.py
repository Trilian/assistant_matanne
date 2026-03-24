"""
Cache IA - Wrapper spécifique pour réponses Mistral.

Ce module fournit un cache dédié aux réponses IA avec :
- Préfixage automatique des clés
- TTL optimisé pour les réponses IA
- Invalidations ciblées
- Statistiques de performance

Utilise ``CacheMultiNiveau`` directement (sans la façade ``Cache``).
"""

__all__ = ["CacheIA"]

import hashlib
import json
import logging
from typing import Any

from ..constants import CACHE_TTL_IA

logger = logging.getLogger(__name__)


def _cache():
    """Accès lazy au singleton CacheMultiNiveau."""
    from ..caching.orchestrator import obtenir_cache

    return obtenir_cache()


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
        hash_sha = hashlib.sha256(chaine.encode()).hexdigest()[:32]

        return f"{CacheIA.PREFIXE}{hash_sha}"

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

        resultat = _cache().get(cle)

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

        _cache().set(cle, reponse, ttl=ttl_final, tags=["ia", "mistral"])

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
        _cache().invalidate(pattern=CacheIA.PREFIXE)
        logger.info("Cache IA vidé")

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
        stats_globales = _cache().obtenir_statistiques()

        # Compter les entrées IA via le L1 directement
        entrees_ia = 0
        try:
            cache = _cache()
            entrees_l1 = cache.l1._cache
            entrees_ia = sum(1 for cle in entrees_l1.keys() if cle.startswith(CacheIA.PREFIXE))
        except Exception as e:
            logger.debug(f"Impossible de compter entrées IA cache: {e}")

        hits = (
            stats_globales.get("l1_hits", 0)
            + stats_globales.get("l2_hits", 0)
            + stats_globales.get("l3_hits", 0)
        )
        misses = stats_globales.get("misses", 0)
        total = hits + misses

        return {
            "entrees_ia": entrees_ia,
            "entrees_totales": stats_globales.get("l1", {}).get("entries", 0),
            "taux_hit": (hits / total * 100) if total > 0 else 0,
            "taille_mo": 0.0,
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
        _cache().l1.cleanup_expired()
        logger.info(f"Nettoyage cache IA (âge max: {age_max_secondes}s)")


# ═══════════════════════════════════════════════════════════
# HELPERS
