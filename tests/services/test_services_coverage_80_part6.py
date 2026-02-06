"""
Tests de couverture étendus pour src/services - Objectif 80%
Couvre: BaseService CRUD, RecetteService, CoursesService, PlanningService,
        InventaireService, NotificationService, BackupService, WeatherService
"""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import patch, MagicMock, Mock, PropertyMock
from io import StringIO
import json
import os


# ═══════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture
def mock_db_session():
    """Mock database session."""
    session = MagicMock()
    session.query.return_value = session
    session.filter.return_value = session
    session.filter_by.return_value = session
    session.order_by.return_value = session
    session.offset.return_value = session
    session.limit.return_value = session
    session.all.return_value = []
    session.first.return_value = None
    session.count.return_value = 0
    session.get.return_value = None
    return session


@pytest.fixture
def patch_db_context(mock_db_session):
    """Patch database context manager to use mock session."""
    from contextlib import contextmanager
    
    @contextmanager
    def mock_context():
        yield mock_db_session
    
    with patch('src.core.database.obtenir_contexte_db', mock_context), \
         patch('src.core.database.get_db_context', mock_context):
        yield mock_db_session


# ═══════════════════════════════════════════════════════════════════════════
# TESTS BASE SERVICE
# ═══════════════════════════════════════════════════════════════════════════


class TestBaseServiceImport:
    """Tests d'import du BaseService."""

    def test_import_base_service(self):
        """Teste l'import du module base_service."""
        from src.services import base_service
        assert base_service is not None

    def test_base_service_class_exists(self):
        """Teste que BaseService existe."""
        from src.services.base_service import BaseService
        assert BaseService is not None

    def test_base_service_is_generic(self):
        """Teste que BaseService est générique."""
        from src.services.base_service import BaseService
        from typing import Generic
        assert issubclass(BaseService, Generic)


class TestBaseServiceMethods:
    """Tests des méthodes du BaseService."""

    def test_base_service_init(self):
        """Teste l'initialisation du BaseService."""
        from src.services.base_service import BaseService
        from src.core.models import Recette
        
        service = BaseService(Recette, cache_ttl=120)
        
        assert service.model == Recette
        assert service.model_name == "Recette"
        assert service.cache_ttl == 120

    def test_base_service_default_cache_ttl(self):
        """Teste le TTL de cache par défaut."""
        from src.services.base_service import BaseService
        from src.core.models import Ingredient
        
        service = BaseService(Ingredient)
        assert service.cache_ttl == 60

    @patch('src.services.base_service.Cache')
    def test_invalider_cache_method(self, mock_cache, patch_db_context):
        """Teste la méthode _invalider_cache."""
        from src.services.base_service import BaseService
        from src.core.models import Recette
        
        service = BaseService(Recette)
        service._invalider_cache()
        
        # La méthode devrait exister et ne pas lever d'erreur


class TestBaseServiceCRUD:
    """Tests des opérations CRUD du BaseService."""

    def test_create_method_exists(self):
        """Teste que la méthode create existe."""
        from src.services.base_service import BaseService
        from src.core.models import Recette
        
        service = BaseService(Recette)
        assert hasattr(service, 'create')
        assert callable(service.create)

    def test_get_by_id_method_exists(self):
        """Teste que la méthode get_by_id existe."""
        from src.services.base_service import BaseService
        from src.core.models import Recette
        
        service = BaseService(Recette)
        assert hasattr(service, 'get_by_id')
        assert callable(service.get_by_id)

    def test_get_all_method_exists(self):
        """Teste que la méthode get_all existe."""
        from src.services.base_service import BaseService
        from src.core.models import Recette
        
        service = BaseService(Recette)
        assert hasattr(service, 'get_all')
        assert callable(service.get_all)

    def test_update_method_exists(self):
        """Teste que la méthode update existe."""
        from src.services.base_service import BaseService
        from src.core.models import Recette
        
        service = BaseService(Recette)
        assert hasattr(service, 'update')
        assert callable(service.update)

    def test_delete_method_exists(self):
        """Teste que la méthode delete existe."""
        from src.services.base_service import BaseService
        from src.core.models import Recette
        
        service = BaseService(Recette)
        assert hasattr(service, 'delete')
        assert callable(service.delete)

    def test_count_method_exists(self):
        """Teste que la méthode count existe."""
        from src.services.base_service import BaseService
        from src.core.models import Recette
        
        service = BaseService(Recette)
        assert hasattr(service, 'count')
        assert callable(service.count)

    def test_advanced_search_method_exists(self):
        """Teste que la méthode advanced_search existe."""
        from src.services.base_service import BaseService
        from src.core.models import Recette
        
        service = BaseService(Recette)
        assert hasattr(service, 'advanced_search')
        assert callable(service.advanced_search)


# ═══════════════════════════════════════════════════════════════════════════
# TESTS NOTIFICATION SERVICE
# ═══════════════════════════════════════════════════════════════════════════


class TestNotificationServiceImport:
    """Tests d'import du NotificationService."""

    def test_import_notifications_module(self):
        """Teste l'import du module notifications."""
        from src.services import notifications
        assert notifications is not None

    def test_notification_service_class_exists(self):
        """Teste que NotificationService existe."""
        from src.services.notifications import NotificationService
        assert NotificationService is not None

    def test_notification_model_exists(self):
        """Teste que le modèle Notification existe."""
        from src.services.notifications import Notification
        assert Notification is not None

    def test_type_alerte_enum_exists(self):
        """Teste que l'enum TypeAlerte existe."""
        from src.services.notifications import TypeAlerte
        assert TypeAlerte is not None


class TestNotificationServiceInit:
    """Tests d'initialisation du NotificationService."""

    def test_notification_service_init(self):
        """Teste l'initialisation du service."""
        from src.services.notifications import NotificationService
        
        service = NotificationService()
        
        assert hasattr(service, 'notifications')
        assert hasattr(service, '_next_id')
        assert service._next_id == 1
        assert isinstance(service.notifications, dict)

    def test_notification_service_empty_by_default(self):
        """Teste que le service est vide par défaut."""
        from src.services.notifications import NotificationService
        
        service = NotificationService()
        
        assert len(service.notifications) == 0


class TestNotificationCreation:
    """Tests de création de notifications."""

    def test_creer_notification_stock_critique(self):
        """Teste la création d'une notification stock critique."""
        from src.services.notifications import NotificationService, TypeAlerte
        
        service = NotificationService()
        
        article = {
            'id': 1,
            'ingredient_id': 10,
            'nom': 'Lait',
            'quantite': 0,
            'quantite_min': 2,
            'unite': 'L'
        }
        
        notif = service.creer_notification_stock_critique(article)
        
        assert notif is not None
        assert notif.type_alerte == TypeAlerte.STOCK_CRITIQUE
        assert notif.article_id == 1
        assert notif.ingredient_id == 10
        assert 'CRITIQUE' in notif.message
        assert notif.priorite == 'haute'
        assert notif.icone == '❌'

    def test_creer_notification_stock_bas(self):
        """Teste la création d'une notification stock bas."""
        from src.services.notifications import NotificationService, TypeAlerte
        
        service = NotificationService()
        
        article = {
            'id': 2,
            'ingredient_id': 20,
            'nom': 'Oeufs',
            'quantite': 2,
            'quantite_min': 6,
            'unite': 'unités'
        }
        
        notif = service.creer_notification_stock_bas(article)
        
        assert notif is not None
        assert notif.type_alerte == TypeAlerte.STOCK_BAS
        assert notif.article_id == 2
        assert 'ALERTE' in notif.message
        assert notif.priorite == 'moyenne'
        assert notif.icone == '⚠️'

    def test_creer_notification_peremption_depassee(self):
        """Teste la création d'une notification péremption dépassée."""
        from src.services.notifications import NotificationService, TypeAlerte
        
        service = NotificationService()
        
        article = {
            'id': 3,
            'ingredient_id': 30,
            'nom': 'Yaourt',
            'date_peremption': '2026-01-01'
        }
        
        notif = service.creer_notification_peremption(article, jours_avant=-2)
        
        assert notif is not None
        assert notif.type_alerte == TypeAlerte.PEREMPTION_DEPASSEE
        assert 'EXPIRÉ' in notif.titre
        assert notif.priorite == 'haute'
        assert notif.icone == '🚨'

    def test_creer_notification_peremption_tres_proche(self):
        """Teste la création d'une notification péremption très proche."""
        from src.services.notifications import NotificationService, TypeAlerte
        
        service = NotificationService()
        
        article = {
            'id': 4,
            'ingredient_id': 40,
            'nom': 'Fromage',
            'date_peremption': '2026-02-08'
        }
        
        notif = service.creer_notification_peremption(article, jours_avant=2)
        
        assert notif is not None
        assert notif.type_alerte == TypeAlerte.PEREMPTION_PROCHE
        assert 'très proche' in notif.titre
        assert notif.priorite == 'haute'
        assert notif.icone == '🔴'

    def test_creer_notification_peremption_proche(self):
        """Teste la création d'une notification péremption proche (>3 jours)."""
        from src.services.notifications import NotificationService, TypeAlerte
        
        service = NotificationService()
        
        article = {
            'id': 5,
            'ingredient_id': 50,
            'nom': 'Jambon',
            'date_peremption': '2026-02-12'
        }
        
        notif = service.creer_notification_peremption(article, jours_avant=5)
        
        assert notif is not None
        assert notif.type_alerte == TypeAlerte.PEREMPTION_PROCHE
        assert 'proche' in notif.titre.lower()
        assert notif.priorite == 'moyenne'
        assert notif.icone == '🟠'


class TestNotificationManagement:
    """Tests de gestion des notifications."""

    def test_ajouter_notification(self):
        """Teste l'ajout d'une notification."""
        from src.services.notifications import NotificationService, Notification, TypeAlerte
        
        service = NotificationService()
        
        notif = Notification(
            type_alerte=TypeAlerte.STOCK_BAS,
            article_id=1,
            ingredient_id=10,
            titre="Test notification",
            message="Ceci est un test de notification"
        )
        
        result = service.ajouter_notification(notif, utilisateur_id=1)
        
        assert result is not None
        assert result.id is not None
        assert 1 in service.notifications
        assert len(service.notifications[1]) == 1

    def test_ajouter_notification_evite_doublons(self):
        """Teste que l'ajout évite les doublons."""
        from src.services.notifications import NotificationService, Notification, TypeAlerte
        
        service = NotificationService()
        
        notif1 = Notification(
            type_alerte=TypeAlerte.STOCK_BAS,
            article_id=1,
            ingredient_id=10,
            titre="Test notification 1",
            message="Message long 1 pour le test"
        )
        
        notif2 = Notification(
            type_alerte=TypeAlerte.STOCK_BAS,
            article_id=1,
            ingredient_id=10,
            titre="Test notification 2",
            message="Message long 2 différent du premier"
        )
        
        service.ajouter_notification(notif1, utilisateur_id=1)
        result = service.ajouter_notification(notif2, utilisateur_id=1)
        
        # Devrait retourner la première notification (pas de doublon)
        assert result.titre == "Test notification 1"
        assert len(service.notifications[1]) == 1


class TestTypeAlerteEnum:
    """Tests de l'énumération TypeAlerte."""

    def test_type_alerte_values(self):
        """Teste les valeurs de l'enum TypeAlerte."""
        from src.services.notifications import TypeAlerte
        
        assert TypeAlerte.STOCK_CRITIQUE.value == "stock_critique"
        assert TypeAlerte.STOCK_BAS.value == "stock_bas"
        assert TypeAlerte.PEREMPTION_PROCHE.value == "peremption_proche"
        assert TypeAlerte.PEREMPTION_DEPASSEE.value == "peremption_depassee"
        assert TypeAlerte.ARTICLE_AJOUTE.value == "article_ajoute"
        assert TypeAlerte.ARTICLE_MODIFIE.value == "article_modifie"


class TestNotificationModel:
    """Tests du modèle Notification."""

    def test_notification_creation(self):
        """Teste la création d'une Notification."""
        from src.services.notifications import Notification, TypeAlerte
        
        notif = Notification(
            type_alerte=TypeAlerte.STOCK_BAS,
            article_id=1,
            ingredient_id=10,
            titre="Test titre",
            message="Test message long enough"
        )
        
        assert notif.type_alerte == TypeAlerte.STOCK_BAS
        assert notif.article_id == 1
        assert notif.lue is False
        assert notif.priorite == "moyenne"
        assert notif.push_envoyee is False

    def test_notification_with_all_fields(self):
        """Teste la création avec tous les champs."""
        from src.services.notifications import Notification, TypeAlerte
        from datetime import datetime, timezone
        
        now = datetime.now(timezone.utc)
        
        notif = Notification(
            id=42,
            type_alerte=TypeAlerte.STOCK_CRITIQUE,
            article_id=5,
            ingredient_id=50,
            titre="Titre complet",
            message="Message complet avec détails",
            icone="⚠️",
            date_creation=now,
            lue=True,
            priorite="haute",
            email="test@example.com",
            push_envoyee=True
        )
        
        assert notif.id == 42
        assert notif.lue is True
        assert notif.email == "test@example.com"
        assert notif.push_envoyee is True


# ═══════════════════════════════════════════════════════════════════════════
# TESTS BACKUP SERVICE
# ═══════════════════════════════════════════════════════════════════════════


class TestBackupModels:
    """Tests des modèles de backup."""

    def test_backup_config_defaults(self):
        """Teste les valeurs par défaut de BackupConfig."""
        from src.services.backup import BackupConfig
        
        config = BackupConfig()
        
        assert config.backup_dir == "backups"
        assert config.max_backups == 10
        assert config.compress is True
        assert config.auto_backup_enabled is True
        assert config.auto_backup_interval_hours == 24

    def test_backup_config_custom(self):
        """Teste BackupConfig avec valeurs personnalisées."""
        from src.services.backup import BackupConfig
        
        config = BackupConfig(
            backup_dir="my_backups",
            max_backups=5,
            compress=False,
            auto_backup_enabled=False
        )
        
        assert config.backup_dir == "my_backups"
        assert config.max_backups == 5
        assert config.compress is False

    def test_backup_metadata_defaults(self):
        """Teste les valeurs par défaut de BackupMetadata."""
        from src.services.backup import BackupMetadata
        
        meta = BackupMetadata()
        
        assert meta.id == ""
        assert meta.version == "1.0"
        assert meta.tables_count == 0
        assert meta.total_records == 0
        assert meta.file_size_bytes == 0
        assert meta.compressed is False
        assert meta.checksum == ""

    def test_backup_result_defaults(self):
        """Teste les valeurs par défaut de BackupResult."""
        from src.services.backup import BackupResult
        
        result = BackupResult()
        
        assert result.success is False
        assert result.message == ""
        assert result.file_path is None
        assert result.metadata is None
        assert result.duration_seconds == 0.0

    def test_backup_result_success(self):
        """Teste BackupResult avec succès."""
        from src.services.backup import BackupResult, BackupMetadata
        
        meta = BackupMetadata(tables_count=5, total_records=100)
        
        result = BackupResult(
            success=True,
            message="Backup completed",
            file_path="/backups/backup_2026.json.gz",
            metadata=meta,
            duration_seconds=3.5
        )
        
        assert result.success is True
        assert result.metadata.tables_count == 5


# ═══════════════════════════════════════════════════════════════════════════
# TESTS WEATHER SERVICE
# ═══════════════════════════════════════════════════════════════════════════


class TestWeatherModels:
    """Tests des modèles météo."""

    def test_type_alert_meteo_enum(self):
        """Teste l'enum TypeAlertMeteo."""
        from src.services.weather import TypeAlertMeteo
        
        assert TypeAlertMeteo.GEL.value == "gel"
        assert TypeAlertMeteo.CANICULE.value == "canicule"
        assert TypeAlertMeteo.PLUIE_FORTE.value == "pluie_forte"
        assert TypeAlertMeteo.SECHERESSE.value == "sécheresse"
        assert TypeAlertMeteo.VENT_FORT.value == "vent_fort"
        assert TypeAlertMeteo.ORAGE.value == "orage"
        assert TypeAlertMeteo.GRELE.value == "grêle"
        assert TypeAlertMeteo.NEIGE.value == "neige"

    def test_niveau_alerte_enum(self):
        """Teste l'enum NiveauAlerte."""
        from src.services.weather import NiveauAlerte
        
        assert NiveauAlerte.INFO.value == "info"
        assert NiveauAlerte.ATTENTION.value == "attention"
        assert NiveauAlerte.DANGER.value == "danger"

    def test_meteo_jour_model(self):
        """Teste le modèle MeteoJour."""
        from src.services.weather import MeteoJour
        from datetime import date
        
        meteo = MeteoJour(
            date=date(2026, 2, 6),
            temperature_min=-2.0,
            temperature_max=8.0,
            temperature_moyenne=3.0,
            humidite=75,
            precipitation_mm=5.5,
            probabilite_pluie=60,
            vent_km_h=25.0,
            condition="nuageux"
        )
        
        assert meteo.date == date(2026, 2, 6)
        assert meteo.temperature_min == -2.0
        assert meteo.humidite == 75
        assert meteo.condition == "nuageux"

    def test_alerte_meteo_model(self):
        """Teste le modèle AlerteMeteo."""
        from src.services.weather import AlerteMeteo, TypeAlertMeteo, NiveauAlerte
        from datetime import date
        
        alerte = AlerteMeteo(
            type_alerte=TypeAlertMeteo.GEL,
            niveau=NiveauAlerte.DANGER,
            titre="Risque de gel",
            message="Gel attendu cette nuit",
            conseil_jardin="Protéger les plantes fragiles",
            date_debut=date(2026, 2, 6),
            temperature=-3.0
        )
        
        assert alerte.type_alerte == TypeAlertMeteo.GEL
        assert alerte.niveau == NiveauAlerte.DANGER
        assert alerte.temperature == -3.0

    def test_conseil_jardin_model(self):
        """Teste le modèle ConseilJardin."""
        from src.services.weather import ConseilJardin
        
        conseil = ConseilJardin(
            priorite=1,
            icone="🌱",
            titre="Arrosage",
            description="Arroser les plantes ce matin",
            plantes_concernees=["Tomates", "Salades"],
            action_recommandee="Arroser avant 10h"
        )
        
        assert conseil.priorite == 1
        assert len(conseil.plantes_concernees) == 2
        assert "Tomates" in conseil.plantes_concernees


# ═══════════════════════════════════════════════════════════════════════════
# TESTS RECETTE SERVICE
# ═══════════════════════════════════════════════════════════════════════════


class TestRecetteServiceImport:
    """Tests d'import du RecetteService."""

    def test_import_recettes_module(self):
        """Teste l'import du module recettes."""
        from src.services import recettes
        assert recettes is not None

    def test_recette_service_class_exists(self):
        """Teste que RecetteService existe."""
        from src.services.recettes import RecetteService
        assert RecetteService is not None

    def test_recette_suggestion_model_exists(self):
        """Teste que RecetteSuggestion existe."""
        from src.services.recettes import RecetteSuggestion
        assert RecetteSuggestion is not None


class TestRecetteSuggestionModel:
    """Tests du modèle RecetteSuggestion."""

    def test_recette_suggestion_valid(self):
        """Teste une suggestion de recette valide."""
        from src.services.recettes import RecetteSuggestion
        
        suggestion = RecetteSuggestion(
            nom="Poulet rôti aux herbes",
            description="Un délicieux poulet rôti avec des herbes de Provence",
            temps_preparation=20,
            temps_cuisson=60,
            portions=4,
            difficulte="moyen",
            type_repas="dîner",
            saison="toute_année",
            ingredients=[{"nom": "Poulet", "quantite": 1}],
            etapes=[{"etape": "Préchauffer le four"}]
        )
        
        assert suggestion.nom == "Poulet rôti aux herbes"
        assert suggestion.temps_preparation == 20
        assert suggestion.difficulte == "moyen"

    def test_recette_suggestion_float_to_int_conversion(self):
        """Teste la conversion float vers int."""
        from src.services.recettes import RecetteSuggestion
        
        # Mistral peut retourner des floats pour ces valeurs
        suggestion = RecetteSuggestion(
            nom="Pâtes carbonara",
            description="Des pâtes carbonara crémeuses et délicieuses",
            temps_preparation=15.0,  # Float
            temps_cuisson=20.0,  # Float
            portions=4.0,  # Float
            difficulte="facile",
            type_repas="dîner",
            ingredients=[{"nom": "Pâtes", "quantite": 500}],
            etapes=[{"etape": "Cuire les pâtes"}]
        )
        
        assert isinstance(suggestion.temps_preparation, int)
        assert suggestion.temps_preparation == 15
        assert isinstance(suggestion.temps_cuisson, int)
        assert suggestion.temps_cuisson == 20
        assert isinstance(suggestion.portions, int)
        assert suggestion.portions == 4


class TestVersionBebeGeneree:
    """Tests du modèle VersionBebeGeneree."""

    def test_version_bebe_valid(self):
        """Teste une version bébé valide."""
        from src.services.recettes import VersionBebeGeneree
        
        version = VersionBebeGeneree(
            instructions_modifiees="Mixer finement les légumes",
            notes_bebe="Adapté pour bébé de 8 mois",
            age_minimum_mois=8
        )
        
        assert version.age_minimum_mois == 8
        assert "Mixer" in version.instructions_modifiees

    def test_version_bebe_float_conversion(self):
        """Teste la conversion float pour age_minimum_mois."""
        from src.services.recettes import VersionBebeGeneree
        
        version = VersionBebeGeneree(
            instructions_modifiees="Instructions adaptées",
            notes_bebe="Notes pour bébé",
            age_minimum_mois=12.0  # Float
        )
        
        assert isinstance(version.age_minimum_mois, int)
        assert version.age_minimum_mois == 12


class TestVersionBatchCookingGeneree:
    """Tests du modèle VersionBatchCookingGeneree."""

    def test_version_batch_cooking_valid(self):
        """Teste une version batch cooking valide."""
        from src.services.recettes import VersionBatchCookingGeneree
        
        version = VersionBatchCookingGeneree(
            instructions_modifiees="Préparer en grande quantité",
            nombre_portions_recommande=12,
            temps_preparation_total_heures=3.5,
            conseils_conservation="Au frigo 5 jours",
            conseils_congelation="Se congèle très bien",
            calendrier_preparation="Préparer le dimanche"
        )
        
        assert version.nombre_portions_recommande == 12
        assert version.temps_preparation_total_heures == 3.5


class TestVersionRobotGeneree:
    """Tests du modèle VersionRobotGeneree."""

    def test_version_robot_valid(self):
        """Teste une version robot valide."""
        from src.services.recettes import VersionRobotGeneree
        
        version = VersionRobotGeneree(
            instructions_modifiees="Utiliser le programme pâtes",
            reglages_robot="Vitesse 5, 10 minutes",
            temps_cuisson_adapte_minutes=45,
            conseils_preparation="Couper les légumes en morceaux",
            etapes_specifiques=["Étape 1", "Étape 2"]
        )
        
        assert version.temps_cuisson_adapte_minutes == 45
        assert len(version.etapes_specifiques) == 2


# ═══════════════════════════════════════════════════════════════════════════
# TESTS COURSES SERVICE
# ═══════════════════════════════════════════════════════════════════════════


class TestCoursesServiceImport:
    """Tests d'import du CoursesService."""

    def test_import_courses_module(self):
        """Teste l'import du module courses."""
        from src.services import courses
        assert courses is not None

    def test_courses_service_class_exists(self):
        """Teste que CoursesService existe."""
        from src.services.courses import CoursesService
        assert CoursesService is not None


class TestSuggestionCoursesModel:
    """Tests du modèle SuggestionCourses."""

    def test_suggestion_courses_valid(self):
        """Teste une suggestion de courses valide."""
        from src.services.courses import SuggestionCourses
        
        suggestion = SuggestionCourses(
            nom="Lait",
            quantite=2.0,
            unite="L",
            priorite="haute",
            rayon="Produits frais"
        )
        
        assert suggestion.nom == "Lait"
        assert suggestion.quantite == 2.0
        assert suggestion.priorite == "haute"

    def test_suggestion_courses_field_aliases(self):
        """Teste la normalisation des aliases de champs."""
        from src.services.courses import SuggestionCourses
        
        # Test avec aliases alternatifs
        data = {
            'article': 'Pain',  # alias pour nom
            'quantity': 1.0,    # alias pour quantite
            'unit': 'unité',    # alias pour unite
            'priority': 'high', # alias pour priorite (sera normalisé en 'haute')
            'section': 'Boulangerie'  # alias pour rayon
        }
        
        suggestion = SuggestionCourses.model_validate(data)
        
        assert suggestion.nom == 'Pain'
        assert suggestion.quantite == 1.0
        assert suggestion.priorite == 'haute'
        assert suggestion.rayon == 'Boulangerie'


# ═══════════════════════════════════════════════════════════════════════════
# TESTS PLANNING SERVICE
# ═══════════════════════════════════════════════════════════════════════════


class TestPlanningServiceImport:
    """Tests d'import du PlanningService."""

    def test_import_planning_module(self):
        """Teste l'import du module planning."""
        from src.services import planning
        assert planning is not None

    def test_planning_service_class_exists(self):
        """Teste que PlanningService existe."""
        from src.services.planning import PlanningService
        assert PlanningService is not None


class TestPlanningModels:
    """Tests des modèles de planning."""

    def test_jour_planning_valid(self):
        """Teste un jour de planning valide."""
        from src.services.planning import JourPlanning
        
        jour = JourPlanning(
            jour="2026-02-06",
            dejeuner="Salade composée",
            diner="Poulet rôti"
        )
        
        assert jour.jour == "2026-02-06"
        assert jour.dejeuner == "Salade composée"

    def test_parametres_equilibre_defaults(self):
        """Teste les valeurs par défaut de ParametresEquilibre."""
        from src.services.planning import ParametresEquilibre
        
        params = ParametresEquilibre()
        
        assert "lundi" in params.poisson_jours
        assert "jeudi" in params.poisson_jours
        assert "mardi" in params.viande_rouge_jours
        assert "mercredi" in params.vegetarien_jours
        assert params.pates_riz_count == 3

    def test_parametres_equilibre_custom(self):
        """Teste ParametresEquilibre avec valeurs perso."""
        from src.services.planning import ParametresEquilibre
        
        params = ParametresEquilibre(
            poisson_jours=["vendredi"],
            viande_rouge_jours=["samedi"],
            vegetarien_jours=["lundi", "mercredi"],
            pates_riz_count=2,
            ingredients_exclus=["fruits de mer", "noix"]
        )
        
        assert params.poisson_jours == ["vendredi"]
        assert len(params.vegetarien_jours) == 2
        assert "noix" in params.ingredients_exclus


# ═══════════════════════════════════════════════════════════════════════════
# TESTS INVENTAIRE SERVICE
# ═══════════════════════════════════════════════════════════════════════════


class TestInventaireServiceImport:
    """Tests d'import du InventaireService."""

    def test_import_inventaire_module(self):
        """Teste l'import du module inventaire."""
        from src.services import inventaire
        assert inventaire is not None

    def test_inventaire_service_class_exists(self):
        """Teste que InventaireService existe."""
        from src.services.inventaire import InventaireService
        assert InventaireService is not None

    def test_categories_constant(self):
        """Teste les catégories définies."""
        from src.services.inventaire import CATEGORIES
        
        assert "Légumes" in CATEGORIES
        assert "Fruits" in CATEGORIES
        assert "Protéines" in CATEGORIES
        assert len(CATEGORIES) >= 5

    def test_emplacements_constant(self):
        """Teste les emplacements définis."""
        from src.services.inventaire import EMPLACEMENTS
        
        assert "Frigo" in EMPLACEMENTS
        assert "Congélateur" in EMPLACEMENTS
        assert "Placard" in EMPLACEMENTS


class TestArticleImportModel:
    """Tests du modèle ArticleImport."""

    def test_article_import_valid(self):
        """Teste un article import valide."""
        from src.services.inventaire import ArticleImport
        
        article = ArticleImport(
            nom="Tomates",
            quantite=5.0,
            quantite_min=2.0,
            unite="kg",
            categorie="Légumes",
            emplacement="Frigo",
            date_peremption="2026-02-15"
        )
        
        assert article.nom == "Tomates"
        assert article.quantite == 5.0
        assert article.categorie == "Légumes"

    def test_article_import_minimal(self):
        """Teste un article import minimal."""
        from src.services.inventaire import ArticleImport
        
        article = ArticleImport(
            nom="Sel",
            quantite=1.0,
            quantite_min=0.5,
            unite="kg"
        )
        
        assert article.nom == "Sel"
        assert article.categorie is None
        assert article.emplacement is None
        assert article.date_peremption is None


# ═══════════════════════════════════════════════════════════════════════════
# TESTS SERVICES FACTORIES
# ═══════════════════════════════════════════════════════════════════════════


class TestServiceFactories:
    """Tests des factory functions des services."""

    def test_get_recette_service_factory(self):
        """Teste la factory get_recette_service."""
        try:
            from src.services.recettes import get_recette_service
            service = get_recette_service()
            assert service is not None
        except ImportError:
            pytest.skip("Factory not available")

    def test_get_courses_service_factory(self):
        """Teste la factory get_courses_service."""
        try:
            from src.services.courses import get_courses_service
            service = get_courses_service()
            assert service is not None
        except ImportError:
            pytest.skip("Factory not available")

    def test_get_planning_service_factory(self):
        """Teste la factory get_planning_service."""
        try:
            from src.services.planning import get_planning_service
            service = get_planning_service()
            assert service is not None
        except ImportError:
            pytest.skip("Factory not available")

    def test_get_inventaire_service_factory(self):
        """Teste la factory get_inventaire_service."""
        try:
            from src.services.inventaire import get_inventaire_service
            service = get_inventaire_service()
            assert service is not None
        except ImportError:
            pytest.skip("Factory not available")


# ═══════════════════════════════════════════════════════════════════════════
# TESTS OTHER SERVICES
# ═══════════════════════════════════════════════════════════════════════════


class TestOtherServicesImport:
    """Tests d'import des autres services."""

    def test_import_auth_service(self):
        """Teste l'import du module auth."""
        from src.services import auth
        assert auth is not None

    def test_import_barcode_service(self):
        """Teste l'import du module barcode."""
        from src.services import barcode
        assert barcode is not None

    def test_import_budget_service(self):
        """Teste l'import du module budget."""
        from src.services import budget
        assert budget is not None

    def test_import_batch_cooking_service(self):
        """Teste l'import du module batch_cooking."""
        from src.services import batch_cooking
        assert batch_cooking is not None

    def test_import_calendar_sync_service(self):
        """Teste l'import du module calendar_sync."""
        from src.services import calendar_sync
        assert calendar_sync is not None

    def test_import_predictions_service(self):
        """Teste l'import du module predictions."""
        from src.services import predictions
        assert predictions is not None

    def test_import_rapports_pdf_service(self):
        """Teste l'import du module rapports_pdf."""
        from src.services import rapports_pdf
        assert rapports_pdf is not None

    def test_import_suggestions_ia_service(self):
        """Teste l'import du module suggestions_ia."""
        from src.services import suggestions_ia
        assert suggestions_ia is not None

    def test_import_user_preferences_service(self):
        """Teste l'import du module user_preferences."""
        from src.services import user_preferences
        assert user_preferences is not None

    def test_import_types_module(self):
        """Teste l'import du module types."""
        from src.services import types
        assert types is not None


class TestBaseAIService:
    """Tests du BaseAIService."""

    def test_import_base_ai_service(self):
        """Teste l'import du BaseAIService."""
        from src.services.base_ai_service import BaseAIService
        assert BaseAIService is not None

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


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
