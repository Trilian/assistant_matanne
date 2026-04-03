"""
Service pour gÃ©rer les notifications enrichies du Sprint E.

Features:
- E.1: WhatsApp flux courses semaine
- E.2: WhatsApp rappel activitÃ© Jules
- E.3: WhatsApp rÃ©sultats paris
- E.4: PrÃ©fÃ©rences notification granulaires
- E.5: Centre de notifications (historique)
- E.9-E.16: Jobs CRON notification
"""

import logging
from datetime import date, datetime, timedelta
from typing import Any, Optional

from sqlalchemy.orm import Session

from src.core.db import obtenir_contexte_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# E.1-E.3: HANDLERS WHATSAPP ENRICHIS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class HandlersTelegramEnrichis:
    """Handlers pour les flux WhatsApp enrichis (E.1-E.3)."""

    @staticmethod
    async def envoyer_flux_courses_semaine(sender: str) -> bool:
        """E.1: Envoie la liste de courses pour la semaine via WhatsApp.
        
        Template:
        ðŸ›’ Courses semaine du [xx/xx]
        
        â€¢ Article 1 (rayon)
        â€¢ Article 2 (rayon)
        ...
        
        [Bouton] Ajouter... [Bouton] Ã‰diter entire liste
        """
        try:
            from src.services.integrations.telegram import envoyer_liste_courses_partagee

            with obtenir_contexte_db() as session:
                # RÃ©cupÃ©rer la liste de courses active
                from src.core.models.courses import ListeCourses, ArticleCourses

                today = date.today()
                liste_active = (
                    session.query(ListeCourses)
                    .filter(ListeCourses.actif == True)
                    .order_by(ListeCourses.date_creation.desc())
                    .first()
                )

                if not liste_active:
                    logger.info("E.1: Aucune liste de courses active")
                    return False

                articles = (
                    session.query(ArticleCourses)
                    .filter(ArticleCourses.liste_courses_id == liste_active.id)
                    .filter(ArticleCourses.fait == False)
                    .all()
                )

                if not articles:
                    return False

                # Formatter les articles
                articles_formatted = [f"{a.nom} ({a.rayon_magasin or 'Autre'})" for a in articles]

                # Envoyer via WhatsApp
                return await envoyer_liste_courses_partagee(
                    articles=articles_formatted,
                    nom_liste=f"Courses {today.strftime('%d/%m')}",
                )
        except Exception as e:
            logger.error(f"E.1 Erreur : {e}")
            return False

    @staticmethod
    async def envoyer_rappel_activite_jules(sender: str) -> bool:
        """E.2: Envoie un rappel d'activitÃ© pour Jules via WhatsApp.
        
        Template:
        ðŸ‘¶ ActivitÃ© Jules de [jour]
        
        ðŸŽ¯ [ActivitÃ©] - [durÃ©e]
        ðŸ“ Lieu: [lieu]
        ðŸ•’ Heure: [heure]
        
        Suggestion IA: [conseil dÃ©veloppement]
        """
        try:
            from src.services.integrations.telegram import envoyer_message_telegram

            with obtenir_contexte_db() as session:
                from src.core.models.famille import ActiviteJules

                today = date.today()
                activities = (
                    session.query(ActiviteJules)
                    .filter(ActiviteJules.date_activite == today)
                    .order_by(ActiviteJules.heure_debut)
                    .all()
                )

                if not activities:
                    logger.info("E.2: Aucune activitÃ© Jules programmÃ©e aujourd'hui")
                    return False

                lines = ["ðŸ‘¶ *ActivitÃ©s Jules pour aujourd'hui*\n"]
                for activity in activities[:5]:
                    heure = activity.heure_debut.strftime("%H:%M") if activity.heure_debut else "?"
                    lines.append(
                        f"ðŸŽ¯ {activity.nom} - {heure}\n"
                        f"   Description: {activity.description or 'N/A'}"
                    )

                message = "\n".join(lines)
                return await envoyer_message_telegram(sender, message)
        except Exception as e:
            logger.error(f"E.2 Erreur : {e}")
            return False

    @staticmethod
    async def envoyer_resultats_paris(sender: str) -> bool:
        """E.3: Envoie rÃ©sultats des paris sportifs via WhatsApp.
        
        Template:
        âš½ RÃ©sultats matchs
        
        [Match 1] [Score] âœ…/âŒ [P&L]
        [Match 2] [Score] âœ…/âŒ [P&L]
        
        ðŸ’° Total: [bilan]
        """
        try:
            from src.services.integrations.telegram import envoyer_message_telegram

            with obtenir_contexte_db() as session:
                from src.core.models.jeux import PariSportif

                today = date.today()
                semaine_debut = today - timedelta(days=today.weekday())

                paris = (
                    session.query(PariSportif)
                    .filter(PariSportif.date_pari >= semaine_debut)
                    .filter(PariSportif.date_pari <= today)
                    .all()
                )

                if not paris:
                    logger.info("E.3: Aucun pari cette semaine")
                    return False

                lines = ["âš½ *RÃ©sultats paris semaine*\n"]
                total_pnl = 0

                for pari in paris[:10]:
                    result_emoji = "âœ…" if pari.gagne else "âŒ"
                    pnl = pari.montant_gagne - pari.mise if pari.gagne else -pari.mise
                    total_pnl += pnl
                    lines.append(
                        f"{result_emoji} {pari.description}: {pari.cote}x "
                        f"({pari.mise}â‚¬ â†’ {pnl:+.0f}â‚¬)"
                    )

                lines.append(f"\nðŸ’° *Total: {total_pnl:+.0f}â‚¬*")
                message = "\n".join(lines)
                return await envoyer_message_telegram(sender, message)
        except Exception as e:
            logger.error(f"E.3 Erreur : {e}")
            return False


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# E.4-E.5: SERVICE NOTIFICATIONS ENRICHI
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class ServiceNotificationsEnrichis:
    """Service pour PreferenceNotification et HistoriqueNotification."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def obtenir_preferences(self, user_id: str) -> dict[str, Any]:
        """RÃ©cupÃ¨re les prÃ©fÃ©rences de notification granulaires (E.4)."""
        try:
            from src.core.models.notifications import PreferenceNotification

            prefs = (
                self.session.query(PreferenceNotification)
                .filter(PreferenceNotification.user_id == user_id)
                .first()
            )

            if not prefs:
                return self._prefs_par_defaut()

            return {
                "canal_prefere": prefs.canal_prefere,
                "canaux_par_categorie": prefs.canaux_par_categorie or {},
                "modules_actifs": prefs.modules_actifs or {},
                "quiet_hours": {
                    "debut": prefs.quiet_hours_start,
                    "fin": prefs.quiet_hours_end,
                },
            }
        except Exception as e:
            logger.error(f"E.4 Erreur lecture prefs: {e}")
            return self._prefs_par_defaut()

    def mettre_a_jour_preferences(
        self, user_id: str, updates: dict[str, Any]
    ) -> bool:
        """Met Ã  jour les prÃ©fÃ©rences (E.4)."""
        try:
            from src.core.models.notifications import PreferenceNotification

            prefs = (
                self.session.query(PreferenceNotification)
                .filter(PreferenceNotification.user_id == user_id)
                .first()
            )

            if not prefs:
                # CrÃ©er les pref par dÃ©faut
                prefs = PreferenceNotification(user_id=user_id)
                self.session.add(prefs)

            # Appliquer les updates
            if "canal_prefere" in updates:
                prefs.canal_prefere = updates["canal_prefere"]
            if "canaux_par_categorie" in updates:
                prefs.canaux_par_categorie = updates["canaux_par_categorie"]
            if "modules_actifs" in updates:
                prefs.modules_actifs = updates["modules_actifs"]

            self.session.commit()
            logger.info(f"E.4: Prefs mises Ã  jour pour {user_id}")
            return True
        except Exception as e:
            logger.error(f"E.4 Erreur update prefs: {e}")
            self.session.rollback()
            return False

    def enregistrer_historique(
        self,
        user_id: str,
        canal: str,
        titre: str,
        message: str,
        type_evenement: Optional[str] = None,
        categorie: str = "autres",
        metadata: Optional[dict] = None,
    ) -> bool:
        """Enregistre une notification dans l'historique (E.5)."""
        try:
            from src.core.models.notifications_historique import HistoriqueNotification

            notif = HistoriqueNotification(
                user_id=user_id,
                canal=canal,
                titre=titre,
                message=message,
                type_evenement=type_evenement,
                categorie=categorie,
                metadata_payload=metadata or {},
                lu=False,
            )
            self.session.add(notif)
            self.session.commit()
            logger.debug(f"E.5: Historique enregistrÃ© pour {user_id}")
            return True
        except Exception as e:
            logger.error(f"E.5 Erreur historique: {e}")
            self.session.rollback()
            return False

    def lister_historique(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        non_lu_seulement: bool = False,
    ) -> list[dict[str, Any]]:
        """Liste l'historique des notifications (E.5)."""
        try:
            from src.core.models.notifications_historique import HistoriqueNotification

            query = self.session.query(HistoriqueNotification).filter(
                HistoriqueNotification.user_id == user_id
            )

            if non_lu_seulement:
                query = query.filter(HistoriqueNotification.lu == False)

            historique = (
                query.order_by(HistoriqueNotification.created_at.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )

            return [
                {
                    "id": h.id,
                    "canal": h.canal,
                    "titre": h.titre,
                    "message": h.message,
                    "type_evenement": h.type_evenement,
                    "categorie": h.categorie,
                    "lu": h.lu,
                    "timestamp": h.created_at.isoformat(),
                }
                for h in historique
            ]
        except Exception as e:
            logger.error(f"E.5 Erreur listing: {e}")
            return []

    def marquer_comme_lu(self, notification_id: int) -> bool:
        """Marque une notification comme lue (E.5)."""
        try:
            from src.core.models.notifications_historique import HistoriqueNotification

            notif = self.session.query(HistoriqueNotification).filter_by(id=notification_id).first()
            if notif:
                notif.lu = True
                self.session.commit()
                return True
        except Exception as e:
            logger.error(f"E.5 Erreur mark read: {e}")
            self.session.rollback()
        return False

    def marquer_tous_lus(self, user_id: str) -> bool:
        """Marque toutes les notifications comme lues (E.5)."""
        try:
            from src.core.models.notifications_historique import HistoriqueNotification

            self.session.query(HistoriqueNotification).filter(
                HistoriqueNotification.user_id == user_id
            ).update({"lu": True})
            self.session.commit()
            return True
        except Exception as e:
            logger.error(f"E.5 Erreur mark all read: {e}")
            self.session.rollback()
        return False

    @staticmethod
    def _prefs_par_defaut() -> dict[str, Any]:
        """Retourne les prÃ©fÃ©rences par dÃ©faut."""
        return {
            "canal_prefere": "push",
            "canaux_par_categorie": {
                "rappels": ["push", "ntfy"],
                "alertes": ["push", "ntfy", "email"],
                "resumes": ["email", "telegram"],
            },
            "modules_actifs": {"max_par_heure": 5},
            "quiet_hours": {"debut": "22:00", "fin": "07:00"},
        }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FACTORY
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@service_factory("service_notifications_enrichis", tags={"notifications", "enrichis"})
def obtenir_service_notifications_enrichis() -> ServiceNotificationsEnrichis:
    """Factory pour le service notifications enrichis."""
    with obtenir_contexte_db() as session:
        return ServiceNotificationsEnrichis(session)
