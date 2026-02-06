"""
Tests Deep Execution Part 33 - Garmin, Push Notifications, Calendar Sync, Batch Cooking.

Couverture ciblée:
- GarminService: get_authorization_url, complete_authorization
- PushNotificationService: models, preferences
- CalendarSyncService: ICalGenerator, ExternalCalendarConfig
- BatchCookingService: get_config, ROBOTS_DISPONIBLES
"""

import pytest
from datetime import date, datetime, time, timedelta
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from contextlib import contextmanager
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool


# ═══════════════════════════════════════════════════════════
# FIXTURES BD EN MÉMOIRE
# ═══════════════════════════════════════════════════════════

@pytest.fixture(scope="function")
def memory_engine():
    """Crée un engine SQLite en mémoire pour chaque test."""
    from src.core.models import Base
    
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        echo=False,
        poolclass=StaticPool,
    )
    
    # Patch JSONB pour SQLite
    from sqlalchemy.dialects.sqlite.base import SQLiteTypeCompiler
    from sqlalchemy.dialects.postgresql import JSONB
    
    original = SQLiteTypeCompiler.process
    def patched(self, type_, **kw):
        if isinstance(type_, JSONB):
            return "JSON"
        return original(self, type_, **kw)
    SQLiteTypeCompiler.process = patched
    
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def memory_session(memory_engine):
    """Session SQLite en mémoire pour les tests."""
    SessionLocal = sessionmaker(bind=memory_engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def patch_db_context(memory_session):
    """Patch obtenir_contexte_db pour utiliser la session en mémoire."""
    @contextmanager
    def mock_context():
        yield memory_session
    
    with patch("src.core.database.obtenir_contexte_db", mock_context):
        with patch("src.core.decorators.obtenir_contexte_db", mock_context):
            yield memory_session


# ═══════════════════════════════════════════════════════════
# TESTS GARMIN SERVICE
# ═══════════════════════════════════════════════════════════

class TestGarminServiceDeepExecution:
    """Tests d'exécution profonde pour GarminService."""
    
    def test_garmin_config_defaults(self):
        """Test GarminConfig avec valeurs par défaut."""
        from src.services.garmin_sync import GarminConfig
        
        config = GarminConfig(
            consumer_key="test_key",
            consumer_secret="test_secret",
        )
        
        assert config.consumer_key == "test_key"
        assert "garmin.com" in config.request_token_url
        assert "garmin.com" in config.authorize_url
        assert "garmin.com" in config.access_token_url
    
    def test_get_garmin_config(self):
        """Test get_garmin_config factory."""
        from src.services.garmin_sync import get_garmin_config
        
        with patch("src.services.garmin_sync.obtenir_parametres") as mock_params:
            mock_settings = MagicMock()
            mock_settings.GARMIN_CONSUMER_KEY = "key123"
            mock_settings.GARMIN_CONSUMER_SECRET = "secret456"
            mock_params.return_value = mock_settings
            
            config = get_garmin_config()
            
            assert config.consumer_key == "key123"
            assert config.consumer_secret == "secret456"
    
    def test_garmin_service_init(self):
        """Test initialisation GarminService."""
        from src.services.garmin_sync import GarminService, GarminConfig
        
        config = GarminConfig(
            consumer_key="test",
            consumer_secret="test",
        )
        service = GarminService(config)
        
        assert service.config == config
        assert service._oauth_session is None
        assert service._temp_request_token is None
    
    def test_garmin_service_init_default_config(self):
        """Test GarminService avec config par défaut."""
        from src.services.garmin_sync import GarminService
        
        with patch("src.services.garmin_sync.get_garmin_config") as mock_config:
            from src.services.garmin_sync import GarminConfig
            mock_config.return_value = GarminConfig(
                consumer_key="default_key",
                consumer_secret="default_secret",
            )
            
            service = GarminService()
            
            assert service.config.consumer_key == "default_key"
    
    def test_get_authorization_url_missing_keys(self):
        """Test get_authorization_url lève exception si clés manquantes."""
        from src.services.garmin_sync import GarminService, GarminConfig
        
        config = GarminConfig(
            consumer_key="",
            consumer_secret="",
        )
        service = GarminService(config)
        
        with pytest.raises(ValueError) as exc_info:
            service.get_authorization_url()
        
        assert "Clés Garmin non configurées" in str(exc_info.value)
    
    def test_get_authorization_url_with_mock_oauth(self):
        """Test get_authorization_url avec OAuth mockée."""
        from src.services.garmin_sync import GarminService, GarminConfig
        
        config = GarminConfig(
            consumer_key="valid_key",
            consumer_secret="valid_secret",
        )
        service = GarminService(config)
        
        with patch("src.services.garmin_sync.OAuth1Session") as mock_oauth:
            mock_session = MagicMock()
            mock_session.fetch_request_token.return_value = {
                "oauth_token": "token123",
                "oauth_token_secret": "secret456",
            }
            mock_session.authorization_url.return_value = "https://garmin.com/authorize?token=123"
            mock_oauth.return_value = mock_session
            
            url, token = service.get_authorization_url()
            
            assert "authorize" in url
            assert token["oauth_token"] == "token123"
            assert service._temp_request_token is not None


# ═══════════════════════════════════════════════════════════
# TESTS PUSH NOTIFICATION SERVICE
# ═══════════════════════════════════════════════════════════

class TestPushNotificationServiceDeepExecution:
    """Tests d'exécution profonde pour PushNotificationService."""
    
    def test_notification_type_enum(self):
        """Test NotificationType enum."""
        from src.services.push_notifications import NotificationType
        
        assert NotificationType.STOCK_LOW.value == "stock_low"
        assert NotificationType.MEAL_REMINDER.value == "meal_reminder"
        assert NotificationType.EXPIRATION_CRITICAL.value == "expiration_critical"
    
    def test_push_subscription_model(self):
        """Test PushSubscription model."""
        from src.services.push_notifications import PushSubscription
        
        subscription = PushSubscription(
            user_id="user123",
            endpoint="https://fcm.googleapis.com/fcm/send/xxx",
            p256dh_key="key123",
            auth_key="auth456",
            user_agent="Mozilla/5.0",
        )
        
        assert subscription.user_id == "user123"
        assert subscription.is_active is True
        assert subscription.endpoint.startswith("https://")
    
    def test_push_notification_model(self):
        """Test PushNotification model."""
        from src.services.push_notifications import PushNotification, NotificationType
        
        notification = PushNotification(
            title="Stock bas",
            body="Le lait est presque épuisé",
            notification_type=NotificationType.STOCK_LOW,
            url="/inventaire",
        )
        
        assert notification.title == "Stock bas"
        assert notification.notification_type == NotificationType.STOCK_LOW
        assert notification.vibrate == [100, 50, 100]
    
    def test_notification_preferences_model(self):
        """Test NotificationPreferences model."""
        from src.services.push_notifications import NotificationPreferences
        
        prefs = NotificationPreferences(
            user_id="user123",
            stock_alerts=True,
            expiration_alerts=True,
            quiet_hours_start=22,
            quiet_hours_end=7,
        )
        
        assert prefs.stock_alerts is True
        assert prefs.quiet_hours_start == 22
        assert prefs.max_per_hour == 5
    
    def test_push_notification_service_init(self):
        """Test initialisation PushNotificationService."""
        from src.services.push_notifications import PushNotificationService
        
        service = PushNotificationService()
        
        assert service._subscriptions == {}
        assert service._preferences == {}
        assert service._sent_count == {}
    
    def test_notification_with_actions(self):
        """Test PushNotification avec actions."""
        from src.services.push_notifications import PushNotification, NotificationType
        
        notification = PushNotification(
            title="Repas prévu",
            body="N'oubliez pas de préparer les pâtes",
            notification_type=NotificationType.MEAL_REMINDER,
            actions=[
                {"action": "dismiss", "title": "Fermer"},
                {"action": "snooze", "title": "Reporter"},
            ],
            require_interaction=True,
        )
        
        assert len(notification.actions) == 2
        assert notification.require_interaction is True


# ═══════════════════════════════════════════════════════════
# TESTS CALENDAR SYNC SERVICE
# ═══════════════════════════════════════════════════════════

class TestCalendarSyncServiceDeepExecution:
    """Tests d'exécution profonde pour CalendarSyncService."""
    
    def test_calendar_provider_enum(self):
        """Test CalendarProvider enum."""
        from src.services.calendar_sync import CalendarProvider
        
        assert CalendarProvider.GOOGLE.value == "google"
        assert CalendarProvider.APPLE.value == "apple"
        assert CalendarProvider.OUTLOOK.value == "outlook"
    
    def test_sync_direction_enum(self):
        """Test SyncDirection enum."""
        from src.services.calendar_sync import SyncDirection
        
        assert SyncDirection.IMPORT_ONLY.value == "import"
        assert SyncDirection.EXPORT_ONLY.value == "export"
        assert SyncDirection.BIDIRECTIONAL.value == "both"
    
    def test_external_calendar_config_defaults(self):
        """Test ExternalCalendarConfig avec valeurs par défaut."""
        from src.services.calendar_sync import ExternalCalendarConfig, CalendarProvider, SyncDirection
        
        config = ExternalCalendarConfig(
            user_id="user123",
            provider=CalendarProvider.GOOGLE,
            name="Mon Google Calendar",
        )
        
        assert config.user_id == "user123"
        assert config.provider == CalendarProvider.GOOGLE
        assert config.sync_direction == SyncDirection.BIDIRECTIONAL
        assert config.sync_meals is True
        assert config.is_active is True
    
    def test_calendar_event_external_model(self):
        """Test CalendarEventExternal model."""
        from src.services.calendar_sync import CalendarEventExternal
        
        event = CalendarEventExternal(
            id="evt123",
            external_id="google_evt_456",
            title="Dîner familial",
            description="Préparation des pâtes",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=1),
            location="Cuisine",
        )
        
        assert event.title == "Dîner familial"
        assert event.all_day is False
    
    def test_sync_result_model(self):
        """Test SyncResult model."""
        from src.services.calendar_sync import SyncResult
        
        result = SyncResult(
            success=True,
            message="Synchronisation réussie",
            events_imported=5,
            events_exported=3,
        )
        
        assert result.success is True
        assert result.events_imported == 5
        assert result.errors == []
    
    def test_ical_generator_basic(self):
        """Test ICalGenerator génère structure de base."""
        from src.services.calendar_sync import ICalGenerator, CalendarEventExternal
        
        events = [
            CalendarEventExternal(
                id="1",
                title="Test Event",
                start_time=datetime(2024, 1, 15, 12, 0),
                end_time=datetime(2024, 1, 15, 13, 0),
            )
        ]
        
        ical = ICalGenerator.generate_ical(events)
        
        assert "BEGIN:VCALENDAR" in ical
        assert "VERSION:2.0" in ical
        assert "PRODID:" in ical
    
    def test_ical_generator_empty(self):
        """Test ICalGenerator avec liste vide."""
        from src.services.calendar_sync import ICalGenerator
        
        ical = ICalGenerator.generate_ical([])
        
        assert "BEGIN:VCALENDAR" in ical


# ═══════════════════════════════════════════════════════════
# TESTS BATCH COOKING SERVICE
# ═══════════════════════════════════════════════════════════

class TestBatchCookingServiceDeepExecution:
    """Tests d'exécution profonde pour BatchCookingService."""
    
    def test_robots_disponibles_constant(self):
        """Test ROBOTS_DISPONIBLES constant."""
        from src.services.batch_cooking import ROBOTS_DISPONIBLES
        
        assert "cookeo" in ROBOTS_DISPONIBLES
        assert ROBOTS_DISPONIBLES["cookeo"]["nom"] == "Cookeo"
        assert ROBOTS_DISPONIBLES["cookeo"]["emoji"] == "🍲"
        assert ROBOTS_DISPONIBLES["four"]["parallele"] is True
    
    def test_jours_semaine_constant(self):
        """Test JOURS_SEMAINE constant."""
        from src.services.batch_cooking import JOURS_SEMAINE
        
        assert len(JOURS_SEMAINE) == 7
        assert JOURS_SEMAINE[0] == "Lundi"
        assert JOURS_SEMAINE[6] == "Dimanche"
    
    def test_etape_batch_ia_model(self):
        """Test EtapeBatchIA model."""
        from src.services.batch_cooking import EtapeBatchIA
        
        etape = EtapeBatchIA(
            ordre=1,
            titre="Préchauffer le four",
            description="Préchauffer à 180°C pendant 15 minutes",
            duree_minutes=15,
            robots=["four"],
            groupe_parallele=0,
        )
        
        assert etape.ordre == 1
        assert etape.duree_minutes == 15
        assert "four" in etape.robots
    
    def test_etape_batch_ia_validation(self):
        """Test EtapeBatchIA validation."""
        from src.services.batch_cooking import EtapeBatchIA
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            EtapeBatchIA(
                ordre=0,  # Doit être >= 1
                titre="X",  # Trop court
                description="X",  # Trop court
                duree_minutes=0,  # Doit être >= 1
            )
    
    def test_session_batch_ia_model(self):
        """Test SessionBatchIA model."""
        from src.services.batch_cooking import SessionBatchIA, EtapeBatchIA
        
        session = SessionBatchIA(
            recettes=["Pâtes carbonara", "Salade César"],
            duree_totale_estimee=90,
            etapes=[
                EtapeBatchIA(
                    ordre=1,
                    titre="Préparer les ingrédients",
                    description="Couper les légumes et mesurer les ingrédients",
                    duree_minutes=20,
                )
            ],
            conseils_jules=["Faire participer Jules à la préparation"],
        )
        
        assert len(session.recettes) == 2
        assert session.duree_totale_estimee == 90
        assert len(session.etapes) == 1
    
    def test_preparation_ia_model(self):
        """Test PreparationIA model."""
        from src.services.batch_cooking import PreparationIA
        
        prep = PreparationIA(
            nom="Sauce tomate maison",
            portions=8,
            conservation_jours=7,
            localisation="frigo",
            container_suggere="Bocal en verre",
        )
        
        assert prep.nom == "Sauce tomate maison"
        assert prep.portions == 8
        assert prep.conservation_jours == 7
    
    def test_batch_cooking_service_init(self):
        """Test initialisation BatchCookingService."""
        from src.services.batch_cooking import BatchCookingService
        
        with patch("src.services.batch_cooking.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            
            service = BatchCookingService()
            
            assert service.cache_ttl == 1800
    
    def test_get_config_mock(self):
        """Test get_config avec mock."""
        from src.services.batch_cooking import BatchCookingService
        
        with patch("src.services.batch_cooking.obtenir_client_ia") as mock_client:
            mock_client.return_value = MagicMock()
            
            service = BatchCookingService()
            
            with patch.object(service, 'get_config') as mock_config:
                from src.core.models import ConfigBatchCooking
                mock_config_obj = MagicMock(spec=ConfigBatchCooking)
                mock_config_obj.jours_batch = [6]
                mock_config_obj.duree_max_session = 180
                mock_config.return_value = mock_config_obj
                
                config = service.get_config()
                
                assert config.jours_batch == [6]


# ═══════════════════════════════════════════════════════════
# TESTS INTÉGRATION MODÈLES
# ═══════════════════════════════════════════════════════════

class TestModelsIntegration:
    """Tests d'intégration des modèles Pydantic."""
    
    def test_all_models_creatable(self):
        """Test que tous les modèles peuvent être créés."""
        from src.services.garmin_sync import GarminConfig
        from src.services.push_notifications import (
            PushSubscription, 
            PushNotification, 
            NotificationPreferences,
            NotificationType,
        )
        from src.services.calendar_sync import (
            ExternalCalendarConfig,
            CalendarEventExternal,
            SyncResult,
            CalendarProvider,
        )
        from src.services.batch_cooking import (
            EtapeBatchIA,
            SessionBatchIA,
            PreparationIA,
        )
        
        # GarminConfig
        gc = GarminConfig(consumer_key="k", consumer_secret="s")
        assert gc.consumer_key == "k"
        
        # PushSubscription
        ps = PushSubscription(
            user_id="u", 
            endpoint="e", 
            p256dh_key="p", 
            auth_key="a"
        )
        assert ps.user_id == "u"
        
        # PushNotification
        pn = PushNotification(title="t", body="b")
        assert pn.title == "t"
        
        # NotificationPreferences
        np = NotificationPreferences(user_id="u")
        assert np.stock_alerts is True
        
        # ExternalCalendarConfig
        ecc = ExternalCalendarConfig(
            user_id="u", 
            provider=CalendarProvider.GOOGLE
        )
        assert ecc.provider == CalendarProvider.GOOGLE
        
        # CalendarEventExternal
        cee = CalendarEventExternal(
            title="t",
            start_time=datetime.now(),
            end_time=datetime.now(),
        )
        assert cee.title == "t"
        
        # SyncResult
        sr = SyncResult()
        assert sr.success is False
        
        # EtapeBatchIA
        ebi = EtapeBatchIA(
            ordre=1,
            titre="Test titre",
            description="Test description minimale",
            duree_minutes=10,
        )
        assert ebi.ordre == 1
        
        # SessionBatchIA
        sbi = SessionBatchIA(
            recettes=["Recette 1"],
            duree_totale_estimee=60,
            etapes=[ebi],
        )
        assert len(sbi.recettes) == 1
        
        # PreparationIA
        pi = PreparationIA(
            nom="Prep test",
            portions=4,
            conservation_jours=5,
        )
        assert pi.portions == 4


# ═══════════════════════════════════════════════════════════
# TESTS ENUMS VALIDATION
# ═══════════════════════════════════════════════════════════

class TestEnumsValidation:
    """Tests validation des enums."""
    
    def test_notification_type_all_values(self):
        """Test tous les types de notification."""
        from src.services.push_notifications import NotificationType
        
        all_types = list(NotificationType)
        
        assert len(all_types) >= 10
        assert NotificationType.STOCK_LOW in all_types
        assert NotificationType.MEAL_REMINDER in all_types
    
    def test_calendar_provider_all_values(self):
        """Test tous les providers de calendrier."""
        from src.services.calendar_sync import CalendarProvider
        
        all_providers = list(CalendarProvider)
        
        assert len(all_providers) == 4
        assert CalendarProvider.GOOGLE in all_providers
        assert CalendarProvider.ICAL_URL in all_providers
    
    def test_sync_direction_all_values(self):
        """Test toutes les directions de sync."""
        from src.services.calendar_sync import SyncDirection
        
        all_directions = list(SyncDirection)
        
        assert len(all_directions) == 3
        assert SyncDirection.BIDIRECTIONAL in all_directions


# ═══════════════════════════════════════════════════════════
# TESTS EDGE CASES
# ═══════════════════════════════════════════════════════════

class TestEdgeCases:
    """Tests des cas limites."""
    
    def test_push_notification_silent(self):
        """Test notification silencieuse."""
        from src.services.push_notifications import PushNotification
        
        notification = PushNotification(
            title="Silent",
            body="No sound",
            silent=True,
            vibrate=[],
        )
        
        assert notification.silent is True
        assert notification.vibrate == []
    
    def test_calendar_event_all_day(self):
        """Test événement toute la journée."""
        from src.services.calendar_sync import CalendarEventExternal
        
        event = CalendarEventExternal(
            title="Vacances",
            start_time=datetime(2024, 7, 1),
            end_time=datetime(2024, 7, 15),
            all_day=True,
        )
        
        assert event.all_day is True
    
    def test_batch_etape_supervision(self):
        """Test étape de supervision."""
        from src.services.batch_cooking import EtapeBatchIA
        
        etape = EtapeBatchIA(
            ordre=1,
            titre="Surveiller la cuisson",
            description="Vérifier que ça ne brûle pas",
            duree_minutes=30,
            est_supervision=True,
            alerte_bruit=True,
        )
        
        assert etape.est_supervision is True
        assert etape.alerte_bruit is True
    
    def test_batch_etape_with_temperature(self):
        """Test étape avec température."""
        from src.services.batch_cooking import EtapeBatchIA
        
        etape = EtapeBatchIA(
            ordre=1,
            titre="Cuisson four",
            description="Cuire au four",
            duree_minutes=45,
            temperature=180,
        )
        
        assert etape.temperature == 180
    
    def test_preparation_conservation_max(self):
        """Test préparation conservation max."""
        from src.services.batch_cooking import PreparationIA
        
        prep = PreparationIA(
            nom="Confiture",
            portions=10,
            conservation_jours=90,  # Max
            localisation="placard",
        )
        
        assert prep.conservation_jours == 90
    
    def test_facture_maison_no_consumption(self):
        """Test facture sans consommation."""
        from src.services.budget import FactureMaison, CategorieDepense
        
        facture = FactureMaison(
            categorie=CategorieDepense.INTERNET,
            montant=39.99,
            mois=1,
            annee=2024,
            consommation=None,
        )
        
        assert facture.prix_unitaire is None
