"""
Tests pour src/utils/formatters/units.py
Données réelles de cuisine et ingrédients
"""
import pytest
from src.utils.formatters.units import (
    formater_poids,
    formater_volume,
    formater_temperature,
)


@pytest.mark.unit
class TestFormaterPoids:
    """Tests formater_poids avec ingrédients réels."""

    # Grammages courants
    def test_500g_farine(self):
        """500g farine."""
        result = formater_poids(500)
        assert "500" in result
        assert "g" in result.lower()

    def test_250g_beurre(self):
        """250g beurre."""
        result = formater_poids(250)
        assert "250" in result
        assert "g" in result.lower()

    def test_100g_chocolat(self):
        """100g chocolat."""
        result = formater_poids(100)
        assert "100" in result

    def test_50g_levure(self):
        """50g levure."""
        result = formater_poids(50)
        assert "50" in result

    # Kilogrammes
    def test_1kg_pommes_de_terre(self):
        """1kg pommes de terre."""
        result = formater_poids(1000)
        assert "1" in result
        assert "kg" in result.lower()

    def test_1_5kg_poulet(self):
        """1.5kg poulet."""
        result = formater_poids(1500)
        assert "1.5" in result or "1,5" in result
        assert "kg" in result.lower()

    def test_2_5kg_roti(self):
        """2.5kg rôti."""
        result = formater_poids(2500)
        assert "2.5" in result or "2,5" in result
        assert "kg" in result.lower()

    # Cas limites
    def test_poids_0(self):
        """0g."""
        result = formater_poids(0)
        assert "0" in result

    def test_poids_none(self):
        """None."""
        result = formater_poids(None)
        assert "0" in result

    def test_poids_negatif(self):
        """Valeur négative."""
        result = formater_poids(-10)
        assert "0" in result or "-" in result


@pytest.mark.unit
class TestFormaterVolume:
    """Tests formater_volume avec liquides cuisine."""

    # Millilitres courants
    def test_250ml_lait(self):
        """250ml lait."""
        result = formater_volume(250)
        assert "250" in result
        assert "ml" in result.lower()

    def test_100ml_huile(self):
        """100ml huile."""
        result = formater_volume(100)
        assert "100" in result

    def test_50ml_vinaigre(self):
        """50ml vinaigre."""
        result = formater_volume(50)
        assert "50" in result

    def test_150ml_creme(self):
        """150ml crème fraîche."""
        result = formater_volume(150)
        assert "150" in result

    # Litres
    def test_1l_eau(self):
        """1L eau."""
        result = formater_volume(1000)
        assert "1" in result
        assert "l" in result.lower()

    def test_1_5l_bouillon(self):
        """1.5L bouillon."""
        result = formater_volume(1500)
        assert "1.5" in result or "1,5" in result
        assert "l" in result.lower()

    def test_2l_lait(self):
        """2L lait."""
        result = formater_volume(2000)
        assert "2" in result
        assert "l" in result.lower()

    # Cas limites
    def test_volume_0(self):
        """0ml."""
        result = formater_volume(0)
        assert "0" in result

    def test_volume_none(self):
        """None."""
        result = formater_volume(None)
        assert "0" in result

    def test_volume_negatif(self):
        """Valeur négative."""
        result = formater_volume(-50)
        assert "0" in result or "-" in result


@pytest.mark.unit
class TestFormaterTemperature:
    """Tests formater_temperature avec températures four/réfrigérateur."""

    # Températures four
    def test_four_180c(self):
        """Four 180Â°C."""
        result = formater_temperature(180)
        assert "180" in result
        assert "Â°" in result

    def test_four_200c(self):
        """Four 200Â°C."""
        result = formater_temperature(200)
        assert "200" in result
        assert "Â°C" in result

    def test_four_220c(self):
        """Four 220Â°C."""
        result = formater_temperature(220)
        assert "220" in result

    def test_four_160c(self):
        """Four doux 160Â°C."""
        result = formater_temperature(160)
        assert "160" in result

    def test_four_250c(self):
        """Four très chaud 250Â°C."""
        result = formater_temperature(250)
        assert "250" in result

    # Températures réfrigérateur/congélateur
    def test_frigo_4c(self):
        """Frigo 4Â°C."""
        result = formater_temperature(4)
        assert "4" in result
        assert "Â°" in result

    def test_congelateur_moins18c(self):
        """Congélateur -18Â°C."""
        result = formater_temperature(-18)
        assert "-18" in result
        assert "Â°" in result

    # Fahrenheit
    def test_fahrenheit_350f(self):
        """Four 350Â°F."""
        result = formater_temperature(350, unit="F")
        assert "350" in result
        assert "Â°F" in result

    def test_fahrenheit_400f(self):
        """Four 400Â°F."""
        result = formater_temperature(400, unit="F")
        assert "400" in result
        assert "Â°F" in result

    # Cas limites
    def test_temperature_0(self):
        """0Â°C."""
        result = formater_temperature(0)
        assert "0" in result
        assert "Â°" in result

    def test_temperature_none(self):
        """None."""
        result = formater_temperature(None)
        assert "Â°" in result or "0" in result

    def test_temperature_float(self):
        """Float 37.5Â°C arrondi Ã  37."""
        result = formater_temperature(37.5)
        assert "37" in result
