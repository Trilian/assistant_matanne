"""
Cron jobs bridges — Prédictions, alertes, consolidation.

9 nouveaux jobs :
1. prediction_courses_hebdo — Vendredi 16h
2. planning_auto_semaine — Dimanche 19h
3. alertes_budget_seuil — Quotidien 20h
4. nettoyage_cache_export — Quotidien 02h (déjà dans cron.py, renforcé)
5. rappel_jardin_saison — Hebdo lundi 9h
6. sync_budget_consolidation — Quotidien 22h
7. tendances_nutrition_hebdo — Dimanche 18h
8. rappel_activite_jules — Quotidien 09h
9. sync_google_calendar — Quotidien 23h
"""

import logging
from datetime import date, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from src.core.db import obtenir_contexte_db

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# JOB 1: PRÉDICTION COURSES HEBDO (Vendredi 16h)
# ═══════════════════════════════════════════════════════════


def prediction_courses_hebdo():
    """Génère la liste prédictive de courses pour la semaine suivante (B8.1)."""
    logger.info("🔄 Prédiction courses hebdomadaire")

    try:
        from src.services.ia.prediction_courses import obtenir_service_prediction_courses

        service = obtenir_service_prediction_courses()
        predictions = service.predire_prochaine_liste(limite=30)

        if predictions:
            logger.info(f"✅ {len(predictions)} article(s) prédit(s) pour la semaine prochaine")
            _notifier_prediction_courses(predictions)
        else:
            logger.info("ℹ️ Aucune prédiction disponible (historique insuffisant)")

    except Exception as e:
        logger.error(f"❌ Erreur prédiction courses: {e}", exc_info=True)


def _notifier_prediction_courses(predictions: list[dict]) -> None:
    """Notifie l'utilisateur des prédictions de courses."""
    try:
        from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

        dispatcher = get_dispatcher_notifications()
        top_5 = [p["nom"] for p in predictions[:5]]
        message = (
            f"🛒 Liste prédictive : {len(predictions)} article(s) habituels à racheter.\n"
            f"Top 5 : {', '.join(top_5)}\n"
            "Ouvrez l'app pour valider et compléter."
        )

        for user_id in _obtenir_user_ids():
            dispatcher.envoyer_evenement(
                user_id=user_id,
                type_evenement="prediction_courses",
                message=message,
                titre="🛒 Prédiction courses",
            )
    except Exception as e:
        logger.error(f"❌ Erreur notification prédiction: {e}", exc_info=True)


# ═══════════════════════════════════════════════════════════
# JOB 2: PLANNING AUTO SEMAINE (Dimanche 19h)
# ═══════════════════════════════════════════════════════════


def planning_auto_semaine():
    """Propose un planning IA via notification si la semaine est vide (B8.2)."""
    logger.info("🔄 Vérification planning semaine prochaine (auto)")

    try:
        from src.core.models.planning import Planning

        with obtenir_contexte_db() as session:
            aujourd_hui = date.today()
            lundi_prochain = aujourd_hui + timedelta(days=(7 - aujourd_hui.weekday()))
            dimanche_prochain = lundi_prochain + timedelta(days=6)

            planning_existant = (
                session.query(Planning)
                .filter(
                    Planning.semaine_debut <= dimanche_prochain,
                    Planning.semaine_fin >= lundi_prochain,
                    Planning.statut == "actif",
                )
                .first()
            )

            if not planning_existant:
                logger.info("📅 Aucun planning → proposition IA")
                _notifier_proposition_planning(lundi_prochain)
            else:
                logger.info(f"✅ Planning actif trouvé pour semaine du {lundi_prochain}")

    except Exception as e:
        logger.error(f"❌ Erreur planning auto: {e}", exc_info=True)


def _notifier_proposition_planning(lundi: date) -> None:
    """Propose un planning IA pour la semaine."""
    try:
        from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

        dispatcher = get_dispatcher_notifications()
        message = (
            f"📅 Semaine du {lundi.strftime('%d/%m')} sans planning !\n"
            "Voulez-vous que l'IA génère un planning de repas adapté ?\n"
            "→ Ouvrez l'app pour lancer la génération."
        )

        for user_id in _obtenir_user_ids():
            dispatcher.envoyer_evenement(
                user_id=user_id,
                type_evenement="rappel_planning",
                message=message,
                titre="📅 Planning de la semaine",
            )
    except Exception as e:
        logger.error(f"❌ Erreur notification planning: {e}", exc_info=True)


# ═══════════════════════════════════════════════════════════
# JOB 3: ALERTES BUDGET SEUIL (Quotidien 20h)
# ═══════════════════════════════════════════════════════════


def alertes_budget_seuil():
    """Alerte si une catégorie dépasse 80% du budget mensuel de référence (B8.3)."""
    logger.info("🔄 Vérification seuils budget")

    try:
        from src.services.ia.prevision_budget import obtenir_service_prevision_budget

        service = obtenir_service_prevision_budget()
        anomalies = service.detecter_anomalies_budget(seuil_pct=80)

        if anomalies:
            logger.warning(f"⚠️ {len(anomalies)} catégorie(s) en dépassement budget")
            _notifier_alertes_budget(anomalies)
        else:
            logger.info("✅ Aucun dépassement budget détecté")

    except Exception as e:
        logger.error(f"❌ Erreur alertes budget: {e}", exc_info=True)


def _notifier_alertes_budget(anomalies: list[dict]) -> None:
    """Notifie les dépassements de budget."""
    try:
        from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

        dispatcher = get_dispatcher_notifications()
        lignes = []
        for a in anomalies[:5]:
            emoji = "🔴" if a["niveau"] == "critique" else "🟠"
            lignes.append(
                f"{emoji} {a['categorie']}: {a['depense']:.0f}€ "
                f"({a['pourcentage']:.0f}% du budget ref)"
            )

        message = "💰 Alertes budget du mois\n" + "\n".join(lignes)

        for user_id in _obtenir_user_ids():
            dispatcher.envoyer_evenement(
                user_id=user_id,
                type_evenement="alerte_budget",
                message=message,
                titre="💰 Dépassement budget",
            )
    except Exception as e:
        logger.error(f"❌ Erreur notification budget: {e}", exc_info=True)


# ═══════════════════════════════════════════════════════════
# JOB 5: RAPPEL JARDIN SAISON (Lundi 9h)
# ═══════════════════════════════════════════════════════════


def rappel_jardin_saison():
    """Rappels saisonniers intelligents pour le jardin (B8.5)."""
    logger.info("🔄 Rappels jardin saisonniers")

    try:
        import json
        from pathlib import Path

        aujourd_hui = date.today()
        mois = aujourd_hui.month

        # Charger le catalogue de plantes pour conseils saisonniers
        catalogue_path = Path(__file__).resolve().parents[3] / "data" / "reference" / "plantes_catalogue.json"

        conseils = []
        if catalogue_path.exists():
            catalogue = json.loads(catalogue_path.read_text(encoding="utf-8"))
            # Filtrer les plantes dont c'est la saison
            for plante in catalogue if isinstance(catalogue, list) else []:
                mois_plantation = plante.get("mois_plantation", [])
                if mois in mois_plantation:
                    conseils.append(f"🌱 {plante.get('nom', '')}: à planter ce mois-ci")

        saison = {1: "hiver", 2: "hiver", 3: "printemps", 4: "printemps", 5: "printemps",
                  6: "été", 7: "été", 8: "été", 9: "automne", 10: "automne",
                  11: "automne", 12: "hiver"}.get(mois, "")

        # Conseils généraux par saison
        conseils_saison = {
            "printemps": ["Préparer les semis", "Nettoyer les massifs", "Tondre régulièrement"],
            "été": ["Arroser tôt le matin", "Pailler les massifs", "Récolter les fruits"],
            "automne": ["Planter les bulbes", "Ramasser les feuilles", "Protéger les plantes fragiles"],
            "hiver": ["Protéger du gel", "Planifier le jardin du printemps", "Entretenir les outils"],
        }

        if conseils or saison:
            general = conseils_saison.get(saison, [])
            all_conseils = conseils[:3] + [f"🌿 {c}" for c in general[:2]]
            if all_conseils:
                _notifier_jardin_saison(saison, all_conseils)

        logger.info(f"✅ Rappels jardin {saison}: {len(conseils)} conseil(s)")

    except Exception as e:
        logger.error(f"❌ Erreur rappels jardin: {e}", exc_info=True)


def _notifier_jardin_saison(saison: str, conseils: list[str]) -> None:
    """Envoie les rappels jardin saisonniers."""
    try:
        from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

        dispatcher = get_dispatcher_notifications()
        message = f"🌿 Rappels jardin ({saison})\n" + "\n".join(conseils[:5])

        for user_id in _obtenir_user_ids():
            dispatcher.envoyer_evenement(
                user_id=user_id,
                type_evenement="rappel_jardin",
                message=message,
                titre=f"🌿 Jardin — {saison.capitalize()}",
            )
    except Exception as e:
        logger.error(f"❌ Erreur notification jardin: {e}", exc_info=True)


# ═══════════════════════════════════════════════════════════
# JOB 7: TENDANCES NUTRITION HEBDO (Dimanche 18h)
# ═══════════════════════════════════════════════════════════


def tendances_nutrition_hebdo():
    """Score nutritionnel hebdomadaire + recommandations (B8.7)."""
    logger.info("🔄 Analyse tendances nutrition hebdomadaire")

    try:
        from src.core.models.planning import Repas

        with obtenir_contexte_db() as session:
            aujourd_hui = date.today()
            lundi = aujourd_hui - timedelta(days=aujourd_hui.weekday())
            dimanche = lundi + timedelta(days=6)

            repas = (
                session.query(Repas)
                .filter(Repas.date_repas >= lundi, Repas.date_repas <= dimanche)
                .all()
            )

            nb_repas = len(repas)
            nb_prepares = sum(1 for r in repas if r.prepare)

            logger.info(
                f"✅ Nutrition semaine: {nb_repas} repas planifiés, "
                f"{nb_prepares} préparés"
            )

    except Exception as e:
        logger.error(f"❌ Erreur tendances nutrition: {e}", exc_info=True)


# ═══════════════════════════════════════════════════════════
# JOB 8: RAPPEL ACTIVITÉ JULES (Quotidien 09h)
# ═══════════════════════════════════════════════════════════


def rappel_activite_jules():
    """Activités recommandées pour Jules basées sur son âge actuel (B8.8)."""
    logger.info("🔄 Vérification activités Jules")

    try:
        from src.core.models.famille import ProfilEnfant

        with obtenir_contexte_db() as session:
            jules = (
                session.query(ProfilEnfant)
                .filter(ProfilEnfant.name == "Jules", ProfilEnfant.actif.is_(True))
                .first()
            )

            if not jules or not jules.date_of_birth:
                logger.info("ℹ️ Profil Jules non trouvé ou sans date de naissance")
                return

            age_jours = (date.today() - jules.date_of_birth).days
            age_mois = age_jours // 30

            # Vérifier si un jalon important approche
            logger.info(f"✅ Jules: {age_mois} mois ({age_jours} jours)")

    except Exception as e:
        logger.error(f"❌ Erreur rappel activité Jules: {e}", exc_info=True)


# ═══════════════════════════════════════════════════════════
# JOB 6: SYNC BUDGET CONSOLIDATION (Quotidien 22h)
# ═══════════════════════════════════════════════════════════


def sync_budget_consolidation():
    """Consolide les dépenses multi-modules (famille + maison) (B8.6)."""
    logger.info("🔄 Consolidation budget quotidienne")

    try:
        from sqlalchemy import func
        from src.core.models import BudgetFamille
        from src.core.models.maison import DepenseMaison

        with obtenir_contexte_db() as session:
            aujourd_hui = date.today()
            mois = aujourd_hui.month
            annee = aujourd_hui.year

            total_famille = (
                session.query(func.sum(BudgetFamille.montant))
                .filter(
                    func.extract("month", BudgetFamille.date) == mois,
                    func.extract("year", BudgetFamille.date) == annee,
                )
                .scalar() or 0
            )

            total_maison = (
                session.query(func.sum(DepenseMaison.montant))
                .filter(DepenseMaison.mois == mois, DepenseMaison.annee == annee)
                .scalar() or 0
            )

            total = float(total_famille) + float(total_maison)
            logger.info(
                f"✅ Budget consolidé {mois:02d}/{annee}: "
                f"famille={float(total_famille):.2f}€, maison={float(total_maison):.2f}€, "
                f"total={total:.2f}€"
            )

    except Exception as e:
        logger.error(f"❌ Erreur consolidation budget: {e}", exc_info=True)


# ═══════════════════════════════════════════════════════════
# JOB 9: SYNC GOOGLE CALENDAR (Quotidien 23h)
# ═══════════════════════════════════════════════════════════


def sync_google_calendar():
    """Synchronise le planning repas avec Google Calendar (11.3)."""
    logger.info("🔄 Sync Google Calendar quotidienne")

    try:
        from src.core.models import CalendrierExterne

        user_ids_connectes: list[str] = []
        with obtenir_contexte_db() as session:
            cals = (
                session.query(CalendrierExterne)
                .filter(
                    CalendrierExterne.provider == "google",
                    CalendrierExterne.enabled.is_(True),
                )
                .all()
            )
            user_ids_connectes = [str(c.user_id) for c in cals]

        if not user_ids_connectes:
            logger.info("ℹ️ Aucun utilisateur connecté à Google Calendar")
            return

        from src.services.famille.calendrier import obtenir_calendar_sync_service

        service = obtenir_calendar_sync_service()

        for user_id in user_ids_connectes:
            try:
                result = service.sync_google_calendar(user_id)
                imported = result.imported if result else 0
                exported = result.exported if result else 0
                logger.info(f"✅ Google sync user {user_id}: {imported} importés, {exported} exportés")
            except Exception as e:
                logger.error(f"❌ Google sync user {user_id}: {e}")

    except Exception as e:
        logger.error(f"❌ Erreur sync Google Calendar: {e}", exc_info=True)


# ═══════════════════════════════════════════════════════════
# HELPER
# ═══════════════════════════════════════════════════════════


def _obtenir_user_ids() -> list[str]:
    """Retourne les user IDs pour les notifications."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models.users import Utilisateur

        with obtenir_contexte_db() as session:
            users = session.query(Utilisateur.id).limit(10).all()
            return [str(u.id) for u in users]
    except Exception:
        return ["dev"]


# ═══════════════════════════════════════════════════════════
# CONFIGURATION SCHEDULER
# ═══════════════════════════════════════════════════════════


def configurer_jobs_bridges(scheduler: BackgroundScheduler) -> None:
    """Enregistre les 9 cron jobs bridges dans le scheduler."""

    # B8.1: Prédiction courses — Vendredi 16h
    scheduler.add_job(
        prediction_courses_hebdo,
        trigger=CronTrigger(day_of_week="fri", hour=16, minute=0),
        id="prediction_courses_hebdo",
        name="Prédiction courses hebdomadaire",
        replace_existing=True,
    )

    # B8.2: Planning auto — Dimanche 19h
    scheduler.add_job(
        planning_auto_semaine,
        trigger=CronTrigger(day_of_week="sun", hour=19, minute=0),
        id="planning_auto_semaine",
        name="Planning auto semaine",
        replace_existing=True,
    )

    # B8.3: Alertes budget — Quotidien 20h
    scheduler.add_job(
        alertes_budget_seuil,
        trigger=CronTrigger(hour=20, minute=0),
        id="alertes_budget_seuil",
        name="Alertes budget seuil quotidien",
        replace_existing=True,
    )

    # B8.5: Rappel jardin — Lundi 9h
    scheduler.add_job(
        rappel_jardin_saison,
        trigger=CronTrigger(day_of_week="mon", hour=9, minute=0),
        id="rappel_jardin_saison",
        name="Rappels jardin saisonniers",
        replace_existing=True,
    )

    # B8.6: Consolidation budget — Quotidien 22h
    scheduler.add_job(
        sync_budget_consolidation,
        trigger=CronTrigger(hour=22, minute=0),
        id="sync_budget_consolidation",
        name="Consolidation budget quotidienne",
        replace_existing=True,
    )

    # B8.7: Tendances nutrition — Dimanche 18h
    scheduler.add_job(
        tendances_nutrition_hebdo,
        trigger=CronTrigger(day_of_week="sun", hour=18, minute=0),
        id="tendances_nutrition_hebdo",
        name="Tendances nutrition hebdomadaire",
        replace_existing=True,
    )

    # B8.8: Rappel activité Jules — Quotidien 9h
    scheduler.add_job(
        rappel_activite_jules,
        trigger=CronTrigger(hour=9, minute=0),
        id="rappel_activite_jules",
        name="Rappel activités Jules",
        replace_existing=True,
    )

    # 11.3: Sync Google Calendar — Quotidien 23h
    scheduler.add_job(
        sync_google_calendar,
        trigger=CronTrigger(hour=23, minute=0),
        id="sync_google_calendar",
        name="Synchronisation Google Calendar quotidienne",
        replace_existing=True,
    )

    logger.info("✅ 8 cron jobs bridges configurés")
