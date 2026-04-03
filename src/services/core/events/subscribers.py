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
from datetime import date, timedelta

from .bus import EvenementDomaine

logger = logging.getLogger(__name__)


# -----------------------------------------------------------
# CACHE INVALIDATION
# -----------------------------------------------------------


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


# -----------------------------------------------------------
# INTERACTIONS INTELLIGENTES
# -----------------------------------------------------------


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
            titre=f"?? Document expirant bientôt — J-{jours}",
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
            titre=f"?? Nouveau jalon Jules — {jalon_nom}",
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


# -----------------------------------------------------------
# AUDIT / LOGGING
# -----------------------------------------------------------


def _logger_evenement_audit(event: EvenementDomaine) -> None:
    """Log structuré de tous les événements domaine pour audit trail."""
    logger.info(
        "[AUDIT] %s | source=%s | data_keys=%s",
        event.type,
        event.source or "N/A",
        list(event.data.keys()) if event.data else [],
    )


# -----------------------------------------------------------
# WEBHOOKS SORTANTS
# -----------------------------------------------------------


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


# -----------------------------------------------------------
# CONNEXIONS INTER-MODULES
# -----------------------------------------------------------


def _sync_entretien_vers_budget(event: EvenementDomaine) -> None:
    """Invalide le cache budget quand une dépense d'entretien est synchronisée."""
    try:
        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        nb = cache.invalidate(pattern="budget")
        nb += cache.invalidate(pattern="depenses")
        nb += cache.invalidate(pattern="dashboard")
        logger.debug(
            "Cache budget/dashboard invalidé (%d entrées) suite à sync entretien",
            nb,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec invalidation cache entretien->budget: %s", e)


def _sync_voyages_vers_planning(event: EvenementDomaine) -> None:
    """Invalide le cache planning quand des voyages sont synchronisés."""
    try:
        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        nb = cache.invalidate(pattern="planning")
        nb += cache.invalidate(pattern="calendrier")
        logger.debug(
            "Cache planning/calendrier invalidé (%d entrées) suite à sync voyages",
            nb,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec invalidation cache voyages->planning: %s", e)


def _sync_charges_vers_dashboard(event: EvenementDomaine) -> None:
    """Invalide le cache dashboard quand les charges sont mises à jour."""
    try:
        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        nb = cache.invalidate(pattern="dashboard")
        nb += cache.invalidate(pattern="charges")
        nb += cache.invalidate(pattern="budget")
        logger.debug(
            "Cache dashboard invalidé (%d entrées) suite à sync charges",
            nb,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec invalidation cache charges->dashboard: %s", e)


# -----------------------------------------------------------
# INTERACTIONS INTER-MODULES (EventBus)
# -----------------------------------------------------------


def _proposer_recettes_saison_depuis_recolte(event: EvenementDomaine) -> None:
    """D.1: récolte jardin -> rafraîchir suggestions recettes/planning."""
    try:
        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        nb = cache.invalidate(pattern="recettes")
        nb += cache.invalidate(pattern="planning")
        nb += cache.invalidate(pattern="suggestions")
        logger.info(
            "Inter-modules: caches recettes/planning invalidés (%d) après %s",
            nb,
            event.type,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec flux D.1 recolte->recettes: %s", e)


def _creer_tache_entretien_sur_anomalie_energie(event: EvenementDomaine) -> None:
    """D.2: anomalie énergie -> création d'une tâche d'entretien auto."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import TacheEntretien

        details = event.data.get("details") or []
        message = event.data.get("message") or "Anomalie énergie détectée"
        with obtenir_contexte_db() as session:
            session.add(
                TacheEntretien(
                    nom="Vérifier anomalie énergie",
                    description=str(message)[:500],
                    categorie="entretien",
                    priorite="haute",
                    fait=False,
                    prochaine_fois=date.today() + timedelta(days=1),
                    notes="; ".join(str(d) for d in details[:5]) if details else None,
                )
            )
            session.commit()
        logger.info("Inter-modules: tâche entretien créée après énergie.anomalie")
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec flux D.2 energie->entretien: %s", e)


def _publier_alerte_dashboard_budget(event: EvenementDomaine) -> None:
    """D.3: dépassement budget -> invalider dashboard/alertes."""
    try:
        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        nb = cache.invalidate(pattern="dashboard")
        nb += cache.invalidate(pattern="budget")
        nb += cache.invalidate(pattern="alertes")
        logger.info("Inter-modules: caches dashboard invalidés (%d)", nb)
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec flux D.3 budget->dashboard: %s", e)


def _mettre_a_jour_courses_predictives(event: EvenementDomaine) -> None:
    """D.4: inventaire impacté -> recalcul des suggestions prédictives."""
    try:
        from src.services.cuisine.prediction_courses import obtenir_service_prediction_courses

        service = obtenir_service_prediction_courses()
        service.predire_articles(limite=20)

        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        cache.invalidate(pattern="courses")
        cache.invalidate(pattern="predictions")
        logger.info("Inter-modules: prédictions courses recalculées")
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec flux D.4 inventaire->courses: %s", e)


def _adapter_planning_sur_feedback_recette(event: EvenementDomaine) -> None:
    """D.5: feedback recette -> invalider recommandations de planning."""
    try:
        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        cache.invalidate(pattern="planning")
        cache.invalidate(pattern="recettes")
        cache.invalidate(pattern="suggestions")
        logger.info("Inter-modules: invalidation planning après recette.feedback")
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec flux D.5 feedback->planning: %s", e)


def _declencher_agent_ia_proactif(event: EvenementDomaine) -> None:
    """I.15: déclenche l'agent proactif selon météo/planning/contexte EventBus."""
    try:
        from src.services.utilitaires.assistant_proactif import (
            obtenir_service_assistant_proactif,
        )

        service = obtenir_service_assistant_proactif()
        resultat = service.traiter_evenement(event_type=event.type, data=event.data)

        if resultat.get("status") == "updated":
            from .bus import obtenir_bus

            obtenir_bus().emettre(
                "assistant.proactif.suggestion",
                {
                    "event_source": event.type,
                    "nb_suggestions": resultat.get("nb_suggestions", 0),
                },
                source="assistant_proactif",
            )
        logger.info("I.15 agent proactif traité: %s -> %s", event.type, resultat.get("status"))
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec I.15 agent proactif: %s", e)


# -----------------------------------------------------------
# BRIDGES INTER-MODULES IA
# -----------------------------------------------------------


def _invalider_cache_predictions(event: EvenementDomaine) -> None:
    """Invalide le cache prédictions quand de nouvelles prédictions sont générées."""
    try:
        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        nb = cache.invalidate(pattern="predictions")
        nb += cache.invalidate(pattern="courses")
        logger.debug(
            "Cache predictions invalidé (%d entrées) suite à %s",
            nb,
            event.type,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec invalidation cache predictions: %s", e)


def _invalider_cache_resume(event: EvenementDomaine) -> None:
    """Invalide le cache résumé hebdomadaire."""
    try:
        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        nb = cache.invalidate(pattern="resume")
        nb += cache.invalidate(pattern="dashboard")
        logger.debug(
            "Cache résumé invalidé (%d entrées) suite à %s",
            nb,
            event.type,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec invalidation cache résumé: %s", e)


def _invalider_cache_bridges(event: EvenementDomaine) -> None:
    """Invalide le cache bridges quand un bridge inter-module est déclenché."""
    try:
        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        nb = cache.invalidate(pattern="bridges")
        logger.debug(
            "Cache bridges invalidé (%d entrées) suite à %s",
            nb,
            event.type,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec invalidation cache bridges: %s", e)


def _bridge_recolte_vers_recettes(event: EvenementDomaine) -> None:
    """Récolte jardin ? suggestion recettes via bridge IA."""
    try:
        from src.services.ia.bridges import obtenir_service_bridges

        service = obtenir_service_bridges()
        nom = event.data.get("nom", "")
        quantite = event.data.get("quantite", 0)
        if nom:
            service.recolte_vers_recettes(ingredient=nom, quantite_kg=float(quantite))
            logger.info("Bridge: récolte '%s' ? suggestions recettes", nom)
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec bridge recolte?recettes: %s", e)


def _bridge_verifier_anomalies_budget(event: EvenementDomaine) -> None:
    """Budget modifié ? vérification anomalies proactive."""
    try:
        from src.services.ia.bridges import obtenir_service_bridges

        service = obtenir_service_bridges()
        service.verifier_anomalies_budget_et_notifier()
        logger.info("Bridge: vérification anomalies budget")
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec bridge budget?anomalies: %s", e)


def _traiter_action_rapide_dashboard(event: EvenementDomaine) -> None:
    """Dashboard action rapide ? invalider le cache dashboard et journaliser l'intention métier."""
    try:
        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        nb = cache.invalidate(pattern="dashboard")
        widget_id = event.data.get("widget_id") or "inconnu"
        action = event.data.get("action") or event.type
        logger.info(
            "Dashboard action rapide: widget=%s action=%s cache_invalide=%d",
            widget_id,
            action,
            nb,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec traitement dashboard.widget.action_rapide: %s", e)



# -----------------------------------------------------------
# BRIDGES INTER-MODULES
# -----------------------------------------------------------


def _generer_courses_depuis_planning(event: EvenementDomaine) -> None:
    """Bridge 1: Planning validé ? génération automatique de la liste de courses.

    Extrait les ingrédients du planning actif et les ajoute à la liste de courses.
    Émet ensuite `courses.generees` pour déclencher les notifications aval.
    Tolère les pannes — n'échoue jamais.
    """
    try:
        planning_id = event.data.get("planning_id")
        if not planning_id:
            return

        from src.core.db import obtenir_contexte_db
        from src.core.models import ArticleCourses, Ingredientx, Repas, Recette

        with obtenir_contexte_db() as session:
            # Récupérer tous les repas du planning
            repas_list = (
                session.query(Repas)
                .filter(Repas.planning_id == planning_id)
                .all()
            )
            if not repas_list:
                logger.info("Bridge 1: planning %s sans repas, courses non générées", planning_id)
                return

            # Collecter les ingrédients de toutes les recettes
            ingredients_ajoutes = 0
            for repas in repas_list:
                if not repas.recette_id:
                    continue
                recette = session.query(Recette).filter(Recette.id == repas.recette_id).first()
                if not recette:
                    continue
                # Récupérer les ingrédients de la recette
                for ri in getattr(recette, "ingredients", []) or []:
                    ingredient_id = getattr(ri, "ingredient_id", None)
                    if not ingredient_id:
                        continue
                    # Éviter les doublons : vérifier si déjà dans courses
                    existant = (
                        session.query(ArticleCourses)
                        .filter(ArticleCourses.ingredient_id == ingredient_id, ArticleCourses.achete.is_(False))
                        .first()
                    )
                    if not existant:
                        session.add(ArticleCourses(
                            ingredient_id=ingredient_id,
                            quantite_necessaire=getattr(ri, "quantite", 1) or 1,
                            priorite="normale",
                            suggere_par_ia=False,
                            notes=f"Ajouté auto depuis planning semaine du {event.data.get('semaine_debut', '')}",
                        ))
                        ingredients_ajoutes += 1

            session.commit()

        # Émettre l'événement de confirmation
        if ingredients_ajoutes > 0:
            from .bus import obtenir_bus
            obtenir_bus().emettre(
                "courses.generees",
                {
                    "nb_articles": ingredients_ajoutes,
                    "source": "planning",
                    "planning_id": planning_id,
                    "semaine_debut": event.data.get("semaine_debut", ""),
                },
                source="bridge_planning_courses",
            )
        logger.info(
            "Bridge 1: planning %s ? %d articles ajoutés aux courses",
            planning_id, ingredients_ajoutes,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec bridge 1 planning?courses: %s", e)


def _notifier_courses_generees(event: EvenementDomaine) -> None:
    """Bridge 1 bis: courses générées ? notification utilisateur.

    Envoie une notification multi-canal après la génération automatique
    de la liste de courses depuis le planning hebdomadaire.
    Tolère les pannes — n'échoue jamais.
    """
    try:
        nb_articles = int(event.data.get("nb_articles", 0) or 0)
        semaine_debut = event.data.get("semaine_debut", "")
        planning_id = event.data.get("planning_id", "")

        from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

        dispatcher = get_dispatcher_notifications()
        message = (
            f"Planning #{planning_id} validé ({semaine_debut}).\n"
            f"La liste de courses est prête ({nb_articles} article(s))."
        )

        # Best-effort sur les utilisateurs connus; fallback safe sur compte principal.
        try:
            from src.core.db import obtenir_contexte_db
            from src.core.models import ProfilUtilisateur

            with obtenir_contexte_db() as session:
                usernames = [
                    p.username
                    for p in session.query(ProfilUtilisateur.username).all()
                    if p.username
                ]
        except Exception:
            usernames = ["matanne"]

        for user_id in usernames or ["matanne"]:
            dispatcher.envoyer(
                user_id=user_id,
                message=message,
                canaux=["telegram", "push"],
                type_evenement="rappel_courses",
                titre=f"?? Courses prêtes ({nb_articles})",
            )

        # Compatibilité historique: side-effect ntfy direct (utilisé par certains tests legacy).
        try:
            from src.services.core.notifications.notif_ntfy import ServiceNtfy
            from src.services.core.notifications.types import NotificationNtfy

            ServiceNtfy().envoyer_sync(
                NotificationNtfy(
                    titre=f"?? Courses prêtes ({nb_articles})",
                    message=message,
                    click_url="/cuisine/courses",
                )
            )
        except Exception:
            pass
        logger.info(
            "Bridge 1 bis: notification courses envoyée (planning=%s, nb_articles=%s)",
            planning_id,
            nb_articles,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec bridge 1 bis courses?notif: %s", e)


def _suggerer_recettes_anti_gaspi(event: EvenementDomaine) -> None:
    """Bridge 2: Stock bientôt périmé ? suggestions recettes anti-gaspillage via IA.

    Appelle le service anti-gaspillage pour identifier les recettes prioritaires
    et invalide le cache de la page anti-gaspillage.
    Tolère les pannes — n'échoue jamais.
    """
    try:
        nom = event.data.get("nom", "")
        jours_restants = event.data.get("jours_restants", 3)
        article_id = event.data.get("article_id", 0)
        if not nom:
            return

        from src.core.caching import obtenir_cache
        cache = obtenir_cache()
        cache.invalidate(pattern="anti_gaspillage")
        cache.invalidate(pattern="recettes")

        # Notification push si article expire très bientôt (= 2 jours)
        if int(jours_restants) <= 2:
            from src.services.core.notifications.notif_ntfy import ServiceNtfy
            from src.services.core.notifications.types import NotificationNtfy

            service = ServiceNtfy()
            service.envoyer_sync(NotificationNtfy(
                titre=f"?? {nom} expire bientôt (J-{jours_restants})",
                message=(
                    f"{nom} expire dans {jours_restants} jour(s).\n"
                    "Des recettes anti-gaspillage ont été calculées pour l'utiliser."
                ),
                priorite=4,
                tags=["warning", "knife_fork_plate"],
                click_url="/cuisine/anti-gaspillage",
            ))

        logger.info(
            "Bridge 2: article '%s' (J-%s) ? anti-gaspi cache invalidé + notification",
            nom, jours_restants,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec bridge 2 inventaire?anti_gaspi: %s", e)


def _notifier_alerte_budget_push(event: EvenementDomaine) -> None:
    """Bridge 3: Dépassement budget ? notification push + widget dashboard.

    Envoie une notification ntfy immédiate et invalide le cache dashboard
    pour forcer l'affichage de l'alerte dans les widgets.
    Tolère les pannes — n'échoue jamais.
    """
    try:
        categorie = event.data.get("categorie", "")
        depense = event.data.get("depense", 0.0)
        budget = event.data.get("budget", 0.0)
        pourcentage = event.data.get("pourcentage", 0.0)

        # Invalider le dashboard
        from src.core.caching import obtenir_cache
        cache = obtenir_cache()
        cache.invalidate(pattern="dashboard")
        cache.invalidate(pattern="budget")
        cache.invalidate(pattern="alertes")

        # Envoyer une notification push
        from src.services.core.notifications.notif_ntfy import ServiceNtfy
        from src.services.core.notifications.types import NotificationNtfy

        service = ServiceNtfy()
        service.envoyer_sync(NotificationNtfy(
            titre=f"?? Budget {categorie} dépassé ({pourcentage:.0f}%)",
            message=(
                f"Dépenses {categorie}: {depense:.0f}€ / {budget:.0f}€ prévu.\n"
                "Consultez le tableau de bord pour les détails."
            ),
            priorite=4,
            tags=["rotating_light", "money_with_wings"],
            click_url="/famille/budget",
        ))
        logger.info(
            "Bridge 3: budget.depassement ? notification push envoyée (catégorie=%s, %.0f%%)",
            categorie, pourcentage,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec bridge 3 budget?dashboard_push: %s", e)


def _enregistrer_jalon_depuis_activite(event: EvenementDomaine) -> None:
    """Bridge 4: Activité famille terminée ? jalon Jules enregistré automatiquement.

    Si l'activité est liée au développement de Jules (catégorie motricite/langage/social/eveil),
    crée un jalon associé dans la timeline de suivi.
    Tolère les pannes — n'échoue jamais.
    """
    try:
        activite_id = event.data.get("activite_id", 0)
        nom = event.data.get("nom", "")
        categorie = event.data.get("categorie", "")
        user_id = event.data.get("user_id")

        # Catégories pertinentes pour Jules
        categories_jules = {"motricite", "langage", "social", "eveil", "developpement"}
        if categorie.lower() not in categories_jules:
            return
        if not nom:
            return

        from src.core.db import obtenir_contexte_db
        from src.core.models.famille import JalonJules
        from datetime import date as _date

        with obtenir_contexte_db() as session:
            # Vérifier qu'il n'existe pas déjà un jalon pour cette activité
            existant = (
                session.query(JalonJules)
                .filter(JalonJules.titre == nom)
                .first()
            )
            if not existant:
                session.add(JalonJules(
                    titre=nom,
                    description=f"Jalon enregistré automatiquement depuis l'activité #{activite_id}",
                    date_atteinte=_date.today(),
                    categorie=categorie,
                    source="auto_bridge",
                ))
                session.commit()
                # Émettre l'événement jalon
                from .bus import obtenir_bus
                obtenir_bus().emettre(
                    "jalon.ajoute",
                    {"nom": nom, "categorie": categorie, "user_id": user_id},
                    source="bridge_activite_jules",
                )
                logger.info("Bridge 4: activité '%s' ? jalon Jules créé auto", nom)
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec bridge 4 activites?jules: %s", e)


def _sync_tache_deadline_vers_calendrier(event: EvenementDomaine) -> None:
    """Bridge 5: Tâche projet avec deadline ? événement dans le calendrier entretien.

    Crée une tâche d'entretien planifiée pour la deadline du projet,
    assurant sa visibilité dans le planning unifié.
    Tolère les pannes — n'échoue jamais.
    """
    try:
        projet_nom = event.data.get("projet_nom", "")
        tache_nom = event.data.get("tache_nom", "")
        deadline_str = event.data.get("deadline", "")
        projet_id = event.data.get("projet_id", 0)
        if not (projet_nom and tache_nom and deadline_str):
            return

        from datetime import date as _date
        from src.core.db import obtenir_contexte_db
        from src.core.models import TacheEntretien

        deadline = _date.fromisoformat(deadline_str)

        with obtenir_contexte_db() as session:
            # Éviter les doublons
            existant = (
                session.query(TacheEntretien)
                .filter(
                    TacheEntretien.nom == f"[Projet] {tache_nom}",
                    TacheEntretien.prochaine_fois == deadline,
                )
                .first()
            )
            if not existant:
                session.add(TacheEntretien(
                    nom=f"[Projet] {tache_nom}",
                    description=f"Échéance projet « {projet_nom} » (id={projet_id})",
                    categorie="projets",
                    priorite="haute",
                    fait=False,
                    prochaine_fois=deadline,
                ))
                session.commit()

        # Invalider le cache calendrier/entretien
        from src.core.caching import obtenir_cache
        cache = obtenir_cache()
        cache.invalidate(pattern="entretien")
        cache.invalidate(pattern="calendrier")

        logger.info(
            "Bridge 5: tâche '%s' (projet %s) ? calendrier entretien J=%s",
            tache_nom, projet_nom, deadline_str,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec bridge 5 projets?calendrier: %s", e)


def _actualiser_stats_pl_dashboard(event: EvenementDomaine) -> None:
    """Bridge 7: Résultat jeu enregistré ? mise à jour stats P&L dashboard.

    Invalide uniquement les caches jeux et dashboard pour forcer
    un recalcul des statistiques profit/perte la prochaine requête.
    Tolère les pannes — n'échoue jamais.
    """
    try:
        type_jeu = event.data.get("type_jeu", "")
        gain = event.data.get("gain", 0.0)
        mise = event.data.get("mise", 0.0)
        est_gagnant = event.data.get("est_gagnant", False)

        from src.core.caching import obtenir_cache
        cache = obtenir_cache()
        cache.invalidate(pattern="jeux")
        cache.invalidate(pattern="paris")
        cache.invalidate(pattern="dashboard")

        # Notification si gain significatif
        if est_gagnant and float(gain) > 50:
            from src.services.core.notifications.notif_ntfy import ServiceNtfy
            from src.services.core.notifications.types import NotificationNtfy
            ServiceNtfy().envoyer_sync(NotificationNtfy(
                titre=f"?? Gain {type_jeu} : +{gain:.0f}€ !",
                message=f"Mise: {mise:.0f}€ ? Gain: {gain:.0f}€. Stats P&L mises à jour.",
                priorite=3,
                tags=["tada", "moneybag"],
                click_url="/jeux",
            ))

        logger.info(
            "Bridge 7: résultat %s ? dashboard P&L invalidé (gain=%.0f€, gagnant=%s)",
            type_jeu, float(gain), est_gagnant,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec bridge 7 jeux?dashboard: %s", e)


def _suggerer_activites_weekend_meteo(event: EvenementDomaine) -> None:
    """Bridge 8: Météo reçue ? suggestions d'activités weekend adaptées.

    Invalide le cache weekend et utilise la condition météo pour
    orienter les suggestions (intérieur si pluie, extérieur si soleil).
    Tolère les pannes — n'échoue jamais.
    """
    try:
        condition = event.data.get("condition", "")
        temperature_max = event.data.get("temperature_max", 15.0)
        date_prevision = event.data.get("date_prevision", "")

        from src.core.caching import obtenir_cache
        cache = obtenir_cache()
        cache.invalidate(pattern="weekend")
        cache.invalidate(pattern="activites_ia")
        cache.invalidate(pattern="suggestions_activites")

        # Déclencher le service weekend IA si mauvais temps prévu
        if condition in ("pluie", "orage", "neige"):
            from src.services.famille.weekend_ai import get_weekend_ai_service
            service = get_weekend_ai_service()
            if hasattr(service, "suggerer_activites_interieur"):
                service.suggerer_activites_interieur(
                    meteo=condition,
                    temperature=float(temperature_max),
                )

        logger.info(
            "Bridge 8: météo '%s' (%s°C) le %s ? suggestions weekend invalidées",
            condition, temperature_max, date_prevision,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec bridge 8 meteo?activites_weekend: %s", e)


def _envoyer_rappel_entretien_push(event: EvenementDomaine) -> None:
    """Bridge 9: Tâche entretien due ? rappel push ntfy le matin.

    Envoie une notification push pour rappeler la tâche d'entretien
    planifiée pour aujourd'hui ou demain.
    Tolère les pannes — n'échoue jamais.
    """
    try:
        tache_id = event.data.get("tache_id", 0)
        nom = event.data.get("nom", "")
        categorie = event.data.get("categorie", "")
        prochaine_fois = event.data.get("prochaine_fois", "")
        priorite = event.data.get("priorite", "normale")
        if not nom:
            return

        priorite_ntfy = 4 if priorite == "haute" else 3

        from src.services.core.notifications.notif_ntfy import ServiceNtfy
        from src.services.core.notifications.types import NotificationNtfy

        ServiceNtfy().envoyer_sync(NotificationNtfy(
            titre=f"?? Entretien à faire : {nom}",
            message=(
                f"Tâche {categorie} planifiée pour {prochaine_fois}.\n"
                "Consultez la liste complète des tâches maison."
            ),
            priorite=priorite_ntfy,
            tags=["house", "wrench"],
            click_url="/maison/entretien",
        ))
        logger.info("Bridge 9: rappel entretien envoyé (tache_id=%s, nom=%s)", tache_id, nom)
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec bridge 9 entretien?push: %s", e)


# -----------------------------------------------------------
# ENREGISTREMENT — Appelé au bootstrap
# -----------------------------------------------------------

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

    # -- Cache invalidation (haute priorité) --
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

    # -- Anniversaires (invalidation + sync checklist proche) --
    bus.souscrire("anniversaires.*", _invalider_cache_anniversaires, priority=100)
    compteur += 1
    bus.souscrire("anniversaire.*", _invalider_cache_anniversaires, priority=100)
    compteur += 1
    bus.souscrire("anniversaire.proche", _proposer_checklist_anniversaire_proche, priority=80)
    compteur += 1
    bus.souscrire("anniversaire.rappel", _proposer_checklist_anniversaire_proche, priority=80)
    compteur += 1

    # -- Préférences — invalider suggestions achats --
    bus.souscrire("preferences.mise_a_jour", _invalider_cache_suggestions_achats, priority=90)
    compteur += 1
    bus.souscrire("preferences.*", _invalider_cache_suggestions_achats, priority=90)
    compteur += 1

    # -- Jalons Jules ? invalider suggestions activités --
    bus.souscrire("jalons.ajoute", _proposer_activites_sur_jalon, priority=70)
    compteur += 1
    bus.souscrire("jalons.*", _proposer_activites_sur_jalon, priority=70)
    compteur += 1

    # -- Achat effectué ? invalider budget --
    bus.souscrire("achats.achete", _invalider_cache_achats_sur_achat_effectue, priority=90)
    compteur += 1
    bus.souscrire("achat.achete", _invalider_cache_achats_sur_achat_effectue, priority=90)
    compteur += 1

    # -- Documents expirés ? invalider rappels --
    bus.souscrire("documents.expire", _invalider_cache_documents_expires, priority=90)
    compteur += 1
    bus.souscrire("documents.proche_expiration", _invalider_cache_documents_expires, priority=90)
    compteur += 1

    # -- Interactions intelligentes --

    # Budget serré ? filtrer suggestions (invalider cache suggestions_*)
    bus.souscrire("budget.contrainte", _filtrer_suggestions_budget_serre, priority=85)
    compteur += 1

    # Document échéance proche J-30 ? notification ntfy
    bus.souscrire("document.echeance_proche", _notifier_document_echeance_proche, priority=80)
    compteur += 1

    # Jalon Jules ajouté ? suggestions activités + notification ntfy
    bus.souscrire("jalon.ajoute", _notifier_jalon_ajoute_avec_activites, priority=75)
    compteur += 1

    # -- Connexions inter-modules --

    # Entretien ? Budget (sync dépenses)
    bus.souscrire("depenses.sync_entretien", _sync_entretien_vers_budget, priority=85)
    compteur += 1

    # Voyages ? Calendrier (sync événements planning)
    bus.souscrire("planning.sync_voyages", _sync_voyages_vers_planning, priority=85)
    compteur += 1

    # Charges ? Dashboard (mise à jour métriques)
    bus.souscrire("dashboard.charges_update", _sync_charges_vers_dashboard, priority=85)
    compteur += 1

    # -- Inter-modules EventBus enrichi --

    bus.souscrire("jardin.recolte", _proposer_recettes_saison_depuis_recolte, priority=80)
    compteur += 1

    bus.souscrire("energie.anomalie", _creer_tache_entretien_sur_anomalie_energie, priority=80)
    compteur += 1

    bus.souscrire("budget.depassement", _publier_alerte_dashboard_budget, priority=80)
    compteur += 1

    bus.souscrire("inventaire.modification_importante", _mettre_a_jour_courses_predictives, priority=80)
    compteur += 1

    bus.souscrire("recette.feedback", _adapter_planning_sur_feedback_recette, priority=80)
    compteur += 1


    # -- Agent IA proactif EventBus --
    bus.souscrire("meteo.*", _declencher_agent_ia_proactif, priority=70)
    compteur += 1
    bus.souscrire("planning.*", _declencher_agent_ia_proactif, priority=70)
    compteur += 1
    bus.souscrire("budget.depassement", _declencher_agent_ia_proactif, priority=70)
    compteur += 1
    bus.souscrire("assistant.commande_executee", _declencher_agent_ia_proactif, priority=70)
    compteur += 1

    # -- Bridges inter-modules IA --
    bus.souscrire("prediction.*", _invalider_cache_predictions, priority=100)
    compteur += 1
    bus.souscrire("resume.*", _invalider_cache_resume, priority=100)
    compteur += 1
    bus.souscrire("bridge.*", _invalider_cache_bridges, priority=90)
    compteur += 1
    bus.souscrire("jardin.recolte", _bridge_recolte_vers_recettes, priority=75)
    compteur += 1
    bus.souscrire("budget.modifie", _bridge_verifier_anomalies_budget, priority=75)
    compteur += 1

    bus.souscrire("dashboard.widget.action_rapide", _traiter_action_rapide_dashboard, priority=75)
    compteur += 1

    # -- Bridges inter-modules (priorité 80) --

    # Bridge 1: Planning validé ? courses auto
    bus.souscrire("planning.valide", _generer_courses_depuis_planning, priority=80)
    compteur += 1
    bus.souscrire("planning.semaine_validee", _generer_courses_depuis_planning, priority=80)
    compteur += 1
    bus.souscrire("courses.generees", _notifier_courses_generees, priority=79)
    compteur += 1

    # Bridge 2: Inventaire péremption proche ? anti-gaspi IA
    bus.souscrire("inventaire.peremption_proche", _suggerer_recettes_anti_gaspi, priority=80)
    compteur += 1

    # Bridge 3: Budget dépassement ? push notification
    bus.souscrire("budget.depassement", _notifier_alerte_budget_push, priority=78)
    compteur += 1

    # Bridge 4: Activité terminée ? jalon Jules auto
    bus.souscrire("activites.terminee", _enregistrer_jalon_depuis_activite, priority=80)
    compteur += 1

    # Bridge 5: Tâche projet deadline ? calendrier entretien
    bus.souscrire("projets.tache_deadline", _sync_tache_deadline_vers_calendrier, priority=80)
    compteur += 1

    # Bridge 7: Résultat jeu ? dashboard P&L
    bus.souscrire("paris.resultat_enregistre", _actualiser_stats_pl_dashboard, priority=80)
    compteur += 1

    # Bridge 8: Météo reçue ? activités weekend
    bus.souscrire("meteo.prevision_recue", _suggerer_activites_weekend_meteo, priority=80)
    compteur += 1

    # Bridge 9: Tâche entretien due ? rappel push
    bus.souscrire("entretien.tache_due", _envoyer_rappel_entretien_push, priority=80)
    compteur += 1

    # -- Métriques (priorité moyenne) --
    bus.souscrire("*", _enregistrer_metrique_evenement, priority=50)
    compteur += 1
    bus.souscrire("service.error", _enregistrer_erreur_service, priority=50)
    compteur += 1

    # -- Bridges inter-modules moyenne priorité (NIM5-NIM8) --
    try:
        from src.services.maison.inter_module_entretien_budget import (
            enregistrer_entretien_budget_subscribers,
        )

        enregistrer_entretien_budget_subscribers()
        compteur += 1
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec enregistrement bridge NIM5 Entretien?Budget: %s", e)

    try:
        from src.services.cuisine.inter_module_courses_validation import (
            enregistrer_courses_validation_subscribers,
        )

        enregistrer_courses_validation_subscribers()
        compteur += 1
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec enregistrement bridge NIM6 Courses?Planning: %s", e)

    try:
        from src.services.cuisine.inter_module_inventaire_fifo import (
            enregistrer_inventaire_fifo_subscribers,
        )

        enregistrer_inventaire_fifo_subscribers()
        compteur += 1
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec enregistrement bridge NIM7 Inventaire?FIFO: %s", e)

    try:
        from src.services.utilitaires.bridges_chat_event_bus import (
            enregistrer_chat_event_bus_subscribers,
        )

        enregistrer_chat_event_bus_subscribers()
        compteur += 1
    except Exception as e:  # noqa: BLE001
        logger.warning("Échec enregistrement bridge NIM8 Chat?EventBus: %s", e)

    # -- Webhooks sortants (basse priorité, fire-and-forget) --
    bus.souscrire("*", _livrer_webhooks, priority=5)
    compteur += 1

    # -- Audit logging (basse priorité) --
    bus.souscrire("*", _logger_evenement_audit, priority=10)
    compteur += 1

    _subscribers_enregistres = True
    logger.info("?? %d event subscribers enregistrés", compteur)
    return compteur


__all__ = [
    "enregistrer_subscribers",
    "_filtrer_suggestions_budget_serre",
    "_notifier_document_echeance_proche",
    "_notifier_jalon_ajoute_avec_activites",
    "_sync_entretien_vers_budget",
    "_sync_voyages_vers_planning",
    "_sync_charges_vers_dashboard",
    "_proposer_recettes_saison_depuis_recolte",
    "_creer_tache_entretien_sur_anomalie_energie",
    "_publier_alerte_dashboard_budget",
    "_mettre_a_jour_courses_predictives",
    "_adapter_planning_sur_feedback_recette",
    "_declencher_agent_ia_proactif",
]

