"""
Tests pour le module d'authentification JWT autonome (src/api/auth.py).

Vérifie:
- Génération de tokens API
- Validation de tokens API (valides, expirés, corrompus)
- Validation de tokens Supabase (avec/sans signature)
- Fonction unifiée valider_token (API puis Supabase)
"""

import time
from datetime import UTC, datetime, timedelta, timezone
from unittest.mock import patch

import jwt
import pytest

from src.api.auth import (
    ALGORITHME,
    UtilisateurToken,
    _extraire_utilisateur_supabase,
    _obtenir_api_secret,
    creer_token_acces,
    valider_token,
    valider_token_api,
    valider_token_supabase,
)

# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def api_secret():
    """Secret de test fixe."""
    return "test-secret-key-for-unit-tests"


@pytest.fixture
def token_valide(api_secret):
    """Token API valide signé."""
    with patch("src.api.auth._obtenir_api_secret", return_value=api_secret):
        return creer_token_acces(
            user_id="user-123",
            email="test@example.com",
            role="admin",
        )


@pytest.fixture
def token_expire(api_secret):
    """Token API expiré."""
    payload = {
        "sub": "user-expired",
        "email": "expired@example.com",
        "role": "membre",
        "iat": datetime.now(UTC) - timedelta(hours=48),
        "exp": datetime.now(UTC) - timedelta(hours=1),
        "iss": "assistant-matanne-api",
    }
    return jwt.encode(payload, api_secret, algorithm=ALGORITHME)


@pytest.fixture
def token_supabase():
    """Token Supabase simulé (sans signature vérifiable)."""
    payload = {
        "sub": "supa-user-456",
        "email": "supa@supabase.io",
        "role": "authenticated",
        "user_metadata": {"role": "admin", "nom": "Dupont"},
        "app_metadata": {},
        "aud": "authenticated",
        "iat": datetime.now(UTC),
        "exp": datetime.now(UTC) + timedelta(hours=1),
    }
    return jwt.encode(payload, "supabase-jwt-secret-test", algorithm=ALGORITHME)


@pytest.fixture
def token_supabase_expire():
    """Token Supabase expiré."""
    payload = {
        "sub": "supa-expired",
        "email": "expired@supabase.io",
        "role": "authenticated",
        "aud": "authenticated",
        "iat": datetime.now(UTC) - timedelta(hours=48),
        "exp": datetime.now(UTC) - timedelta(hours=1),
    }
    return jwt.encode(payload, "supabase-jwt-secret-test", algorithm=ALGORITHME)


# ═══════════════════════════════════════════════════════════
# TESTS: GÉNÉRATION DE TOKENS
# ═══════════════════════════════════════════════════════════


class TestCreerTokenAcces:
    """Tests pour la génération de tokens JWT API."""

    def test_genere_token_valide(self, api_secret):
        """Le token généré est décodable et contient les bonnes infos."""
        with patch("src.api.auth._obtenir_api_secret", return_value=api_secret):
            token = creer_token_acces("user-1", "test@mail.com", "admin")

        payload = jwt.decode(token, api_secret, algorithms=[ALGORITHME])
        assert payload["sub"] == "user-1"
        assert payload["email"] == "test@mail.com"
        assert payload["role"] == "admin"
        assert payload["iss"] == "assistant-matanne-api"
        assert "exp" in payload
        assert "iat" in payload

    def test_role_defaut_membre(self, api_secret):
        """Le rôle par défaut est 'membre'."""
        with patch("src.api.auth._obtenir_api_secret", return_value=api_secret):
            token = creer_token_acces("user-1", "test@mail.com")

        payload = jwt.decode(token, api_secret, algorithms=[ALGORITHME])
        assert payload["role"] == "membre"

    def test_duree_personnalisee(self, api_secret):
        """La durée de validité est configurable."""
        with patch("src.api.auth._obtenir_api_secret", return_value=api_secret):
            token = creer_token_acces("user-1", "a@b.com", duree_heures=1)

        payload = jwt.decode(token, api_secret, algorithms=[ALGORITHME])
        exp = datetime.fromtimestamp(payload["exp"], tz=UTC)
        iat = datetime.fromtimestamp(payload["iat"], tz=UTC)
        delta = exp - iat
        assert 3500 < delta.total_seconds() < 3700  # ~1 heure

    def test_retourne_string(self, api_secret):
        """Le token est une chaîne de caractères."""
        with patch("src.api.auth._obtenir_api_secret", return_value=api_secret):
            token = creer_token_acces("u1", "e@e.com")
        assert isinstance(token, str)
        assert len(token) > 50
        assert token.count(".") == 2  # format JWT: header.payload.signature


# ═══════════════════════════════════════════════════════════
# TESTS: VALIDATION TOKEN API
# ═══════════════════════════════════════════════════════════


class TestValiderTokenApi:
    """Tests pour la validation de tokens API."""

    def test_token_valide(self, api_secret, token_valide):
        """Un token valide retourne l'utilisateur."""
        with patch("src.api.auth._obtenir_api_secret", return_value=api_secret):
            result = valider_token_api(token_valide)

        assert result is not None
        assert isinstance(result, UtilisateurToken)
        assert result.id == "user-123"
        assert result.email == "test@example.com"
        assert result.role == "admin"

    def test_token_expire(self, api_secret, token_expire):
        """Un token expiré retourne None."""
        with patch("src.api.auth._obtenir_api_secret", return_value=api_secret):
            result = valider_token_api(token_expire)
        assert result is None

    def test_token_mauvaise_signature(self, api_secret, token_valide):
        """Un token avec mauvaise clé retourne None."""
        with patch("src.api.auth._obtenir_api_secret", return_value="wrong-key"):
            result = valider_token_api(token_valide)
        assert result is None

    def test_token_corrompu(self, api_secret):
        """Un token corrompu retourne None."""
        with patch("src.api.auth._obtenir_api_secret", return_value=api_secret):
            result = valider_token_api("not.a.valid.jwt.token")
        assert result is None

    def test_token_vide(self, api_secret):
        """Un token vide retourne None."""
        with patch("src.api.auth._obtenir_api_secret", return_value=api_secret):
            result = valider_token_api("")
        assert result is None

    def test_mauvais_issuer(self, api_secret):
        """Un token avec un mauvais issuer est rejeté."""
        payload = {
            "sub": "user-1",
            "email": "a@b.com",
            "role": "membre",
            "iat": datetime.now(UTC),
            "exp": datetime.now(UTC) + timedelta(hours=1),
            "iss": "autre-api",
        }
        token = jwt.encode(payload, api_secret, algorithm=ALGORITHME)
        with patch("src.api.auth._obtenir_api_secret", return_value=api_secret):
            result = valider_token_api(token)
        assert result is None


# ═══════════════════════════════════════════════════════════
# TESTS: VALIDATION TOKEN SUPABASE
# ═══════════════════════════════════════════════════════════


class TestValiderTokenSupabase:
    """Tests pour la validation de tokens Supabase."""

    def test_avec_signature_valide(self, token_supabase):
        """Un token Supabase avec bonne signature est validé."""
        with patch(
            "src.api.auth._obtenir_supabase_jwt_secret",
            return_value="supabase-jwt-secret-test",
        ):
            result = valider_token_supabase(token_supabase)

        assert result is not None
        assert result.id == "supa-user-456"
        assert result.email == "supa@supabase.io"
        assert result.role == "admin"

    def test_avec_mauvaise_signature(self, token_supabase):
        """Un token Supabase avec mauvaise signature est rejeté."""
        with patch(
            "src.api.auth._obtenir_supabase_jwt_secret",
            return_value="wrong-secret",
        ):
            result = valider_token_supabase(token_supabase)
        assert result is None

    def test_sans_signature_valide(self, token_supabase):
        """Sans secret configuré, le token est décodé sans vérification."""
        with patch("src.api.auth._obtenir_supabase_jwt_secret", return_value=None):
            result = valider_token_supabase(token_supabase)

        assert result is not None
        assert result.id == "supa-user-456"
        assert result.email == "supa@supabase.io"

    def test_sans_signature_expire(self, token_supabase_expire):
        """Un token expiré est rejeté même sans vérification de signature."""
        with patch("src.api.auth._obtenir_supabase_jwt_secret", return_value=None):
            result = valider_token_supabase(token_supabase_expire)
        assert result is None


# ═══════════════════════════════════════════════════════════
# TESTS: EXTRACTION UTILISATEUR SUPABASE
# ═══════════════════════════════════════════════════════════


class TestExtraireUtilisateurSupabase:
    """Tests pour l'extraction des infos utilisateur depuis un payload Supabase."""

    def test_extraction_basique(self):
        """Extrait sub, email, role du payload."""
        payload = {
            "sub": "abc-123",
            "email": "user@test.com",
            "role": "authenticated",
            "user_metadata": {"role": "admin"},
        }
        result = _extraire_utilisateur_supabase(payload)
        assert result.id == "abc-123"
        assert result.email == "user@test.com"
        assert result.role == "admin"

    def test_role_depuis_app_metadata(self):
        """Le rôle peut venir de app_metadata si absent de user_metadata."""
        payload = {
            "sub": "abc",
            "email": "u@t.com",
            "user_metadata": {},
            "app_metadata": {"role": "invite"},
        }
        result = _extraire_utilisateur_supabase(payload)
        assert result.role == "invite"

    def test_role_fallback(self):
        """Sans metadata, utilise le role du payload principal."""
        payload = {"sub": "abc", "email": "u@t.com", "role": "custom_role"}
        result = _extraire_utilisateur_supabase(payload)
        assert result.role == "custom_role"

    def test_valeurs_par_defaut(self):
        """Les champs manquants ont des valeurs par défaut."""
        result = _extraire_utilisateur_supabase({})
        assert result.id == "unknown"
        assert result.email == ""
        assert result.role == "membre"


# ═══════════════════════════════════════════════════════════
# TESTS: FONCTION UNIFIÉE valider_token
# ═══════════════════════════════════════════════════════════


class TestValiderToken:
    """Tests pour la fonction unifiée de validation."""

    def test_token_api_prioritaire(self, api_secret, token_valide):
        """Les tokens API sont validés en priorité."""
        with patch("src.api.auth._obtenir_api_secret", return_value=api_secret):
            result = valider_token(token_valide)

        assert result is not None
        assert result.id == "user-123"

    def test_fallback_supabase(self, token_supabase):
        """Si le token n'est pas API, essaie Supabase."""
        with (
            patch(
                "src.api.auth._obtenir_api_secret",
                return_value="different-key",
            ),
            patch(
                "src.api.auth._obtenir_supabase_jwt_secret",
                return_value="supabase-jwt-secret-test",
            ),
        ):
            result = valider_token(token_supabase)

        assert result is not None
        assert result.id == "supa-user-456"

    def test_token_invalide_partout(self, api_secret):
        """Un token invalide pour les deux systèmes retourne None."""
        with (
            patch("src.api.auth._obtenir_api_secret", return_value=api_secret),
            patch("src.api.auth._obtenir_supabase_jwt_secret", return_value=None),
        ):
            result = valider_token("garbage.token.here")
        assert result is None

    def test_token_non_string(self, api_secret):
        """Un token mal formé retourne None."""
        with (
            patch("src.api.auth._obtenir_api_secret", return_value=api_secret),
            patch("src.api.auth._obtenir_supabase_jwt_secret", return_value=None),
        ):
            result = valider_token("")
        assert result is None


# ═══════════════════════════════════════════════════════════
# TESTS: SCHÉMA UtilisateurToken
# ═══════════════════════════════════════════════════════════


class TestUtilisateurToken:
    """Tests pour le modèle UtilisateurToken."""

    def test_creation_complete(self):
        """Création avec tous les champs."""
        u = UtilisateurToken(id="1", email="a@b.com", role="admin")
        assert u.id == "1"
        assert u.email == "a@b.com"
        assert u.role == "admin"

    def test_role_par_defaut(self):
        """Le rôle par défaut est 'membre'."""
        u = UtilisateurToken(id="1", email="a@b.com")
        assert u.role == "membre"


# ═══════════════════════════════════════════════════════════
# TESTS: CONFIGURATION
# ═══════════════════════════════════════════════════════════


class TestConfiguration:
    """Tests pour les fonctions de configuration."""

    def test_api_secret_depuis_env(self):
        """La clé API est lue depuis la variable d'environnement."""
        with patch.dict("os.environ", {"API_SECRET_KEY": "my-secret"}):
            assert _obtenir_api_secret() == "my-secret"

    def test_api_secret_defaut(self):
        """Sans variable d'environnement, utilise une clé aléatoire générée."""
        with patch.dict("os.environ", {}, clear=True):
            secret = _obtenir_api_secret()
            # A2: la clé par défaut est maintenant aléatoire (64 bytes base64)
            assert len(secret) >= 40
            assert secret != "dev-secret-key-change-in-production"
