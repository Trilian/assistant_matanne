"""
Cron jobs pour le module Cuisine.

4 jobs automatisés :
1. Analyse péremptions matin : 7h00 → alerte articles expirant sous 3 jours
2. Suggestion planning semaine : Dimanche 18h → génère planning IA si aucun actif
3. Vérifier stocks bas : Lundi 9h → détecte articles sous seuil min
4. Rapport mensuel cuisine : 1er du mois 8h → synthèse consommation/gaspillage
"""

import logging
from datetime import UTC, date, datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from src.core.db import obtenir_contexte_db

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# JOB 1: ALERTES PÉREMPTION (tous les jours 7h)
# ═══════════════════════════════════════════════════════════


def analyser_peremptions_matin():
    """Détecte les articles expirant dans les 3 prochains jours et ceux déjà expirés."""
    logger.info("🔄 Analyse des péremptions inventaire")

    try:
        from src.core.models import ArticleInventaire

        with obtenir_contexte_db() as session:
            aujourd_hui = date.today()
            seuil = aujourd_hui + timedelta(days=3)

            # Articles expirant sous 3 jours
            a_risque = (
                session.query(ArticleInventaire)
                .filter(
                    ArticleInventaire.date_peremption.isnot(None),
                    ArticleInventaire.date_peremption <= seuil,
                    ArticleInventaire.quantite > 0,
                )
                .all()
            )

            expires = [a for a in a_risque if a.date_peremption and a.date_peremption <= aujourd_hui]
            bientot = [a for a in a_risque if a.date_peremption and a.date_peremption > aujourd_hui]

            if expires:
                logger.warning(
                    f"⚠️ {len(expires)} article(s) expiré(s) : "
                    f"{', '.join(a.nom for a in expires[:5])}"
                )
            if bientot:
                logger.info(
                    f"📅 {len(bientot)} article(s) expirent sous 3j : "
                    f"{', '.join(a.nom for a in bientot[:5])}"
                )

            # Bridge inter-modules : inventaire péremption -> anti-gaspi IA.
            if a_risque:
                try:
                    from src.services.core.events import obtenir_bus

                    bus = obtenir_bus()
                    for article in a_risque:
                        if not article.date_peremption:
                            continue
                        jours_restants = (article.date_peremption - aujourd_hui).days
                        bus.emettre(
                            "inventaire.peremption_proche",
                            {
                                "article_id": article.id,
                                "nom": article.nom,
                                "jours_restants": jours_restants,
                                "date_peremption": article.date_peremption.isoformat(),
                            },
                            source="cron_cuisine.peremptions",
                        )
                except Exception as exc:
                    logger.debug("Emission inventaire.peremption_proche ignorée: %s", exc)

            # Envoyer notifications push/Telegram
            if expires or bientot:
                _notifier_peremptions(expires, bientot)

            logger.info(f"✅ Analyse péremptions terminée : {len(expires)} expirés, {len(bientot)} à risque")

    except Exception as e:
        logger.error(f"❌ Erreur analyse péremptions : {e}", exc_info=True)


# ═══════════════════════════════════════════════════════════
# JOB 2: SUGGESTION PLANNING (dimanche 18h)
# ═══════════════════════════════════════════════════════════


def suggerer_planning_semaine():
    """Vérifie si un planning est actif pour la semaine prochaine. Sinon, log un rappel."""
    logger.info("🔄 Vérification planning semaine prochaine")

    try:
        from src.core.models.planning import Planning

        with obtenir_contexte_db() as session:
            aujourd_hui = date.today()
            # Semaine prochaine
            lundi_prochain = aujourd_hui + timedelta(days=(7 - aujourd_hui.weekday()))
            dimanche_prochain = lundi_prochain + timedelta(days=6)

            planning_existant = (
                session.query(Planning)
                .filter(
                    Planning.date_debut <= dimanche_prochain,
                    Planning.date_fin >= lundi_prochain,
                    Planning.statut == "actif",
                )
                .first()
            )

            if planning_existant:
                logger.info(f"✅ Planning actif trouvé pour semaine du {lundi_prochain}")
            else:
                logger.warning(
                    f"⚠️ Aucun planning actif pour la semaine du {lundi_prochain}. "
                    "Notification à envoyer."
                )
                _notifier_planning_manquant(lundi_prochain)

    except Exception as e:
        logger.error(f"❌ Erreur vérification planning : {e}", exc_info=True)


# ═══════════════════════════════════════════════════════════
# JOB 3: VÉRIFIER STOCKS BAS (lundi 9h)
# ═══════════════════════════════════════════════════════════


def verifier_stocks_bas():
    """Détecte les articles dont la quantité est inférieure au seuil minimum."""
    logger.info("🔄 Vérification des stocks bas")

    try:
        from src.core.models import ArticleInventaire

        with obtenir_contexte_db() as session:
            stocks_bas = (
                session.query(ArticleInventaire)
                .filter(ArticleInventaire.quantite <= ArticleInventaire.quantite_min)
                .all()
            )

            if stocks_bas:
                noms = ", ".join(a.nom for a in stocks_bas[:10])
                logger.warning(f"⚠️ {len(stocks_bas)} article(s) en stock bas : {noms}")
                _ajouter_stocks_bas_aux_courses(stocks_bas)
            else:
                logger.info("✅ Tous les stocks sont au-dessus du seuil minimum")

    except Exception as e:
        logger.error(f"❌ Erreur vérification stocks : {e}", exc_info=True)


# ═══════════════════════════════════════════════════════════
# HELPERS NOTIFICATIONS & AUTO-AJOUT COURSES
# ═══════════════════════════════════════════════════════════


def _notifier_peremptions(expires: list, bientot: list) -> None:
    """Envoie une notification push pour les articles expirés et expirant bientôt."""
    try:
        from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

        dispatcher = get_dispatcher_notifications()
        parties = []
        if expires:
            noms_expires = ", ".join(a.nom for a in expires[:5])
            parties.append(f"❌ {len(expires)} expiré(s) : {noms_expires}")
        if bientot:
            noms_bientot = ", ".join(a.nom for a in bientot[:5])
            parties.append(f"⚠️ {len(bientot)} expire(nt) sous 3j : {noms_bientot}")

        message = "🍽️ Alerte péremption\n" + "\n".join(parties)

        for user_id in _obtenir_user_ids():
            dispatcher.envoyer_evenement(
                user_id=user_id,
                type_evenement="peremption_j2",
                message=message,
                titre="Alerte péremption inventaire",
            )
        logger.info("📤 Notification péremption envoyée")
    except Exception as e:
        logger.error(f"❌ Erreur envoi notification péremption : {e}", exc_info=True)


def _notifier_planning_manquant(lundi_prochain: date) -> None:
    """Envoie un rappel push/Telegram pour planifier les repas de la semaine."""
    try:
        from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

        dispatcher = get_dispatcher_notifications()
        message = (
            f"📅 Aucun planning repas pour la semaine du {lundi_prochain.strftime('%d/%m')}. "
            "Pensez à planifier vos repas !"
        )

        for user_id in _obtenir_user_ids():
            dispatcher.envoyer_evenement(
                user_id=user_id,
                type_evenement="rappel_courses",
                message=message,
                titre="Rappel planning repas",
            )
        logger.info("📤 Notification planning manquant envoyée")
    except Exception as e:
        logger.error(f"❌ Erreur envoi notification planning : {e}", exc_info=True)


def _ajouter_stocks_bas_aux_courses(stocks_bas: list) -> None:
    """Ajoute automatiquement les articles en stock bas à la liste de courses active."""
    try:
        from src.services.cuisine.courses.service import obtenir_service_courses

        service = obtenir_service_courses()
        nb_ajoutes = 0

        for article in stocks_bas:
            nom = article.nom
            if not nom:
                continue
            ingredient_id = service.obtenir_ou_creer_ingredient(
                nom=nom,
                unite=article.unite or "pièce",
            )
            if ingredient_id:
                quantite = max(article.quantite_min - article.quantite, 1)
                service.create({
                    "ingredient_id": ingredient_id,
                    "quantite_necessaire": quantite,
                    "priorite": "haute",
                    "rayon_magasin": article.categorie or "Autre",
                    "notes": f"Ajout auto — stock bas ({article.quantite}/{article.quantite_min})",
                    "suggere_par_ia": False,
                })
                nb_ajoutes += 1

        if nb_ajoutes > 0:
            logger.info(f"🛒 {nb_ajoutes} article(s) ajouté(s) automatiquement aux courses")

            # Notifier l'utilisateur
            from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

            dispatcher = get_dispatcher_notifications()
            noms = ", ".join(a.nom for a in stocks_bas[:5] if a.nom)
            message = (
                f"🛒 {nb_ajoutes} article(s) en stock bas ajouté(s) aux courses : {noms}"
            )
            for user_id in _obtenir_user_ids():
                dispatcher.envoyer_evenement(
                    user_id=user_id,
                    type_evenement="rappel_courses",
                    message=message,
                    titre="Stock bas → courses",
                )

    except Exception as e:
        logger.error(f"❌ Erreur ajout auto courses : {e}", exc_info=True)


def _obtenir_user_ids() -> list[str]:
    """Récupère les identifiants des utilisateurs actifs (réutilise le helper global)."""
    import os

    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import ProfilUtilisateur

        with obtenir_contexte_db() as session:
            profils = session.query(ProfilUtilisateur.username).all()
            if profils:
                return [p.username for p in profils if p.username]
    except Exception:
        pass

    fallback = os.getenv("CRON_DEFAULT_USER_IDS", "matanne")
    return [uid.strip() for uid in fallback.split(",") if uid.strip()]


# ═══════════════════════════════════════════════════════════
# JOB 4: RAPPORT MENSUEL CUISINE (1er du mois 8h)
# ═══════════════════════════════════════════════════════════


def generer_rapport_mensuel_cuisine():
    """Génère une synthèse mensuelle : repas consommés, gaspillage, recettes favorites."""
    logger.info("🔄 Génération rapport mensuel cuisine")

    try:
        from sqlalchemy import func

        from src.core.models import Recette, Repas
        from src.core.models import ArticleInventaire
        from src.core.models.courses import HistoriqueAchats

        with obtenir_contexte_db() as session:
            aujourd_hui = date.today()
            debut_mois_prec = (aujourd_hui.replace(day=1) - timedelta(days=1)).replace(day=1)
            fin_mois_prec = aujourd_hui.replace(day=1) - timedelta(days=1)

            # Articles expirés jetés
            articles_expires = (
                session.query(func.count(ArticleInventaire.id))
                .filter(
                    ArticleInventaire.date_peremption.isnot(None),
                    ArticleInventaire.date_peremption < debut_mois_prec,
                )
                .scalar()
                or 0
            )

            logger.info(
                f"📊 Rapport cuisine {debut_mois_prec.strftime('%B %Y')} : "
                f"{articles_expires} articles expirés"
            )

    except Exception as e:
        logger.error(f"❌ Erreur rapport mensuel cuisine : {e}", exc_info=True)


# ═══════════════════════════════════════════════════════════
# CONFIGURATION DES JOBS
# ═══════════════════════════════════════════════════════════


def configurer_jobs_cuisine(scheduler: BackgroundScheduler) -> None:
    """Enregistre les 4 cron jobs cuisine dans le scheduler."""

    # Job 1: Alertes péremption — tous les jours à 7h
    scheduler.add_job(
        analyser_peremptions_matin,
        trigger=CronTrigger(hour=7, minute=0),
        id="cuisine_peremptions_matin",
        name="Cuisine: Alertes péremption (7h)",
        replace_existing=True,
    )

    # Job 2: Suggestion planning — dimanche 18h
    scheduler.add_job(
        suggerer_planning_semaine,
        trigger=CronTrigger(day_of_week="sun", hour=18, minute=0),
        id="cuisine_planning_dimanche",
        name="Cuisine: Suggestion planning (dim 18h)",
        replace_existing=True,
    )

    # Job 3: Vérifier stocks bas — lundi 9h
    scheduler.add_job(
        verifier_stocks_bas,
        trigger=CronTrigger(day_of_week="mon", hour=9, minute=0),
        id="cuisine_stocks_lundi",
        name="Cuisine: Stocks bas (lun 9h)",
        replace_existing=True,
    )

    # Job 4: Rapport mensuel — 1er du mois 8h
    scheduler.add_job(
        generer_rapport_mensuel_cuisine,
        trigger=CronTrigger(day=1, hour=8, minute=0),
        id="cuisine_rapport_mensuel",
        name="Cuisine: Rapport mensuel (1er 8h)",
        replace_existing=True,
    )

    logger.info("✅ 4 cron jobs Cuisine configurés")
