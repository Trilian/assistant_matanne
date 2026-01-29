"""
Tests pour src/utils/formatters/ - dates, numbers, text, units
Ces tests couvrent ~230 statements de fonctions pures
"""

import pytest
from datetime import date, datetime, timedelta


# =============================================================================
# Tests formatters/dates.py (~83 statements)
# =============================================================================

class TestFormatDate:
    """Tests pour format_date"""
    
    def test_format_date_none(self):
        from src.utils.formatters.dates import format_date
        assert format_date(None) == "â€”"
    
    def test_format_date_short(self):
        from src.utils.formatters.dates import format_date
        d = date(2025, 12, 1)
        assert format_date(d, "short") == "01/12"
    
    def test_format_date_medium(self):
        from src.utils.formatters.dates import format_date
        d = date(2025, 12, 1)
        assert format_date(d, "medium") == "01/12/2025"
    
    def test_format_date_long_fr(self):
        from src.utils.formatters.dates import format_date
        d = date(2025, 12, 1)
        assert format_date(d, "long", "fr") == "1 décembre 2025"
    
    def test_format_date_long_en(self):
        from src.utils.formatters.dates import format_date
        d = date(2025, 12, 1)
        result = format_date(d, "long", "en")
        assert "2025" in result
    
    def test_format_date_from_datetime(self):
        from src.utils.formatters.dates import format_date
        dt = datetime(2025, 12, 1, 14, 30)
        assert format_date(dt, "short") == "01/12"
    
    def test_format_date_unknown_format(self):
        from src.utils.formatters.dates import format_date
        d = date(2025, 12, 1)
        assert format_date(d, "unknown") == "01/12/2025"
    
    def test_format_date_all_months_fr(self):
        """Teste tous les mois en français"""
        from src.utils.formatters.dates import format_date
        months = [
            "janvier", "février", "mars", "avril", "mai", "juin",
            "juillet", "août", "septembre", "octobre", "novembre", "décembre"
        ]
        for i, month_name in enumerate(months, 1):
            d = date(2025, i, 15)
            result = format_date(d, "long", "fr")
            assert month_name in result


class TestFormatDatetime:
    """Tests pour format_datetime"""
    
    def test_format_datetime_none(self):
        from src.utils.formatters.dates import format_datetime
        assert format_datetime(None) == "â€”"
    
    def test_format_datetime_short(self):
        from src.utils.formatters.dates import format_datetime
        dt = datetime(2025, 12, 1, 14, 30)
        assert format_datetime(dt, "short") == "01/12 14:30"
    
    def test_format_datetime_medium(self):
        from src.utils.formatters.dates import format_datetime
        dt = datetime(2025, 12, 1, 14, 30)
        assert format_datetime(dt, "medium") == "01/12/2025 14:30"
    
    def test_format_datetime_long(self):
        from src.utils.formatters.dates import format_datetime
        dt = datetime(2025, 12, 1, 14, 30)
        result = format_datetime(dt, "long", "fr")
        assert "1 décembre 2025" in result
        assert "14:30" in result
    
    def test_format_datetime_unknown(self):
        from src.utils.formatters.dates import format_datetime
        dt = datetime(2025, 12, 1, 14, 30)
        assert format_datetime(dt, "unknown") == "01/12/2025 14:30"


class TestFormatRelativeDate:
    """Tests pour format_relative_date"""
    
    def test_today(self):
        from src.utils.formatters.dates import format_relative_date
        assert format_relative_date(date.today()) == "Aujourd'hui"
    
    def test_tomorrow(self):
        from src.utils.formatters.dates import format_relative_date
        tomorrow = date.today() + timedelta(days=1)
        assert format_relative_date(tomorrow) == "Demain"
    
    def test_yesterday(self):
        from src.utils.formatters.dates import format_relative_date
        yesterday = date.today() - timedelta(days=1)
        assert format_relative_date(yesterday) == "Hier"
    
    def test_in_few_days(self):
        from src.utils.formatters.dates import format_relative_date
        in_3_days = date.today() + timedelta(days=3)
        assert format_relative_date(in_3_days) == "Dans 3 jours"
    
    def test_few_days_ago(self):
        from src.utils.formatters.dates import format_relative_date
        days_ago = date.today() - timedelta(days=3)
        assert format_relative_date(days_ago) == "Il y a 3 jours"
    
    def test_far_future(self):
        from src.utils.formatters.dates import format_relative_date
        far = date.today() + timedelta(days=30)
        result = format_relative_date(far)
        assert "/" in result  # format medium
    
    def test_far_past(self):
        from src.utils.formatters.dates import format_relative_date
        far = date.today() - timedelta(days=30)
        result = format_relative_date(far)
        assert "/" in result
    
    def test_from_datetime(self):
        from src.utils.formatters.dates import format_relative_date
        dt = datetime.now()
        assert format_relative_date(dt) == "Aujourd'hui"


class TestFormatTime:
    """Tests pour format_time (durée en minutes)"""
    
    def test_format_time_none(self):
        from src.utils.formatters.dates import format_time
        assert format_time(None) == "0min"
    
    def test_format_time_zero(self):
        from src.utils.formatters.dates import format_time
        assert format_time(0) == "0min"
    
    def test_format_time_minutes_only(self):
        from src.utils.formatters.dates import format_time
        assert format_time(45) == "45min"
    
    def test_format_time_hours_only(self):
        from src.utils.formatters.dates import format_time
        assert format_time(120) == "2h"
    
    def test_format_time_hours_and_minutes(self):
        from src.utils.formatters.dates import format_time
        assert format_time(90) == "1h30"
    
    def test_format_time_invalid(self):
        from src.utils.formatters.dates import format_time
        assert format_time("invalid") == "0min"


class TestFormatDuration:
    """Tests pour format_duration (durée en secondes)"""
    
    def test_format_duration_none(self):
        from src.utils.formatters.dates import format_duration
        assert format_duration(None) == "0 seconde"
        assert format_duration(None, short=True) == "0s"
    
    def test_format_duration_zero(self):
        from src.utils.formatters.dates import format_duration
        assert format_duration(0) == "0 seconde"
    
    def test_format_duration_seconds_only(self):
        from src.utils.formatters.dates import format_duration
        assert format_duration(45) == "45 secondes"
        assert format_duration(45, short=True) == "45s"
    
    def test_format_duration_one_second(self):
        from src.utils.formatters.dates import format_duration
        assert format_duration(1) == "1 seconde"
    
    def test_format_duration_minutes(self):
        from src.utils.formatters.dates import format_duration
        assert format_duration(120) == "2 minutes"
        assert format_duration(120, short=True) == "2min"
    
    def test_format_duration_one_minute(self):
        from src.utils.formatters.dates import format_duration
        assert format_duration(60) == "1 minute"
    
    def test_format_duration_hours(self):
        from src.utils.formatters.dates import format_duration
        assert format_duration(7200) == "2 heures"
        assert format_duration(7200, short=True) == "2h"
    
    def test_format_duration_one_hour(self):
        from src.utils.formatters.dates import format_duration
        assert format_duration(3600) == "1 heure"
    
    def test_format_duration_complex(self):
        from src.utils.formatters.dates import format_duration
        # 1h 1min 5s = 3665 seconds
        result = format_duration(3665, short=True)
        assert "1h" in result
        assert "1min" in result
        assert "5s" in result
    
    def test_format_duration_invalid(self):
        from src.utils.formatters.dates import format_duration
        assert format_duration("invalid") == "0s"


# =============================================================================
# Tests formatters/numbers.py (~90 statements)
# =============================================================================

class TestFormatQuantity:
    """Tests pour format_quantity"""
    
    def test_format_quantity_none(self):
        from src.utils.formatters.numbers import format_quantity
        assert format_quantity(None) == "0"
    
    def test_format_quantity_zero(self):
        from src.utils.formatters.numbers import format_quantity
        assert format_quantity(0) == "0"
    
    def test_format_quantity_integer(self):
        from src.utils.formatters.numbers import format_quantity
        assert format_quantity(2.0) == "2"
    
    def test_format_quantity_decimal(self):
        from src.utils.formatters.numbers import format_quantity
        assert format_quantity(2.5) == "2.5"
    
    def test_format_quantity_rounded(self):
        from src.utils.formatters.numbers import format_quantity
        assert format_quantity(2.123) == "2.12"
    
    def test_format_quantity_invalid(self):
        from src.utils.formatters.numbers import format_quantity
        assert format_quantity("invalid") == "0"


class TestFormatQuantityWithUnit:
    """Tests pour format_quantity_with_unit"""
    
    def test_with_unit(self):
        from src.utils.formatters.numbers import format_quantity_with_unit
        assert format_quantity_with_unit(2.5, "kg") == "2.5 kg"
    
    def test_without_unit(self):
        from src.utils.formatters.numbers import format_quantity_with_unit
        assert format_quantity_with_unit(2.5, "") == "2.5"
    
    def test_unit_with_spaces(self):
        from src.utils.formatters.numbers import format_quantity_with_unit
        assert format_quantity_with_unit(2.5, "  kg  ") == "2.5 kg"


class TestFormatPrice:
    """Tests pour format_price"""
    
    def test_format_price_none(self):
        from src.utils.formatters.numbers import format_price
        assert format_price(None) == "0â‚¬"
    
    def test_format_price_integer(self):
        from src.utils.formatters.numbers import format_price
        assert format_price(10.0) == "10â‚¬"
    
    def test_format_price_decimal(self):
        from src.utils.formatters.numbers import format_price
        assert format_price(10.50) == "10.50â‚¬"
    
    def test_format_price_invalid(self):
        from src.utils.formatters.numbers import format_price
        assert format_price("invalid") == "0â‚¬"
    
    def test_format_price_custom_currency(self):
        from src.utils.formatters.numbers import format_price
        assert format_price(10, "$") == "10$"


class TestFormatCurrency:
    """Tests pour format_currency"""
    
    def test_format_currency_none(self):
        from src.utils.formatters.numbers import format_currency
        result = format_currency(None)
        assert "0" in result
    
    def test_format_currency_fr(self):
        from src.utils.formatters.numbers import format_currency
        result = format_currency(1234.56, "EUR", "fr_FR")
        assert "â‚¬" in result
        assert "234" in result  # milliers séparés
    
    def test_format_currency_en(self):
        from src.utils.formatters.numbers import format_currency
        result = format_currency(1234.56, "USD", "en_US")
        assert "$" in result
    
    def test_format_currency_invalid(self):
        from src.utils.formatters.numbers import format_currency
        result = format_currency("invalid")
        assert "0" in result


class TestFormatPercentage:
    """Tests pour format_percentage"""
    
    def test_format_percentage_none(self):
        from src.utils.formatters.numbers import format_percentage
        assert format_percentage(None) == "0%"
    
    def test_format_percentage_integer(self):
        from src.utils.formatters.numbers import format_percentage
        assert format_percentage(85.0) == "85%"
    
    def test_format_percentage_decimal(self):
        from src.utils.formatters.numbers import format_percentage
        assert format_percentage(85.5) == "85.5%"
    
    def test_format_percentage_invalid(self):
        from src.utils.formatters.numbers import format_percentage
        assert format_percentage("invalid") == "0%"


class TestFormatNumber:
    """Tests pour format_number"""
    
    def test_format_number_none(self):
        from src.utils.formatters.numbers import format_number
        assert format_number(None) == "0"
    
    def test_format_number_thousands(self):
        from src.utils.formatters.numbers import format_number
        result = format_number(1234567)
        assert " " in result  # séparateur de milliers
        assert "234" in result
    
    def test_format_number_decimals(self):
        from src.utils.formatters.numbers import format_number
        result = format_number(1234.56, decimals=2)
        assert "," in result  # virgule décimale française
    
    def test_format_number_invalid(self):
        from src.utils.formatters.numbers import format_number
        assert format_number("invalid") == "0"


class TestFormatFileSize:
    """Tests pour format_file_size"""
    
    def test_format_file_size_none(self):
        from src.utils.formatters.numbers import format_file_size
        assert format_file_size(None) == "0 o"
    
    def test_format_file_size_zero(self):
        from src.utils.formatters.numbers import format_file_size
        assert format_file_size(0) == "0 o"
    
    def test_format_file_size_bytes(self):
        from src.utils.formatters.numbers import format_file_size
        assert format_file_size(500) == "500 o"
    
    def test_format_file_size_kilobytes(self):
        from src.utils.formatters.numbers import format_file_size
        assert format_file_size(1024) == "1 Ko"
    
    def test_format_file_size_megabytes(self):
        from src.utils.formatters.numbers import format_file_size
        assert format_file_size(1048576) == "1 Mo"
    
    def test_format_file_size_gigabytes(self):
        from src.utils.formatters.numbers import format_file_size
        result = format_file_size(1073741824)
        assert "Go" in result
    
    def test_format_file_size_invalid(self):
        from src.utils.formatters.numbers import format_file_size
        assert format_file_size("invalid") == "0 o"


class TestFormatRange:
    """Tests pour format_range"""
    
    def test_format_range_without_unit(self):
        from src.utils.formatters.numbers import format_range
        assert format_range(10, 20) == "10-20"
    
    def test_format_range_with_unit(self):
        from src.utils.formatters.numbers import format_range
        assert format_range(10, 20, "â‚¬") == "10-20 â‚¬"


class TestSmartRound:
    """Tests pour smart_round"""
    
    def test_smart_round_normal(self):
        from src.utils.formatters.numbers import smart_round
        assert smart_round(2.5000000001) == 2.5
    
    def test_smart_round_none(self):
        from src.utils.formatters.numbers import smart_round
        assert smart_round(None) == 0.0
    
    def test_smart_round_invalid(self):
        from src.utils.formatters.numbers import smart_round
        assert smart_round("invalid") == 0.0


# =============================================================================
# Tests formatters/text.py (~31 statements)
# =============================================================================

class TestTruncate:
    """Tests pour truncate"""
    
    def test_truncate_short_text(self):
        from src.utils.formatters.text import truncate
        assert truncate("Hello", 10) == "Hello"
    
    def test_truncate_long_text(self):
        from src.utils.formatters.text import truncate
        result = truncate("Un texte très long qui dépasse", 15)
        assert len(result) <= 15
        assert result.endswith("...")
    
    def test_truncate_custom_suffix(self):
        from src.utils.formatters.text import truncate
        result = truncate("Un texte long", 10, suffix="â€¦")
        assert result.endswith("â€¦")


class TestCleanText:
    """Tests pour clean_text"""
    
    def test_clean_text_xss(self):
        from src.utils.formatters.text import clean_text
        result = clean_text("<script>alert('xss')</script>")
        assert "<" not in result
        assert ">" not in result
    
    def test_clean_text_empty(self):
        from src.utils.formatters.text import clean_text
        assert clean_text("") == ""
    
    def test_clean_text_curly_braces(self):
        from src.utils.formatters.text import clean_text
        result = clean_text("{test}")
        assert "{" not in result
        assert "}" not in result


class TestSlugify:
    """Tests pour slugify"""
    
    def test_slugify_simple(self):
        from src.utils.formatters.text import slugify
        assert slugify("Tarte aux Pommes") == "tarte-aux-pommes"
    
    def test_slugify_accents(self):
        from src.utils.formatters.text import slugify
        result = slugify("Café Crème")
        assert "é" not in result
        assert "è" not in result


class TestExtractNumber:
    """Tests pour extract_number"""
    
    def test_extract_number_simple(self):
        from src.utils.formatters.text import extract_number
        assert extract_number("2.5 kg") == 2.5
    
    def test_extract_number_french(self):
        from src.utils.formatters.text import extract_number
        assert extract_number("Prix: 10,50â‚¬") == 10.5
    
    def test_extract_number_empty(self):
        from src.utils.formatters.text import extract_number
        assert extract_number("") is None
    
    def test_extract_number_no_number(self):
        from src.utils.formatters.text import extract_number
        assert extract_number("no number here") is None
    
    def test_extract_number_negative(self):
        from src.utils.formatters.text import extract_number
        assert extract_number("-5 degrés") == -5


class TestCapitalizeFirst:
    """Tests pour capitalize_first"""
    
    def test_capitalize_first_normal(self):
        from src.utils.formatters.text import capitalize_first
        assert capitalize_first("tomate") == "Tomate"
    
    def test_capitalize_first_empty(self):
        from src.utils.formatters.text import capitalize_first
        assert capitalize_first("") == ""
    
    def test_capitalize_first_uppercase(self):
        from src.utils.formatters.text import capitalize_first
        assert capitalize_first("TOMATE") == "Tomate"

