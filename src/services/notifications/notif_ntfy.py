"""
Service de notifications push via ntfy.sh.

Fonctionnalités:
- Envoi notifications push gratuites via ntfy.sh
- Alertes tâches en retard (MaintenanceTask)
- Rappels quotidiens configurables
- Support multi-appareils (abonnement topic)
"""

import asyncio
import logging
from datetime import date

import httpx
from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.core.models import ArticleCourses, MaintenanceTask
from src.services.notifications.types import (
    NTFY_BASE_URL,
    ConfigurationNtfy,
    NotificationNtfy,
    ResultatEnvoiNtfy,
)

logger = logging.getLogger(__name__)


class ServiceNtfy:
    """Service d'envoi de notifications push via ntfy.sh."""

    def __init__(self, config: ConfigurationNtfy | None = None):
        self.config = config or ConfigurationNtfy()
        self.client = httpx.AsyncClient(timeout=10.0)

    async def envoyer(self, notification: NotificationNtfy) -> ResultatEnvoiNtfy:
        """
        Envoie une notification push via ntfy.sh.

        Args:
            notification: Notification à envoyer

        Returns:
            ResultatEnvoiNtfy avec statut
        """
        if not self.config.actif:
            return ResultatEnvoiNtfy(succes=False, message="Notifications désactivées")

        url = f"{NTFY_BASE_URL}/{self.config.topic}"

        headers = {
            "Title": notification.titre,
            "Priority": str(notification.priorite),
        }

        # Tags (emojis)
        if notification.tags:
            headers["Tags"] = ",".join(notification.tags)

        # URL de clic
        if notification.click_url:
            headers["Click"] = notification.click_url

        # Actions
        if notification.actions:
            import json

            headers["Actions"] = json.dumps(notification.actions)

        try:
            response = await self.client.post(url, content=notification.message, headers=headers)

            if response.status_code == 200:
                data = response.json()
                return ResultatEnvoiNtfy(
                    succes=True, message="Notification envoyée", notification_id=data.get("id")
                )
            else:
                return ResultatEnvoiNtfy(
                    succes=False, message=f"Erreur {response.status_code}: {response.text}"
                )

        except Exception as e:
            logger.error(f"Erreur envoi notification: {e}")
            return ResultatEnvoiNtfy(succes=False, message=str(e))

    def envoyer_sync(self, notification: NotificationNtfy) -> ResultatEnvoiNtfy:
        """Version synchrone de l'envoi."""
        return asyncio.run(self.envoyer(notification))

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def obtenir_taches_en_retard(self, db: Session = None) -> list[MaintenanceTask]:
        """Récupère les tâches ménage/jardin en retard."""
        today = date.today()

        taches = (
            db.query(MaintenanceTask)
            .filter(MaintenanceTask.prochaine_fois < today, MaintenanceTask.fait == False)
            .order_by(MaintenanceTask.prochaine_fois)
            .all()
        )

        return taches

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def obtenir_taches_du_jour(self, db: Session = None) -> list[MaintenanceTask]:
        """Récupère les tâches prévues pour aujourd'hui."""
        today = date.today()

        taches = (
            db.query(MaintenanceTask)
            .filter(MaintenanceTask.prochaine_fois == today, MaintenanceTask.fait == False)
            .all()
        )

        return taches

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def obtenir_courses_urgentes(self, db: Session = None) -> list[ArticleCourses]:
        """Récupère les articles de courses haute priorité."""
        articles = (
            db.query(ArticleCourses)
            .filter(ArticleCourses.achete == False, ArticleCourses.priorite == "haute")
            .limit(10)
            .all()
        )

        return articles

    async def envoyer_alerte_tache_retard(self, tache: MaintenanceTask) -> ResultatEnvoiNtfy:
        """Envoie une alerte pour une tâche en retard."""
        jours_retard = (date.today() - tache.prochaine_fois).days

        # Priorité selon retard
        if jours_retard > 7:
            priorite = 5
            tags = ["warning", "calendar"]
        elif jours_retard > 3:
            priorite = 4
            tags = ["warning"]
        else:
            priorite = 3
            tags = ["calendar"]

        notification = NotificationNtfy(
            titre=f"â° Tâche en retard: {tache.nom}",
            message=f"{tache.nom}\n\nðŸ“… Prévue le {tache.prochaine_fois.strftime('%d/%m')}\nâš ï¸ {jours_retard} jour(s) de retard\n\n{tache.description or ''}",
            priorite=priorite,
            tags=tags,
        )

        return await self.envoyer(notification)

    async def envoyer_digest_quotidien(self) -> ResultatEnvoiNtfy:
        """Envoie le digest quotidien des tâches et rappels."""
        taches_retard = self.obtenir_taches_en_retard()
        taches_jour = self.obtenir_taches_du_jour()

        if not taches_retard and not taches_jour:
            return ResultatEnvoiNtfy(succes=True, message="Pas de tâches à notifier")

        # Construire message
        lines = ["ðŸ“‹ Résumé du jour\n"]

        if taches_retard:
            lines.append(f"âš ï¸ {len(taches_retard)} tâche(s) en retard:")
            for t in taches_retard[:3]:
                lines.append(f"  • {t.nom}")

        if taches_jour:
            lines.append(f"\nðŸ“… {len(taches_jour)} tâche(s) aujourd'hui:")
            for t in taches_jour[:5]:
                lines.append(f"  • {t.nom}")

        notification = NotificationNtfy(
            titre="ðŸ“‹ Digest Matanne",
            message="\n".join(lines),
            priorite=3 if not taches_retard else 4,
            tags=["house", "clipboard"],
        )

        return await self.envoyer(notification)

    async def envoyer_rappel_courses(self, nb_articles: int) -> ResultatEnvoiNtfy:
        """Envoie un rappel pour les courses."""
        courses_urgentes = self.obtenir_courses_urgentes()

        if not courses_urgentes:
            return ResultatEnvoiNtfy(succes=True, message="Pas de courses urgentes")

        articles_noms = [c.nom for c in courses_urgentes[:5]]

        notification = NotificationNtfy(
            titre=f"ðŸ›’ {nb_articles} articles en attente",
            message="Articles prioritaires:\n• " + "\n• ".join(articles_noms),
            priorite=2,
            tags=["shopping_cart"],
        )

        return await self.envoyer(notification)

    async def test_connexion(self) -> ResultatEnvoiNtfy:
        """Teste la connexion au serveur ntfy."""
        notification = NotificationNtfy(
            titre="ðŸ”” Test Matanne",
            message="Les notifications sont correctement configurées!",
            priorite=3,
            tags=["white_check_mark"],
        )

        return await self.envoyer(notification)

    def test_connexion_sync(self) -> ResultatEnvoiNtfy:
        """Version synchrone du test de connexion."""
        return asyncio.run(self.test_connexion())

    def get_subscribe_url(self) -> str:
        """Retourne l'URL d'abonnement pour les appareils."""
        return f"ntfy://{self.config.topic}"

    def get_web_url(self) -> str:
        """Retourne l'URL web pour voir les notifications."""
        return f"{NTFY_BASE_URL}/{self.config.topic}"

    def get_subscribe_qr_url(self) -> str:
        """Retourne l'URL pour générer un QR code d'abonnement."""
        topic_url = f"{NTFY_BASE_URL}/{self.config.topic}"
        return f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={topic_url}"


class PlanificateurNtfy:
    """Planificateur de notifications automatiques ntfy."""

    def __init__(self, service: ServiceNtfy):
        self.service = service
        self._running = False

    async def verifier_et_envoyer_alertes(self) -> list[ResultatEnvoiNtfy]:
        """Vérifie et envoie les alertes pour tâches en retard."""
        taches = self.service.obtenir_taches_en_retard()

        resultats = []
        for tache in taches[:5]:  # Max 5 notifications à la fois
            resultat = await self.service.envoyer_alerte_tache_retard(tache)
            resultats.append(resultat)

        return resultats

    def lancer_verification_sync(self) -> list[ResultatEnvoiNtfy]:
        """Lance la vérification de manière synchrone."""
        return asyncio.run(self.verifier_et_envoyer_alertes())


# ═══════════════════════════════════════════════════════════
# FACTORIES
# ═══════════════════════════════════════════════════════════


def obtenir_service_ntfy(config: ConfigurationNtfy | None = None) -> ServiceNtfy:
    """Factory pour le service de notifications ntfy."""
    return ServiceNtfy(config)


def obtenir_planificateur_ntfy() -> PlanificateurNtfy:
    """Factory pour le planificateur de notifications ntfy."""
    service = obtenir_service_ntfy()
    return PlanificateurNtfy(service)


# Alias rétrocompatibilité
NotificationPushService = ServiceNtfy
NotificationPushScheduler = PlanificateurNtfy
NotificationPushConfig = ConfigurationNtfy
NotificationPush = NotificationNtfy
ResultatEnvoiPush = ResultatEnvoiNtfy
get_notification_push_service = obtenir_service_ntfy
get_notification_push_scheduler = obtenir_planificateur_ntfy


__all__ = [
    "ServiceNtfy",
    "PlanificateurNtfy",
    "obtenir_service_ntfy",
    "obtenir_planificateur_ntfy",
    # Alias rétrocompatibilité
    "NotificationPushService",
    "NotificationPushScheduler",
    "NotificationPushConfig",
    "NotificationPush",
    "ResultatEnvoiPush",
    "get_notification_push_service",
    "get_notification_push_scheduler",
]
