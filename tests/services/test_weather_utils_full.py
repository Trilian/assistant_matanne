"""
Tests complets pour weather_utils.py

Couvre toutes les fonctions pures du module:
- Conversion de données météo
- Calcul de températures
- Détection d'alertes
- Calcul d'arrosage
- Conseils jardinage
- Parsing API Open-Meteo
"""

import pytest
from datetime import date, datetime

from src.services.weather import (
    # Constantes
    SEUIL_GEL,
    SEUIL_GEL_SEVERE,
    SEUIL_CANICULE,
    SEUIL_CANICULE_SEVERE,
    SEUIL_PLUIE_FORTE,
    SEUIL_PLUIE_VIOLENTE,
    SEUIL_VENT_FORT,
    SEUIL_VENT_TEMPETE,
    SEUIL_UV_ELEVE,
    SEUIL_UV_EXTREME,
    DIRECTIONS_CARDINALES,
    WEATHERCODES,
    # Conversion
    direction_from_degrees,
    degrees_from_direction,
    weathercode_to_condition,
    weathercode_to_icon,
    get_arrosage_factor,
    # Températures
    calculate_average_temperature,
    calculate_temperature_amplitude,
    celsius_to_fahrenheit,
    fahrenheit_to_celsius,
    calculate_feels_like,
    # Alertes
    detect_gel_alert,
    detect_canicule_alert,
    detect_pluie_forte_alert,
    detect_vent_fort_alert,
    detect_uv_alert,
    detect_all_alerts,
    # Arrosage
    calculate_watering_need,
    detect_drought_risk,
    # Conseils jardinage
    get_season,
    get_gardening_advice_for_weather,
    format_weather_summary,
    # Parsing API
    parse_open_meteo_daily,
    validate_coordinates,
)
# Fonction interne importée depuis utils
from src.services.weather.utils import _safe_get_index


# ═══════════════════════════════════════════════════════════
# TESTS CONSTANTES
# ═══════════════════════════════════════════════════════════


class TestConstantes:
    """Tests pour vérifier que les constantes sont bien définies."""

    def test_seuils_gel(self):
        assert SEUIL_GEL == 2.0
        assert SEUIL_GEL_SEVERE == 0.0

    def test_seuils_canicule(self):
        assert SEUIL_CANICULE == 35.0
        assert SEUIL_CANICULE_SEVERE == 40.0

    def test_seuils_pluie(self):
        assert SEUIL_PLUIE_FORTE == 20.0
        assert SEUIL_PLUIE_VIOLENTE == 50.0

    def test_seuils_vent(self):
        assert SEUIL_VENT_FORT == 50.0
        assert SEUIL_VENT_TEMPETE == 80.0

    def test_seuils_uv(self):
        assert SEUIL_UV_ELEVE == 6
        assert SEUIL_UV_EXTREME == 10

    def test_directions_cardinales(self):
        assert len(DIRECTIONS_CARDINALES) == 8
        assert "N" in DIRECTIONS_CARDINALES
        assert "S" in DIRECTIONS_CARDINALES
        assert "E" in DIRECTIONS_CARDINALES
        assert "O" in DIRECTIONS_CARDINALES

    def test_weathercodes_complet(self):
        # Vérifie les codes essentiels
        assert 0 in WEATHERCODES  # Ensoleillé
        assert 63 in WEATHERCODES  # Pluie modérée
        assert 95 in WEATHERCODES  # Orage


# ═══════════════════════════════════════════════════════════
# TESTS CONVERSION DIRECTION
# ═══════════════════════════════════════════════════════════


class TestDirectionFromDegrees:
    """Tests pour direction_from_degrees()."""

    def test_nord(self):
        assert direction_from_degrees(0) == "N"
        assert direction_from_degrees(360) == "N"

    def test_est(self):
        assert direction_from_degrees(90) == "E"

    def test_sud(self):
        assert direction_from_degrees(180) == "S"

    def test_ouest(self):
        assert direction_from_degrees(270) == "O"

    def test_nord_est(self):
        assert direction_from_degrees(45) == "NE"

    def test_sud_ouest(self):
        assert direction_from_degrees(225) == "SO"

    def test_none_retourne_vide(self):
        assert direction_from_degrees(None) == ""

    def test_normalisation_360_plus(self):
        assert direction_from_degrees(450) == "E"  # 450 % 360 = 90

    def test_valeurs_limites(self):
        # Test autour des limites de chaque direction
        assert direction_from_degrees(22) == "N"
        assert direction_from_degrees(23) == "NE"
        assert direction_from_degrees(67) == "NE"
        assert direction_from_degrees(68) == "E"


class TestDegreesFromDirection:
    """Tests pour degrees_from_direction()."""

    def test_nord(self):
        assert degrees_from_direction("N") == 0.0

    def test_est(self):
        assert degrees_from_direction("E") == 90.0

    def test_sud(self):
        assert degrees_from_direction("S") == 180.0

    def test_ouest(self):
        assert degrees_from_direction("O") == 270.0

    def test_case_insensitive(self):
        assert degrees_from_direction("n") == 0.0
        assert degrees_from_direction("ne") == 45.0

    def test_avec_espaces(self):
        assert degrees_from_direction(" SO ") == 225.0

    def test_invalide_retourne_none(self):
        assert degrees_from_direction("INVALIDE") is None
        assert degrees_from_direction("") is None


# ═══════════════════════════════════════════════════════════
# TESTS CONVERSION WEATHERCODE
# ═══════════════════════════════════════════════════════════


class TestWeathercodeToCondition:
    """Tests pour weathercode_to_condition()."""

    def test_ensoleille(self):
        assert weathercode_to_condition(0) == "Ensoleillé"

    def test_pluie_moderee(self):
        assert weathercode_to_condition(63) == "Pluie modérée"

    def test_orage(self):
        assert weathercode_to_condition(95) == "Orage"

    def test_none_retourne_inconnu(self):
        assert weathercode_to_condition(None) == "Inconnu"

    def test_code_invalide_retourne_inconnu(self):
        assert weathercode_to_condition(9999) == "Inconnu"


class TestWeathercodeToIcon:
    """Tests pour weathercode_to_icon()."""

    def test_ensoleille(self):
        assert weathercode_to_icon(0) == "☀️"

    def test_pluie(self):
        assert weathercode_to_icon(63) == "🌧️"

    def test_orage(self):
        assert weathercode_to_icon(95) == "⛈️"

    def test_neige(self):
        assert weathercode_to_icon(73) == "❄️"

    def test_none_retourne_question(self):
        assert weathercode_to_icon(None) == "❓"

    def test_code_invalide(self):
        assert weathercode_to_icon(9999) == "🌡️"


class TestGetArrosageFactor:
    """Tests pour get_arrosage_factor()."""

    def test_ensoleille_facteur_eleve(self):
        factor = get_arrosage_factor(0)
        assert factor == 1.2

    def test_pluie_forte_facteur_zero(self):
        factor = get_arrosage_factor(65)
        assert factor == 0.0

    def test_couvert_facteur_reduit(self):
        factor = get_arrosage_factor(3)
        assert factor == 0.8

    def test_none_facteur_normal(self):
        factor = get_arrosage_factor(None)
        assert factor == 1.0

    def test_code_invalide_facteur_normal(self):
        factor = get_arrosage_factor(9999)
        assert factor == 1.0


# ═══════════════════════════════════════════════════════════
# TESTS CALCUL TEMPÉRATURES
# ═══════════════════════════════════════════════════════════


class TestCalculateAverageTemperature:
    """Tests pour calculate_average_temperature()."""

    def test_moyenne_simple(self):
        assert calculate_average_temperature(10, 20) == 15.0

    def test_moyenne_negative(self):
        assert calculate_average_temperature(-10, 0) == -5.0

    def test_meme_valeur(self):
        assert calculate_average_temperature(15, 15) == 15.0


class TestCalculateTemperatureAmplitude:
    """Tests pour calculate_temperature_amplitude()."""

    def test_amplitude_positive(self):
        assert calculate_temperature_amplitude(10, 25) == 15.0

    def test_amplitude_negative(self):
        assert calculate_temperature_amplitude(-5, 10) == 15.0

    def test_amplitude_zero(self):
        assert calculate_temperature_amplitude(20, 20) == 0.0


class TestCelsiusToFahrenheit:
    """Tests pour celsius_to_fahrenheit()."""

    def test_zero(self):
        assert celsius_to_fahrenheit(0) == 32.0

    def test_cent(self):
        assert celsius_to_fahrenheit(100) == 212.0

    def test_negatif(self):
        assert celsius_to_fahrenheit(-40) == -40.0  # Point égal C/F


class TestFahrenheitToCelsius:
    """Tests pour fahrenheit_to_celsius()."""

    def test_zero(self):
        result = fahrenheit_to_celsius(32)
        assert result == pytest.approx(0.0)

    def test_cent(self):
        result = fahrenheit_to_celsius(212)
        assert result == pytest.approx(100.0)

    def test_negatif(self):
        result = fahrenheit_to_celsius(-40)
        assert result == pytest.approx(-40.0)


class TestCalculateFeelsLike:
    """Tests pour calculate_feels_like()."""

    def test_conditions_normales(self):
        # Entre 10 et 20°C, peu de vent, humidité normale
        result = calculate_feels_like(15, 50, 10)
        assert result == 15.0

    def test_effet_vent_froid(self):
        # Température froide avec vent
        result = calculate_feels_like(5, 50, 30)
        assert result < 5  # Refroidissement éolien

    def test_effet_humidite_chaud(self):
        # Température chaude avec humidité
        result = calculate_feels_like(25, 80, 5)
        assert result > 25  # Chaleur ressentie supérieure

    def test_vent_faible_pas_effet(self):
        # Vent trop faible pour effet
        result = calculate_feels_like(5, 50, 3)
        assert result == 5.0


# ═══════════════════════════════════════════════════════════
# TESTS DÉTECTION ALERTES
# ═══════════════════════════════════════════════════════════


class TestDetectGelAlert:
    """Tests pour detect_gel_alert()."""

    def test_pas_dalerte_temperature_normale(self):
        result = detect_gel_alert(10.0)
        assert result is None

    def test_alerte_risque_gel(self):
        result = detect_gel_alert(1.0)
        assert result is not None
        assert result["niveau"] == "attention"
        assert "gel" in result["message"].lower()

    def test_alerte_gel_severe(self):
        result = detect_gel_alert(-5.0)
        assert result is not None
        assert result["niveau"] == "danger"
        assert result["temperature"] == -5.0


class TestDetectCaniculeAlert:
    """Tests pour detect_canicule_alert()."""

    def test_pas_dalerte_temperature_normale(self):
        result = detect_canicule_alert(25.0)
        assert result is None

    def test_alerte_forte_chaleur(self):
        result = detect_canicule_alert(36.0)
        assert result is not None
        assert result["niveau"] == "attention"

    def test_alerte_canicule_extreme(self):
        result = detect_canicule_alert(42.0)
        assert result is not None
        assert result["niveau"] == "danger"
        assert "extrême" in result["message"].lower()


class TestDetectPluieForteAlert:
    """Tests pour detect_pluie_forte_alert()."""

    def test_pas_dalerte_pluie_legere(self):
        result = detect_pluie_forte_alert(5.0)
        assert result is None

    def test_alerte_pluie_forte(self):
        result = detect_pluie_forte_alert(25.0)
        assert result is not None
        assert result["niveau"] == "attention"

    def test_alerte_pluie_violente(self):
        result = detect_pluie_forte_alert(60.0)
        assert result is not None
        assert result["niveau"] == "danger"
        assert result["precipitation"] == 60.0


class TestDetectVentFortAlert:
    """Tests pour detect_vent_fort_alert()."""

    def test_pas_dalerte_vent_leger(self):
        result = detect_vent_fort_alert(20.0)
        assert result is None

    def test_alerte_vent_fort(self):
        result = detect_vent_fort_alert(60.0)
        assert result is not None
        assert result["niveau"] == "attention"

    def test_alerte_tempete(self):
        result = detect_vent_fort_alert(100.0)
        assert result is not None
        assert result["niveau"] == "danger"
        assert "tempête" in result["message"].lower()


class TestDetectUvAlert:
    """Tests pour detect_uv_alert()."""

    def test_pas_dalerte_uv_normal(self):
        result = detect_uv_alert(3)
        assert result is None

    def test_alerte_uv_eleve(self):
        result = detect_uv_alert(7)
        assert result is not None
        assert result["niveau"] == "attention"

    def test_alerte_uv_extreme(self):
        result = detect_uv_alert(11)
        assert result is not None
        assert result["niveau"] == "danger"


class TestDetectAllAlerts:
    """Tests pour detect_all_alerts()."""

    def test_aucune_alerte(self):
        prevision = {
            "temp_min": 10,
            "temp_max": 25,
            "precipitation_mm": 5,
            "vent_km_h": 20,
            "uv_index": 3,
        }
        alertes = detect_all_alerts(prevision)
        assert len(alertes) == 0

    def test_alerte_gel(self):
        prevision = {"temp_min": -5}
        alertes = detect_all_alerts(prevision)
        assert len(alertes) == 1
        assert alertes[0]["type"] == "gel"

    def test_alertes_multiples(self):
        prevision = {
            "temp_min": -5,
            "temp_max": 42,
            "precipitation_mm": 60,
            "vent_km_h": 100,
            "uv_index": 11,
        }
        alertes = detect_all_alerts(prevision)
        assert len(alertes) == 5

    def test_cles_alternatives(self):
        """Supporte temperature_min au lieu de temp_min."""
        prevision = {"temperature_min": -5}
        alertes = detect_all_alerts(prevision)
        assert len(alertes) == 1
        assert alertes[0]["type"] == "gel"


# ═══════════════════════════════════════════════════════════
# TESTS CALCUL ARROSAGE
# ═══════════════════════════════════════════════════════════


class TestCalculateWateringNeed:
    """Tests pour calculate_watering_need()."""

    def test_pas_arrosage_si_pluie(self):
        result = calculate_watering_need(
            temp_max=25, precipitation_mm=10, wind_speed=10
        )
        assert result["besoin"] is False
        assert result["quantite_litres"] == 0.0

    def test_arrosage_normal(self):
        result = calculate_watering_need(
            temp_max=25, precipitation_mm=0, wind_speed=10
        )
        assert result["besoin"] is True
        assert result["quantite_litres"] > 0

    def test_arrosage_augmente_chaleur(self):
        result_normal = calculate_watering_need(
            temp_max=25, precipitation_mm=0, wind_speed=10
        )
        result_chaud = calculate_watering_need(
            temp_max=35, precipitation_mm=0, wind_speed=10
        )
        assert result_chaud["quantite_litres"] > result_normal["quantite_litres"]

    def test_arrosage_reduit_frais(self):
        result = calculate_watering_need(
            temp_max=10, precipitation_mm=0, wind_speed=5
        )
        # Température fraîche = réduction
        assert result["facteur"] < 1.0

    def test_effet_vent(self):
        result_calme = calculate_watering_need(
            temp_max=25, precipitation_mm=0, wind_speed=5
        )
        result_venteux = calculate_watering_need(
            temp_max=25, precipitation_mm=0, wind_speed=40
        )
        assert result_venteux["quantite_litres"] > result_calme["quantite_litres"]

    def test_effet_humidite_basse(self):
        result = calculate_watering_need(
            temp_max=25, precipitation_mm=0, wind_speed=10, humidity=30
        )
        assert "sec" in result["raison"].lower()

    def test_effet_humidite_haute(self):
        result = calculate_watering_need(
            temp_max=25, precipitation_mm=0, wind_speed=10, humidity=80
        )
        assert "humide" in result["raison"].lower()

    def test_effet_jours_sans_pluie(self):
        result = calculate_watering_need(
            temp_max=25, precipitation_mm=0, wind_speed=10, jours_sans_pluie=7
        )
        assert "sans pluie" in result["raison"].lower()

    def test_priorite_haute_si_facteur_eleve(self):
        result = calculate_watering_need(
            temp_max=38, precipitation_mm=0, wind_speed=40, humidity=30, jours_sans_pluie=7
        )
        assert result["priorite"] == 1


class TestDetectDroughtRisk:
    """Tests pour detect_drought_risk()."""

    def test_pas_de_secheresse(self):
        previsions = [
            {"precipitation_mm": 10},
            {"precipitation_mm": 5},
        ]
        risque, jours = detect_drought_risk(previsions)
        assert risque is False

    def test_secheresse_detectee(self):
        previsions = [{"precipitation_mm": 0} for _ in range(10)]
        risque, jours = detect_drought_risk(previsions)
        assert risque is True
        assert jours >= 7

    def test_comptage_jours(self):
        previsions = [
            {"precipitation_mm": 0},
            {"precipitation_mm": 0},
            {"precipitation_mm": 0},
            {"precipitation_mm": 10},  # Stop counting
            {"precipitation_mm": 0},
        ]
        risque, jours = detect_drought_risk(previsions)
        assert jours == 3


# ═══════════════════════════════════════════════════════════
# TESTS CONSEILS JARDINAGE
# ═══════════════════════════════════════════════════════════


class TestGetSeason:
    """Tests pour get_season()."""

    def test_printemps(self):
        assert get_season(date(2024, 4, 15)) == "printemps"

    def test_ete(self):
        assert get_season(date(2024, 7, 15)) == "été"

    def test_automne(self):
        assert get_season(date(2024, 10, 15)) == "automne"

    def test_hiver(self):
        assert get_season(date(2024, 1, 15)) == "hiver"

    def test_none_retourne_actuel(self):
        result = get_season(None)
        assert result in ["printemps", "été", "automne", "hiver"]


class TestGetGardeningAdviceForWeather:
    """Tests pour get_gardening_advice_for_weather()."""

    def test_conseils_chaleur(self):
        conseils = get_gardening_advice_for_weather("Ensoleillé", 32, 0)
        assert len(conseils) > 0
        assert any("arrosage" in c["titre"].lower() for c in conseils)

    def test_conseils_gel(self):
        conseils = get_gardening_advice_for_weather("Froid", 2, 0)
        assert len(conseils) > 0
        assert any("protection" in c["titre"].lower() for c in conseils)

    def test_conseils_pluie_forte(self):
        conseils = get_gardening_advice_for_weather("Pluie", 15, 40)
        assert len(conseils) > 0
        assert any("drainage" in c["titre"].lower() for c in conseils)

    def test_conseils_beau_temps(self):
        conseils = get_gardening_advice_for_weather("Ensoleillé", 20, 0)
        assert any("idéale" in c["titre"].lower() for c in conseils)

    def test_conseils_orage(self):
        conseils = get_gardening_advice_for_weather("Orage prévu", 25, 30)
        assert any("orage" in c["titre"].lower() for c in conseils)

    def test_tri_par_priorite(self):
        conseils = get_gardening_advice_for_weather("Orage avec chaleur", 35, 40)
        if len(conseils) >= 2:
            assert conseils[0]["priorite"] <= conseils[1]["priorite"]


class TestFormatWeatherSummary:
    """Tests pour format_weather_summary()."""

    def test_format_complet(self):
        previsions = [
            {"temp_min": 10, "temp_max": 20, "precipitation_mm": 5},
            {"temp_min": 12, "temp_max": 22, "precipitation_mm": 0},
        ]
        result = format_weather_summary(previsions)
        assert "2 jours" in result
        assert "10°C" in result
        assert "22°C" in result

    def test_format_sans_pluie(self):
        previsions = [
            {"temp_min": 15, "temp_max": 25, "precipitation_mm": 0},
        ]
        result = format_weather_summary(previsions)
        assert "pas de pluie" in result.lower()

    def test_format_avec_pluie(self):
        previsions = [
            {"temp_min": 15, "temp_max": 25, "precipitation_mm": 10},
        ]
        result = format_weather_summary(previsions)
        assert "10mm" in result

    def test_liste_vide(self):
        result = format_weather_summary([])
        assert "aucune" in result.lower()


# ═══════════════════════════════════════════════════════════
# TESTS PARSING API
# ═══════════════════════════════════════════════════════════


class TestSafeGetIndex:
    """Tests pour _safe_get_index()."""

    def test_index_valide(self):
        data = {"values": [10, 20, 30]}
        result = _safe_get_index(data, "values", 1)
        assert result == 20

    def test_index_hors_limites(self):
        data = {"values": [10, 20]}
        result = _safe_get_index(data, "values", 5)
        assert result is None

    def test_cle_inexistante(self):
        data = {"autres": [10]}
        result = _safe_get_index(data, "values", 0)
        assert result is None

    def test_default_value(self):
        data = {"values": [10]}
        result = _safe_get_index(data, "values", 5, default=-1)
        assert result == -1

    def test_liste_vide(self):
        data = {"values": []}
        result = _safe_get_index(data, "values", 0)
        assert result is None


class TestParseOpenMeteoDaily:
    """Tests pour parse_open_meteo_daily()."""

    def test_parse_complet(self):
        data = {
            "daily": {
                "time": ["2024-07-01", "2024-07-02"],
                "temperature_2m_min": [15, 16],
                "temperature_2m_max": [25, 26],
                "precipitation_sum": [0, 5],
                "weathercode": [0, 63],
                "wind_speed_10m_max": [10, 20],
                "uv_index_max": [5, 6],
            }
        }
        result = parse_open_meteo_daily(data)
        assert len(result) == 2
        assert result[0]["date"] == "2024-07-01"
        assert result[0]["temperature_min"] == 15
        assert result[0]["temperature_max"] == 25
        assert result[0]["condition"] == "Ensoleillé"
        assert result[1]["condition"] == "Pluie modérée"

    def test_parse_avec_lever_coucher_soleil(self):
        data = {
            "daily": {
                "time": ["2024-07-01"],
                "sunrise": ["2024-07-01T05:30"],
                "sunset": ["2024-07-01T21:30"],
            }
        }
        result = parse_open_meteo_daily(data)
        assert result[0]["lever_soleil"] == "05:30"
        assert result[0]["coucher_soleil"] == "21:30"

    def test_parse_donnees_manquantes(self):
        data = {"daily": {"time": ["2024-07-01"]}}
        result = parse_open_meteo_daily(data)
        assert len(result) == 1
        assert result[0]["precipitation_mm"] == 0  # Default

    def test_parse_vide(self):
        data = {}
        result = parse_open_meteo_daily(data)
        assert result == []


class TestValidateCoordinates:
    """Tests pour validate_coordinates()."""

    def test_coordonnees_valides(self):
        valide, msg = validate_coordinates(48.8566, 2.3522)  # Paris
        assert valide is True
        assert msg == ""

    def test_latitude_invalide_haute(self):
        valide, msg = validate_coordinates(95, 0)
        assert valide is False
        assert "latitude" in msg.lower()

    def test_latitude_invalide_basse(self):
        valide, msg = validate_coordinates(-95, 0)
        assert valide is False

    def test_longitude_invalide_haute(self):
        valide, msg = validate_coordinates(0, 185)
        assert valide is False
        assert "longitude" in msg.lower()

    def test_longitude_invalide_basse(self):
        valide, msg = validate_coordinates(0, -185)
        assert valide is False

    def test_type_invalide_latitude(self):
        valide, msg = validate_coordinates("48", 2)
        assert valide is False
        assert "latitude" in msg.lower()

    def test_type_invalide_longitude(self):
        valide, msg = validate_coordinates(48, "2")
        assert valide is False
        assert "longitude" in msg.lower()

    def test_limites_valides(self):
        # Limites exactes
        valide1, _ = validate_coordinates(90, 180)
        valide2, _ = validate_coordinates(-90, -180)
        assert valide1 is True
        assert valide2 is True
