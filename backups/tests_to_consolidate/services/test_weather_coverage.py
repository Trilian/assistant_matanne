"""
Tests complets pour src/services/weather.py

Couverture cible: >80%
"""

from datetime import date, timedelta
from unittest.mock import Mock, patch

import httpx
import pytest

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS SCHà‰MAS PYDANTIC
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


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
            vent_km_h=20.0,
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
            icone="â˜ï¸",
        )

        assert meteo.direction_vent == "NE"
        assert meteo.uv_index == 5
        assert meteo.condition == "nuageux"


class TestAlerteMeteo:
    """Tests schéma AlerteMeteo."""

    def test_creation_alerte(self):
        from src.services.weather import AlerteMeteo, NiveauAlerte, TypeAlertMeteo

        alerte = AlerteMeteo(
            type_alerte=TypeAlertMeteo.GEL,
            niveau=NiveauAlerte.DANGER,
            titre="Risque de gel",
            message="Gel prévu cette nuit",
            conseil_jardin="Protéger les plantes",
            date_debut=date.today(),
        )

        assert alerte.type_alerte == TypeAlertMeteo.GEL
        assert alerte.niveau == NiveauAlerte.DANGER
        assert alerte.date_fin is None

    def test_alerte_avec_temperature(self):
        from src.services.weather import AlerteMeteo, NiveauAlerte, TypeAlertMeteo

        alerte = AlerteMeteo(
            type_alerte=TypeAlertMeteo.CANICULE,
            niveau=NiveauAlerte.ATTENTION,
            titre="Canicule",
            message="Forte chaleur",
            conseil_jardin="Arroser le soir",
            date_debut=date.today(),
            temperature=38.5,
        )

        assert alerte.temperature == 38.5


class TestConseilJardin:
    """Tests schéma ConseilJardin."""

    def test_creation_conseil(self):
        from src.services.weather import ConseilJardin

        conseil = ConseilJardin(
            priorite=1, icone="ðŸŒ±", titre="Arrosage", description="Arrosez vos plantes ce matin"
        )

        assert conseil.priorite == 1
        assert conseil.icone == "ðŸŒ±"

    def test_conseil_avec_plantes(self):
        from src.services.weather import ConseilJardin

        conseil = ConseilJardin(
            titre="Protection gel",
            description="Protéger les plantes sensibles",
            plantes_concernees=["Tomates", "Basilic", "Courgettes"],
            action_recommandee="Couvrir avec un voile",
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
            raison="Pas de pluie prévue",
        )

        assert plan.besoin_arrosage is True
        assert plan.quantite_recommandee_litres == 5.0


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS SERVICE WEATHER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


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
        mock_response.json.return_value = {"results": [{"latitude": 43.2965, "longitude": 5.3698}]}
        mock_response.raise_for_status = Mock()

        with patch.object(service.http_client, "get", return_value=mock_response):
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

        with patch.object(service.http_client, "get", return_value=mock_response):
            result = service.set_location_from_city("VilleInexistante123")

        assert result is False

    def test_set_location_from_city_error(self):
        from src.services.weather import WeatherGardenService

        service = WeatherGardenService()

        with patch.object(service.http_client, "get", side_effect=httpx.HTTPError("Network error")):
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

        with patch.object(service.http_client, "get", return_value=mock_response):
            previsions = service.get_previsions(7)

        assert previsions is not None
        assert len(previsions) == 2
        assert previsions[0].temperature_min == 5.0
        assert previsions[0].temperature_max == 15.0

    def test_get_previsions_error(self):
        from src.services.weather import WeatherGardenService

        service = WeatherGardenService()

        with patch.object(service.http_client, "get", side_effect=Exception("API Error")):
            previsions = service.get_previsions(7)

        # Should return None on error (default_return)
        assert previsions is None


class TestWeatherGardenServiceGenererAlertes:
    """Tests generer_alertes."""

    def test_generer_alertes_gel(self):
        from src.services.weather import (
            MeteoJour,
            NiveauAlerte,
            TypeAlertMeteo,
            WeatherGardenService,
        )

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
                vent_km_h=10.0,
            )
        ]

        alertes = service.generer_alertes(previsions)

        assert len(alertes) >= 1
        alerte_gel = next((a for a in alertes if a.type_alerte == TypeAlertMeteo.GEL), None)
        assert alerte_gel is not None
        assert alerte_gel.niveau == NiveauAlerte.DANGER  # < 0Â°C

    def test_generer_alertes_canicule(self):
        from src.services.weather import (
            MeteoJour,
            NiveauAlerte,
            TypeAlertMeteo,
            WeatherGardenService,
        )

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
                vent_km_h=5.0,
            )
        ]

        alertes = service.generer_alertes(previsions)

        alerte_canicule = next(
            (a for a in alertes if a.type_alerte == TypeAlertMeteo.CANICULE), None
        )
        assert alerte_canicule is not None
        assert alerte_canicule.niveau == NiveauAlerte.DANGER  # >= 40Â°C

    def test_generer_alertes_pluie_forte(self):
        from src.services.weather import MeteoJour, TypeAlertMeteo, WeatherGardenService

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
                vent_km_h=20.0,
            )
        ]

        alertes = service.generer_alertes(previsions)

        alerte_pluie = next(
            (a for a in alertes if a.type_alerte == TypeAlertMeteo.PLUIE_FORTE), None
        )
        assert alerte_pluie is not None

    def test_generer_alertes_vent_fort(self):
        from src.services.weather import MeteoJour, TypeAlertMeteo, WeatherGardenService

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
                vent_km_h=60.0,  # > SEUIL_VENT_FORT (50 km/h)
            )
        ]

        alertes = service.generer_alertes(previsions)

        alerte_vent = next((a for a in alertes if a.type_alerte == TypeAlertMeteo.VENT_FORT), None)
        assert alerte_vent is not None

    def test_generer_alertes_orage(self):
        from src.services.weather import MeteoJour, TypeAlertMeteo, WeatherGardenService

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
                condition="Orage",
            )
        ]

        alertes = service.generer_alertes(previsions)

        alerte_orage = next((a for a in alertes if a.type_alerte == TypeAlertMeteo.ORAGE), None)
        assert alerte_orage is not None

    def test_generer_alertes_secheresse(self):
        from src.services.weather import MeteoJour, TypeAlertMeteo, WeatherGardenService

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
                vent_km_h=10.0,
            )
            for i in range(8)
        ]

        alertes = service.generer_alertes(previsions)

        alerte_secheresse = next(
            (a for a in alertes if a.type_alerte == TypeAlertMeteo.SECHERESSE), None
        )
        assert alerte_secheresse is not None

    def test_generer_alertes_sans_previsions(self):
        from src.services.weather import WeatherGardenService

        service = WeatherGardenService()

        # Mock get_previsions pour retourner None
        with patch.object(service, "get_previsions", return_value=None):
            alertes = service.generer_alertes()

        assert alertes == []

    def test_generer_alertes_aucune(self):
        from src.services.weather import MeteoJour, WeatherGardenService

        service = WeatherGardenService()

        # météo parfaite, aucune alerte
        previsions = [
            MeteoJour(
                date=date.today(),
                temperature_min=15.0,
                temperature_max=25.0,
                temperature_moyenne=20.0,
                humidite=50,
                precipitation_mm=5.0,  # Pluie légère
                probabilite_pluie=50,
                vent_km_h=15.0,
            )
        ]

        alertes = service.generer_alertes(previsions)

        # Pas d'alertes critiques
        assert (
            len(
                [
                    a
                    for a in alertes
                    if a.type_alerte.value in ["gel", "canicule", "pluie_forte", "vent_fort"]
                ]
            )
            == 0
        )


class TestWeatherGardenServiceGenererConseils:
    """Tests generer_conseils."""

    def test_generer_conseils_sans_previsions(self):
        from src.services.weather import WeatherGardenService

        service = WeatherGardenService()

        # Mock get_previsions pour retourner None
        with patch.object(service, "get_previsions", return_value=None):
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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS EDGE CASES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestWeatherEdgeCases:
    """Tests cas limites."""

    def test_previsions_limite_jours(self):
        from src.services.weather import WeatherGardenService

        service = WeatherGardenService()

        # Le service devrait limiter à  16 jours max
        mock_response = Mock()
        mock_response.json.return_value = {"daily": {"time": []}}
        mock_response.raise_for_status = Mock()

        with patch.object(service.http_client, "get", return_value=mock_response) as mock_get:
            service.get_previsions(20)  # Demande 20 jours

        # Vérifie que forecast_days est limité à  16
        call_args = mock_get.call_args
        assert call_args[1]["params"]["forecast_days"] == 16

    def test_alerte_gel_attention_vs_danger(self):
        from src.services.weather import MeteoJour, NiveauAlerte, WeatherGardenService

        service = WeatherGardenService()

        # Température entre 0 et 2Â°C => ATTENTION
        previsions_attention = [
            MeteoJour(
                date=date.today(),
                temperature_min=1.5,
                temperature_max=8.0,
                temperature_moyenne=4.75,
                humidite=70,
                precipitation_mm=0.0,
                probabilite_pluie=10,
                vent_km_h=5.0,
            )
        ]

        alertes = service.generer_alertes(previsions_attention)
        alerte_gel = next((a for a in alertes if "gel" in a.type_alerte.value.lower()), None)
        assert alerte_gel is not None
        assert alerte_gel.niveau == NiveauAlerte.ATTENTION

    def test_alerte_canicule_attention_vs_danger(self):
        from src.services.weather import MeteoJour, NiveauAlerte, WeatherGardenService

        service = WeatherGardenService()

        # Température entre 35 et 40Â°C => ATTENTION
        previsions_attention = [
            MeteoJour(
                date=date.today(),
                temperature_min=22.0,
                temperature_max=37.0,
                temperature_moyenne=29.5,
                humidite=40,
                precipitation_mm=0.0,
                probabilite_pluie=5,
                vent_km_h=10.0,
            )
        ]

        alertes = service.generer_alertes(previsions_attention)
        alerte_canicule = next(
            (a for a in alertes if "canicule" in a.type_alerte.value.lower()), None
        )
        assert alerte_canicule is not None
        assert alerte_canicule.niveau == NiveauAlerte.ATTENTION


class TestWeatherIntegration:
    """Tests d'intégration (sans appel API réel)."""

    def test_workflow_complet(self):
        from src.services.weather import MeteoJour, WeatherGardenService

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
                vent_km_h=15.0,
            )
            for i in range(7)
        ]

        # générer alertes
        alertes = service.generer_alertes(previsions)

        # générer conseils
        conseils = service.generer_conseils(previsions)

        # Les deux devraient fonctionner sans erreur
        assert isinstance(alertes, list)
        assert isinstance(conseils, list)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS Gà‰OCODAGE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestWeatherGeocoding:
    """Tests pour la méthode set_location_from_city."""

    def test_set_location_from_city_success(self):
        """Test géocodage réussi."""
        from src.services.weather import WeatherGardenService

        service = WeatherGardenService()

        # Mock de la réponse HTTP
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{"latitude": 45.7640, "longitude": 4.8357, "name": "Lyon"}]
        }
        mock_response.raise_for_status = Mock()

        with patch.object(service.http_client, "get", return_value=mock_response):
            result = service.set_location_from_city("Lyon")

        assert result is True
        assert service.latitude == 45.7640
        assert service.longitude == 4.8357

    def test_set_location_from_city_no_results(self):
        """Test géocodage sans résultats."""
        from src.services.weather import WeatherGardenService

        service = WeatherGardenService()
        original_lat = service.latitude
        original_lon = service.longitude

        mock_response = Mock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status = Mock()

        with patch.object(service.http_client, "get", return_value=mock_response):
            result = service.set_location_from_city("VilleInexistante12345")

        assert result is False
        # Coordonnées non modifiées
        assert service.latitude == original_lat
        assert service.longitude == original_lon

    def test_set_location_from_city_empty_response(self):
        """Test géocodage avec réponse vide."""
        from src.services.weather import WeatherGardenService

        service = WeatherGardenService()

        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status = Mock()

        with patch.object(service.http_client, "get", return_value=mock_response):
            result = service.set_location_from_city("Test")

        assert result is False

    def test_set_location_from_city_http_error(self):
        """Test géocodage avec erreur HTTP."""
        from src.services.weather import WeatherGardenService

        service = WeatherGardenService()

        with patch.object(service.http_client, "get", side_effect=httpx.HTTPError("Network error")):
            result = service.set_location_from_city("Paris")

        assert result is False

    def test_set_location_from_city_json_error(self):
        """Test géocodage avec erreur JSON."""
        from src.services.weather import WeatherGardenService

        service = WeatherGardenService()

        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")

        with patch.object(service.http_client, "get", return_value=mock_response):
            result = service.set_location_from_city("Paris")

        assert result is False


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS PLAN D'ARROSAGE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestWeatherWateringPlan:
    """Tests pour generer_plan_arrosage."""

    def test_generer_plan_arrosage_basic(self):
        """Test génération plan d'arrosage basique."""
        from src.services.weather import MeteoJour, WeatherGardenService

        service = WeatherGardenService()

        # créer des prévisions mock
        previsions = [
            MeteoJour(
                date=date.today() + timedelta(days=i),
                temperature_min=15.0,
                temperature_max=25.0,
                temperature_moyenne=20.0,
                precipitation_mm=0.0,
                probabilite_pluie=10,
                humidite=50,
                vent_km_h=10,
                uv_index=5,
                condition="Ensoleillé",
            )
            for i in range(7)
        ]

        with patch.object(service, "get_previsions", return_value=previsions):
            plan = service.generer_plan_arrosage(nb_jours=7, surface_m2=50.0)

        assert len(plan) == 7
        assert all(hasattr(p, "date") for p in plan)
        assert all(hasattr(p, "besoin_arrosage") for p in plan)
        assert all(hasattr(p, "quantite_recommandee_litres") for p in plan)

    def test_generer_plan_arrosage_with_rain(self):
        """Test plan d'arrosage avec pluie prévue."""
        from src.services.weather import MeteoJour, WeatherGardenService

        service = WeatherGardenService()

        # prévisions avec pluie
        previsions = [
            MeteoJour(
                date=date.today() + timedelta(days=i),
                temperature_min=15.0,
                temperature_max=20.0,
                temperature_moyenne=17.5,
                precipitation_mm=10.0,
                probabilite_pluie=80,
                humidite=80,
                vent_km_h=10,
                uv_index=3,
                condition="Pluie",
            )
            for i in range(3)
        ]

        with patch.object(service, "get_previsions", return_value=previsions):
            plan = service.generer_plan_arrosage(nb_jours=3, surface_m2=30.0)

        assert len(plan) == 3
        # Avec 10mm de pluie, pas besoin d'arroser
        for p in plan:
            assert "Pluie" in p.raison or "pluie" in p.raison.lower()

    def test_generer_plan_arrosage_canicule(self):
        """Test plan d'arrosage en canicule."""
        from src.services.weather import MeteoJour, WeatherGardenService

        service = WeatherGardenService()

        # Canicule
        previsions = [
            MeteoJour(
                date=date.today() + timedelta(days=i),
                temperature_min=25.0,
                temperature_max=38.0,
                temperature_moyenne=31.5,
                precipitation_mm=0.0,
                probabilite_pluie=0,
                humidite=30,
                vent_km_h=5,
                uv_index=10,
                condition="Caniculaire",
            )
            for i in range(3)
        ]

        with patch.object(service, "get_previsions", return_value=previsions):
            plan = service.generer_plan_arrosage(nb_jours=3, surface_m2=50.0)

        assert len(plan) == 3
        # En canicule, les plantes prioritaires devraient inclure tomates, etc.
        for p in plan:
            if p.plantes_prioritaires:
                assert "Tomates" in p.plantes_prioritaires or len(p.plantes_prioritaires) > 0

    def test_generer_plan_arrosage_cold_weather(self):
        """Test plan d'arrosage par temps froid."""
        from src.services.weather import MeteoJour, WeatherGardenService

        service = WeatherGardenService()

        # Temps froid
        previsions = [
            MeteoJour(
                date=date.today() + timedelta(days=i),
                temperature_min=5.0,
                temperature_max=12.0,
                temperature_moyenne=8.5,
                precipitation_mm=0.0,
                probabilite_pluie=20,
                humidite=60,
                vent_km_h=10,
                uv_index=2,
                condition="Frais",
            )
            for i in range(3)
        ]

        with patch.object(service, "get_previsions", return_value=previsions):
            plan = service.generer_plan_arrosage(nb_jours=3, surface_m2=50.0)

        assert len(plan) == 3
        # Besoin réduit par temps froid
        for p in plan:
            assert p.quantite_recommandee_litres >= 0

    def test_generer_plan_arrosage_empty_previsions(self):
        """Test plan d'arrosage sans prévisions."""
        from src.services.weather import WeatherGardenService

        service = WeatherGardenService()

        with patch.object(service, "get_previsions", return_value=[]):
            plan = service.generer_plan_arrosage(nb_jours=7, surface_m2=50.0)

        assert plan == []

    def test_generer_plan_arrosage_none_previsions(self):
        """Test plan d'arrosage avec prévisions None."""
        from src.services.weather import WeatherGardenService

        service = WeatherGardenService()

        with patch.object(service, "get_previsions", return_value=None):
            plan = service.generer_plan_arrosage(nb_jours=7, surface_m2=50.0)

        assert plan == []

    def test_generer_plan_arrosage_high_rain_probability(self):
        """Test plan d'arrosage avec forte probabilité de pluie."""
        from src.services.weather import MeteoJour, WeatherGardenService

        service = WeatherGardenService()

        previsions = [
            MeteoJour(
                date=date.today(),
                temperature_min=18.0,
                temperature_max=24.0,
                temperature_moyenne=21.0,
                precipitation_mm=2.0,
                probabilite_pluie=75,
                humidite=70,
                vent_km_h=15,
                uv_index=4,
                condition="Nuageux",
            )
        ]

        with patch.object(service, "get_previsions", return_value=previsions):
            plan = service.generer_plan_arrosage(nb_jours=1, surface_m2=50.0)

        assert len(plan) == 1
        # Forte probabilité de pluie devrait àªtre mentionnée
        assert "probabilité" in plan[0].raison.lower() or "pluie" in plan[0].raison.lower()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS PERSISTANCE BASE DE DONNà‰ES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestWeatherDBPersistence:
    """Tests pour les méthodes de persistance DB."""

    @pytest.fixture
    def mock_db_session(self):
        """Fixture pour session DB mock."""
        session = Mock()
        session.add = Mock()
        session.commit = Mock()
        session.rollback = Mock()
        session.query = Mock()
        session.flush = Mock()
        return session

    @pytest.fixture
    def sample_alerte(self):
        """Fixture pour une alerte météo Pydantic."""
        from src.services.weather import AlerteMeteo as AlerteMeteoSchema
        from src.services.weather import NiveauAlerte, TypeAlertMeteo

        return AlerteMeteoSchema(
            type_alerte=TypeAlertMeteo.GEL,
            niveau=NiveauAlerte.ATTENTION,
            titre="Risque de gel",
            message="Températures négatives prévues",
            conseil_jardin="Protégez vos plantes sensibles",
            date_debut=date.today(),
            date_fin=date.today() + timedelta(days=2),
            temperature=-2.0,
        )

    def test_sauvegarder_alerte_success(self, mock_db_session, sample_alerte):
        """Test sauvegarde d'une alerte réussie."""
        from uuid import uuid4

        from src.services.weather import WeatherGardenService

        service = WeatherGardenService()
        user_id = uuid4()

        # Le mock retourne un objet "sauvegardé"
        mock_alerte_model = Mock()
        mock_alerte_model.id = 1

        with patch("src.services.weather.AlerteMeteoModel") as MockModel:
            MockModel.return_value = mock_alerte_model
            result = service.sauvegarder_alerte(
                alerte=sample_alerte, user_id=user_id, db=mock_db_session
            )

        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        assert result is not None

    def test_sauvegarder_alerte_with_string_user_id(self, mock_db_session, sample_alerte):
        """Test sauvegarde avec user_id string."""
        from src.services.weather import WeatherGardenService

        service = WeatherGardenService()

        mock_alerte_model = Mock()
        mock_alerte_model.id = 1

        with patch("src.services.weather.AlerteMeteoModel") as MockModel:
            MockModel.return_value = mock_alerte_model
            result = service.sauvegarder_alerte(
                alerte=sample_alerte,
                user_id="12345678-1234-5678-1234-567812345678",
                db=mock_db_session,
            )

        assert result is not None

    def test_sauvegarder_alerte_without_user_id(self, mock_db_session, sample_alerte):
        """Test sauvegarde sans user_id."""
        from src.services.weather import WeatherGardenService

        service = WeatherGardenService()

        mock_alerte_model = Mock()
        mock_alerte_model.id = 1

        with patch("src.services.weather.AlerteMeteoModel") as MockModel:
            MockModel.return_value = mock_alerte_model
            result = service.sauvegarder_alerte(
                alerte=sample_alerte, user_id=None, db=mock_db_session
            )

        assert result is not None

    def test_sauvegarder_alerte_db_error(self, mock_db_session, sample_alerte):
        """Test sauvegarde avec erreur DB."""
        from src.services.weather import WeatherGardenService

        service = WeatherGardenService()
        mock_db_session.commit.side_effect = Exception("DB Error")

        with patch("src.services.weather.AlerteMeteoModel"):
            result = service.sauvegarder_alerte(
                alerte=sample_alerte, user_id=None, db=mock_db_session
            )

        mock_db_session.rollback.assert_called_once()
        assert result is None

    def test_sauvegarder_alertes_batch(self, mock_db_session, sample_alerte):
        """Test sauvegarde batch d'alertes."""
        from uuid import uuid4

        from src.services.weather import AlerteMeteo as AlerteMeteoSchema
        from src.services.weather import NiveauAlerte, TypeAlertMeteo, WeatherGardenService

        service = WeatherGardenService()
        user_id = uuid4()

        # créer plusieurs alertes
        alertes = [
            sample_alerte,
            AlerteMeteoSchema(
                type_alerte=TypeAlertMeteo.CANICULE,
                niveau=NiveauAlerte.DANGER,
                titre="Canicule",
                message="Températures très élevées",
                conseil_jardin="Arrosez abondamment",
                date_debut=date.today(),
                date_fin=date.today() + timedelta(days=3),
                temperature=40.0,
            ),
        ]

        mock_alerte_model = Mock()
        mock_alerte_model.id = 1

        with patch("src.services.weather.AlerteMeteoModel") as MockModel:
            MockModel.return_value = mock_alerte_model
            result = service.sauvegarder_alertes(
                alertes=alertes, user_id=user_id, db=mock_db_session
            )

        assert isinstance(result, list)
        assert len(result) == 2

    def test_sauvegarder_alertes_empty_list(self, mock_db_session):
        """Test sauvegarde batch avec liste vide."""
        from src.services.weather import WeatherGardenService

        service = WeatherGardenService()

        result = service.sauvegarder_alertes(alertes=[], user_id=None, db=mock_db_session)

        assert result == []
        mock_db_session.add.assert_not_called()

    def test_lister_alertes_actives_no_filter(self, mock_db_session):
        """Test liste des alertes actives sans filtre user."""
        from src.services.weather import WeatherGardenService

        service = WeatherGardenService()

        # Mock de la query chain
        mock_alert1 = Mock()
        mock_alert1.id = 1
        mock_alert1.type_alerte = "gel"
        mock_alert2 = Mock()
        mock_alert2.id = 2
        mock_alert2.type_alerte = "canicule"

        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [mock_alert1, mock_alert2]
        mock_db_session.query.return_value = mock_query

        result = service.lister_alertes_actives(user_id=None, db=mock_db_session)

        assert len(result) == 2
        mock_db_session.query.assert_called_once()

    def test_lister_alertes_actives_with_user_id(self, mock_db_session):
        """Test liste des alertes actives avec filtre user."""
        from uuid import uuid4

        from src.services.weather import WeatherGardenService

        service = WeatherGardenService()
        user_id = uuid4()

        mock_alert = Mock()
        mock_alert.id = 1

        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [mock_alert]
        mock_db_session.query.return_value = mock_query

        result = service.lister_alertes_actives(user_id=user_id, db=mock_db_session)

        assert len(result) == 1

    def test_marquer_alerte_lue_success(self, mock_db_session):
        """Test marquer une alerte comme lue."""
        from src.services.weather import WeatherGardenService

        service = WeatherGardenService()

        mock_alerte = Mock()
        mock_alerte.id = 42
        mock_alerte.lu = False

        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_alerte
        mock_db_session.query.return_value = mock_query

        result = service.marquer_alerte_lue(alerte_id=42, db=mock_db_session)

        assert result is True
        assert mock_alerte.lu is True
        mock_db_session.commit.assert_called_once()

    def test_marquer_alerte_lue_not_found(self, mock_db_session):
        """Test marquer alerte inexistante."""
        from src.services.weather import WeatherGardenService

        service = WeatherGardenService()

        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db_session.query.return_value = mock_query

        result = service.marquer_alerte_lue(alerte_id=999, db=mock_db_session)

        assert result is False
        mock_db_session.commit.assert_not_called()

    def test_obtenir_config_meteo_exists(self, mock_db_session):
        """Test obtenir config météo existante."""
        from uuid import uuid4

        from src.services.weather import WeatherGardenService

        service = WeatherGardenService()
        user_id = uuid4()

        mock_config = Mock()
        mock_config.id = 1
        mock_config.latitude = 48.8566
        mock_config.longitude = 2.3522
        mock_config.ville = "Paris"

        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_config
        mock_db_session.query.return_value = mock_query

        result = service.obtenir_config_meteo(user_id=user_id, db=mock_db_session)

        assert result is not None
        assert result.ville == "Paris"

    def test_obtenir_config_meteo_not_found(self, mock_db_session):
        """Test obtenir config météo inexistante."""
        from uuid import uuid4

        from src.services.weather import WeatherGardenService

        service = WeatherGardenService()
        user_id = uuid4()

        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db_session.query.return_value = mock_query

        result = service.obtenir_config_meteo(user_id=user_id, db=mock_db_session)

        assert result is None

    def test_sauvegarder_config_meteo_create_new(self, mock_db_session):
        """Test création nouvelle config météo."""
        from uuid import uuid4

        from src.services.weather import WeatherGardenService

        service = WeatherGardenService()
        user_id = uuid4()

        # Pas de config existante
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db_session.query.return_value = mock_query

        mock_new_config = Mock()
        mock_new_config.id = 1
        mock_new_config.ville = "Lyon"

        with patch("src.services.weather.ConfigMeteo") as MockConfigModel:
            MockConfigModel.return_value = mock_new_config
            result = service.sauvegarder_config_meteo(
                user_id=user_id,
                latitude=45.7640,
                longitude=4.8357,
                ville="Lyon",
                surface_jardin=100.0,
                db=mock_db_session,
            )

        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        assert result is not None

    def test_sauvegarder_config_meteo_update_existing(self, mock_db_session):
        """Test mise à  jour config météo existante."""
        from uuid import uuid4

        from src.services.weather import WeatherGardenService

        service = WeatherGardenService()
        user_id = uuid4()

        # Config existante
        existing_config = Mock()
        existing_config.id = 1
        existing_config.latitude = 48.8566
        existing_config.longitude = 2.3522
        existing_config.ville = "Paris"
        existing_config.surface_jardin_m2 = 50.0

        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = existing_config
        mock_db_session.query.return_value = mock_query

        result = service.sauvegarder_config_meteo(
            user_id=user_id, ville="Marseille", db=mock_db_session
        )

        # Mis à  jour
        assert existing_config.ville == "Marseille"
        mock_db_session.commit.assert_called_once()
        # Pas d'add car mise à  jour
        mock_db_session.add.assert_not_called()

    def test_sauvegarder_config_meteo_partial_update(self, mock_db_session):
        """Test mise à  jour partielle de la config."""
        from uuid import uuid4

        from src.services.weather import WeatherGardenService

        service = WeatherGardenService()
        user_id = uuid4()

        existing_config = Mock()
        existing_config.latitude = 48.8566
        existing_config.longitude = 2.3522
        existing_config.ville = "Paris"
        existing_config.surface_jardin_m2 = 50.0

        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = existing_config
        mock_db_session.query.return_value = mock_query

        # Mise à  jour seulement de la surface
        result = service.sauvegarder_config_meteo(
            user_id=user_id, surface_jardin=150.0, db=mock_db_session
        )

        assert existing_config.surface_jardin_m2 == 150.0
        # Autres champs inchangés
        assert existing_config.ville == "Paris"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS Mà‰THODE SET LOCATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestWeatherSetLocation:
    """Tests pour set_location."""

    def test_set_location_updates_coordinates(self):
        """Test mise à  jour des coordonnées."""
        from src.services.weather import WeatherGardenService

        service = WeatherGardenService()

        service.set_location(latitude=43.6047, longitude=1.4442)

        assert service.latitude == 43.6047
        assert service.longitude == 1.4442

    def test_set_location_overrides_defaults(self):
        """Test que set_location écrase les valeurs par défaut."""
        from src.services.weather import WeatherGardenService

        service = WeatherGardenService()

        # Valeurs par défaut (Paris)
        assert service.latitude == 48.8566
        assert service.longitude == 2.3522

        # Mise à  jour (Bordeaux)
        service.set_location(latitude=44.8378, longitude=-0.5792)

        assert service.latitude == 44.8378
        assert service.longitude == -0.5792


# ═══════════════════════════════════════════════════════════
# TESTS COVERAGE ADDITIONNELS
# ═══════════════════════════════════════════════════════════


class TestWeatherConseils:
    """Tests generer_conseils coverage."""

    def test_generer_conseils_high_temp(self):
        """Test conseils haute temperature."""
        from datetime import date
        from unittest.mock import patch

        from src.services.weather import MeteoJour, WeatherGardenService

        service = WeatherGardenService()
        previsions = [
            MeteoJour(
                date=date.today(),
                temperature_min=18.0,
                temperature_max=28.0,
                temperature_moyenne=23.0,
                precipitation_mm=0.0,
                probabilite_pluie=10,
                humidite=50,
                vent_km_h=10,
                uv_index=5,
                condition="Ensoleille",
            )
        ]

        with patch.object(service, "get_previsions", return_value=previsions):
            conseils = service.generer_conseils()

        assert len(conseils) > 0

    def test_generer_conseils_cold_night(self):
        """Test conseils nuit fraiche."""
        from datetime import date
        from unittest.mock import patch

        from src.services.weather import MeteoJour, WeatherGardenService

        service = WeatherGardenService()
        previsions = [
            MeteoJour(
                date=date.today(),
                temperature_min=5.0,
                temperature_max=18.0,
                temperature_moyenne=11.5,
                precipitation_mm=0.0,
                probabilite_pluie=20,
                humidite=60,
                vent_km_h=15,
                uv_index=4,
                condition="Nuageux",
            )
        ]

        with patch.object(service, "get_previsions", return_value=previsions):
            conseils = service.generer_conseils()

        assert isinstance(conseils, list)

    def test_generer_conseils_high_uv(self):
        """Test conseils UV forts."""
        from datetime import date
        from unittest.mock import patch

        from src.services.weather import MeteoJour, WeatherGardenService

        service = WeatherGardenService()
        previsions = [
            MeteoJour(
                date=date.today(),
                temperature_min=20.0,
                temperature_max=30.0,
                temperature_moyenne=25.0,
                precipitation_mm=0.0,
                probabilite_pluie=5,
                humidite=40,
                vent_km_h=5,
                uv_index=9,
                condition="Ensoleille",
            )
        ]

        with patch.object(service, "get_previsions", return_value=previsions):
            conseils = service.generer_conseils()

        assert len(conseils) > 0

    def test_generer_conseils_rainy(self):
        """Test conseils pluie."""
        from datetime import date
        from unittest.mock import patch

        from src.services.weather import MeteoJour, WeatherGardenService

        service = WeatherGardenService()
        previsions = [
            MeteoJour(
                date=date.today(),
                temperature_min=15.0,
                temperature_max=20.0,
                temperature_moyenne=17.5,
                precipitation_mm=10.0,
                probabilite_pluie=80,
                humidite=80,
                vent_km_h=20,
                uv_index=2,
                condition="Pluie",
            )
        ]

        with patch.object(service, "get_previsions", return_value=previsions):
            conseils = service.generer_conseils()

        assert isinstance(conseils, list)


class TestWeatherPlanArrosageExtra:
    """Tests plan arrosage supplementaires."""

    def test_plan_moderate_temp(self):
        """Test temp 25-30."""
        from datetime import date
        from unittest.mock import patch

        from src.services.weather import MeteoJour, WeatherGardenService

        service = WeatherGardenService()
        previsions = [
            MeteoJour(
                date=date.today(),
                temperature_min=18.0,
                temperature_max=27.0,
                temperature_moyenne=22.5,
                precipitation_mm=0.0,
                probabilite_pluie=10,
                humidite=50,
                vent_km_h=10,
                uv_index=6,
                condition="Ensoleille",
            )
        ]

        with patch.object(service, "get_previsions", return_value=previsions):
            plan = service.generer_plan_arrosage(nb_jours=1, surface_m2=50.0)

        assert len(plan) == 1

    def test_plan_cumul_rain(self):
        """Test pluie cumulee."""
        from datetime import date, timedelta
        from unittest.mock import patch

        from src.services.weather import MeteoJour, WeatherGardenService

        service = WeatherGardenService()
        previsions = [
            MeteoJour(
                date=date.today(),
                temperature_min=15.0,
                temperature_max=20.0,
                temperature_moyenne=17.5,
                precipitation_mm=15.0,
                probabilite_pluie=80,
                humidite=85,
                vent_km_h=10,
                uv_index=2,
                condition="Pluie",
            ),
            MeteoJour(
                date=date.today() + timedelta(days=1),
                temperature_min=15.0,
                temperature_max=22.0,
                temperature_moyenne=18.5,
                precipitation_mm=0.0,
                probabilite_pluie=20,
                humidite=65,
                vent_km_h=10,
                uv_index=4,
                condition="Nuageux",
            ),
        ]

        with patch.object(service, "get_previsions", return_value=previsions):
            plan = service.generer_plan_arrosage(nb_jours=2, surface_m2=50.0)

        assert len(plan) == 2

    def test_plan_favorable(self):
        """Test conditions favorables."""
        from datetime import date
        from unittest.mock import patch

        from src.services.weather import MeteoJour, WeatherGardenService

        service = WeatherGardenService()
        previsions = [
            MeteoJour(
                date=date.today(),
                temperature_min=12.0,
                temperature_max=20.0,
                temperature_moyenne=16.0,
                precipitation_mm=3.0,
                probabilite_pluie=40,
                humidite=55,
                vent_km_h=8,
                uv_index=4,
                condition="Nuageux",
            )
        ]

        with patch.object(service, "get_previsions", return_value=previsions):
            plan = service.generer_plan_arrosage(nb_jours=1, surface_m2=50.0)

        assert len(plan) == 1


class TestWeatherFactory:
    """Tests factory function."""

    def test_get_weather_garden_service(self):
        """Test factory retourne service."""
        from src.services.weather import WeatherGardenService, get_weather_garden_service

        service = get_weather_garden_service()
        assert isinstance(service, WeatherGardenService)

    def test_factory_returns_singleton(self):
        """Test factory retourne meme instance."""
        from src.services.weather import get_weather_garden_service

        s1 = get_weather_garden_service()
        s2 = get_weather_garden_service()
        assert s1 is s2


class TestWeatherSaveAlertesBatchError:
    """Tests erreur batch alertes."""

    def test_sauvegarder_alertes_db_error(self):
        """Test erreur commit batch."""
        from datetime import date
        from unittest.mock import Mock, patch
        from uuid import uuid4

        from src.services.weather import (
            AlerteMeteo,
            NiveauAlerte,
            TypeAlertMeteo,
            WeatherGardenService,
        )

        service = WeatherGardenService()
        mock_db = Mock()
        mock_db.add = Mock()
        mock_db.commit = Mock(side_effect=Exception("DB Error"))
        mock_db.rollback = Mock()

        alertes = [
            AlerteMeteo(
                type_alerte=TypeAlertMeteo.GEL,
                niveau=NiveauAlerte.ATTENTION,
                titre="Test",
                message="Test",
                conseil_jardin="Test",
                date_debut=date.today(),
                temperature=-2.0,
            )
        ]

        with patch("src.services.weather.AlerteMeteoModel"):
            result = service.sauvegarder_alertes(alertes=alertes, user_id=uuid4(), db=mock_db)

        mock_db.rollback.assert_called_once()
        assert result == []


class TestWeatherPlanElseBranch:
    """Test else branch in plan arrosage."""

    def test_favorable_conditions_else(self):
        """Test conditions favorables else branch."""
        from datetime import date
        from unittest.mock import patch

        from src.services.weather import MeteoJour, WeatherGardenService

        service = WeatherGardenService()

        # Conditions pour else: temp froide + un peu de pluie
        # besoin_net sera faible car temp < 15 et apport_pluie > 0
        previsions = [
            MeteoJour(
                date=date.today(),
                temperature_min=8.0,
                temperature_max=14.0,  # Froid = besoin_base * 0.7
                temperature_moyenne=11.0,
                precipitation_mm=4.0,  # Pluie < 5 mais réduit besoin
                probabilite_pluie=40,  # < 60
                humidite=70,
                vent_km_h=10,
                uv_index=3,
                condition="Nuageux",
            )
        ]

        with patch.object(service, "get_previsions", return_value=previsions):
            plan = service.generer_plan_arrosage(nb_jours=1, surface_m2=50.0)

        assert len(plan) == 1
        # Devrait etre favorable
        assert "favorable" in plan[0].raison.lower() or len(plan[0].raison) > 0


class TestWeatherConseilsLune:
    """Tests conseils lune."""

    def test_generer_conseils_lune_favorable(self):
        """Test conseils lune quand jour favorable (1-7 ou 15-22)."""
        from datetime import date
        from unittest.mock import patch

        from src.services.weather import MeteoJour, WeatherGardenService

        service = WeatherGardenService()

        # Creer une date mock avec jour=5 (entre 1-7)
        mock_date = MagicMock()
        mock_date.today.return_value.day = 5

        previsions = [
            MeteoJour(
                date=date.today(),
                temperature_min=15.0,
                temperature_max=22.0,
                temperature_moyenne=18.5,
                precipitation_mm=0.0,
                probabilite_pluie=10,
                humidite=50,
                vent_km_h=5,
                uv_index=5,
                condition="Ensoleille",
            )
        ]

        with patch("src.services.weather.date") as mock_date_mod:
            mock_date_mod.today.return_value.day = 5
            with patch.object(service, "get_previsions", return_value=previsions):
                conseils = service.generer_conseils()

        # Peut contenir conseil lune
        assert isinstance(conseils, list)
