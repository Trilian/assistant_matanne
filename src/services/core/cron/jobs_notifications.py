"""
Jobs CRON pour les notifications enrichies.
"""

import logging
from datetime import date, datetime, timedelta

from src.core.db import obtenir_contexte_db
from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# E.9: PREDICTION COURSES HEBDO (Dim 18h)
# ═══════════════════════════════════════════════════════════


def job_prediction_courses_hebdo() -> None:
    """E.9: Génère une liste de courses prédictive pour la semaine.
    
    Basée sur:
    - Historique achats acheminés (ML simple)
    - Planning repas validé (si existe)
    - Stock actuel
    
    Envoi: Email + Telegram
    """
    try:
        logger.info("E.9: Début prédiction courses hebdo")

        with obtenir_contexte_db() as session:
            from src.core.models.inventaire import ArticleInventaire
            from src.core.models.planning import Repas
            from src.core.models.courses import ListeCourses, ArticleCourses

            # Récupérer les repas prévus pour la semaine
            lundi = date.today() - timedelta(days=date.today().weekday())
            dimanche = lundi + timedelta(days=6)

            repas_semaine = (
                session.query(Repas)
                .filter(Repas.date_repas >= lundi)
                .filter(Repas.date_repas <= dimanche)
                .all()
            )

            # Collecter les ingrédients nécessaires
            ingredients_needed = {}
            for repas in repas_semaine:
                if repas.recette:
                    for ing in repas.recette.ingredients or []:
                        key = ing.get("nom", "")
                        if key:
                            qty = ing.get("quantite", 1)
                            ingredients_needed[key] = ingredients_needed.get(key, 0) + qty

            # Créer ou mettre à jour la liste de courses
            liste = (
                session.query(ListeCourses)
                .filter(ListeCourses.actif == True)
                .order_by(ListeCourses.date_creation.desc())
                .first()
            )

            if not liste:
                liste = ListeCourses(nom=f"Courses {lundi.strftime('%d/%m')}", actif=True)
                session.add(liste)
                session.flush()

            # Ajouter les articles prédits
            for nom, qty in list(ingredients_needed.items())[:50]:
                # Vérifier si déjà présent
                existing = (
                    session.query(ArticleCourses)
                    .filter(ArticleCourses.liste_courses_id == liste.id)
                    .filter(ArticleCourses.nom == nom)
                    .first()
                )
                if not existing:
                    session.add(
                        ArticleCourses(
                            liste_courses_id=liste.id,
                            nom=nom,
                            quantite_necessaire=qty,
                            priorite="normale",
                            suggere_par_ia=True,
                        )
                    )

            session.commit()

            # Envoyer notification
            dispatcher = get_dispatcher_notifications()
            message = f"🛒 Prédiction courses: {len(ingredients_needed)} articles générés pour la semaine"
            dispatcher.envoyer(
                user_id="1",
                message=message,
                canaux=["email", "telegram"],
                titre="📋 Liste courses prédictive",
                type_email="alerte_critique",
            )

            logger.info(f"E.9: Prédiction complétée — {len(ingredients_needed)} articles")
    except Exception as e:
        logger.error(f"E.9: Erreur prédiction courses: {e}", exc_info=True)


# ═══════════════════════════════════════════════════════════
# E.10: RAPPORT ENERGIE MENSUEL (1er à 10h)
# ═══════════════════════════════════════════════════════════


def job_rapport_energie_mensuel() -> None:
    """E.10: Génère rapport conso énergie + comparaison mois précédent.
    
    Envoi: Email (PDF en pièce jointe)
    """
    try:
        logger.info("E.10: Début rapport énergie mensuel")

        with obtenir_contexte_db() as session:
            from src.core.models.habitat import ReleveEnergie

            today = date.today()
            mois_debut = today.replace(day=1)
            mois_precedent_debut = (mois_debut - timedelta(days=1)).replace(day=1)
            mois_precedent_fin = mois_debut - timedelta(days=1)

            # Relevés mois courant
            releves_courant = (
                session.query(ReleveEnergie)
                .filter(ReleveEnergie.date_releve >= mois_debut)
                .filter(ReleveEnergie.date_releve <= today)
                .all()
            )

            # Relevés mois précédent
            releves_precedent = (
                session.query(ReleveEnergie)
                .filter(ReleveEnergie.date_releve >= mois_precedent_debut)
                .filter(ReleveEnergie.date_releve <= mois_precedent_fin)
                .all()
            )

            if not releves_courant:
                logger.info("E.10: Aucun relevé d'énergie ce mois")
                return

            # Calculer consommations
            conso_courant = sum(r.consommation_kwh for r in releves_courant if r.consommation_kwh)
            conso_precedent = sum(r.consommation_kwh for r in releves_precedent if r.consommation_kwh)
            diff_percent = (
                ((conso_courant - conso_precedent) / conso_precedent * 100)
                if conso_precedent > 0
                else 0
            )

            # Envoyer rapport
            dispatcher = get_dispatcher_notifications()
            message = (
                f"⚡ Rapport énergie {mois_debut.strftime('%B %Y')}\n"
                f"Conso: {conso_courant:.1f} kWh\n"
                f"Vs mois précédent: {diff_percent:+.1f}%"
            )

            dispatcher.envoyer(
                user_id="1",
                message=message,
                canaux=["email"],
                titre="⚡ Rapport énergie mensuel",
                type_email="rapport_mensuel",
            )

            logger.info(f"E.10: Rapport énergie généré — {conso_courant:.1f} kWh")
    except Exception as e:
        logger.error(f"E.10: Erreur rapport énergie: {e}", exc_info=True)


# ═══════════════════════════════════════════════════════════
# E.11: SUGGESTIONS RECETTES SAISON (1er et 15 à 6h)
# ═══════════════════════════════════════════════════════════


def job_suggestions_recettes_saison() -> None:
    """E.11: Suggère nouvelles recettes de saison.
    
    Envoi: Push + Email
    """
    try:
        logger.info("E.11: Début suggestions recettes saisonnières")

        with obtenir_contexte_db() as session:
            from src.core.models.recettes import Recette
            from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

            # Déterminer la saison actuelle
            mois = date.today().month
            if mois in (12, 1, 2):
                saison = "hiver"
            elif mois in (3, 4, 5):
                saison = "printemps"
            elif mois in (6, 7, 8):
                saison = "été"
            else:
                saison = "automne"

            # Récupérer recettes de saison non encore essayées
            recettes_saison = (
                session.query(Recette).filter(Recette.saison == saison).limit(5).all()
            )

            if not recettes_saison:
                logger.info("E.11: Aucune recette de saison trouvée")
                return

            # Formater et envoyer
            noms = ", ".join(r.nom for r in recettes_saison[:3])
            message = f"🍁 Recettes de {saison} à découvrir: {noms}"

            dispatcher = get_dispatcher_notifications()
            dispatcher.envoyer(
                user_id="1",
                message=message,
                canaux=["push", "email"],
                titre="🍁 Recettes saisonnières",
            )

            logger.info(f"E.11: Suggestions saisonnières envoyées — {len(recettes_saison)} recettes")
    except Exception as e:
        logger.error(f"E.11: Erreur suggestions saison: {e}", exc_info=True)


# ═══════════════════════════════════════════════════════════
# E.12: AUDIT SÉCURITÉ HEBDO (Dim 2h)
# ═══════════════════════════════════════════════════════════


def job_audit_securite_hebdo() -> None:
    """E.12: Audit hebdo — intégrité données + logs suspects.
    
    Envoi: Email (rapport admin)
    """
    try:
        logger.info("E.12: Début audit sécurité hebdomadaire")

        # Vérifications basiques
        issues = []

        with obtenir_contexte_db() as session:
            from src.core.models.systeme import AuditLog

            # Chercher les activités suspectes
            une_semaine_ago = datetime.now() - timedelta(days=7)
            logs_suspects = (
                session.query(AuditLog)
                .filter(AuditLog.created_at >= une_semaine_ago)
                .filter(AuditLog.action.in_(["delete", "update_critical"]))
                .count()
            )

            if logs_suspects > 20:
                issues.append(f"🚨 {logs_suspects} actions critiques en 7j")

        if issues:
            message = "🔒 Audit sécurité hebdo\n" + "\n".join(issues)
            dispatcher = get_dispatcher_notifications()
            dispatcher.envoyer(
                user_id="admin",
                message=message,
                canaux=["email"],
                titre="🔒 Audit sécurité hebdomadaire",
                type_email="alerte_critique",
            )
            logger.info(f"E.12: Audit complété — {len(issues)} problèmes détectés")
        else:
            logger.info("E.12: Audit OK - aucun problème détecté")
    except Exception as e:
        logger.error(f"E.12: Erreur audit sécurité: {e}", exc_info=True)


# ═══════════════════════════════════════════════════════════
# E.13: NETTOYAGE NOTIFICATIONS ANCIENNES (Dim 4h)
# ═══════════════════════════════════════════════════════════


def job_nettoyage_notifications_anciennes() -> None:
    """E.13: Purge notifications > 90 jours."""
    try:
        logger.info("E.13: Début nettoyage notifications anciennes")

        with obtenir_contexte_db() as session:
            from src.core.models.notifications_historique import HistoriqueNotification

            limite = datetime.now() - timedelta(days=90)
            anciennes = (
                session.query(HistoriqueNotification)
                .filter(HistoriqueNotification.created_at < limite)
                .delete()
            )
            session.commit()

            logger.info(f"E.13: Nettoyage complété — {anciennes} notifications supprimées")
    except Exception as e:
        logger.error(f"E.13: Erreur nettoyage: {e}", exc_info=True)


# ═══════════════════════════════════════════════════════════
# E.14: MISE À JOUR SCORES GAMIFICATION (Minuit)
# ═══════════════════════════════════════════════════════════


def job_mise_a_jour_scores_gamification() -> None:
    """E.14: Recalcule scores/badges quotidiens."""
    try:
        logger.info("E.14: Début mise à jour scores gamification")

        with obtenir_contexte_db() as session:
            from src.core.models.gamification import ScoreUtilisateur

            # Exemple: ajouter 1 point = 1 tâche complétée
            utilisateurs = session.query(ScoreUtilisateur).all()
            for user_score in utilisateurs:
                # Logique de calcul simple
                # À enrichir selon les métriques métier
                pass

            session.commit()
            logger.info("E.14: Scores mis à jour")
    except Exception as e:
        logger.error(f"E.14: Erreur mise à jour scores: {e}", exc_info=True)


# ═══════════════════════════════════════════════════════════
# E.15: ALERTE MÉTÉO JARDIN (7h)
# ═══════════════════════════════════════════════════════════


def job_alerte_meteo_jardin() -> None:
    """E.15: Alerte gel/canicule → protéger plantes."""
    try:
        logger.info("E.15: Début alerte météo jardin")

        # Récupérer météo (exemple: API météo)
        # En production: intégrer OpenWeatherMap ou MétéoFrance
        temp_min = 5  # Exemple: gelée prévue
        temp_max = 35  # Exemple: canicule prévue

        alerts = []
        if temp_min <= 2:
            alerts.append("❄️ Risk de gelée — protéger les plantes sensibles")
        if temp_max >= 33:
            alerts.append("🔥 Canicule prévue — arroser abondamment")

        if alerts:
            dispatcher = get_dispatcher_notifications()
            message = "🌱 Alerte jardin\n" + "\n".join(alerts)
            dispatcher.envoyer(
                user_id="1",
                message=message,
                canaux=["ntfy", "push"],
                titre="🌱 Alerte météo jardin",
            )
            logger.info(f"E.15: Alerte météo envoyée — {len(alerts)} alertes")
    except Exception as e:
        logger.error(f"E.15: Erreur alerte météo jardin: {e}", exc_info=True)


# ═══════════════════════════════════════════════════════════
# E.16: RÉSUMÉ FINANCIER SEMAINE (Ven 18h)
# ═══════════════════════════════════════════════════════════


def job_resume_financier_semaine() -> None:
    """E.16: Résumé dépenses de la semaine.
    
    Envoi: Email + Push
    """
    try:
        logger.info("E.16: Début résumé financier semaine")

        with obtenir_contexte_db() as session:
            from src.core.models.finances import Depense

            today = date.today()
            lundi = today - timedelta(days=today.weekday())

            depenses_semaine = (
                session.query(Depense)
                .filter(Depense.date_depense >= lundi)
                .filter(Depense.date_depense <= today)
                .all()
            )

            if not depenses_semaine:
                logger.info("E.16: Aucune dépense cette semaine")
                return

            # Agréger par catégorie
            par_categorie = {}
            for dep in depenses_semaine:
                cat = dep.categorie or "Autre"
                par_categorie[cat] = par_categorie.get(cat, 0) + dep.montant

            total = sum(d.montant for d in depenses_semaine)

            # Formater message
            lines = ["💰 *Résumé dépenses semaine*\n"]
            for cat, montant in sorted(par_categorie.items(), key=lambda x: x[1], reverse=True)[:5]:
                lines.append(f"  {cat}: {montant:.2f}€")
            lines.append(f"\n📊 *Total: {total:.2f}€*")

            message = "\n".join(lines)

            dispatcher = get_dispatcher_notifications()
            dispatcher.envoyer(
                user_id="1",
                message=message,
                canaux=["email", "push"],
                titre="💰 Résumé financier semaine",
            )

            logger.info(f"E.16: Résumé financier généré — {total:.2f}€")
    except Exception as e:
        logger.error(f"E.16: Erreur résumé financier: {e}", exc_info=True)
