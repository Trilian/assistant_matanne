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


def _invalider_cache_anniversaires(event: EvenementDomaine) -> None:
    """Invalide le cache anniversaires quand les données changent."""
    try:
        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        nb = cache.invalidate(pattern="anniversaires")
        nb += cache.invalidate(pattern="checklists_anniversaire")
        logger.debug(
            "Cache anniversaires invalidé (%d entrées) suite à %s",
            nb,
            event.type,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec invalidation cache anniversaires: %s", e)


def _proposer_checklist_anniversaire_proche(event: EvenementDomaine) -> None:
    """Synchronise automatiquement la checklist quand un anniversaire est proche (J-30/J-14/J-7).

    Déclencheur : événement anniversaire.proche ou anniversaire.rappel avec
    jours_restants dans la liste [30, 14, 7].
    Tolère les pannes et n'échoue jamais.
    """
    try:
        jours = event.data.get("jours_restants")
        anniversaire_id = event.data.get("anniversaire_id") or event.data.get("id")
        if jours not in (30, 14, 7, 1) or not anniversaire_id:
            return

        from src.services.famille.checklists_anniversaire import (
            obtenir_service_checklists_anniversaire,
        )

        service = obtenir_service_checklists_anniversaire()
        service.synchroniser_checklist_auto(
            anniversaire_id=int(anniversaire_id),
            user_id=event.data.get("user_id"),
            force_recalcul_budget=False,
        )
        logger.info(
            "Checklist anniversaire synchronisée automatiquement (id=%s, J-%s)",
            anniversaire_id,
            jours,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec sync checklist anniversaire proche: %s", e)


def _invalider_cache_suggestions_achats(event: EvenementDomaine) -> None:
    """Invalide les caches de suggestions achats quand les préférences changent."""
    try:
        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        nb = cache.invalidate(pattern="achats_famille")
        nb += cache.invalidate(pattern="suggestions_achats")
        nb += cache.invalidate(pattern="achats_ia")
        logger.debug(
            "Cache suggestions achats invalidé (%d entrées) suite à %s",
            nb,
            event.type,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec invalidation cache suggestions achats: %s", e)


def _proposer_activites_sur_jalon(event: EvenementDomaine) -> None:
    """Suggère des activités adaptées quand un jalon Jules est ajouté.
    Déclencheur: jalons.ajoute avec user_id et age_mois dans event.data.
    Tolère les pannes."""
    try:
        jalon_nom = event.data.get("nom", "")
        user_id = event.data.get("user_id")
        if not user_id:
            return
        from src.core.caching import obtenir_cache
        cache = obtenir_cache()
        # Invalide les suggestions d'activités pour forcer un recalcul
        cache.invalidate(pattern="suggestions_activites")
        cache.invalidate(pattern="activites_ia")
        logger.info(
            "Cache activités invalidé suite au jalon '%s' (user_id=%s)",
            jalon_nom, user_id,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec suggestion activités sur jalon: %s", e)


def _invalider_cache_achats_sur_achat_effectue(event: EvenementDomaine) -> None:
    """Invalide le cache budget et achats quand un achat est marqué effectué.
    Déclencheur: achats.achete ou achat.achete.
    """
    try:
        from src.core.caching import obtenir_cache
        cache = obtenir_cache()
        cache.invalidate(pattern="budget_famille")
        cache.invalidate(pattern="achats_famille")
        cache.invalidate(pattern="contexte_familial")
        logger.info(
            "Cache budget+achats invalidé suite à un achat effectué (event=%s)",
            event.type,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec invalidation cache budget sur achat: %s", e)


def _invalider_cache_documents_expires(event: EvenementDomaine) -> None:
    """Invalide le cache rappels et contexte familial quand un document expire.
    Déclencheur: documents.expire ou documents.proche_expiration.
    """
    try:
        from src.core.caching import obtenir_cache
        cache = obtenir_cache()
        cache.invalidate(pattern="rappels_famille")
        cache.invalidate(pattern="contexte_familial")
        logger.info(
            "Cache rappels invalidé suite à expiration document (event=%s)",
            event.type,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec invalidation cache documents expirés: %s", e)


# ═══════════════════════════════════════════════════════════
# SPRINT 2 — INTERACTIONS INTELLIGENTES
# ═══════════════════════════════════════════════════════════


def _filtrer_suggestions_budget_serre(event: EvenementDomaine) -> None:
    """Invalide le cache des suggestions achats quand le budget est marqué comme 'serré'.

    Les suggestions seront recalculées au prochain appel en ne retenant
    que les items de priorité 'essentiel'.
    Déclencheur : budget.contrainte avec niveau in (serre, critique, depasse).
    """
    try:
        niveau = event.data.get("niveau", "")
        if niveau not in ("serre", "critique", "depasse"):
            return

        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        nb = cache.invalidate(pattern="suggestions_")
        nb += cache.invalidate(pattern="suggestions_achats")
        nb += cache.invalidate(pattern="achats_ia")
        logger.info(
            "Cache suggestions invalidé suite à budget '%s' (%d entrées, event=%s)",
            niveau,
            nb,
            event.type,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec filtrage suggestions budget serré: %s", e)


def _notifier_document_echeance_proche(event: EvenementDomaine) -> None:
    """Envoie une notification ntfy.sh quand un document expire dans les 30 jours.

    Déclencheur : document.echeance_proche avec jours_restants <= 30 dans event.data.
    Tolère les pannes — n'échoue jamais.
    """
    try:
        jours = event.data.get("jours_restants")
        titre_doc = event.data.get("titre") or event.data.get("nom", "Document")
        if jours is None or int(jours) > 30:
            return

        from src.services.core.notifications.notif_ntfy import ServiceNtfy
        from src.services.core.notifications.types import NotificationNtfy

        service = ServiceNtfy()
        notification = NotificationNtfy(
            titre=f"📄 Document expirant bientôt — J-{jours}",
            message=(
                f"{titre_doc} expire dans {jours} jour(s).\n"
                "Pensez à le renouveler avant l'échéance."
            ),
            priorite=4 if int(jours) <= 7 else 3,
            tags=["warning", "page_facing_up"],
            click_url="/famille/documents",
        )
        service.envoyer_sync(notification)
        logger.info(
            "Notification ntfy envoyée pour document expirant (titre=%s, J-%s)",
            titre_doc,
            jours,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec notification document échéance proche: %s", e)


def _notifier_jalon_ajoute_avec_activites(event: EvenementDomaine) -> None:
    """Suggère des activités adaptées à l'âge et pousse une notification ntfy
    quand un jalon Jules est ajouté.

    Invalide le cache des suggestions d'activités et envoie une notification ntfy
    invitant l'utilisateur à consulter les nouvelles suggestions générées.
    Déclencheur : jalon.ajoute avec nom et age_mois dans event.data.
    Tolère les pannes — n'échoue jamais.
    """
    try:
        jalon_nom = event.data.get("nom", "Nouveau jalon")
        age_mois = event.data.get("age_mois")
        user_id = event.data.get("user_id")

        # Invalider le cache pour forcer recalcul des suggestions
        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        cache.invalidate(pattern="suggestions_activites")
        cache.invalidate(pattern="activites_ia")

        # Notification ntfy avec résumé
        from src.services.core.notifications.notif_ntfy import ServiceNtfy
        from src.services.core.notifications.types import NotificationNtfy

        age_str = f" ({age_mois} mois)" if age_mois else ""
        service = ServiceNtfy()
        notification = NotificationNtfy(
            titre=f"🎯 Nouveau jalon Jules — {jalon_nom}",
            message=(
                f"Jules vient d'atteindre le jalon « {jalon_nom} »{age_str}.\n"
                "Des suggestions d'activités adaptées à son âge sont disponibles."
            ),
            priorite=3,
            tags=["baby", "sparkles"],
            click_url="/famille/jules",
        )
        service.envoyer_sync(notification)
        logger.info(
            "Notification jalon envoyée (jalon=%s, age_mois=%s, user_id=%s)",
            jalon_nom,
            age_mois,
            user_id,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec notification jalon ajouté: %s", e)




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
# WEBHOOKS SORTANTS
# ═══════════════════════════════════════════════════════════


def _livrer_webhooks(event: EvenementDomaine) -> None:
    """Livre l'événement aux webhooks enregistrés (fire-and-forget).

    N'échoue jamais — toute exception est capturée et loguée.
    La livraison effective est déléguée au thread pool du WebhookService.
    """
    try:
        from src.services.integrations.webhooks import get_webhook_service

        service = get_webhook_service()
        service.livrer_evenement(event.type, event.data)
    except ImportError:
        pass  # Module webhooks optionnel
    except Exception as e:  # noqa: BLE001
        logger.debug("Échec livraison webhooks pour %s: %s", event.type, e)


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

    # ── Anniversaires (invalidation + sync checklist proche) ──
    bus.souscrire("anniversaires.*", _invalider_cache_anniversaires, priority=100)
    compteur += 1
    bus.souscrire("anniversaire.*", _invalider_cache_anniversaires, priority=100)
    compteur += 1
    bus.souscrire("anniversaire.proche", _proposer_checklist_anniversaire_proche, priority=80)
    compteur += 1
    bus.souscrire("anniversaire.rappel", _proposer_checklist_anniversaire_proche, priority=80)
    compteur += 1

    # ── Préférences — invalider suggestions achats ──
    bus.souscrire("preferences.mise_a_jour", _invalider_cache_suggestions_achats, priority=90)
    compteur += 1
    bus.souscrire("preferences.*", _invalider_cache_suggestions_achats, priority=90)
    compteur += 1

    # ── Jalons Jules → invalider suggestions activités ──
    bus.souscrire("jalons.ajoute", _proposer_activites_sur_jalon, priority=70)
    compteur += 1
    bus.souscrire("jalons.*", _proposer_activites_sur_jalon, priority=70)
    compteur += 1

    # ── Achat effectué → invalider budget ──
    bus.souscrire("achats.achete", _invalider_cache_achats_sur_achat_effectue, priority=90)
    compteur += 1
    bus.souscrire("achat.achete", _invalider_cache_achats_sur_achat_effectue, priority=90)
    compteur += 1

    # ── Documents expirés → invalider rappels ──
    bus.souscrire("documents.expire", _invalider_cache_documents_expires, priority=90)
    compteur += 1
    bus.souscrire("documents.proche_expiration", _invalider_cache_documents_expires, priority=90)
    compteur += 1

    # ── Sprint 2 — Interactions intelligentes ──

    # Budget serré → filtrer suggestions (invalider cache suggestions_*)
    bus.souscrire("budget.contrainte", _filtrer_suggestions_budget_serre, priority=85)
    compteur += 1

    # Document échéance proche J-30 → notification ntfy
    bus.souscrire("document.echeance_proche", _notifier_document_echeance_proche, priority=80)
    compteur += 1

    # Jalon Jules ajouté → suggestions activités + notification ntfy
    bus.souscrire("jalon.ajoute", _notifier_jalon_ajoute_avec_activites, priority=75)
    compteur += 1

    # ── Métriques (priorité moyenne) ──
    bus.souscrire("*", _enregistrer_metrique_evenement, priority=50)
    compteur += 1
    bus.souscrire("service.error", _enregistrer_erreur_service, priority=50)
    compteur += 1

    # ── Webhooks sortants (basse priorité, fire-and-forget) ──
    bus.souscrire("*", _livrer_webhooks, priority=5)
    compteur += 1

    # ── Audit logging (basse priorité) ──
    bus.souscrire("*", _logger_evenement_audit, priority=10)
    compteur += 1

    _subscribers_enregistres = True
    logger.info("📡 %d event subscribers enregistrés", compteur)
    return compteur


__all__ = [
    "enregistrer_subscribers",
    "_filtrer_suggestions_budget_serre",
    "_notifier_document_echeance_proche",
    "_notifier_jalon_ajoute_avec_activites",
]
