"""
Tests unitaires pour notifications.py - Service de notifications
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from src.services.notifications import (
    NotificationService,
    Notification,
    TypeAlerte,
)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FIXTURES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

@pytest.fixture
def notification_service():
    """Service de notifications pour tests"""
    return NotificationService()


@pytest.fixture
def sample_article():
    """Article d'exemple pour tests"""
    return {
        "id": 1,
        "nom": "Lait",
        "ingredient_id": 10,
        "quantite": 2,
        "quantite_min": 5,
        "unite": "L",
        "date_peremption": datetime.now(timezone.utc),
    }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ENUM TYPE ALERTE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestTypeAlerte:
    """Tests de l'enum TypeAlerte"""
    
    def test_stock_critique_exists(self):
        """Test que STOCK_CRITIQUE existe"""
        assert TypeAlerte.STOCK_CRITIQUE is not None
        assert TypeAlerte.STOCK_CRITIQUE.value == "stock_critique"
    
    def test_stock_bas_exists(self):
        """Test que STOCK_BAS existe"""
        assert TypeAlerte.STOCK_BAS is not None
        assert TypeAlerte.STOCK_BAS.value == "stock_bas"
    
    def test_peremption_proche_exists(self):
        """Test que PEREMPTION_PROCHE existe"""
        assert TypeAlerte.PEREMPTION_PROCHE is not None
        assert TypeAlerte.PEREMPTION_PROCHE.value == "peremption_proche"
    
    def test_peremption_depassee_exists(self):
        """Test que PEREMPTION_DEPASSEE existe"""
        assert TypeAlerte.PEREMPTION_DEPASSEE is not None
        assert TypeAlerte.PEREMPTION_DEPASSEE.value == "peremption_depassee"
    
    def test_article_ajoute_exists(self):
        """Test que ARTICLE_AJOUTE existe"""
        assert TypeAlerte.ARTICLE_AJOUTE is not None
    
    def test_article_modifie_exists(self):
        """Test que ARTICLE_MODIFIE existe"""
        assert TypeAlerte.ARTICLE_MODIFIE is not None
    
    def test_all_types_count(self):
        """Test le nombre total de types"""
        assert len(TypeAlerte) == 6


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS MODÃˆLE NOTIFICATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestNotificationModel:
    """Tests du modÃ¨le Notification"""
    
    def test_notification_creation_minimal(self):
        """Test crÃ©ation notification minimale"""
        notif = Notification(
            type_alerte=TypeAlerte.STOCK_BAS,
            article_id=1,
            ingredient_id=10,
            titre="Test Alert",
            message="Ceci est un test de notification",
        )
        
        assert notif.type_alerte == TypeAlerte.STOCK_BAS
        assert notif.article_id == 1
        assert notif.titre == "Test Alert"
    
    def test_notification_defaults(self):
        """Test valeurs par dÃ©faut"""
        notif = Notification(
            type_alerte=TypeAlerte.STOCK_CRITIQUE,
            article_id=1,
            ingredient_id=10,
            titre="Test notification",
            message="Message de test complet",
        )
        
        assert notif.lue is False
        assert notif.priorite == "moyenne"
        assert notif.push_envoyee is False
        assert notif.id is None
        assert notif.email is None
    
    def test_notification_with_priority(self):
        """Test notification avec prioritÃ©"""
        notif = Notification(
            type_alerte=TypeAlerte.STOCK_CRITIQUE,
            article_id=1,
            ingredient_id=10,
            titre="Alerte haute prioritÃ©",
            message="Message urgent trÃ¨s important",
            priorite="haute",
        )
        
        assert notif.priorite == "haute"
    
    def test_notification_icone_default(self):
        """Test icÃ´ne par dÃ©faut"""
        notif = Notification(
            type_alerte=TypeAlerte.STOCK_BAS,
            article_id=1,
            ingredient_id=10,
            titre="Test icÃ´ne",
            message="Test du message icÃ´ne",
        )
        
        assert notif.icone == "â„¹ï¸"
    
    def test_notification_date_creation_auto(self):
        """Test date crÃ©ation automatique"""
        notif = Notification(
            type_alerte=TypeAlerte.STOCK_BAS,
            article_id=1,
            ingredient_id=10,
            titre="Test dates",
            message="Test du message dates",
        )
        
        assert notif.date_creation is not None
        assert isinstance(notif.date_creation, datetime)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS SERVICE INIT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestNotificationServiceInit:
    """Tests d'initialisation du service"""
    
    def test_service_creation(self, notification_service):
        """Test crÃ©ation du service"""
        assert notification_service is not None
    
    def test_service_has_notifications_dict(self, notification_service):
        """Test que le service a un dict notifications"""
        assert hasattr(notification_service, 'notifications')
        assert isinstance(notification_service.notifications, dict)
    
    def test_service_has_next_id(self, notification_service):
        """Test que le service a un compteur d'ID"""
        assert hasattr(notification_service, '_next_id')
        assert notification_service._next_id == 1


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CRÃ‰ER NOTIFICATION STOCK CRITIQUE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestCreerNotificationStockCritique:
    """Tests de crÃ©ation notification stock critique"""
    
    def test_creates_notification(self, notification_service, sample_article):
        """Test crÃ©ation notification"""
        notif = notification_service.creer_notification_stock_critique(sample_article)
        
        assert notif is not None
        assert isinstance(notif, Notification)
    
    def test_notification_type(self, notification_service, sample_article):
        """Test type de notification"""
        notif = notification_service.creer_notification_stock_critique(sample_article)
        
        assert notif.type_alerte == TypeAlerte.STOCK_CRITIQUE
    
    def test_notification_priority_haute(self, notification_service, sample_article):
        """Test prioritÃ© haute pour stock critique"""
        notif = notification_service.creer_notification_stock_critique(sample_article)
        
        assert notif.priorite == "haute"
    
    def test_notification_contains_article_name(self, notification_service, sample_article):
        """Test que le nom de l'article est dans le message"""
        notif = notification_service.creer_notification_stock_critique(sample_article)
        
        assert "Lait" in notif.message
        assert "Lait" in notif.titre
    
    def test_notification_contains_quantities(self, notification_service, sample_article):
        """Test que les quantitÃ©s sont dans le message"""
        notif = notification_service.creer_notification_stock_critique(sample_article)
        
        assert "2" in notif.message  # quantitÃ© actuelle
        assert "5" in notif.message  # quantitÃ© min


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CRÃ‰ER NOTIFICATION STOCK BAS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestCreerNotificationStockBas:
    """Tests de crÃ©ation notification stock bas"""
    
    def test_creates_notification(self, notification_service, sample_article):
        """Test crÃ©ation notification"""
        notif = notification_service.creer_notification_stock_bas(sample_article)
        
        assert notif is not None
        assert isinstance(notif, Notification)
    
    def test_notification_type(self, notification_service, sample_article):
        """Test type de notification"""
        notif = notification_service.creer_notification_stock_bas(sample_article)
        
        assert notif.type_alerte == TypeAlerte.STOCK_BAS
    
    def test_notification_priority_moyenne(self, notification_service, sample_article):
        """Test prioritÃ© moyenne pour stock bas"""
        notif = notification_service.creer_notification_stock_bas(sample_article)
        
        assert notif.priorite == "moyenne"
    
    def test_notification_icone_warning(self, notification_service, sample_article):
        """Test icÃ´ne warning pour stock bas"""
        notif = notification_service.creer_notification_stock_bas(sample_article)
        
        assert notif.icone == "âš ï¸"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CRÃ‰ER NOTIFICATION PEREMPTION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestCreerNotificationPeremption:
    """Tests de crÃ©ation notification pÃ©remption"""
    
    def test_method_exists(self, notification_service):
        """Test que la mÃ©thode existe"""
        assert hasattr(notification_service, 'creer_notification_peremption')
        assert callable(notification_service.creer_notification_peremption)
    
    def test_creates_notification_for_proche(self, notification_service, sample_article):
        """Test crÃ©ation notification pÃ©remption proche"""
        notif = notification_service.creer_notification_peremption(sample_article, jours_avant=3)
        
        assert notif is not None
    
    def test_creates_notification_for_expired(self, notification_service, sample_article):
        """Test crÃ©ation notification produit expirÃ©"""
        notif = notification_service.creer_notification_peremption(sample_article, jours_avant=0)
        
        assert notif is not None
    
    def test_expired_has_different_title(self, notification_service, sample_article):
        """Test titre diffÃ©rent pour produit expirÃ©"""
        notif = notification_service.creer_notification_peremption(sample_article, jours_avant=-1)
        
        assert "EXPIRÃ‰" in notif.titre or "expirÃ©" in notif.titre.lower()

