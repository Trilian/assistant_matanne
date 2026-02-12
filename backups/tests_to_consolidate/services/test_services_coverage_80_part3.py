"""
Tests supplÃ©mentaires pour amÃ©liorer la couverture des services
 
Partie 3 - Schemas Pydantic et fonctions pures additionnelles
"""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import Mock, MagicMock, patch


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS Predictions Service - Schemas
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestPredictionArticleSchema:
    """Tests pour PredictionArticle schema"""
    
    def test_prediction_article_minimal(self):
        """Test minimal fields"""
        from src.services.predictions import PredictionArticle
        pred = PredictionArticle(
            article_id=1,
            ingredient_id=1,
            nom="Pommes",
            quantite_actuelle=10.0,
            quantite_predite_semaine=8.0,
            quantite_predite_mois=5.0,
            taux_consommation_moyen=0.5
        )
        assert pred.nom == "Pommes"
        assert pred.tendance == "stable"  # default
        assert pred.confiance == 0.0
    
    def test_prediction_article_full(self):
        """Test with all fields"""
        from src.services.predictions import PredictionArticle
        pred = PredictionArticle(
            article_id=1,
            ingredient_id=1,
            nom="Pommes",
            quantite_actuelle=10.0,
            quantite_predite_semaine=8.0,
            quantite_predite_mois=5.0,
            taux_consommation_moyen=0.5,
            tendance="decroissante",
            confiance=0.85,
            risque_rupture_mois=True,
            jours_avant_rupture=15
        )
        assert pred.tendance == "decroissante"
        assert pred.risque_rupture_mois is True
        assert pred.jours_avant_rupture == 15


class TestAnalysePredictionSchema:
    """Tests pour AnalysePrediction schema"""
    
    def test_analyse_prediction_minimal(self):
        """Test minimal fields"""
        from src.services.predictions import AnalysePrediction
        analyse = AnalysePrediction(
            nombre_articles=10,
            articles_en_rupture_risque=["Art1", "Art2"],
            articles_croissance=["Art3"],
            articles_decroissance=["Art4"],
            consommation_moyenne_globale=5.5,
            tendance_globale="stable"
        )
        assert analyse.nombre_articles == 10
        assert len(analyse.articles_en_rupture_risque) == 2
    
    def test_analyse_prediction_with_stats(self):
        """Test with additional stats"""
        from src.services.predictions import AnalysePrediction
        analyse = AnalysePrediction(
            nombre_articles=50,
            articles_en_rupture_risque=[],
            articles_croissance=["A", "B"],
            articles_decroissance=["C"],
            consommation_moyenne_globale=12.5,
            consommation_min=2.0,
            consommation_max=25.0,
            nb_articles_croissance=2,
            nb_articles_decroissance=1,
            nb_articles_stables=47,
            tendance_globale="croissante"
        )
        assert analyse.consommation_min == 2.0
        assert analyse.consommation_max == 25.0
        assert analyse.nb_articles_stables == 47


class TestPredictionServiceInit:
    """Tests pour PredictionService initialization"""
    
    def test_service_init(self):
        """Test service can be instantiated"""
        from src.services.predictions import PredictionService
        service = PredictionService()
        assert service.min_data_points == 3
    
    def test_analyser_historique_empty(self):
        """Test analyse with empty history"""
        from src.services.predictions import PredictionService
        service = PredictionService()
        result = service.analyser_historique_article(1, [])
        assert result is None
    
    def test_analyser_historique_insufficient_data(self):
        """Test analyse with insufficient data points"""
        from src.services.predictions import PredictionService
        service = PredictionService()
        historique = [
            {"article_id": 1, "type_modification": "modification_quantite"}
        ]
        result = service.analyser_historique_article(1, historique)
        assert result is None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS Weather Service - Enums and Schemas
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestTypeAlertMeteoEnum:
    """Tests pour TypeAlertMeteo enum"""
    
    def test_gel(self):
        """Test GEL value"""
        from src.services.weather import TypeAlertMeteo
        assert TypeAlertMeteo.GEL.value == "gel"
    
    def test_canicule(self):
        """Test CANICULE value"""
        from src.services.weather import TypeAlertMeteo
        assert TypeAlertMeteo.CANICULE.value == "canicule"
    
    def test_pluie_forte(self):
        """Test PLUIE_FORTE value"""
        from src.services.weather import TypeAlertMeteo
        assert TypeAlertMeteo.PLUIE_FORTE.value == "pluie_forte"
    
    def test_secheresse(self):
        """Test SECHERESSE value"""
        from src.services.weather import TypeAlertMeteo
        assert TypeAlertMeteo.SECHERESSE.value == "sÃ©cheresse"
    
    def test_vent_fort(self):
        """Test VENT_FORT value"""
        from src.services.weather import TypeAlertMeteo
        assert TypeAlertMeteo.VENT_FORT.value == "vent_fort"
    
    def test_orage(self):
        """Test ORAGE value"""
        from src.services.weather import TypeAlertMeteo
        assert TypeAlertMeteo.ORAGE.value == "orage"
    
    def test_grele(self):
        """Test GRELE value"""
        from src.services.weather import TypeAlertMeteo
        assert TypeAlertMeteo.GRELE.value == "grÃªle"
    
    def test_neige(self):
        """Test NEIGE value"""
        from src.services.weather import TypeAlertMeteo
        assert TypeAlertMeteo.NEIGE.value == "neige"


class TestNiveauAlerteEnum:
    """Tests pour NiveauAlerte enum"""
    
    def test_info(self):
        """Test INFO value"""
        from src.services.weather import NiveauAlerte
        assert NiveauAlerte.INFO.value == "info"
    
    def test_attention(self):
        """Test ATTENTION value"""
        from src.services.weather import NiveauAlerte
        assert NiveauAlerte.ATTENTION.value == "attention"
    
    def test_danger(self):
        """Test DANGER value"""
        from src.services.weather import NiveauAlerte
        assert NiveauAlerte.DANGER.value == "danger"


class TestMeteoJourSchema:
    """Tests pour MeteoJour schema"""
    
    def test_meteo_jour_minimal(self):
        """Test minimal fields"""
        from src.services.weather import MeteoJour
        meteo = MeteoJour(
            date=date.today(),
            temperature_min=5.0,
            temperature_max=15.0,
            temperature_moyenne=10.0,
            humidite=65,
            precipitation_mm=0.0,
            probabilite_pluie=10,
            vent_km_h=15.0
        )
        assert meteo.temperature_moyenne == 10.0
        assert meteo.uv_index == 0  # default
        assert meteo.condition == ""  # default
    
    def test_meteo_jour_full(self):
        """Test with all fields"""
        from src.services.weather import MeteoJour
        meteo = MeteoJour(
            date=date.today(),
            temperature_min=5.0,
            temperature_max=25.0,
            temperature_moyenne=15.0,
            humidite=50,
            precipitation_mm=5.5,
            probabilite_pluie=70,
            vent_km_h=20.0,
            direction_vent="Nord",
            uv_index=6,
            lever_soleil="06:30",
            coucher_soleil="20:45",
            condition="nuageux",
            icone="â˜ï¸"
        )
        assert meteo.direction_vent == "Nord"
        assert meteo.condition == "nuageux"


class TestAlerteMeteoSchema:
    """Tests pour AlerteMeteo schema"""
    
    def test_alerte_meteo_minimal(self):
        """Test minimal fields"""
        from src.services.weather import AlerteMeteo, TypeAlertMeteo, NiveauAlerte
        alerte = AlerteMeteo(
            type_alerte=TypeAlertMeteo.GEL,
            niveau=NiveauAlerte.ATTENTION,
            titre="Risque de gel",
            message="Gel attendu cette nuit",
            conseil_jardin="ProtÃ©gez vos plantes",
            date_debut=date.today()
        )
        assert alerte.titre == "Risque de gel"
        assert alerte.date_fin is None  # default
    
    def test_alerte_meteo_full(self):
        """Test with all fields"""
        from src.services.weather import AlerteMeteo, TypeAlertMeteo, NiveauAlerte
        alerte = AlerteMeteo(
            type_alerte=TypeAlertMeteo.CANICULE,
            niveau=NiveauAlerte.DANGER,
            titre="Canicule",
            message="TempÃ©ratures extrÃªmes",
            conseil_jardin="Arrosez matin et soir",
            date_debut=date.today(),
            date_fin=date.today() + timedelta(days=3),
            temperature=38.5
        )
        assert alerte.temperature == 38.5
        assert alerte.date_fin is not None


class TestConseilJardinSchema:
    """Tests pour ConseilJardin schema"""
    
    def test_conseil_jardin_minimal(self):
        """Test minimal fields"""
        from src.services.weather import ConseilJardin
        conseil = ConseilJardin(
            titre="Arrosage",
            description="Arrosez les plantes ce soir"
        )
        assert conseil.priorite == 1  # default
        assert conseil.icone == "ðŸŒ±"  # default
    
    def test_conseil_jardin_full(self):
        """Test with all fields"""
        from src.services.weather import ConseilJardin
        conseil = ConseilJardin(
            priorite=2,
            icone="ðŸ’§",
            titre="Arrosage",
            description="Arrosez abondamment",
            plantes_concernees=["Tomates", "Courgettes"],
            action_recommandee="15L par plante"
        )
        assert conseil.priorite == 2
        assert len(conseil.plantes_concernees) == 2


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS Facture OCR - Schemas
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestFactureOCRImports:
    """Tests pour facture_ocr imports"""
    
    def test_import_module(self):
        """Test module can be imported"""
        from src.services import facture_ocr
        assert facture_ocr is not None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS Notifications Service - Imports
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestNotificationsImports:
    """Tests pour notifications imports"""
    
    def test_import_notifications_module(self):
        """Test notifications module import"""
        from src.services import notifications
        assert notifications is not None
    
    def test_import_notifications_push_module(self):
        """Test notifications_push module import"""
        from src.services import notifications_push
        assert notifications_push is not None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS Planning Unified - Schemas
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestPlanningUnifiedImports:
    """Tests pour planning_unified imports"""
    
    def test_import_module(self):
        """Test module can be imported"""
        from src.services import planning_unified
        assert planning_unified is not None
    
    def test_import_jour_planning(self):
        """Test JourPlanning import"""
        from src.services import JourPlanning
        jour = JourPlanning(jour="2025-01-15", dejeuner="PÃ¢tes", diner="Soupe")
        assert jour.jour == "2025-01-15"
    
    def test_import_parametres_equilibre(self):
        """Test ParametresEquilibre import"""
        from src.services import ParametresEquilibre
        params = ParametresEquilibre()
        assert params is not None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS Garmin Sync - Imports and Schemas
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestGarminSyncImports:
    """Tests pour garmin_sync imports"""
    
    def test_import_module(self):
        """Test module can be imported"""
        from src.services import garmin_sync
        assert garmin_sync is not None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS Course Intelligentes - Imports
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestCoursesIntelligentesImports:
    """Tests pour courses_intelligentes imports"""
    
    def test_import_module(self):
        """Test module can be imported"""
        from src.services import courses_intelligentes
        assert courses_intelligentes is not None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS PDF Export - Imports
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestPDFExportImports:
    """Tests pour pdf_export imports"""
    
    def test_import_module(self):
        """Test module can be imported"""
        from src.services import pdf_export
        assert pdf_export is not None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS User Preferences - Imports
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestUserPreferencesImports:
    """Tests pour user_preferences imports"""
    
    def test_import_module(self):
        """Test module can be imported"""
        from src.services import user_preferences
        assert user_preferences is not None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS Realtime Sync - Imports
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestRealtimeSyncImports:
    """Tests pour realtime_sync imports"""
    
    def test_import_module(self):
        """Test module can be imported"""
        from src.services import realtime_sync
        assert realtime_sync is not None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS PWA - Imports
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestPWAImports:
    """Tests pour pwa imports"""
    
    def test_import_module(self):
        """Test module can be imported"""
        from src.services import pwa
        assert pwa is not None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS Suggestions IA - Imports
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestSuggestionsIAImports:
    """Tests pour suggestions_ia imports"""
    
    def test_import_module(self):
        """Test module can be imported"""
        from src.services import suggestions_ia
        assert suggestions_ia is not None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS recipe_import - Parsers additionnels
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestCuisineAZParser:
    """Tests pour CuisineAZParser"""
    
    def test_cuisineaz_parser_exists(self):
        """Test CuisineAZParser class exists"""
        from src.services.recipe_import import CuisineAZParser
        assert CuisineAZParser is not None


class TestGenericRecipeParser:
    """Tests pour GenericRecipeParser"""
    
    def test_generic_parser_exists(self):
        """Test import works"""
        from src.services.recipe_import import RecipeParser
        assert RecipeParser is not None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS Services __init__ exports
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestServicesExports:
    """Tests pour vÃ©rifier les exports du package services"""
    
    def test_recette_service_module(self):
        """Test recettes module exists"""
        from src.services import recettes
        assert recettes is not None
    
    def test_courses_service_module(self):
        """Test courses module exists"""
        from src.services import courses
        assert courses is not None
    
    def test_planning_service_export(self):
        """Test get_planning_service export"""
        from src.services import get_planning_service
        assert get_planning_service is not None
    
    def test_inventaire_module(self):
        """Test inventaire module exists"""
        from src.services import inventaire
        assert inventaire is not None
    
    def test_base_service_export(self):
        """Test BaseService export"""
        from src.services import BaseService
        assert BaseService is not None
    
    def test_io_service_export(self):
        """Test IOService export"""
        from src.services import IOService
        assert IOService is not None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS types.py - Additional methods via inheritance
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestBaseServiceCountByStatus:
    """Tests pour BaseService.count_by_status"""
    
    def test_count_by_status_method_exists(self):
        """Test method exists"""
        from src.services.types import BaseService
        
        class MockModel:
            __name__ = "MockModel"
        
        service = BaseService(MockModel)
        assert hasattr(service, "count_by_status")


class TestBaseServiceMarkAs:
    """Tests pour BaseService.mark_as"""
    
    def test_mark_as_method_exists(self):
        """Test method exists"""
        from src.services.types import BaseService
        
        class MockModel:
            __name__ = "MockModel"
        
        service = BaseService(MockModel)
        assert hasattr(service, "mark_as")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS OpenFoodFacts - API mocking
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestOpenFoodFactsRechercherProduit:
    """Tests pour rechercher_produit avec mocks"""
    
    @patch('httpx.Client')
    def test_rechercher_produit_http_error(self, mock_client_class):
        """Test handling of HTTP errors"""
        from src.services.openfoodfacts import OpenFoodFactsService
        
        mock_client = Mock()
        mock_client_class.return_value.__enter__ = Mock(return_value=mock_client)
        mock_client_class.return_value.__exit__ = Mock(return_value=False)
        
        mock_response = Mock()
        mock_response.status_code = 500
        mock_client.get.return_value = mock_response
        
        service = OpenFoodFactsService()
        result = service.rechercher_produit("123456")
        
        assert result is None


class TestOpenFoodFactsRechercherParNom:
    """Tests pour rechercher_par_nom avec mocks"""
    
    def test_method_exists(self):
        """Test rechercher_par_nom method exists"""
        from src.services.openfoodfacts import OpenFoodFactsService
        service = OpenFoodFactsService()
        assert hasattr(service, "rechercher_par_nom")
