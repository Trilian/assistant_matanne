"""
Subscribers — Handlers d'événements enregistrés au démarrage.

Ces subscribers réagissent aux événements domaine émis par les services
pour effectuer des actions transversales :
- Invalidation de cache quand les données changent
- Enregistrement de métriques (compteurs, durées)
- Logging structuré pour audit trail

Tous les handlers sont tolérants aux pannes (never crash the bus).
"""

from __future__ import annotations

import logging

from .bus import EvenementDomaine

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CACHE INVALIDATION
# ═══════════════════════════════════════════════════════════


def _invalider_cache_recettes(event: EvenementDomaine) -> None:
    """Invalide le cache des recettes quand le catalogue change."""
    try:
        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        nb = cache.invalidate(pattern="recettes")
        logger.debug(
            "Cache recettes invalidé (%d entrées) suite à %s",
            nb,
            event.type,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec invalidation cache recettes: %s", e)


def _invalider_cache_stock(event: EvenementDomaine) -> None:
    """Invalide le cache inventaire/stock quand le stock change."""
    try:
        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        nb = cache.invalidate(pattern="inventaire")
        nb += cache.invalidate(pattern="stock")
        logger.debug(
            "Cache stock invalidé (%d entrées) suite à %s",
            nb,
            event.type,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec invalidation cache stock: %s", e)


def _invalider_cache_courses(event: EvenementDomaine) -> None:
    """Invalide le cache courses quand une liste est générée."""
    try:
        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        nb = cache.invalidate(pattern="courses")
        logger.debug(
            "Cache courses invalidé (%d entrées) suite à %s",
            nb,
            event.type,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec invalidation cache courses: %s", e)


def _invalider_cache_entretien(event: EvenementDomaine) -> None:
    """Invalide le cache entretien quand les routines changent."""
    try:
        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        nb = cache.invalidate(pattern="entretien")
        logger.debug(
            "Cache entretien invalidé (%d entrées) suite à %s",
            nb,
            event.type,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec invalidation cache entretien: %s", e)


def _invalider_cache_planning(event: EvenementDomaine) -> None:
    """Invalide le cache planning quand les plannings changent."""
    try:
        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        nb = cache.invalidate(pattern="planning")
        logger.debug(
            "Cache planning invalidé (%d entrées) suite à %s",
            nb,
            event.type,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec invalidation cache planning: %s", e)


def _invalider_cache_batch_cooking(event: EvenementDomaine) -> None:
    """Invalide le cache batch cooking quand les sessions changent."""
    try:
        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        nb = cache.invalidate(pattern="batch_cooking")
        logger.debug(
            "Cache batch_cooking invalidé (%d entrées) suite à %s",
            nb,
            event.type,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec invalidation cache batch_cooking: %s", e)


def _invalider_cache_activites(event: EvenementDomaine) -> None:
    """Invalide le cache activités quand les activités changent."""
    try:
        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        nb = cache.invalidate(pattern="activites")
        logger.debug(
            "Cache activités invalidé (%d entrées) suite à %s",
            nb,
            event.type,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec invalidation cache activités: %s", e)


def _invalider_cache_routines(event: EvenementDomaine) -> None:
    """Invalide le cache routines quand les routines changent."""
    try:
        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        nb = cache.invalidate(pattern="routines")
        logger.debug(
            "Cache routines invalidé (%d entrées) suite à %s",
            nb,
            event.type,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec invalidation cache routines: %s", e)


def _invalider_cache_weekend(event: EvenementDomaine) -> None:
    """Invalide le cache weekend quand les plannings weekend changent."""
    try:
        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        nb = cache.invalidate(pattern="weekend")
        logger.debug(
            "Cache weekend invalidé (%d entrées) suite à %s",
            nb,
            event.type,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec invalidation cache weekend: %s", e)


def _invalider_cache_achats(event: EvenementDomaine) -> None:
    """Invalide le cache achats quand les achats changent."""
    try:
        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        nb = cache.invalidate(pattern="achats")
        logger.debug(
            "Cache achats invalidé (%d entrées) suite à %s",
            nb,
            event.type,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec invalidation cache achats: %s", e)


def _invalider_cache_food_log(event: EvenementDomaine) -> None:
    """Invalide le cache food_log quand les entrées alimentaires changent."""
    try:
        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        nb = cache.invalidate(pattern="food_log")
        logger.debug(
            "Cache food_log invalidé (%d entrées) suite à %s",
            nb,
            event.type,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec invalidation cache food_log: %s", e)


def _invalider_cache_depenses(event: EvenementDomaine) -> None:
    """Invalide le cache dépenses quand les dépenses changent."""
    try:
        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        nb = cache.invalidate(pattern="depenses")
        nb += cache.invalidate(pattern="budget")
        logger.debug(
            "Cache dépenses/budget invalidé (%d entrées) suite à %s",
            nb,
            event.type,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec invalidation cache dépenses: %s", e)


def _invalider_cache_jardin(event: EvenementDomaine) -> None:
    """Invalide le cache jardin quand les éléments changent."""
    try:
        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        nb = cache.invalidate(pattern="jardin")
        logger.debug(
            "Cache jardin invalidé (%d entrées) suite à %s",
            nb,
            event.type,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec invalidation cache jardin: %s", e)


def _invalider_cache_projets(event: EvenementDomaine) -> None:
    """Invalide le cache projets quand les projets changent."""
    try:
        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        nb = cache.invalidate(pattern="projets")
        logger.debug(
            "Cache projets invalidé (%d entrées) suite à %s",
            nb,
            event.type,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec invalidation cache projets: %s", e)


def _invalider_cache_jeux(event: EvenementDomaine) -> None:
    """Invalide le cache jeux quand les données sont synchronisées."""
    try:
        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        nb = cache.invalidate(pattern="jeux")
        nb += cache.invalidate(pattern="paris")
        nb += cache.invalidate(pattern="loto")
        logger.debug(
            "Cache jeux invalidé (%d entrées) suite à %s",
            nb,
            event.type,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec invalidation cache jeux: %s", e)


def _invalider_cache_budget(event: EvenementDomaine) -> None:
    """Invalide le cache budget quand le budget familial change."""
    try:
        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        nb = cache.invalidate(pattern="budget")
        nb += cache.invalidate(pattern="depenses")
        logger.debug(
            "Cache budget invalidé (%d entrées) suite à %s",
            nb,
            event.type,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec invalidation cache budget: %s", e)


def _invalider_cache_sante(event: EvenementDomaine) -> None:
    """Invalide le cache santé quand les données de santé changent."""
    try:
        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        nb = cache.invalidate(pattern="sante")
        logger.debug(
            "Cache santé invalidé (%d entrées) suite à %s",
            nb,
            event.type,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec invalidation cache santé: %s", e)


def _invalider_cache_loto(event: EvenementDomaine) -> None:
    """Invalide le cache loto quand les grilles/tirages changent."""
    try:
        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        nb = cache.invalidate(pattern="loto")
        nb += cache.invalidate(pattern="jeux")
        logger.debug(
            "Cache loto invalidé (%d entrées) suite à %s",
            nb,
            event.type,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec invalidation cache loto: %s", e)


def _invalider_cache_paris(event: EvenementDomaine) -> None:
    """Invalide le cache paris quand les paris/matchs changent."""
    try:
        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        nb = cache.invalidate(pattern="paris")
        nb += cache.invalidate(pattern="jeux")
        logger.debug(
            "Cache paris invalidé (%d entrées) suite à %s",
            nb,
            event.type,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec invalidation cache paris: %s", e)


# ═══════════════════════════════════════════════════════════
# MÉTRIQUES
# ═══════════════════════════════════════════════════════════


def _enregistrer_metrique_evenement(event: EvenementDomaine) -> None:
    """Enregistre une métrique pour chaque événement domaine émis."""
    try:
        from src.core.monitoring import MetriqueType, enregistrer_metrique

        enregistrer_metrique(
            f"events.{event.type}",
            1,
            MetriqueType.COMPTEUR,
        )
    except ImportError:
        pass  # Module monitoring optionnel
    except Exception as e:  # noqa: BLE001
        logger.debug("Échec enregistrement métrique événement: %s", e)


def _enregistrer_erreur_service(event: EvenementDomaine) -> None:
    """Enregistre les erreurs de service dans les métriques."""
    try:
        from src.core.monitoring import MetriqueType, enregistrer_metrique

        service = event.data.get("service", "inconnu")
        enregistrer_metrique(
            f"errors.service.{service}",
            1,
            MetriqueType.COMPTEUR,
        )
        duree = event.data.get("duration_ms", 0.0)
        if duree:
            enregistrer_metrique(
                f"errors.service.{service}.duree_ms",
                duree,
                MetriqueType.HISTOGRAMME,
            )
    except ImportError:
        pass
    except Exception as e:  # noqa: BLE001
        logger.debug("Échec enregistrement métrique erreur: %s", e)


# ═══════════════════════════════════════════════════════════
# AUDIT / LOGGING
# ═══════════════════════════════════════════════════════════


def _logger_evenement_audit(event: EvenementDomaine) -> None:
    """Log structuré de tous les événements domaine pour audit trail."""
    logger.info(
        "[AUDIT] %s | source=%s | data_keys=%s",
        event.type,
        event.source or "N/A",
        list(event.data.keys()) if event.data else [],
    )


# ═══════════════════════════════════════════════════════════
# ENREGISTREMENT — Appelé au bootstrap
# ═══════════════════════════════════════════════════════════

_subscribers_enregistres = False


def enregistrer_subscribers() -> int:
    """Enregistre tous les subscribers sur le bus d'événements.

    Idempotent : ne s'exécute qu'une fois.

    Returns:
        Nombre de souscriptions créées.
    """
    global _subscribers_enregistres
    if _subscribers_enregistres:
        return 0

    from .bus import obtenir_bus

    bus = obtenir_bus()
    compteur = 0

    # ── Cache invalidation (haute priorité) ──
    bus.souscrire("recette.*", _invalider_cache_recettes, priority=100)
    compteur += 1
    bus.souscrire("stock.*", _invalider_cache_stock, priority=100)
    compteur += 1
    bus.souscrire("courses.*", _invalider_cache_courses, priority=100)
    compteur += 1
    bus.souscrire("entretien.*", _invalider_cache_entretien, priority=100)
    compteur += 1
    bus.souscrire("planning.*", _invalider_cache_planning, priority=100)
    compteur += 1
    bus.souscrire("batch_cooking.*", _invalider_cache_batch_cooking, priority=100)
    compteur += 1
    bus.souscrire("activites.*", _invalider_cache_activites, priority=100)
    compteur += 1
    bus.souscrire("routines.*", _invalider_cache_routines, priority=100)
    compteur += 1
    bus.souscrire("weekend.*", _invalider_cache_weekend, priority=100)
    compteur += 1
    bus.souscrire("achats.*", _invalider_cache_achats, priority=100)
    compteur += 1
    bus.souscrire("food_log.*", _invalider_cache_food_log, priority=100)
    compteur += 1
    bus.souscrire("depenses.*", _invalider_cache_depenses, priority=100)
    compteur += 1
    bus.souscrire("jardin.*", _invalider_cache_jardin, priority=100)
    compteur += 1
    bus.souscrire("projets.*", _invalider_cache_projets, priority=100)
    compteur += 1
    bus.souscrire("jeux.*", _invalider_cache_jeux, priority=100)
    compteur += 1
    bus.souscrire("budget.*", _invalider_cache_budget, priority=100)
    compteur += 1
    bus.souscrire("sante.*", _invalider_cache_sante, priority=100)
    compteur += 1
    bus.souscrire("loto.*", _invalider_cache_loto, priority=100)
    compteur += 1
    bus.souscrire("paris.*", _invalider_cache_paris, priority=100)
    compteur += 1

    # ── Métriques (priorité moyenne) ──
    bus.souscrire("*", _enregistrer_metrique_evenement, priority=50)
    compteur += 1
    bus.souscrire("service.error", _enregistrer_erreur_service, priority=50)
    compteur += 1

    # ── Audit logging (basse priorité) ──
    bus.souscrire("*", _logger_evenement_audit, priority=10)
    compteur += 1

    _subscribers_enregistres = True
    logger.info("📡 %d event subscribers enregistrés", compteur)
    return compteur


__all__ = ["enregistrer_subscribers"]
