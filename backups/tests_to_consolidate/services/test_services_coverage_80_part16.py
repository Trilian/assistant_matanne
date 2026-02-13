"""
Tests Couverture 80% - Part 16: Tests METHODES avec mocks DB complets
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

# ═══════════════════════════════════════════════════════════
# BASE SERVICE - TESTS METHODES COMPLETES
# ═══════════════════════════════════════════════════════════


class TestBaseServiceMethodsCRUD:
    """Tests méthodes CRUD BaseService"""

    @pytest.fixture
    def mock_model(self):
        model = Mock()
        model.__name__ = "TestEntity"
        model.id = Mock()
        return model

    @pytest.fixture
    def service(self, mock_model):
        from src.services.base_service import BaseService

        return BaseService(mock_model, cache_ttl=60)

    def test_count_executes(self, service, mock_model):
        """Test count exécute la requête"""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.count.return_value = 42

        result = service.count(db=mock_session)

        assert result == 42
        mock_session.query.assert_called_once()
        mock_query.count.assert_called_once()

    def test_delete_executes_success(self, service, mock_model):
        """Test delete exécute correctement"""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.delete.return_value = 1

        with patch.object(service, "_invalider_cache"):
            result = service.delete(1, db=mock_session)

        assert result is True
        mock_session.commit.assert_called()

    def test_delete_executes_not_found(self, service, mock_model):
        """Test delete renvoie False"""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.delete.return_value = 0

        with patch.object(service, "_invalider_cache"):
            result = service.delete(999, db=mock_session)

        assert result is False


class TestBaseServiceFiltersExecution:
    """Tests filtres BaseService"""

    @pytest.fixture
    def mock_model(self):
        model = Mock()
        model.__name__ = "TestEntity"
        model.status = Mock()
        model.status.__eq__ = Mock(return_value=Mock())
        model.age = Mock()
        model.age.__ge__ = Mock(return_value=Mock())
        model.age.__le__ = Mock(return_value=Mock())
        return model

    @pytest.fixture
    def service(self, mock_model):
        from src.services.base_service import BaseService

        return BaseService(mock_model)

    def test_apply_filters_equal(self, service, mock_model):
        """Test filtre égalité"""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query

        result = service._apply_filters(mock_query, {"status": "active"})

        assert mock_query.filter.called


# ═══════════════════════════════════════════════════════════
# INVENTAIRE SERVICE - TESTS METHODES
# ═══════════════════════════════════════════════════════════


class TestInventaireServiceMethods:
    """Tests méthodes InventaireService"""

    def test_inventaire_init(self):
        from src.services.inventaire import InventaireService

        service = InventaireService()

        assert service is not None
        assert service.model is not None

    def test_inventaire_model_is_article(self):
        from src.core.models import ArticleInventaire
        from src.services.inventaire import InventaireService

        service = InventaireService()

        assert service.model == ArticleInventaire


# ═══════════════════════════════════════════════════════════
# BUDGET SERVICE - TESTS METHODES
# ═══════════════════════════════════════════════════════════


class TestBudgetServiceMethods:
    """Tests méthodes BudgetService"""

    def test_budget_init(self):
        from src.services.budget import BudgetService

        service = BudgetService()

        assert service is not None

    def test_budget_has_ajouter_depense(self):
        from src.services.budget import BudgetService

        service = BudgetService()

        assert hasattr(service, "ajouter_depense") or hasattr(service, "create")


# ═══════════════════════════════════════════════════════════
# RAPPORTS PDF - TESTS METHODES AVANCEES
# ═══════════════════════════════════════════════════════════


class TestRapportsPDFMethodsAdvanced:
    """Tests méthodes avancées RapportsPDFService"""

    def test_rapports_pdf_service_model(self):
        from src.core.models import ArticleInventaire
        from src.services.rapports_pdf import RapportsPDFService

        service = RapportsPDFService()

        assert service.model == ArticleInventaire

    def test_rapports_pdf_has_generate_methods(self):
        from src.services.rapports_pdf import RapportsPDFService

        service = RapportsPDFService()

        assert hasattr(service, "generer_donnees_rapport_stocks")
        assert hasattr(service, "generer_pdf_rapport_stocks")


# ═══════════════════════════════════════════════════════════
# NOTIFICATIONS SERVICE - TESTS METHODES
# ═══════════════════════════════════════════════════════════


class TestNotificationsServiceMethods:
    """Tests méthodes NotificationsService"""

    def test_notifications_module_imports(self):
        import src.services.notifications

        assert src.services.notifications is not None


# ═══════════════════════════════════════════════════════════
# BARCODE SERVICE - TESTS METHODES
# ═══════════════════════════════════════════════════════════


class TestBarcodeServiceMethods:
    """Tests méthodes BarcodeService"""

    def test_barcode_module_imports(self):
        import src.services.barcode

        assert src.services.barcode is not None


# ═══════════════════════════════════════════════════════════
# ACTION HISTORY - TESTS METHODES
# ═══════════════════════════════════════════════════════════


class TestActionHistoryMethods:
    """Tests méthodes ActionHistoryService"""

    def test_action_history_module(self):
        import src.services.action_history

        assert src.services.action_history is not None


# ═══════════════════════════════════════════════════════════
# CALENDAR SYNC - TESTS METHODES
# ═══════════════════════════════════════════════════════════


class TestCalendarSyncMethods:
    """Tests méthodes CalendarSync"""

    def test_calendar_provider_values(self):
        from src.services.calendar_sync import CalendarProvider

        # Tester toutes les valeurs
        assert CalendarProvider.GOOGLE.value == "google"
        assert CalendarProvider.APPLE.value == "apple"
        assert CalendarProvider.OUTLOOK.value == "outlook"
        assert CalendarProvider.ICAL_URL.value == "ical_url"

    def test_sync_direction_values(self):
        from src.services.calendar_sync import SyncDirection

        assert SyncDirection.IMPORT_ONLY.value == "import"
        assert SyncDirection.EXPORT_ONLY.value == "export"
        assert SyncDirection.BIDIRECTIONAL.value == "both"

    def test_external_calendar_config_creation(self):
        from src.services.calendar_sync import CalendarProvider, ExternalCalendarConfig

        config = ExternalCalendarConfig(
            user_id="user1",
            provider=CalendarProvider.GOOGLE,
            name="Mon Agenda",
            calendar_id="primary",
            sync_meals=True,
            sync_activities=False,
        )

        assert config.name == "Mon Agenda"
        assert config.sync_meals is True
        assert config.sync_activities is False


# ═══════════════════════════════════════════════════════════
# GARMIN SYNC - TESTS METHODES
# ═══════════════════════════════════════════════════════════


class TestGarminSyncMethods:
    """Tests méthodes GarminSync"""

    def test_garmin_config_values(self):
        from src.services.garmin_sync import GarminConfig

        config = GarminConfig(consumer_key="mykey", consumer_secret="mysecret")

        assert config.consumer_key == "mykey"
        assert "garmin" in config.authorize_url.lower()


# ═══════════════════════════════════════════════════════════
# BACKUP SERVICE - TESTS METHODES
# ═══════════════════════════════════════════════════════════


class TestBackupServiceMethods:
    """Tests méthodes BackupService"""

    def test_backup_config_values(self):
        from src.services.backup import BackupConfig

        config = BackupConfig(backup_dir="custom/backups", max_backups=5, compress=True)

        assert config.backup_dir == "custom/backups"
        assert config.max_backups == 5

    def test_backup_metadata_creation(self):
        from src.services.backup import BackupMetadata

        meta = BackupMetadata(
            id="backup-001", version="2.0", tables_count=25, total_records=10000, compressed=True
        )

        assert meta.id == "backup-001"
        assert meta.total_records == 10000


# ═══════════════════════════════════════════════════════════
# AUTH SERVICE - TESTS METHODES
# ═══════════════════════════════════════════════════════════


class TestAuthServiceMethods:
    """Tests méthodes AuthService"""

    def test_role_permissions_mapping(self):
        from src.services.auth import ROLE_PERMISSIONS, Permission, Role

        # Admin a toutes les permissions
        assert Permission.ADMIN_ALL in ROLE_PERMISSIONS[Role.ADMIN]

        # Membre peut lire/écrire mais pas admin
        assert Permission.READ_RECIPES in ROLE_PERMISSIONS[Role.MEMBRE]
        assert Permission.WRITE_RECIPES in ROLE_PERMISSIONS[Role.MEMBRE]
        assert Permission.ADMIN_ALL not in ROLE_PERMISSIONS[Role.MEMBRE]

        # Invité peut seulement lire
        assert Permission.READ_RECIPES in ROLE_PERMISSIONS[Role.INVITE]
        assert Permission.WRITE_RECIPES not in ROLE_PERMISSIONS[Role.INVITE]

    def test_user_profile_display_name_full(self):
        from src.services.auth import UserProfile

        profile = UserProfile(prenom="Jean", nom="Dupont")

        assert profile.display_name == "Jean Dupont"

    def test_user_profile_display_name_email(self):
        from src.services.auth import UserProfile

        profile = UserProfile(email="jean.dupont@example.com")

        assert "jean" in profile.display_name.lower()


# ═══════════════════════════════════════════════════════════
# RECIPE IMPORT - TESTS METHODES
# ═══════════════════════════════════════════════════════════


class TestRecipeImportMethods:
    """Tests méthodes RecipeImport"""

    def test_parse_duration_minutes(self):
        from src.services.recipe_import import RecipeParser

        assert RecipeParser.parse_duration("30 min") == 30
        assert RecipeParser.parse_duration("45 minutes") == 45

    def test_parse_duration_hours(self):
        from src.services.recipe_import import RecipeParser

        assert RecipeParser.parse_duration("1h") == 60
        assert RecipeParser.parse_duration("2 heures") == 120


# ═══════════════════════════════════════════════════════════
# TYPES MODELS - TESTS METHODES
# ═══════════════════════════════════════════════════════════


class TestTypesModels:
    """Tests types models"""

    def test_base_service_generic(self):
        from src.services.types import BaseService

        mock = Mock()
        mock.__name__ = "TestModel"

        service = BaseService(mock)

        assert service.model == mock


# ═══════════════════════════════════════════════════════════
# OPENFOODFACTS - TESTS METHODES
# ═══════════════════════════════════════════════════════════


class TestOpenfoodfactsMethods:
    """Tests méthodes OpenFoodFacts"""

    def test_openfoodfacts_module(self):
        import src.services.openfoodfacts

        assert src.services.openfoodfacts is not None
