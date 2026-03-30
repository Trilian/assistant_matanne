"""Tests pour les intégrations météo — alertes, arrosage, service."""

import pytest

from src.services.integrations.weather.alertes_meteo import (
    calculate_average_temperature,
    calculate_feels_like,
    calculate_temperature_amplitude,
    celsius_to_fahrenheit,
    detect_canicule_alert,
    detect_gel_alert,
    detect_pluie_forte_alert,
    detect_uv_alert,
    detect_vent_fort_alert,
    fahrenheit_to_celsius,
)
from src.services.integrations.weather.arrosage import (
    calculate_watering_need,
    detect_drought_risk,
)


# ═══════════════════════════════════════════════════════════
# TESTS TEMPÉRATURES
# ═══════════════════════════════════════════════════════════


class TestCalculsTemperature:
    def test_moyenne(self):
        assert calculate_average_temperature(10.0, 20.0) == 15.0
        assert calculate_average_temperature(-5.0, 5.0) == 0.0

    def test_amplitude(self):
        assert calculate_temperature_amplitude(10.0, 30.0) == 20.0
        assert calculate_temperature_amplitude(-5.0, 5.0) == 10.0

    def test_celsius_fahrenheit(self):
        assert celsius_to_fahrenheit(0) == 32.0
        assert celsius_to_fahrenheit(100) == 212.0
        assert fahrenheit_to_celsius(32) == 0.0
        assert fahrenheit_to_celsius(212) == 100.0

    def test_ressenti_froid_vent(self):
        """Vent fort + froid → refroidissement éolien."""
        result = calculate_feels_like(5.0, 50, 20.0)
        assert result < 5.0  # Doit être inférieur à la temp réelle

    def test_ressenti_chaud_humide(self):
        """Chaleur + humidité → chaleur ressentie supérieure."""
        result = calculate_feels_like(30.0, 80, 5.0)
        assert result > 30.0

    def test_ressenti_normal(self):
        """Conditions normales → pas d'ajustement significatif."""
        result = calculate_feels_like(15.0, 50, 10.0)
        assert result == 15.0


# ═══════════════════════════════════════════════════════════
# TESTS ALERTES MÉTÉO
# ═══════════════════════════════════════════════════════════


class TestAlertesGel:
    def test_pas_de_gel(self):
        assert detect_gel_alert(10.0) is None
        assert detect_gel_alert(3.0) is None

    def test_risque_gel(self):
        result = detect_gel_alert(1.5)
        assert result is not None
        assert result["niveau"] == "attention"
        assert "gel" in result["message"].lower() or "Gel" in result["message"]

    def test_gel_severe(self):
        result = detect_gel_alert(-3.0)
        assert result is not None
        assert result["niveau"] == "danger"
        assert result["temperature"] == -3.0


class TestAlertesCanicule:
    def test_pas_de_canicule(self):
        assert detect_canicule_alert(30.0) is None

    def test_forte_chaleur(self):
        result = detect_canicule_alert(36.0)
        assert result is not None
        assert result["niveau"] == "attention"

    def test_canicule_extreme(self):
        result = detect_canicule_alert(42.0)
        assert result is not None
        assert result["niveau"] == "danger"


class TestAlertesPluie:
    def test_pas_de_pluie_forte(self):
        assert detect_pluie_forte_alert(5.0) is None

    def test_pluie_forte(self):
        result = detect_pluie_forte_alert(25.0)
        assert result is not None
        assert result["niveau"] == "attention"

    def test_pluie_violente(self):
        result = detect_pluie_forte_alert(55.0)
        assert result is not None
        assert result["niveau"] == "danger"


class TestAlertesVent:
    def test_pas_de_vent_fort(self):
        assert detect_vent_fort_alert(30.0) is None

    def test_vent_fort(self):
        result = detect_vent_fort_alert(55.0)
        assert result is not None
        assert result["niveau"] == "attention"

    def test_tempete(self):
        result = detect_vent_fort_alert(85.0)
        assert result is not None
        assert result["niveau"] == "danger"


class TestAlertesUV:
    def test_uv_normal(self):
        assert detect_uv_alert(4) is None

    def test_uv_eleve(self):
        result = detect_uv_alert(7)
        assert result is not None
        assert result["niveau"] == "attention"

    def test_uv_extreme(self):
        result = detect_uv_alert(11)
        assert result is not None
        assert result["niveau"] == "danger"


# ═══════════════════════════════════════════════════════════
# TESTS ARROSAGE
# ═══════════════════════════════════════════════════════════


class TestCalculArrosage:
    def test_pluie_forte_pas_arrosage(self):
        result = calculate_watering_need(
            temp_max=25.0,
            precipitation_mm=10.0,
            wind_speed=5.0,
        )
        assert result["besoin"] is False
        assert result["quantite_litres"] == 0.0

    def test_chaleur_arrosage_necessaire(self):
        result = calculate_watering_need(
            temp_max=36.0,
            precipitation_mm=0.0,
            wind_speed=5.0,
            humidity=30,
        )
        assert result["besoin"] is True
        assert result["quantite_litres"] > 0

    def test_secheresse_prolongee(self):
        result = calculate_watering_need(
            temp_max=30.0,
            precipitation_mm=0.0,
            wind_speed=10.0,
            jours_sans_pluie=10,
        )
        assert result["besoin"] is True
        assert result["priorite"] > 0

    def test_conditions_fraiches(self):
        result = calculate_watering_need(
            temp_max=12.0,
            precipitation_mm=0.0,
            wind_speed=5.0,
            humidity=70,
        )
        # Peut nécessiter moins mais reste un dict valide
        assert "besoin" in result
        assert "quantite_litres" in result


class TestDetectionSecheresse:
    def test_pas_de_secheresse(self):
        previsions = [{"precipitation_mm": 5.0}] * 3  # 3 jours avec pluie
        risque, jours = detect_drought_risk(previsions)
        assert risque is False

    def test_secheresse_detectee(self):
        previsions = [{"precipitation_mm": 0.0}] * 10  # 10 jours sans pluie
        risque, jours = detect_drought_risk(previsions)
        assert risque is True
        assert jours == 10

    def test_pluie_arrete_compteur(self):
        previsions = [
            {"precipitation_mm": 0.0},
            {"precipitation_mm": 0.0},
            {"precipitation_mm": 10.0},  # pluie → stop
            {"precipitation_mm": 0.0},
        ]
        risque, jours = detect_drought_risk(previsions)
        assert jours == 2
        assert risque is False
