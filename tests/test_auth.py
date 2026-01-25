"""
Tests pour le service d'authentification.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.services.auth import (
    AuthService,
    UserProfile,
    AuthResult,
    Role,
    Permission,
    ROLE_PERMISSIONS,
    get_auth_service,
    require_authenticated,
    require_role,
)


# ═══════════════════════════════════════════════════════════
# TESTS USERPROFILE
# ═══════════════════════════════════════════════════════════


class TestUserProfile:
    """Tests pour le modèle UserProfile."""
    
    def test_create_profile(self):
        """Test création d'un profil utilisateur."""
        profile = UserProfile(
            id="123",
            email="test@example.com",
            nom="Dupont",
            prenom="Jean",
            role=Role.MEMBRE,
        )
        
        assert profile.id == "123"
        assert profile.email == "test@example.com"
        assert profile.nom == "Dupont"
        assert profile.prenom == "Jean"
        assert profile.role == Role.MEMBRE
    
    def test_display_name_with_names(self):
        """Test nom d'affichage avec prénom et nom."""
        profile = UserProfile(
            email="test@example.com",
            nom="Dupont",
            prenom="Jean",
        )
        
        assert profile.display_name == "Jean Dupont"
    
    def test_display_name_without_names(self):
        """Test nom d'affichage sans prénom/nom."""
        profile = UserProfile(email="jean.dupont@example.com")
        
        assert profile.display_name == "jean.dupont"
    
    def test_display_name_empty(self):
        """Test nom d'affichage sans email."""
        profile = UserProfile()
        
        assert profile.display_name == "Utilisateur"
    
    def test_has_permission_membre(self):
        """Test permissions pour un membre."""
        profile = UserProfile(role=Role.MEMBRE)
        
        assert profile.has_permission(Permission.READ_RECIPES)
        assert profile.has_permission(Permission.WRITE_RECIPES)
        assert not profile.has_permission(Permission.MANAGE_USERS)
        assert not profile.has_permission(Permission.ADMIN_ALL)
    
    def test_has_permission_admin(self):
        """Test permissions pour un admin."""
        profile = UserProfile(role=Role.ADMIN)
        
        assert profile.has_permission(Permission.READ_RECIPES)
        assert profile.has_permission(Permission.MANAGE_USERS)
        assert profile.has_permission(Permission.ADMIN_ALL)
    
    def test_has_permission_invite(self):
        """Test permissions pour un invité."""
        profile = UserProfile(role=Role.INVITE)
        
        assert profile.has_permission(Permission.READ_RECIPES)
        assert not profile.has_permission(Permission.WRITE_RECIPES)
        assert not profile.has_permission(Permission.MANAGE_USERS)


# ═══════════════════════════════════════════════════════════
# TESTS ROLE_PERMISSIONS
# ═══════════════════════════════════════════════════════════


class TestRolePermissions:
    """Tests pour la configuration des permissions."""
    
    def test_admin_has_all_permissions(self):
        """L'admin a toutes les permissions."""
        admin_perms = ROLE_PERMISSIONS[Role.ADMIN]
        
        for perm in Permission:
            assert perm in admin_perms
    
    def test_invite_has_read_only(self):
        """L'invité a seulement les permissions de lecture."""
        invite_perms = ROLE_PERMISSIONS[Role.INVITE]
        
        for perm in invite_perms:
            assert "READ" in perm.value.upper()
    
    def test_membre_can_write(self):
        """Le membre peut écrire."""
        membre_perms = ROLE_PERMISSIONS[Role.MEMBRE]
        
        assert Permission.WRITE_RECIPES in membre_perms
        assert Permission.WRITE_INVENTORY in membre_perms


# ═══════════════════════════════════════════════════════════
# TESTS AUTHRESULT
# ═══════════════════════════════════════════════════════════


class TestAuthResult:
    """Tests pour le modèle AuthResult."""
    
    def test_success_result(self):
        """Test résultat de succès."""
        user = UserProfile(email="test@example.com")
        result = AuthResult(
            success=True,
            user=user,
            message="OK"
        )
        
        assert result.success
        assert result.user == user
        assert result.message == "OK"
    
    def test_error_result(self):
        """Test résultat d'erreur."""
        result = AuthResult(
            success=False,
            message="Erreur",
            error_code="INVALID_CREDENTIALS"
        )
        
        assert not result.success
        assert result.user is None
        assert result.error_code == "INVALID_CREDENTIALS"


# ═══════════════════════════════════════════════════════════
# TESTS AUTHSERVICE
# ═══════════════════════════════════════════════════════════


class TestAuthService:
    """Tests pour le service d'authentification."""
    
    def test_init_without_supabase(self):
        """Test initialisation sans Supabase configuré."""
        with patch.dict('sys.modules', {'supabase': None}):
            service = AuthService()
            assert not service.is_configured
    
    def test_signup_not_configured(self):
        """Test inscription quand non configuré."""
        service = AuthService()
        service._client = None
        
        result = service.signup("test@example.com", "password123")
        
        assert not result.success
        assert result.error_code == "NOT_CONFIGURED"
    
    def test_login_not_configured(self):
        """Test connexion quand non configuré."""
        service = AuthService()
        service._client = None
        
        result = service.login("test@example.com", "password123")
        
        assert not result.success
        assert result.error_code == "NOT_CONFIGURED"
    
    def test_logout_always_succeeds(self):
        """Test déconnexion réussit toujours."""
        service = AuthService()
        service._client = None
        
        result = service.logout()
        
        assert result.success
    
    def test_reset_password_not_configured(self):
        """Test reset password quand non configuré."""
        service = AuthService()
        service._client = None
        
        result = service.reset_password("test@example.com")
        
        assert not result.success
        assert result.error_code == "NOT_CONFIGURED"
    
    @patch('streamlit.session_state', {})
    def test_get_current_user_not_logged_in(self):
        """Test utilisateur courant non connecté."""
        service = AuthService()
        
        user = service.get_current_user()
        
        assert user is None
    
    @patch('streamlit.session_state')
    def test_get_current_user_logged_in(self, mock_state):
        """Test utilisateur courant connecté."""
        user = UserProfile(email="test@example.com")
        mock_state.get.return_value = user
        
        service = AuthService()
        result = service.get_current_user()
        
        assert result == user
    
    @patch('streamlit.session_state', {})
    def test_is_authenticated_false(self):
        """Test non authentifié."""
        service = AuthService()
        
        assert not service.is_authenticated()
    
    def test_factory_singleton(self):
        """Test que la factory retourne le même service."""
        import src.services.auth as auth_module
        
        # Reset le singleton
        auth_module._auth_service = None
        
        service1 = get_auth_service()
        service2 = get_auth_service()
        
        assert service1 is service2


# ═══════════════════════════════════════════════════════════
# TESTS AVEC MOCK SUPABASE
# ═══════════════════════════════════════════════════════════


class TestAuthServiceWithMockSupabase:
    """Tests avec Supabase mocké."""
    
    @pytest.fixture
    def mock_supabase_client(self):
        """Fixture pour un client Supabase mocké."""
        client = Mock()
        client.auth = Mock()
        return client
    
    @pytest.fixture
    def auth_service(self, mock_supabase_client):
        """Fixture pour le service avec Supabase mocké."""
        service = AuthService()
        service._client = mock_supabase_client
        return service
    
    def test_signup_success(self, auth_service, mock_supabase_client):
        """Test inscription réussie."""
        # Mock la réponse Supabase
        mock_user = Mock()
        mock_user.id = "123"
        mock_user.user_metadata = {}
        
        mock_response = Mock()
        mock_response.user = mock_user
        mock_response.session = Mock()
        
        mock_supabase_client.auth.sign_up.return_value = mock_response
        
        with patch('streamlit.session_state', {}):
            result = auth_service.signup(
                "test@example.com",
                "password123",
                nom="Dupont",
                prenom="Jean"
            )
        
        assert result.success
        assert result.user is not None
        assert result.user.email == "test@example.com"
    
    def test_signup_email_exists(self, auth_service, mock_supabase_client):
        """Test inscription avec email existant."""
        mock_supabase_client.auth.sign_up.side_effect = Exception(
            "User already registered"
        )
        
        result = auth_service.signup("existing@example.com", "password123")
        
        assert not result.success
        assert result.error_code == "EMAIL_EXISTS"
    
    def test_login_success(self, auth_service, mock_supabase_client):
        """Test connexion réussie."""
        mock_user = Mock()
        mock_user.id = "123"
        mock_user.email = "test@example.com"
        mock_user.user_metadata = {"nom": "Dupont", "prenom": "Jean", "role": "membre"}
        
        mock_response = Mock()
        mock_response.user = mock_user
        mock_response.session = Mock()
        
        mock_supabase_client.auth.sign_in_with_password.return_value = mock_response
        
        with patch('streamlit.session_state', {}):
            result = auth_service.login("test@example.com", "password123")
        
        assert result.success
        assert result.user is not None
        assert result.user.nom == "Dupont"
    
    def test_login_invalid_credentials(self, auth_service, mock_supabase_client):
        """Test connexion avec identifiants invalides."""
        mock_supabase_client.auth.sign_in_with_password.side_effect = Exception(
            "Invalid login credentials"
        )
        
        result = auth_service.login("test@example.com", "wrong_password")
        
        assert not result.success
        assert result.error_code == "INVALID_CREDENTIALS"
    
    def test_logout_success(self, auth_service, mock_supabase_client):
        """Test déconnexion."""
        with patch('streamlit.session_state', {'_auth_user': Mock(), '_auth_session': Mock()}):
            result = auth_service.logout()
        
        assert result.success
        mock_supabase_client.auth.sign_out.assert_called_once()


# ═══════════════════════════════════════════════════════════
# TESTS DÉCORATEURS
# ═══════════════════════════════════════════════════════════


class TestDecorators:
    """Tests pour les décorateurs d'authentification."""
    
    @patch('src.services.auth.get_auth_service')
    @patch('src.services.auth.render_login_form')
    @patch('streamlit.warning')
    def test_require_authenticated_not_logged_in(
        self, mock_warning, mock_render, mock_get_auth
    ):
        """Test décorateur sans authentification."""
        mock_auth = Mock()
        mock_auth.is_authenticated.return_value = False
        mock_get_auth.return_value = mock_auth
        
        @require_authenticated
        def protected_function():
            return "secret"
        
        result = protected_function()
        
        assert result is None
        mock_warning.assert_called_once()
        mock_render.assert_called_once()
    
    @patch('src.services.auth.get_auth_service')
    def test_require_authenticated_logged_in(self, mock_get_auth):
        """Test décorateur avec authentification."""
        mock_auth = Mock()
        mock_auth.is_authenticated.return_value = True
        mock_get_auth.return_value = mock_auth
        
        @require_authenticated
        def protected_function():
            return "secret"
        
        result = protected_function()
        
        assert result == "secret"
    
    @patch('src.services.auth.get_auth_service')
    @patch('src.services.auth.render_login_form')
    @patch('streamlit.warning')
    def test_require_role_not_logged_in(
        self, mock_warning, mock_render, mock_get_auth
    ):
        """Test décorateur de rôle sans authentification."""
        mock_auth = Mock()
        mock_auth.get_current_user.return_value = None
        mock_get_auth.return_value = mock_auth
        
        @require_role(Role.ADMIN)
        def admin_function():
            return "admin secret"
        
        result = admin_function()
        
        assert result is None
        mock_warning.assert_called_once()
    
    @patch('src.services.auth.get_auth_service')
    @patch('streamlit.error')
    def test_require_role_insufficient(self, mock_error, mock_get_auth):
        """Test décorateur de rôle avec rôle insuffisant."""
        mock_auth = Mock()
        mock_auth.get_current_user.return_value = UserProfile(role=Role.INVITE)
        mock_get_auth.return_value = mock_auth
        
        @require_role(Role.ADMIN)
        def admin_function():
            return "admin secret"
        
        result = admin_function()
        
        assert result is None
        mock_error.assert_called_once()
    
    @patch('src.services.auth.get_auth_service')
    def test_require_role_sufficient(self, mock_get_auth):
        """Test décorateur de rôle avec rôle suffisant."""
        mock_auth = Mock()
        mock_auth.get_current_user.return_value = UserProfile(role=Role.ADMIN)
        mock_get_auth.return_value = mock_auth
        
        @require_role(Role.MEMBRE)
        def membre_function():
            return "membre secret"
        
        result = membre_function()
        
        assert result == "membre secret"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
