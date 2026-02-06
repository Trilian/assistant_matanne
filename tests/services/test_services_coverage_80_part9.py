"""
Tests de couverture étendus pour src/services - Partie 9
Tests ciblés: auth enums/models, garmin config, base_ai_service, rapports_pdf
Focus sur amélioration couverture fichiers < 20%
"""

import pytest
from datetime import date, datetime
from unittest.mock import patch, MagicMock, Mock
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════
# TESTS AUTH - ENUMS ET MODÈLES
# ═══════════════════════════════════════════════════════════════════════════


class TestAuthRole:
    """Tests de l'enum Role."""

    def test_role_admin_exists(self):
        """Teste que ADMIN existe."""
        from src.services.auth import Role
        
        assert Role.ADMIN is not None
        assert Role.ADMIN.value == "admin"

    def test_role_membre_exists(self):
        """Teste que MEMBRE existe."""
        from src.services.auth import Role
        
        assert Role.MEMBRE is not None
        assert Role.MEMBRE.value == "membre"

    def test_role_invite_exists(self):
        """Teste que INVITE existe."""
        from src.services.auth import Role
        
        assert Role.INVITE is not None
        assert Role.INVITE.value == "invite"

    def test_role_is_str_enum(self):
        """Teste que Role est un str Enum."""
        from src.services.auth import Role
        
        assert issubclass(Role, str)
        assert issubclass(Role, Enum)


class TestAuthPermission:
    """Tests de l'enum Permission."""

    def test_permission_read_recipes(self):
        """Teste READ_RECIPES."""
        from src.services.auth import Permission
        
        assert Permission.READ_RECIPES.value == "read_recipes"

    def test_permission_write_recipes(self):
        """Teste WRITE_RECIPES."""
        from src.services.auth import Permission
        
        assert Permission.WRITE_RECIPES.value == "write_recipes"

    def test_permission_delete_recipes(self):
        """Teste DELETE_RECIPES."""
        from src.services.auth import Permission
        
        assert Permission.DELETE_RECIPES.value == "delete_recipes"

    def test_permission_read_inventory(self):
        """Teste READ_INVENTORY."""
        from src.services.auth import Permission
        
        assert Permission.READ_INVENTORY.value == "read_inventory"

    def test_permission_write_inventory(self):
        """Teste WRITE_INVENTORY."""
        from src.services.auth import Permission
        
        assert Permission.WRITE_INVENTORY.value == "write_inventory"

    def test_permission_read_planning(self):
        """Teste READ_PLANNING."""
        from src.services.auth import Permission
        
        assert Permission.READ_PLANNING.value == "read_planning"

    def test_permission_write_planning(self):
        """Teste WRITE_PLANNING."""
        from src.services.auth import Permission
        
        assert Permission.WRITE_PLANNING.value == "write_planning"

    def test_permission_manage_users(self):
        """Teste MANAGE_USERS."""
        from src.services.auth import Permission
        
        assert Permission.MANAGE_USERS.value == "manage_users"

    def test_permission_admin_all(self):
        """Teste ADMIN_ALL."""
        from src.services.auth import Permission
        
        assert Permission.ADMIN_ALL.value == "admin_all"


class TestRolePermissions:
    """Tests du mapping ROLE_PERMISSIONS."""

    def test_admin_has_all_permissions(self):
        """Teste que ADMIN a toutes les permissions."""
        from src.services.auth import Role, Permission, ROLE_PERMISSIONS
        
        admin_perms = ROLE_PERMISSIONS[Role.ADMIN]
        
        # Admin devrait avoir toutes les permissions
        for perm in Permission:
            assert perm in admin_perms

    def test_membre_has_read_write(self):
        """Teste que MEMBRE a les permissions lecture/écriture."""
        from src.services.auth import Role, Permission, ROLE_PERMISSIONS
        
        membre_perms = ROLE_PERMISSIONS[Role.MEMBRE]
        
        assert Permission.READ_RECIPES in membre_perms
        assert Permission.WRITE_RECIPES in membre_perms
        assert Permission.READ_INVENTORY in membre_perms
        assert Permission.WRITE_INVENTORY in membre_perms
        assert Permission.READ_PLANNING in membre_perms
        assert Permission.WRITE_PLANNING in membre_perms

    def test_invite_has_only_read(self):
        """Teste que INVITE n'a que les permissions lecture."""
        from src.services.auth import Role, Permission, ROLE_PERMISSIONS
        
        invite_perms = ROLE_PERMISSIONS[Role.INVITE]
        
        assert Permission.READ_RECIPES in invite_perms
        assert Permission.READ_INVENTORY in invite_perms
        assert Permission.READ_PLANNING in invite_perms
        
        # Pas d'écriture pour invite
        assert Permission.WRITE_RECIPES not in invite_perms
        assert Permission.WRITE_INVENTORY not in invite_perms


class TestAuthUserProfile:
    """Tests du modèle UserProfile."""

    def test_user_profile_default_values(self):
        """Teste les valeurs par défaut."""
        from src.services.auth import UserProfile, Role
        
        profile = UserProfile()
        
        assert profile.id == ""
        assert profile.email == ""
        assert profile.nom == ""
        assert profile.prenom == ""
        assert profile.role == Role.MEMBRE
        assert profile.avatar_url is None
        assert profile.preferences == {}
        assert profile.created_at is None
        assert profile.last_login is None

    def test_user_profile_with_values(self):
        """Teste création avec valeurs."""
        from src.services.auth import UserProfile, Role
        
        profile = UserProfile(
            id="user123",
            email="test@example.com",
            nom="Dupont",
            prenom="Jean",
            role=Role.ADMIN,
            avatar_url="https://example.com/avatar.jpg",
            preferences={"theme": "dark"}
        )
        
        assert profile.id == "user123"
        assert profile.email == "test@example.com"
        assert profile.nom == "Dupont"
        assert profile.prenom == "Jean"
        assert profile.role == Role.ADMIN
        assert profile.avatar_url == "https://example.com/avatar.jpg"
        assert profile.preferences["theme"] == "dark"

    def test_user_profile_has_permission_admin(self):
        """Teste has_permission pour admin."""
        from src.services.auth import UserProfile, Role, Permission
        
        profile = UserProfile(role=Role.ADMIN)
        
        # Admin a toutes les permissions
        assert profile.has_permission(Permission.READ_RECIPES) is True
        assert profile.has_permission(Permission.WRITE_RECIPES) is True
        assert profile.has_permission(Permission.MANAGE_USERS) is True
        assert profile.has_permission(Permission.ADMIN_ALL) is True

    def test_user_profile_has_permission_membre(self):
        """Teste has_permission pour membre."""
        from src.services.auth import UserProfile, Role, Permission
        
        profile = UserProfile(role=Role.MEMBRE)
        
        assert profile.has_permission(Permission.READ_RECIPES) is True
        assert profile.has_permission(Permission.WRITE_RECIPES) is True
        # Membre n'a pas MANAGE_USERS
        assert profile.has_permission(Permission.MANAGE_USERS) is False

    def test_user_profile_has_permission_invite(self):
        """Teste has_permission pour invite."""
        from src.services.auth import UserProfile, Role, Permission
        
        profile = UserProfile(role=Role.INVITE)
        
        assert profile.has_permission(Permission.READ_RECIPES) is True
        assert profile.has_permission(Permission.WRITE_RECIPES) is False

    def test_user_profile_display_name_full(self):
        """Teste display_name avec prénom et nom."""
        from src.services.auth import UserProfile
        
        profile = UserProfile(prenom="Jean", nom="Dupont")
        
        assert profile.display_name == "Jean Dupont"

    def test_user_profile_display_name_email(self):
        """Teste display_name avec juste email."""
        from src.services.auth import UserProfile
        
        profile = UserProfile(email="jean.dupont@example.com")
        
        assert profile.display_name == "jean.dupont"

    def test_user_profile_display_name_empty(self):
        """Teste display_name sans infos."""
        from src.services.auth import UserProfile
        
        profile = UserProfile()
        
        assert profile.display_name == "Utilisateur"


class TestAuthResult:
    """Tests du modèle AuthResult."""

    def test_auth_result_default(self):
        """Teste les valeurs par défaut."""
        from src.services.auth import AuthResult
        
        result = AuthResult()
        
        assert result.success is False
        assert result.user is None
        assert result.message == ""
        assert result.error_code is None

    def test_auth_result_success(self):
        """Teste un résultat de succès."""
        from src.services.auth import AuthResult, UserProfile
        
        user = UserProfile(email="test@example.com")
        result = AuthResult(
            success=True,
            user=user,
            message="Connexion réussie"
        )
        
        assert result.success is True
        assert result.user.email == "test@example.com"
        assert result.message == "Connexion réussie"

    def test_auth_result_failure(self):
        """Teste un résultat d'échec."""
        from src.services.auth import AuthResult
        
        result = AuthResult(
            success=False,
            message="Mot de passe invalide",
            error_code="INVALID_PASSWORD"
        )
        
        assert result.success is False
        assert result.user is None
        assert result.error_code == "INVALID_PASSWORD"


# ═══════════════════════════════════════════════════════════════════════════
# TESTS GARMIN CONFIG
# ═══════════════════════════════════════════════════════════════════════════


class TestGarminConfig:
    """Tests de la configuration Garmin."""

    def test_garmin_config_dataclass_import(self):
        """Teste que GarminConfig s'importe."""
        from src.services.garmin_sync import GarminConfig
        
        assert GarminConfig is not None

    def test_garmin_config_default_urls(self):
        """Teste les URLs par défaut."""
        from src.services.garmin_sync import GarminConfig
        
        config = GarminConfig(
            consumer_key="test_key",
            consumer_secret="test_secret"
        )
        
        assert "garmin.com" in config.request_token_url
        assert "garmin.com" in config.authorize_url
        assert "garmin.com" in config.access_token_url
        assert "garmin.com" in config.api_base_url

    def test_garmin_config_custom_urls(self):
        """Teste avec URLs personnalisées."""
        from src.services.garmin_sync import GarminConfig
        
        config = GarminConfig(
            consumer_key="key",
            consumer_secret="secret",
            request_token_url="https://custom.com/request",
            authorize_url="https://custom.com/authorize"
        )
        
        assert config.request_token_url == "https://custom.com/request"
        assert config.authorize_url == "https://custom.com/authorize"


class TestGetGarminConfig:
    """Tests de get_garmin_config."""

    def test_get_garmin_config_returns_config(self):
        """Teste que get_garmin_config retourne un GarminConfig."""
        from src.services.garmin_sync import get_garmin_config, GarminConfig
        
        config = get_garmin_config()
        
        assert isinstance(config, GarminConfig)

    def test_get_garmin_config_has_keys(self):
        """Teste que la config a les clés."""
        from src.services.garmin_sync import get_garmin_config
        
        config = get_garmin_config()
        
        # Les clés peuvent être vides si non configurées
        assert hasattr(config, 'consumer_key')
        assert hasattr(config, 'consumer_secret')


class TestGarminServiceInit:
    """Tests d'initialisation de GarminService."""

    def test_garmin_service_import(self):
        """Teste l'import de GarminService."""
        from src.services.garmin_sync import GarminService
        
        assert GarminService is not None

    def test_garmin_service_init_default(self):
        """Teste l'initialisation avec config par défaut."""
        from src.services.garmin_sync import GarminService
        
        service = GarminService()
        
        assert service.config is not None
        assert service._oauth_session is None
        assert service._temp_request_token is None

    def test_garmin_service_init_custom_config(self):
        """Teste l'initialisation avec config personnalisée."""
        from src.services.garmin_sync import GarminService, GarminConfig
        
        custom_config = GarminConfig(
            consumer_key="my_key",
            consumer_secret="my_secret"
        )
        
        service = GarminService(config=custom_config)
        
        assert service.config.consumer_key == "my_key"
        assert service.config.consumer_secret == "my_secret"


# ═══════════════════════════════════════════════════════════════════════════
# TESTS BASE AI SERVICE
# ═══════════════════════════════════════════════════════════════════════════


class TestBaseAIServiceImport:
    """Tests d'import du BaseAIService."""

    def test_import_base_ai_service(self):
        """Teste l'import de BaseAIService."""
        from src.services.base_ai_service import BaseAIService
        
        assert BaseAIService is not None

    def test_base_ai_service_has_call_method(self):
        """Teste que BaseAIService a une méthode call."""
        from src.services.base_ai_service import BaseAIService
        
        # Vérifie qu'une des méthodes d'appel IA existe
        assert hasattr(BaseAIService, 'call_with_list_parsing_sync') or hasattr(BaseAIService, '_call_ia')


class TestBaseAIServiceMixins:
    """Tests des mixins IA."""

    def test_recipe_ai_mixin_exists(self):
        """Teste que RecipeAIMixin existe."""
        from src.services.base_ai_service import RecipeAIMixin
        
        assert RecipeAIMixin is not None

    def test_planning_ai_mixin_exists(self):
        """Teste que PlanningAIMixin existe."""
        from src.services.base_ai_service import PlanningAIMixin
        
        assert PlanningAIMixin is not None

    def test_inventory_ai_mixin_exists(self):
        """Teste que InventoryAIMixin existe."""
        from src.services.base_ai_service import InventoryAIMixin
        
        assert InventoryAIMixin is not None


# ═══════════════════════════════════════════════════════════════════════════
# TESTS PREDICTIONS SERVICE
# ═══════════════════════════════════════════════════════════════════════════


class TestPredictionsServiceImport:
    """Tests d'import du service predictions."""

    def test_import_predictions_module(self):
        """Teste l'import du module predictions."""
        from src.services import predictions
        
        assert predictions is not None


# ═══════════════════════════════════════════════════════════════════════════
# TESTS SUGGESTIONS IA SERVICE
# ═══════════════════════════════════════════════════════════════════════════


class TestSuggestionsIAServiceImport:
    """Tests d'import du service suggestions IA."""

    def test_import_suggestions_ia_module(self):
        """Teste l'import du module suggestions_ia."""
        from src.services import suggestions_ia
        
        assert suggestions_ia is not None


# ═══════════════════════════════════════════════════════════════════════════
# TESTS USER PREFERENCES SERVICE
# ═══════════════════════════════════════════════════════════════════════════


class TestUserPreferencesServiceImport:
    """Tests d'import du service user preferences."""

    def test_import_user_preferences_module(self):
        """Teste l'import du module user_preferences."""
        from src.services import user_preferences
        
        assert user_preferences is not None


# ═══════════════════════════════════════════════════════════════════════════
# TESTS RAPPORTS PDF SERVICE
# ═══════════════════════════════════════════════════════════════════════════


class TestRapportsPDFServiceImport:
    """Tests d'import du service rapports PDF."""

    def test_import_rapports_pdf_module(self):
        """Teste l'import du module rapports_pdf."""
        from src.services import rapports_pdf
        
        assert rapports_pdf is not None


# ═══════════════════════════════════════════════════════════════════════════
# TESTS CALENDAR SYNC SERVICE
# ═══════════════════════════════════════════════════════════════════════════


class TestCalendarSyncServiceImport:
    """Tests d'import du service calendar sync."""

    def test_import_calendar_sync_module(self):
        """Teste l'import du module calendar_sync."""
        from src.services import calendar_sync
        
        assert calendar_sync is not None


# ═══════════════════════════════════════════════════════════════════════════
# TESTS BATCH COOKING SERVICE
# ═══════════════════════════════════════════════════════════════════════════


class TestBatchCookingServiceImport:
    """Tests d'import du service batch cooking."""

    def test_import_batch_cooking_module(self):
        """Teste l'import du module batch_cooking."""
        from src.services import batch_cooking
        
        assert batch_cooking is not None


# ═══════════════════════════════════════════════════════════════════════════
# TESTS BUDGET SERVICE
# ═══════════════════════════════════════════════════════════════════════════


class TestBudgetServiceImport:
    """Tests d'import du service budget."""

    def test_import_budget_module(self):
        """Teste l'import du module budget."""
        from src.services import budget
        
        assert budget is not None


# ═══════════════════════════════════════════════════════════════════════════
# TESTS BACKUP SERVICE
# ═══════════════════════════════════════════════════════════════════════════


class TestBackupServiceImport:
    """Tests d'import du service backup."""

    def test_import_backup_module(self):
        """Teste l'import du module backup."""
        from src.services import backup
        
        assert backup is not None


# ═══════════════════════════════════════════════════════════════════════════
# TESTS BARCODE SERVICE
# ═══════════════════════════════════════════════════════════════════════════


class TestBarcodeServiceImport:
    """Tests d'import du service barcode."""

    def test_import_barcode_module(self):
        """Teste l'import du module barcode."""
        from src.services import barcode
        
        assert barcode is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
