"""
Service pour gérer les notifications enrichies du Sprint E.

Features:
- E.1: WhatsApp flux courses semaine
- E.2: WhatsApp rappel activité Jules
- E.3: WhatsApp résultats paris
- E.4: Préférences notification granulaires
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


# ═══════════════════════════════════════════════════════════
# E.1-E.3: HANDLERS WHATSAPP ENRICHIS
# ═══════════════════════════════════════════════════════════


class HandlersWhatsAppEnrichis:
    """Handlers pour les flux WhatsApp enrichis (E.1-E.3)."""

    @staticmethod
    async def envoyer_flux_courses_semaine(sender: str) -> bool:
        """E.1: Envoie la liste de courses pour la semaine via WhatsApp.
        
        Template:
        🛒 Courses semaine du [xx/xx]
        
        • Article 1 (rayon)
        • Article 2 (rayon)
        ...
        
        [Bouton] Ajouter... [Bouton] Éditer entire liste
        """
        try:
            from src.services.integrations.whatsapp import envoyer_liste_courses_partagee

            with obtenir_contexte_db() as session:
                # Récupérer la liste de courses active
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
        """E.2: Envoie un rappel d'activité pour Jules via WhatsApp.
        
        Template:
        👶 Activité Jules de [jour]
        
        🎯 [Activité] - [durée]
        📍 Lieu: [lieu]
        🕒 Heure: [heure]
        
        Suggestion IA: [conseil développement]
        """
        try:
            from src.services.integrations.whatsapp import envoyer_message_whatsapp

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
                    logger.info("E.2: Aucune activité Jules programmée aujourd'hui")
                    return False

                lines = ["👶 *Activités Jules pour aujourd'hui*\n"]
                for activity in activities[:5]:
                    heure = activity.heure_debut.strftime("%H:%M") if activity.heure_debut else "?"
                    lines.append(
                        f"🎯 {activity.nom} - {heure}\n"
                        f"   Description: {activity.description or 'N/A'}"
                    )

                message = "\n".join(lines)
                return await envoyer_message_whatsapp(sender, message)
        except Exception as e:
            logger.error(f"E.2 Erreur : {e}")
            return False

    @staticmethod
    async def envoyer_resultats_paris(sender: str) -> bool:
        """E.3: Envoie résultats des paris sportifs via WhatsApp.
        
        Template:
        ⚽ Résultats matchs
        
        [Match 1] [Score] ✅/❌ [P&L]
        [Match 2] [Score] ✅/❌ [P&L]
        
        💰 Total: [bilan]
        """
        try:
            from src.services.integrations.whatsapp import envoyer_message_whatsapp

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

                lines = ["⚽ *Résultats paris semaine*\n"]
                total_pnl = 0

                for pari in paris[:10]:
                    result_emoji = "✅" if pari.gagne else "❌"
                    pnl = pari.montant_gagne - pari.mise if pari.gagne else -pari.mise
                    total_pnl += pnl
                    lines.append(
                        f"{result_emoji} {pari.description}: {pari.cote}x "
                        f"({pari.mise}€ → {pnl:+.0f}€)"
                    )

                lines.append(f"\n💰 *Total: {total_pnl:+.0f}€*")
                message = "\n".join(lines)
                return await envoyer_message_whatsapp(sender, message)
        except Exception as e:
            logger.error(f"E.3 Erreur : {e}")
            return False


# ═══════════════════════════════════════════════════════════
# E.4-E.5: SERVICE NOTIFICATIONS ENRICHI
# ═══════════════════════════════════════════════════════════


class ServiceNotificationsEnrichis:
    """Service pour PreferenceNotification et HistoriqueNotification."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def obtenir_preferences(self, user_id: str) -> dict[str, Any]:
        """Récupère les préférences de notification granulaires (E.4)."""
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
        """Met à jour les préférences (E.4)."""
        try:
            from src.core.models.notifications import PreferenceNotification

            prefs = (
                self.session.query(PreferenceNotification)
                .filter(PreferenceNotification.user_id == user_id)
                .first()
            )

            if not prefs:
                # Créer les pref par défaut
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
            logger.info(f"E.4: Prefs mises à jour pour {user_id}")
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
            from src.core.models.notifications_sprint_e import HistoriqueNotification

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
            logger.debug(f"E.5: Historique enregistré pour {user_id}")
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
            from src.core.models.notifications_sprint_e import HistoriqueNotification

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
            from src.core.models.notifications_sprint_e import HistoriqueNotification

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
            from src.core.models.notifications_sprint_e import HistoriqueNotification

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
        """Retourne les préférences par défaut."""
        return {
            "canal_prefere": "push",
            "canaux_par_categorie": {
                "rappels": ["push", "ntfy"],
                "alertes": ["push", "ntfy", "email"],
                "resumes": ["email", "whatsapp"],
            },
            "modules_actifs": {"max_par_heure": 5},
            "quiet_hours": {"debut": "22:00", "fin": "07:00"},
        }


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("service_notifications_enrichis", tags={"notifications", "sprint_e"})
def obtenir_service_notifications_enrichis() -> ServiceNotificationsEnrichis:
    """Factory pour le service notifications enrichis (E)."""
    with obtenir_contexte_db() as session:
        return ServiceNotificationsEnrichis(session)
