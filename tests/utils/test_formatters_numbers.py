"""
Tests pour les formatters de nombres
"""

import pytest

from src.utils.formatters.numbers import (
    format_quantity,
    format_quantity_with_unit,
    format_price,
    format_currency,
    format_percentage,
    format_number,
    format_file_size,
    format_range,
    smart_round,
)


class TestFormatQuantity:
    """Tests pour format_quantity"""

    def test_format_quantity_none(self):
        """Test avec None"""
        assert format_quantity(None) == "0"

    def test_format_quantity_zero(self):
        """Test avec 0"""
        assert format_quantity(0) == "0"

    def test_format_quantity_integer(self):
        """Test entier"""
        assert format_quantity(5) == "5"

    def test_format_quantity_float_whole(self):
        """Test float entier"""
        assert format_quantity(5.0) == "5"

    def test_format_quantity_float_decimal(self):
        """Test float décimal"""
        assert format_quantity(2.5) == "2.5"

    def test_format_quantity_long_decimal(self):
        """Test float long"""
        result = format_quantity(2.123)
        assert result == "2.12"

    def test_format_quantity_custom_decimals(self):
        """Test avec décimales personnalisées"""
        result = format_quantity(2.12345, decimals=3)
        assert result == "2.123"

    def test_format_quantity_invalid(self):
        """Test valeur invalide"""
        assert format_quantity("invalid") == "0"


class TestFormatQuantityWithUnit:
    """Tests pour format_quantity_with_unit"""

    def test_format_quantity_with_unit_basic(self):
        """Test basique"""
        result = format_quantity_with_unit(2.5, "kg")
        assert result == "2.5 kg"

    def test_format_quantity_with_unit_no_unit(self):
        """Test sans unité"""
        result = format_quantity_with_unit(2.5, "")
        assert result == "2.5"

    def test_format_quantity_with_unit_none_unit(self):
        """Test unité None"""
        result = format_quantity_with_unit(2.5, None)
        assert result == "2.5"

    def test_format_quantity_with_unit_integer(self):
        """Test entier"""
        result = format_quantity_with_unit(3, "pièces")
        assert result == "3 pièces"


class TestFormatPrice:
    """Tests pour format_price"""

    def test_format_price_none(self):
        """Test avec None"""
        assert format_price(None) == "0â‚¬"

    def test_format_price_integer(self):
        """Test prix entier"""
        assert format_price(10) == "10â‚¬"

    def test_format_price_float_whole(self):
        """Test prix float entier"""
        assert format_price(10.0) == "10â‚¬"

    def test_format_price_decimal(self):
        """Test prix décimal"""
        assert format_price(10.50) == "10.50â‚¬"

    def test_format_price_custom_currency(self):
        """Test devise personnalisée"""
        assert format_price(10, "$") == "10$"

    def test_format_price_invalid(self):
        """Test valeur invalide"""
        assert format_price("invalid") == "0â‚¬"


class TestFormatCurrency:
    """Tests pour format_currency"""

    def test_format_currency_french(self):
        """Test format français"""
        result = format_currency(1234.56, "EUR", "fr_FR")
        assert "â‚¬" in result
        assert " " in result  # Séparateur milliers

    def test_format_currency_english(self):
        """Test format anglais"""
        result = format_currency(1234.56, "USD", "en_US")
        assert "$" in result

    def test_format_currency_none(self):
        """Test avec None"""
        result = format_currency(None)
        assert "â‚¬" in result

    def test_format_currency_gbp(self):
        """Test livre sterling"""
        result = format_currency(100, "GBP", "fr_FR")
        assert "Â£" in result


class TestFormatPercentage:
    """Tests pour format_percentage"""

    def test_format_percentage_none(self):
        """Test avec None"""
        assert format_percentage(None) == "0%"

    def test_format_percentage_integer(self):
        """Test entier"""
        assert format_percentage(85) == "85%"

    def test_format_percentage_float_whole(self):
        """Test float entier"""
        assert format_percentage(85.0) == "85%"

    def test_format_percentage_decimal(self):
        """Test décimal"""
        result = format_percentage(85.5)
        assert "85.5%" == result or "85,5%" in result

    def test_format_percentage_custom_decimals(self):
        """Test décimales personnalisées"""
        result = format_percentage(85.567, decimals=2)
        assert "85.57%" == result or "85,57" in result

    def test_format_percentage_invalid(self):
        """Test valeur invalide"""
        assert format_percentage("invalid") == "0%"


class TestFormatNumber:
    """Tests pour format_number"""

    def test_format_number_none(self):
        """Test avec None"""
        assert format_number(None) == "0"

    def test_format_number_simple(self):
        """Test nombre simple"""
        assert format_number(123) == "123"

    def test_format_number_thousands(self):
        """Test avec séparateurs milliers"""
        result = format_number(1234567)
        assert "1 234 567" == result

    def test_format_number_decimals(self):
        """Test avec décimales"""
        result = format_number(1234.56, decimals=2)
        assert "1 234" in result

    def test_format_number_invalid(self):
        """Test valeur invalide"""
        assert format_number("invalid") == "0"


class TestFormatFileSize:
    """Tests pour format_file_size"""

    def test_format_file_size_none(self):
        """Test avec None"""
        assert format_file_size(None) == "0 o"

    def test_format_file_size_zero(self):
        """Test avec 0"""
        assert format_file_size(0) == "0 o"

    def test_format_file_size_bytes(self):
        """Test octets"""
        result = format_file_size(500)
        assert "500" in result
        assert "o" in result

    def test_format_file_size_kilobytes(self):
        """Test Ko"""
        result = format_file_size(1024)
        assert "Ko" in result

    def test_format_file_size_megabytes(self):
        """Test Mo"""
        result = format_file_size(1048576)
        assert "Mo" in result

    def test_format_file_size_gigabytes(self):
        """Test Go"""
        result = format_file_size(1073741824)
        assert "Go" in result

    def test_format_file_size_invalid(self):
        """Test valeur invalide"""
        assert format_file_size("invalid") == "0 o"


class TestFormatRange:
    """Tests pour format_range"""

    def test_format_range_basic(self):
        """Test basique"""
        result = format_range(10, 20)
        assert "10-20" == result

    def test_format_range_with_unit(self):
        """Test avec unité"""
        result = format_range(10, 20, "â‚¬")
        assert "10-20 â‚¬" == result

    def test_format_range_decimals(self):
        """Test avec décimales"""
        result = format_range(10.5, 20.5)
        assert "10.5-20.5" == result


class TestSmartRound:
    """Tests pour smart_round"""

    def test_smart_round_basic(self):
        """Test basique"""
        assert smart_round(2.5) == 2.5

    def test_smart_round_float_error(self):
        """Test erreur de float"""
        result = smart_round(2.5000000001)
        assert result == 2.5

    def test_smart_round_precision(self):
        """Test précision personnalisée"""
        result = smart_round(2.12345, precision=3)
        assert result == 2.123

    def test_smart_round_none(self):
        """Test avec None"""
        assert smart_round(None) == 0.0

    def test_smart_round_invalid(self):
        """Test valeur invalide"""
        assert smart_round("invalid") == 0.0

