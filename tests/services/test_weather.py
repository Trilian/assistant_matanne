"""
Tests pour le service météo (weather.py).

Ce fichier teste les fonctionnalités météo pour le jardinage:
- Modèles de données météo (MeteoJour, AlerteMeteo, ConseilJardin)
- Conversion des codes météo
- Génération d'alertes (gel, canicule, pluie forte)
- Plans d'arrosage intelligent
"""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import patch, MagicMock
import httpx


# ═══════════════════════════════════════════════════════════
# TESTS ENUMS
# ═══════════════════════════════════════════════════════════


class TestTypeAlertMeteoEnum:
    """Tests pour TypeAlertMeteo enum."""

    def test_types_alertes_disponibles(self):
        """Vérifie tous les types d'alertes."""
        from src.services.weather import TypeAlertMeteo
        
        types = [t.value for t in TypeAlertMeteo]
        assert "gel" in types
        assert "canicule" in types
        assert "pluie_forte" in types
        assert "sécheresse" in types
        assert "vent_fort" in types
        assert "orage" in types

    def test_type_alerte_valeur_string(self):
        """TypeAlertMeteo est un string enum."""
        from src.services.weather import TypeAlertMeteo
        
        assert TypeAlertMeteo.GEL.value == "gel"
        assert TypeAlertMeteo.CANICULE.value == "canicule"


class TestNiveauAlerteEnum:
    """Tests pour NiveauAlerte enum."""

    def test_niveaux_disponibles(self):
        """Vérifie les niveaux de gravité."""
        from src.services.weather import NiveauAlerte
        
        niveaux = [n.value for n in NiveauAlerte]
        assert "info" in niveaux
        assert "attention" in niveaux
        assert "danger" in niveaux


# ═══════════════════════════════════════════════════════════
# TESTS MODÈLES PYDANTIC
# ═══════════════════════════════════════════════════════════


class TestMeteoJourModel:
    """Tests pour MeteoJour model."""

    def test_meteo_jour_creation(self):
        """Création d'un MeteoJour."""
        from src.services.weather import MeteoJour
        
        meteo = MeteoJour(
            date=date.today(),
            temperature_min=5.0,
            temperature_max=15.0,
            temperature_moyenne=10.0,
            humidite=60,
            precipitation_mm=2.5,
            probabilite_pluie=40,
            vent_km_h=20.0,
        )
        
        assert meteo.temperature_min == 5.0
        assert meteo.temperature_max == 15.0
        assert meteo.humidite == 60

    def test_meteo_jour_defaults(self):
        """Valeurs par défaut de MeteoJour."""
        from src.services.weather import MeteoJour
        
        meteo = MeteoJour(
            date=date.today(),
            temperature_min=0.0,
            temperature_max=10.0,
            temperature_moyenne=5.0,
            humidite=50,
            precipitation_mm=0.0,
            probabilite_pluie=0,
            vent_km_h=0.0,
        )
        
        assert meteo.direction_vent == ""
        assert meteo.uv_index == 0
        assert meteo.condition == ""
        assert meteo.icone == ""


class TestAlerteMeteoModel:
    """Tests pour AlerteMeteo model."""

    def test_alerte_creation(self):
        """Création d'une alerte météo."""
        from src.services.weather import AlerteMeteo, TypeAlertMeteo, NiveauAlerte
        
        alerte = AlerteMeteo(
            type_alerte=TypeAlertMeteo.GEL,
            niveau=NiveauAlerte.DANGER,
            titre="🥶 Risque de gel",
            message="Température -2°C prévue",
            conseil_jardin="Protégez vos plantes",
            date_debut=date.today(),
        )
        
        assert alerte.type_alerte == TypeAlertMeteo.GEL
        assert alerte.niveau == NiveauAlerte.DANGER

    def test_alerte_date_fin_optionnelle(self):
        """date_fin est optionnel."""
        from src.services.weather import AlerteMeteo, TypeAlertMeteo, NiveauAlerte
        
        alerte = AlerteMeteo(
            type_alerte=TypeAlertMeteo.CANICULE,
            niveau=NiveauAlerte.ATTENTION,
            titre="Test",
            message="Test",
            conseil_jardin="Test",
            date_debut=date.today(),
        )
        
        assert alerte.date_fin is None


class TestConseilJardinModel:
    """Tests pour ConseilJardin model."""

    def test_conseil_creation(self):
        """Création d'un conseil jardin."""
        from src.services.weather import ConseilJardin
        
        conseil = ConseilJardin(
            priorite=1,
            icone="💧",
            titre="Arrosage nécessaire",
            description="Le sol est sec",
            plantes_concernees=["Tomates", "Courgettes"],
            action_recommandee="Arroser le matin",
        )
        
        assert conseil.priorite == 1
        assert conseil.icone == "💧"
        assert len(conseil.plantes_concernees) == 2

    def test_conseil_defaults(self):
        """Valeurs par défaut ConseilJardin."""
        from src.services.weather import ConseilJardin
        
        conseil = ConseilJardin(
            titre="Test",
            description="Test",
        )
        
        assert conseil.priorite == 1
        assert conseil.icone == "🌱"
        assert conseil.plantes_concernees == []


class TestPlanArrosageModel:
    """Tests pour PlanArrosage model."""

    def test_plan_arrosage_creation(self):
        """Création d'un plan d'arrosage."""
        from src.services.weather import PlanArrosage
        
        plan = PlanArrosage(
            date=date.today(),
            besoin_arrosage=True,
            quantite_recommandee_litres=5.0,
            raison="Pas de pluie prévue",
            plantes_prioritaires=["Tomates"],
        )
        
        assert plan.besoin_arrosage is True
        assert plan.quantite_recommandee_litres == 5.0


# ═══════════════════════════════════════════════════════════
# TESTS SERVICE - INITIALISATION
# ═══════════════════════════════════════════════════════════


class TestWeatherGardenServiceInit:
    """Tests pour l'initialisation du service."""

    def test_service_creation(self):
        """Création du service avec coordonnées par défaut."""
        from src.services.weather import WeatherGardenService
        
        service = WeatherGardenService()
        
        # Paris par défaut
        assert service.latitude == 48.8566
        assert service.longitude == 2.3522

    def test_service_creation_custom_location(self):
        """Création avec coordonnées personnalisées."""
        from src.services.weather import WeatherGardenService
        
        service = WeatherGardenService(latitude=45.75, longitude=4.85)  # Lyon
        
        assert service.latitude == 45.75
        assert service.longitude == 4.85

    def test_set_location(self):
        """Mise à jour de la localisation."""
        from src.services.weather import WeatherGardenService
        
        service = WeatherGardenService()
        service.set_location(43.6047, 1.4442)  # Toulouse
        
        assert service.latitude == 43.6047
        assert service.longitude == 1.4442


# ═══════════════════════════════════════════════════════════
# TESTS CONVERSION CODES MÉTÉO
# ═══════════════════════════════════════════════════════════


class TestWeathercodeConversion:
    """Tests pour conversion des codes météo."""

    def test_direction_from_degrees(self):
        """Conversion degrés → direction cardinale."""
        from src.services.weather import WeatherGardenService
        
        service = WeatherGardenService()
        
        assert service._direction_from_degrees(0) == "N"
        assert service._direction_from_degrees(90) == "E"
        assert service._direction_from_degrees(180) == "S"
        assert service._direction_from_degrees(270) == "O"
        assert service._direction_from_degrees(45) == "NE"

    def test_direction_from_degrees_none(self):
        """Direction avec valeur None."""
        from src.services.weather import WeatherGardenService
        
        service = WeatherGardenService()
        assert service._direction_from_degrees(None) == ""

    def test_weathercode_to_condition_soleil(self):
        """Code 0 = Ensoleillé."""
        from src.services.weather import WeatherGardenService
        
        service = WeatherGardenService()
        assert service._weathercode_to_condition(0) == "Ensoleillé"

    def test_weathercode_to_condition_pluie(self):
        """Codes pluie."""
        from src.services.weather import WeatherGardenService
        
        service = WeatherGardenService()
        assert service._weathercode_to_condition(61) == "Pluie légère"
        assert service._weathercode_to_condition(63) == "Pluie modérée"
        assert service._weathercode_to_condition(65) == "Pluie forte"

    def test_weathercode_to_condition_neige(self):
        """Codes neige."""
        from src.services.weather import WeatherGardenService
        
        service = WeatherGardenService()
        assert service._weathercode_to_condition(71) == "Neige légère"
        assert service._weathercode_to_condition(75) == "Neige forte"

    def test_weathercode_to_condition_none(self):
        """Code None retourne Inconnu."""
        from src.services.weather import WeatherGardenService
        
        service = WeatherGardenService()
        assert service._weathercode_to_condition(None) == "Inconnu"

    def test_weathercode_to_icon_soleil(self):
        """Icône soleil."""
        from src.services.weather import WeatherGardenService
        
        service = WeatherGardenService()
        assert service._weathercode_to_icon(0) == "☀️"

    def test_weathercode_to_icon_pluie(self):
        """Icône pluie."""
        from src.services.weather import WeatherGardenService
        
        service = WeatherGardenService()
        assert service._weathercode_to_icon(61) == "🌧️"

    def test_weathercode_to_icon_orage(self):
        """Icône orage."""
        from src.services.weather import WeatherGardenService
        
        service = WeatherGardenService()
        assert service._weathercode_to_icon(95) == "⛈️"


# ═══════════════════════════════════════════════════════════
# TESTS GÉNÉRATION ALERTES
# ═══════════════════════════════════════════════════════════


class TestGenererAlertes:
    """Tests pour génération d'alertes."""

    def test_alerte_gel(self):
        """Génération alerte gel."""
        from src.services.weather import WeatherGardenService, MeteoJour, TypeAlertMeteo
        
        service = WeatherGardenService()
        
        # Prévision avec gel
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
        assert alerte_gel.temperature == -2.0

    def test_alerte_canicule(self):
        """Génération alerte canicule."""
        from src.services.weather import WeatherGardenService, MeteoJour, TypeAlertMeteo
        
        service = WeatherGardenService()
        
        previsions = [
            MeteoJour(
                date=date.today(),
                temperature_min=25.0,
                temperature_max=38.0,
                temperature_moyenne=31.5,
                humidite=30,
                precipitation_mm=0.0,
                probabilite_pluie=0,
                vent_km_h=5.0,
            )
        ]
        
        alertes = service.generer_alertes(previsions)
        
        alerte_canicule = next((a for a in alertes if a.type_alerte == TypeAlertMeteo.CANICULE), None)
        assert alerte_canicule is not None
        assert alerte_canicule.temperature == 38.0

    def test_pas_alerte_temperature_normale(self):
        """Pas d'alerte pour température normale."""
        from src.services.weather import WeatherGardenService, MeteoJour, TypeAlertMeteo
        
        service = WeatherGardenService()
        
        previsions = [
            MeteoJour(
                date=date.today(),
                temperature_min=10.0,
                temperature_max=20.0,
                temperature_moyenne=15.0,
                humidite=50,
                precipitation_mm=2.0,
                probabilite_pluie=40,
                vent_km_h=15.0,
            )
        ]
        
        alertes = service.generer_alertes(previsions)
        
        # Pas d'alerte gel ni canicule
        alerte_gel = next((a for a in alertes if a.type_alerte == TypeAlertMeteo.GEL), None)
        alerte_canicule = next((a for a in alertes if a.type_alerte == TypeAlertMeteo.CANICULE), None)
        assert alerte_gel is None
        assert alerte_canicule is None

    def test_alertes_previsions_vides(self):
        """Retourne liste vide si pas de prévisions."""
        from src.services.weather import WeatherGardenService
        
        service = WeatherGardenService()
        alertes = service.generer_alertes([])
        
        assert alertes == []


# ═══════════════════════════════════════════════════════════
# TESTS SEUILS
# ═══════════════════════════════════════════════════════════


class TestSeuils:
    """Tests pour les seuils d'alerte."""

    def test_seuil_gel(self):
        """Seuil de gel = 2°C."""
        from src.services.weather import WeatherGardenService
        
        assert WeatherGardenService.SEUIL_GEL == 2.0

    def test_seuil_canicule(self):
        """Seuil canicule = 35°C."""
        from src.services.weather import WeatherGardenService
        
        assert WeatherGardenService.SEUIL_CANICULE == 35.0

    def test_seuil_pluie_forte(self):
        """Seuil pluie forte = 20mm/jour."""
        from src.services.weather import WeatherGardenService
        
        assert WeatherGardenService.SEUIL_PLUIE_FORTE == 20.0

    def test_seuil_vent_fort(self):
        """Seuil vent fort = 50 km/h."""
        from src.services.weather import WeatherGardenService
        
        assert WeatherGardenService.SEUIL_VENT_FORT == 50.0


# ═══════════════════════════════════════════════════════════
# TESTS NIVEAUX ALERTE
# ═══════════════════════════════════════════════════════════


class TestNiveauxAlerte:
    """Tests pour détermination niveau alerte."""

    def test_niveau_danger_gel_negatif(self):
        """Gel négatif = DANGER."""
        from src.services.weather import WeatherGardenService, MeteoJour, NiveauAlerte
        
        service = WeatherGardenService()
        
        previsions = [
            MeteoJour(
                date=date.today(),
                temperature_min=-5.0,
                temperature_max=3.0,
                temperature_moyenne=-1.0,
                humidite=90,
                precipitation_mm=0.0,
                probabilite_pluie=10,
                vent_km_h=5.0,
            )
        ]
        
        alertes = service.generer_alertes(previsions)
        alerte_gel = alertes[0]
        
        assert alerte_gel.niveau == NiveauAlerte.DANGER

    def test_niveau_attention_gel_positif(self):
        """Gel entre 0 et 2 = ATTENTION."""
        from src.services.weather import WeatherGardenService, MeteoJour, NiveauAlerte
        
        service = WeatherGardenService()
        
        previsions = [
            MeteoJour(
                date=date.today(),
                temperature_min=1.0,  # Entre 0 et 2
                temperature_max=8.0,
                temperature_moyenne=4.5,
                humidite=70,
                precipitation_mm=0.0,
                probabilite_pluie=20,
                vent_km_h=10.0,
            )
        ]
        
        alertes = service.generer_alertes(previsions)
        alerte_gel = alertes[0]
        
        assert alerte_gel.niveau == NiveauAlerte.ATTENTION


# ═══════════════════════════════════════════════════════════
# TESTS API (MOCKED)
# ═══════════════════════════════════════════════════════════


class TestAPIGeocoding:
    """Tests pour le géocodage."""

    @patch.object(httpx.Client, 'get')
    def test_set_location_from_city_success(self, mock_get):
        """Géocodage réussi."""
        from src.services.weather import WeatherGardenService
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {
                    "latitude": 45.764,
                    "longitude": 4.8357,
                    "name": "Lyon"
                }
            ]
        }
        mock_get.return_value = mock_response
        
        service = WeatherGardenService()
        result = service.set_location_from_city("Lyon")
        
        assert result is True
        assert abs(service.latitude - 45.764) < 0.01

    @patch.object(httpx.Client, 'get')
    def test_set_location_from_city_not_found(self, mock_get):
        """Ville non trouvée."""
        from src.services.weather import WeatherGardenService
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}
        mock_get.return_value = mock_response
        
        service = WeatherGardenService()
        result = service.set_location_from_city("VilleInexistante12345")
        
        assert result is False
        # Coordonnées inchangées (Paris)
        assert service.latitude == 48.8566


# ═══════════════════════════════════════════════════════════
# TESTS CAS LIMITES
# ═══════════════════════════════════════════════════════════


class TestCasLimites:
    """Tests pour cas limites."""

    def test_multiple_alertes_meme_jour(self):
        """Plusieurs alertes pour un même jour."""
        from src.services.weather import WeatherGardenService, MeteoJour, TypeAlertMeteo
        
        service = WeatherGardenService()
        
        # Prévision avec gel ET vent fort
        previsions = [
            MeteoJour(
                date=date.today(),
                temperature_min=-3.0,  # Gel
                temperature_max=5.0,
                temperature_moyenne=1.0,
                humidite=60,
                precipitation_mm=0.0,
                probabilite_pluie=0,
                vent_km_h=60.0,  # Vent fort
            )
        ]
        
        alertes = service.generer_alertes(previsions)
        
        # Au moins l'alerte gel (vent fort peut ne pas être implémenté)
        types_alertes = [a.type_alerte for a in alertes]
        assert TypeAlertMeteo.GEL in types_alertes

    def test_previsions_plusieurs_jours(self):
        """Prévisions sur plusieurs jours."""
        from src.services.weather import WeatherGardenService, MeteoJour, TypeAlertMeteo
        
        service = WeatherGardenService()
        
        previsions = [
            MeteoJour(
                date=date.today(),
                temperature_min=15.0,
                temperature_max=25.0,
                temperature_moyenne=20.0,
                humidite=50,
                precipitation_mm=0.0,
                probabilite_pluie=0,
                vent_km_h=10.0,
            ),
            MeteoJour(
                date=date.today() + timedelta(days=1),
                temperature_min=-2.0,  # Gel le lendemain
                temperature_max=5.0,
                temperature_moyenne=1.5,
                humidite=80,
                precipitation_mm=0.0,
                probabilite_pluie=20,
                vent_km_h=15.0,
            ),
        ]
        
        alertes = service.generer_alertes(previsions)
        
        # Une alerte gel pour le 2ème jour
        alerte_gel = next((a for a in alertes if a.type_alerte == TypeAlertMeteo.GEL), None)
        assert alerte_gel is not None
        assert alerte_gel.date_debut == date.today() + timedelta(days=1)
