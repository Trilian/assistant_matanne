"""
Tests pour les formatters d'unités (poids/volume)
"""

import pytest

from src.utils.formatters.units import format_weight, format_volume


class TestFormatWeight:
    """Tests pour format_weight"""

    def test_format_weight_none(self):
        """Test avec None"""
        assert format_weight(None) == "0 g"

    def test_format_weight_zero(self):
        """Test avec 0"""
        assert format_weight(0) == "0 g"

    def test_format_weight_grams(self):
        """Test grammes"""
        result = format_weight(500)
        assert "500" in result
        assert "g" in result

    def test_format_weight_one_kg(self):
        """Test 1 kg"""
        result = format_weight(1000)
        assert "1" in result
        assert "kg" in result

    def test_format_weight_kg_decimal(self):
        """Test kg décimal"""
        result = format_weight(1500)
        assert "1.5" in result
        assert "kg" in result

    def test_format_weight_small(self):
        """Test petite quantité"""
        result = format_weight(50)
        assert "50" in result
        assert "g" in result

    def test_format_weight_invalid(self):
        """Test valeur invalide"""
        assert format_weight("invalid") == "0 g"


class TestFormatVolume:
    """Tests pour format_volume"""

    def test_format_volume_none(self):
        """Test avec None"""
        assert format_volume(None) == "0 mL"

    def test_format_volume_zero(self):
        """Test avec 0"""
        assert format_volume(0) == "0 mL"

    def test_format_volume_milliliters(self):
        """Test millilitres"""
        result = format_volume(500)
        assert "500" in result
        assert "mL" in result

    def test_format_volume_one_liter(self):
        """Test 1 litre"""
        result = format_volume(1000)
        assert "1" in result
        assert "L" in result

    def test_format_volume_liter_decimal(self):
        """Test litre décimal"""
        result = format_volume(1500)
        assert "1.5" in result
        assert "L" in result

    def test_format_volume_small(self):
        """Test petite quantité"""
        result = format_volume(50)
        assert "50" in result
        assert "mL" in result

    def test_format_volume_invalid(self):
        """Test valeur invalide"""
        assert format_volume("invalid") == "0 mL"

