"""Tests pour ServiceGarmin — OAuth et configuration."""

from unittest.mock import MagicMock, patch

import pytest

from src.services.integrations.garmin.service import ServiceGarmin, get_garmin_config
from src.services.integrations.garmin.types import GarminConfig


class TestGetGarminConfig:
    def test_retourne_config_depuis_settings(self):
        with patch("src.services.integrations.garmin.service.obtenir_parametres") as mock_settings:
            mock_settings.return_value.GARMIN_CONSUMER_KEY = "key"
            mock_settings.return_value.GARMIN_CONSUMER_SECRET = "secret"

            config = get_garmin_config()

        assert config.consumer_key == "key"
        assert config.consumer_secret == "secret"


class TestServiceGarminAuth:
    def test_get_authorization_url_erreur_si_cles_absentes(self):
        service = ServiceGarmin(config=GarminConfig(consumer_key="", consumer_secret=""))

        url, token = service.get_authorization_url()
        # avec_resilience fallback=(None, None)
        assert url is None
        assert token is None

    @patch("src.services.integrations.garmin.service.OAuth1Session")
    def test_get_authorization_url_succes(self, mock_oauth_cls):
        service = ServiceGarmin(config=GarminConfig(consumer_key="key", consumer_secret="secret"))

        mock_oauth = MagicMock()
        mock_oauth.fetch_request_token.return_value = {
            "oauth_token": "temp_token",
            "oauth_token_secret": "temp_secret",
        }
        mock_oauth.authorization_url.return_value = "https://garmin.com/authorize"
        mock_oauth_cls.return_value = mock_oauth

        url, token = service.get_authorization_url()

        assert url == "https://garmin.com/authorize"
        assert token["oauth_token"] == "temp_token"
        assert service._temp_request_token is not None

    def test_complete_authorization_erreur_si_request_token_manquant(self):
        service = ServiceGarmin(config=GarminConfig(consumer_key="key", consumer_secret="secret"))

        # avec_resilience fallback=False
        result = service.complete_authorization(user_id=1, oauth_verifier="abc", request_token=None, db=None)
        assert result is False
