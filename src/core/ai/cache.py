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
import time
from typing import Any

from ..constants import CACHE_TTL_IA
from .embeddings import (
    embedder_texte,
    distance_hamming,
    signature_ann,
    similarite_cosine,
)

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

    PREFIXE_INDEX_SEMANTIQUE = "ia_semidx_"
    """Préfixe des indexes sémantiques par couple (modèle, système)."""

    TTL_PAR_DEFAUT = CACHE_TTL_IA
    """TTL par défaut pour réponses IA (1h)."""

    INDEX_SEMANTIQUE_MAX = 300
    """Nombre max d'entrées mémorisées pour la recherche sémantique."""

    SEUIL_SIMILARITE_DEFAUT = 0.72
    """Seuil cosine minimal pour considérer deux prompts comme proches."""

    _hits_semantiques = 0

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

        resultat_semantique = CacheIA._obtenir_semantique(
            prompt=prompt,
            systeme=systeme,
            temperature=temperature,
            modele=modele,
            ttl=ttl,
        )
        if resultat_semantique:
            CacheIA._hits_semantiques += 1
            logger.debug("Cache IA HIT sémantique")
            return resultat_semantique

        return None

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
        CacheIA._mettre_a_jour_index_semantique(
            cle=cle,
            prompt=prompt,
            systeme=systeme,
            temperature=temperature,
            modele=modele,
            ttl=ttl_final,
        )

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
            "hits_semantiques": CacheIA._hits_semantiques,
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

    @staticmethod
    def _cle_index_semantique(systeme: str, modele: str) -> str:
        """Construit la clé d'index sémantique isolée par système et modèle."""
        identifiant = hashlib.sha256(f"{modele}|{systeme}".encode()).hexdigest()[:16]
        return f"{CacheIA.PREFIXE_INDEX_SEMANTIQUE}{identifiant}"

    @staticmethod
    def _mettre_a_jour_index_semantique(
        cle: str,
        prompt: str,
        systeme: str,
        temperature: float,
        modele: str,
        ttl: int,
    ) -> None:
        """Mémorise les métadonnées prompt pour la recherche sémantique future."""
        cle_index = CacheIA._cle_index_semantique(systeme=systeme, modele=modele)
        index = _cache().get(cle_index, default=[])
        if not isinstance(index, list):
            index = []

        vecteur, provider = embedder_texte(prompt, prefer_externe=True)
        signature = signature_ann(vecteur)

        entree = {
            "cle": cle,
            "prompt": prompt,
            "temperature": float(temperature),
            "embedding": vecteur,
            "signature": signature,
            "provider": provider,
            "timestamp": time.time(),
        }

        index = [i for i in index if isinstance(i, dict) and i.get("cle") != cle]
        index.append(entree)
        index = index[-CacheIA.INDEX_SEMANTIQUE_MAX :]

        _cache().set(
            cle_index,
            index,
            ttl=max(ttl, CacheIA.TTL_PAR_DEFAUT),
            tags=["ia", "ia_semantique"],
            persistent=True,
        )

    @staticmethod
    def _obtenir_semantique(
        prompt: str,
        systeme: str,
        temperature: float,
        modele: str,
        ttl: int | None,
    ) -> str | None:
        """Recherche une réponse de prompt sémantiquement proche."""
        cle_index = CacheIA._cle_index_semantique(systeme=systeme, modele=modele)
        index = _cache().get(cle_index, default=[])
        if not isinstance(index, list) or not index:
            return None

        prompt_vecteur, provider = embedder_texte(prompt, prefer_externe=True)
        signature_cible = signature_ann(prompt_vecteur)
        meilleur_score = 0.0
        meilleure_entree: dict[str, Any] | None = None

        for entree in index[-80:]:
            if not isinstance(entree, dict):
                continue

            temp_candidate = float(entree.get("temperature") or 0.7)
            if abs(temp_candidate - float(temperature)) > 0.25:
                continue

            signature_candidate = str(entree.get("signature") or "")
            if signature_candidate and signature_cible:
                if distance_hamming(signature_candidate, signature_cible) > 28:
                    continue

            vecteur_candidate = entree.get("embedding")
            if not isinstance(vecteur_candidate, list):
                prompt_candidate = str(entree.get("prompt") or "")
                if not prompt_candidate:
                    continue
                vecteur_candidate, _ = embedder_texte(
                    prompt_candidate,
                    prefer_externe=(provider == "mistral"),
                )

            score = similarite_cosine(prompt_vecteur, vecteur_candidate)
            if score > meilleur_score:
                meilleur_score = score
                meilleure_entree = entree

        if not meilleure_entree or meilleur_score < CacheIA.SEUIL_SIMILARITE_DEFAUT:
            return None

        cle_candidate = str(meilleure_entree.get("cle") or "")
        if not cle_candidate:
            return None

        resultat = _cache().get(cle_candidate)
        if not resultat:
            return None

        # Promotion: on hydrate la clé exacte demandée pour les prochains appels.
        cle_exacte = CacheIA.generer_cle(prompt, systeme, temperature, modele)
        _cache().set(
            cle_exacte,
            resultat,
            ttl=ttl or CacheIA.TTL_PAR_DEFAUT,
            tags=["ia", "mistral", "ia_semantique"],
        )
        return resultat


# ═══════════════════════════════════════════════════════════
# HELPERS
