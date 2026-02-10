"""
Service Notifications Push - Alertes via ntfy.sh

Fonctionnalités:
- Envoi notifications push gratuites via ntfy.sh
- Alertes tâches en retard (MaintenanceTask)
- Rappels quotidiens configurables
- Support multi-appareils (abonnement topic)
"""

import logging
import asyncio
import httpx
from datetime import datetime, date, timedelta
from typing import Optional
from pydantic import BaseModel, Field

from src.core.database import obtenir_contexte_db
from src.core.decorators import avec_session_db, avec_gestion_erreurs
from src.core.config import obtenir_parametres
from src.core.models import MaintenanceTask, ShoppingItem

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

NTFY_BASE_URL = "https://ntfy.sh"

# Topic par défaut (peut être personnalisé par utilisateur)
DEFAULT_TOPIC = "matanne-famille"

# Priorités ntfy (1-5)
PRIORITY_MAPPING = {
    "urgente": 5,
    "haute": 4,
    "normale": 3,
    "basse": 2,
    "min": 1
}


# ═══════════════════════════════════════════════════════════
# MODÈLES DE DONNÉES
# ═══════════════════════════════════════════════════════════

class NotificationPushConfig(BaseModel):
    """Configuration des notifications push pour un utilisateur."""
    topic: str = Field(default=DEFAULT_TOPIC)
    actif: bool = Field(default=True)
    rappels_taches: bool = Field(default=True)
    rappels_courses: bool = Field(default=False)
    heure_digest: int = Field(default=8, ge=0, le=23)  # Heure du digest quotidien
    jours_digest: list[int] = Field(default_factory=lambda: [0, 1, 2, 3, 4, 5, 6])  # Tous les jours


class NotificationPush(BaseModel):
    """Une notification push à envoyer."""
    titre: str
    message: str
    priorite: int = Field(default=3, ge=1, le=5)
    tags: list[str] = Field(default_factory=list)
    click_url: Optional[str] = None
    actions: list[dict] = Field(default_factory=list)


class ResultatEnvoiPush(BaseModel):
    """Résultat d'envoi de notification push."""
    succes: bool
    message: str
    notification_id: Optional[str] = None


# ═══════════════════════════════════════════════════════════
# SERVICE NOTIFICATIONS PUSH
# ═══════════════════════════════════════════════════════════

class NotificationPushService:
    """Service d'envoi de notifications push via ntfy.sh."""
    
    def __init__(self, config: Optional[NotificationPushConfig] = None):
        self.config = config or NotificationPushConfig()
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def envoyer(self, notification: NotificationPush) -> ResultatEnvoiPush:
        """
        Envoie une notification push via ntfy.sh.
        
        Args:
            notification: Notification à envoyer
            
        Returns:
            ResultatEnvoiPush avec statut
        """
        if not self.config.actif:
            return ResultatEnvoiPush(succes=False, message="Notifications désactivées")
        
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
            response = await self.client.post(
                url,
                content=notification.message,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                return ResultatEnvoiPush(
                    succes=True,
                    message="Notification envoyée",
                    notification_id=data.get("id")
                )
            else:
                return ResultatEnvoiPush(
                    succes=False,
                    message=f"Erreur {response.status_code}: {response.text}"
                )
        
        except Exception as e:
            logger.error(f"Erreur envoi notification: {e}")
            return ResultatEnvoiPush(succes=False, message=str(e))
    
    def envoyer_sync(self, notification: NotificationPush) -> ResultatEnvoiPush:
        """Version synchrone de l'envoi."""
        return asyncio.run(self.envoyer(notification))
    
    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def obtenir_taches_en_retard(self, db: Session = None) -> list[MaintenanceTask]:
        """Récupère les tâches ménage/jardin en retard."""
        today = date.today()
        
        taches = db.query(MaintenanceTask).filter(
            MaintenanceTask.date_echeance < today,
            MaintenanceTask.statut != "termine"
        ).order_by(MaintenanceTask.date_echeance).all()
        
        return taches
    
    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def obtenir_taches_du_jour(self, db: Session = None) -> list[MaintenanceTask]:
        """Récupère les tâches prévues pour aujourd'hui."""
        today = date.today()
        
        taches = db.query(MaintenanceTask).filter(
            MaintenanceTask.date_echeance == today,
            MaintenanceTask.statut != "termine"
        ).all()
        
        return taches
    
    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def obtenir_courses_urgentes(self, db: Session = None) -> list[ShoppingItem]:
        """Récupère les articles de courses haute priorité."""
        articles = db.query(ShoppingItem).filter(
            ShoppingItem.achete == False,
            ShoppingItem.priorite == 1
        ).limit(10).all()
        
        return articles
    
    async def envoyer_alerte_tache_retard(self, tache: MaintenanceTask) -> ResultatEnvoiPush:
        """Envoie une alerte pour une tâche en retard."""
        jours_retard = (date.today() - tache.date_echeance).days
        
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
        
        notification = NotificationPush(
            titre=f"⏰ Tâche en retard: {tache.titre}",
            message=f"{tache.titre}\n\n📅 Prévue le {tache.date_echeance.strftime('%d/%m')}\n⚠️ {jours_retard} jour(s) de retard\n\n{tache.description or ''}",
            priorite=priorite,
            tags=tags
        )
        
        return await self.envoyer(notification)
    
    async def envoyer_digest_quotidien(self) -> ResultatEnvoiPush:
        """Envoie le digest quotidien des tâches et rappels."""
        taches_retard = self.obtenir_taches_en_retard()
        taches_jour = self.obtenir_taches_du_jour()
        
        if not taches_retard and not taches_jour:
            return ResultatEnvoiPush(succes=True, message="Pas de tâches à notifier")
        
        # Construire message
        lines = ["📋 Résumé du jour\n"]
        
        if taches_retard:
            lines.append(f"⚠️ {len(taches_retard)} tâche(s) en retard:")
            for t in taches_retard[:3]:
                lines.append(f"  • {t.titre}")
        
        if taches_jour:
            lines.append(f"\n📅 {len(taches_jour)} tâche(s) aujourd'hui:")
            for t in taches_jour[:5]:
                lines.append(f"  • {t.titre}")
        
        notification = NotificationPush(
            titre="📋 Digest Matanne",
            message="\n".join(lines),
            priorite=3 if not taches_retard else 4,
            tags=["house", "clipboard"]
        )
        
        return await self.envoyer(notification)
    
    async def envoyer_rappel_courses(self, nb_articles: int) -> ResultatEnvoiPush:
        """Envoie un rappel pour les courses."""
        courses_urgentes = self.obtenir_courses_urgentes()
        
        if not courses_urgentes:
            return ResultatEnvoiPush(succes=True, message="Pas de courses urgentes")
        
        articles_noms = [c.nom for c in courses_urgentes[:5]]
        
        notification = NotificationPush(
            titre=f"🛒 {nb_articles} articles en attente",
            message=f"Articles prioritaires:\n• " + "\n• ".join(articles_noms),
            priorite=2,
            tags=["shopping_cart"]
        )
        
        return await self.envoyer(notification)
    
    async def test_connexion(self) -> ResultatEnvoiPush:
        """Teste la connexion au serveur ntfy."""
        notification = NotificationPush(
            titre="🔔 Test Matanne",
            message="Les notifications sont correctement configurées!",
            priorite=3,
            tags=["white_check_mark"]
        )
        
        return await self.envoyer(notification)
    
    def test_connexion_sync(self) -> ResultatEnvoiPush:
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


# ═══════════════════════════════════════════════════════════
# SCHEDULER (optionnel)
# ═══════════════════════════════════════════════════════════

class NotificationPushScheduler:
    """Planificateur de notifications automatiques."""
    
    def __init__(self, service: NotificationPushService):
        self.service = service
        self._running = False
    
    async def verifier_et_envoyer_alertes(self) -> list[ResultatEnvoiPush]:
        """Vérifie et envoie les alertes pour tâches en retard."""
        taches = self.service.obtenir_taches_en_retard()
        
        resultats = []
        for tache in taches[:5]:  # Max 5 notifications à la fois
            resultat = await self.service.envoyer_alerte_tache_retard(tache)
            resultats.append(resultat)
        
        return resultats
    
    def lancer_verification_sync(self) -> list[ResultatEnvoiPush]:
        """Lance la vérification de manière synchrone."""
        return asyncio.run(self.verifier_et_envoyer_alertes())


# ═══════════════════════════════════════════════════════════
# FACTORY FUNCTIONS
# ═══════════════════════════════════════════════════════════

def get_notification_push_service(config: Optional[NotificationPushConfig] = None) -> NotificationPushService:
    """Factory pour le service de notifications push."""
    return NotificationPushService(config)


def get_notification_push_scheduler() -> NotificationPushScheduler:
    """Factory pour le scheduler de notifications push."""
    service = get_notification_push_service()
    return NotificationPushScheduler(service)

