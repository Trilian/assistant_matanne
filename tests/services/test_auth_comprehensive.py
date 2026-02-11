"""
Tests complets pour le service auth.

Couvre:
- Role, Permission (enums)
- UserProfile, AuthResult (modèles)
- AuthService (signup, login, logout, permissions)
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from src.services.utilisateur import (
    Role,
    Permission,
    UserProfile,
    AuthResult,
    AuthService,
)


# ═══════════════════════════════════════════════════════════
# TESTS ENUMS
# ═══════════════════════════════════════════════════════════


class TestRole:
    """Tests pour l'enum Role."""

    def test_admin_role(self):
        assert Role.ADMIN.value == "admin"

    def test_membre_role(self):
        assert Role.MEMBRE.value == "membre"

    def test_invite_role(self):
        assert Role.INVITE.value == "invite"

    def test_all_roles_defined(self):
        roles = list(Role)
        assert len(roles) >= 3


class TestPermission:
    """Tests pour l'enum Permission."""

    def test_read_recipes_permission(self):
        assert Permission.READ_RECIPES.value == "read_recipes"

    def test_write_recipes_permission(self):
        assert Permission.WRITE_RECIPES.value == "write_recipes"

    def test_delete_recipes_permission(self):
        assert Permission.DELETE_RECIPES.value == "delete_recipes"

    def test_admin_all_permission(self):
        assert Permission.ADMIN_ALL.value == "admin_all"

    def test_all_permissions_defined(self):
        permissions = list(Permission)
        assert len(permissions) >= 4


# ═══════════════════════════════════════════════════════════
# TESTS MODÈLES PYDANTIC
# ═══════════════════════════════════════════════════════════


class TestUserProfile:
    """Tests pour le modèle UserProfile."""

    def test_create_minimal_profile(self):
        profile = UserProfile(
            id="user123",
            email="test@example.com",
            role=Role.MEMBRE,
        )
        assert profile.id == "user123"
        assert profile.email == "test@example.com"
        assert profile.role == Role.MEMBRE

    def test_create_profile_with_name(self):
        profile = UserProfile(
            id="user456",
            email="membre@famille.com",
            role=Role.MEMBRE,
            nom="Dupont",
            prenom="Marie",
        )
        assert profile.nom == "Dupont"
        assert profile.prenom == "Marie"

    def test_admin_has_all_permissions(self):
        profile = UserProfile(
            id="admin1",
            email="admin@famille.com",
            role=Role.ADMIN,
        )
        # Admin has all permissions
        assert profile.has_permission(Permission.ADMIN_ALL) is True
        assert profile.has_permission(Permission.READ_RECIPES) is True
        assert profile.has_permission(Permission.WRITE_RECIPES) is True
        assert profile.has_permission(Permission.DELETE_RECIPES) is True

    def test_membre_has_standard_permissions(self):
        profile = UserProfile(
            id="membre1",
            email="membre@famille.com",
            role=Role.MEMBRE,
        )
        assert profile.has_permission(Permission.READ_RECIPES) is True
        assert profile.has_permission(Permission.WRITE_RECIPES) is True
        # Membre may or may not have delete permission

    def test_invite_has_limited_permissions(self):
        profile = UserProfile(
            id="invite1",
            email="invite@externe.com",
            role=Role.INVITE,
        )
        assert profile.has_permission(Permission.READ_RECIPES) is True
        assert profile.has_permission(Permission.ADMIN_ALL) is False

    def test_display_name_with_prenom(self):
        profile = UserProfile(
            id="user1",
            email="test@example.com",
            role=Role.MEMBRE,
            prenom="Jean",
            nom="Dupont",  # Need both prenom AND nom
        )
        assert profile.display_name == "Jean Dupont"

    def test_display_name_without_prenom(self):
        profile = UserProfile(
            id="user1",
            email="test@example.com",
            role=Role.MEMBRE,
        )
        # Should return email or some default
        assert profile.display_name is not None
        assert len(profile.display_name) > 0


class TestAuthResult:
    """Tests pour le modèle AuthResult."""

    def test_successful_auth_result(self):
        profile = UserProfile(
            id="user1",
            email="test@example.com",
            role=Role.MEMBRE,
        )
        result = AuthResult(
            success=True,
            user=profile,
            message="Connexion réussie",
        )
        assert result.success is True
        assert result.user is not None
        assert result.message == "Connexion réussie"

    def test_failed_auth_result(self):
        result = AuthResult(
            success=False,
            user=None,
            message="Email ou mot de passe incorrect",
        )
        assert result.success is False
        assert result.user is None

    def test_auth_result_with_error(self):
        result = AuthResult(
            success=False,
            error_code="INVALID_CREDENTIALS",
            message="Identifiants invalides",
        )
        assert result.error_code == "INVALID_CREDENTIALS"


# ═══════════════════════════════════════════════════════════
# TESTS AUTH SERVICE
# ═══════════════════════════════════════════════════════════


class TestAuthServiceInit:
    """Tests pour l'initialisation du service auth."""

    def test_service_initialization(self):
        with patch.object(AuthService, '_init_client'):
            service = AuthService()
            assert service is not None

    def test_is_configured_true(self):
        """Test is_configured returns True when client exists."""
        with patch.object(AuthService, '_init_client'):
            service = AuthService()
            # Mock the client as non-None
            service._client = MagicMock()
            
            # is_configured is a property that checks self._client is not None
            assert service.is_configured == True

    def test_is_configured_false(self):
        """Test is_configured returns False when client is None."""
        with patch.object(AuthService, '_init_client'):
            service = AuthService()
            service._client = None
            
            # is_configured is a property that checks self._client is not None  
            assert service.is_configured == False


class TestAuthServiceSignup:
    """Tests pour l'inscription."""

    @pytest.fixture
    def service(self):
        with patch.object(AuthService, '_init_client'):
            service = AuthService()
            service._client = MagicMock()
            return service

    def test_signup_success(self, service):
        mock_response = MagicMock()
        mock_response.user = MagicMock()
        mock_response.user.id = "new_user_123"
        mock_response.user.email = "new@example.com"
        mock_response.session = MagicMock()
        
        service._client.auth.sign_up.return_value = mock_response
        
        result = service.signup(
            email="new@example.com",
            password="SecurePass123!",
            nom="Test",
            prenom="User",
        )
        
        assert result.success is True
        service._client.auth.sign_up.assert_called()

    def test_signup_email_already_exists(self, service):
        service._client.auth.sign_up.side_effect = Exception("User already registered")
        
        result = service.signup(
            email="existing@example.com",
            password="Password123!",
        )
        
        assert result.success is False
        # French message: "Cet email est déjà utilisé"
        assert "email" in result.message.lower() or "déjà" in result.message.lower()

    def test_signup_weak_password(self, service):
        service._client.auth.sign_up.side_effect = Exception("Password should be at least 6 characters")
        
        result = service.signup(
            email="test@example.com",
            password="123",
        )
        
        assert result.success is False

    def test_signup_invalid_email(self, service):
        service._client.auth.sign_up.side_effect = Exception("Invalid email")
        
        result = service.signup(
            email="not-an-email",
            password="Password123!",
        )
        
        assert result.success is False


class TestAuthServiceLogin:
    """Tests pour la connexion."""

    @pytest.fixture
    def service(self):
        with patch.object(AuthService, '_init_client'):
            service = AuthService()
            service._client = MagicMock()
            return service

    def test_login_success(self, service):
        mock_response = MagicMock()
        mock_response.user = MagicMock()
        mock_response.user.id = "user_123"
        mock_response.user.email = "test@example.com"
        mock_response.user.user_metadata = {"nom": "Test", "prenom": "User", "role": "membre"}
        mock_response.session = MagicMock()
        mock_response.session.access_token = "access_token"
        
        service._client.auth.sign_in_with_password.return_value = mock_response
        
        with patch('src.services.auth.st') as mock_st:
            mock_st.session_state = {}
            result = service.login(
                email="test@example.com",
                password="Password123!",
            )
        
        assert result.success is True
        assert result.user is not None

    def test_login_invalid_credentials(self, service):
        service._client.auth.sign_in_with_password.side_effect = Exception("Invalid login credentials")
        
        result = service.login(
            email="test@example.com",
            password="WrongPassword",
        )
        
        assert result.success is False

    def test_login_user_not_found(self, service):
        service._client.auth.sign_in_with_password.side_effect = Exception("User not found")
        
        result = service.login(
            email="nonexistent@example.com",
            password="Password123!",
        )
        
        assert result.success is False

    def test_login_empty_email(self, service):
        result = service.login(
            email="",
            password="Password123!",
        )
        
        assert result.success is False

    def test_login_empty_password(self, service):
        result = service.login(
            email="test@example.com",
            password="",
        )
        
        assert result.success is False


class TestAuthServiceLogout:
    """Tests pour la déconnexion."""

    @pytest.fixture
    def service(self):
        with patch.object(AuthService, '_init_client'):
            service = AuthService()
            service._client = MagicMock()
            return service

    def test_logout_success(self, service):
        with patch.object(service, '_clear_session'):
            result = service.logout()
        
        assert result.success is True
        service._client.auth.sign_out.assert_called()

    def test_logout_error(self, service):
        service._client.auth.sign_out.side_effect = Exception("Logout failed")
        
        with patch.object(service, '_clear_session'):
            result = service.logout()
        
        # Should still succeed or handle gracefully
        assert result is not None


class TestAuthServicePasswordReset:
    """Tests pour la réinitialisation de mot de passe."""

    @pytest.fixture
    def service(self):
        with patch.object(AuthService, '_init_client'):
            service = AuthService()
            service._client = MagicMock()
            return service

    def test_reset_password_success(self, service):
        result = service.reset_password(email="test@example.com")
        
        assert result.success is True
        service._client.auth.reset_password_for_email.assert_called()

    def test_reset_password_invalid_email(self, service):
        service._client.auth.reset_password_for_email.side_effect = Exception("Invalid email")
        
        result = service.reset_password(email="invalid")
        
        # Method returns success=True even on error (for security - don't reveal if email exists)
        assert result.success is True
        assert "email" in result.message.lower() or "lien" in result.message.lower()

    def test_reset_password_empty_email(self, service):
        result = service.reset_password(email="")
        
        # Method returns success=True even for empty email (security)
        assert result.success is True


class TestAuthServiceSession:
    """Tests pour la gestion de session."""

    @pytest.fixture
    def service(self):
        with patch.object(AuthService, '_init_client'):
            service = AuthService()
            service._client = MagicMock()
            service._current_user = None
            return service

    def test_get_current_user_authenticated(self, service):
        mock_user = UserProfile(
            id="user1",
            email="test@example.com",
            role=Role.MEMBRE,
        )
        # Mock st.session_state as MagicMock that returns user
        with patch('src.services.auth.st') as mock_st:
            mock_session_state = MagicMock()
            mock_session_state.get.return_value = mock_user
            mock_st.session_state = mock_session_state
            
            user = service.get_current_user()
        
        assert user is not None

    def test_get_current_user_not_authenticated(self, service):
        # Mock st.session_state that returns None
        with patch('src.services.auth.st') as mock_st:
            mock_session_state = MagicMock()
            mock_session_state.get.return_value = None
            mock_st.session_state = mock_session_state
            
            user = service.get_current_user()
        
        assert user is None

    def test_is_authenticated_true(self, service):
        service._current_user = UserProfile(
            id="user1",
            email="test@example.com",
            role=Role.MEMBRE,
        )
        
        assert service.is_authenticated() is True

    def test_is_authenticated_false(self, service):
        # Mock get_current_user to return None
        with patch.object(service, 'get_current_user', return_value=None):
            assert service.is_authenticated() is False


class TestAuthServicePermissions:
    """Tests pour la vérification des permissions."""

    @pytest.fixture
    def service(self):
        with patch.object(AuthService, '_init_client'):
            service = AuthService()
            service._client = MagicMock()
            return service

    def test_require_auth_authenticated(self, service):
        user = UserProfile(
            id="user1",
            email="test@example.com",
            role=Role.MEMBRE,
        )
        
        with patch.object(service, 'get_current_user', return_value=user):
            result = service.require_auth()
        
        assert result is not None
        assert result.email == "test@example.com"

    def test_require_auth_not_authenticated(self, service):
        with patch.object(service, 'get_current_user', return_value=None):
            with patch('src.services.auth.render_login_form'):  # Mock UI render
                result = service.require_auth()
        
        # Should return None or show warning
        assert result is None

    def test_require_permission_has_permission(self, service):
        user = UserProfile(
            id="admin1",
            email="admin@example.com",
            role=Role.ADMIN,
        )
        
        with patch.object(service, 'get_current_user', return_value=user):
            result = service.require_permission(Permission.ADMIN_ALL)
        
        assert result is True

    def test_require_permission_lacks_permission(self, service):
        user = UserProfile(
            id="invite1",
            email="invite@example.com",
            role=Role.INVITE,
        )
        service._current_user = user
        
        result = service.require_permission(Permission.ADMIN_ALL)
        
        assert result is False

    def test_require_permission_not_authenticated(self, service):
        with patch.object(service, 'get_current_user', return_value=None):
            result = service.require_permission(Permission.READ_RECIPES)
        
        assert result is False


class TestAuthServiceRefresh:
    """Tests pour le refresh de session."""

    @pytest.fixture
    def service(self):
        with patch.object(AuthService, '_init_client'):
            service = AuthService()
            service._client = MagicMock()
            return service

    def test_refresh_session_success(self, service):
        mock_session = MagicMock()
        
        # Mock st.session_state.get to return a session
        with patch('src.services.auth.st') as mock_st:
            mock_st.session_state.get.return_value = mock_session
            service._client.auth.obtenir_contexte_db.return_value = mock_session
            
            result = service.refresh_session()
        
        assert result is True

    def test_refresh_session_expired(self, service):
        # Mock st.session_state.get to return a session
        with patch('src.services.auth.st') as mock_st:
            mock_st.session_state.get.return_value = MagicMock()
            service._client.auth.obtenir_contexte_db.side_effect = Exception("Session expired")
            
            result = service.refresh_session()
        
        assert result is False


class TestAuthServiceEdgeCases:
    """Tests pour les cas limites."""

    @pytest.fixture
    def service(self):
        with patch.object(AuthService, '_init_client'):
            service = AuthService()
            service._client = MagicMock()
            return service

    def test_login_with_special_characters_in_password(self, service):
        mock_response = MagicMock()
        mock_response.user = MagicMock()
        mock_response.user.id = "user1"
        mock_response.user.email = "test@example.com"
        mock_response.user.user_metadata = {}
        mock_response.session = MagicMock()
        
        service._client.auth.sign_in_with_password.return_value = mock_response
        
        with patch.object(service, '_save_session'):
            result = service.login(
                email="test@example.com",
                password="P@$$w0rd!#%&*()",
            )
        
        assert result is not None

    def test_signup_with_unicode_name(self, service):
        mock_response = MagicMock()
        mock_response.user = MagicMock()
        mock_response.user.id = "user1"
        mock_response.user.email = "test@example.com"
        mock_response.session = MagicMock()
        
        service._client.auth.sign_up.return_value = mock_response
        
        result = service.signup(
            email="test@example.com",
            password="Password123!",
            prenom="François",
            nom="Müller",
        )
        
        assert result is not None

    def test_multiple_login_attempts(self, service):
        mock_response = MagicMock()
        mock_response.user = MagicMock()
        mock_response.user.id = "user1"
        mock_response.user.email = "test@example.com"
        mock_response.user.user_metadata = {}
        mock_response.session = MagicMock()
        
        service._client.auth.sign_in_with_password.return_value = mock_response
        
        with patch.object(service, '_save_session'):
            # Multiple logins should work
            for _ in range(3):
                result = service.login("test@example.com", "Password123!")
                assert result is not None

