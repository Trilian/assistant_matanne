"""
Jobs cron — Ordonnanceur APScheduler pour l'automatisation quotidienne.

Jobs déclarés :
- 07h00 quotidien : Rappels famille (anniversaires, documents, crèche, jalons)
- 08h00 quotidien : Rappels maison (garanties, contrats, entretien)
- 08h30 quotidien : Rappels généraux (inventaire, garanties intelligentes)
- lundi 06h00    : Entretien saisonnier (vérification tâches de saison)
"""

import logging
import os
import time
from collections.abc import Callable
from datetime import UTC, date, datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import func, text

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def _obtenir_user_ids_actifs() -> list[str]:
    """Récupère les identifiants de tous les utilisateurs actifs.

    Interroge la table ``profils_utilisateurs`` pour obtenir les usernames.
    Si la DB est inaccessible, utilise la variable d'env ``CRON_DEFAULT_USER_IDS``
    (liste séparée par des virgules) ou le fallback ``"matanne"``.
    """
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import ProfilUtilisateur

        with obtenir_contexte_db() as session:
            profils = session.query(ProfilUtilisateur.username).all()
            if profils:
                return [p.username for p in profils if p.username]
    except Exception:
        logger.debug("Impossible de charger les profils utilisateurs, utilisation du fallback")

    fallback = os.getenv("CRON_DEFAULT_USER_IDS", "matanne")
    return [uid.strip() for uid in fallback.split(",") if uid.strip()]


def _envoyer_notif_tous_users(
    dispatcher: object,
    message: str,
    canaux: list[str],
    **kwargs: object,
) -> dict[str, bool]:
    """Envoie une notification à tous les utilisateurs actifs."""
    resultats: dict[str, bool] = {}
    for user_id in _obtenir_user_ids_actifs():
        try:
            res = dispatcher.envoyer(user_id=user_id, message=message, canaux=canaux, **kwargs)  # type: ignore[union-attr]
            resultats.update(res or {})
        except Exception:
            logger.debug("Échec envoi notification à %s", user_id)
    return resultats


def _obtenir_admin_user_ids() -> list[str]:
    """Retourne les identifiants admin pour les alertes d'échec de jobs.

    Priorité:
    1) Variable d'env ``ADMIN_USER_IDS`` (csv)
    2) Fallback sur le 1er utilisateur actif
    """
    admins_env = os.getenv("ADMIN_USER_IDS", "")
    admins = [uid.strip() for uid in admins_env.split(",") if uid.strip()]
    if admins:
        return admins

    actifs = _obtenir_user_ids_actifs()
    return actifs[:1] if actifs else ["matanne"]


def _creer_execution_job(
    *,
    job_id: str,
    job_name: str,
    status: str,
    started_at: datetime,
    dry_run: bool = False,
    source: str = "cron",
    triggered_by_user_id: str | None = None,
) -> int | None:
    """Insère une exécution dans ``job_executions`` (best-effort)."""
    try:
        from src.core.db import obtenir_contexte_db

        with obtenir_contexte_db() as session:
            result = session.execute(
                text(
                    """
                    INSERT INTO job_executions (
                        job_id,
                        job_name,
                        started_at,
                        status,
                        output_logs,
                        triggered_by_user_id,
                        triggered_by_user_role,
                        created_at,
                        modified_at
                    )
                    VALUES (
                        :job_id,
                        :job_name,
                        :started_at,
                        :status,
                        :output_logs,
                        :triggered_by_user_id,
                        :triggered_by_user_role,
                        NOW(),
                        NOW()
                    )
                    RETURNING id
                    """
                ),
                {
                    "job_id": job_id,
                    "job_name": job_name,
                    "started_at": started_at,
                    "status": status,
                    "output_logs": f"source={source};dry_run={dry_run}",
                    "triggered_by_user_id": triggered_by_user_id,
                    "triggered_by_user_role": "admin" if source == "manual" else "system",
                },
            )
            execution_id = result.scalar()
            session.commit()
            return int(execution_id) if execution_id is not None else None
    except Exception:
        logger.debug("Table job_executions indisponible (migration non appliquée?)", exc_info=True)
        return None


def _finaliser_execution_job(
    execution_id: int | None,
    *,
    status: str,
    duration_ms: int,
    error_message: str | None = None,
    output_logs: str | None = None,
) -> None:
    """Met à jour une exécution de job (best-effort)."""
    if execution_id is None:
        return

    try:
        from src.core.db import obtenir_contexte_db

        with obtenir_contexte_db() as session:
            session.execute(
                text(
                    """
                    UPDATE job_executions
                    SET
                        ended_at = NOW(),
                        duration_ms = :duration_ms,
                        status = :status,
                        error_message = :error_message,
                        output_logs = COALESCE(:output_logs, output_logs),
                        modified_at = NOW()
                    WHERE id = :id
                    """
                ),
                {
                    "id": execution_id,
                    "duration_ms": duration_ms,
                    "status": status,
                    "error_message": error_message,
                    "output_logs": output_logs,
                },
            )
            session.commit()
    except Exception:
        logger.debug("Impossible de finaliser job_executions id=%s", execution_id, exc_info=True)


def _notifier_echec_job_admin(job_id: str, job_name: str, erreur: str) -> None:
    """Notifie les admins en push + email si un job échoue."""
    try:
        from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

        dispatcher = get_dispatcher_notifications()
        message = (
            f"Le job '{job_name}' ({job_id}) a échoué. "
            f"Erreur: {erreur[:300]}"
        )
        for admin_id in _obtenir_admin_user_ids():
            dispatcher.envoyer(
                user_id=admin_id,
                message=message,
                canaux=["push", "email"],
                titre="Echec job cron",
                type_email="alerte_critique",
                alerte={
                    "titre": "Echec job cron",
                    "message": message,
                },
            )
    except Exception:
        logger.exception("Impossible d'envoyer la notification d'échec job aux admins")


def _executer_job_trace(
    *,
    job_id: str,
    job_name: str,
    fonction: Callable[[], None],
    dry_run: bool = False,
    source: str = "cron",
    triggered_by_user_id: str | None = None,
    relancer_exception: bool = False,
) -> dict[str, str | int | bool]:
    """Exécute un job avec traçabilité complète (historique + métriques)."""
    started_at = datetime.now(UTC)
    t0 = time.perf_counter()
    execution_id = _creer_execution_job(
        job_id=job_id,
        job_name=job_name,
        status="running",
        started_at=started_at,
        dry_run=dry_run,
        source=source,
        triggered_by_user_id=triggered_by_user_id,
    )

    if dry_run:
        duration_ms = int((time.perf_counter() - t0) * 1000)
        _finaliser_execution_job(
            execution_id,
            status="dry_run",
            duration_ms=duration_ms,
            output_logs="Simulation uniquement - aucune écriture effectuée.",
        )
        return {
            "status": "dry_run",
            "job_id": job_id,
            "message": f"Job '{job_id}' simulé (dry-run).",
            "duration_ms": duration_ms,
            "dry_run": True,
        }

    try:
        fonction()
        duration_ms = int((time.perf_counter() - t0) * 1000)
        _finaliser_execution_job(
            execution_id,
            status="success",
            duration_ms=duration_ms,
        )
        return {
            "status": "ok",
            "job_id": job_id,
            "message": f"Job '{job_id}' exécuté.",
            "duration_ms": duration_ms,
            "dry_run": False,
        }
    except Exception as exc:
        duration_ms = int((time.perf_counter() - t0) * 1000)
        erreur = str(exc)
        _finaliser_execution_job(
            execution_id,
            status="failure",
            duration_ms=duration_ms,
            error_message=erreur[:1000],
        )
        _notifier_echec_job_admin(job_id, job_name, erreur)
        logger.exception("Erreur job %s", job_id)
        if relancer_exception:
            raise
        return {
            "status": "error",
            "job_id": job_id,
            "message": erreur,
            "duration_ms": duration_ms,
            "dry_run": False,
        }


# ─── Jobs ─────────────────────────────────────────────────────────────────────


def _job_rappels_famille() -> None:
    """Évalue et envoie les rappels famille du jour (anniversaires, documents, crèche, jalons)."""
    try:
        from src.services.famille.rappels import ServiceRappelsFamille
        from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

        service = ServiceRappelsFamille()
        nb = service.envoyer_rappels_du_jour()
        logger.info("Rappels famille : %d envoyé(s)", nb)

        # Sprint 9 (MT-02): rappel proactif WhatsApp pour les rappels famille.
        if nb > 0:
            dispatcher = get_dispatcher_notifications()
            _envoyer_notif_tous_users(
                dispatcher,
                message=(
                    f"{nb} rappel(s) famille aujourd'hui (anniversaires, documents, crèche, jalons). "
                    "Ouvre l'application pour le détail."
                ),
                canaux=["whatsapp"],
                titre="Rappels famille",
            )
    except Exception:
        logger.exception("Erreur lors des rappels famille")


def _job_rappels_maison() -> None:
    """Évalue et envoie les rappels maison du jour (garanties, contrats, entretien)."""
    try:
        from src.services.maison.notifications_maison import NotificationsMaisonService

        service = NotificationsMaisonService()
        result = service.evaluer_et_envoyer_rappels()
        if result:
            logger.info(
                "Rappels maison : %d envoyé(s), %d ignoré(s), %d erreur(s)",
                result.rappels_envoyes,
                result.rappels_ignores,
                len(result.erreurs),
            )
    except Exception:
        logger.exception("Erreur lors des rappels maison")


def _job_rappels_generaux() -> None:
    """Évalue les rappels GenericService (inventaire faible, garanties générales)."""
    try:
        from datetime import date

        from src.core.db import obtenir_contexte_db
        from src.core.models import Repas
        from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications
        from src.services.core.rappels_intelligents import get_rappels_intelligents_service
        from sqlalchemy.orm import joinedload

        service = get_rappels_intelligents_service()
        rappels = service.evaluer_rappels()
        if rappels:
            logger.info("Rappels intelligents : %d rappel(s) actif(s)", len(rappels))
        else:
            logger.debug("Rappels intelligents : aucun rappel actif")

        # Sprint 11 (F3): rappel repas du jour avec ingrédients à sortir.
        try:
            aujourd_hui = date.today()
            with obtenir_contexte_db() as session:
                repas_soir = (
                    session.query(Repas)
                    .options(joinedload(Repas.recette))
                    .filter(Repas.date_repas == aujourd_hui, Repas.type_repas == "diner")
                    .first()
                )

                nom_recette = None
                ingredients: list[str] = []
                if repas_soir and getattr(repas_soir, "recette", None):
                    nom_recette = repas_soir.recette.nom or "Repas du soir"
                    for ri in getattr(repas_soir.recette, "ingredients", []):
                        if getattr(ri, "ingredient", None) and getattr(ri.ingredient, "nom", None):
                            ingredients.append(ri.ingredient.nom)

            if nom_recette:
                ingredients_txt = ", ".join(ingredients[:5]) if ingredients else "vérifie la fiche recette"

                dispatcher = get_dispatcher_notifications()
                _envoyer_notif_tous_users(
                    dispatcher,
                    message=f"Ce soir : {nom_recette}. A sortir : {ingredients_txt}.",
                    canaux=["ntfy", "push"],
                    titre="Rappel repas du jour",
                )
        except Exception:
            logger.debug("Rappel repas du jour: impossible d'envoyer le rappel", exc_info=True)
    except Exception:
        logger.exception("Erreur lors des rappels intelligents")


def _job_push_quotidien() -> None:
    """Envoie les alertes urgentes du jour via Web Push (VAPID) à tous les abonnés.

    Complète les notifications ntfy.sh avec des push navigateur pour :
    - Rappels intelligents urgents (garanties, péremptions)
    - Alertes jeux responsable (série de défaites ≥ 5)
    - Alertes prédictives maison
    """
    try:
        from src.services.core.notifications.notif_web_core import get_push_notification_service
        from src.services.core.rappels_intelligents import get_rappels_intelligents_service

        push_service = get_push_notification_service()

        # B-01 : charger les abonnés actifs depuis la DB (pas depuis le cache mémoire)
        try:
            abonnes_db = push_service.charger_tous_abonnements_actifs_db()
        except Exception:
            abonnes_db = []

        # Fallback sur le cache mémoire si DB indisponible
        nb_abonnes = len(abonnes_db) if abonnes_db else len(push_service.obtenir_abonnes())

        if not nb_abonnes:
            logger.debug("Push quotidien : aucun abonné actif, job ignoré")
            return

        logger.debug("Push quotidien : %d abonné(s) actif(s)", nb_abonnes)

        # ── Rappels intelligents ──
        rappels_service = get_rappels_intelligents_service()
        rappels = rappels_service.evaluer_rappels()
        urgents = [r for r in rappels if getattr(r, "priorite", "normale") in ("haute", "critique")]

        for rappel in urgents[:5]:  # limiter à 5 push par run
            titre = getattr(rappel, "titre", "Rappel")
            message = getattr(rappel, "message", "")
            nb_envoyes = push_service.envoyer_a_tous(
                push_service.creer_notification_generique(titre, message)
            ) if hasattr(push_service, "creer_notification_generique") else 0
            if nb_envoyes:
                logger.info("Push urgent '%s' → %d utilisateur(s)", titre, nb_envoyes)

        # ── Alertes jeux responsable ──
        try:
            from src.services.jeux import get_responsable_gaming_service
            jeux_service = get_responsable_gaming_service()
            suivi = jeux_service.obtenir_suivi() if hasattr(jeux_service, "obtenir_suivi") else None
            if suivi and getattr(suivi, "serie_type", None) == "perdu":
                nb_series = int(getattr(suivi, "serie_nb", 0))
                if nb_series >= 5:
                    # Utiliser les abonnés DB plutôt que le cache mémoire
                    user_ids = {str(a.user_id) for a in abonnes_db if a.user_id} or push_service.obtenir_abonnes()
                    for user_id in user_ids:
                        push_service.notifier_alerte_serie_jeux(user_id, nb_series)
                    logger.info("Alerte série jeux (%d défaites) envoyée", nb_series)
        except Exception:
            logger.debug("Alerte jeux responsable : service indisponible")

        logger.info("Push quotidien terminé")
    except Exception:
        logger.exception("Erreur lors du push quotidien")


def _job_entretien_saisonnier() -> None:
    """Vérifie si des tâches d'entretien saisonnières doivent être créées cette semaine."""
    try:
        from src.services.maison import get_entretien_service

        service = get_entretien_service()
        if hasattr(service, "verifier_saison"):
            resultats = service.verifier_saison()
            logger.info("Entretien saisonnier : %s", resultats)
        else:
            logger.warning("Entretien saisonnier : méthode verifier_saison non disponible")
    except Exception:
        logger.exception("Erreur lors de la vérification saisonnière")


def _job_enrichissement_catalogues() -> None:
    """Enrichit les catalogues de référence via l'IA (1er du mois à 3h00)."""
    try:
        from src.services.maison.catalogue_enrichissement_service import (
            get_catalogue_enrichissement_service,
        )

        service = get_catalogue_enrichissement_service()
        resultats = service.enrichir_tout()
        logger.info(
            "Enrichissement catalogues terminé: lessive=%d, domotique=%d, routines=%d, plantes=%d",
            resultats.get("lessive", 0),
            resultats.get("domotique", 0),
            resultats.get("routines", 0),
            resultats.get("plantes", 0),
        )
    except Exception:
        logger.exception("Erreur lors de l'enrichissement des catalogues")


def _job_digest_ntfy() -> None:
    """Envoie le digest quotidien ntfy.sh (résumé tâches + rappels du jour) à 9h."""
    try:
        from src.services.core.notifications.notif_ntfy import obtenir_service_ntfy

        service = obtenir_service_ntfy()
        resultat = service.envoyer_digest_quotidien_sync()
        if resultat.succes:
            logger.info("Digest ntfy envoyé : %s", resultat.message)
        else:
            logger.warning("Digest ntfy échoué : %s", resultat.message)
    except Exception:
        logger.exception("Erreur lors du digest ntfy")


def _job_digest_whatsapp_matinal() -> None:
    """Envoie le digest WhatsApp matinal (repas, tâches, péremptions) à 07h30."""
    try:
        import asyncio

        from src.services.integrations.whatsapp import envoyer_digest_matinal

        resultat = asyncio.run(envoyer_digest_matinal())
        if resultat:
            logger.info("Digest WhatsApp matinal envoyé")
        else:
            logger.debug("Digest WhatsApp matinal non envoyé (désactivé/non configuré)")
    except Exception:
        logger.exception("Erreur lors du digest WhatsApp matinal")


def _job_digest_notifications_queue() -> None:
    """Vide les files digest en attente (Phase 8.4) et envoie les résumés utilisateur.

    Ce job complète le digest ntfy quotidien avec un flush multi-canal basé
    sur les notifications mises en file d'attente par throttling/mode digest.
    """
    try:
        from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

        dispatcher = get_dispatcher_notifications()
        user_ids = dispatcher.lister_users_digest_pending()

        if not user_ids:
            logger.debug("Digest queue: aucun utilisateur à traiter")
            return

        nb_succes = 0
        nb_echecs = 0
        for user_id in user_ids:
            try:
                resultats = dispatcher.vider_digest(user_id)
                if any(resultats.values()):
                    nb_succes += 1
                else:
                    nb_echecs += 1
            except Exception:
                nb_echecs += 1
                logger.debug("Digest queue: échec flush pour %s", user_id, exc_info=True)

        logger.info(
            "Digest queue flush terminé: %d utilisateur(s) traité(s), %d succès, %d échec(s)",
            len(user_ids),
            nb_succes,
            nb_echecs,
        )
    except Exception:
        logger.exception("Erreur lors du flush automatique de la queue digest")


def _job_rappel_courses_ntfy() -> None:
    """Envoie un rappel ntfy.sh pour les articles de courses en attente à 18h."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

        nb_articles = 0
        noms_articles: list[str] = []
        try:
            with obtenir_contexte_db() as session:
                # Compter les articles non achetés dans les listes actives
                from sqlalchemy import text
                result = session.execute(
                    text(
                        "SELECT COUNT(*) FROM articles_courses ac"
                        " JOIN listes_courses ls ON ls.id = ac.liste_id"
                        " WHERE ac.achete = FALSE AND ls.statut IN ('active', 'en_cours')"
                    )
                )
                nb_articles = result.scalar() or 0

                top_rows = session.execute(
                    text(
                        "SELECT i.nom "
                        "FROM articles_courses ac "
                        "JOIN ingredients i ON i.id = ac.ingredient_id "
                        "JOIN listes_courses ls ON ls.id = ac.liste_id "
                        "WHERE ac.achete = FALSE AND ls.statut IN ('active', 'en_cours') "
                        "ORDER BY ac.id ASC LIMIT 8"
                    )
                )
                noms_articles = [str(r[0]) for r in top_rows.fetchall() if r and r[0]]
        except Exception:
            logger.debug("Impossible de compter les articles en attente, rappel annulé")
            return

        if nb_articles == 0:
            logger.debug("Rappel courses ntfy : aucun article en attente")
            return

        import asyncio
        from src.services.core.notifications.notif_ntfy import obtenir_service_ntfy

        service = obtenir_service_ntfy()

        async def _envoyer():
            return await service.envoyer_rappel_courses(nb_articles)

        resultat = asyncio.run(_envoyer())
        if resultat.succes:
            logger.info("Rappel courses ntfy envoyé (%d articles)", nb_articles)

            # Sprint 9 (MT-02): partage WhatsApp de la liste active.
            dispatcher = get_dispatcher_notifications()
            _envoyer_notif_tous_users(
                dispatcher,
                message=f"{nb_articles} article(s) en attente sur la liste.",
                canaux=["whatsapp"],
                type_whatsapp="articles_courses",
                articles=noms_articles or [f"{nb_articles} article(s) en attente"],
                nom_liste="Courses en attente",
                titre="Courses",
            )
        else:
            logger.warning("Rappel courses ntfy échoué : %s", resultat.message)
    except Exception:
        logger.exception("Erreur lors du rappel courses ntfy")


def _job_push_contextuel_soir() -> None:
    """Envoie un push contextuel du soir (planning de demain + météo)."""
    try:
        from datetime import date, timedelta

        from src.core.db import obtenir_contexte_db
        from src.core.models import ArticleInventaire, Repas
        from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications
        from src.services.integrations.weather import obtenir_service_meteo

        demain = date.today() + timedelta(days=1)

        # 1) Planning du lendemain
        plats = []
        try:
            with obtenir_contexte_db() as session:
                repas_demain = session.query(Repas).filter(Repas.date_repas == demain).all()
                for r in repas_demain:
                    nom = r.recette.nom if getattr(r, "recette", None) else (r.notes or "Repas")
                    plats.append(f"{r.type_repas}: {nom}")
        except Exception:
            logger.debug("Push contextuel: planning indisponible")

        # 2) Météo du lendemain
        meteo_txt = "météo indisponible"
        try:
            service_meteo = obtenir_service_meteo()
            previsions = service_meteo.get_previsions(nb_jours=2)
            if previsions:
                prevision = previsions[1] if len(previsions) > 1 else previsions[0]
                meteo_txt = (
                    f"{prevision.condition}, {prevision.temperature_min:.0f}–"
                    f"{prevision.temperature_max:.0f}°C"
                )
        except Exception:
            logger.debug("Push contextuel: météo indisponible")

        # 3) Produits à décongeler (heuristique sur emplacement congélateur)
        a_decongeler = []
        try:
            with obtenir_contexte_db() as session:
                rows = (
                    session.query(ArticleInventaire)
                    .filter(ArticleInventaire.emplacement.ilike("%congel%"))
                    .limit(3)
                    .all()
                )
                a_decongeler = [a.nom or "Article" for a in rows]
        except Exception:
            logger.debug("Push contextuel: impossible de charger les articles congelés")

        repas_msg = " ; ".join(plats) if plats else "Aucun repas planifié"
        decongel_msg = (
            f"Pense à décongeler: {', '.join(a_decongeler)}."
            if a_decongeler
            else ""
        )
        message = (
            f"Demain ({demain.isoformat()}) -> {repas_msg}. "
            f"Météo: {meteo_txt}. {decongel_msg}"
        ).strip()

        dispatcher = get_dispatcher_notifications()
        resultats = _envoyer_notif_tous_users(
            dispatcher,
            message=message,
            canaux=["push"],
            strategie="failover",
            titre="Préparation de demain",
        )
        logger.info("Push contextuel soir envoyé: %s", resultats)
    except Exception:
        logger.exception("Erreur lors du push contextuel soir")


def _job_resume_hebdo() -> None:
    """Génère le résumé hebdomadaire et l'envoie via ntfy/email."""
    try:
        from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications
        from src.services.famille.resume_hebdo import obtenir_service_resume_hebdo

        service = obtenir_service_resume_hebdo()
        resume = service.generer_resume_semaine_sync()
        texte = resume.resume_narratif or (
            f"Résumé semaine {resume.semaine}: score {resume.score_semaine}/100"
        )

        dispatcher = get_dispatcher_notifications()
        # ntfy, email et WhatsApp sont tous tentés. Le dispatcher résout
        # l'email utilisateur depuis la DB quand aucun override n'est fourni.
        canaux = ["ntfy", "email", "whatsapp"]
        kwargs = {
            "titre": f"Résumé hebdomadaire {resume.semaine}",
            "type_email": "resume_hebdo",
            "resume": {
                "semaine": resume.semaine,
                "recettes_cuisinees": resume.repas.nb_repas_realises,
                "budget_depense": resume.budget.total_depenses,
                "activites_jules": resume.activites.nb_activites,
                "taches_maison": resume.taches.nb_taches_realisees,
                "resume_ia": resume.resume_narratif,
            },
            "type_evenement": "resume_hebdo",
        }

        # Canal WhatsApp: résumé compact dédié.
        kwargs["type_whatsapp"] = "rapport_hebdo"

        resultats = _envoyer_notif_tous_users(
            dispatcher,
            message=texte,
            canaux=canaux,
            **kwargs,
        )
        logger.info("Résumé hebdo envoyé: %s", resultats)
    except Exception:
        logger.exception("Erreur lors du résumé hebdomadaire")


def _job_planning_semaine_si_vide() -> None:
    """J-03: vérifie le planning de la semaine prochaine et alerte s'il est vide."""
    try:
        from datetime import date, timedelta

        from src.core.db import obtenir_contexte_db
        from src.core.models import Planning
        from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

        aujourd_hui = date.today()
        lundi_prochain = aujourd_hui + timedelta(days=(7 - aujourd_hui.weekday()))
        dimanche_prochain = lundi_prochain + timedelta(days=6)

        with obtenir_contexte_db() as session:
            planning = (
                session.query(Planning)
                .filter(
                    Planning.semaine_debut <= dimanche_prochain,
                    Planning.semaine_fin >= lundi_prochain,
                    Planning.statut == "actif",
                )
                .first()
            )

        if planning is not None:
            logger.info("J-03: planning déjà actif pour la semaine du %s", lundi_prochain)
            return

        message = (
            f"Aucun planning actif pour la semaine du {lundi_prochain:%d/%m}. "
            "Pense à générer le menu hebdo."
        )
        dispatcher = get_dispatcher_notifications()
        res = _envoyer_notif_tous_users(
            dispatcher,
            message=message,
            canaux=["ntfy", "whatsapp"],
            titre="Planning semaine à générer",
        )
        logger.info("J-03 exécuté: %s", res)
    except Exception:
        logger.exception("Erreur job J-03")


def _job_alertes_peremption_48h() -> None:
    """J-04: envoie les alertes de péremption à J+48h.

    Sprint 13 — W3 : si péremption < 24h, envoie aussi un email critique.
    """
    try:
        from datetime import date, timedelta

        from sqlalchemy import func

        from src.core.db import obtenir_contexte_db
        from src.core.models import ArticleInventaire
        from src.core.models.recettes import Ingredient, Recette, RecetteIngredient
        from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

        aujourd_hui = date.today()
        seuil_48h = aujourd_hui + timedelta(days=2)
        seuil_24h = aujourd_hui + timedelta(days=1)

        with obtenir_contexte_db() as session:
            articles = (
                session.query(ArticleInventaire)
                .filter(
                    ArticleInventaire.date_peremption.isnot(None),
                    ArticleInventaire.date_peremption >= aujourd_hui,
                    ArticleInventaire.date_peremption <= seuil_48h,
                    ArticleInventaire.quantite > 0,
                )
                .order_by(ArticleInventaire.date_peremption.asc())
                .limit(10)
                .all()
            )

        if not articles:
            logger.info("J-04: aucune péremption critique à 48h")
            return

        lignes = [
            f"- {a.nom} ({a.date_peremption:%d/%m})"
            for a in articles
            if getattr(a, "date_peremption", None)
        ]
        message = "Produits à consommer sous 48h:\n" + "\n".join(lignes)

        # IM-9: proposer automatiquement des recettes "rescue" basées sur les produits urgents.
        suggestions_recettes: list[str] = []
        try:
            noms_urgents = [a.nom.lower() for a in articles if getattr(a, "nom", None)]
            if noms_urgents:
                with obtenir_contexte_db() as session:
                    recettes_avec_urgents = (
                        session.query(Recette.nom)
                        .join(RecetteIngredient, RecetteIngredient.recette_id == Recette.id)
                        .join(Ingredient, Ingredient.id == RecetteIngredient.ingredient_id)
                        .filter(func.lower(Ingredient.nom).in_(noms_urgents))
                        .group_by(Recette.id)
                        .order_by(func.count(RecetteIngredient.ingredient_id).desc())
                        .limit(3)
                        .all()
                    )
                suggestions_recettes = [str(row[0]) for row in recettes_avec_urgents if row and row[0]]
        except Exception:
            logger.debug("J-04: impossible de calculer les recettes rescue", exc_info=True)

        if suggestions_recettes:
            message += (
                "\n\nRecettes suggérées: "
                + ", ".join(suggestions_recettes)
                + "."
                + "\nTu peux générer plus d'idées via /api/v1/anti-gaspillage/suggestions-ia."
            )

        # Déterminer si des produits expirent dans les 24h (alerte critique → email)
        articles_critiques_24h = [
            a for a in articles
            if getattr(a, "date_peremption", None) and a.date_peremption <= seuil_24h
        ]

        dispatcher = get_dispatcher_notifications()
        canaux = ["ntfy", "whatsapp"]
        kwargs: dict = {"titre": "Alerte péremption 48h"}

        if articles_critiques_24h:
            # Péremption < 24h → email critique en plus
            canaux = ["ntfy", "whatsapp", "email"]
            noms_critiques = ", ".join(a.nom for a in articles_critiques_24h[:5])
            kwargs.update({
                "type_email": "alerte_critique",
                "alerte": {
                    "titre": "Alerte péremption urgente — < 24h",
                    "message": f"Les produits suivants expirent aujourd'hui ou demain : {noms_critiques}. "
                               "Consommez-les ou congélez-les rapidement.",
                    "lien": "http://localhost:3000/cuisine/inventaire",
                },
            })
            logger.info("J-04: %d produit(s) expirent sous 24h → email critique envoyé", len(articles_critiques_24h))

        res = _envoyer_notif_tous_users(
            dispatcher,
            message=message,
            canaux=canaux,
            **kwargs,
        )
        logger.info("J-04 exécuté: %s", res)
    except Exception:
        logger.exception("Erreur job J-04")


def _job_rapport_mensuel_budget() -> None:
    """J-07: envoie un rapport mensuel consolidé famille + maison + jeux."""
    try:
        from datetime import date, timedelta

        from src.core.db import obtenir_contexte_db
        from src.core.models import BudgetFamille, DepenseMaison, PariSportif
        from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

        aujourd_hui = date.today()
        mois_ref = (aujourd_hui.replace(day=1) - timedelta(days=1))
        mois = mois_ref.month
        annee = mois_ref.year

        with obtenir_contexte_db() as session:
            total_famille = (
                session.query(func.sum(BudgetFamille.montant))
                .filter(
                    func.extract("month", BudgetFamille.date) == mois,
                    func.extract("year", BudgetFamille.date) == annee,
                )
                .scalar()
                or 0
            )
            total_maison = (
                session.query(func.sum(DepenseMaison.montant))
                .filter(DepenseMaison.mois == mois, DepenseMaison.annee == annee)
                .scalar()
                or 0
            )
            mises = (
                session.query(func.sum(PariSportif.mise))
                .filter(
                    func.extract("month", PariSportif.cree_le) == mois,
                    func.extract("year", PariSportif.cree_le) == annee,
                )
                .scalar()
                or 0
            )
            gains = (
                session.query(func.sum(PariSportif.gain))
                .filter(
                    func.extract("month", PariSportif.cree_le) == mois,
                    func.extract("year", PariSportif.cree_le) == annee,
                )
                .scalar()
                or 0
            )

        net_jeux = float(gains) - float(mises)
        total_global = float(total_famille) + float(total_maison)
        message = (
            f"Rapport mensuel {mois:02d}/{annee}: "
            f"Famille {float(total_famille):.2f} EUR, "
            f"Maison {float(total_maison):.2f} EUR, "
            f"Jeux net {net_jeux:.2f} EUR. "
            f"Total dépenses hors jeux: {total_global:.2f} EUR."
        )

        dispatcher = get_dispatcher_notifications()
        res = _envoyer_notif_tous_users(
            dispatcher,
            message=message,
            canaux=["ntfy", "email", "whatsapp"],
            titre=f"Rapport mensuel {mois:02d}/{annee}",
            type_email="rapport_mensuel",
            rapport={
                "mois": f"{mois:02d}/{annee}",
                "depenses_famille": float(total_famille),
                "depenses_maison": float(total_maison),
                "mises_jeux": float(mises),
                "gains_jeux": float(gains),
                "net_jeux": net_jeux,
                "total_global": total_global,
            },
            type_whatsapp="rapport_hebdo",
        )
        logger.info("J-07 exécuté: %s", res)
    except Exception:
        logger.exception("Erreur job J-07")


def _job_score_weekend() -> None:
    """J-08: calcule un score weekend basé sur activités + météo + contexte Jules."""
    try:
        from datetime import date, timedelta

        from src.core.db import obtenir_contexte_db
        from src.core.models import ActiviteFamille
        from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications
        from src.services.integrations.weather import obtenir_service_meteo

        aujourd_hui = date.today()
        samedi = aujourd_hui + timedelta(days=(5 - aujourd_hui.weekday()) % 7)
        dimanche = samedi + timedelta(days=1)

        with obtenir_contexte_db() as session:
            activites = (
                session.query(ActiviteFamille)
                .filter(ActiviteFamille.date_prevue >= samedi, ActiviteFamille.date_prevue <= dimanche)
                .all()
            )

        bonus_meteo = 0
        meteo_resume = "indisponible"
        try:
            service_meteo = obtenir_service_meteo()
            previsions = service_meteo.get_previsions(nb_jours=3)
            if previsions:
                p = previsions[-1]
                cond = (getattr(p, "condition", "") or "").lower()
                meteo_resume = f"{getattr(p, 'condition', 'variable')}"
                if "soleil" in cond or "clair" in cond:
                    bonus_meteo = 15
                elif "pluie" in cond or "orage" in cond:
                    bonus_meteo = -10
        except Exception:
            pass

        nb_activites = len(activites)
        bonus_jules = 10 if nb_activites > 0 else 0
        score = max(0, min(100, 45 + nb_activites * 12 + bonus_meteo + bonus_jules))

        message = (
            f"Score weekend: {score}/100. "
            f"Activités prévues: {nb_activites}. Météo: {meteo_resume}."
        )
        dispatcher = get_dispatcher_notifications()
        res = _envoyer_notif_tous_users(
            dispatcher,
            message=message,
            canaux=["ntfy", "whatsapp"],
            titre="Score weekend",
        )
        logger.info("J-08 exécuté: %s", res)
    except Exception:
        logger.exception("Erreur job J-08")


def _job_controle_contrats_garanties() -> None:
    """J-09: contrôle des contrats/garanties expirant dans 3 mois.

    Sprint 13 — W3 : si garantie expire dans 30j, envoie aussi un email critique.
    """
    try:
        from datetime import date, timedelta

        from src.core.db import obtenir_contexte_db
        from src.core.models import Contrat, Garantie
        from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

        aujourd_hui = date.today()
        horizon = aujourd_hui + timedelta(days=90)
        horizon_30j = aujourd_hui + timedelta(days=30)

        with obtenir_contexte_db() as session:
            contrats = (
                session.query(Contrat)
                .filter(
                    Contrat.statut == "actif",
                    (
                        ((Contrat.date_renouvellement.isnot(None)) & (Contrat.date_renouvellement >= aujourd_hui) & (Contrat.date_renouvellement <= horizon))
                        | ((Contrat.date_fin.isnot(None)) & (Contrat.date_fin >= aujourd_hui) & (Contrat.date_fin <= horizon))
                    ),
                )
                .all()
            )
            garanties = (
                session.query(Garantie)
                .filter(
                    Garantie.statut == "active",
                    Garantie.date_fin_garantie >= aujourd_hui,
                    Garantie.date_fin_garantie <= horizon,
                )
                .all()
            )

        if not contrats and not garanties:
            logger.info("J-09: aucun contrat/garantie à échéance sur 3 mois")
            return

        message = (
            f"Échéances 3 mois: {len(contrats)} contrat(s), {len(garanties)} garantie(s). "
            "Vérifie les renouvellements et options de résiliation."
        )

        # Garanties expirant dans 30j → email critique
        garanties_30j = [
            g for g in garanties
            if getattr(g, "date_fin_garantie", None) and g.date_fin_garantie <= horizon_30j
        ]

        canaux = ["ntfy", "whatsapp"]
        kwargs: dict = {"titre": "Contrats & garanties à surveiller"}

        if garanties_30j:
            canaux = ["ntfy", "whatsapp", "email"]
            noms_garanties = ", ".join(
                getattr(g, "appareil", None) or getattr(g, "nom", "Garantie")
                for g in garanties_30j[:5]
            )
            kwargs.update({
                "type_email": "alerte_critique",
                "alerte": {
                    "titre": f"Garanties expirant dans moins de 30 jours ({len(garanties_30j)})",
                    "message": f"Les garanties suivantes expirent bientôt : {noms_garanties}. "
                               "Pensez à vérifier les options de prolongation ou de remplacement.",
                    "lien": "http://localhost:3000/maison/entretien",
                },
            })
            logger.info("J-09: %d garantie(s) expirent dans 30j → email critique envoyé", len(garanties_30j))

        dispatcher = get_dispatcher_notifications()
        res = _envoyer_notif_tous_users(
            dispatcher,
            message=message,
            canaux=canaux,
            **kwargs,
        )
        logger.info("J-09 exécuté: %s", res)
    except Exception:
        logger.exception("Erreur job J-09")


def _job_rapport_jardin() -> None:
    """J-10: rapport jardin hebdomadaire (arrosage + récoltes/semis)."""
    try:
        from datetime import date, timedelta

        from src.core.db import obtenir_contexte_db
        from src.core.models import ElementJardin, JournalJardin
        from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

        aujourd_hui = date.today()
        horizon = aujourd_hui + timedelta(days=7)
        debut = aujourd_hui - timedelta(days=7)

        with obtenir_contexte_db() as session:
            actifs = session.query(ElementJardin).filter(ElementJardin.statut == "actif").all()
            recoltes_proches = (
                session.query(ElementJardin)
                .filter(
                    ElementJardin.date_recolte_prevue.isnot(None),
                    ElementJardin.date_recolte_prevue >= aujourd_hui,
                    ElementJardin.date_recolte_prevue <= horizon,
                )
                .all()
            )
            actions = (
                session.query(JournalJardin.action, func.count(JournalJardin.id))
                .filter(JournalJardin.date >= debut, JournalJardin.date <= aujourd_hui)
                .group_by(JournalJardin.action)
                .all()
            )

        action_txt = ", ".join(f"{a}:{n}" for a, n in actions[:4]) if actions else "aucune action loggée"
        message = (
            f"Jardin: {len(actifs)} élément(s) actifs, {len(recoltes_proches)} récolte(s) prévues sous 7 jours. "
            f"Journal 7j: {action_txt}."
        )

        dispatcher = get_dispatcher_notifications()
        res = _envoyer_notif_tous_users(
            dispatcher,
            message=message,
            canaux=["ntfy", "whatsapp"],
            titre="Rapport jardin hebdo",
        )
        logger.info("J-10 exécuté: %s", res)
    except Exception:
        logger.exception("Erreur job J-10")


def _job_score_bien_etre_hebdo() -> None:
    """J-11: calcule le score bien-être hebdo et alerte en cas de dérive."""
    try:
        from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications
        from src.services.dashboard.score_bienetre import get_score_bien_etre_service

        service = get_score_bien_etre_service()
        score = service.calculer_score()
        score_global = int(score.get("score_global", 0))
        trend = float(score.get("trend_semaine_precedente", 0.0))

        niveau = "normal"
        if score_global < 60:
            niveau = "alerte"
        elif score_global < 75:
            niveau = "attention"

        message = (
            f"Score bien-être hebdo: {score_global}/100 "
            f"({trend:+.0f} pts vs semaine précédente) - niveau {niveau}."
        )

        dispatcher = get_dispatcher_notifications()
        canaux = ["ntfy", "whatsapp"] if niveau != "normal" else ["ntfy"]
        res = _envoyer_notif_tous_users(
            dispatcher,
            message=message,
            canaux=canaux,
            titre="Score bien-être hebdo",
        )
        logger.info("J-11 exécuté: %s", res)
    except Exception:
        logger.exception("Erreur job J-11")


def _job_garmin_sync_matinal() -> None:
    """Synchronise les données Garmin de tous les profils connectés (LT-01)."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import ProfilUtilisateur
        from src.services.integrations.garmin.service import get_garmin_service

        nb_profils = 0
        with obtenir_contexte_db() as session:
            profils = (
                session.query(ProfilUtilisateur)
                .filter(ProfilUtilisateur.garmin_connected == True)  # noqa: E712
                .all()
            )
            service = get_garmin_service()
            for profil in profils:
                try:
                    service.sync_user_data(user_id=profil.id, days_back=2, db=session)
                    nb_profils += 1
                except Exception:
                    logger.exception("Sync Garmin échouée pour le profil %s", profil.id)
        logger.info("Sync Garmin matinale terminée (%d profil(s))", nb_profils)
    except Exception:
        logger.exception("Erreur lors de la sync Garmin matinale")


def _job_automations() -> None:
    """Exécute périodiquement les règles d'automation actives (LT-04)."""
    try:
        from src.services.utilitaires.automations_engine import get_moteur_automations_service

        result = get_moteur_automations_service().executer_automations_actives()
        logger.info(
            "Automations exécutées: %s sur %s règle(s)",
            result.get("executed", 0),
            result.get("total", 0),
        )
    except Exception:
        logger.exception("Erreur lors de l'exécution des automations")


def _job_points_famille_hebdo() -> None:
    """Calcule les points famille hebdo (LT-02, dim 20h00)."""
    try:
        from src.services.dashboard.points_famille import get_points_famille_service

        points = get_points_famille_service().calculer_points()
        logger.info("Points famille hebdo recalculés: %s", points.get("total_points", 0))
    except Exception:
        logger.exception("Erreur lors du calcul des points famille hebdo")


def _job_sync_google_calendar() -> None:
    """J1 — Sync planning repas + activités → Google Calendar (quotidien 23h00)."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import CalendrierExterne
        from src.services.famille.calendrier import get_calendar_sync_service

        service = get_calendar_sync_service()

        with obtenir_contexte_db() as session:
            calendriers = (
                session.query(CalendrierExterne)
                .filter(
                    CalendrierExterne.enabled == True,  # noqa: E712
                    CalendrierExterne.provider == "google",
                )
                .all()
            )
            user_ids = list({str(c.user_id) for c in calendriers if c.user_id})

        nb_syncs = 0
        for user_id in user_ids:
            try:
                user_calendriers = service.lister_calendriers_utilisateur(user_id=user_id, db=session)
                for cal_config in user_calendriers:
                    result = service.sync_google_calendar(cal_config)
                    if result.success:
                        nb_syncs += 1
                    else:
                        logger.warning("J1: sync Google Calendar échouée pour user %s: %s", user_id, result.message)
            except Exception:
                logger.exception("J1: erreur sync pour user %s", user_id)

        logger.info("J1 sync_google_calendar terminée: %d calendrier(s) synchronisé(s)", nb_syncs)
    except Exception:
        logger.exception("Erreur job J1 sync_google_calendar")


def _job_alerte_stock_bas() -> None:
    """J3 — Alerte stock bas : articles inventaire < seuil → ajout auto liste courses (quotidien 07h00)."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import ArticleInventaire, ArticleCourses, ListeCourses
        from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications
        from datetime import date

        articles_stock_bas: list[ArticleInventaire] = []
        with obtenir_contexte_db() as session:
            articles_stock_bas = (
                session.query(ArticleInventaire)
                .filter(
                    ArticleInventaire.quantite < ArticleInventaire.quantite_min,
                    ArticleInventaire.quantite_min > 0,
                )
                .limit(30)
                .all()
            )

            if not articles_stock_bas:
                logger.info("J3: aucun article en stock bas")
                return

            # Trouver ou créer la liste courses active du jour
            aujourd_hui = date.today()
            liste = (
                session.query(ListeCourses)
                .filter(
                    ListeCourses.statut.in_(["active", "en_cours"]),
                )
                .order_by(ListeCourses.id.desc())
                .first()
            )

            if liste is None:
                liste = ListeCourses(
                    nom=f"Courses {aujourd_hui:%d/%m/%Y}",
                    statut="active",
                )
                session.add(liste)
                session.flush()

            # Ajouter les articles manquants (éviter doublons)
            ingredient_ids_existants: set[int] = {
                ac.ingredient_id
                for ac in session.query(ArticleCourses.ingredient_id)
                .filter(ArticleCourses.liste_id == liste.id, ArticleCourses.achete == False)  # noqa: E712
                .all()
            }

            nb_ajoutes = 0
            for article in articles_stock_bas:
                if article.ingredient_id in ingredient_ids_existants:
                    continue
                quantite_a_acheter = max(
                    article.quantite_min - article.quantite,
                    article.quantite_min,
                )
                nouvel_article = ArticleCourses(
                    liste_id=liste.id,
                    ingredient_id=article.ingredient_id,
                    quantite_necessaire=quantite_a_acheter,
                    achete=False,
                )
                session.add(nouvel_article)
                nb_ajoutes += 1

            session.commit()

        if nb_ajoutes > 0:
            noms = [a.nom or f"Ingrédient #{a.ingredient_id}" for a in articles_stock_bas[:5]]
            message = (
                f"{nb_ajoutes} article(s) ajouté(s) automatiquement à la liste courses "
                f"(stock bas) : {', '.join(noms)}{'...' if len(articles_stock_bas) > 5 else ''}."
            )
            dispatcher = get_dispatcher_notifications()
            _envoyer_notif_tous_users(
                dispatcher,
                message=message,
                canaux=["ntfy"],
                titre="Stock bas — courses mises à jour",
            )
            logger.info("J3: %d article(s) ajouté(s) à la liste courses", nb_ajoutes)
        else:
            logger.info("J3: aucun nouvel article à ajouter (déjà sur la liste)")
    except Exception:
        logger.exception("Erreur job J3 alerte_stock_bas")


def _job_archive_batches_expires() -> None:
    """J4 — Archive les préparations batch cooking expirées (quotidien 02h00)."""
    try:
        from datetime import datetime

        from sqlalchemy import text

        from src.core.db import obtenir_contexte_db

        with obtenir_contexte_db() as session:
            result = session.execute(
                text(
                    "UPDATE preparations_batch"
                    " SET consomme = TRUE"
                    " WHERE consomme = FALSE"
                    "   AND date_peremption IS NOT NULL"
                    "   AND date_peremption < :now"
                ),
                {"now": datetime.utcnow()},
            )
            nb_archivees = result.rowcount
            session.commit()

        logger.info("J4: %d préparation(s) batch expirée(s) archivée(s)", nb_archivees)
    except Exception:
        logger.exception("Erreur job J4 archive_batches_expires")


def _job_rapport_maison_mensuel() -> None:
    """J5 — Rapport maison mensuel : projets actifs, entretiens N+30j, dépenses mois N-1 (1er/mois 09h30)."""
    try:
        from datetime import date, timedelta

        from src.core.db import obtenir_contexte_db
        from src.core.models import DepenseMaison, Projet, TacheEntretien
        from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

        aujourd_hui = date.today()
        mois_ref = (aujourd_hui.replace(day=1) - timedelta(days=1))
        mois = mois_ref.month
        annee = mois_ref.year
        horizon_30j = aujourd_hui + timedelta(days=30)

        with obtenir_contexte_db() as session:
            nb_projets_actifs = (
                session.query(Projet)
                .filter(Projet.statut == "en_cours")
                .count()
            )
            entretiens_a_venir = (
                session.query(TacheEntretien)
                .filter(
                    TacheEntretien.fait == False,  # noqa: E712
                    TacheEntretien.prochaine_fois.isnot(None),
                    TacheEntretien.prochaine_fois >= aujourd_hui,
                    TacheEntretien.prochaine_fois <= horizon_30j,
                )
                .count()
            )
            total_depenses = (
                session.query(func.sum(DepenseMaison.montant))
                .filter(DepenseMaison.mois == mois, DepenseMaison.annee == annee)
                .scalar()
                or 0
            )

        message = (
            f"Rapport maison {mois:02d}/{annee}: "
            f"{nb_projets_actifs} projet(s) en cours, "
            f"{entretiens_a_venir} entretien(s) planifié(s) dans 30j, "
            f"dépenses mois N-1: {float(total_depenses):.2f} EUR."
        )

        import os
        email_dest = os.getenv("EMAIL_RESUME_HEBDO")
        canaux = ["ntfy", "email"] if email_dest else ["ntfy"]
        kwargs: dict = {
            "titre": f"Rapport maison mensuel {mois:02d}/{annee}",
        }
        if email_dest:
            kwargs.update({
                "email": email_dest,
                "type_email": "rapport_mensuel",
                "rapport": {
                    "mois": f"{mois:02d}/{annee}",
                    "projets_actifs": nb_projets_actifs,
                    "entretiens_a_venir": entretiens_a_venir,
                    "depenses_maison": float(total_depenses),
                },
            })

        dispatcher = get_dispatcher_notifications()
        res = _envoyer_notif_tous_users(dispatcher, message=message, canaux=canaux, **kwargs)
        logger.info("J5 rapport_maison_mensuel exécuté: %s", res)
    except Exception:
        logger.exception("Erreur job J5 rapport_maison_mensuel")


def _job_sync_openfoodfacts() -> None:
    """J6 — Refresh cache OpenFoodFacts pour les articles scannés les 30 derniers jours (dim 03h00)."""
    try:
        from datetime import datetime, timedelta

        from src.core.db import obtenir_contexte_db
        from src.core.models import ArticleInventaire
        from src.core.models.user_preferences import OpenFoodFactsCache
        from src.services.integrations.produit import OpenFoodFactsService
        import time

        service = OpenFoodFactsService()
        horizon = datetime.utcnow() - timedelta(days=30)

        with obtenir_contexte_db() as session:
            # Articles scannés (avec code-barres) ajoutés ou modifiés dans les 30 derniers jours
            articles = (
                session.query(ArticleInventaire)
                .filter(
                    ArticleInventaire.code_barres.isnot(None),
                    ArticleInventaire.code_barres != "",
                )
                .limit(100)
                .all()
            )

            codes_barres = list({a.code_barres for a in articles if a.code_barres})

        nb_maj = 0
        for code in codes_barres:
            try:
                produit = service.rechercher_produit(code)
                if produit is None:
                    continue

                with obtenir_contexte_db() as session:
                    cache_entry = (
                        session.query(OpenFoodFactsCache)
                        .filter(OpenFoodFactsCache.code_barres == code)
                        .first()
                    )
                    if cache_entry is None:
                        cache_entry = OpenFoodFactsCache(code_barres=code)
                        session.add(cache_entry)

                    cache_entry.nom = produit.nom
                    cache_entry.marque = produit.marque
                    cache_entry.categorie = produit.categorie
                    cache_entry.nutriscore = produit.nutriscore
                    cache_entry.nova_group = produit.nova_group
                    cache_entry.ecoscore = produit.ecoscore
                    cache_entry.nutrition_data = produit.nutrition_data
                    cache_entry.image_url = produit.image_url
                    cache_entry.last_updated = datetime.utcnow()
                    session.commit()

                nb_maj += 1
                # Respecter l'API publique OpenFoodFacts (throttle léger)
                time.sleep(0.5)
            except Exception:
                logger.debug("J6: impossible de mettre à jour le code-barres %s", code, exc_info=True)

        logger.info("J6 sync_openfoodfacts terminée: %d produit(s) mis à jour sur %d", nb_maj, len(codes_barres))
    except Exception:
        logger.exception("Erreur job J6 sync_openfoodfacts")


def _job_prediction_courses_weekly() -> None:
    """JOB-1 — Pré-remplit la liste courses hebdomadaire selon l'historique."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import ArticleCourses, ListeCourses
        from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications
        from src.services.cuisine.prediction_courses import obtenir_service_prediction_courses

        predictions = obtenir_service_prediction_courses().predire_articles(limite=30)
        if not predictions:
            logger.info("JOB-1: aucune prédiction courses disponible")
            return

        with obtenir_contexte_db() as session:
            liste = (
                session.query(ListeCourses)
                .filter(ListeCourses.archivee.is_(False))
                .order_by(ListeCourses.id.desc())
                .first()
            )
            if liste is None:
                liste = ListeCourses(nom="Courses prédites", archivee=False)
                session.add(liste)
                session.flush()

            existants = {
                row[0]
                for row in session.query(ArticleCourses.ingredient_id)
                .filter(
                    ArticleCourses.liste_id == liste.id,
                    ArticleCourses.achete.is_(False),
                )
                .all()
            }

            nb_ajoutes = 0
            for pred in predictions:
                ingredient_id = pred.get("ingredient_id")
                if not ingredient_id or ingredient_id in existants:
                    continue

                session.add(
                    ArticleCourses(
                        liste_id=liste.id,
                        ingredient_id=int(ingredient_id),
                        quantite_necessaire=float(pred.get("quantite_suggeree", 1.0) or 1.0),
                        priorite="moyenne",
                        achete=False,
                        suggere_par_ia=True,
                        notes="Ajout automatique (prediction hebdo)",
                    )
                )
                nb_ajoutes += 1

            session.commit()

        if nb_ajoutes > 0:
            dispatcher = get_dispatcher_notifications()
            _envoyer_notif_tous_users(
                dispatcher,
                message=f"{nb_ajoutes} article(s) prédit(s) ajouté(s) à la liste courses.",
                canaux=["ntfy", "push"],
                titre="Courses hebdo prédites",
            )
        logger.info("JOB-1 exécuté: %d article(s) ajouté(s)", nb_ajoutes)
    except Exception:
        logger.exception("Erreur JOB-1 prediction_courses_weekly")


def _job_sync_jeux_budget() -> None:
    """JOB-2 — Synchronise les gains/pertes jeux vers le budget famille."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import BudgetFamille, PariSportif

        today = date.today()
        debut_jour = datetime.combine(today - timedelta(days=1), datetime.min.time(), tzinfo=UTC)
        fin_jour = datetime.combine(today, datetime.min.time(), tzinfo=UTC)

        with obtenir_contexte_db() as session:
            mises = (
                session.query(func.sum(PariSportif.mise))
                .filter(PariSportif.date_pari >= debut_jour, PariSportif.date_pari < fin_jour)
                .scalar()
                or 0
            )
            gains = (
                session.query(func.sum(PariSportif.gain))
                .filter(PariSportif.date_pari >= debut_jour, PariSportif.date_pari < fin_jour)
                .scalar()
                or 0
            )

            net = float(gains) - float(mises)
            if net == 0:
                logger.info("JOB-2: aucun mouvement jeux à synchroniser")
                return

            existe = (
                session.query(BudgetFamille)
                .filter(
                    BudgetFamille.date == (today - timedelta(days=1)),
                    BudgetFamille.categorie == "jeux",
                    BudgetFamille.description == "Sync jeux auto",
                )
                .first()
            )
            if existe is None:
                session.add(
                    BudgetFamille(
                        date=today - timedelta(days=1),
                        categorie="jeux",
                        description="Sync jeux auto",
                        montant=abs(net),
                        notes=f"Net jeux J-1: {net:.2f} EUR (gains={float(gains):.2f}, mises={float(mises):.2f})",
                    )
                )
                session.commit()

        logger.info("JOB-2 exécuté: net jeux J-1 synchronisé (%.2f EUR)", net)
    except Exception:
        logger.exception("Erreur JOB-2 sync_jeux_budget")


def _job_analyse_nutrition_hebdo() -> None:
    """JOB-3 — Analyse nutritionnelle hebdomadaire simple sur les repas planifiés."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import Recette, Repas
        from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

        aujourd_hui = date.today()
        debut = aujourd_hui - timedelta(days=7)

        with obtenir_contexte_db() as session:
            rows = (
                session.query(Recette.calories, Recette.proteines, Recette.glucides, Recette.lipides)
                .join(Repas, Repas.recette_id == Recette.id)
                .filter(Repas.date_repas >= debut, Repas.date_repas <= aujourd_hui)
                .all()
            )

        if not rows:
            logger.info("JOB-3: aucune donnée nutritionnelle sur la semaine")
            return

        nb = len(rows)
        cal_moy = sum(float(r[0] or 0) for r in rows) / nb
        prot_moy = sum(float(r[1] or 0) for r in rows) / nb
        gluc_moy = sum(float(r[2] or 0) for r in rows) / nb
        lip_moy = sum(float(r[3] or 0) for r in rows) / nb

        carences: list[str] = []
        if prot_moy < 15:
            carences.append("protéines")
        if cal_moy < 350:
            carences.append("apports énergétiques")

        msg_carences = (
            f" Carences possibles: {', '.join(carences)}." if carences else ""
        )
        message = (
            f"Nutrition semaine: {cal_moy:.0f} kcal/repas, {prot_moy:.1f}g prot, "
            f"{gluc_moy:.1f}g gluc, {lip_moy:.1f}g lip.{msg_carences}"
        )

        dispatcher = get_dispatcher_notifications()
        _envoyer_notif_tous_users(
            dispatcher,
            message=message,
            canaux=["ntfy", "email"],
            titre="Analyse nutrition hebdo",
            type_email="resume_hebdo",
            resume={"semaine": f"{debut.isoformat()} → {aujourd_hui.isoformat()}", "resume_ia": message},
        )
        logger.info("JOB-3 exécuté")
    except Exception:
        logger.exception("Erreur JOB-3 analyse_nutrition_hebdo")


def _job_alertes_energie() -> None:
    """JOB-4 — Détection simple d'anomalies énergie (vs moyenne historique)."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import ReleveEnergie
        from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

        alertes: list[str] = []
        with obtenir_contexte_db() as session:
            types = [r[0] for r in session.query(ReleveEnergie.type_energie).distinct().all() if r and r[0]]
            for t in types:
                releves = (
                    session.query(ReleveEnergie)
                    .filter(ReleveEnergie.type_energie == t)
                    .order_by(ReleveEnergie.annee.desc(), ReleveEnergie.mois.desc())
                    .limit(6)
                    .all()
                )
                if len(releves) < 4:
                    continue

                dernier = float(releves[0].consommation or 0)
                historique = [float(r.consommation or 0) for r in releves[1:] if r.consommation is not None]
                if not historique:
                    continue

                moyenne = sum(historique) / len(historique)
                if moyenne > 0 and dernier > moyenne * 1.25:
                    alertes.append(f"{t}: {dernier:.1f} (> +25% vs {moyenne:.1f})")

        if not alertes:
            logger.info("JOB-4: aucune anomalie énergie détectée")
            return

        message = "Anomalies énergie détectées: " + "; ".join(alertes)
        dispatcher = get_dispatcher_notifications()
        _envoyer_notif_tous_users(
            dispatcher,
            message=message,
            canaux=["ntfy", "push", "email"],
            titre="Alerte consommation énergie",
            type_email="alerte_critique",
            alerte={"titre": "Alerte consommation énergie", "message": message},
        )
        logger.info("JOB-4 exécuté: %d alerte(s)", len(alertes))
    except Exception:
        logger.exception("Erreur JOB-4 alertes_energie")


def _job_nettoyage_logs() -> None:
    """JOB-5 — Purge des logs d'audit/sécurité > 90 jours."""
    try:
        from src.core.db import obtenir_contexte_db

        with obtenir_contexte_db() as session:
            nb_audit = session.execute(
                text("DELETE FROM historique_actions WHERE cree_le < (NOW() - INTERVAL '90 days')")
            ).rowcount or 0
            nb_secu = session.execute(
                text("DELETE FROM logs_securite WHERE created_at < (NOW() - INTERVAL '90 days')")
            ).rowcount or 0
            session.commit()

        logger.info("JOB-5 exécuté: purge logs (audit=%s, securite=%s)", nb_audit, nb_secu)
    except Exception:
        logger.exception("Erreur JOB-5 nettoyage_logs")


def _job_check_garmin_anomalies() -> None:
    """JOB-6 — Alerte si inactivité Garmin > 3 jours."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import ActiviteGarmin, ProfilUtilisateur
        from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

        seuil = datetime.now(UTC) - timedelta(days=3)
        inactifs: list[str] = []

        with obtenir_contexte_db() as session:
            profils = (
                session.query(ProfilUtilisateur)
                .filter(ProfilUtilisateur.garmin_connected.is_(True))
                .all()
            )
            for profil in profils:
                derniere = (
                    session.query(func.max(ActiviteGarmin.date_debut))
                    .filter(ActiviteGarmin.user_id == profil.id)
                    .scalar()
                )
                if derniere is None or derniere < seuil:
                    inactifs.append(profil.display_name or profil.username)

        if inactifs:
            message = "Aucune activité Garmin depuis 3 jours: " + ", ".join(inactifs)
            dispatcher = get_dispatcher_notifications()
            _envoyer_notif_tous_users(
                dispatcher,
                message=message,
                canaux=["ntfy", "push"],
                titre="Inactivité Garmin",
            )
            logger.info("JOB-6 exécuté: %d profil(s) inactif(s)", len(inactifs))
        else:
            logger.info("JOB-6: aucune anomalie Garmin")
    except Exception:
        logger.exception("Erreur JOB-6 check_garmin_anomalies")


def _job_resume_jardin_saisonnier() -> None:
    """JOB-7 — Résumé mensuel jardin avec recommandations synthétiques."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import ElementJardin, JournalJardin
        from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

        aujourd_hui = date.today()
        debut = aujourd_hui - timedelta(days=30)

        with obtenir_contexte_db() as session:
            nb_elements = session.query(ElementJardin).filter(ElementJardin.statut == "actif").count()
            actions = (
                session.query(JournalJardin.action, func.count(JournalJardin.id))
                .filter(JournalJardin.date >= debut, JournalJardin.date <= aujourd_hui)
                .group_by(JournalJardin.action)
                .all()
            )

        top_actions = ", ".join(f"{a}:{n}" for a, n in actions[:4]) if actions else "aucune"
        recos = "Pense à planifier arrosage + taille préventive si hausse températures."
        message = (
            f"Bilan jardin mensuel: {nb_elements} élément(s) actif(s), actions: {top_actions}. "
            f"Reco: {recos}"
        )

        dispatcher = get_dispatcher_notifications()
        _envoyer_notif_tous_users(
            dispatcher,
            message=message,
            canaux=["ntfy", "email"],
            titre="Résumé jardin saisonnier",
            type_email="resume_hebdo",
            resume={"semaine": "bilan mois", "resume_ia": message},
        )
        logger.info("JOB-7 exécuté")
    except Exception:
        logger.exception("Erreur JOB-7 resume_jardin_saisonnier")


def _job_expiration_documents() -> None:
    """JOB-8 — Rappels de documents proches d'expiration."""
    try:
        from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications
        from src.services.famille.documents import obtenir_service_documents

        alertes = obtenir_service_documents().obtenir_alertes_expiration(jours=30)
        if not alertes:
            logger.info("JOB-8: aucun document à renouveler")
            return

        noms = ", ".join(a.get("nom") or a.get("titre") or "document" for a in alertes[:5])
        message = f"{len(alertes)} document(s) à renouveler sous 30 jours: {noms}."
        dispatcher = get_dispatcher_notifications()
        _envoyer_notif_tous_users(
            dispatcher,
            message=message,
            canaux=["ntfy", "email", "push"],
            titre="Expiration documents",
            type_email="alerte_critique",
            alerte={"titre": "Expiration documents", "message": message},
        )
        logger.info("JOB-8 exécuté: %d alerte(s)", len(alertes))
    except Exception:
        logger.exception("Erreur JOB-8 expiration_documents")


def _job_sync_calendrier_scolaire() -> None:
    """INNO-14 — Resynchronise les calendriers scolaires auto actifs."""
    try:
        from src.services.famille.calendrier_scolaire import (
            synchroniser_calendriers_scolaires_actifs,
        )

        result = synchroniser_calendriers_scolaires_actifs()
        logger.info(
            "Calendrier scolaire auto sync: %d total, %d succes, %d erreurs",
            result.get("total", 0),
            result.get("succes", 0),
            result.get("erreurs", 0),
        )
    except Exception:
        logger.exception("Erreur INNO-14 sync calendrier scolaire")


_REGISTRE_JOBS: dict[str, tuple[str, Callable[[], None]]] = {
    # Jobs existants
    "rappels_famille": ("Rappels famille quotidiens", _job_rappels_famille),
    "rappels_maison": ("Rappels maison quotidiens", _job_rappels_maison),
    "rappels_generaux": ("Rappels intelligents quotidiens", _job_rappels_generaux),
    "entretien_saisonnier": ("Entretien saisonnier hebdomadaire", _job_entretien_saisonnier),
    "push_quotidien": ("Notifications Web Push quotidiennes", _job_push_quotidien),
    "enrichissement_catalogues": ("Enrichissement mensuel catalogues IA", _job_enrichissement_catalogues),
    "digest_ntfy": ("Digest quotidien ntfy.sh", _job_digest_ntfy),
    "digest_whatsapp_matinal": ("Digest WhatsApp matinal", _job_digest_whatsapp_matinal),
    "digest_notifications_queue": ("Flush digest notifications", _job_digest_notifications_queue),
    "rappel_courses": ("Rappel courses ntfy.sh", _job_rappel_courses_ntfy),
    "push_contextuel_soir": ("Push contextuel soir", _job_push_contextuel_soir),
    "resume_hebdo": ("Résumé hebdomadaire", _job_resume_hebdo),
    "planning_semaine_si_vide": ("Vérification planning semaine suivante", _job_planning_semaine_si_vide),
    "alertes_peremption_48h": ("Alertes péremption 48h", _job_alertes_peremption_48h),
    "rapport_mensuel_budget": ("Rapport mensuel budget", _job_rapport_mensuel_budget),
    "score_weekend": ("Score weekend", _job_score_weekend),
    "controle_contrats_garanties": ("Contrats et garanties", _job_controle_contrats_garanties),
    "rapport_jardin": ("Rapport jardin hebdo", _job_rapport_jardin),
    "score_bien_etre_hebdo": ("Score bien-être hebdo", _job_score_bien_etre_hebdo),
    "garmin_sync_matinal": ("Sync Garmin automatique matinale", _job_garmin_sync_matinal),
    "automations_runner": ("Exécution automations", _job_automations),
    "points_famille_hebdo": ("Calcul points famille hebdo", _job_points_famille_hebdo),
    "sync_google_calendar": ("Sync Google Calendar", _job_sync_google_calendar),
    "alerte_stock_bas": ("Alerte stock bas", _job_alerte_stock_bas),
    "archive_batches_expires": ("Archivage batch expiré", _job_archive_batches_expires),
    "rapport_maison_mensuel": ("Rapport maison mensuel", _job_rapport_maison_mensuel),
    "sync_openfoodfacts": ("Sync cache OpenFoodFacts", _job_sync_openfoodfacts),
    # Phase 7 — nouveaux jobs
    "prediction_courses_weekly": ("Prédiction courses hebdo", _job_prediction_courses_weekly),
    "sync_jeux_budget": ("Sync jeux -> budget", _job_sync_jeux_budget),
    "analyse_nutrition_hebdo": ("Analyse nutrition hebdo", _job_analyse_nutrition_hebdo),
    "alertes_energie": ("Alertes énergie", _job_alertes_energie),
    "nettoyage_logs": ("Nettoyage logs > 90j", _job_nettoyage_logs),
    "check_garmin_anomalies": ("Anomalies Garmin", _job_check_garmin_anomalies),
    "resume_jardin_saisonnier": ("Résumé jardin saisonnier", _job_resume_jardin_saisonnier),
    "expiration_documents": ("Expiration documents", _job_expiration_documents),
    "sync_calendrier_scolaire": ("Sync calendrier scolaire auto", _job_sync_calendrier_scolaire),
}


def lister_jobs_disponibles() -> list[str]:
    """Retourne la liste des IDs de jobs exécutable par API admin."""
    return sorted(_REGISTRE_JOBS.keys())


def executer_job_par_id(
    job_id: str,
    *,
    dry_run: bool = False,
    source: str = "manual",
    triggered_by_user_id: str | None = None,
    relancer_exception: bool = False,
) -> dict[str, str | int | bool]:
    """Exécute un job connu avec instrumentation Phase 7."""
    if job_id not in _REGISTRE_JOBS:
        raise ValueError(f"Job inconnu: {job_id}")

    job_name, job_func = _REGISTRE_JOBS[job_id]
    return _executer_job_trace(
        job_id=job_id,
        job_name=job_name,
        fonction=job_func,
        dry_run=dry_run,
        source=source,
        triggered_by_user_id=triggered_by_user_id,
        relancer_exception=relancer_exception,
    )


# ─── Orchestrateur ────────────────────────────────────────────────────────────


def _job_sync_routines_planning() -> None:
    """IM-10: synchronise les routines actives dans le planning quotidien."""
    try:
        from datetime import date, datetime, time, timedelta

        from sqlalchemy import func

        from src.core.db import obtenir_contexte_db
        from src.core.models import EvenementPlanning, Routine, TacheRoutine

        aujourd_hui = date.today()
        nb_crees = 0
        nb_conflits = 0

        def _heure_par_defaut(moment_journee: str) -> time:
            mapping = {
                "matin": time(hour=8, minute=0),
                "midi": time(hour=12, minute=30),
                "apres_midi": time(hour=16, minute=30),
                "soir": time(hour=19, minute=0),
                "nuit": time(hour=21, minute=0),
            }
            return mapping.get((moment_journee or "").lower(), time(hour=8, minute=0))

        def _parser_heure(heure_prevue: str | None, moment_journee: str) -> time:
            if heure_prevue and ":" in heure_prevue:
                try:
                    h, m = heure_prevue.split(":", 1)
                    return time(hour=int(h), minute=int(m))
                except Exception:
                    logger.debug("Routine: heure_prevue invalide '%s'", heure_prevue)
            return _heure_par_defaut(moment_journee)

        with obtenir_contexte_db() as session:
            routines = (
                session.query(Routine)
                .filter(Routine.actif == True)  # noqa: E712
                .all()
            )

            for routine in routines:
                taches = (
                    session.query(TacheRoutine)
                    .filter(TacheRoutine.routine_id == routine.id)
                    .order_by(TacheRoutine.ordre.asc())
                    .all()
                )

                for tache in taches:
                    heure = _parser_heure(getattr(tache, "heure_prevue", None), routine.moment_journee)
                    debut = datetime.combine(aujourd_hui, heure)
                    fin = debut + timedelta(minutes=30)
                    marqueur = f"sync_routine:{tache.id}:{aujourd_hui.isoformat()}"

                    deja_sync = (
                        session.query(EvenementPlanning.id)
                        .filter(
                            EvenementPlanning.description == marqueur,
                            func.date(EvenementPlanning.date_debut) == aujourd_hui,
                        )
                        .first()
                    )
                    if deja_sync:
                        continue

                    conflit = (
                        session.query(EvenementPlanning.id)
                        .filter(
                            func.date(EvenementPlanning.date_debut) == aujourd_hui,
                            EvenementPlanning.date_debut < fin,
                            func.coalesce(EvenementPlanning.date_fin, EvenementPlanning.date_debut)
                            >= debut,
                        )
                        .first()
                    )
                    if conflit:
                        nb_conflits += 1
                        continue

                    session.add(
                        EvenementPlanning(
                            titre=f"Routine: {routine.nom} - {tache.nom}",
                            description=marqueur,
                            date_debut=debut,
                            date_fin=fin,
                            type_event="routine",
                            lieu="maison",
                            couleur="#7AA2F7",
                        )
                    )
                    nb_crees += 1

            session.commit()

        if nb_crees or nb_conflits:
            logger.info(
                "IM-10 sync routines->planning: %d événement(s) créé(s), %d conflit(s)",
                nb_crees,
                nb_conflits,
            )
    except Exception:
        logger.exception("Erreur IM-10 sync routines->planning")


def _job_sync_recoltes_inventaire() -> None:
    """IM-12: synchronise les récoltes du jardin vers l'inventaire cuisine."""
    try:
        from datetime import date, timedelta

        from sqlalchemy import func

        from src.core.db import obtenir_contexte_db
        from src.core.models import ArticleInventaire, ElementJardin, Ingredient, JournalJardin

        today = date.today()
        nb_sync = 0

        with obtenir_contexte_db() as session:
            recoltes = (
                session.query(ElementJardin)
                .filter(
                    ElementJardin.statut == "actif",
                    ElementJardin.date_recolte_prevue.isnot(None),
                    ElementJardin.date_recolte_prevue <= today,
                )
                .all()
            )

            for element in recoltes:
                deja_sync = (
                    session.query(JournalJardin.id)
                    .filter(
                        JournalJardin.garden_item_id == element.id,
                        JournalJardin.action == "sync_inventaire",
                    )
                    .first()
                )
                if deja_sync:
                    continue

                ingredient = (
                    session.query(Ingredient)
                    .filter(func.lower(Ingredient.nom) == (element.nom or "").lower())
                    .first()
                )
                if ingredient is None:
                    ingredient = Ingredient(
                        nom=element.nom,
                        categorie="jardin",
                        unite="pièce",
                    )
                    session.add(ingredient)
                    session.flush()

                article = (
                    session.query(ArticleInventaire)
                    .filter(ArticleInventaire.ingredient_id == ingredient.id)
                    .first()
                )
                if article:
                    article.quantite = float(article.quantite or 0) + 1.0
                    if not article.emplacement:
                        article.emplacement = "jardin"
                    if not article.date_peremption:
                        article.date_peremption = today + timedelta(days=5)
                else:
                    session.add(
                        ArticleInventaire(
                            ingredient_id=ingredient.id,
                            quantite=1.0,
                            quantite_min=1.0,
                            emplacement="jardin",
                            date_peremption=today + timedelta(days=5),
                        )
                    )

                session.add(
                    JournalJardin(
                        garden_item_id=element.id,
                        date=today,
                        action="sync_inventaire",
                        notes="Synchronisation automatique récolte -> inventaire",
                    )
                )
                nb_sync += 1

            session.commit()

        if nb_sync:
            logger.info("IM-12 sync récoltes->inventaire: %d récolte(s) synchronisée(s)", nb_sync)
    except Exception:
        logger.exception("Erreur IM-12 sync récoltes->inventaire")


def _job_suggestions_activites_meteo() -> None:
    """IM-14: génère des suggestions d'activités à partir de la météo et notifie la famille."""
    try:
        from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications
        from src.services.integrations.weather.service import obtenir_service_meteo

        service_meteo = obtenir_service_meteo()
        previsions = service_meteo.get_previsions(nb_jours=1)
        if not previsions:
            logger.info("IM-14: météo indisponible, suggestions non envoyées")
            return

        meteo = previsions[0]
        condition = (getattr(meteo, "condition", "") or "").lower()
        pluie = getattr(meteo, "precipitation_mm", 0) >= 5 or "pluie" in condition

        if pluie:
            suggestions = [
                "atelier peinture à la maison",
                "parcours motricité intérieur",
                "lecture interactive + musique",
            ]
        else:
            suggestions = [
                "balade au parc",
                "atelier jardinage avec récolte",
                "jeu d'eau / motricité extérieure",
            ]

        message = (
            f"Météo du jour: {getattr(meteo, 'condition', 'variable')}. "
            f"Idées activités famille: {', '.join(suggestions)}."
        )

        dispatcher = get_dispatcher_notifications()
        _envoyer_notif_tous_users(
            dispatcher,
            message=message,
            canaux=["ntfy", "push"],
            titre="Suggestions activités selon météo",
        )
        logger.info("IM-14 suggestions météo envoyées")
    except Exception:
        logger.exception("Erreur IM-14 suggestions météo")


def _job_sync_veille_habitat() -> None:
    """Synchronise la veille Habitat et pousse les meilleures alertes."""
    try:
        from src.api.utils import executer_avec_session
        from src.services.habitat import obtenir_service_veille_habitat

        with executer_avec_session() as session:
            resultat = obtenir_service_veille_habitat().synchroniser_annonces(
                session,
                user_id="matanne",
                limite_par_source=10,
                envoyer_alertes=True,
            )
        logger.info("Habitat veille sync: %s", resultat)
    except Exception:
        logger.exception("Erreur sync veille Habitat")


_REGISTRE_JOBS.update(
    {
        "sync_routines_planning": ("Sync routines -> planning", _job_sync_routines_planning),
        "sync_recoltes_inventaire": ("Sync récoltes -> inventaire", _job_sync_recoltes_inventaire),
        "suggestions_activites_meteo": ("Suggestions activités selon météo", _job_suggestions_activites_meteo),
        "sync_veille_habitat": ("Sync veille habitat", _job_sync_veille_habitat),
    }
)


class DémarreurCron:
    """Enveloppe legère autour de BackgroundScheduler pour un démarrage/arrêt propre."""

    def __init__(self) -> None:
        self._scheduler = BackgroundScheduler(
            job_defaults={"coalesce": True, "max_instances": 1},
            timezone="Europe/Paris",
        )
        self._configurer_jobs()

    def _planifier_job(self, job_id: str, trigger: CronTrigger, *, replace_existing: bool = False) -> None:
        """Planifie un job en passant systématiquement par l'instrumentation Phase 7."""
        nom = _REGISTRE_JOBS.get(job_id, (job_id, None))[0]
        self._scheduler.add_job(
            lambda _job_id=job_id: executer_job_par_id(_job_id, source="cron"),
            trigger,
            id=job_id,
            name=nom,
            replace_existing=replace_existing,
        )

    def _configurer_jobs(self) -> None:
        self._planifier_job("rappels_famille", CronTrigger(hour=7, minute=0))
        self._planifier_job("rappels_maison", CronTrigger(hour=8, minute=0))
        self._planifier_job("rappels_generaux", CronTrigger(hour=8, minute=30))
        self._planifier_job("entretien_saisonnier", CronTrigger(day_of_week="mon", hour=6, minute=0))
        self._planifier_job("push_quotidien", CronTrigger(hour=9, minute=0))
        self._planifier_job("enrichissement_catalogues", CronTrigger(day=1, hour=3, minute=0))
        self._planifier_job("digest_ntfy", CronTrigger(hour=9, minute=0), replace_existing=True)
        self._planifier_job("digest_whatsapp_matinal", CronTrigger(hour=7, minute=30), replace_existing=True)
        self._planifier_job("digest_notifications_queue", CronTrigger(hour="*/2", minute=5), replace_existing=True)
        self._planifier_job("rappel_courses", CronTrigger(hour=18, minute=0), replace_existing=True)
        self._planifier_job("push_contextuel_soir", CronTrigger(hour=18, minute=0), replace_existing=True)
        self._planifier_job("resume_hebdo", CronTrigger(day_of_week="mon", hour=7, minute=30), replace_existing=True)
        self._planifier_job("planning_semaine_si_vide", CronTrigger(day_of_week="sun", hour=20, minute=0), replace_existing=True)
        self._planifier_job("alertes_peremption_48h", CronTrigger(hour=6, minute=0), replace_existing=True)
        self._planifier_job("rapport_mensuel_budget", CronTrigger(day=1, hour=8, minute=15), replace_existing=True)
        self._planifier_job("score_weekend", CronTrigger(day_of_week="fri", hour=17, minute=0), replace_existing=True)
        self._planifier_job("controle_contrats_garanties", CronTrigger(day=1, hour=9, minute=0), replace_existing=True)
        self._planifier_job("rapport_jardin", CronTrigger(day_of_week="wed", hour=20, minute=0), replace_existing=True)
        self._planifier_job("score_bien_etre_hebdo", CronTrigger(day_of_week="sun", hour=20, minute=0), replace_existing=True)
        self._planifier_job("garmin_sync_matinal", CronTrigger(hour=6, minute=0), replace_existing=True)
        self._planifier_job("automations_runner", CronTrigger(minute="*/5"), replace_existing=True)
        self._planifier_job("points_famille_hebdo", CronTrigger(day_of_week="sun", hour=20, minute=0), replace_existing=True)
        self._planifier_job("sync_google_calendar", CronTrigger(hour=23, minute=0), replace_existing=True)
        self._planifier_job("sync_veille_habitat", CronTrigger(hour=12, minute=15), replace_existing=True)
        self._planifier_job("alerte_stock_bas", CronTrigger(hour=7, minute=0), replace_existing=True)
        self._planifier_job("archive_batches_expires", CronTrigger(hour=2, minute=0), replace_existing=True)
        self._planifier_job("rapport_maison_mensuel", CronTrigger(day=1, hour=9, minute=30), replace_existing=True)
        self._planifier_job("sync_openfoodfacts", CronTrigger(day_of_week="sun", hour=3, minute=0), replace_existing=True)

        # Phase 7 — nouveaux jobs manquants
        self._planifier_job("prediction_courses_weekly", CronTrigger(day_of_week="sun", hour=10, minute=0), replace_existing=True)
        self._planifier_job("sync_jeux_budget", CronTrigger(hour=22, minute=0), replace_existing=True)
        self._planifier_job("analyse_nutrition_hebdo", CronTrigger(day_of_week="sun", hour=20, minute=0), replace_existing=True)
        self._planifier_job("alertes_energie", CronTrigger(hour=7, minute=0), replace_existing=True)
        self._planifier_job("nettoyage_logs", CronTrigger(day_of_week="sun", hour=4, minute=0), replace_existing=True)
        self._planifier_job("check_garmin_anomalies", CronTrigger(hour=8, minute=0), replace_existing=True)
        self._planifier_job("resume_jardin_saisonnier", CronTrigger(day=1, hour=8, minute=0), replace_existing=True)
        self._planifier_job("expiration_documents", CronTrigger(hour=9, minute=0), replace_existing=True)
        self._planifier_job("sync_calendrier_scolaire", CronTrigger(hour=5, minute=30), replace_existing=True)
        self._planifier_job("sync_routines_planning", CronTrigger(hour=5, minute=45), replace_existing=True)
        self._planifier_job("sync_recoltes_inventaire", CronTrigger(hour=6, minute=15), replace_existing=True)
        self._planifier_job("suggestions_activites_meteo", CronTrigger(hour=7, minute=15), replace_existing=True)

    def demarrer(self) -> None:
        if not self._scheduler.running:
            self._scheduler.start()
            logger.info("Scheduler cron démarré (%d job(s))", len(self._scheduler.get_jobs()))

    def arreter(self) -> None:
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)
            logger.info("Scheduler cron arrêté")


# ─── Helpers module-level ─────────────────────────────────────────────────────

_demarreur: DémarreurCron | None = None


def demarrer_scheduler() -> None:
    """Initialise et démarre l'ordonnanceur global (appelé depuis le lifespan FastAPI)."""
    global _demarreur
    try:
        _demarreur = DémarreurCron()
        _demarreur.demarrer()
    except Exception:
        logger.exception("Impossible de démarrer le scheduler cron")


def arreter_scheduler() -> None:
    """Arrête proprement l'ordonnanceur (appelé depuis le lifespan FastAPI à l'arrêt)."""
    global _demarreur
    if _demarreur is not None:
        try:
            _demarreur.arreter()
        except Exception:
            logger.exception("Erreur à l'arrêt du scheduler cron")
        finally:
            _demarreur = None
