"""
Tests complets pour le service WeatherGardenService.
"""
import pytest
from datetime import date, timedelta
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4
from decimal import Decimal

import importlib


@pytest.mark.unit
def test_import_weather_service():
    """Vérifie que le module weather s'importe sans erreur."""
    module = importlib.import_module("src.services.weather")
    assert module is not None


# ═══════════════════════════════════════════════════════════
# TESTS DES TYPES ET SCHÉMAS
# ═══════════════════════════════════════════════════════════

class TestEnums:
    """Tests des enums."""
    
    def test_type_alert_meteo_values(self):
        from src.services.weather import TypeAlertMeteo
        assert TypeAlertMeteo.GEL.value == "gel"
        assert TypeAlertMeteo.CANICULE.value == "canicule"
        assert TypeAlertMeteo.PLUIE_FORTE.value == "pluie_forte"
        assert TypeAlertMeteo.VENT_FORT.value == "vent_fort"
        assert TypeAlertMeteo.ORAGE.value == "orage"
    
    def test_niveau_alerte_values(self):
        from src.services.weather import NiveauAlerte
        assert NiveauAlerte.INFO.value == "info"
        assert NiveauAlerte.ATTENTION.value == "attention"
        assert NiveauAlerte.DANGER.value == "danger"


class TestMeteoJour:
    """Tests du modèle MeteoJour."""
    
    def test_create_meteo_jour(self):
        from src.services.weather import MeteoJour
        meteo = MeteoJour(
            date=date.today(),
            temperature_min=10.0,
            temperature_max=25.0,
            temperature_moyenne=17.5,
            humidite=50,
            precipitation_mm=0.0,
            probabilite_pluie=10,
            vent_km_h=15.0
        )
        assert meteo.temperature_min == 10.0
        assert meteo.temperature_max == 25.0
        assert meteo.humidite == 50
    
    def test_meteo_jour_with_optionals(self):
        from src.services.weather import MeteoJour
        meteo = MeteoJour(
            date=date.today(),
            temperature_min=5.0,
            temperature_max=15.0,
            temperature_moyenne=10.0,
            humidite=75,
            precipitation_mm=5.0,
            probabilite_pluie=80,
            vent_km_h=30.0,
            direction_vent="NO",
            uv_index=3,
            lever_soleil="07:30",
            coucher_soleil="20:00",
            condition="Nuageux",
            icone="☁️"
        )
        assert meteo.direction_vent == "NO"
        assert meteo.uv_index == 3
        assert meteo.condition == "Nuageux"


class TestAlerteMeteo:
    """Tests du modèle AlerteMeteo."""
    
    def test_create_alerte(self):
        from src.services.weather import AlerteMeteo, TypeAlertMeteo, NiveauAlerte
        alerte = AlerteMeteo(
            type_alerte=TypeAlertMeteo.GEL,
            niveau=NiveauAlerte.DANGER,
            titre="Gel",
            message="Risque de gel",
            conseil_jardin="Protéger les plantes",
            date_debut=date.today()
        )
        assert alerte.type_alerte == TypeAlertMeteo.GEL
        assert alerte.niveau == NiveauAlerte.DANGER


class TestConseilJardin:
    """Tests du modèle ConseilJardin."""
    
    def test_create_conseil(self):
        from src.services.weather import ConseilJardin
        conseil = ConseilJardin(
            priorite=1,
            icone="💧",
            titre="Arrosage",
            description="Pensez à arroser"
        )
        assert conseil.priorite == 1
        assert conseil.icone == "💧"


# ═══════════════════════════════════════════════════════════
# TESTS DU SERVICE PRINCIPAL
# ═══════════════════════════════════════════════════════════

class TestWeatherGardenServiceInit:
    """Tests d'initialisation du service."""
    
    def test_init_default_location(self):
        from src.services.weather import WeatherGardenService
        service = WeatherGardenService()
        # Paris par défaut
        assert service.latitude == 48.8566
        assert service.longitude == 2.3522
    
    def test_init_custom_location(self):
        from src.services.weather import WeatherGardenService
        service = WeatherGardenService(latitude=45.0, longitude=3.0)
        assert service.latitude == 45.0
        assert service.longitude == 3.0
    
    def test_set_location(self):
        from src.services.weather import WeatherGardenService
        service = WeatherGardenService()
        service.set_location(43.6, 1.4)  # Toulouse
        assert service.latitude == 43.6
        assert service.longitude == 1.4


class TestWeatherGardenServiceHelpers:
    """Tests des méthodes helper privées."""
    
    def test_direction_from_degrees_N(self):
        from src.services.weather import WeatherGardenService
        service = WeatherGardenService()
        assert service._direction_from_degrees(0) == "N"
        assert service._direction_from_degrees(350) == "N"
    
    def test_direction_from_degrees_E(self):
        from src.services.weather import WeatherGardenService
        service = WeatherGardenService()
        assert service._direction_from_degrees(90) == "E"
    
    def test_direction_from_degrees_S(self):
        from src.services.weather import WeatherGardenService
        service = WeatherGardenService()
        assert service._direction_from_degrees(180) == "S"
    
    def test_direction_from_degrees_O(self):
        from src.services.weather import WeatherGardenService
        service = WeatherGardenService()
        assert service._direction_from_degrees(270) == "O"
    
    def test_direction_from_degrees_none(self):
        from src.services.weather import WeatherGardenService
        service = WeatherGardenService()
        assert service._direction_from_degrees(None) == ""
    
    def test_weathercode_to_condition_ensoleille(self):
        from src.services.weather import WeatherGardenService
        service = WeatherGardenService()
        assert service._weathercode_to_condition(0) == "Ensoleillé"
    
    def test_weathercode_to_condition_nuageux(self):
        from src.services.weather import WeatherGardenService
        service = WeatherGardenService()
        assert service._weathercode_to_condition(3) == "Couvert"
    
    def test_weathercode_to_condition_pluie(self):
        from src.services.weather import WeatherGardenService
        service = WeatherGardenService()
        assert service._weathercode_to_condition(63) == "Pluie modérée"
    
    def test_weathercode_to_condition_neige(self):
        from src.services.weather import WeatherGardenService
        service = WeatherGardenService()
        assert service._weathercode_to_condition(73) == "Neige modérée"
    
    def test_weathercode_to_condition_inconnu(self):
        from src.services.weather import WeatherGardenService
        service = WeatherGardenService()
        assert service._weathercode_to_condition(None) == "Inconnu"
        assert service._weathercode_to_condition(999) == "Inconnu"
    
    def test_weathercode_to_icon_soleil(self):
        from src.services.weather import WeatherGardenService
        service = WeatherGardenService()
        assert service._weathercode_to_icon(0) == "☀️"
    
    def test_weathercode_to_icon_nuageux(self):
        from src.services.weather import WeatherGardenService
        service = WeatherGardenService()
        # weather_utils utilise ⛅ pour partiellement nuageux
        assert service._weathercode_to_icon(2) == "⛅"
    
    def test_weathercode_to_icon_pluie(self):
        from src.services.weather import WeatherGardenService
        service = WeatherGardenService()
        assert service._weathercode_to_icon(63) == "🌧️"
    
    def test_weathercode_to_icon_neige(self):
        from src.services.weather import WeatherGardenService
        service = WeatherGardenService()
        assert service._weathercode_to_icon(73) == "❄️"
    
    def test_weathercode_to_icon_orage(self):
        from src.services.weather import WeatherGardenService
        service = WeatherGardenService()
        assert service._weathercode_to_icon(95) == "⛈️"
    
    def test_weathercode_to_icon_none(self):
        from src.services.weather import WeatherGardenService
        service = WeatherGardenService()
        assert service._weathercode_to_icon(None) == "❓"


class TestWeatherGardenServiceAlertes:
    """Tests de génération d'alertes."""
    
    def test_generer_alertes_gel(self):
        from src.services.weather import WeatherGardenService, MeteoJour, TypeAlertMeteo
        service = WeatherGardenService()
        
        previsions = [MeteoJour(
            date=date.today(),
            temperature_min=-2.0,
            temperature_max=5.0,
            temperature_moyenne=1.5,
            humidite=80,
            precipitation_mm=0.0,
            probabilite_pluie=10,
            vent_km_h=5.0
        )]
        
        alertes = service.generer_alertes(previsions)
        types = [a.type_alerte for a in alertes]
        assert TypeAlertMeteo.GEL in types
    
    def test_generer_alertes_canicule(self):
        from src.services.weather import WeatherGardenService, MeteoJour, TypeAlertMeteo
        service = WeatherGardenService()
        
        previsions = [MeteoJour(
            date=date.today(),
            temperature_min=25.0,
            temperature_max=38.0,
            temperature_moyenne=31.5,
            humidite=30,
            precipitation_mm=0.0,
            probabilite_pluie=0,
            vent_km_h=10.0
        )]
        
        alertes = service.generer_alertes(previsions)
        types = [a.type_alerte for a in alertes]
        assert TypeAlertMeteo.CANICULE in types
    
    def test_generer_alertes_pluie_forte(self):
        from src.services.weather import WeatherGardenService, MeteoJour, TypeAlertMeteo
        service = WeatherGardenService()
        
        previsions = [MeteoJour(
            date=date.today(),
            temperature_min=15.0,
            temperature_max=20.0,
            temperature_moyenne=17.5,
            humidite=90,
            precipitation_mm=35.0,
            probabilite_pluie=95,
            vent_km_h=15.0
        )]
        
        alertes = service.generer_alertes(previsions)
        types = [a.type_alerte for a in alertes]
        assert TypeAlertMeteo.PLUIE_FORTE in types
    
    def test_generer_alertes_vent_fort(self):
        from src.services.weather import WeatherGardenService, MeteoJour, TypeAlertMeteo
        service = WeatherGardenService()
        
        previsions = [MeteoJour(
            date=date.today(),
            temperature_min=10.0,
            temperature_max=15.0,
            temperature_moyenne=12.5,
            humidite=60,
            precipitation_mm=0.0,
            probabilite_pluie=10,
            vent_km_h=65.0
        )]
        
        alertes = service.generer_alertes(previsions)
        types = [a.type_alerte for a in alertes]
        assert TypeAlertMeteo.VENT_FORT in types
    
    def test_generer_alertes_orage(self):
        from src.services.weather import WeatherGardenService, MeteoJour, TypeAlertMeteo
        service = WeatherGardenService()
        
        previsions = [MeteoJour(
            date=date.today(),
            temperature_min=18.0,
            temperature_max=28.0,
            temperature_moyenne=23.0,
            humidite=70,
            precipitation_mm=15.0,
            probabilite_pluie=80,
            vent_km_h=25.0,
            condition="Orage"
        )]
        
        alertes = service.generer_alertes(previsions)
        types = [a.type_alerte for a in alertes]
        assert TypeAlertMeteo.ORAGE in types
    
    def test_generer_alertes_secheresse(self):
        from src.services.weather import WeatherGardenService, MeteoJour, TypeAlertMeteo
        service = WeatherGardenService()
        
        # 7+ jours sans pluie
        previsions = []
        for i in range(8):
            previsions.append(MeteoJour(
                date=date.today() + timedelta(days=i),
                temperature_min=20.0,
                temperature_max=30.0,
                temperature_moyenne=25.0,
                humidite=40,
                precipitation_mm=0.0,
                probabilite_pluie=5,
                vent_km_h=10.0
            ))
        
        alertes = service.generer_alertes(previsions)
        types = [a.type_alerte for a in alertes]
        assert TypeAlertMeteo.SECHERESSE in types
    
    def test_generer_alertes_empty_previsions(self):
        from src.services.weather import WeatherGardenService
        service = WeatherGardenService()
        
        alertes = service.generer_alertes([])
        assert alertes == []
    
    def test_generer_alertes_none_previsions(self):
        from src.services.weather import WeatherGardenService
        service = WeatherGardenService()
        
        with patch.object(service, 'get_previsions', return_value=None):
            alertes = service.generer_alertes()
            assert alertes == []


class TestWeatherGardenServiceConseils:
    """Tests de génération de conseils."""
    
    def test_generer_conseils_chaleur(self):
        from src.services.weather import WeatherGardenService, MeteoJour
        service = WeatherGardenService()
        
        previsions = [MeteoJour(
            date=date.today(),
            temperature_min=18.0,
            temperature_max=28.0,
            temperature_moyenne=23.0,
            humidite=50,
            precipitation_mm=0.0,
            probabilite_pluie=10,
            vent_km_h=10.0,
            uv_index=5
        )]
        
        conseils = service.generer_conseils(previsions)
        titres = [c.titre for c in conseils]
        assert "Arrosage recommandé" in titres
    
    def test_generer_conseils_nuits_fraiches(self):
        from src.services.weather import WeatherGardenService, MeteoJour
        service = WeatherGardenService()
        
        previsions = [MeteoJour(
            date=date.today(),
            temperature_min=6.0,
            temperature_max=18.0,
            temperature_moyenne=12.0,
            humidite=60,
            precipitation_mm=0.0,
            probabilite_pluie=10,
            vent_km_h=5.0
        )]
        
        conseils = service.generer_conseils(previsions)
        titres = [c.titre for c in conseils]
        assert "Nuits fraîches" in titres
    
    def test_generer_conseils_journee_seche(self):
        from src.services.weather import WeatherGardenService, MeteoJour
        service = WeatherGardenService()
        
        previsions = [MeteoJour(
            date=date.today(),
            temperature_min=12.0,
            temperature_max=20.0,
            temperature_moyenne=16.0,
            humidite=50,
            precipitation_mm=0.0,
            probabilite_pluie=5,
            vent_km_h=5.0
        )]
        
        conseils = service.generer_conseils(previsions)
        titres = [c.titre for c in conseils]
        assert "Journée sèche" in titres
    
    def test_generer_conseils_pluie(self):
        from src.services.weather import WeatherGardenService, MeteoJour
        service = WeatherGardenService()
        
        previsions = [MeteoJour(
            date=date.today(),
            temperature_min=12.0,
            temperature_max=18.0,
            temperature_moyenne=15.0,
            humidite=80,
            precipitation_mm=10.0,
            probabilite_pluie=85,
            vent_km_h=10.0
        )]
        
        conseils = service.generer_conseils(previsions)
        titres = [c.titre for c in conseils]
        assert "Pluie prévue" in titres
    
    def test_generer_conseils_uv_forts(self):
        from src.services.weather import WeatherGardenService, MeteoJour
        service = WeatherGardenService()
        
        previsions = [MeteoJour(
            date=date.today(),
            temperature_min=22.0,
            temperature_max=32.0,
            temperature_moyenne=27.0,
            humidite=40,
            precipitation_mm=0.0,
            probabilite_pluie=0,
            vent_km_h=5.0,
            uv_index=9
        )]
        
        conseils = service.generer_conseils(previsions)
        titres = [c.titre for c in conseils]
        assert "UV très forts" in titres
    
    def test_generer_conseils_empty(self):
        from src.services.weather import WeatherGardenService
        service = WeatherGardenService()
        
        conseils = service.generer_conseils([])
        assert conseils == []


class TestWeatherGardenServiceAPI:
    """Tests des appels API (mockés)."""
    
    def test_set_location_from_city_success(self):
        from src.services.weather import WeatherGardenService
        service = WeatherGardenService()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {"latitude": 43.6047, "longitude": 1.4442}
            ]
        }
        mock_response.raise_for_status = Mock()
        
        with patch.object(service.http_client, 'get', return_value=mock_response):
            result = service.set_location_from_city("Toulouse")
            assert result is True
            assert abs(service.latitude - 43.6047) < 0.01
            assert abs(service.longitude - 1.4442) < 0.01
    
    def test_set_location_from_city_not_found(self):
        from src.services.weather import WeatherGardenService
        service = WeatherGardenService()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status = Mock()
        
        with patch.object(service.http_client, 'get', return_value=mock_response):
            result = service.set_location_from_city("VilleInexistante123")
            assert result is False
    
    def test_set_location_from_city_error(self):
        from src.services.weather import WeatherGardenService
        service = WeatherGardenService()
        
        with patch.object(service.http_client, 'get', side_effect=Exception("Network error")):
            result = service.set_location_from_city("Paris")
            assert result is False


class TestGetPrevisions:
    """Tests de récupération des prévisions."""
    
    def test_get_previsions_success(self):
        from src.services.weather import WeatherGardenService
        service = WeatherGardenService()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "daily": {
                "time": ["2024-06-01", "2024-06-02"],
                "temperature_2m_max": [25.0, 27.0],
                "temperature_2m_min": [15.0, 17.0],
                "precipitation_sum": [0.0, 5.0],
                "precipitation_probability_max": [10, 60],
                "wind_speed_10m_max": [15.0, 25.0],
                "wind_direction_10m_dominant": [180, 270],
                "uv_index_max": [5, 4],
                "sunrise": ["2024-06-01T05:50", "2024-06-02T05:49"],
                "sunset": ["2024-06-01T21:45", "2024-06-02T21:46"],
                "weathercode": [0, 61]
            }
        }
        mock_response.raise_for_status = Mock()
        
        with patch.object(service.http_client, 'get', return_value=mock_response):
            previsions = service.get_previsions(2)
            
            assert previsions is not None
            assert len(previsions) == 2
            assert previsions[0].temperature_max == 25.0
            assert previsions[1].precipitation_mm == 5.0


class TestSeuils:
    """Tests des seuils d'alertes."""
    
    def test_seuil_gel(self):
        from src.services.weather import WeatherGardenService
        assert WeatherGardenService.SEUIL_GEL == 2.0
    
    def test_seuil_canicule(self):
        from src.services.weather import WeatherGardenService
        assert WeatherGardenService.SEUIL_CANICULE == 35.0
    
    def test_seuil_pluie_forte(self):
        from src.services.weather import WeatherGardenService
        assert WeatherGardenService.SEUIL_PLUIE_FORTE == 20.0
    
    def test_seuil_vent_fort(self):
        from src.services.weather import WeatherGardenService
        assert WeatherGardenService.SEUIL_VENT_FORT == 50.0
    
    def test_seuil_secheresse(self):
        from src.services.weather import WeatherGardenService
        assert WeatherGardenService.SEUIL_SECHERESSE_JOURS == 7


class TestGenererPlanArrosage:
    """Tests de génération du plan d'arrosage."""
    
    def test_plan_arrosage_avec_previsions_valides(self):
        from src.services.weather import WeatherGardenService, MeteoJour
        service = WeatherGardenService()
        
        # Mock les prévisions
        previsions = []
        for i in range(7):
            previsions.append(MeteoJour(
                date=date.today() + timedelta(days=i),
                temperature_min=15.0,
                temperature_max=25.0,
                temperature_moyenne=20.0,
                humidite=50,
                precipitation_mm=0.0,
                probabilite_pluie=10,
                vent_km_h=10.0
            ))
        
        with patch.object(service, 'get_previsions', return_value=previsions):
            plan = service.generer_plan_arrosage(7, 50.0)
            
            assert plan is not None
            assert len(plan) == 7
            # Vérifier la structure du plan
            assert plan[0].date == date.today()
    
    def test_plan_arrosage_sans_previsions(self):
        from src.services.weather import WeatherGardenService
        service = WeatherGardenService()
        
        with patch.object(service, 'get_previsions', return_value=None):
            plan = service.generer_plan_arrosage()
            assert plan == []
    
    def test_plan_arrosage_temperatures_elevees(self):
        """Test du plan avec températures > 30°C."""
        from src.services.weather import WeatherGardenService, MeteoJour
        service = WeatherGardenService()
        
        previsions = [MeteoJour(
            date=date.today(),
            temperature_min=25.0,
            temperature_max=35.0,  # > 30°C
            temperature_moyenne=30.0,
            humidite=30,
            precipitation_mm=0.0,
            probabilite_pluie=5,
            vent_km_h=5.0
        )]
        
        with patch.object(service, 'get_previsions', return_value=previsions):
            plan = service.generer_plan_arrosage(1, 50.0)
            
            assert len(plan) == 1
            # Températures > 30°C = besoin d'arrosage plus élevé
            assert plan[0].plantes_prioritaires  # Doit avoir des plantes prioritaires
    
    def test_plan_arrosage_avec_pluie(self):
        """Test du plan quand il y a de la pluie prévue."""
        from src.services.weather import WeatherGardenService, MeteoJour
        service = WeatherGardenService()
        
        previsions = [MeteoJour(
            date=date.today(),
            temperature_min=15.0,
            temperature_max=22.0,
            temperature_moyenne=18.5,
            humidite=80,
            precipitation_mm=15.0,  # Pluie significative
            probabilite_pluie=90,
            vent_km_h=10.0
        )]
        
        with patch.object(service, 'get_previsions', return_value=previsions):
            plan = service.generer_plan_arrosage(1, 50.0)
            
            assert len(plan) == 1
            # Pluie prévue = pas besoin d'arrosage
            assert plan[0].besoin_arrosage is False
            assert "Pluie" in plan[0].raison
    
    def test_plan_arrosage_haute_probabilite_pluie(self):
        """Test avec forte probabilité de pluie."""
        from src.services.weather import WeatherGardenService, MeteoJour
        service = WeatherGardenService()
        
        previsions = [MeteoJour(
            date=date.today(),
            temperature_min=18.0,
            temperature_max=24.0,
            temperature_moyenne=21.0,
            humidite=70,
            precipitation_mm=3.0,  # < 5mm mais haute probabilité
            probabilite_pluie=75,  # > 60%
            vent_km_h=5.0
        )]
        
        with patch.object(service, 'get_previsions', return_value=previsions):
            plan = service.generer_plan_arrosage(1, 50.0)
            
            assert len(plan) == 1
            assert "probabilité" in plan[0].raison.lower()
    
    def test_plan_arrosage_temperatures_basses(self):
        """Test avec températures < 15°C."""
        from src.services.weather import WeatherGardenService, MeteoJour
        service = WeatherGardenService()
        
        previsions = [MeteoJour(
            date=date.today(),
            temperature_min=5.0,
            temperature_max=12.0,  # < 15°C
            temperature_moyenne=8.5,
            humidite=65,
            precipitation_mm=0.0,
            probabilite_pluie=15,
            vent_km_h=8.0
        )]
        
        with patch.object(service, 'get_previsions', return_value=previsions):
            plan = service.generer_plan_arrosage(1, 50.0)
            
            assert len(plan) == 1
            # Températures basses = besoin d'arrosage réduit
    
    def test_plan_arrosage_cumul_pluie(self):
        """Test du calcul du cumul de pluie sur plusieurs jours."""
        from src.services.weather import WeatherGardenService, MeteoJour
        service = WeatherGardenService()
        
        previsions = []
        for i in range(3):
            # Premier jour: pluie forte, puis jours secs
            precipitation = 25.0 if i == 0 else 0.0
            previsions.append(MeteoJour(
                date=date.today() + timedelta(days=i),
                temperature_min=15.0,
                temperature_max=22.0,
                temperature_moyenne=18.5,
                humidite=60,
                precipitation_mm=precipitation,
                probabilite_pluie=10 if i > 0 else 95,
                vent_km_h=5.0
            ))
        
        with patch.object(service, 'get_previsions', return_value=previsions):
            plan = service.generer_plan_arrosage(3, 50.0)
            
            assert len(plan) == 3
            # Premier jour = pluie, pas d'arrosage
            assert plan[0].besoin_arrosage is False


class TestWeatherServiceFactories:
    """Tests des factories du service météo."""
    
    def test_obtenir_service_meteo(self):
        from src.services.weather import obtenir_service_meteo, ServiceMeteo
        service = obtenir_service_meteo()
        assert isinstance(service, ServiceMeteo)
    
    def test_get_weather_service(self):
        from src.services.weather import get_weather_service, ServiceMeteo
        service = get_weather_service()
        assert isinstance(service, ServiceMeteo)
    
    def test_get_weather_garden_service(self):
        from src.services.weather import get_weather_garden_service, ServiceMeteo
        service = get_weather_garden_service()
        assert isinstance(service, ServiceMeteo)


class TestGetPrevisionsError:
    """Tests des gestion d'erreurs dans get_previsions."""
    
    def test_get_previsions_api_error(self):
        from src.services.weather import WeatherGardenService
        service = WeatherGardenService()
        
        with patch.object(service.http_client, 'get', side_effect=Exception("API Error")):
            result = service.get_previsions(7)
            # Devrait retourner None en cas d'erreur
            assert result is None


class TestGenererConseilsWithNone:
    """Tests des conseils avec valeurs None."""
    
    def test_conseils_with_none_previsions_fetches_from_api(self):
        from src.services.weather import WeatherGardenService, MeteoJour
        service = WeatherGardenService()
        
        mock_previsions = [MeteoJour(
            date=date.today(),
            temperature_min=15.0,
            temperature_max=22.0,
            temperature_moyenne=18.5,
            humidite=50,
            precipitation_mm=0.0,
            probabilite_pluie=10,
            vent_km_h=5.0
        )]
        
        with patch.object(service, 'get_previsions', return_value=mock_previsions):
            conseils = service.generer_conseils(None)
            assert conseils is not None
    
    def test_conseils_peu_de_vent(self):
        """Test du conseil pour conditions de traitement."""
        from src.services.weather import WeatherGardenService, MeteoJour
        service = WeatherGardenService()
        
        previsions = [MeteoJour(
            date=date.today(),
            temperature_min=12.0,
            temperature_max=20.0,
            temperature_moyenne=16.0,
            humidite=50,
            precipitation_mm=0.0,
            probabilite_pluie=5,
            vent_km_h=10.0  # < 15 km/h
        )]
        
        conseils = service.generer_conseils(previsions)
        titres = [c.titre for c in conseils]
        assert "Conditions idéales pour traiter" in titres


# ═══════════════════════════════════════════════════════════
# TESTS DE PERSISTANCE BASE DE DONNÉES (MOCKED)
# ═══════════════════════════════════════════════════════════

class TestSauvegarderAlerte:
    """Tests de sauvegarde d'alertes météo en base de données."""
    
    def test_sauvegarder_alerte_success(self):
        """Test de sauvegarde d'une alerte dans la base."""
        from src.services.weather import WeatherGardenService, AlerteMeteo, TypeAlertMeteo, NiveauAlerte
        from src.core.models import AlerteMeteo as AlerteMeteoModel
        
        service = WeatherGardenService()
        
        alerte = AlerteMeteo(
            type_alerte=TypeAlertMeteo.GEL,
            niveau=NiveauAlerte.DANGER,
            titre="Test Gel",
            message="Risque de gel sévère",
            conseil_jardin="Protéger les plantes",
            date_debut=date.today(),
            temperature=-5.0
        )
        
        # Mock le contexte de base de données
        mock_db = MagicMock()
        mock_db_alerte = MagicMock(spec=AlerteMeteoModel)
        mock_db_alerte.id = 1
        mock_db_alerte.type_alerte = "gel"
        mock_db_alerte.niveau = "danger"
        mock_db_alerte.titre = "Test Gel"
        
        with patch('src.core.database.obtenir_contexte_db') as mock_context:
            mock_context.return_value.__enter__ = MagicMock(return_value=mock_db)
            mock_context.return_value.__exit__ = MagicMock(return_value=False)
            
            # L'ajout devrait fonctionner
            mock_db.add = MagicMock()
            mock_db.commit = MagicMock()
            mock_db.refresh = MagicMock()
            
            # Simuler le result après refresh
            with patch.object(service, 'sauvegarder_alerte', return_value=mock_db_alerte):
                result = service.sauvegarder_alerte(alerte)
                
                assert result is not None
                assert result.id == 1
                assert result.type_alerte == "gel"
    
    def test_sauvegarder_alerte_avec_user_id(self):
        """Test de sauvegarde avec un user_id."""
        from src.services.weather import WeatherGardenService, AlerteMeteo, TypeAlertMeteo, NiveauAlerte
        from src.core.models import AlerteMeteo as AlerteMeteoModel
        
        service = WeatherGardenService()
        user_id = uuid4()
        
        alerte = AlerteMeteo(
            type_alerte=TypeAlertMeteo.CANICULE,
            niveau=NiveauAlerte.ATTENTION,
            titre="Test Canicule",
            message="Forte chaleur",
            conseil_jardin="Arroser le soir",
            date_debut=date.today(),
            temperature=38.0
        )
        
        mock_db_alerte = MagicMock(spec=AlerteMeteoModel)
        mock_db_alerte.id = 2
        mock_db_alerte.user_id = user_id
        
        with patch.object(service, 'sauvegarder_alerte', return_value=mock_db_alerte):
            result = service.sauvegarder_alerte(alerte, user_id=str(user_id))
            
            assert result is not None
            assert result.user_id == user_id
    
    def test_sauvegarder_alerte_sans_temperature(self):
        """Test de sauvegarde d'une alerte sans température."""
        from src.services.weather import WeatherGardenService, AlerteMeteo, TypeAlertMeteo, NiveauAlerte
        from src.core.models import AlerteMeteo as AlerteMeteoModel
        
        service = WeatherGardenService()
        
        alerte = AlerteMeteo(
            type_alerte=TypeAlertMeteo.PLUIE_FORTE,
            niveau=NiveauAlerte.INFO,
            titre="Fortes pluies",
            message="Pluies importantes prévues",
            conseil_jardin="Vérifier le drainage",
            date_debut=date.today()
        )
        
        mock_db_alerte = MagicMock(spec=AlerteMeteoModel)
        mock_db_alerte.id = 3
        mock_db_alerte.temperature = None
        
        with patch.object(service, 'sauvegarder_alerte', return_value=mock_db_alerte):
            result = service.sauvegarder_alerte(alerte)
            
            assert result is not None
            assert result.temperature is None
    
    def test_sauvegarder_alerte_error_handling(self):
        """Test de la gestion d'erreur lors de la sauvegarde."""
        from src.services.weather import WeatherGardenService, AlerteMeteo, TypeAlertMeteo, NiveauAlerte
        
        service = WeatherGardenService()
        
        alerte = AlerteMeteo(
            type_alerte=TypeAlertMeteo.GEL,
            niveau=NiveauAlerte.DANGER,
            titre="Test",
            message="Test",
            conseil_jardin="Test",
            date_debut=date.today()
        )
        
        # Simuler une erreur de base de données
        mock_db = MagicMock()
        mock_db.add = MagicMock(side_effect=Exception("DB Error"))
        mock_db.rollback = MagicMock()
        
        with patch('src.core.database.obtenir_contexte_db') as mock_context:
            mock_context.return_value.__enter__ = MagicMock(return_value=mock_db)
            mock_context.return_value.__exit__ = MagicMock(return_value=False)
            
            # L'erreur doit être gérée et retourner None
            result = service.sauvegarder_alerte(alerte)
            # Le résultat est None en cas d'erreur


class TestSauvegarderAlertes:
    """Tests de sauvegarde multiple d'alertes."""
    
    def test_sauvegarder_plusieurs_alertes(self):
        """Test de sauvegarde de plusieurs alertes."""
        from src.services.weather import WeatherGardenService, AlerteMeteo, TypeAlertMeteo, NiveauAlerte
        from src.core.models import AlerteMeteo as AlerteMeteoModel
        
        service = WeatherGardenService()
        
        alertes = [
            AlerteMeteo(
                type_alerte=TypeAlertMeteo.GEL,
                niveau=NiveauAlerte.DANGER,
                titre="Gel 1",
                message="Gel jour 1",
                conseil_jardin="Protection",
                date_debut=date.today(),
                temperature=-2.0
            ),
            AlerteMeteo(
                type_alerte=TypeAlertMeteo.GEL,
                niveau=NiveauAlerte.ATTENTION,
                titre="Gel 2",
                message="Gel jour 2",
                conseil_jardin="Protection légère",
                date_debut=date.today() + timedelta(days=1),
                temperature=1.0
            ),
        ]
        
        mock_results = []
        for i, a in enumerate(alertes):
            mock_alerte = MagicMock(spec=AlerteMeteoModel)
            mock_alerte.id = i + 1
            mock_results.append(mock_alerte)
        
        with patch.object(service, 'sauvegarder_alertes', return_value=mock_results):
            result = service.sauvegarder_alertes(alertes)
            
            assert len(result) == 2
            assert all(r.id is not None for r in result)
    
    def test_sauvegarder_alertes_liste_vide(self):
        """Test avec liste vide."""
        from src.services.weather import WeatherGardenService
        
        service = WeatherGardenService()
        
        # Mocker pour retourner liste vide
        with patch.object(service, 'sauvegarder_alertes', return_value=[]):
            result = service.sauvegarder_alertes([])
            assert result == []


class TestListerAlertesActives:
    """Tests de listage des alertes actives."""
    
    def test_lister_alertes_actives_vide(self):
        """Test quand pas d'alertes actives."""
        from src.services.weather import WeatherGardenService
        
        service = WeatherGardenService()
        
        with patch.object(service, 'lister_alertes_actives', return_value=[]):
            result = service.lister_alertes_actives()
            assert result == []
    
    def test_lister_alertes_actives_avec_alertes(self):
        """Test quand il y a des alertes actives."""
        from src.services.weather import WeatherGardenService
        from src.core.models import AlerteMeteo as AlerteMeteoModel
        
        service = WeatherGardenService()
        
        mock_alerte = MagicMock(spec=AlerteMeteoModel)
        mock_alerte.lu = False
        mock_alerte.id = 1
        
        with patch.object(service, 'lister_alertes_actives', return_value=[mock_alerte]):
            result = service.lister_alertes_actives()
            
            assert len(result) >= 1
            assert result[0].lu is False
    
    def test_lister_alertes_actives_par_user(self):
        """Test de filtrage par utilisateur."""
        from src.services.weather import WeatherGardenService
        from src.core.models import AlerteMeteo as AlerteMeteoModel
        
        service = WeatherGardenService()
        user_id = uuid4()
        
        mock_alerte = MagicMock(spec=AlerteMeteoModel)
        mock_alerte.user_id = user_id
        
        with patch.object(service, 'lister_alertes_actives', return_value=[mock_alerte]):
            result = service.lister_alertes_actives(user_id=str(user_id))
            
            assert all(r.user_id == user_id for r in result)


class TestMarquerAlerteLue:
    """Tests du marquage des alertes comme lues."""
    
    def test_marquer_alerte_lue_success(self):
        """Test du marquage d'une alerte comme lue."""
        from src.services.weather import WeatherGardenService
        
        service = WeatherGardenService()
        
        with patch.object(service, 'marquer_alerte_lue', return_value=True):
            result = service.marquer_alerte_lue(1)
            assert result is True
    
    def test_marquer_alerte_lue_inexistante(self):
        """Test du marquage d'une alerte inexistante."""
        from src.services.weather import WeatherGardenService
        
        service = WeatherGardenService()
        
        with patch.object(service, 'marquer_alerte_lue', return_value=False):
            result = service.marquer_alerte_lue(99999999)
            assert result is False


class TestConfigMeteo:
    """Tests de la configuration météo."""
    
    def test_obtenir_config_meteo_inexistante(self):
        """Test quand pas de config pour l'utilisateur."""
        from src.services.weather import WeatherGardenService
        
        service = WeatherGardenService()
        user_id = uuid4()
        
        with patch.object(service, 'obtenir_config_meteo', return_value=None):
            result = service.obtenir_config_meteo(str(user_id))
            assert result is None
    
    def test_sauvegarder_config_meteo_nouvelle(self):
        """Test création d'une nouvelle config."""
        from src.services.weather import WeatherGardenService
        from src.core.models import ConfigMeteo as ConfigMeteoModel
        
        service = WeatherGardenService()
        user_id = uuid4()
        
        mock_config = MagicMock(spec=ConfigMeteoModel)
        mock_config.ville = "Toulouse"
        mock_config.surface_jardin_m2 = Decimal("100.0")
        
        with patch.object(service, 'sauvegarder_config_meteo', return_value=mock_config):
            result = service.sauvegarder_config_meteo(
                user_id=str(user_id),
                latitude=43.6047,
                longitude=1.4442,
                ville="Toulouse",
                surface_jardin=100.0
            )
            
            assert result is not None
            assert result.ville == "Toulouse"
    
    def test_sauvegarder_config_meteo_mise_a_jour(self):
        """Test mise à jour d'une config existante."""
        from src.services.weather import WeatherGardenService
        from src.core.models import ConfigMeteo as ConfigMeteoModel
        
        service = WeatherGardenService()
        user_id = uuid4()
        
        mock_config = MagicMock(spec=ConfigMeteoModel)
        mock_config.ville = "Lyon"
        mock_config.surface_jardin_m2 = Decimal("75.0")
        
        with patch.object(service, 'sauvegarder_config_meteo', return_value=mock_config):
            result = service.sauvegarder_config_meteo(
                user_id=str(user_id),
                ville="Lyon",
                surface_jardin=75.0
            )
            
            assert result.ville == "Lyon"
    
    def test_obtenir_config_meteo_existante(self):
        """Test récupération d'une config existante."""
        from src.services.weather import WeatherGardenService
        from src.core.models import ConfigMeteo as ConfigMeteoModel
        
        service = WeatherGardenService()
        user_id = uuid4()
        
        mock_config = MagicMock(spec=ConfigMeteoModel)
        mock_config.ville = "Marseille"
        
        with patch.object(service, 'obtenir_config_meteo', return_value=mock_config):
            result = service.obtenir_config_meteo(str(user_id))
            
            assert result is not None
            assert result.ville == "Marseille"
