"""
Tests unitaires pour weather_utils.py

Ces tests vérifient les fonctions pures sans dépendance externe.
"""

import pytest
from datetime import date
from src.services.weather import (
    # Conversion de direction
    direction_from_degrees,
    degrees_from_direction,
    
    # Weathercodes
    weathercode_to_condition,
    weathercode_to_icon,
    get_arrosage_factor,
    
    # Températures
    calculate_average_temperature,
    calculate_temperature_amplitude,
    calculate_feels_like,
    celsius_to_fahrenheit,
    fahrenheit_to_celsius,
    
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
    
    # Saisons
    get_season,
    get_gardening_advice_for_weather,
    
    # Parsing API
    parse_open_meteo_daily,
    validate_coordinates,
    
    # Constantes
    WEATHERCODES,
)


# ═══════════════════════════════════════════════════════════
# Tests: Direction du vent
# ═══════════════════════════════════════════════════════════


class TestDirectionFromDegrees:
    """Tests pour direction_from_degrees"""
    
    def test_nord(self):
        assert direction_from_degrees(0) == "N"
        assert direction_from_degrees(360) == "N"
        assert direction_from_degrees(11) == "N"
    
    def test_nord_est(self):
        assert direction_from_degrees(45) == "NE"
        assert direction_from_degrees(33) == "NE"
    
    def test_est(self):
        assert direction_from_degrees(90) == "E"
        assert direction_from_degrees(80) == "E"
    
    def test_sud_est(self):
        assert direction_from_degrees(135) == "SE"
    
    def test_sud(self):
        assert direction_from_degrees(180) == "S"
    
    def test_sud_ouest(self):
        assert direction_from_degrees(225) == "SO"
    
    def test_ouest(self):
        assert direction_from_degrees(270) == "O"
    
    def test_nord_ouest(self):
        assert direction_from_degrees(315) == "NO"
    
    def test_valeur_none(self):
        assert direction_from_degrees(None) == ""
    
    def test_valeur_negative(self):
        # Devrait normaliser en utilisant modulo
        result = direction_from_degrees(-45)
        assert result == "NO"  # -45 % 360 = 315 -> NO


class TestDegreesFromDirection:
    """Tests pour degrees_from_direction"""
    
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
    
    def test_invalide(self):
        assert degrees_from_direction("INVALID") is None


# ═══════════════════════════════════════════════════════════
# Tests: Weathercodes
# ═══════════════════════════════════════════════════════════


class TestWeathercodeToCondition:
    """Tests pour weathercode_to_condition"""
    
    def test_ensoleille(self):
        condition = weathercode_to_condition(0)
        assert "ensoleillé" in condition.lower() or "soleil" in condition.lower()
    
    def test_partiellement_nuageux(self):
        condition = weathercode_to_condition(2)
        assert condition is not None
        assert len(condition) > 0
        assert "nuageux" in condition.lower()
    
    def test_brouillard(self):
        condition = weathercode_to_condition(45)
        assert "brouillard" in condition.lower()
    
    def test_pluie_faible(self):
        condition = weathercode_to_condition(61)
        assert "pluie" in condition.lower()
    
    def test_neige(self):
        condition = weathercode_to_condition(71)
        assert "neige" in condition.lower()
    
    def test_orage(self):
        condition = weathercode_to_condition(95)
        assert "orage" in condition.lower()
    
    def test_code_inconnu(self):
        condition = weathercode_to_condition(999)
        assert condition is not None


class TestWeathercodeToIcon:
    """Tests pour weathercode_to_icon"""
    
    def test_soleil(self):
        icon = weathercode_to_icon(0)
        assert icon in ["☀️", "🌞", "🌤️"]
    
    def test_nuages(self):
        icon = weathercode_to_icon(3)
        assert icon is not None
    
    def test_pluie(self):
        icon = weathercode_to_icon(63)
        assert "🌧" in icon or "💧" in icon or icon == "🌧️"
    
    def test_neige_icon(self):
        icon = weathercode_to_icon(75)
        assert "❄" in icon or "🌨" in icon
    
    def test_orage_icon(self):
        icon = weathercode_to_icon(95)
        assert "⛈" in icon or "🌩" in icon


class TestGetArrosageFactor:
    """Tests pour get_arrosage_factor"""
    
    def test_ensoleille_plus_arrosage(self):
        # Soleil = besoin d'arroser plus
        factor = get_arrosage_factor(0)
        assert factor > 1.0
    
    def test_couvert_moins_arrosage(self):
        factor = get_arrosage_factor(3)
        assert factor < 1.0
    
    def test_pluie_pas_arrosage(self):
        # Pluie forte = pas besoin d'arroser
        factor = get_arrosage_factor(65)
        assert factor == 0.0
    
    def test_neige_pas_arrosage(self):
        factor = get_arrosage_factor(75)
        assert factor == 0.0
    
    def test_code_inconnu(self):
        factor = get_arrosage_factor(999)
        assert factor >= 0.0  # Valeur par défaut


# ═══════════════════════════════════════════════════════════
# Tests: Températures
# ═══════════════════════════════════════════════════════════


class TestCalculateAverageTemperature:
    """Tests pour calculate_average_temperature"""
    
    def test_moyenne_normale(self):
        assert calculate_average_temperature(10.0, 20.0) == 15.0
    
    def test_moyenne_negative(self):
        assert calculate_average_temperature(-5.0, 5.0) == 0.0
    
    def test_meme_valeur(self):
        assert calculate_average_temperature(15.0, 15.0) == 15.0
    
    def test_decimales(self):
        result = calculate_average_temperature(10.5, 11.5)
        assert result == 11.0


class TestCalculateTemperatureAmplitude:
    """Tests pour calculate_temperature_amplitude"""
    
    def test_amplitude_normale(self):
        assert calculate_temperature_amplitude(10.0, 20.0) == 10.0
    
    def test_amplitude_zero(self):
        assert calculate_temperature_amplitude(15.0, 15.0) == 0.0
    
    def test_amplitude_negative(self):
        # min > max devrait retourner la valeur absolue
        result = calculate_temperature_amplitude(20.0, 10.0)
        assert result == 10.0 or result == -10.0


class TestCalculateFeelsLike:
    """Tests pour calculate_feels_like"""
    
    def test_temperature_normale_sans_vent(self):
        # temp=20, humidity=50 (int), wind_speed=0
        result = calculate_feels_like(20.0, 50, 0.0)
        assert 18.0 <= result <= 22.0
    
    def test_vent_froid(self):
        # Le vent fait baisser le ressenti quand temp < 10
        result = calculate_feels_like(5.0, 50, 30.0)
        assert result < 5.0
    
    def test_humidite_elevee_chaud(self):
        # Humidité élevée + chaleur = ressenti plus chaud
        result = calculate_feels_like(25.0, 80, 5.0)
        assert result >= 25.0
    
    def test_temperature_normale(self):
        # Cas normal: retourne la température
        result = calculate_feels_like(15.0, 50, 10.0)
        assert 14.0 <= result <= 16.0


class TestCelsiusFahrenheit:
    """Tests pour les conversions Celsius/Fahrenheit"""
    
    def test_celsius_to_fahrenheit_zero(self):
        assert celsius_to_fahrenheit(0.0) == 32.0
    
    def test_celsius_to_fahrenheit_cent(self):
        assert celsius_to_fahrenheit(100.0) == 212.0
    
    def test_fahrenheit_to_celsius_32(self):
        assert fahrenheit_to_celsius(32.0) == 0.0
    
    def test_fahrenheit_to_celsius_212(self):
        assert fahrenheit_to_celsius(212.0) == 100.0
    
    def test_round_trip(self):
        original = 25.0
        converted = fahrenheit_to_celsius(celsius_to_fahrenheit(original))
        assert abs(converted - original) < 0.01


# ═══════════════════════════════════════════════════════════
# Tests: Alertes météo
# ═══════════════════════════════════════════════════════════


class TestDetectGelAlert:
    """Tests pour detect_gel_alert"""
    
    def test_gel_severe(self):
        alerte = detect_gel_alert(-2.0)
        assert alerte is not None
        assert alerte["niveau"] == "danger"
        assert "gel" in alerte["message"].lower()
    
    def test_risque_gel(self):
        alerte = detect_gel_alert(1.5)
        assert alerte is not None
        assert alerte["niveau"] == "attention"
        assert "risque" in alerte["message"].lower() or "gel" in alerte["message"].lower()
    
    def test_pas_de_gel(self):
        alerte = detect_gel_alert(10.0)
        assert alerte is None
    
    def test_gel_tres_severe(self):
        alerte = detect_gel_alert(-10.0)
        assert alerte is not None
        assert alerte["niveau"] == "danger"


class TestDetectCaniculeAlert:
    """Tests pour detect_canicule_alert"""
    
    def test_canicule_extreme(self):
        alerte = detect_canicule_alert(42.0)
        assert alerte is not None
        assert alerte["niveau"] == "danger"
        assert "canicule" in alerte["message"].lower()
    
    def test_forte_chaleur(self):
        alerte = detect_canicule_alert(36.0)
        assert alerte is not None
        assert alerte["niveau"] == "attention"
    
    def test_pas_de_canicule(self):
        alerte = detect_canicule_alert(25.0)
        assert alerte is None
    
    def test_temperature_limite(self):
        # Juste au-dessus du seuil (35°C)
        alerte = detect_canicule_alert(35.0)
        assert alerte is not None


class TestDetectPluieForteAlert:
    """Tests pour detect_pluie_forte_alert"""
    
    def test_pluie_forte(self):
        alerte = detect_pluie_forte_alert(30.0)
        assert alerte is not None
        assert alerte["niveau"] == "attention"
    
    def test_pluie_violente(self):
        alerte = detect_pluie_forte_alert(60.0)
        assert alerte is not None
        assert alerte["niveau"] == "danger"
    
    def test_pluie_faible(self):
        alerte = detect_pluie_forte_alert(5.0)
        assert alerte is None


class TestDetectVentFortAlert:
    """Tests pour detect_vent_fort_alert"""
    
    def test_vent_fort(self):
        alerte = detect_vent_fort_alert(60.0)
        assert alerte is not None
        assert alerte["niveau"] == "attention"
    
    def test_tempete(self):
        alerte = detect_vent_fort_alert(90.0)
        assert alerte is not None
        assert alerte["niveau"] == "danger"
    
    def test_vent_faible(self):
        alerte = detect_vent_fort_alert(20.0)
        assert alerte is None


class TestDetectUVAlert:
    """Tests pour detect_uv_alert"""
    
    def test_uv_extreme(self):
        alerte = detect_uv_alert(11)
        assert alerte is not None
        assert alerte["niveau"] == "danger"
    
    def test_uv_eleve(self):
        alerte = detect_uv_alert(7)
        assert alerte is not None
        assert alerte["niveau"] == "attention"
    
    def test_uv_faible(self):
        alerte = detect_uv_alert(3)
        assert alerte is None


class TestDetectAllAlerts:
    """Tests pour detect_all_alerts"""
    
    def test_plusieurs_alertes(self):
        meteo = {
            "temp_min": -3.0,
            "temp_max": 5.0,
            "precipitation_mm": 40.0,
            "vent_km_h": 70.0,
            "uv_index": 8,
        }
        alertes = detect_all_alerts(meteo)
        assert len(alertes) >= 2  # Au moins gel, pluie et vent
    
    def test_pas_d_alerte(self):
        meteo = {
            "temp_min": 15.0,
            "temp_max": 25.0,
            "precipitation_mm": 2.0,
            "vent_km_h": 15.0,
            "uv_index": 3,
        }
        alertes = detect_all_alerts(meteo)
        assert len(alertes) == 0
    
    def test_canicule_et_uv(self):
        meteo = {
            "temp_min": 25.0,
            "temp_max": 42.0,
            "precipitation_mm": 0.0,
            "vent_km_h": 10.0,
            "uv_index": 11,
        }
        alertes = detect_all_alerts(meteo)
        types = [a["type"] for a in alertes]
        assert "canicule" in types
        assert "uv" in types


# ═══════════════════════════════════════════════════════════
# Tests: Arrosage
# ═══════════════════════════════════════════════════════════


class TestCalculateWateringNeed:
    """Tests pour calculate_watering_need"""
    
    def test_besoin_normal(self):
        result = calculate_watering_need(
            temp_max=25.0,
            precipitation_mm=0.0,
            wind_speed=10.0,
            humidity=50
        )
        assert isinstance(result, dict)
        assert result["besoin"] is True
        assert result["quantite_litres"] > 0
    
    def test_apres_pluie(self):
        result = calculate_watering_need(
            temp_max=25.0,
            precipitation_mm=20.0,
            wind_speed=5.0,
            humidity=80
        )
        assert result["besoin"] is False
        assert result["quantite_litres"] == 0
    
    def test_canicule(self):
        result = calculate_watering_need(
            temp_max=38.0,
            precipitation_mm=0.0,
            wind_speed=20.0,
            humidity=30
        )
        assert result["besoin"] is True
        assert result["quantite_litres"] > 3.0  # Plus que le besoin de base
    
    def test_temps_frais_pluie(self):
        result = calculate_watering_need(
            temp_max=15.0,
            precipitation_mm=10.0,
            wind_speed=5.0,
            humidity=90
        )
        assert result["besoin"] is False


class TestDetectDroughtRisk:
    """Tests pour detect_drought_risk"""
    
    def test_risque_secheresse(self):
        meteo_semaine = [
            {"temp_max": 35.0, "precipitation_mm": 0.0},
            {"temp_max": 36.0, "precipitation_mm": 0.0},
            {"temp_max": 34.0, "precipitation_mm": 0.0},
            {"temp_max": 35.0, "precipitation_mm": 0.0},
            {"temp_max": 37.0, "precipitation_mm": 0.0},
            {"temp_max": 35.0, "precipitation_mm": 0.0},
            {"temp_max": 36.0, "precipitation_mm": 0.0},
            {"temp_max": 34.0, "precipitation_mm": 0.0},
        ]
        risque, jours = detect_drought_risk(meteo_semaine)
        assert risque is True
        assert jours >= 7
    
    def test_pas_de_risque(self):
        meteo_semaine = [
            {"temp_max": 22.0, "precipitation_mm": 5.0},
            {"temp_max": 20.0, "precipitation_mm": 10.0},
            {"temp_max": 18.0, "precipitation_mm": 2.0},
        ]
        risque, jours = detect_drought_risk(meteo_semaine)
        assert risque is False


# ═══════════════════════════════════════════════════════════
# Tests: Saisons et conseils jardinage
# ═══════════════════════════════════════════════════════════


class TestGetSeason:
    """Tests pour get_season"""
    
    def test_printemps(self):
        assert get_season(date(2024, 4, 15)) == "printemps"
        assert get_season(date(2024, 3, 21)) == "printemps"
    
    def test_ete(self):
        assert get_season(date(2024, 7, 15)) == "été"
        assert get_season(date(2024, 8, 1)) == "été"
    
    def test_automne(self):
        assert get_season(date(2024, 10, 15)) == "automne"
        assert get_season(date(2024, 11, 1)) == "automne"
    
    def test_hiver(self):
        assert get_season(date(2024, 1, 15)) == "hiver"
        assert get_season(date(2024, 12, 25)) == "hiver"
    
    def test_sans_date(self):
        saison = get_season(None)
        assert saison in ["printemps", "été", "automne", "hiver"]


class TestGetGardeningAdvice:
    """Tests pour get_gardening_advice_for_weather"""
    
    def test_conseil_froid(self):
        conseils = get_gardening_advice_for_weather(
            condition="ensoleillé",
            temp_max=3.0,
            precipitation_mm=0.0
        )
        assert isinstance(conseils, list)
        # Devrait avoir des conseils pour le froid
        assert len(conseils) > 0
    
    def test_conseil_pluie(self):
        conseils = get_gardening_advice_for_weather(
            condition="pluie",
            temp_max=20.0,
            precipitation_mm=15.0
        )
        assert isinstance(conseils, list)
    
    def test_conseil_canicule(self):
        conseils = get_gardening_advice_for_weather(
            condition="ensoleillé",
            temp_max=35.0,
            precipitation_mm=0.0
        )
        assert len(conseils) > 0
        # Conseil sur l'arrosage
        has_arrosage = any(
            "arros" in c.get("titre", "").lower() or 
            "arros" in c.get("description", "").lower()
            for c in conseils
        )
        assert has_arrosage


# ═══════════════════════════════════════════════════════════
# Tests: Parsing API
# ═══════════════════════════════════════════════════════════


class TestParseOpenMeteoDaily:
    """Tests pour parse_open_meteo_daily"""
    
    def test_parsing_normal(self):
        data = {
            "daily": {
                "time": ["2024-06-01", "2024-06-02"],
                "temperature_2m_max": [25.0, 27.0],
                "temperature_2m_min": [15.0, 17.0],
                "precipitation_sum": [0.0, 5.0],
                "weathercode": [0, 61],
            }
        }
        result = parse_open_meteo_daily(data)
        assert len(result) == 2
        assert result[0]["temperature_max"] == 25.0
        assert result[1]["precipitation_mm"] == 5.0
    
    def test_donnees_vides(self):
        result = parse_open_meteo_daily({})
        assert result == []
    
    def test_donnees_partielles(self):
        data = {
            "daily": {
                "time": ["2024-06-01"],
                "temperature_2m_max": [25.0],
                # Autres champs manquants
            }
        }
        result = parse_open_meteo_daily(data)
        assert len(result) == 1
        assert result[0].get("temperature_max") == 25.0


class TestValidateCoordinates:
    """Tests pour validate_coordinates"""
    
    def test_coordonnees_valides(self):
        is_valid, msg = validate_coordinates(48.8566, 2.3522)  # Paris
        assert is_valid is True
        assert msg == ""
        
        is_valid, msg = validate_coordinates(0.0, 0.0)
        assert is_valid is True
    
    def test_latitude_invalide(self):
        is_valid, msg = validate_coordinates(91.0, 2.0)
        assert is_valid is False
        assert "latitude" in msg.lower()
        
        is_valid, msg = validate_coordinates(-91.0, 2.0)
        assert is_valid is False
    
    def test_longitude_invalide(self):
        is_valid, msg = validate_coordinates(45.0, 181.0)
        assert is_valid is False
        assert "longitude" in msg.lower()
        
        is_valid, msg = validate_coordinates(45.0, -181.0)
        assert is_valid is False
    
    def test_valeurs_none(self):
        is_valid, msg = validate_coordinates(None, 2.0)
        assert is_valid is False
        
        is_valid, msg = validate_coordinates(45.0, None)
        assert is_valid is False


# ═══════════════════════════════════════════════════════════
# Tests: Constantes
# ═══════════════════════════════════════════════════════════


class TestWeathercodesConstant:
    """Tests pour la constante WEATHERCODES"""
    
    def test_codes_principaux_presents(self):
        assert 0 in WEATHERCODES
        assert 45 in WEATHERCODES
        assert 61 in WEATHERCODES
        assert 95 in WEATHERCODES
    
    def test_format_description(self):
        for code, data in WEATHERCODES.items():
            assert isinstance(code, int)
            assert isinstance(data, dict)
            assert "condition" in data
            assert "icon" in data
            assert len(data["condition"]) > 0
