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
from sqlalchemy import func

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


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
            dispatcher.envoyer(
                user_id="matanne",
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
            dispatcher.envoyer(
                user_id="matanne",
                message=f"{nb_articles} article(s) en attente sur la liste.",
                canaux=["whatsapp"],
                type_whatsapp="liste_courses",
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
        # ntfy toujours tenté; email et whatsapp si configurés
        canaux = ["ntfy", "email", "whatsapp"]
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
            canaux = ["ntfy", "whatsapp"]

        # Canal WhatsApp: résumé compact dédié.
        kwargs["type_whatsapp"] = "rapport_hebdo"

        resultats = dispatcher.envoyer(
            user_id="matanne",
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
        res = dispatcher.envoyer(
            user_id="matanne",
            message=message,
            canaux=["ntfy", "whatsapp"],
            titre="Planning semaine à générer",
        )
        logger.info("J-03 exécuté: %s", res)
    except Exception:
        logger.exception("Erreur job J-03")


def _job_alertes_peremption_48h() -> None:
    """J-04: envoie les alertes de péremption à J+48h."""
    try:
        from datetime import date, timedelta

        from src.core.db import obtenir_contexte_db
        from src.core.models import ArticleInventaire
        from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

        aujourd_hui = date.today()
        seuil = aujourd_hui + timedelta(days=2)

        with obtenir_contexte_db() as session:
            articles = (
                session.query(ArticleInventaire)
                .filter(
                    ArticleInventaire.date_peremption.isnot(None),
                    ArticleInventaire.date_peremption >= aujourd_hui,
                    ArticleInventaire.date_peremption <= seuil,
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

        dispatcher = get_dispatcher_notifications()
        res = dispatcher.envoyer(
            user_id="matanne",
            message=message,
            canaux=["ntfy", "whatsapp"],
            titre="Alerte péremption 48h",
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
        res = dispatcher.envoyer(
            user_id="matanne",
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
        res = dispatcher.envoyer(
            user_id="matanne",
            message=message,
            canaux=["ntfy", "whatsapp"],
            titre="Score weekend",
        )
        logger.info("J-08 exécuté: %s", res)
    except Exception:
        logger.exception("Erreur job J-08")


def _job_controle_contrats_garanties() -> None:
    """J-09: contrôle des contrats/garanties expirant dans 3 mois."""
    try:
        from datetime import date, timedelta

        from src.core.db import obtenir_contexte_db
        from src.core.models import Contrat, Garantie
        from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

        aujourd_hui = date.today()
        horizon = aujourd_hui + timedelta(days=90)

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
        dispatcher = get_dispatcher_notifications()
        res = dispatcher.envoyer(
            user_id="matanne",
            message=message,
            canaux=["ntfy", "whatsapp"],
            titre="Contrats & garanties à surveiller",
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
        res = dispatcher.envoyer(
            user_id="matanne",
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
        res = dispatcher.envoyer(
            user_id="matanne",
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
        self._scheduler.add_job(
            _job_planning_semaine_si_vide,
            CronTrigger(day_of_week="sun", hour=20, minute=0),
            id="planning_semaine_si_vide",
            replace_existing=True,
            name="J-03 Vérification planning semaine suivante",
        )
        self._scheduler.add_job(
            _job_alertes_peremption_48h,
            CronTrigger(hour=6, minute=0),
            id="alertes_peremption_48h",
            replace_existing=True,
            name="J-04 Alertes péremption 48h",
        )
        self._scheduler.add_job(
            _job_rapport_mensuel_budget,
            CronTrigger(day=1, hour=8, minute=15),
            id="rapport_mensuel_budget",
            replace_existing=True,
            name="J-07 Rapport mensuel budget",
        )
        self._scheduler.add_job(
            _job_score_weekend,
            CronTrigger(day_of_week="fri", hour=17, minute=0),
            id="score_weekend",
            replace_existing=True,
            name="J-08 Score weekend",
        )
        self._scheduler.add_job(
            _job_controle_contrats_garanties,
            CronTrigger(day=1, hour=9, minute=0),
            id="controle_contrats_garanties",
            replace_existing=True,
            name="J-09 Contrats et garanties",
        )
        self._scheduler.add_job(
            _job_rapport_jardin,
            CronTrigger(day_of_week="wed", hour=20, minute=0),
            id="rapport_jardin",
            replace_existing=True,
            name="J-10 Rapport jardin hebdo",
        )
        self._scheduler.add_job(
            _job_score_bien_etre_hebdo,
            CronTrigger(day_of_week="sun", hour=20, minute=0),
            id="score_bien_etre_hebdo",
            replace_existing=True,
            name="J-11 Score bien-être hebdo",
        )
        self._scheduler.add_job(
            _job_garmin_sync_matinal,
            CronTrigger(hour=6, minute=0),
            id="garmin_sync_matinal",
            replace_existing=True,
            name="Sync Garmin automatique matinale",
        )
        self._scheduler.add_job(
            _job_automations,
            CronTrigger(minute="*/5"),
            id="automations_runner",
            replace_existing=True,
            name="Exécution des automations (toutes les 5 min)",
        )
        self._scheduler.add_job(
            _job_points_famille_hebdo,
            CronTrigger(day_of_week="sun", hour=20, minute=0),
            id="points_famille_hebdo",
            replace_existing=True,
            name="Calcul points famille hebdomadaire",
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
