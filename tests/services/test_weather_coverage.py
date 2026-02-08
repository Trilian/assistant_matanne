"""
Tests complets pour src/services/weather.py

Couverture cible: >80%
"""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import httpx


# ═══════════════════════════════════════════════════════════
# TESTS SCHÉMAS PYDANTIC
# ═══════════════════════════════════════════════════════════


class TestTypeAlertMeteo:
    """Tests enum TypeAlertMeteo."""

    def test_import_enum(self):
        from src.services.weather import TypeAlertMeteo
        assert TypeAlertMeteo is not None

    def test_enum_values(self):
        from src.services.weather import TypeAlertMeteo
        assert TypeAlertMeteo.GEL == "gel"
        assert TypeAlertMeteo.CANICULE == "canicule"
        assert TypeAlertMeteo.PLUIE_FORTE == "pluie_forte"
        assert TypeAlertMeteo.SECHERESSE == "sécheresse"
        assert TypeAlertMeteo.VENT_FORT == "vent_fort"
        assert TypeAlertMeteo.ORAGE == "orage"
        assert TypeAlertMeteo.GRELE == "grêle"
        assert TypeAlertMeteo.NEIGE == "neige"

    def test_enum_count(self):
        from src.services.weather import TypeAlertMeteo
        assert len(TypeAlertMeteo) == 8


class TestNiveauAlerte:
    """Tests enum NiveauAlerte."""

    def test_enum_values(self):
        from src.services.weather import NiveauAlerte
        assert NiveauAlerte.INFO == "info"
        assert NiveauAlerte.ATTENTION == "attention"
        assert NiveauAlerte.DANGER == "danger"


class TestMeteoJour:
    """Tests schéma MeteoJour."""

    def test_creation_basique(self):
        from src.services.weather import MeteoJour
        
        meteo = MeteoJour(
            date=date.today(),
            temperature_min=5.0,
            temperature_max=15.0,
            temperature_moyenne=10.0,
            humidite=60,
            precipitation_mm=0.0,
            probabilite_pluie=10,
            vent_km_h=20.0
        )
        
        assert meteo.temperature_min == 5.0
        assert meteo.temperature_max == 15.0
        assert meteo.humidite == 60

    def test_valeurs_optionnelles(self):
        from src.services.weather import MeteoJour
        
        meteo = MeteoJour(
            date=date.today(),
            temperature_min=0.0,
            temperature_max=10.0,
            temperature_moyenne=5.0,
            humidite=50,
            precipitation_mm=5.0,
            probabilite_pluie=80,
            vent_km_h=30.0,
            direction_vent="NE",
            uv_index=5,
            lever_soleil="07:30",
            coucher_soleil="19:45",
            condition="nuageux",
            icone="☁️"
        )
        
        assert meteo.direction_vent == "NE"
        assert meteo.uv_index == 5
        assert meteo.condition == "nuageux"


class TestAlerteMeteo:
    """Tests schéma AlerteMeteo."""

    def test_creation_alerte(self):
        from src.services.weather import AlerteMeteo, TypeAlertMeteo, NiveauAlerte
        
        alerte = AlerteMeteo(
            type_alerte=TypeAlertMeteo.GEL,
            niveau=NiveauAlerte.DANGER,
            titre="Risque de gel",
            message="Gel prévu cette nuit",
            conseil_jardin="Protéger les plantes",
            date_debut=date.today()
        )
        
        assert alerte.type_alerte == TypeAlertMeteo.GEL
        assert alerte.niveau == NiveauAlerte.DANGER
        assert alerte.date_fin is None

    def test_alerte_avec_temperature(self):
        from src.services.weather import AlerteMeteo, TypeAlertMeteo, NiveauAlerte
        
        alerte = AlerteMeteo(
            type_alerte=TypeAlertMeteo.CANICULE,
            niveau=NiveauAlerte.ATTENTION,
            titre="Canicule",
            message="Forte chaleur",
            conseil_jardin="Arroser le soir",
            date_debut=date.today(),
            temperature=38.5
        )
        
        assert alerte.temperature == 38.5


class TestConseilJardin:
    """Tests schéma ConseilJardin."""

    def test_creation_conseil(self):
        from src.services.weather import ConseilJardin
        
        conseil = ConseilJardin(
            priorite=1,
            icone="🌱",
            titre="Arrosage",
            description="Arrosez vos plantes ce matin"
        )
        
        assert conseil.priorite == 1
        assert conseil.icone == "🌱"

    def test_conseil_avec_plantes(self):
        from src.services.weather import ConseilJardin
        
        conseil = ConseilJardin(
            titre="Protection gel",
            description="Protéger les plantes sensibles",
            plantes_concernees=["Tomates", "Basilic", "Courgettes"],
            action_recommandee="Couvrir avec un voile"
        )
        
        assert len(conseil.plantes_concernees) == 3


class TestPlanArrosage:
    """Tests schéma PlanArrosage."""

    def test_creation_plan(self):
        from src.services.weather import PlanArrosage
        
        plan = PlanArrosage(
            date=date.today(),
            besoin_arrosage=True,
            quantite_recommandee_litres=5.0,
            raison="Pas de pluie prévue"
        )
        
        assert plan.besoin_arrosage is True
        assert plan.quantite_recommandee_litres == 5.0


# ═══════════════════════════════════════════════════════════
# TESTS SERVICE WEATHER
# ═══════════════════════════════════════════════════════════


class TestWeatherGardenServiceInit:
    """Tests initialisation du service."""

    def test_init_default(self):
        from src.services.weather import WeatherGardenService
        
        service = WeatherGardenService()
        
        # Paris par défaut
        assert service.latitude == 48.8566
        assert service.longitude == 2.3522
        assert service.http_client is not None

    def test_init_custom_location(self):
        from src.services.weather import WeatherGardenService
        
        # Lyon
        service = WeatherGardenService(latitude=45.7640, longitude=4.8357)
        
        assert service.latitude == 45.7640
        assert service.longitude == 4.8357

    def test_set_location(self):
        from src.services.weather import WeatherGardenService
        
        service = WeatherGardenService()
        service.set_location(43.6047, 1.4442)  # Toulouse
        
        assert service.latitude == 43.6047
        assert service.longitude == 1.4442

    def test_seuils_constants(self):
        from src.services.weather import WeatherGardenService
        
        assert WeatherGardenService.SEUIL_GEL == 2.0
        assert WeatherGardenService.SEUIL_CANICULE == 35.0
        assert WeatherGardenService.SEUIL_PLUIE_FORTE == 20.0
        assert WeatherGardenService.SEUIL_VENT_FORT == 50.0
        assert WeatherGardenService.API_URL == "https://api.open-meteo.com/v1/forecast"


class TestWeatherGardenServiceSetLocationFromCity:
    """Tests set_location_from_city."""

    def test_set_location_from_city_success(self):
        from src.services.weather import WeatherGardenService
        
        service = WeatherGardenService()
        
        # Mock HTTP client
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{"latitude": 43.2965, "longitude": 5.3698}]
        }
        mock_response.raise_for_status = Mock()
        
        with patch.object(service.http_client, 'get', return_value=mock_response):
            result = service.set_location_from_city("Marseille")
        
        assert result is True
        assert service.latitude == 43.2965
        assert service.longitude == 5.3698

    def test_set_location_from_city_not_found(self):
        from src.services.weather import WeatherGardenService
        
        service = WeatherGardenService()
        
        mock_response = Mock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status = Mock()
        
        with patch.object(service.http_client, 'get', return_value=mock_response):
            result = service.set_location_from_city("VilleInexistante123")
        
        assert result is False

    def test_set_location_from_city_error(self):
        from src.services.weather import WeatherGardenService
        
        service = WeatherGardenService()
        
        with patch.object(service.http_client, 'get', side_effect=httpx.HTTPError("Network error")):
            result = service.set_location_from_city("Paris")
        
        assert result is False


class TestWeatherGardenServiceGetPrevisions:
    """Tests get_previsions."""

    def test_get_previsions_success(self):
        from src.services.weather import WeatherGardenService
        
        service = WeatherGardenService()
        
        today = date.today()
        mock_response = Mock()
        mock_response.json.return_value = {
            "daily": {
                "time": [today.isoformat(), (today + timedelta(days=1)).isoformat()],
                "temperature_2m_min": [5.0, 8.0],
                "temperature_2m_max": [15.0, 18.0],
                "precipitation_sum": [0.0, 5.0],
                "precipitation_probability_max": [10, 80],
                "wind_speed_10m_max": [20.0, 35.0],
                "wind_direction_10m_dominant": [180, 270],
                "uv_index_max": [5, 3],
                "sunrise": [f"{today}T07:30:00", f"{today + timedelta(days=1)}T07:28:00"],
                "sunset": [f"{today}T19:45:00", f"{today + timedelta(days=1)}T19:47:00"],
                "weathercode": [1, 61],
            }
        }
        mock_response.raise_for_status = Mock()
        
        with patch.object(service.http_client, 'get', return_value=mock_response):
            previsions = service.get_previsions(7)
        
        assert previsions is not None
        assert len(previsions) == 2
        assert previsions[0].temperature_min == 5.0
        assert previsions[0].temperature_max == 15.0

    def test_get_previsions_error(self):
        from src.services.weather import WeatherGardenService
        
        service = WeatherGardenService()
        
        with patch.object(service.http_client, 'get', side_effect=Exception("API Error")):
            previsions = service.get_previsions(7)
        
        # Should return None on error (default_return)
        assert previsions is None


class TestWeatherGardenServiceGenererAlertes:
    """Tests generer_alertes."""

    def test_generer_alertes_gel(self):
        from src.services.weather import WeatherGardenService, MeteoJour, TypeAlertMeteo, NiveauAlerte
        
        service = WeatherGardenService()
        
        previsions = [
            MeteoJour(
                date=date.today(),
                temperature_min=-2.0,
                temperature_max=5.0,
                temperature_moyenne=1.5,
                humidite=80,
                precipitation_mm=0.0,
                probabilite_pluie=0,
                vent_km_h=10.0
            )
        ]
        
        alertes = service.generer_alertes(previsions)
        
        assert len(alertes) >= 1
        alerte_gel = next((a for a in alertes if a.type_alerte == TypeAlertMeteo.GEL), None)
        assert alerte_gel is not None
        assert alerte_gel.niveau == NiveauAlerte.DANGER  # < 0°C

    def test_generer_alertes_canicule(self):
        from src.services.weather import WeatherGardenService, MeteoJour, TypeAlertMeteo, NiveauAlerte
        
        service = WeatherGardenService()
        
        previsions = [
            MeteoJour(
                date=date.today(),
                temperature_min=25.0,
                temperature_max=40.0,
                temperature_moyenne=32.5,
                humidite=30,
                precipitation_mm=0.0,
                probabilite_pluie=0,
                vent_km_h=5.0
            )
        ]
        
        alertes = service.generer_alertes(previsions)
        
        alerte_canicule = next((a for a in alertes if a.type_alerte == TypeAlertMeteo.CANICULE), None)
        assert alerte_canicule is not None
        assert alerte_canicule.niveau == NiveauAlerte.DANGER  # >= 40°C

    def test_generer_alertes_pluie_forte(self):
        from src.services.weather import WeatherGardenService, MeteoJour, TypeAlertMeteo
        
        service = WeatherGardenService()
        
        previsions = [
            MeteoJour(
                date=date.today(),
                temperature_min=15.0,
                temperature_max=18.0,
                temperature_moyenne=16.5,
                humidite=90,
                precipitation_mm=30.0,  # > SEUIL_PLUIE_FORTE (20mm)
                probabilite_pluie=95,
                vent_km_h=20.0
            )
        ]
        
        alertes = service.generer_alertes(previsions)
        
        alerte_pluie = next((a for a in alertes if a.type_alerte == TypeAlertMeteo.PLUIE_FORTE), None)
        assert alerte_pluie is not None

    def test_generer_alertes_vent_fort(self):
        from src.services.weather import WeatherGardenService, MeteoJour, TypeAlertMeteo
        
        service = WeatherGardenService()
        
        previsions = [
            MeteoJour(
                date=date.today(),
                temperature_min=10.0,
                temperature_max=15.0,
                temperature_moyenne=12.5,
                humidite=60,
                precipitation_mm=0.0,
                probabilite_pluie=10,
                vent_km_h=60.0  # > SEUIL_VENT_FORT (50 km/h)
            )
        ]
        
        alertes = service.generer_alertes(previsions)
        
        alerte_vent = next((a for a in alertes if a.type_alerte == TypeAlertMeteo.VENT_FORT), None)
        assert alerte_vent is not None

    def test_generer_alertes_orage(self):
        from src.services.weather import WeatherGardenService, MeteoJour, TypeAlertMeteo
        
        service = WeatherGardenService()
        
        previsions = [
            MeteoJour(
                date=date.today(),
                temperature_min=18.0,
                temperature_max=28.0,
                temperature_moyenne=23.0,
                humidite=75,
                precipitation_mm=10.0,
                probabilite_pluie=80,
                vent_km_h=40.0,
                condition="Orage"
            )
        ]
        
        alertes = service.generer_alertes(previsions)
        
        alerte_orage = next((a for a in alertes if a.type_alerte == TypeAlertMeteo.ORAGE), None)
        assert alerte_orage is not None

    def test_generer_alertes_secheresse(self):
        from src.services.weather import WeatherGardenService, MeteoJour, TypeAlertMeteo
        
        service = WeatherGardenService()
        
        # 8 jours sans pluie (> SEUIL_SECHERESSE_JOURS = 7)
        previsions = [
            MeteoJour(
                date=date.today() + timedelta(days=i),
                temperature_min=20.0,
                temperature_max=30.0,
                temperature_moyenne=25.0,
                humidite=40,
                precipitation_mm=0.0,  # Pas de pluie
                probabilite_pluie=5,  # Faible probabilité
                vent_km_h=10.0
            )
            for i in range(8)
        ]
        
        alertes = service.generer_alertes(previsions)
        
        alerte_secheresse = next((a for a in alertes if a.type_alerte == TypeAlertMeteo.SECHERESSE), None)
        assert alerte_secheresse is not None

    def test_generer_alertes_sans_previsions(self):
        from src.services.weather import WeatherGardenService
        
        service = WeatherGardenService()
        
        # Mock get_previsions pour retourner None
        with patch.object(service, 'get_previsions', return_value=None):
            alertes = service.generer_alertes()
        
        assert alertes == []

    def test_generer_alertes_aucune(self):
        from src.services.weather import WeatherGardenService, MeteoJour
        
        service = WeatherGardenService()
        
        # Météo parfaite, aucune alerte
        previsions = [
            MeteoJour(
                date=date.today(),
                temperature_min=15.0,
                temperature_max=25.0,
                temperature_moyenne=20.0,
                humidite=50,
                precipitation_mm=5.0,  # Pluie légère
                probabilite_pluie=50,
                vent_km_h=15.0
            )
        ]
        
        alertes = service.generer_alertes(previsions)
        
        # Pas d'alertes critiques
        assert len([a for a in alertes if a.type_alerte.value in ["gel", "canicule", "pluie_forte", "vent_fort"]]) == 0


class TestWeatherGardenServiceGenererConseils:
    """Tests generer_conseils."""

    def test_generer_conseils_sans_previsions(self):
        from src.services.weather import WeatherGardenService
        
        service = WeatherGardenService()
        
        # Mock get_previsions pour retourner None
        with patch.object(service, 'get_previsions', return_value=None):
            conseils = service.generer_conseils()
        
        assert conseils == []


class TestWeatherGardenServiceDirectionMethods:
    """Tests méthodes utilitaires de conversion."""

    def test_direction_from_degrees(self):
        from src.services.weather import WeatherGardenService
        
        service = WeatherGardenService()
        
        assert service._direction_from_degrees(0) == "N"
        assert service._direction_from_degrees(90) == "E"
        assert service._direction_from_degrees(180) == "S"
        assert service._direction_from_degrees(270) == "O"

    def test_weathercode_to_condition(self):
        from src.services.weather import WeatherGardenService
        
        service = WeatherGardenService()
        
        result = service._weathercode_to_condition(0)
        assert isinstance(result, str)

    def test_weathercode_to_icon(self):
        from src.services.weather import WeatherGardenService
        
        service = WeatherGardenService()
        
        result = service._weathercode_to_icon(0)
        assert isinstance(result, str)


# ═══════════════════════════════════════════════════════════
# TESTS EDGE CASES
# ═══════════════════════════════════════════════════════════


class TestWeatherEdgeCases:
    """Tests cas limites."""

    def test_previsions_limite_jours(self):
        from src.services.weather import WeatherGardenService
        
        service = WeatherGardenService()
        
        # Le service devrait limiter à 16 jours max
        mock_response = Mock()
        mock_response.json.return_value = {"daily": {"time": []}}
        mock_response.raise_for_status = Mock()
        
        with patch.object(service.http_client, 'get', return_value=mock_response) as mock_get:
            service.get_previsions(20)  # Demande 20 jours
        
        # Vérifie que forecast_days est limité à 16
        call_args = mock_get.call_args
        assert call_args[1]["params"]["forecast_days"] == 16

    def test_alerte_gel_attention_vs_danger(self):
        from src.services.weather import WeatherGardenService, MeteoJour, NiveauAlerte
        
        service = WeatherGardenService()
        
        # Température entre 0 et 2°C => ATTENTION
        previsions_attention = [
            MeteoJour(
                date=date.today(),
                temperature_min=1.5,
                temperature_max=8.0,
                temperature_moyenne=4.75,
                humidite=70,
                precipitation_mm=0.0,
                probabilite_pluie=10,
                vent_km_h=5.0
            )
        ]
        
        alertes = service.generer_alertes(previsions_attention)
        alerte_gel = next((a for a in alertes if "gel" in a.type_alerte.value.lower()), None)
        assert alerte_gel is not None
        assert alerte_gel.niveau == NiveauAlerte.ATTENTION

    def test_alerte_canicule_attention_vs_danger(self):
        from src.services.weather import WeatherGardenService, MeteoJour, NiveauAlerte
        
        service = WeatherGardenService()
        
        # Température entre 35 et 40°C => ATTENTION
        previsions_attention = [
            MeteoJour(
                date=date.today(),
                temperature_min=22.0,
                temperature_max=37.0,
                temperature_moyenne=29.5,
                humidite=40,
                precipitation_mm=0.0,
                probabilite_pluie=5,
                vent_km_h=10.0
            )
        ]
        
        alertes = service.generer_alertes(previsions_attention)
        alerte_canicule = next((a for a in alertes if "canicule" in a.type_alerte.value.lower()), None)
        assert alerte_canicule is not None
        assert alerte_canicule.niveau == NiveauAlerte.ATTENTION


class TestWeatherIntegration:
    """Tests d'intégration (sans appel API réel)."""

    def test_workflow_complet(self):
        from src.services.weather import WeatherGardenService, MeteoJour
        
        service = WeatherGardenService()
        
        # Simuler des prévisions
        previsions = [
            MeteoJour(
                date=date.today() + timedelta(days=i),
                temperature_min=10.0 + i,
                temperature_max=20.0 + i,
                temperature_moyenne=15.0 + i,
                humidite=60,
                precipitation_mm=2.0 if i % 3 == 0 else 0.0,
                probabilite_pluie=40 if i % 3 == 0 else 10,
                vent_km_h=15.0
            )
            for i in range(7)
        ]
        
        # Générer alertes
        alertes = service.generer_alertes(previsions)
        
        # Générer conseils
        conseils = service.generer_conseils(previsions)
        
        # Les deux devraient fonctionner sans erreur
        assert isinstance(alertes, list)
        assert isinstance(conseils, list)
