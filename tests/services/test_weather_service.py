"""
Tests complets pour le service WeatherGardenService.
"""
import pytest
from datetime import date, timedelta
from unittest.mock import Mock, patch, MagicMock

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

