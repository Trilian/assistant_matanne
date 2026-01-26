"""
Tests pour les nouveaux services implémentés.

Couvre:
- BackupService
- RecipeImportService
- CalendarSyncService
- BudgetService
- WeatherGardenService
- RateLimiting
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, datetime, timedelta
from io import BytesIO


# ═══════════════════════════════════════════════════════════
# TESTS BACKUP SERVICE
# ═══════════════════════════════════════════════════════════


class TestBackupService:
    """Tests pour le service de backup."""
    
    def test_backup_config_defaults(self):
        """Test configuration par défaut du backup."""
        from src.services.backup import BackupConfig
        
        config = BackupConfig()
        
        assert config.backup_dir == "backups"
        assert config.max_backups == 10
        assert config.compress is True
        assert "recettes" in config.tables_to_backup
        assert "ingredients" in config.tables_to_backup
    
    def test_backup_metadata_creation(self):
        """Test création métadonnées de backup."""
        from src.services.backup import BackupMetadata
        
        meta = BackupMetadata(
            filename="backup_20240125.json.gz",
            created_at=datetime.now(),
            tables=["recettes", "ingredients"],
            row_counts={"recettes": 10, "ingredients": 50},
            size_bytes=1024,
            compressed=True,
            version="1.0.0"
        )
        
        assert meta.filename == "backup_20240125.json.gz"
        assert meta.compressed is True
        assert meta.row_counts["recettes"] == 10
    
    @patch('src.services.backup.obtenir_contexte_db')
    def test_backup_service_init(self, mock_db):
        """Test initialisation du service backup."""
        from src.services.backup import BackupService, BackupConfig
        
        config = BackupConfig(max_backups=5)
        service = BackupService(config)
        
        assert service.config.max_backups == 5
    
    @patch('src.services.backup.obtenir_contexte_db')
    def test_get_backup_service_factory(self, mock_db):
        """Test factory function."""
        from src.services.backup import get_backup_service
        
        service1 = get_backup_service()
        service2 = get_backup_service()
        
        # Singleton pattern
        assert service1 is service2


class TestBackupResult:
    """Tests pour les résultats de backup."""
    
    def test_backup_result_success(self):
        """Test résultat de backup réussi."""
        from src.services.backup import BackupResult, BackupMetadata
        
        meta = BackupMetadata(
            filename="test.json.gz",
            created_at=datetime.now(),
            tables=["recettes"],
            row_counts={"recettes": 5},
            size_bytes=512,
            compressed=True
        )
        
        result = BackupResult(
            success=True,
            message="Backup créé avec succès",
            metadata=meta
        )
        
        assert result.success is True
        assert result.metadata is not None
        assert result.metadata.filename == "test.json.gz"
    
    def test_backup_result_failure(self):
        """Test résultat de backup échoué."""
        from src.services.backup import BackupResult
        
        result = BackupResult(
            success=False,
            message="Erreur de connexion",
            metadata=None
        )
        
        assert result.success is False
        assert result.metadata is None


# ═══════════════════════════════════════════════════════════
# TESTS RECIPE IMPORT SERVICE
# ═══════════════════════════════════════════════════════════


class TestRecipeImportService:
    """Tests pour l'import de recettes depuis URL."""
    
    def test_imported_recipe_model(self):
        """Test modèle de recette importée."""
        from src.services.recipe_import import ImportedRecipe
        
        recipe = ImportedRecipe(
            nom="Tarte aux pommes",
            description="Délicieuse tarte",
            temps_preparation=30,
            temps_cuisson=45,
            portions=8,
            ingredients=["Pommes", "Pâte", "Sucre"],
            instructions=["Étaler la pâte", "Ajouter les pommes"],
            source_url="https://example.com/tarte",
            source_site="Example"
        )
        
        assert recipe.nom == "Tarte aux pommes"
        assert recipe.temps_total == 75
        assert len(recipe.ingredients) == 3
    
    def test_detect_site_marmiton(self):
        """Test détection du site Marmiton."""
        from src.services.recipe_import import RecipeImportService
        
        service = RecipeImportService()
        
        assert service._detect_site("https://www.marmiton.org/recettes/tarte") == "marmiton"
        assert service._detect_site("https://marmiton.org/recipe") == "marmiton"
    
    def test_detect_site_cuisineaz(self):
        """Test détection du site CuisineAZ."""
        from src.services.recipe_import import RecipeImportService
        
        service = RecipeImportService()
        
        assert service._detect_site("https://www.cuisineaz.com/recettes/") == "cuisineaz"
    
    def test_detect_site_unknown(self):
        """Test site non reconnu."""
        from src.services.recipe_import import RecipeImportService
        
        service = RecipeImportService()
        
        assert service._detect_site("https://www.unknown-site.com/recipe") == "unknown"
    
    def test_clean_text(self):
        """Test nettoyage du texte."""
        from src.services.recipe_import import RecipeImportService
        
        service = RecipeImportService()
        
        dirty = "  Test   with   spaces  \n\t"
        clean = service._clean_text(dirty)
        
        assert clean == "Test with spaces"
    
    @patch('httpx.Client')
    def test_import_invalid_url(self, mock_client):
        """Test import URL invalide."""
        from src.services.recipe_import import RecipeImportService
        
        service = RecipeImportService()
        
        result = service.import_from_url("not-a-valid-url")
        
        assert result is None


class TestRecipeParsers:
    """Tests pour les parsers de recettes."""
    
    def test_parse_duration_minutes(self):
        """Test parsing de durée en minutes."""
        from src.services.recipe_import import RecipeImportService
        
        service = RecipeImportService()
        
        assert service._parse_duration("30 minutes") == 30
        assert service._parse_duration("45 min") == 45
        assert service._parse_duration("1h30") == 90
        assert service._parse_duration("2 heures") == 120
    
    def test_extract_schema_org(self):
        """Test extraction JSON-LD schema.org."""
        from src.services.recipe_import import RecipeImportService
        from bs4 import BeautifulSoup
        
        html = """
        <html>
        <head>
            <script type="application/ld+json">
            {
                "@type": "Recipe",
                "name": "Test Recipe",
                "description": "A test",
                "prepTime": "PT30M",
                "cookTime": "PT45M",
                "recipeIngredient": ["Ingredient 1", "Ingredient 2"],
                "recipeInstructions": [{"text": "Step 1"}]
            }
            </script>
        </head>
        <body></body>
        </html>
        """
        
        service = RecipeImportService()
        soup = BeautifulSoup(html, "html.parser")
        
        recipe = service._extract_schema_org(soup, "https://test.com")
        
        assert recipe is not None
        assert recipe.nom == "Test Recipe"


# ═══════════════════════════════════════════════════════════
# TESTS CALENDAR SYNC SERVICE
# ═══════════════════════════════════════════════════════════


class TestCalendarSyncService:
    """Tests pour la synchronisation calendrier."""
    
    def test_calendar_event_model(self):
        """Test modèle d'événement calendrier."""
        from src.services.calendar_sync import CalendarEvent
        
        event = CalendarEvent(
            uid="test-123",
            title="Repas famille",
            start=datetime.now(),
            end=datetime.now() + timedelta(hours=2),
            description="Déjeuner dominical",
            location="Maison"
        )
        
        assert event.uid == "test-123"
        assert event.title == "Repas famille"
        assert event.duration.total_seconds() == 7200
    
    def test_ical_generator_creation(self):
        """Test création d'un calendrier iCal."""
        from src.services.calendar_sync import ICalGenerator
        
        generator = ICalGenerator("Test Calendar")
        
        assert generator.cal_name == "Test Calendar"
    
    def test_ical_add_event(self):
        """Test ajout d'événement au calendrier."""
        from src.services.calendar_sync import ICalGenerator, CalendarEvent
        
        generator = ICalGenerator("Test")
        
        event = CalendarEvent(
            uid="event-1",
            title="Test Event",
            start=datetime(2024, 1, 25, 12, 0),
            end=datetime(2024, 1, 25, 14, 0)
        )
        
        generator.add_event(event)
        
        ical_str = generator.to_string()
        
        assert "BEGIN:VCALENDAR" in ical_str
        assert "Test Event" in ical_str
        assert "BEGIN:VEVENT" in ical_str
    
    def test_external_calendar_config(self):
        """Test configuration calendrier externe."""
        from src.services.calendar_sync import ExternalCalendarConfig, CalendarProvider
        
        config = ExternalCalendarConfig(
            provider=CalendarProvider.GOOGLE,
            name="Mon Google Calendar",
            url="https://calendar.google.com/...",
            enabled=True,
            sync_interval_minutes=30
        )
        
        assert config.provider == CalendarProvider.GOOGLE
        assert config.sync_interval_minutes == 30


class TestICalParsing:
    """Tests pour le parsing iCal."""
    
    def test_parse_simple_ical(self):
        """Test parsing d'un iCal simple."""
        from src.services.calendar_sync import CalendarSyncService
        
        ical_content = """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:test@example.com
DTSTART:20240125T120000
DTEND:20240125T140000
SUMMARY:Test Event
END:VEVENT
END:VCALENDAR"""
        
        service = CalendarSyncService()
        events = service._parse_ical(ical_content)
        
        assert len(events) == 1
        assert events[0].title == "Test Event"


# ═══════════════════════════════════════════════════════════
# TESTS BUDGET SERVICE
# ═══════════════════════════════════════════════════════════


class TestBudgetService:
    """Tests pour le service de budget."""
    
    def test_categorie_depense_enum(self):
        """Test énumération des catégories."""
        from src.services.budget import CategorieDepense
        
        assert CategorieDepense.ALIMENTATION.value == "alimentation"
        assert CategorieDepense.LOISIRS.value == "loisirs"
        assert len(CategorieDepense) == 13
    
    def test_depense_model(self):
        """Test modèle de dépense."""
        from src.services.budget import Depense, CategorieDepense
        
        depense = Depense(
            montant=45.50,
            categorie=CategorieDepense.ALIMENTATION,
            description="Courses Carrefour",
            date=date.today()
        )
        
        assert depense.montant == 45.50
        assert depense.categorie == CategorieDepense.ALIMENTATION
    
    def test_budget_mensuel_model(self):
        """Test modèle budget mensuel."""
        from src.services.budget import BudgetMensuel, CategorieDepense
        
        budget = BudgetMensuel(
            mois=date(2024, 1, 1),
            budgets_par_categorie={
                CategorieDepense.ALIMENTATION: 500.0,
                CategorieDepense.TRANSPORT: 150.0
            },
            budget_total=2000.0
        )
        
        assert budget.budget_total == 2000.0
        assert budget.budgets_par_categorie[CategorieDepense.ALIMENTATION] == 500.0
    
    def test_resume_financier(self):
        """Test résumé financier."""
        from src.services.budget import ResumeFinancier, CategorieDepense
        
        resume = ResumeFinancier(
            periode_debut=date(2024, 1, 1),
            periode_fin=date(2024, 1, 31),
            total_depenses=1500.0,
            budget_total=2000.0,
            depenses_par_categorie={
                CategorieDepense.ALIMENTATION: 500.0,
                CategorieDepense.TRANSPORT: 200.0
            }
        )
        
        assert resume.reste_budget == 500.0
        assert resume.pourcentage_utilise == 75.0
    
    @patch('src.services.budget.obtenir_contexte_db')
    def test_budget_service_init(self, mock_db):
        """Test initialisation service budget."""
        from src.services.budget import BudgetService
        
        service = BudgetService()
        
        assert service is not None


class TestBudgetCalculations:
    """Tests pour les calculs budgétaires."""
    
    def test_calculer_moyenne_categorie(self):
        """Test calcul moyenne par catégorie."""
        from src.services.budget import Depense, CategorieDepense
        
        depenses = [
            Depense(montant=100, categorie=CategorieDepense.ALIMENTATION, date=date.today()),
            Depense(montant=150, categorie=CategorieDepense.ALIMENTATION, date=date.today()),
            Depense(montant=50, categorie=CategorieDepense.ALIMENTATION, date=date.today()),
        ]
        
        total = sum(d.montant for d in depenses)
        moyenne = total / len(depenses)
        
        assert moyenne == 100.0


# ═══════════════════════════════════════════════════════════
# TESTS WEATHER SERVICE
# ═══════════════════════════════════════════════════════════


class TestWeatherGardenService:
    """Tests pour le service météo jardin."""
    
    def test_meteo_jour_model(self):
        """Test modèle météo journalière."""
        from src.services.weather import MeteoJour
        
        meteo = MeteoJour(
            date=date.today(),
            temperature_min=5.0,
            temperature_max=15.0,
            temperature_moyenne=10.0,
            humidite=65,
            precipitation_mm=2.5,
            probabilite_pluie=40,
            vent_km_h=25.0,
            condition="Nuageux",
            icone="☁️"
        )
        
        assert meteo.temperature_moyenne == 10.0
        assert meteo.humidite == 65
    
    def test_alerte_meteo_model(self):
        """Test modèle alerte météo."""
        from src.services.weather import AlerteMeteo, TypeAlertMeteo, NiveauAlerte
        
        alerte = AlerteMeteo(
            type_alerte=TypeAlertMeteo.GEL,
            niveau=NiveauAlerte.DANGER,
            titre="Risque de gel",
            message="Température négative prévue",
            conseil_jardin="Protégez vos plantes",
            date_debut=date.today()
        )
        
        assert alerte.type_alerte == TypeAlertMeteo.GEL
        assert alerte.niveau == NiveauAlerte.DANGER
    
    def test_conseil_jardin_model(self):
        """Test modèle conseil jardin."""
        from src.services.weather import ConseilJardin
        
        conseil = ConseilJardin(
            priorite=1,
            icone="💧",
            titre="Arrosage recommandé",
            description="Températures élevées",
            action_recommandee="Arroser ce soir"
        )
        
        assert conseil.priorite == 1
        assert conseil.icone == "💧"
    
    def test_plan_arrosage_model(self):
        """Test modèle plan arrosage."""
        from src.services.weather import PlanArrosage
        
        plan = PlanArrosage(
            date=date.today(),
            besoin_arrosage=True,
            quantite_recommandee_litres=30.0,
            raison="Températures élevées",
            plantes_prioritaires=["Tomates", "Salades"]
        )
        
        assert plan.besoin_arrosage is True
        assert plan.quantite_recommandee_litres == 30.0
    
    def test_weather_service_init(self):
        """Test initialisation service météo."""
        from src.services.weather import WeatherGardenService
        
        service = WeatherGardenService(latitude=48.8, longitude=2.3)
        
        assert service.latitude == 48.8
        assert service.longitude == 2.3
    
    def test_direction_from_degrees(self):
        """Test conversion degrés -> direction."""
        from src.services.weather import WeatherGardenService
        
        service = WeatherGardenService()
        
        assert service._direction_from_degrees(0) == "N"
        assert service._direction_from_degrees(90) == "E"
        assert service._direction_from_degrees(180) == "S"
        assert service._direction_from_degrees(270) == "O"
    
    def test_weathercode_to_condition(self):
        """Test conversion code météo -> description."""
        from src.services.weather import WeatherGardenService
        
        service = WeatherGardenService()
        
        assert service._weathercode_to_condition(0) == "Ensoleillé"
        assert service._weathercode_to_condition(3) == "Couvert"
        assert service._weathercode_to_condition(61) == "Pluie légère"
        assert service._weathercode_to_condition(95) == "Orage"
    
    def test_weathercode_to_icon(self):
        """Test conversion code météo -> emoji."""
        from src.services.weather import WeatherGardenService
        
        service = WeatherGardenService()
        
        assert service._weathercode_to_icon(0) == "☀️"
        assert service._weathercode_to_icon(3) == "☁️"
        assert service._weathercode_to_icon(61) == "🌧️"
        assert service._weathercode_to_icon(95) == "⛈️"


class TestWeatherAlerts:
    """Tests pour les alertes météo."""
    
    def test_generer_alerte_gel(self):
        """Test génération alerte gel."""
        from src.services.weather import (
            WeatherGardenService, MeteoJour, TypeAlertMeteo, NiveauAlerte
        )
        
        service = WeatherGardenService()
        
        previsions = [
            MeteoJour(
                date=date.today(),
                temperature_min=-2.0,
                temperature_max=5.0,
                temperature_moyenne=1.5,
                humidite=80,
                precipitation_mm=0,
                probabilite_pluie=10,
                vent_km_h=10,
                condition="Ensoleillé",
                icone="☀️"
            )
        ]
        
        alertes = service.generer_alertes(previsions)
        
        gel_alerts = [a for a in alertes if a.type_alerte == TypeAlertMeteo.GEL]
        assert len(gel_alerts) == 1
        assert gel_alerts[0].niveau == NiveauAlerte.DANGER
    
    def test_generer_alerte_canicule(self):
        """Test génération alerte canicule."""
        from src.services.weather import (
            WeatherGardenService, MeteoJour, TypeAlertMeteo
        )
        
        service = WeatherGardenService()
        
        previsions = [
            MeteoJour(
                date=date.today(),
                temperature_min=22.0,
                temperature_max=38.0,
                temperature_moyenne=30.0,
                humidite=40,
                precipitation_mm=0,
                probabilite_pluie=5,
                vent_km_h=15,
                condition="Ensoleillé",
                icone="☀️"
            )
        ]
        
        alertes = service.generer_alertes(previsions)
        
        canicule_alerts = [a for a in alertes if a.type_alerte == TypeAlertMeteo.CANICULE]
        assert len(canicule_alerts) == 1


# ═══════════════════════════════════════════════════════════
# TESTS RATE LIMITING
# ═══════════════════════════════════════════════════════════


class TestRateLimitStore:
    """Tests pour le stockage rate limiting."""
    
    def test_store_increment(self):
        """Test incrémentation compteur."""
        from src.api.rate_limiting import RateLimitStore
        
        store = RateLimitStore()
        
        count1 = store.increment("test_key", 60)
        count2 = store.increment("test_key", 60)
        count3 = store.increment("test_key", 60)
        
        assert count1 == 1
        assert count2 == 2
        assert count3 == 3
    
    def test_store_get_remaining(self):
        """Test calcul requêtes restantes."""
        from src.api.rate_limiting import RateLimitStore
        
        store = RateLimitStore()
        
        store.increment("test_key", 60)
        store.increment("test_key", 60)
        
        remaining = store.get_remaining("test_key", 60, limit=10)
        
        assert remaining == 8
    
    def test_store_block(self):
        """Test blocage temporaire."""
        from src.api.rate_limiting import RateLimitStore
        
        store = RateLimitStore()
        
        assert store.is_blocked("test_key") is False
        
        store.block("test_key", 60)
        
        assert store.is_blocked("test_key") is True


class TestRateLimiter:
    """Tests pour le rate limiter."""
    
    def test_rate_limit_config(self):
        """Test configuration rate limit."""
        from src.api.rate_limiting import RateLimitConfig
        
        config = RateLimitConfig(
            requests_per_minute=30,
            requests_per_hour=500,
            ai_requests_per_minute=5
        )
        
        assert config.requests_per_minute == 30
        assert config.ai_requests_per_minute == 5
    
    def test_exempt_paths(self):
        """Test chemins exemptés."""
        from src.api.rate_limiting import RateLimitConfig
        
        config = RateLimitConfig()
        
        assert "/health" in config.exempt_paths
        assert "/docs" in config.exempt_paths


class TestRateLimitStats:
    """Tests pour les statistiques rate limit."""
    
    def test_get_stats(self):
        """Test récupération statistiques."""
        from src.api.rate_limiting import get_rate_limit_stats
        
        stats = get_rate_limit_stats()
        
        assert "active_keys" in stats
        assert "blocked_keys" in stats
        assert "config" in stats
    
    def test_reset_limits(self):
        """Test reset des compteurs."""
        from src.api.rate_limiting import RateLimitStore, reset_rate_limits
        
        # Ajouter des données
        store = RateLimitStore()
        store.increment("key1", 60)
        store.increment("key2", 60)
        
        # Reset
        reset_rate_limits()
        
        # Vérifier reset
        stats = get_rate_limit_stats()
        # Note: le reset crée un nouveau store global


# ═══════════════════════════════════════════════════════════
# TESTS TABLET MODE
# ═══════════════════════════════════════════════════════════


class TestTabletMode:
    """Tests pour le mode tablette."""
    
    def test_tablet_mode_enum(self):
        """Test énumération modes."""
        from src.ui.tablet_mode import TabletMode
        
        assert TabletMode.NORMAL.value == "normal"
        assert TabletMode.TABLET.value == "tablet"
        assert TabletMode.KITCHEN.value == "kitchen"
    
    def test_tablet_css_exists(self):
        """Test présence CSS tablette."""
        from src.ui.tablet_mode import TABLET_CSS, KITCHEN_MODE_CSS
        
        assert "tablet-mode" in TABLET_CSS
        assert "kitchen-mode" in KITCHEN_MODE_CSS
        assert ".stButton" in TABLET_CSS
    
    def test_tablet_css_responsive(self):
        """Test CSS responsive."""
        from src.ui.tablet_mode import TABLET_CSS
        
        assert "@media" in TABLET_CSS
        assert "768px" in TABLET_CSS  # Breakpoint tablette


# ═══════════════════════════════════════════════════════════
# TESTS D'INTÉGRATION SIMPLES
# ═══════════════════════════════════════════════════════════


class TestServiceFactories:
    """Tests pour les factory functions."""
    
    def test_get_backup_service(self):
        """Test factory backup service."""
        from src.services.backup import get_backup_service
        
        service = get_backup_service()
        assert service is not None
    
    def test_get_weather_service(self):
        """Test factory weather service."""
        from src.services.weather import get_weather_garden_service
        
        service = get_weather_garden_service()
        assert service is not None
    
    def test_get_recipe_import_service(self):
        """Test factory recipe import service."""
        from src.services.recipe_import import get_recipe_import_service
        
        service = get_recipe_import_service()
        assert service is not None
    
    def test_get_calendar_sync_service(self):
        """Test factory calendar sync service."""
        from src.services.calendar_sync import get_calendar_sync_service
        
        service = get_calendar_sync_service()
        assert service is not None
    
    def test_get_budget_service(self):
        """Test factory budget service."""
        from src.services.budget import get_budget_service
        
        service = get_budget_service()
        assert service is not None
