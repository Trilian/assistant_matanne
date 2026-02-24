"""
Cache - Façade statique rétro-compatible sur CacheMultiNiveau.

.. deprecated:: 2.0.0
   Cette façade est conservée pour rétro-compatibilité uniquement.
   Pour du code neuf, utiliser ``@avec_cache`` (décorateur) ou
   ``CacheMultiNiveau()`` directement via ``obtenir_cache()``.

Ce module maintient l'API historique ``Cache.obtenir()``, ``Cache.definir()``,
etc. mais délègue désormais tout au ``CacheMultiNiveau`` (L1/L2/L3).
"""

import logging
import warnings
from typing import Any

logger = logging.getLogger(__name__)


def _cache() -> "CacheMultiNiveau":  # noqa: F821
    """Accès lazy au singleton CacheMultiNiveau (évite import circulaire)."""
    from .orchestrator import obtenir_cache

    return obtenir_cache()


# ═══════════════════════════════════════════════════════════
# CACHE PRINCIPAL — FAÇADE STATIQUE
# ═══════════════════════════════════════════════════════════


class Cache:
    """
    Cache simplifié via API statique.

    .. deprecated:: 2.0.0
       Utiliser ``@avec_cache`` ou ``CacheMultiNiveau`` pour du code neuf.

    Délègue tout au :class:`CacheMultiNiveau` (L1 mémoire → L2 session
    → L3 fichier).  Conserve la même interface publique pour les
    consommateurs existants.
    """

    _deprecation_warned: bool = False

    @classmethod
    def _warn_deprecated(cls) -> None:
        """Émet un avertissement de dépréciation une seule fois."""
        if not cls._deprecation_warned:
            warnings.warn(
                "Cache est déprécié. Utiliser @avec_cache ou CacheMultiNiveau à la place.",
                DeprecationWarning,
                stacklevel=3,
            )
            cls._deprecation_warned = True

    # Clés conservées pour compatibilité (lecture seule dans les tests/UI)
    CLE_DONNEES = "cache_donnees"
    CLE_TIMESTAMPS = "cache_timestamps"
    CLE_DEPENDANCES = "cache_dependances"
    CLE_STATS = "cache_statistiques"

    # ── Lecture ──────────────────────────────────────────────

    @staticmethod
    def obtenir(cle: str, ttl: int = 300, sentinelle: Any = None) -> Any | None:
        """
        Récupère une valeur du cache.

        .. deprecated:: 2.0.0
           Utiliser ``@avec_cache`` ou ``CacheMultiNiveau.get()``.

        Args:
            cle: Clé de cache
            ttl: Durée de vie en secondes (ignoré – le TTL est celui du set)
            sentinelle: Valeur retournée si clé non trouvée

        Returns:
            Valeur ou sentinelle si expiré/absent
        """
        Cache._warn_deprecated()
        result = _cache().get(cle)
        return result if result is not None else sentinelle

    # ── Écriture ─────────────────────────────────────────────

    @staticmethod
    def definir(
        cle: str,
        valeur: Any,
        ttl: int = 300,
        dependencies: list[str] | None = None,
    ) -> None:
        """
        Sauvegarde une valeur dans le cache.

        .. deprecated:: 2.0.0
           Utiliser ``@avec_cache`` ou ``CacheMultiNiveau.set()``.

        Args:
            cle: Clé de cache
            valeur: Valeur à cacher
            ttl: Durée de vie en secondes
            dependencies: Tags pour invalidations groupées
        """
        Cache._warn_deprecated()
        _cache().set(cle, valeur, ttl=ttl, tags=dependencies)

    # ── Invalidation ─────────────────────────────────────────

    @staticmethod
    def invalider(
        pattern: str | None = None,
        dependencies: list[str] | None = None,
    ) -> None:
        """
        Invalide le cache selon pattern ou dépendances.

        Args:
            pattern: Pattern dans la clé (ex: ``"recettes"``)
            dependencies: Tags spécifiques (ex: ``["recette_42"]``)
        """
        _cache().invalidate(pattern=pattern, tags=dependencies)

    # ── Nettoyage ────────────────────────────────────────────

    @staticmethod
    def nettoyer_expires(age_max_secondes: int = 3600) -> None:
        """
        Nettoie les entrées expirées (délègue au L1 thread-safe).

        Args:
            age_max_secondes: Âge maximum en secondes (informatif)
        """
        # Le L1 gère son propre TTL ; on force un nettoyage
        c = _cache()
        c.l1.cleanup_expired()

    @staticmethod
    def vider() -> None:
        """Vide complètement le cache (tous niveaux)."""
        _cache().clear()

    @staticmethod
    def clear() -> None:
        """
        Alias de :meth:`vider` — pratique pour les tests.

        Safe to call outside Streamlit context.
        """
        try:
            _cache().clear()
            logger.info("Cache cleared")
        except Exception:
            pass

    # ── Statistiques ─────────────────────────────────────────

    @staticmethod
    def obtenir_statistiques() -> dict:
        """
        Retourne les statistiques du cache.

        Returns:
            Dictionnaire avec métriques compatibles (hits, misses,
            taux_hit, entrees, taille_octets, …).
        """
        try:
            c = _cache()
            raw = c.obtenir_statistiques()

            # Recalculer des stats compatibles avec l'ancien format
            hits = raw.get("l1_hits", 0) + raw.get("l2_hits", 0) + raw.get("l3_hits", 0)
            misses = raw.get("misses", 0)
            total = hits + misses

            return {
                "hits": hits,
                "misses": misses,
                "invalidations": raw.get("evictions", 0),
                "taille_octets": 0,  # plus de tracking byte-level
                "entrees": raw.get("l1", {}).get("entries", 0),
                "dependances": 0,
                "taille_mo": 0.0,
                "taux_hit": (hits / total * 100) if total > 0 else 0,
                # Extensions multi-niveaux
                "l1_hits": raw.get("l1_hits", 0),
                "l2_hits": raw.get("l2_hits", 0),
                "l3_hits": raw.get("l3_hits", 0),
                "writes": raw.get("writes", 0),
            }
        except Exception:
            return {
                "hits": 0,
                "misses": 0,
                "invalidations": 0,
                "taille_octets": 0,
                "entrees": 0,
                "dependances": 0,
                "taille_mo": 0.0,
                "taux_hit": 0,
            }
