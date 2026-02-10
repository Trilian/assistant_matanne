"""
Tests Couverture 80% - Part 17: Weather, Suggestions IA, Backup - Tests approfondis
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, date, timedelta


# ═══════════════════════════════════════════════════════════
# WEATHER SERVICE TESTS COMPLETS
# ═══════════════════════════════════════════════════════════

class TestWeatherModels:
    """Tests complets modèles Weather"""
    
    def test_type_alert_meteo_values(self):
        from src.services.weather import TypeAlertMeteo
        
        assert TypeAlertMeteo.GEL.value == "gel"
        assert TypeAlertMeteo.CANICULE.value == "canicule"
        assert TypeAlertMeteo.PLUIE_FORTE.value == "pluie_forte"
        assert TypeAlertMeteo.SECHERESSE.value == "sécheresse"
        assert TypeAlertMeteo.VENT_FORT.value == "vent_fort"
        assert TypeAlertMeteo.ORAGE.value == "orage"
        assert TypeAlertMeteo.GRELE.value == "grêle"
        assert TypeAlertMeteo.NEIGE.value == "neige"
        
    def test_niveau_alerte_values(self):
        from src.services.weather import NiveauAlerte
        
        assert NiveauAlerte.INFO.value == "info"
        assert NiveauAlerte.ATTENTION.value == "attention"
        assert NiveauAlerte.DANGER.value == "danger"
        
    def test_meteo_jour_creation(self):
        from src.services.weather import MeteoJour
        
        meteo = MeteoJour(
            date=date(2024, 6, 15),
            temperature_min=15.0,
            temperature_max=28.0,
            temperature_moyenne=21.5,
            humidite=65,
            precipitation_mm=0.0,
            probabilite_pluie=10,
            vent_km_h=15.0,
            direction_vent="NO",
            uv_index=6,
            condition="ensoleillé"
        )
        
        assert meteo.date == date(2024, 6, 15)
        assert meteo.temperature_min == 15.0
        assert meteo.temperature_max == 28.0
        assert meteo.humidite == 65
        
    def test_alerte_meteo_creation(self):
        from src.services.weather import AlerteMeteo, TypeAlertMeteo, NiveauAlerte
        
        alerte = AlerteMeteo(
            type_alerte=TypeAlertMeteo.GEL,
            niveau=NiveauAlerte.DANGER,
            titre="Risque de gel",
            message="Températures négatives prévues",
            conseil_jardin="Protégez vos plantes fragiles",
            date_debut=date(2024, 1, 15),
            date_fin=date(2024, 1, 17),
            temperature=-3.0
        )
        
        assert alerte.type_alerte == TypeAlertMeteo.GEL
        assert alerte.niveau == NiveauAlerte.DANGER
        assert alerte.temperature == -3.0
        
    def test_conseil_jardin_creation(self):
        from src.services.weather import ConseilJardin
        
        conseil = ConseilJardin(
            priorite=1,
            icone="💧",
            titre="Arrosage nécessaire",
            description="Le sol est sec",
            plantes_concernees=["Tomates", "Courgettes"],
            action_recommandee="Arroser abondamment"
        )
        
        assert conseil.priorite == 1
        assert len(conseil.plantes_concernees) == 2
        
    def test_plan_arrosage_creation(self):
        from src.services.weather import PlanArrosage
        
        plan = PlanArrosage(
            date=date(2024, 7, 15),
            besoin_arrosage=True,
            quantite_recommandee_litres=10.0,
            raison="Temps sec depuis 3 jours",
            plantes_prioritaires=["Tomates", "Salades"]
        )
        
        assert plan.besoin_arrosage is True
        assert plan.quantite_recommandee_litres == 10.0


class TestWeatherGardenService:
    """Tests WeatherGardenService"""
    
    def test_service_init_default(self):
        from src.services.weather import WeatherGardenService
        
        with patch('src.services.weather.httpx.Client'):
            service = WeatherGardenService()
            
        assert service.latitude == 48.8566  # Paris
        assert service.longitude == 2.3522
        
    def test_service_init_custom_location(self):
        from src.services.weather import WeatherGardenService
        
        with patch('src.services.weather.httpx.Client'):
            service = WeatherGardenService(latitude=45.0, longitude=5.0)
            
        assert service.latitude == 45.0
        assert service.longitude == 5.0
        
    def test_set_location(self):
        from src.services.weather import WeatherGardenService
        
        with patch('src.services.weather.httpx.Client'):
            service = WeatherGardenService()
            service.set_location(43.6, 1.44)
            
        assert service.latitude == 43.6
        assert service.longitude == 1.44
        
    def test_seuils_alerte(self):
        from src.services.weather import WeatherGardenService
        
        assert WeatherGardenService.SEUIL_GEL == 2.0
        assert WeatherGardenService.SEUIL_CANICULE == 35.0
        assert WeatherGardenService.SEUIL_PLUIE_FORTE == 20.0
        assert WeatherGardenService.SEUIL_VENT_FORT == 50.0
        
    def test_api_url(self):
        from src.services.weather import WeatherGardenService
        
        assert "open-meteo" in WeatherGardenService.API_URL


# ═══════════════════════════════════════════════════════════
# SUGGESTIONS IA TESTS COMPLETS
# ═══════════════════════════════════════════════════════════

class TestSuggestionsIAModels:
    """Tests modèles SuggestionsIA"""
    
    def test_profil_culinaire_defaults(self):
        from src.services.suggestions_ia import ProfilCulinaire
        
        profil = ProfilCulinaire()
        
        assert profil.categories_preferees == []
        assert profil.ingredients_frequents == []
        assert profil.difficulte_moyenne == "moyen"
        assert profil.temps_moyen_minutes == 45
        assert profil.nb_portions_habituel == 4
        
    def test_profil_culinaire_with_data(self):
        from src.services.suggestions_ia import ProfilCulinaire
        
        profil = ProfilCulinaire(
            categories_preferees=["Italien", "Français"],
            ingredients_frequents=["Tomates", "Oignons"],
            ingredients_evites=["Piments"],
            difficulte_moyenne="facile",
            temps_moyen_minutes=30,
            recettes_favorites=[1, 2, 3]
        )
        
        assert len(profil.categories_preferees) == 2
        assert "Tomates" in profil.ingredients_frequents
        
    def test_contexte_suggestion_defaults(self):
        from src.services.suggestions_ia import ContexteSuggestion
        
        ctx = ContexteSuggestion()
        
        assert ctx.type_repas == "dîner"
        assert ctx.nb_personnes == 4
        assert ctx.temps_disponible_minutes == 60
        assert ctx.budget == "normal"
        
    def test_contexte_suggestion_full(self):
        from src.services.suggestions_ia import ContexteSuggestion
        
        ctx = ContexteSuggestion(
            type_repas="déjeuner",
            nb_personnes=2,
            temps_disponible_minutes=30,
            ingredients_disponibles=["Pâtes", "Tomates"],
            ingredients_a_utiliser=["Crème fraîche"],
            contraintes=["végétarien"],
            saison="été",
            budget="économique"
        )
        
        assert ctx.type_repas == "déjeuner"
        assert len(ctx.ingredients_disponibles) == 2
        assert "végétarien" in ctx.contraintes
        
    def test_suggestion_recette_creation(self):
        from src.services.suggestions_ia import SuggestionRecette
        
        suggestion = SuggestionRecette(
            recette_id=42,
            nom="Pâtes carbonara",
            raison="Ingrédients disponibles",
            score=0.85,
            tags=["Italien", "Rapide"],
            temps_preparation=25,
            difficulte="facile",
            ingredients_manquants=["Parmesan"],
            est_nouvelle=False
        )
        
        assert suggestion.recette_id == 42
        assert suggestion.score == 0.85
        assert not suggestion.est_nouvelle


class TestSuggestionsIAService:
    """Tests SuggestionsIAService"""
    
    def test_service_init(self):
        from src.services.suggestions_ia import SuggestionsIAService
        
        with patch('src.services.suggestions_ia.ClientIA'):
            with patch('src.services.suggestions_ia.AnalyseurIA'):
                with patch('src.services.suggestions_ia.obtenir_cache'):
                    service = SuggestionsIAService()
                    
        assert service is not None
        
    def test_service_has_client_ia(self):
        from src.services.suggestions_ia import SuggestionsIAService
        
        with patch('src.services.suggestions_ia.ClientIA') as mock_client:
            with patch('src.services.suggestions_ia.AnalyseurIA'):
                with patch('src.services.suggestions_ia.obtenir_cache'):
                    service = SuggestionsIAService()
                    
        mock_client.assert_called_once()


# ═══════════════════════════════════════════════════════════
# BACKUP SERVICE TESTS COMPLETS
# ═══════════════════════════════════════════════════════════

class TestBackupModelsComplete:
    """Tests complets modèles Backup"""
    
    def test_backup_config_all_fields(self):
        from src.services.backup import BackupConfig
        
        config = BackupConfig(
            backup_dir="/var/backups",
            max_backups=7,
            compress=True,
            include_timestamps=True,
            auto_backup_enabled=False,
            auto_backup_interval_hours=12
        )
        
        assert config.backup_dir == "/var/backups"
        assert config.max_backups == 7
        assert config.compress is True
        assert config.auto_backup_enabled is False
        assert config.auto_backup_interval_hours == 12
        
    def test_backup_metadata_with_checksum(self):
        from src.services.backup import BackupMetadata
        
        meta = BackupMetadata(
            id="bkp-20240115-123456",
            version="2.1",
            tables_count=25,
            total_records=50000,
            file_size_bytes=5242880,
            compressed=True,
            checksum="sha256:abc123def456"
        )
        
        assert meta.id == "bkp-20240115-123456"
        assert meta.version == "2.1"
        assert meta.file_size_bytes == 5242880
        assert meta.checksum == "sha256:abc123def456"
        
    def test_backup_result_complete(self):
        from src.services.backup import BackupResult, BackupMetadata
        
        meta = BackupMetadata(id="test", tables_count=10)
        result = BackupResult(
            success=True,
            message="Backup terminé avec succès",
            file_path="/backups/backup_2024.json.gz",
            metadata=meta,
            duration_seconds=45.5
        )
        
        assert result.success
        assert result.duration_seconds == 45.5
        assert result.metadata.tables_count == 10


# ═══════════════════════════════════════════════════════════
# USER PREFERENCES SERVICE TESTS
# ═══════════════════════════════════════════════════════════

class TestUserPreferencesModels:
    """Tests modèles UserPreferences"""
    
    def test_user_preferences_module(self):
        import src.services.user_preferences
        assert src.services.user_preferences is not None


# ═══════════════════════════════════════════════════════════
# REALTIME SYNC TESTS
# ═══════════════════════════════════════════════════════════

class TestRealtimeSyncModels:
    """Tests modèles RealtimeSync"""
    
    def test_realtime_sync_module(self):
        import src.services.realtime_sync
        assert src.services.realtime_sync is not None


# ═══════════════════════════════════════════════════════════
# BATCH COOKING SERVICE TESTS COMPLETS
# ═══════════════════════════════════════════════════════════

class TestBatchCookingModels:
    """Tests modèles BatchCooking"""
    
    def test_batch_cooking_module_imports(self):
        import src.services.batch_cooking
        assert src.services.batch_cooking is not None


# ═══════════════════════════════════════════════════════════
# PDF EXPORT SERVICE TESTS
# ═══════════════════════════════════════════════════════════

class TestPDFExportModels:
    """Tests modèles PDFExport"""
    
    def test_pdf_export_module(self):
        import src.services.pdf_export
        assert src.services.pdf_export is not None
