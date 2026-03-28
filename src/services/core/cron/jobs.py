"""
Jobs cron — Ordonnanceur APScheduler pour l'automatisation quotidienne.

Jobs déclarés :
- 07h00 quotidien : Rappels famille (anniversaires, documents, crèche, jalons)
- 08h00 quotidien : Rappels maison (garanties, contrats, entretien)
- 08h30 quotidien : Rappels généraux (inventaire, garanties intelligentes)
- lundi 06h00    : Entretien saisonnier (vérification tâches de saison)
"""

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


# ─── Jobs ─────────────────────────────────────────────────────────────────────


def _job_rappels_famille() -> None:
    """Évalue et envoie les rappels famille du jour (anniversaires, documents, crèche, jalons)."""
    try:
        from src.services.famille.rappels import ServiceRappelsFamille

        service = ServiceRappelsFamille()
        nb = service.envoyer_rappels_du_jour()
        logger.info("Rappels famille : %d envoyé(s)", nb)
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
        from src.services.core.rappels_intelligents import get_rappels_intelligents_service

        service = get_rappels_intelligents_service()
        rappels = service.evaluer_rappels()
        if rappels:
            logger.info("Rappels intelligents : %d rappel(s) actif(s)", len(rappels))
        else:
            logger.debug("Rappels intelligents : aucun rappel actif")
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
        nb_abonnes = len(abonnes_db) if abonnes_db else sum(
            len(subs) for subs in push_service._subscriptions.values()
        )

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
                    user_ids = {str(a.user_id) for a in abonnes_db if a.user_id} or set(
                        push_service._subscriptions.keys()
                    )
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


def _job_rappel_courses_ntfy() -> None:
    """Envoie un rappel ntfy.sh pour les articles de courses en attente à 18h."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models.courses import LisCourse  # noqa: F401 — import for query

        nb_articles = 0
        try:
            with obtenir_contexte_db() as session:
                # Compter les articles non achetés dans les listes actives
                from sqlalchemy import text
                result = session.execute(
                    text(
                        "SELECT COUNT(*) FROM liste_courses lc"
                        " JOIN listes_courses ls ON ls.id = lc.liste_id"
                        " WHERE lc.achete = FALSE AND ls.statut IN ('active', 'en_cours')"
                    )
                )
                nb_articles = result.scalar() or 0
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
        resultats = dispatcher.envoyer(
            user_id="matanne",
            message=message,
            canaux=["ntfy", "push"],
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
        # ntfy toujours tenté; email seulement si adresse fournie en env
        canaux = ["ntfy", "email"]
        import os

        email_dest = os.getenv("EMAIL_RESUME_HEBDO")
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
        }
        if email_dest:
            kwargs["email"] = email_dest
        else:
            canaux = ["ntfy"]

        resultats = dispatcher.envoyer(
            user_id="matanne",
            message=texte,
            canaux=canaux,
            **kwargs,
        )
        logger.info("Résumé hebdo envoyé: %s", resultats)
    except Exception:
        logger.exception("Erreur lors du résumé hebdomadaire")


# ─── Orchestrateur ────────────────────────────────────────────────────────────


class DémarreurCron:
    """Enveloppe legère autour de BackgroundScheduler pour un démarrage/arrêt propre."""

    def __init__(self) -> None:
        self._scheduler = BackgroundScheduler(
            job_defaults={"coalesce": True, "max_instances": 1},
            timezone="Europe/Paris",
        )
        self._configurer_jobs()

    def _configurer_jobs(self) -> None:
        self._scheduler.add_job(
            _job_rappels_famille,
            CronTrigger(hour=7, minute=0),
            id="rappels_famille",
            name="Rappels famille quotidiens",
        )
        self._scheduler.add_job(
            _job_rappels_maison,
            CronTrigger(hour=8, minute=0),
            id="rappels_maison",
            name="Rappels maison quotidiens",
        )
        self._scheduler.add_job(
            _job_rappels_generaux,
            CronTrigger(hour=8, minute=30),
            id="rappels_generaux",
            name="Rappels intelligents quotidiens",
        )
        self._scheduler.add_job(
            _job_entretien_saisonnier,
            CronTrigger(day_of_week="mon", hour=6, minute=0),
            id="entretien_saisonnier",
            name="Entretien saisonnier hebdomadaire",
        )
        self._scheduler.add_job(
            _job_push_quotidien,
            CronTrigger(hour=9, minute=0),
            id="push_quotidien",
            name="Notifications Web Push quotidiennes (alertes urgentes)",
        )
        self._scheduler.add_job(
            _job_enrichissement_catalogues,
            CronTrigger(day=1, hour=3, minute=0),
            id="enrichissement_catalogues",
            name="Enrichissement mensuel catalogues IA",
        )
        self._scheduler.add_job(
            _job_digest_ntfy,
            CronTrigger(hour=9, minute=0),
            id="digest_ntfy",
            replace_existing=True,
            name="Digest quotidien ntfy.sh (tâches + rappels)",
        )
        self._scheduler.add_job(
            _job_rappel_courses_ntfy,
            CronTrigger(hour=18, minute=0),
            id="rappel_courses",
            replace_existing=True,
            name="Rappel courses ntfy.sh (articles en attente)",
        )
        self._scheduler.add_job(
            _job_push_contextuel_soir,
            CronTrigger(hour=18, minute=0),
            id="push_contextuel_soir",
            replace_existing=True,
            name="Push contextuel soir (planning + météo)",
        )
        self._scheduler.add_job(
            _job_resume_hebdo,
            CronTrigger(day_of_week="mon", hour=7, minute=30),
            id="resume_hebdo",
            replace_existing=True,
            name="Résumé hebdomadaire (lundi 07h30)",
        )

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
