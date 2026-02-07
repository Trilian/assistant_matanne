"""
Tests couverture pour src/services/garmin_sync.py
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import date, datetime, timedelta


# ═══════════════════════════════════════════════════════════
# TESTS GARMIN CONFIG
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGarminConfig:
    """Tests pour GarminConfig dataclass."""

    def test_garmin_config_creation(self):
        """Test création basique."""
        from src.services.garmin_sync import GarminConfig
        
        config = GarminConfig(
            consumer_key="test_key",
            consumer_secret="test_secret"
        )
        
        assert config.consumer_key == "test_key"
        assert config.consumer_secret == "test_secret"
        assert config.api_base_url == "https://apis.garmin.com"

    def test_garmin_config_defaults(self):
        """Test valeurs par défaut."""
        from src.services.garmin_sync import GarminConfig
        
        config = GarminConfig(consumer_key="key", consumer_secret="secret")
        
        assert "oauth/request_token" in config.request_token_url
        assert "oauthConfirm" in config.authorize_url
        assert "oauth/access_token" in config.access_token_url


@pytest.mark.unit
class TestGetGarminConfig:
    """Tests pour get_garmin_config()."""

    @patch('src.services.garmin_sync.obtenir_parametres')
    def test_get_garmin_config(self, mock_params):
        """Test récupération config depuis settings."""
        mock_settings = Mock()
        mock_settings.GARMIN_CONSUMER_KEY = "from_env_key"
        mock_settings.GARMIN_CONSUMER_SECRET = "from_env_secret"
        mock_params.return_value = mock_settings
        
        from src.services.garmin_sync import get_garmin_config
        
        config = get_garmin_config()
        
        assert config.consumer_key == "from_env_key"
        assert config.consumer_secret == "from_env_secret"

    @patch('src.services.garmin_sync.obtenir_parametres')
    def test_get_garmin_config_missing_keys(self, mock_params):
        """Test config sans clés."""
        mock_settings = Mock(spec=[])
        mock_params.return_value = mock_settings
        
        from src.services.garmin_sync import get_garmin_config
        
        config = get_garmin_config()
        
        assert config.consumer_key == ""
        assert config.consumer_secret == ""


# ═══════════════════════════════════════════════════════════
# TESTS GARMIN SERVICE INIT
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGarminServiceInit:
    """Tests pour l'initialisation du service."""

    @patch('src.services.garmin_sync.get_garmin_config')
    def test_init_with_default_config(self, mock_get_config):
        """Test initialisation avec config par défaut."""
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        from src.services.garmin_sync import GarminService
        
        service = GarminService()
        
        assert service.config == mock_config
        mock_get_config.assert_called_once()

    def test_init_with_custom_config(self):
        """Test initialisation avec config personnalisée."""
        from src.services.garmin_sync import GarminService, GarminConfig
        
        custom_config = GarminConfig(
            consumer_key="custom_key",
            consumer_secret="custom_secret"
        )
        
        service = GarminService(config=custom_config)
        
        assert service.config == custom_config
        assert service.config.consumer_key == "custom_key"


# ═══════════════════════════════════════════════════════════
# TESTS GET AUTHORIZATION URL
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGetAuthorizationUrl:
    """Tests pour get_authorization_url()."""

    def test_get_authorization_url_no_keys(self):
        """Test erreur si clés manquantes."""
        from src.services.garmin_sync import GarminService, GarminConfig
        
        config = GarminConfig(consumer_key="", consumer_secret="")
        service = GarminService(config=config)
        
        with pytest.raises(ValueError, match="Clés Garmin non configurées"):
            service.get_authorization_url()

    @patch('src.services.garmin_sync.OAuth1Session')
    def test_get_authorization_url_success(self, mock_oauth_class):
        """Test URL d'autorisation générée."""
        from src.services.garmin_sync import GarminService, GarminConfig
        
        # Mock OAuth session
        mock_session = Mock()
        mock_session.fetch_request_token.return_value = {
            "oauth_token": "request_token_value",
            "oauth_token_secret": "request_secret_value"
        }
        mock_session.authorization_url.return_value = "https://garmin.com/oauth?token=abc"
        mock_oauth_class.return_value = mock_session
        
        config = GarminConfig(consumer_key="key", consumer_secret="secret")
        service = GarminService(config=config)
        
        url, token = service.get_authorization_url()
        
        assert "garmin.com" in url
        assert token["oauth_token"] == "request_token_value"
        assert token["oauth_token_secret"] == "request_secret_value"

    @patch('src.services.garmin_sync.OAuth1Session')
    def test_get_authorization_url_with_callback(self, mock_oauth_class):
        """Test avec URL callback personnalisée."""
        from src.services.garmin_sync import GarminService, GarminConfig
        
        mock_session = Mock()
        mock_session.fetch_request_token.return_value = {
            "oauth_token": "token",
            "oauth_token_secret": "secret"
        }
        mock_session.authorization_url.return_value = "https://garmin.com/auth"
        mock_oauth_class.return_value = mock_session
        
        config = GarminConfig(consumer_key="key", consumer_secret="secret")
        service = GarminService(config=config)
        
        url, token = service.get_authorization_url(callback_url="https://myapp.com/callback")
        
        mock_oauth_class.assert_called_with(
            "key",
            client_secret="secret",
            callback_uri="https://myapp.com/callback"
        )

    @patch('src.services.garmin_sync.OAuth1Session')
    def test_get_authorization_url_exception(self, mock_oauth_class):
        """Test exception lors de la requête."""
        from src.services.garmin_sync import GarminService, GarminConfig
        
        mock_session = Mock()
        mock_session.fetch_request_token.side_effect = Exception("Network error")
        mock_oauth_class.return_value = mock_session
        
        config = GarminConfig(consumer_key="key", consumer_secret="secret")
        service = GarminService(config=config)
        
        with pytest.raises(Exception, match="Network error"):
            service.get_authorization_url()


# ═══════════════════════════════════════════════════════════
# TESTS COMPLETE AUTHORIZATION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCompleteAuthorization:
    """Tests pour complete_authorization()."""

    @patch('src.services.garmin_sync.OAuth1Session')
    def test_complete_authorization_no_token(self, mock_oauth_class):
        """Test erreur si token manquant."""
        from src.services.garmin_sync import GarminService, GarminConfig
        
        config = GarminConfig(consumer_key="key", consumer_secret="secret")
        service = GarminService(config=config)
        service._temp_request_token = None
        
        mock_db = MagicMock()
        
        with pytest.raises(ValueError, match="Request token manquant"):
            service.complete_authorization(user_id=1, oauth_verifier="verifier", db=mock_db)

    @patch('src.services.garmin_sync.OAuth1Session')
    def test_complete_authorization_user_not_found(self, mock_oauth_class):
        """Test erreur si utilisateur non trouvé."""
        from src.services.garmin_sync import GarminService, GarminConfig
        
        mock_session = Mock()
        mock_session.fetch_access_token.return_value = {
            "oauth_token": "access_token",
            "oauth_token_secret": "access_secret"
        }
        mock_oauth_class.return_value = mock_session
        
        config = GarminConfig(consumer_key="key", consumer_secret="secret")
        service = GarminService(config=config)
        service._temp_request_token = {"oauth_token": "t", "oauth_token_secret": "s"}
        
        mock_db = MagicMock()
        mock_db.get.return_value = None  # User not found
        
        with pytest.raises(ValueError, match="Utilisateur .* non trouvé"):
            service.complete_authorization(user_id=999, oauth_verifier="verifier", db=mock_db)

    @patch('src.services.garmin_sync.OAuth1Session')
    def test_complete_authorization_success_new_token(self, mock_oauth_class):
        """Test création nouveau token."""
        from src.services.garmin_sync import GarminService, GarminConfig
        
        mock_session = Mock()
        mock_session.fetch_access_token.return_value = {
            "oauth_token": "access_token",
            "oauth_token_secret": "access_secret"
        }
        mock_oauth_class.return_value = mock_session
        
        config = GarminConfig(consumer_key="key", consumer_secret="secret")
        service = GarminService(config=config)
        service._temp_request_token = {"oauth_token": "t", "oauth_token_secret": "s"}
        
        # Mock user without existing garmin_token
        mock_user = Mock()
        mock_user.garmin_token = None
        mock_user.garmin_connected = False
        
        mock_db = MagicMock()
        mock_db.get.return_value = mock_user
        
        result = service.complete_authorization(user_id=1, oauth_verifier="verifier123", db=mock_db)
        
        assert result is True
        mock_db.add.assert_called_once()  # New token added
        mock_db.commit.assert_called_once()

    @patch('src.services.garmin_sync.OAuth1Session')
    def test_complete_authorization_update_existing_token(self, mock_oauth_class):
        """Test mise à jour token existant."""
        from src.services.garmin_sync import GarminService, GarminConfig
        
        mock_session = Mock()
        mock_session.fetch_access_token.return_value = {
            "oauth_token": "new_access_token",
            "oauth_token_secret": "new_access_secret"
        }
        mock_oauth_class.return_value = mock_session
        
        config = GarminConfig(consumer_key="key", consumer_secret="secret")
        service = GarminService(config=config)
        
        # Use provided request_token instead of _temp
        request_tok = {"oauth_token": "req_t", "oauth_token_secret": "req_s"}
        
        # Mock user with existing garmin_token
        mock_garmin_token = Mock()
        mock_user = Mock()
        mock_user.garmin_token = mock_garmin_token
        
        mock_db = MagicMock()
        mock_db.get.return_value = mock_user
        
        result = service.complete_authorization(
            user_id=1, 
            oauth_verifier="verifier", 
            request_token=request_tok,
            db=mock_db
        )
        
        assert result is True
        assert mock_garmin_token.oauth_token == "new_access_token"
        assert mock_garmin_token.oauth_token_secret == "new_access_secret"


# ═══════════════════════════════════════════════════════════
# TESTS GET AUTHENTICATED SESSION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGetAuthenticatedSession:
    """Tests pour _get_authenticated_session()."""

    @patch('src.services.garmin_sync.OAuth1Session')
    def test_get_authenticated_session(self, mock_oauth_class):
        """Test création session authentifiée."""
        from src.services.garmin_sync import GarminService, GarminConfig
        
        mock_session = Mock()
        mock_oauth_class.return_value = mock_session
        
        config = GarminConfig(consumer_key="key", consumer_secret="secret")
        service = GarminService(config=config)
        
        mock_token = Mock()
        mock_token.oauth_token = "user_token"
        mock_token.oauth_token_secret = "user_secret"
        
        session = service._get_authenticated_session(mock_token)
        
        mock_oauth_class.assert_called_with(
            "key",
            client_secret="secret",
            resource_owner_key="user_token",
            resource_owner_secret="user_secret"
        )
        assert session == mock_session


# ═══════════════════════════════════════════════════════════
# TESTS SYNC USER DATA
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSyncUserData:
    """Tests pour sync_user_data()."""

    @patch('src.services.garmin_sync.get_garmin_config')
    def test_sync_user_data_not_connected(self, mock_get_config):
        """Test erreur si utilisateur non trouvé."""
        from src.services.garmin_sync import GarminService
        
        mock_config = Mock()
        mock_config.consumer_key = "key"
        mock_config.consumer_secret = "secret"
        mock_get_config.return_value = mock_config
        
        service = GarminService()
        
        mock_db = MagicMock()
        mock_db.get.return_value = None  # Utilisateur non trouvé
        
        with pytest.raises(ValueError, match="non trouvé"):
            service.sync_user_data(user_id=1, db=mock_db)

    @patch('src.services.garmin_sync.get_garmin_config')
    def test_sync_user_data_no_token(self, mock_get_config):
        """Test erreur si token manquant."""
        from src.services.garmin_sync import GarminService
        
        mock_config = Mock()
        mock_config.consumer_key = "key"
        mock_config.consumer_secret = "secret"
        mock_get_config.return_value = mock_config
        
        service = GarminService()
        
        mock_user = Mock()
        mock_user.garmin_connected = True
        mock_user.garmin_token = None
        mock_user.prenom = "Test"
        
        mock_db = MagicMock()
        mock_db.get.return_value = mock_user
        
        with pytest.raises(ValueError, match="non trouvé ou Garmin non connecté"):
            service.sync_user_data(user_id=1, db=mock_db)
    
    @patch('src.services.garmin_sync.get_garmin_config')
    def test_sync_user_data_sync_disabled(self, mock_get_config):
        """Test sync désactivée retourne zéros."""
        from src.services.garmin_sync import GarminService
        
        mock_config = Mock()
        mock_config.consumer_key = "key"
        mock_config.consumer_secret = "secret"
        mock_get_config.return_value = mock_config
        
        service = GarminService()
        
        mock_user = Mock()
        mock_token = Mock()
        mock_token.sync_active = False
        mock_user.garmin_token = mock_token
        
        mock_db = MagicMock()
        mock_db.get.return_value = mock_user
        
        result = service.sync_user_data(user_id=1, db=mock_db)
        
        assert result["activities_synced"] == 0
        assert result["summaries_synced"] == 0


# ═══════════════════════════════════════════════════════════
# TESTS FACTORY FUNCTION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGarminFactoryFunction:
    """Tests pour get_garmin_service()."""

    @patch('src.services.garmin_sync.get_garmin_config')
    def test_get_garmin_service(self, mock_get_config):
        """Test factory retourne service."""
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        from src.services.garmin_sync import get_garmin_service
        
        service = get_garmin_service()
        
        assert service is not None


# ═══════════════════════════════════════════════════════════
# TESTS USER HELPERS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUserHelpers:
    """Tests pour les fonctions utilitaires utilisateur."""

    def test_get_or_create_user_existing(self):
        """Test récupération utilisateur existant."""
        from src.services.garmin_sync import get_or_create_user
        
        mock_user = Mock()
        mock_user.username = "existing"
        
        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_user
        
        result = get_or_create_user("existing", "Existing User", db=mock_db)
        
        assert result == mock_user

    def test_get_or_create_user_new(self):
        """Test création nouvel utilisateur."""
        from src.services.garmin_sync import get_or_create_user
        
        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        
        result = get_or_create_user("newuser", "New User", db=mock_db)
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_get_user_by_username(self):
        """Test récupération par username."""
        from src.services.garmin_sync import get_user_by_username
        
        mock_user = Mock()
        mock_user.username = "testuser"
        
        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_user
        
        result = get_user_by_username("testuser", db=mock_db)
        
        assert result == mock_user

    def test_list_all_users(self):
        """Test liste tous les utilisateurs."""
        from src.services.garmin_sync import list_all_users
        
        mock_users = [Mock(), Mock(), Mock()]
        
        mock_db = MagicMock()
        mock_db.query.return_value.all.return_value = mock_users
        
        result = list_all_users(db=mock_db)
        
        assert result == mock_users


# ═══════════════════════════════════════════════════════════
# TESTS DISCONNECT USER
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestDisconnectUser:
    """Tests pour disconnect_user()."""

    @patch('src.services.garmin_sync.get_garmin_config')
    def test_disconnect_user_not_found(self, mock_get_config):
        """Test utilisateur non trouvé."""
        mock_get_config.return_value = Mock()
        
        from src.services.garmin_sync import GarminService
        
        service = GarminService()
        
        mock_db = MagicMock()
        mock_db.get.return_value = None
        
        result = service.disconnect_user(user_id=999, db=mock_db)
        
        assert result is False

    @patch('src.services.garmin_sync.get_garmin_config')
    def test_disconnect_user_success(self, mock_get_config):
        """Test déconnexion réussie."""
        mock_get_config.return_value = Mock()
        
        from src.services.garmin_sync import GarminService
        
        service = GarminService()
        
        mock_garmin_token = Mock()
        mock_user = Mock()
        mock_user.garmin_connected = True
        mock_user.garmin_token = mock_garmin_token
        
        mock_db = MagicMock()
        mock_db.get.return_value = mock_user
        
        result = service.disconnect_user(user_id=1, db=mock_db)
        
        assert result is True
        # La fonction supprime le token et met garmin_connected à False
        mock_db.delete.assert_called_once_with(mock_garmin_token)
        mock_db.commit.assert_called_once()


# ═══════════════════════════════════════════════════════════
# TESTS MODULE EXPORTS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestModuleExports:
    """Tests pour les exports du module."""

    def test_garmin_config_exported(self):
        """Test GarminConfig exporté."""
        from src.services.garmin_sync import GarminConfig
        assert GarminConfig is not None

    def test_garmin_service_exported(self):
        """Test GarminService exporté."""
        from src.services.garmin_sync import GarminService
        assert GarminService is not None

    def test_get_garmin_service_exported(self):
        """Test get_garmin_service exporté."""
        from src.services.garmin_sync import get_garmin_service
        assert get_garmin_service is not None

    def test_get_garmin_config_exported(self):
        """Test get_garmin_config exporté."""
        from src.services.garmin_sync import get_garmin_config
        assert get_garmin_config is not None

    def test_helper_functions_exported(self):
        """Test fonctions utilitaires exportées."""
        from src.services.garmin_sync import (
            get_or_create_user,
            get_user_by_username,
            list_all_users,
            init_family_users
        )
        assert all([get_or_create_user, get_user_by_username, list_all_users, init_family_users])


# ═══════════════════════════════════════════════════════════
# TESTS FETCH ACTIVITIES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestFetchActivities:
    """Tests pour _fetch_activities()."""

    @patch('src.services.garmin_sync.get_garmin_config')
    def test_fetch_activities_success(self, mock_get_config):
        """Test récupération activités réussie."""
        from src.services.garmin_sync import GarminService, GarminConfig
        from datetime import date, timedelta
        
        config = GarminConfig(consumer_key="key", consumer_secret="secret")
        service = GarminService(config=config)
        
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = [{"activityId": "123"}]
        mock_session.get.return_value = mock_response
        
        start = date.today() - timedelta(days=7)
        end = date.today()
        
        result = service._fetch_activities(mock_session, start, end)
        
        assert len(result) == 1
        assert result[0]["activityId"] == "123"

    @patch('src.services.garmin_sync.get_garmin_config')
    def test_fetch_activities_error(self, mock_get_config):
        """Test erreur lors de récupération activités."""
        from src.services.garmin_sync import GarminService, GarminConfig
        from datetime import date
        
        config = GarminConfig(consumer_key="key", consumer_secret="secret")
        service = GarminService(config=config)
        
        mock_session = Mock()
        mock_session.get.side_effect = Exception("API Error")
        
        result = service._fetch_activities(mock_session, date.today(), date.today())
        
        assert result == []


# ═══════════════════════════════════════════════════════════
# TESTS FETCH DAILY SUMMARIES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestFetchDailySummaries:
    """Tests pour _fetch_daily_summaries()."""

    @patch('src.services.garmin_sync.get_garmin_config')
    def test_fetch_daily_summaries_success(self, mock_get_config):
        """Test récupération résumés réussie."""
        from src.services.garmin_sync import GarminService, GarminConfig
        from datetime import date
        
        config = GarminConfig(consumer_key="key", consumer_secret="secret")
        service = GarminService(config=config)
        
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = [{"calendarDate": "2024-01-01", "steps": 10000}]
        mock_session.get.return_value = mock_response
        
        result = service._fetch_daily_summaries(mock_session, date.today(), date.today())
        
        assert len(result) == 1
        assert result[0]["steps"] == 10000

    @patch('src.services.garmin_sync.get_garmin_config')
    def test_fetch_daily_summaries_error(self, mock_get_config):
        """Test erreur lors de récupération résumés."""
        from src.services.garmin_sync import GarminService, GarminConfig
        from datetime import date
        
        config = GarminConfig(consumer_key="key", consumer_secret="secret")
        service = GarminService(config=config)
        
        mock_session = Mock()
        mock_session.get.side_effect = Exception("API Error")
        
        result = service._fetch_daily_summaries(mock_session, date.today(), date.today())
        
        assert result == []


# ═══════════════════════════════════════════════════════════
# TESTS SAVE ACTIVITY
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSaveActivity:
    """Tests pour _save_activity()."""

    @patch('src.services.garmin_sync.get_garmin_config')
    def test_save_activity_new(self, mock_get_config):
        """Test sauvegarde nouvelle activité."""
        from src.services.garmin_sync import GarminService, GarminConfig
        
        config = GarminConfig(consumer_key="key", consumer_secret="secret")
        service = GarminService(config=config)
        
        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        
        data = {
            "activityId": "123456",
            "activityType": "running",
            "activityName": "Morning Run",
            "startTimeInSeconds": 1704067200,  # 2024-01-01
            "durationInSeconds": 3600,
            "distanceInMeters": 5000,
            "activeKilocalories": 300
        }
        
        result = service._save_activity(mock_db, 1, data)
        
        mock_db.add.assert_called_once()

    @patch('src.services.garmin_sync.get_garmin_config')
    def test_save_activity_existing(self, mock_get_config):
        """Test activité déjà existante."""
        from src.services.garmin_sync import GarminService, GarminConfig
        
        config = GarminConfig(consumer_key="key", consumer_secret="secret")
        service = GarminService(config=config)
        
        existing = Mock()
        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = existing
        
        data = {"activityId": "123456"}
        
        result = service._save_activity(mock_db, 1, data)
        
        assert result == existing
        mock_db.add.assert_not_called()

    @patch('src.services.garmin_sync.get_garmin_config')
    def test_save_activity_no_start_time(self, mock_get_config):
        """Test sauvegarde sans timestamp."""
        from src.services.garmin_sync import GarminService, GarminConfig
        
        config = GarminConfig(consumer_key="key", consumer_secret="secret")
        service = GarminService(config=config)
        
        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        
        data = {"activityId": "123456", "activityType": "walking"}
        
        result = service._save_activity(mock_db, 1, data)
        
        mock_db.add.assert_called_once()


# ═══════════════════════════════════════════════════════════
# TESTS SAVE DAILY SUMMARY
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSaveDailySummary:
    """Tests pour _save_daily_summary()."""

    @patch('src.services.garmin_sync.get_garmin_config')
    def test_save_daily_summary_new(self, mock_get_config):
        """Test sauvegarde nouveau résumé."""
        from src.services.garmin_sync import GarminService, GarminConfig
        
        config = GarminConfig(consumer_key="key", consumer_secret="secret")
        service = GarminService(config=config)
        
        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        
        data = {
            "calendarDate": "2024-01-01",
            "steps": 10000,
            "distanceInMeters": 8000,
            "totalKilocalories": 2000,
            "activeKilocalories": 500,
            "restingHeartRateInBeatsPerMinute": 60
        }
        
        result = service._save_daily_summary(mock_db, 1, data)
        
        mock_db.add.assert_called_once()

    @patch('src.services.garmin_sync.get_garmin_config')
    def test_save_daily_summary_existing(self, mock_get_config):
        """Test mise à jour résumé existant."""
        from src.services.garmin_sync import GarminService, GarminConfig
        
        config = GarminConfig(consumer_key="key", consumer_secret="secret")
        service = GarminService(config=config)
        
        existing = Mock()
        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = existing
        
        data = {"calendarDate": "2024-01-01", "steps": 12000}
        
        result = service._save_daily_summary(mock_db, 1, data)
        
        assert result == existing
        assert existing.pas == 12000
        mock_db.add.assert_not_called()

    @patch('src.services.garmin_sync.get_garmin_config')
    def test_save_daily_summary_from_timestamp(self, mock_get_config):
        """Test avec timestamp au lieu de calendarDate."""
        from src.services.garmin_sync import GarminService, GarminConfig
        
        config = GarminConfig(consumer_key="key", consumer_secret="secret")
        service = GarminService(config=config)
        
        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        
        data = {"startTimeInSeconds": 1704067200, "steps": 8000}  # 2024-01-01
        
        result = service._save_daily_summary(mock_db, 1, data)
        
        mock_db.add.assert_called_once()


# ═══════════════════════════════════════════════════════════
# TESTS GET USER STATS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGetUserStats:
    """Tests pour get_user_stats()."""

    @patch('src.services.garmin_sync.get_garmin_config')
    def test_get_user_stats_user_not_found(self, mock_get_config):
        """Test utilisateur non trouvé."""
        from src.services.garmin_sync import GarminService, GarminConfig
        
        config = GarminConfig(consumer_key="key", consumer_secret="secret")
        service = GarminService(config=config)
        
        mock_db = MagicMock()
        mock_db.get.return_value = None
        
        result = service.get_user_stats(user_id=999, db=mock_db)
        
        assert result == {}

    @patch('src.services.garmin_sync.get_garmin_config')
    def test_get_user_stats_success(self, mock_get_config):
        """Test récupération stats réussie."""
        from src.services.garmin_sync import GarminService, GarminConfig
        
        config = GarminConfig(consumer_key="key", consumer_secret="secret")
        service = GarminService(config=config)
        
        # Mock user
        mock_user = Mock()
        mock_user.garmin_connected = True
        mock_user.objectif_pas_quotidien = 10000
        mock_user.objectif_calories_brulees = 500
        mock_user.garmin_token = Mock(derniere_sync=None)
        
        # Mock summaries
        mock_summary = Mock()
        mock_summary.pas = 10000
        mock_summary.calories_actives = 300
        mock_summary.distance_metres = 8000
        
        # Mock activities
        mock_activity = Mock()
        
        mock_db = MagicMock()
        mock_db.get.return_value = mock_user
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_summary]
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
        
        # On utilise side_effect pour différencier les appels
        service._calculate_streak = Mock(return_value=5)
        
        result = service.get_user_stats(user_id=1, db=mock_db)
        
        assert result["garmin_connected"] is True


# ═══════════════════════════════════════════════════════════
# TESTS CALCULATE STREAK
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCalculateStreak:
    """Tests pour _calculate_streak()."""

    @patch('src.services.garmin_sync.get_garmin_config')
    def test_calculate_streak_no_user(self, mock_get_config):
        """Test pas d'utilisateur."""
        from src.services.garmin_sync import GarminService, GarminConfig
        
        config = GarminConfig(consumer_key="key", consumer_secret="secret")
        service = GarminService(config=config)
        
        mock_db = MagicMock()
        mock_db.get.return_value = None
        
        result = service._calculate_streak(user_id=999, db=mock_db)
        
        assert result == 0

    @patch('src.services.garmin_sync.get_garmin_config')
    def test_calculate_streak_with_data(self, mock_get_config):
        """Test calcul avec données."""
        from src.services.garmin_sync import GarminService, GarminConfig
        from datetime import date
        
        config = GarminConfig(consumer_key="key", consumer_secret="secret")
        service = GarminService(config=config)
        
        mock_user = Mock()
        mock_user.objectif_pas_quotidien = 10000
        
        # Summaries avec objectif atteint
        mock_summary = Mock()
        mock_summary.date = date.today()
        mock_summary.pas = 12000
        
        mock_db = MagicMock()
        mock_db.get.return_value = mock_user
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_summary]
        
        result = service._calculate_streak(user_id=1, db=mock_db)
        
        assert result >= 1


# ═══════════════════════════════════════════════════════════
# TESTS INIT FAMILY USERS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestInitFamilyUsers:
    """Tests pour init_family_users()."""

    def test_init_family_users(self):
        """Test initialisation utilisateurs famille."""
        from src.services.garmin_sync import init_family_users
        
        mock_user_anne = Mock(username="anne")
        mock_user_mathieu = Mock(username="mathieu")
        
        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.side_effect = [
            mock_user_anne, mock_user_mathieu
        ]
        
        anne, mathieu = init_family_users(db=mock_db)
        
        assert anne.username == "anne"
        assert mathieu.username == "mathieu"


# ═══════════════════════════════════════════════════════════
# TESTS SYNC USER DATA FULL
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSyncUserDataFull:
    """Tests complets pour sync_user_data()."""

    @patch('src.services.garmin_sync.get_garmin_config')
    def test_sync_user_data_success(self, mock_get_config):
        """Test sync complète réussie."""
        from src.services.garmin_sync import GarminService, GarminConfig
        
        config = GarminConfig(
            consumer_key="key",
            consumer_secret="secret",
            api_base_url="https://api.test"
        )
        service = GarminService(config=config)
        
        # Mock user avec token actif
        mock_token = Mock()
        mock_token.sync_active = True
        mock_token.oauth_token = "token"
        mock_token.oauth_token_secret = "secret"
        
        mock_user = Mock()
        mock_user.garmin_token = mock_token
        
        mock_db = MagicMock()
        mock_db.get.return_value = mock_user
        
        # Mock les méthodes fetch
        service._fetch_activities = Mock(return_value=[{"activityId": "1"}])
        service._fetch_daily_summaries = Mock(return_value=[{"calendarDate": "2024-01-01"}])
        service._save_activity = Mock()
        service._save_daily_summary = Mock()
        
        result = service.sync_user_data(user_id=1, db=mock_db)
        
        assert result["activities_synced"] == 1
        assert result["summaries_synced"] == 1
