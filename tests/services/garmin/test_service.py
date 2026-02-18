"""
Tests pour src/services/garmin/service.py

Couvre:
- Connexion OAuth à Garmin Connect
- Récupération des activités
- Récupération des métriques de santé
- Gestion des erreurs d'authentification
"""

from contextlib import contextmanager
from datetime import date, timedelta
from unittest.mock import Mock, patch

import pytest

from src.services.garmin.service import (
    GarminService,
    ServiceGarmin,
    get_garmin_config,
    get_garmin_service,
    get_garmin_sync_service,
    get_or_create_user,
    get_user_by_username,
    list_all_users,
    obtenir_service_garmin,
)
from src.services.garmin.types import GarminConfig


# Helper pour créer un mock de contexte DB compatible avec 'with'
@contextmanager
def mock_db_context_manager(mock_session):
    """Context manager mocké pour la base de données."""
    yield mock_session


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def mock_config():
    """Configuration Garmin mockée."""
    return GarminConfig(
        consumer_key="test_consumer_key",
        consumer_secret="test_consumer_secret",
    )


@pytest.fixture
def mock_garmin_token():
    """Token Garmin mocké."""
    token = Mock()
    token.oauth_token = "test_access_token"
    token.oauth_token_secret = "test_access_secret"
    token.sync_active = True
    token.derniere_sync = None
    return token


@pytest.fixture
def mock_user(mock_garmin_token):
    """Utilisateur mocké avec token Garmin."""
    user = Mock()
    user.id = 1
    user.username = "testuser"
    user.garmin_token = mock_garmin_token
    user.garmin_connected = True
    user.objectif_pas_quotidien = 10000
    user.objectif_calories_brulees = 500
    return user


@pytest.fixture
def mock_db_session(mock_user):
    """Session de base de données mockée."""
    session = Mock()
    session.get = Mock(return_value=mock_user)
    session.query = Mock()
    session.add = Mock()
    session.commit = Mock()
    session.delete = Mock()
    return session


@pytest.fixture
def service(mock_config):
    """Service Garmin avec config mockée."""
    return ServiceGarmin(config=mock_config)


# ═══════════════════════════════════════════════════════════
# TESTS CONFIGURATION
# ═══════════════════════════════════════════════════════════


class TestGetGarminConfig:
    """Tests pour get_garmin_config."""

    @patch("src.services.garmin.service.obtenir_parametres")
    def test_config_depuis_settings(self, mock_settings):
        """La config est chargée depuis les paramètres."""
        mock_settings.return_value = Mock(
            GARMIN_CONSUMER_KEY="key123",
            GARMIN_CONSUMER_SECRET="secret456",
        )

        config = get_garmin_config()

        assert config.consumer_key == "key123"
        assert config.consumer_secret == "secret456"

    @patch("src.services.garmin.service.obtenir_parametres")
    def test_config_valeurs_defaut(self, mock_settings):
        """Valeurs par défaut si paramètres absents."""
        mock_settings.return_value = Mock(spec=[])

        config = get_garmin_config()

        assert config.consumer_key == ""
        assert config.consumer_secret == ""


# ═══════════════════════════════════════════════════════════
# TESTS SERVICE GARMIN - INIT
# ═══════════════════════════════════════════════════════════


class TestServiceGarminInit:
    """Tests pour l'initialisation du service."""

    def test_init_avec_config(self, mock_config):
        """Initialisation avec config fournie."""
        service = ServiceGarmin(config=mock_config)

        assert service.config == mock_config
        assert service._oauth_session is None
        assert service._temp_request_token is None

    @patch("src.services.garmin.service.get_garmin_config")
    def test_init_sans_config(self, mock_get_config, mock_config):
        """Initialisation sans config charge depuis factory."""
        mock_get_config.return_value = mock_config

        service = ServiceGarmin()

        mock_get_config.assert_called_once()
        assert service.config == mock_config


# ═══════════════════════════════════════════════════════════
# TESTS OAUTH FLOW
# ═══════════════════════════════════════════════════════════


class TestGetAuthorizationUrl:
    """Tests pour get_authorization_url."""

    def test_cles_non_configurees(self):
        """Erreur si clés non configurées."""
        config = GarminConfig(consumer_key="", consumer_secret="")
        service = ServiceGarmin(config=config)

        with pytest.raises(ValueError, match="Clés Garmin non configurées"):
            service.get_authorization_url()

    @patch("src.services.garmin.service.OAuth1Session")
    def test_generation_url(self, mock_oauth_class, mock_config):
        """URL d'autorisation générée correctement."""
        # Mock de la session OAuth
        mock_oauth = Mock()
        mock_oauth.fetch_request_token.return_value = {
            "oauth_token": "request_token_123",
            "oauth_token_secret": "request_secret_456",
        }
        mock_oauth.authorization_url.return_value = "https://garmin.com/authorize?token=xyz"
        mock_oauth_class.return_value = mock_oauth

        service = ServiceGarmin(config=mock_config)
        url, token = service.get_authorization_url()

        assert url == "https://garmin.com/authorize?token=xyz"
        assert token["oauth_token"] == "request_token_123"
        assert token["oauth_token_secret"] == "request_secret_456"
        assert service._temp_request_token == token

    @patch("src.services.garmin.service.OAuth1Session")
    def test_callback_url_personnalisee(self, mock_oauth_class, mock_config):
        """Callback URL personnalisée utilisée."""
        mock_oauth = Mock()
        mock_oauth.fetch_request_token.return_value = {
            "oauth_token": "token",
            "oauth_token_secret": "secret",
        }
        mock_oauth.authorization_url.return_value = "https://garmin.com/auth"
        mock_oauth_class.return_value = mock_oauth

        service = ServiceGarmin(config=mock_config)
        service.get_authorization_url(callback_url="https://myapp.com/callback")

        mock_oauth_class.assert_called_once()
        call_kwargs = mock_oauth_class.call_args[1]
        assert call_kwargs["callback_uri"] == "https://myapp.com/callback"

    @patch("src.services.garmin.service.OAuth1Session")
    def test_erreur_fetch_token(self, mock_oauth_class, mock_config):
        """Exception si fetch_request_token échoue."""
        mock_oauth = Mock()
        mock_oauth.fetch_request_token.side_effect = Exception("Network error")
        mock_oauth_class.return_value = mock_oauth

        service = ServiceGarmin(config=mock_config)

        with pytest.raises(Exception, match="Network error"):
            service.get_authorization_url()


class TestCompleteAuthorization:
    """Tests pour complete_authorization."""

    @patch("src.services.garmin.service.OAuth1Session")
    @patch("src.core.db.obtenir_contexte_db")
    def test_token_manquant(self, mock_db_ctx, mock_oauth_class, mock_config):
        """Erreur si request token manquant."""
        # Setup mock DB context
        mock_db = Mock()
        mock_db_ctx.return_value = mock_db_context_manager(mock_db)

        service = ServiceGarmin(config=mock_config)

        with pytest.raises(ValueError, match="Request token manquant"):
            service.complete_authorization(user_id=1, oauth_verifier="verifier")

    @patch("src.services.garmin.service.OAuth1Session")
    @patch("src.core.db.obtenir_contexte_db")
    def test_autorisation_complete(
        self, mock_db_ctx, mock_oauth_class, mock_config, mock_user, mock_garmin_token
    ):
        """Autorisation complète avec succès."""
        # Mock OAuth
        mock_oauth = Mock()
        mock_oauth.fetch_access_token.return_value = {
            "oauth_token": "access_token_final",
            "oauth_token_secret": "access_secret_final",
        }
        mock_oauth_class.return_value = mock_oauth

        # Mock DB
        mock_db = Mock()
        mock_db.get.return_value = mock_user
        mock_db_ctx.return_value = mock_db_context_manager(mock_db)

        # Nouveau token à créer
        mock_user.garmin_token = None

        service = ServiceGarmin(config=mock_config)
        service._temp_request_token = {
            "oauth_token": "request_token",
            "oauth_token_secret": "request_secret",
        }

        result = service.complete_authorization(user_id=1, oauth_verifier="verifier123")

        assert result is True
        assert service._temp_request_token is None

    @patch("src.services.garmin.service.OAuth1Session")
    @patch("src.core.db.obtenir_contexte_db")
    def test_utilisateur_non_trouve(self, mock_db_ctx, mock_oauth_class, mock_config):
        """Erreur si utilisateur non trouvé."""
        mock_oauth = Mock()
        mock_oauth.fetch_access_token.return_value = {
            "oauth_token": "token",
            "oauth_token_secret": "secret",
        }
        mock_oauth_class.return_value = mock_oauth

        mock_db = Mock()
        mock_db.get.return_value = None  # Utilisateur non trouvé
        mock_db_ctx.return_value = mock_db_context_manager(mock_db)

        service = ServiceGarmin(config=mock_config)
        service._temp_request_token = {"oauth_token": "t", "oauth_token_secret": "s"}

        with pytest.raises(ValueError, match="non trouvé"):
            service.complete_authorization(user_id=999, oauth_verifier="verifier")

    @patch("src.services.garmin.service.OAuth1Session")
    @patch("src.core.db.obtenir_contexte_db")
    def test_request_token_fourni(self, mock_db_ctx, mock_oauth_class, mock_config, mock_user):
        """Request token fourni explicitement."""
        mock_oauth = Mock()
        mock_oauth.fetch_access_token.return_value = {
            "oauth_token": "access",
            "oauth_token_secret": "secret",
        }
        mock_oauth_class.return_value = mock_oauth

        mock_db = Mock()
        mock_db.get.return_value = mock_user
        mock_db_ctx.return_value = mock_db_context_manager(mock_db)

        service = ServiceGarmin(config=mock_config)
        # Pas de _temp_request_token défini

        external_token = {"oauth_token": "ext_token", "oauth_token_secret": "ext_secret"}
        result = service.complete_authorization(
            user_id=1, oauth_verifier="verifier", request_token=external_token
        )

        assert result is True


# ═══════════════════════════════════════════════════════════
# TESTS SYNCHRONISATION
# ═══════════════════════════════════════════════════════════


class TestSyncUserData:
    """Tests pour sync_user_data."""

    @patch("src.core.db.obtenir_contexte_db")
    def test_utilisateur_non_trouve(self, mock_db_ctx, mock_config):
        """Erreur si utilisateur non trouvé."""
        mock_db = Mock()
        mock_db.get.return_value = None
        mock_db_ctx.return_value = mock_db_context_manager(mock_db)

        service = ServiceGarmin(config=mock_config)

        with pytest.raises(ValueError, match="non trouvé"):
            service.sync_user_data(user_id=999)

    @patch("src.core.db.obtenir_contexte_db")
    def test_sync_desactivee(self, mock_db_ctx, mock_config, mock_user, mock_garmin_token):
        """Retourne zéros si sync désactivée."""
        mock_garmin_token.sync_active = False
        mock_user.garmin_token = mock_garmin_token

        mock_db = Mock()
        mock_db.get.return_value = mock_user
        mock_db_ctx.return_value = mock_db_context_manager(mock_db)

        service = ServiceGarmin(config=mock_config)
        result = service.sync_user_data(user_id=1)

        assert result["activities_synced"] == 0
        assert result["summaries_synced"] == 0

    @patch("src.services.garmin.service.OAuth1Session")
    @patch("src.core.db.obtenir_contexte_db")
    def test_sync_complete(self, mock_db_ctx, mock_oauth_class, mock_config, mock_user):
        """Sync complète avec activités et résumés."""
        # Mock OAuth session
        mock_oauth = Mock()
        mock_response = Mock()
        mock_response.json.return_value = [
            {"activityId": "1", "activityType": "running", "durationInSeconds": 3600},
            {"activityId": "2", "activityType": "cycling", "durationInSeconds": 1800},
        ]
        mock_response.raise_for_status = Mock()
        mock_oauth.get.return_value = mock_response
        mock_oauth_class.return_value = mock_oauth

        # Mock DB
        mock_db = Mock()
        mock_db.get.return_value = mock_user
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        mock_db_ctx.return_value = mock_db_context_manager(mock_db)

        service = ServiceGarmin(config=mock_config)
        result = service.sync_user_data(user_id=1, days_back=7)

        assert result["activities_synced"] == 2
        assert result["summaries_synced"] == 2  # Même réponse mockée pour les 2 appels


class TestFetchActivities:
    """Tests pour _fetch_activities."""

    def test_fetch_success(self, service, mock_config):
        """Récupération réussie des activités."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = [
            {"activityId": "123", "activityType": "running"},
        ]
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response

        result = service._fetch_activities(mock_session, date(2024, 1, 1), date(2024, 1, 7))

        assert len(result) == 1
        assert result[0]["activityId"] == "123"

    def test_fetch_error(self, service):
        """Retourne liste vide en cas d'erreur."""
        mock_session = Mock()
        mock_session.get.side_effect = Exception("API Error")

        result = service._fetch_activities(mock_session, date(2024, 1, 1), date(2024, 1, 7))

        assert result == []


class TestFetchDailySummaries:
    """Tests pour _fetch_daily_summaries."""

    def test_fetch_success(self, service):
        """Récupération réussie des résumés."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = [
            {"calendarDate": "2024-01-15", "steps": 12000},
        ]
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response

        result = service._fetch_daily_summaries(mock_session, date(2024, 1, 15), date(2024, 1, 15))

        assert len(result) == 1
        assert result[0]["steps"] == 12000

    def test_fetch_error(self, service):
        """Retourne liste vide en cas d'erreur."""
        mock_session = Mock()
        mock_session.get.side_effect = Exception("API Error")

        result = service._fetch_daily_summaries(mock_session, date(2024, 1, 1), date(2024, 1, 7))

        assert result == []


class TestSaveActivity:
    """Tests pour _save_activity."""

    def test_nouvelle_activite(self, service, mock_db_session):
        """Sauvegarde d'une nouvelle activité."""
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = None

        data = {
            "activityId": "123",
            "activityType": "running",
            "activityName": "Morning Run",
            "startTimeInSeconds": 1700000000,
            "durationInSeconds": 3600,
            "distanceInMeters": 10000,
            "activeKilocalories": 500,
        }

        result = service._save_activity(mock_db_session, 1, data)

        assert result is not None
        mock_db_session.add.assert_called_once()

    def test_activite_existante(self, service, mock_db_session):
        """Activité existante retourne l'existante."""
        existing = Mock()
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = existing

        data = {"activityId": "123"}

        result = service._save_activity(mock_db_session, 1, data)

        assert result == existing
        mock_db_session.add.assert_not_called()


class TestSaveDailySummary:
    """Tests pour _save_daily_summary."""

    def test_nouveau_summary(self, service, mock_db_session):
        """Sauvegarde d'un nouveau résumé."""
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = None

        data = {
            "calendarDate": "2024-01-15",
            "steps": 12000,
            "distanceInMeters": 9500,
            "totalKilocalories": 2200,
        }

        result = service._save_daily_summary(mock_db_session, 1, data)

        assert result is not None
        mock_db_session.add.assert_called_once()

    def test_summary_existant_mise_a_jour(self, service, mock_db_session):
        """Résumé existant est mis à jour."""
        existing = Mock()
        existing.pas = 0
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = existing

        data = {
            "calendarDate": "2024-01-15",
            "steps": 15000,
        }

        result = service._save_daily_summary(mock_db_session, 1, data)

        assert result == existing
        assert existing.pas == 15000
        mock_db_session.add.assert_not_called()


# ═══════════════════════════════════════════════════════════
# TESTS HELPERS
# ═══════════════════════════════════════════════════════════


class TestDisconnectUser:
    """Tests pour disconnect_user."""

    @patch("src.core.db.obtenir_contexte_db")
    def test_disconnect_success(self, mock_db_ctx, mock_config, mock_user):
        """Déconnexion réussie."""
        mock_db = Mock()
        mock_db.get.return_value = mock_user
        mock_db_ctx.return_value = mock_db_context_manager(mock_db)

        service = ServiceGarmin(config=mock_config)
        result = service.disconnect_user(user_id=1)

        assert result is True
        assert mock_user.garmin_connected is False
        mock_db.delete.assert_called_once()

    @patch("src.core.db.obtenir_contexte_db")
    def test_disconnect_user_not_found(self, mock_db_ctx, mock_config):
        """Retourne False si utilisateur non trouvé."""
        mock_db = Mock()
        mock_db.get.return_value = None
        mock_db_ctx.return_value = mock_db_context_manager(mock_db)

        service = ServiceGarmin(config=mock_config)
        result = service.disconnect_user(user_id=999)

        assert result is False


class TestGetUserStats:
    """Tests pour get_user_stats."""

    @patch("src.core.db.obtenir_contexte_db")
    def test_user_not_found(self, mock_db_ctx, mock_config):
        """Retourne dict vide si utilisateur non trouvé."""
        mock_db = Mock()
        mock_db.get.return_value = None
        mock_db_ctx.return_value = mock_db_context_manager(mock_db)

        service = ServiceGarmin(config=mock_config)
        result = service.get_user_stats(user_id=999)

        assert result == {}

    @patch("src.core.db.obtenir_contexte_db")
    def test_stats_calculees(self, mock_db_ctx, mock_config, mock_user):
        """Stats correctement calculées."""
        # Mock des résumés quotidiens
        mock_summary1 = Mock()
        mock_summary1.pas = 10000
        mock_summary1.calories_actives = 400
        mock_summary1.distance_metres = 8000
        mock_summary1.date = date.today()

        mock_summary2 = Mock()
        mock_summary2.pas = 12000
        mock_summary2.calories_actives = 500
        mock_summary2.distance_metres = 9500
        mock_summary2.date = date.today() - timedelta(days=1)

        # Mock des activités
        mock_activity = Mock()

        mock_db = Mock()
        mock_db.get.return_value = mock_user
        mock_db.query.return_value.filter.return_value.all.return_value = [
            mock_summary1,
            mock_summary2,
        ]
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            mock_summary1
        ]
        mock_db_ctx.return_value = mock_db_context_manager(mock_db)

        service = ServiceGarmin(config=mock_config)
        result = service.get_user_stats(user_id=1, days=7)

        assert "total_pas" in result
        assert "total_calories" in result
        assert "garmin_connected" in result


class TestCalculateStreak:
    """Tests pour _calculate_streak."""

    def test_streak_calcul(self, mock_config, mock_user):
        """Calcul du streak."""
        mock_summary = Mock()
        mock_summary.pas = 12000
        mock_summary.date = date.today()

        mock_db = Mock()
        mock_db.get.return_value = mock_user
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            mock_summary
        ]

        service = ServiceGarmin(config=mock_config)
        result = service._calculate_streak(1, mock_db)

        assert result >= 0

    def test_streak_user_not_found(self, mock_config):
        """Retourne 0 si utilisateur non trouvé."""
        mock_db = Mock()
        mock_db.get.return_value = None

        service = ServiceGarmin(config=mock_config)
        result = service._calculate_streak(999, mock_db)

        assert result == 0


# ═══════════════════════════════════════════════════════════
# TESTS FACTORIES
# ═══════════════════════════════════════════════════════════


class TestFactories:
    """Tests pour les fonctions factory."""

    @patch("src.services.garmin.service.get_garmin_config")
    def test_obtenir_service_garmin(self, mock_config_fn, mock_config):
        """Factory française retourne un service."""
        mock_config_fn.return_value = mock_config

        service = obtenir_service_garmin()

        assert isinstance(service, ServiceGarmin)

    @patch("src.services.garmin.service.get_garmin_config")
    def test_get_garmin_service(self, mock_config_fn, mock_config):
        """Factory anglaise retourne un service."""
        mock_config_fn.return_value = mock_config

        service = get_garmin_service()

        assert isinstance(service, ServiceGarmin)

    @patch("src.services.garmin.service.get_garmin_config")
    def test_get_garmin_sync_service_alias(self, mock_config_fn, mock_config):
        """Alias de rétrocompatibilité fonctionne."""
        mock_config_fn.return_value = mock_config

        service = get_garmin_sync_service()

        assert isinstance(service, ServiceGarmin)


class TestGarminServiceAlias:
    """Test de l'alias GarminService."""

    def test_alias_identique(self):
        """GarminService est un alias de ServiceGarmin."""
        assert GarminService is ServiceGarmin


# ═══════════════════════════════════════════════════════════
# TESTS HELPERS UTILISATEURS
# ═══════════════════════════════════════════════════════════


class TestGetOrCreateUser:
    """Tests pour get_or_create_user."""

    @patch("src.core.db.obtenir_contexte_db")
    def test_user_existant(self, mock_db_ctx):
        """Retourne utilisateur existant."""
        existing_user = Mock()
        existing_user.username = "anne"

        mock_db = Mock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = existing_user
        mock_db_ctx.return_value = mock_db_context_manager(mock_db)

        result = get_or_create_user("anne", "Anne")

        assert result == existing_user
        mock_db.add.assert_not_called()

    @patch("src.core.db.obtenir_contexte_db")
    def test_creation_user(self, mock_db_ctx):
        """Crée un nouvel utilisateur."""
        mock_db = Mock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        mock_db_ctx.return_value = mock_db_context_manager(mock_db)

        result = get_or_create_user("newuser", "New User")

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()


class TestGetUserByUsername:
    """Tests pour get_user_by_username."""

    @patch("src.core.db.obtenir_contexte_db")
    def test_user_trouve(self, mock_db_ctx):
        """Utilisateur trouvé."""
        user = Mock()
        user.username = "testuser"

        mock_db = Mock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = user
        mock_db_ctx.return_value = mock_db_context_manager(mock_db)

        result = get_user_by_username("testuser")

        assert result == user

    @patch("src.core.db.obtenir_contexte_db")
    def test_user_non_trouve(self, mock_db_ctx):
        """Utilisateur non trouvé retourne None."""
        mock_db = Mock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        mock_db_ctx.return_value = mock_db_context_manager(mock_db)

        result = get_user_by_username("unknown")

        assert result is None


class TestListAllUsers:
    """Tests pour list_all_users."""

    @patch("src.core.db.obtenir_contexte_db")
    def test_liste_users(self, mock_db_ctx):
        """Liste tous les utilisateurs."""
        users = [Mock(), Mock()]

        mock_db = Mock()
        mock_db.query.return_value.all.return_value = users
        mock_db_ctx.return_value = mock_db_context_manager(mock_db)

        result = list_all_users()

        assert len(result) == 2


# ═══════════════════════════════════════════════════════════
# TESTS AUTHENTIFICATION ERREURS
# ═══════════════════════════════════════════════════════════


class TestAuthenticationErrors:
    """Tests pour la gestion des erreurs d'authentification."""

    @patch("src.services.garmin.service.OAuth1Session")
    def test_oauth_token_error(self, mock_oauth_class, mock_config):
        """Gère les erreurs de récupération de token."""
        mock_oauth = Mock()
        mock_oauth.fetch_request_token.side_effect = Exception("Invalid consumer key")
        mock_oauth_class.return_value = mock_oauth

        service = ServiceGarmin(config=mock_config)

        with pytest.raises(Exception, match="Invalid consumer key"):
            service.get_authorization_url()

    @patch("src.services.garmin.service.OAuth1Session")
    @patch("src.core.db.obtenir_contexte_db")
    def test_access_token_error(self, mock_db_ctx, mock_oauth_class, mock_config, mock_user):
        """Gère les erreurs de récupération d'access token."""
        mock_oauth = Mock()
        mock_oauth.fetch_access_token.side_effect = Exception("Token rejected")
        mock_oauth_class.return_value = mock_oauth

        mock_db = Mock()
        mock_db_ctx.return_value = mock_db_context_manager(mock_db)

        service = ServiceGarmin(config=mock_config)
        service._temp_request_token = {"oauth_token": "t", "oauth_token_secret": "s"}

        with pytest.raises(Exception, match="Token rejected"):
            service.complete_authorization(user_id=1, oauth_verifier="verifier")


class TestGetAuthenticatedSession:
    """Tests pour _get_authenticated_session."""

    @patch("src.services.garmin.service.OAuth1Session")
    def test_session_creation(self, mock_oauth_class, mock_config, mock_garmin_token):
        """Crée une session OAuth authentifiée."""
        mock_oauth = Mock()
        mock_oauth_class.return_value = mock_oauth

        service = ServiceGarmin(config=mock_config)
        result = service._get_authenticated_session(mock_garmin_token)

        assert result == mock_oauth
        mock_oauth_class.assert_called_once_with(
            mock_config.consumer_key,
            client_secret=mock_config.consumer_secret,
            resource_owner_key=mock_garmin_token.oauth_token,
            resource_owner_secret=mock_garmin_token.oauth_token_secret,
        )
