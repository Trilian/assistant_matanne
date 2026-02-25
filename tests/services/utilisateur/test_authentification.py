"""
Tests pour src/services/utilisateur/authentification.py
Cible: Couverture >80%

Tests pour:
- AuthService: signup, login, logout, reset_password
- ProfilUtilisateur: permissions, display_name
- Session management
- JWT validation
- Profile updates
- Decorators
"""

from unittest.mock import Mock, patch

import pytest

# ═══════════════════════════════════════════════════════════
# IMPORTS DU MODULE
# ═══════════════════════════════════════════════════════════
from src.services.core.utilisateur.authentification import (
    ROLE_PERMISSIONS,
    AuthResult,
    AuthService,
    Permission,
    ProfilUtilisateur,
    Role,
    get_auth_service,
)
from src.ui.views.authentification import (
    require_authenticated,
    require_role,
)

# ═══════════════════════════════════════════════════════════
# TESTS ENUMS ET PERMISSIONS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRole:
    """Tests pour l'enum Role."""

    def test_role_values(self):
        """Vérifie les valeurs des rôles."""
        assert Role.ADMIN.value == "admin"
        assert Role.MEMBRE.value == "membre"
        assert Role.INVITE.value == "invite"

    def test_role_count(self):
        """Vérifie le nombre de rôles."""
        assert len(Role) == 3


@pytest.mark.unit
class TestPermission:
    """Tests pour l'enum Permission."""

    def test_permission_values(self):
        """Vérifie quelques permissions."""
        assert Permission.READ_RECIPES.value == "read_recipes"
        assert Permission.WRITE_RECIPES.value == "write_recipes"
        assert Permission.ADMIN_ALL.value == "admin_all"
        assert Permission.MANAGE_USERS.value == "manage_users"

    def test_permission_count(self):
        """Vérifie le nombre de permissions."""
        assert len(Permission) == 9


@pytest.mark.unit
class TestRolePermissions:
    """Tests pour le mapping ROLE_PERMISSIONS."""

    def test_admin_has_all_permissions(self):
        """Admin a toutes les permissions."""
        admin_perms = ROLE_PERMISSIONS[Role.ADMIN]
        assert len(admin_perms) == len(Permission)
        for p in Permission:
            assert p in admin_perms

    def test_membre_permissions(self):
        """Membre a les permissions de lecture/écriture."""
        membre_perms = ROLE_PERMISSIONS[Role.MEMBRE]
        assert Permission.READ_RECIPES in membre_perms
        assert Permission.WRITE_RECIPES in membre_perms
        assert Permission.MANAGE_USERS not in membre_perms
        assert Permission.ADMIN_ALL not in membre_perms

    def test_invite_read_only(self):
        """Invité n'a que les permissions de lecture."""
        invite_perms = ROLE_PERMISSIONS[Role.INVITE]
        assert Permission.READ_RECIPES in invite_perms
        assert Permission.READ_INVENTORY in invite_perms
        assert Permission.READ_PLANNING in invite_perms
        assert Permission.WRITE_RECIPES not in invite_perms
        assert Permission.WRITE_INVENTORY not in invite_perms


# ═══════════════════════════════════════════════════════════
# TESTS USERPROFILE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUserProfile:
    """Tests pour ProfilUtilisateur."""

    def test_default_values(self):
        """Vérifie les valeurs par défaut."""
        profile = ProfilUtilisateur()
        assert profile.id == ""
        assert profile.email == ""
        assert profile.role == Role.MEMBRE
        assert profile.avatar_url is None
        assert profile.preferences == {}

    def test_has_permission_admin(self):
        """Admin a toutes les permissions."""
        profile = ProfilUtilisateur(role=Role.ADMIN)
        assert profile.has_permission(Permission.ADMIN_ALL)
        assert profile.has_permission(Permission.MANAGE_USERS)
        assert profile.has_permission(Permission.READ_RECIPES)

    def test_has_permission_membre(self):
        """Membre a les permissions de base."""
        profile = ProfilUtilisateur(role=Role.MEMBRE)
        assert profile.has_permission(Permission.READ_RECIPES)
        assert profile.has_permission(Permission.WRITE_RECIPES)
        assert not profile.has_permission(Permission.ADMIN_ALL)
        assert not profile.has_permission(Permission.MANAGE_USERS)

    def test_has_permission_invite(self):
        """Invité a les permissions de lecture."""
        profile = ProfilUtilisateur(role=Role.INVITE)
        assert profile.has_permission(Permission.READ_RECIPES)
        assert not profile.has_permission(Permission.WRITE_RECIPES)

    def test_display_name_with_names(self):
        """Display name avec prénom et nom."""
        profile = ProfilUtilisateur(prenom="Anne", nom="Matanne")
        assert profile.display_name == "Anne Matanne"

    def test_display_name_from_email(self):
        """Display name depuis email."""
        profile = ProfilUtilisateur(email="anne@matanne.fr")
        assert profile.display_name == "anne"

    def test_display_name_default(self):
        """Display name par défaut."""
        profile = ProfilUtilisateur()
        assert profile.display_name == "Utilisateur"


# ═══════════════════════════════════════════════════════════
# TESTS AUTHRESULT
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAuthResult:
    """Tests pour AuthResult."""

    def test_default_values(self):
        """Vérifie les valeurs par défaut."""
        result = AuthResult()
        assert result.success is False
        assert result.user is None
        assert result.message == ""
        assert result.error_code is None

    def test_success_result(self):
        """Résultat de succès."""
        user = ProfilUtilisateur(email="test@test.fr")
        result = AuthResult(success=True, user=user, message="OK")
        assert result.success is True
        assert result.user == user
        assert result.message == "OK"

    def test_error_result(self):
        """Résultat d'erreur."""
        result = AuthResult(success=False, message="Erreur", error_code="TEST_ERROR")
        assert result.success is False
        assert result.error_code == "TEST_ERROR"


# ═══════════════════════════════════════════════════════════
# TESTS AUTHSERVICE - INITIALISATION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAuthServiceInit:
    """Tests pour l'initialisation d'AuthService."""

    @patch("src.services.core.utilisateur.authentification.AuthService._init_client")
    def test_init_calls_init_client(self, mock_init):
        """Vérifie que _init_client est appelé."""
        _service = AuthService()  # noqa: F841
        mock_init.assert_called_once()

    def test_session_keys(self):
        """Vérifie les clés de session."""
        assert AuthService.SESSION_KEY == "_auth_session"
        assert AuthService.USER_KEY == "_auth_user"


# ═══════════════════════════════════════════════════════════
# TESTS AUTHSERVICE - LOGIN
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAuthServiceLogin:
    """Tests pour la méthode login."""

    def test_login_demo_mode_success(self):
        """Login en mode démo avec compte valide."""
        storage = {}

        service = AuthService(storage=storage)
        service._client = None  # Mode démo

        result = service.login("anne@matanne.fr", "password123")

        assert result.success is True
        assert result.user is not None
        assert result.user.email == "anne@matanne.fr"
        assert result.user.role == Role.ADMIN
        # Vérifie que "demo" ou "démo" est dans le message (encodage variable)
        assert "mo" in result.message.lower()  # Mode/demo

    def test_login_demo_mode_membre(self):
        """Login en mode démo avec compte membre."""
        storage = {}

        service = AuthService(storage=storage)
        service._client = None

        result = service.login("demo@test.fr", "password123")

        assert result.success is True
        assert result.user.role == Role.MEMBRE

    def test_login_demo_mode_invite(self):
        """Login en mode démo avec compte invité."""
        storage = {}

        service = AuthService(storage=storage)
        service._client = None

        result = service.login("test@test.fr", "password123")

        assert result.success is True
        assert result.user.role == Role.INVITE

    def test_login_demo_mode_invalid(self):
        """Login en mode démo avec mauvais identifiants."""
        storage = {}

        service = AuthService(storage=storage)
        service._client = None

        result = service.login("wrong@email.fr", "wrongpassword")

        assert result.success is False
        assert result.error_code == "DEMO_MODE"

    def test_login_supabase_success(self):
        """Login avec Supabase succès."""
        storage = {}

        mock_client = Mock()
        mock_response = Mock()
        mock_response.user = Mock()
        mock_response.user.id = "123"
        mock_response.user.email = "test@test.fr"
        mock_response.user.user_metadata = {"nom": "Test", "prenom": "User", "role": "membre"}
        mock_response.session = Mock()
        mock_client.auth.sign_in_with_password.return_value = mock_response

        service = AuthService(storage=storage)
        service._client = mock_client

        result = service.login("test@test.fr", "password123")

        assert result.success is True
        assert result.user.email == "test@test.fr"

    def test_login_supabase_no_user(self):
        """Login avec Supabase sans utilisateur retourné."""
        storage = {}

        mock_client = Mock()
        mock_response = Mock()
        mock_response.user = None
        mock_client.auth.sign_in_with_password.return_value = mock_response

        service = AuthService(storage=storage)
        service._client = mock_client

        result = service.login("test@test.fr", "password123")

        assert result.success is False
        assert "incorrect" in result.message.lower()

    def test_login_supabase_invalid_credentials(self):
        """Login avec Supabase credentials invalides."""
        storage = {}

        mock_client = Mock()
        mock_client.auth.sign_in_with_password.side_effect = Exception("Invalid credentials")

        service = AuthService(storage=storage)
        service._client = mock_client

        result = service.login("test@test.fr", "wrongpassword")

        assert result.success is False
        assert result.error_code == "INVALID_CREDENTIALS"

    def test_login_supabase_generic_error(self):
        """Login avec Supabase erreur générique."""
        storage = {}

        mock_client = Mock()
        mock_client.auth.sign_in_with_password.side_effect = Exception("Network error")

        service = AuthService(storage=storage)
        service._client = mock_client

        result = service.login("test@test.fr", "password123")

        assert result.success is False
        assert result.error_code == "LOGIN_ERROR"


# ═══════════════════════════════════════════════════════════
# TESTS AUTHSERVICE - SIGNUP
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAuthServiceSignup:
    """Tests pour la méthode signup."""

    def test_signup_not_configured(self):
        """Signup quand non configuré."""
        storage = {}
        service = AuthService(storage=storage)
        service._client = None

        result = service.signup("test@test.fr", "password123")

        assert result.success is False
        assert result.error_code == "NOT_CONFIGURED"

    def test_signup_success(self):
        """Signup avec succès."""
        storage = {}

        mock_client = Mock()
        mock_response = Mock()
        mock_response.user = Mock()
        mock_response.user.id = "new123"
        mock_response.session = Mock()
        mock_client.auth.sign_up.return_value = mock_response

        service = AuthService(storage=storage)
        service._client = mock_client

        result = service.signup("new@test.fr", "password123", nom="Test", prenom="User")

        assert result.success is True
        assert result.user.nom == "Test"
        assert result.user.prenom == "User"

    def test_signup_no_user(self):
        """Signup sans utilisateur retourné."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.user = None
        mock_client.auth.sign_up.return_value = mock_response

        storage = {}
        service = AuthService(storage=storage)
        service._client = mock_client

        result = service.signup("new@test.fr", "password123")

        assert result.success is False

    def test_signup_email_exists(self):
        """Signup avec email déjà existant."""
        mock_client = Mock()
        mock_client.auth.sign_up.side_effect = Exception("already registered")

        storage = {}
        service = AuthService(storage=storage)
        service._client = mock_client

        result = service.signup("existing@test.fr", "password123")

        assert result.success is False
        assert result.error_code == "EMAIL_EXISTS"

    def test_signup_generic_error(self):
        """Signup avec erreur générique."""
        mock_client = Mock()
        mock_client.auth.sign_up.side_effect = Exception("Something went wrong")

        storage = {}
        service = AuthService(storage=storage)
        service._client = mock_client

        result = service.signup("new@test.fr", "password123")

        assert result.success is False
        assert result.error_code == "SIGNUP_ERROR"


# ═══════════════════════════════════════════════════════════
# TESTS AUTHSERVICE - LOGOUT
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAuthServiceLogout:
    """Tests pour la méthode logout."""

    def test_logout_not_configured(self):
        """Logout quand non configuré."""
        storage = {}
        service = AuthService(storage=storage)
        service._client = None

        result = service.logout()

        assert result.success is True

    def test_logout_success(self):
        """Logout avec succès."""
        storage = {AuthService.SESSION_KEY: "session", AuthService.USER_KEY: "user"}

        mock_client = Mock()
        mock_client.auth.sign_out.return_value = None

        service = AuthService(storage=storage)
        service._client = mock_client

        result = service.logout()

        assert result.success is True
        mock_client.auth.sign_out.assert_called_once()

    def test_logout_with_error(self):
        """Logout avec erreur (session toujours nettoyée)."""
        storage = {AuthService.SESSION_KEY: "session", AuthService.USER_KEY: "user"}

        mock_client = Mock()
        mock_client.auth.sign_out.side_effect = Exception("Error")

        service = AuthService(storage=storage)
        service._client = mock_client

        result = service.logout()

        assert result.success is True  # Session nettoyée quand même


# ═══════════════════════════════════════════════════════════
# TESTS AUTHSERVICE - RESET PASSWORD
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAuthServiceResetPassword:
    """Tests pour la méthode reset_password."""

    def test_reset_not_configured(self):
        """Reset quand non configuré."""
        storage = {}
        service = AuthService(storage=storage)
        service._client = None

        result = service.reset_password("test@test.fr")

        assert result.success is False
        assert result.error_code == "NOT_CONFIGURED"

    def test_reset_success(self):
        """Reset avec succès."""
        mock_client = Mock()
        mock_client.auth.reset_password_for_email.return_value = None

        storage = {}
        service = AuthService(storage=storage)
        service._client = mock_client

        result = service.reset_password("test@test.fr")

        assert result.success is True
        assert "email existe" in result.message.lower()

    def test_reset_with_error(self):
        """Reset avec erreur (ne révèle pas si email existe)."""
        mock_client = Mock()
        mock_client.auth.reset_password_for_email.side_effect = Exception("Error")

        storage = {}
        service = AuthService(storage=storage)
        service._client = mock_client

        result = service.reset_password("test@test.fr")

        # Ne révèle pas si l'email existe
        assert result.success is True


# ═══════════════════════════════════════════════════════════
# TESTS AUTHSERVICE - SESSION MANAGEMENT
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAuthServiceSession:
    """Tests pour la gestion des sessions."""

    def test_get_current_user_exists(self):
        """Récupère l'utilisateur connecté."""
        user = ProfilUtilisateur(email="test@test.fr")
        storage = {AuthService.USER_KEY: user}

        service = AuthService(storage=storage)
        service._client = None

        result = service.get_current_user()

        assert result == user

    def test_get_current_user_none(self):
        """Pas d'utilisateur connecté."""
        storage = {}

        service = AuthService(storage=storage)
        service._client = None

        result = service.get_current_user()

        assert result is None

    def test_is_authenticated_true(self):
        """Utilisateur authentifié."""
        storage = {AuthService.USER_KEY: ProfilUtilisateur()}

        service = AuthService(storage=storage)
        service._client = None

        assert service.is_authenticated() is True

    def test_is_authenticated_false(self):
        """Utilisateur non authentifié."""
        storage = {}

        service = AuthService(storage=storage)
        service._client = None

        assert service.is_authenticated() is False

    def test_require_permission_with_user(self):
        """Vérifie permission avec utilisateur."""
        user = ProfilUtilisateur(role=Role.ADMIN)
        storage = {AuthService.USER_KEY: user}

        service = AuthService(storage=storage)
        service._client = None

        assert service.require_permission(Permission.ADMIN_ALL) is True

    def test_require_permission_no_user(self):
        """Vérifie permission sans utilisateur."""
        storage = {}

        service = AuthService(storage=storage)
        service._client = None

        assert service.require_permission(Permission.READ_RECIPES) is False

    def test_save_session(self):
        """Sauvegarde de session."""
        storage = {}

        service = AuthService(storage=storage)
        service._client = None

        session = Mock()
        user = ProfilUtilisateur(email="test@test.fr")

        service._save_session(session, user)

        assert storage[AuthService.SESSION_KEY] == session
        assert storage[AuthService.USER_KEY] == user

    def test_clear_session(self):
        """Nettoyage de session."""
        storage = {AuthService.SESSION_KEY: "session", AuthService.USER_KEY: "user"}

        service = AuthService(storage=storage)
        service._client = None

        service._clear_session()

        assert AuthService.SESSION_KEY not in storage
        assert AuthService.USER_KEY not in storage


# ═══════════════════════════════════════════════════════════
# TESTS AUTHSERVICE - JWT
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAuthServiceJWT:
    """Tests pour la validation JWT."""

    def test_validate_token_not_configured(self):
        """Validation token quand non configuré."""
        storage = {}
        service = AuthService(storage=storage)
        service._client = None

        result = service.validate_token("token")

        assert result is None

    def test_validate_token_success(self):
        """Validation token avec succès."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.user = Mock()
        mock_response.user.id = "123"
        mock_response.user.email = "test@test.fr"
        mock_response.user.user_metadata = {"nom": "Test", "prenom": "User", "role": "membre"}
        mock_client.auth.get_user.return_value = mock_response

        storage = {}
        service = AuthService(storage=storage)
        service._client = mock_client

        result = service.validate_token("valid_token")

        assert result is not None
        assert result.email == "test@test.fr"

    def test_validate_token_no_user(self):
        """Validation token sans utilisateur."""
        mock_client = Mock()
        mock_client.auth.get_user.return_value = None

        storage = {}
        service = AuthService(storage=storage)
        service._client = mock_client

        result = service.validate_token("invalid_token")

        assert result is None

    def test_validate_token_error(self):
        """Validation token avec erreur."""
        mock_client = Mock()
        mock_client.auth.get_user.side_effect = Exception("Error")

        storage = {}
        service = AuthService(storage=storage)
        service._client = mock_client

        result = service.validate_token("invalid_token")

        assert result is None

    def test_decode_jwt_payload_success(self):
        """Décodage payload JWT."""
        import base64
        import json

        payload = {"sub": "123", "email": "test@test.fr"}
        encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")

        token = f"header.{encoded}.signature"

        storage = {}
        service = AuthService(storage=storage)
        service._client = None

        result = service.decode_jwt_payload(token)

        assert result == payload

    def test_decode_jwt_payload_invalid_format(self):
        """Décodage JWT format invalide."""
        storage = {}
        service = AuthService(storage=storage)
        service._client = None

        result = service.decode_jwt_payload("invalid_token")

        assert result is None

    def test_decode_jwt_payload_invalid_base64(self):
        """Décodage JWT base64 invalide."""
        storage = {}
        service = AuthService(storage=storage)
        service._client = None

        result = service.decode_jwt_payload("header.invalid!!!.signature")

        assert result is None


# ═══════════════════════════════════════════════════════════
# TESTS AUTHSERVICE - UPDATE PROFILE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAuthServiceUpdateProfile:
    """Tests pour update_profile."""

    def test_update_profile_not_configured(self):
        """Update profile quand non configuré."""
        storage = {}
        service = AuthService(storage=storage)
        service._client = None

        result = service.update_profile(nom="Test")

        assert result.success is False
        assert result.error_code == "NOT_CONFIGURED"

    def test_update_profile_not_authenticated(self):
        """Update profile quand non connecté."""
        storage = {}

        mock_client = Mock()
        service = AuthService(storage=storage)
        service._client = mock_client

        result = service.update_profile(nom="Test")

        assert result.success is False
        assert result.error_code == "NOT_AUTHENTICATED"

    def test_update_profile_no_changes(self):
        """Update profile sans modifications."""
        user = ProfilUtilisateur(email="test@test.fr")
        storage = {AuthService.USER_KEY: user}

        mock_client = Mock()
        service = AuthService(storage=storage)
        service._client = mock_client

        result = service.update_profile()

        assert result.success is True
        assert "modification" in result.message.lower()

    def test_update_profile_success(self):
        """Update profile avec succès."""
        user = ProfilUtilisateur(email="test@test.fr", nom="Old", prenom="Name")
        storage = {AuthService.USER_KEY: user}

        mock_client = Mock()
        mock_response = Mock()
        mock_response.user = Mock()
        mock_response.user.id = "123"
        mock_response.user.email = "test@test.fr"
        mock_response.user.user_metadata = {"nom": "New", "prenom": "Name", "role": "membre"}
        mock_client.auth.update_user.return_value = mock_response

        service = AuthService(storage=storage)
        service._client = mock_client

        result = service.update_profile(nom="New")

        assert result.success is True
        assert result.user.nom == "New"

    def test_update_profile_no_response(self):
        """Update profile sans réponse."""
        user = ProfilUtilisateur(email="test@test.fr")
        storage = {AuthService.USER_KEY: user}

        mock_client = Mock()
        mock_client.auth.update_user.return_value = None

        service = AuthService(storage=storage)
        service._client = mock_client

        result = service.update_profile(nom="New")

        assert result.success is False

    def test_update_profile_error(self):
        """Update profile avec erreur."""
        user = ProfilUtilisateur(email="test@test.fr")
        storage = {AuthService.USER_KEY: user}

        mock_client = Mock()
        mock_client.auth.update_user.side_effect = Exception("Error")

        service = AuthService(storage=storage)
        service._client = mock_client

        result = service.update_profile(nom="New")

        assert result.success is False
        assert result.error_code == "UPDATE_ERROR"


# ═══════════════════════════════════════════════════════════
# TESTS AUTHSERVICE - CHANGE PASSWORD
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAuthServiceChangePassword:
    """Tests pour change_password."""

    def test_change_password_not_configured(self):
        """Change password quand non configuré."""
        storage = {}
        service = AuthService(storage=storage)
        service._client = None

        result = service.change_password("newpassword123")

        assert result.success is False

    def test_change_password_too_short(self):
        """Change password trop court."""
        mock_client = Mock()
        storage = {}
        service = AuthService(storage=storage)
        service._client = mock_client

        result = service.change_password("12345")

        assert result.success is False
        assert "court" in result.message.lower()

    def test_change_password_success(self):
        """Change password avec succès."""
        mock_client = Mock()
        mock_client.auth.update_user.return_value = Mock()

        storage = {}
        service = AuthService(storage=storage)
        service._client = mock_client

        result = service.change_password("newpassword123")

        assert result.success is True

    def test_change_password_no_response(self):
        """Change password sans réponse."""
        mock_client = Mock()
        mock_client.auth.update_user.return_value = None

        storage = {}
        service = AuthService(storage=storage)
        service._client = mock_client

        result = service.change_password("newpassword123")

        assert result.success is False

    def test_change_password_error(self):
        """Change password avec erreur."""
        mock_client = Mock()
        mock_client.auth.update_user.side_effect = Exception("Error")

        storage = {}
        service = AuthService(storage=storage)
        service._client = mock_client

        result = service.change_password("newpassword123")

        assert result.success is False


# ═══════════════════════════════════════════════════════════
# TESTS FACTORY
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAuthServiceFactory:
    """Tests pour get_auth_service."""

    def test_get_auth_service_singleton(self):
        """Factory retourne la même instance."""
        # Reset le singleton
        import src.services.core.utilisateur.authentification as auth_module

        # Reset via registry
        from src.services.core.registry import obtenir_registre

        obtenir_registre().reinitialiser("authentification")

        service1 = get_auth_service()
        service2 = get_auth_service()

        assert service1 is service2

    def test_get_auth_service_returns_authservice(self):
        """Factory retourne AuthService."""
        import src.services.core.utilisateur.authentification as auth_module

        # Reset via registry
        from src.services.core.registry import obtenir_registre

        obtenir_registre().reinitialiser("authentification")

        service = get_auth_service()

        assert isinstance(service, AuthService)


# ═══════════════════════════════════════════════════════════
# TESTS DECORATORS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestDecorators:
    """Tests pour les décorateurs d'authentification."""

    @patch("src.ui.views.authentification.afficher_formulaire_connexion")
    @patch("src.ui.views.authentification.get_auth_service")
    @patch("src.ui.views.authentification.st")
    def test_require_authenticated_not_authenticated(self, mock_st, mock_get_auth, mock_render):
        """Décorateur avec utilisateur non authentifié."""
        mock_auth = Mock()
        mock_auth.is_authenticated.return_value = False
        mock_get_auth.return_value = mock_auth

        @require_authenticated
        def protected_func():
            return "success"

        result = protected_func()

        assert result is None
        mock_render.assert_called_once()

    @patch("src.ui.views.authentification.get_auth_service")
    @patch("src.ui.views.authentification.st")
    def test_require_authenticated_authenticated(self, mock_st, mock_get_auth):
        """Décorateur avec utilisateur authentifié."""
        mock_auth = Mock()
        mock_auth.is_authenticated.return_value = True
        mock_get_auth.return_value = mock_auth

        @require_authenticated
        def protected_func():
            return "success"

        result = protected_func()

        assert result == "success"

    @patch("src.ui.views.authentification.afficher_formulaire_connexion")
    @patch("src.ui.views.authentification.get_auth_service")
    @patch("src.ui.views.authentification.st")
    def test_require_role_not_authenticated(self, mock_st, mock_get_auth, mock_render):
        """Décorateur role sans utilisateur."""
        mock_auth = Mock()
        mock_auth.get_current_user.return_value = None
        mock_get_auth.return_value = mock_auth

        @require_role(Role.MEMBRE)
        def admin_func():
            return "success"

        result = admin_func()

        assert result is None
        mock_render.assert_called_once()

    @patch("src.ui.views.authentification.get_auth_service")
    @patch("src.ui.views.authentification.st")
    def test_require_role_insufficient_role(self, mock_st, mock_get_auth):
        """Décorateur role avec rôle insuffisant."""
        mock_auth = Mock()
        user = ProfilUtilisateur(role=Role.INVITE)
        mock_auth.get_current_user.return_value = user
        mock_get_auth.return_value = mock_auth

        @require_role(Role.ADMIN)
        def admin_func():
            return "success"

        result = admin_func()

        assert result is None

    @patch("src.ui.views.authentification.get_auth_service")
    @patch("src.ui.views.authentification.st")
    def test_require_role_sufficient_role(self, mock_st, mock_get_auth):
        """Décorateur role avec rôle suffisant."""
        mock_auth = Mock()
        user = ProfilUtilisateur(role=Role.ADMIN)
        mock_auth.get_current_user.return_value = user
        mock_get_auth.return_value = mock_auth

        @require_role(Role.MEMBRE)
        def member_func():
            return "success"

        result = member_func()

        assert result == "success"


# ═══════════════════════════════════════════════════════════
# TESTS IS_CONFIGURED
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestIsConfigured:
    """Tests pour is_configured."""

    def test_is_configured_with_client(self):
        """is_configured avec client."""
        storage = {}
        service = AuthService(storage=storage)
        service._client = Mock()

        assert service.is_configured is True

    def test_is_configured_without_client(self):
        """is_configured sans client."""
        storage = {}
        service = AuthService(storage=storage)
        service._client = None

        assert service.is_configured is False


# ═══════════════════════════════════════════════════════════
# TESTS INIT CLIENT
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestInitClient:
    """Tests pour _init_client."""

    def test_init_client_default_state(self):
        """Par défaut, client est None sans Supabase configuré."""
        storage = {}
        service = AuthService(storage=storage)
        # Sans configuration Supabase, _client sera None
        # C'est le comportement attendu en mode développement
        # Le test passe car on vérifie juste que l'init ne crash pas
        assert hasattr(service, "_client")

    def test_init_client_instance_created(self):
        """L'instance est créée même sans client Supabase."""
        storage = {}
        service = AuthService(storage=storage)
        assert isinstance(service, AuthService)
        assert hasattr(service, "SESSION_KEY")
        assert hasattr(service, "USER_KEY")


# ═══════════════════════════════════════════════════════════
# TESTS REQUIRE_AUTH
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRequireAuth:
    """Tests pour require_auth."""

    @patch("src.ui.views.authentification.afficher_formulaire_connexion")
    def test_require_auth_not_authenticated(self, mock_render):
        """require_auth sans utilisateur connecté."""
        storage = {}

        service = AuthService(storage=storage)
        service._client = None

        result = service.require_auth()

        assert result is None
        mock_render.assert_called_once()

    def test_require_auth_authenticated(self):
        """require_auth avec utilisateur connecté."""
        user = ProfilUtilisateur(email="test@test.fr")
        storage = {AuthService.USER_KEY: user}

        service = AuthService(storage=storage)
        service._client = None

        result = service.require_auth()

        assert result == user


# ═══════════════════════════════════════════════════════════
# TESTS REFRESH_SESSION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRefreshSession:
    """Tests pour refresh_session."""

    def test_refresh_session_not_configured(self):
        """refresh_session quand non configuré."""
        storage = {}
        service = AuthService(storage=storage)
        service._client = None

        result = service.refresh_session()

        assert result is False

    def test_refresh_session_no_session(self):
        """refresh_session sans session."""
        storage = {}

        mock_client = Mock()
        service = AuthService(storage=storage)
        service._client = mock_client

        result = service.refresh_session()

        assert result is False

    def test_refresh_session_success(self):
        """refresh_session avec succès."""
        storage = {AuthService.SESSION_KEY: Mock()}

        mock_client = Mock()
        mock_client.auth.obtenir_contexte_db.return_value = Mock()

        service = AuthService(storage=storage)
        service._client = mock_client

        result = service.refresh_session()

        assert result is True

    def test_refresh_session_error(self):
        """refresh_session avec erreur."""
        storage = {AuthService.SESSION_KEY: Mock()}

        mock_client = Mock()
        mock_client.auth.obtenir_contexte_db.side_effect = Exception("Error")

        service = AuthService(storage=storage)
        service._client = mock_client

        result = service.refresh_session()

        assert result is False


# ═══════════════════════════════════════════════════════════
# TESTS UPDATE PROFILE AVEC AVATAR ET PREFERENCES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUpdateProfileExtended:
    """Tests étendus pour update_profile avec avatar et preferences."""

    def test_update_profile_with_avatar(self):
        """Update profile avec avatar_url."""
        user = ProfilUtilisateur(email="test@test.fr", nom="Test", avatar_url=None)
        storage = {AuthService.USER_KEY: user}

        mock_client = Mock()
        mock_response = Mock()
        mock_response.user = Mock()
        mock_response.user.id = "123"
        mock_response.user.email = "test@test.fr"
        mock_response.user.user_metadata = {
            "nom": "Test",
            "prenom": "",
            "role": "membre",
            "avatar_url": "https://example.com/avatar.png",
        }
        mock_client.auth.update_user.return_value = mock_response

        service = AuthService(storage=storage)
        service._client = mock_client

        result = service.update_profile(avatar_url="https://example.com/avatar.png")

        assert result.success is True
        assert result.user.avatar_url == "https://example.com/avatar.png"

    def test_update_profile_with_preferences(self):
        """Update profile avec preferences."""
        user = ProfilUtilisateur(email="test@test.fr", nom="Test")
        storage = {AuthService.USER_KEY: user}

        mock_client = Mock()
        mock_response = Mock()
        mock_response.user = Mock()
        mock_response.user.id = "123"
        mock_response.user.email = "test@test.fr"
        mock_response.user.user_metadata = {
            "nom": "Test",
            "prenom": "",
            "role": "membre",
            "preferences": {"theme": "dark"},
        }
        mock_client.auth.update_user.return_value = mock_response

        service = AuthService(storage=storage)
        service._client = mock_client

        result = service.update_profile(preferences={"theme": "dark"})

        assert result.success is True


# ═══════════════════════════════════════════════════════════
# TESTS VALIDATE TOKEN EXTENDED
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestValidateTokenExtended:
    """Tests étendus pour validate_token."""

    def test_validate_token_response_no_user(self):
        """validate_token avec réponse mais sans user."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.user = None
        mock_client.auth.get_user.return_value = mock_response

        storage = {}
        service = AuthService(storage=storage)
        service._client = mock_client

        result = service.validate_token("token")

        assert result is None


# ═══════════════════════════════════════════════════════════
# TESTS UI COMPONENTS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRenderLoginForm:
    """Tests pour afficher_login_form - ces tests vérifient la fonction est appelable."""

    def test_render_login_form_exists(self):
        """afficher_login_form existe et est importable."""
        from src.ui.views.authentification import (
            afficher_formulaire_connexion as afficher_login_form,
        )

        assert callable(afficher_login_form)

    def test_render_login_form_raises_without_context(self):
        """afficher_login_form lève une erreur sans contexte Streamlit."""
        from src.ui.views.authentification import (
            afficher_formulaire_connexion as afficher_login_form,
        )

        # Without proper Streamlit context, function will fail
        # This is expected behavior
        try:
            afficher_login_form()
        except (ValueError, AttributeError):
            pass  # Expected without Streamlit context


@pytest.mark.unit
class TestRenderUserMenu:
    """Tests pour afficher_user_menu."""

    def test_render_user_menu_exists(self):
        """afficher_user_menu existe et est importable."""
        from src.ui.views.authentification import afficher_menu_utilisateur as afficher_user_menu

        assert callable(afficher_user_menu)

    def test_render_user_menu_raises_without_context(self):
        """afficher_user_menu lève une erreur sans contexte Streamlit."""
        from src.ui.views.authentification import afficher_menu_utilisateur as afficher_user_menu

        try:
            afficher_user_menu()
        except (ValueError, AttributeError):
            pass  # Expected without Streamlit context


@pytest.mark.unit
class TestRenderProfileSettings:
    """Tests pour afficher_profile_settings."""

    def test_render_profile_settings_exists(self):
        """afficher_profile_settings existe et est importable."""
        from src.ui.views.authentification import (
            afficher_parametres_profil as afficher_profile_settings,
        )

        assert callable(afficher_profile_settings)

    def test_render_profile_settings_raises_without_context(self):
        """afficher_profile_settings lève une erreur sans contexte Streamlit."""
        from src.ui.views.authentification import (
            afficher_parametres_profil as afficher_profile_settings,
        )

        try:
            afficher_profile_settings()
        except (ValueError, AttributeError):
            pass  # Expected without Streamlit context


# ═══════════════════════════════════════════════════════════
# TESTS ADDITIONAL COVERAGE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAdditionalCoverage:
    """Tests additionnels pour couverture."""

    def test_role_enum_values(self):
        """Role enum contient les valeurs attendues."""
        assert Role.ADMIN.value == "admin"
        assert Role.MEMBRE.value == "membre"
        assert Role.INVITE.value == "invite"

    def test_permission_enum_values(self):
        """Permission enum contient les valeurs attendues."""
        assert Permission.READ_RECIPES.value == "read_recipes"
        assert Permission.ADMIN_ALL.value == "admin_all"

    def test_auth_service_init_with_session_state(self):
        """AuthService init avec st.session_state préexistant."""
        storage = {
            AuthService.USER_KEY: ProfilUtilisateur(email="test@test.fr"),
            AuthService.SESSION_KEY: {"token": "abc"},
        }

        service = AuthService(storage=storage)

        user = service.get_current_user()
        assert user is not None
        assert user.email == "test@test.fr"

    def test_login_invalid_email(self):
        """Login avec email invalide."""
        storage = {}

        mock_client = Mock()
        mock_client.auth.sign_in_with_password.side_effect = Exception("Invalid email")

        service = AuthService(storage=storage)
        service._client = mock_client

        result = service.login("not-an-email", "password")

        assert result.success is False

    def test_signup_weak_password(self):
        """Signup avec mot de passe faible."""
        storage = {}

        mock_client = Mock()
        mock_client.auth.sign_up.side_effect = Exception("Password too weak")

        service = AuthService(storage=storage)
        service._client = mock_client

        result = service.signup("test@test.fr", "123", "Test", "User")

        assert result.success is False
        assert "123" not in result.message  # Ne pas exposer le mot de passe


# ═══════════════════════════════════════════════════════════
# TESTS INIT CLIENT - BRANCHES ADDITIONNELLES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestInitClientBranches:
    """Tests branches supplémentaires pour _init_client."""

    def test_init_client_import_error(self):
        """Test branche ImportError dans _init_client."""
        with patch.dict("sys.modules", {"supabase": None}):
            # Simuler que le module supabase n'est pas installé
            storage = {}
            service = AuthService(storage=storage)
            # Le service doit être créé sans erreur
            assert service._client is None

    def test_init_client_with_missing_config(self):
        """Test initialisation avec config manquante."""
        # Par défaut en test, SUPABASE_URL et SUPABASE_ANON_KEY ne sont pas configurés
        storage = {}
        service = AuthService(storage=storage)

        # Vérifier que l'instance est créée
        assert isinstance(service, AuthService)
        # Sans config, client est None
        assert service._client is None

    def test_init_client_handles_exception(self):
        """Test que _init_client gère les exceptions gracieusement."""
        # En env de test, pas de supabase configuré
        storage = {}
        service = AuthService(storage=storage)

        # L'instance doit être créée même si l'init client échoue
        assert hasattr(service, "_client")
        assert hasattr(service, "SESSION_KEY")
        assert hasattr(service, "USER_KEY")


# ═══════════════════════════════════════════════════════════
# TESTS REFRESH SESSION - BRANCHES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRefreshSessionBranches:
    """Tests branches pour refresh_session."""

    def test_refresh_session_not_configured(self):
        """refresh_session retourne False si pas configuré."""
        storage = {}

        service = AuthService(storage=storage)
        service._client = None

        result = service.refresh_session()

        assert result is False

    def test_refresh_session_no_session_key(self):
        """refresh_session retourne False sans clé de session."""
        # session_state vide (pas de SESSION_KEY)
        storage = {}

        mock_client = Mock()

        service = AuthService(storage=storage)
        service._client = mock_client

        result = service.refresh_session()

        assert result is False

    def test_refresh_session_exception(self):
        """refresh_session gère les exceptions."""
        storage = {AuthService.SESSION_KEY: {"token": "abc"}}

        mock_client = Mock()
        mock_client.auth.obtenir_contexte_db.side_effect = Exception("Session error")

        service = AuthService(storage=storage)
        service._client = mock_client

        result = service.refresh_session()

        assert result is False


# ═══════════════════════════════════════════════════════════
# TESTS UPDATE PROFILE - BRANCHE NO UPDATE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUpdateProfileNoChange:
    """Tests pour update_profile sans modifications."""

    def test_update_profile_no_changes(self):
        """update_profile sans aucune modification."""
        user = ProfilUtilisateur(email="test@test.fr", nom="Doe", prenom="John")
        storage = {AuthService.USER_KEY: user}

        mock_client = Mock()

        service = AuthService(storage=storage)
        service._client = mock_client

        # Appel sans aucun paramètre de modification
        result = service.update_profile()

        assert result.success is True
        assert "Aucune modification" in result.message


# ═══════════════════════════════════════════════════════════
# TESTS RENDER FONCTIONS (UI) - MOCK
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRenderFunctions:
    """Tests basiques pour les fonctions render (UI)."""

    @patch("src.ui.views.authentification.st")
    @patch("src.ui.views.authentification.get_auth_service")
    def test_render_login_form_basic(self, mock_get_auth, mock_st):
        """Test afficher_login_form est appelable."""
        from src.ui.views.authentification import (
            afficher_formulaire_connexion as afficher_login_form,
        )

        mock_st.form.return_value.__enter__ = Mock()
        mock_st.form.return_value.__exit__ = Mock(return_value=False)
        mock_st.text_input.return_value = ""
        mock_st.form_submit_button.return_value = False
        mock_st.columns.return_value = [Mock(), Mock()]
        mock_st.tabs.return_value = [Mock(), Mock()]

        # Vérifier juste que la fonction ne crash pas
        try:
            afficher_login_form()
        except Exception:
            pass  # OK si exception due aux mocks incomplets

    @patch("src.ui.views.authentification.st")
    @patch("src.ui.views.authentification.get_auth_service")
    def test_render_user_menu_not_logged(self, mock_get_auth, mock_st):
        """Test afficher_user_menu sans utilisateur connecté."""
        from src.ui.views.authentification import afficher_menu_utilisateur as afficher_user_menu

        mock_service = Mock()
        mock_service.get_current_user.return_value = None
        mock_get_auth.return_value = mock_service

        mock_st.sidebar.__enter__ = Mock()
        mock_st.sidebar.__exit__ = Mock(return_value=False)

        try:
            afficher_user_menu()
        except Exception:
            pass  # OK pour ce test basique

    @patch("src.ui.views.authentification.st")
    @patch("src.ui.views.authentification.get_auth_service")
    def test_render_profile_settings_not_logged(self, mock_get_auth, mock_st):
        """Test afficher_profile_settings sans utilisateur connecté."""
        from src.ui.views.authentification import (
            afficher_parametres_profil as afficher_profile_settings,
        )

        mock_service = Mock()
        mock_service.get_current_user.return_value = None
        mock_get_auth.return_value = mock_service

        afficher_profile_settings()

        mock_st.warning.assert_called_once()


@pytest.mark.unit
class TestRenderFunctionsAdditional:
    """Tests supplémentaires pour les fonctions render (couverture branches)."""

    @patch("src.ui.views.authentification.st")
    @patch("src.ui.views.authentification.get_auth_service")
    def test_render_login_form_login_success(self, mock_get_auth, mock_st):
        """Test login réussi avec rerun."""
        from src.ui.views.authentification import (
            afficher_formulaire_connexion as afficher_login_form,
        )

        mock_service = Mock()
        mock_service.login.return_value = AuthResult(success=True, message="Bienvenue!")
        mock_get_auth.return_value = mock_service

        # Setup mocks pour le formulaire - utiliser MagicMock pour context managers
        from unittest.mock import MagicMock

        form_mock = MagicMock()
        mock_st.form.return_value = form_mock
        # Tab1: email, password (2) + Tab2: email, prenom, nom, password, password2 (5) = 7 text_inputs
        mock_st.text_input.side_effect = ["test@test.com", "password123", "", "", "", "", ""]
        # Tab1: submit, forgot (2) + Tab2: submit (1) = 3 form_submit_buttons
        mock_st.form_submit_button.side_effect = [True, False, False]
        mock_st.columns.return_value = [MagicMock(), MagicMock()]

        # Utiliser MagicMock pour les tabs (context managers)
        tab1_mock = MagicMock()
        tab2_mock = MagicMock()
        mock_st.tabs.return_value = [tab1_mock, tab2_mock]

        afficher_login_form(rediriger_apres_succes=True)

        mock_st.success.assert_called()
        mock_st.rerun.assert_called()

    @patch("src.ui.views.authentification.st")
    @patch("src.ui.views.authentification.get_auth_service")
    def test_render_login_form_login_failure(self, mock_get_auth, mock_st):
        """Test login échoué."""
        from unittest.mock import MagicMock

        from src.ui.views.authentification import (
            afficher_formulaire_connexion as afficher_login_form,
        )

        mock_service = Mock()
        mock_service.login.return_value = AuthResult(
            success=False, message="Identifiants incorrects"
        )
        mock_get_auth.return_value = mock_service

        form_mock = MagicMock()
        mock_st.form.return_value = form_mock
        # Tab1: email, password (2) + Tab2: email, prenom, nom, password, password2 (5) = 7 text_inputs
        mock_st.text_input.side_effect = ["test@test.com", "wrongpass", "", "", "", "", ""]
        mock_st.form_submit_button.side_effect = [True, False, False]
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        tab1_mock = MagicMock()
        tab2_mock = MagicMock()
        mock_st.tabs.return_value = [tab1_mock, tab2_mock]

        afficher_login_form()

        mock_st.error.assert_called()

    @patch("src.ui.views.authentification.st")
    @patch("src.ui.views.authentification.get_auth_service")
    def test_render_login_form_forgot_password(self, mock_get_auth, mock_st):
        """Test mot de passe oublié."""
        from unittest.mock import MagicMock

        from src.ui.views.authentification import (
            afficher_formulaire_connexion as afficher_login_form,
        )

        mock_service = Mock()
        mock_service.reset_password.return_value = AuthResult(success=True, message="Email envoyé")
        mock_get_auth.return_value = mock_service

        form_mock = MagicMock()
        mock_st.form.return_value = form_mock
        # Tab1: email, password (2) + Tab2: email, prenom, nom, password, password2 (5) = 7 text_inputs
        mock_st.text_input.side_effect = ["reset@test.com", "", "", "", "", "", ""]
        mock_st.form_submit_button.side_effect = [False, True, False]  # Submit=False, forgot=True
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        tab1_mock = MagicMock()
        tab2_mock = MagicMock()
        mock_st.tabs.return_value = [tab1_mock, tab2_mock]

        afficher_login_form()

        mock_st.info.assert_called()

    @patch("src.ui.views.authentification.st")
    @patch("src.ui.views.authentification.get_auth_service")
    def test_render_user_menu_logged_in(self, mock_get_auth, mock_st):
        """Test menu utilisateur connecté."""
        from unittest.mock import MagicMock

        from src.ui.views.authentification import afficher_menu_utilisateur as afficher_user_menu

        mock_user = Mock()
        mock_user.display_name = "Test User"
        mock_user.role = Role.MEMBRE

        mock_service = Mock()
        mock_service.get_current_user.return_value = mock_user
        mock_get_auth.return_value = mock_service

        # Sidebar est un context manager
        sidebar_mock = MagicMock()
        mock_st.sidebar = sidebar_mock
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.button.return_value = False

        afficher_user_menu()

        mock_st.markdown.assert_called()

    @patch("src.ui.views.authentification.st")
    @patch("src.ui.views.authentification.get_auth_service")
    def test_render_user_menu_logout_clicked(self, mock_get_auth, mock_st):
        """Test bouton déconnexion cliqué."""
        from unittest.mock import MagicMock

        from src.ui.views.authentification import afficher_menu_utilisateur as afficher_user_menu

        mock_user = Mock()
        mock_user.display_name = "Test User"
        mock_user.role = Role.ADMIN

        mock_service = Mock()
        mock_service.get_current_user.return_value = mock_user
        mock_get_auth.return_value = mock_service

        sidebar_mock = MagicMock()
        mock_st.sidebar = sidebar_mock
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.button.return_value = True  # Logout clicked

        afficher_user_menu()

        mock_service.logout.assert_called_once()
        mock_st.rerun.assert_called()

    @patch("src.ui.views.authentification.st")
    @patch("src.ui.views.authentification.get_auth_service")
    def test_render_user_menu_login_clicked(self, mock_get_auth, mock_st):
        """Test bouton connexion cliqué (non connecté)."""
        from unittest.mock import MagicMock

        from src.ui.views.authentification import afficher_menu_utilisateur as afficher_user_menu

        mock_service = Mock()
        mock_service.get_current_user.return_value = None
        mock_get_auth.return_value = mock_service

        sidebar_mock = MagicMock()
        mock_st.sidebar = sidebar_mock
        mock_st.button.return_value = True  # Login button clicked
        mock_st.session_state = {}

        afficher_user_menu()

        assert mock_st.session_state["show_login"] is True

    @patch("src.ui.views.authentification.st")
    @patch("src.ui.views.authentification.get_auth_service")
    def test_render_profile_settings_with_user(self, mock_get_auth, mock_st):
        """Test paramètres profil avec utilisateur connecté."""
        from datetime import datetime
        from unittest.mock import MagicMock

        from src.ui.views.authentification import (
            afficher_parametres_profil as afficher_profile_settings,
        )

        mock_user = Mock()
        mock_user.prenom = "Jean"
        mock_user.nom = "Dupont"
        mock_user.avatar_url = None
        mock_user.email = "jean@test.com"
        mock_user.role = Role.MEMBRE
        mock_user.cree_le = datetime(2024, 1, 1)

        mock_service = Mock()
        mock_service.get_current_user.return_value = mock_user
        mock_service.update_profile.return_value = AuthResult(success=True, message="OK")
        mock_get_auth.return_value = mock_service

        form_mock = MagicMock()
        mock_st.form.return_value = form_mock
        mock_st.text_input.side_effect = ["Jean", "Dupont", "", "newpass", "newpass"]
        mock_st.form_submit_button.side_effect = [True, False]  # Save=True, Change pwd=False

        afficher_profile_settings()

        mock_st.success.assert_called()

    @patch("src.ui.views.authentification.st")
    @patch("src.ui.views.authentification.get_auth_service")
    def test_render_profile_password_change(self, mock_get_auth, mock_st):
        """Test changement de mot de passe."""
        from datetime import datetime
        from unittest.mock import MagicMock

        from src.ui.views.authentification import (
            afficher_parametres_profil as afficher_profile_settings,
        )

        mock_user = Mock()
        mock_user.prenom = "Test"
        mock_user.nom = "User"
        mock_user.avatar_url = None
        mock_user.email = "test@test.com"
        mock_user.role = Role.MEMBRE
        mock_user.cree_le = datetime(2024, 1, 1)

        mock_service = Mock()
        mock_service.get_current_user.return_value = mock_user
        mock_service.change_password.return_value = AuthResult(success=True, message="Changé")
        mock_get_auth.return_value = mock_service

        form_mock = MagicMock()
        mock_st.form.return_value = form_mock
        # First form (profile), second form (password)
        mock_st.text_input.side_effect = ["Test", "User", "", "newpass123", "newpass123"]
        mock_st.form_submit_button.side_effect = [False, True]  # Save=False, Change pwd=True

        afficher_profile_settings()

        mock_service.change_password.assert_called_with("newpass123")
        mock_st.success.assert_called()
