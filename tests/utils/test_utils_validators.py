"""
Tests pour src/utils/validators/ - common, dates
Ces tests couvrent ~67 statements de fonctions de validation utilitaires
"""

import pytest
from datetime import date, timedelta


# =============================================================================
# Tests validators/common.py (~41 statements)
# =============================================================================

class TestIsValidEmail:
    """Tests pour is_valid_email"""
    
    def test_valid_email(self):
        from src.utils.validators.common import is_valid_email
        assert is_valid_email("test@example.com") is True
    
    def test_invalid_email_no_at(self):
        from src.utils.validators.common import is_valid_email
        assert is_valid_email("invalid") is False
    
    def test_invalid_email_no_domain(self):
        from src.utils.validators.common import is_valid_email
        assert is_valid_email("test@") is False
    
    def test_invalid_email_no_tld(self):
        from src.utils.validators.common import is_valid_email
        assert is_valid_email("test@example") is False


class TestIsValidPhone:
    """Tests pour is_valid_phone"""
    
    def test_valid_phone_fr(self):
        from src.utils.validators.common import is_valid_phone
        assert is_valid_phone("0612345678") is True
    
    def test_valid_phone_fr_with_prefix(self):
        from src.utils.validators.common import is_valid_phone
        assert is_valid_phone("+33612345678") is True
    
    def test_invalid_phone(self):
        from src.utils.validators.common import is_valid_phone
        assert is_valid_phone("123") is False
    
    def test_phone_other_country(self):
        from src.utils.validators.common import is_valid_phone
        # Non-FR country returns False with current implementation
        assert is_valid_phone("123", country="US") is False


class TestClamp:
    """Tests pour clamp"""
    
    def test_clamp_above_max(self):
        from src.utils.validators.common import clamp
        assert clamp(15, 0, 10) == 10
    
    def test_clamp_below_min(self):
        from src.utils.validators.common import clamp
        assert clamp(-5, 0, 10) == 0
    
    def test_clamp_in_range(self):
        from src.utils.validators.common import clamp
        assert clamp(5, 0, 10) == 5
    
    def test_clamp_at_min(self):
        from src.utils.validators.common import clamp
        assert clamp(0, 0, 10) == 0
    
    def test_clamp_at_max(self):
        from src.utils.validators.common import clamp
        assert clamp(10, 0, 10) == 10


class TestValidateRange:
    """Tests pour validate_range"""
    
    def test_validate_range_valid(self):
        from src.utils.validators.common import validate_range
        is_valid, msg = validate_range(5, 0, 10)
        assert is_valid is True
        assert msg == ""
    
    def test_validate_range_below_min(self):
        from src.utils.validators.common import validate_range
        is_valid, msg = validate_range(-5, 0, 10)
        assert is_valid is False
        assert ">=" in msg
    
    def test_validate_range_above_max(self):
        from src.utils.validators.common import validate_range
        is_valid, msg = validate_range(15, 0, 10)
        assert is_valid is False
        assert "<=" in msg
    
    def test_validate_range_invalid_type(self):
        from src.utils.validators.common import validate_range
        is_valid, msg = validate_range("invalid", 0, 10)
        assert is_valid is False
        assert "nombre" in msg
    
    def test_validate_range_no_limits(self):
        from src.utils.validators.common import validate_range
        is_valid, msg = validate_range(100)
        assert is_valid is True


class TestValidateStringLength:
    """Tests pour validate_string_length"""
    
    def test_validate_string_valid(self):
        from src.utils.validators.common import validate_string_length
        is_valid, msg = validate_string_length("hello", min_length=1, max_length=10)
        assert is_valid is True
    
    def test_validate_string_too_short(self):
        from src.utils.validators.common import validate_string_length
        is_valid, msg = validate_string_length("hi", min_length=5)
        assert is_valid is False
        assert "au moins" in msg
    
    def test_validate_string_too_long(self):
        from src.utils.validators.common import validate_string_length
        is_valid, msg = validate_string_length("hello world", max_length=5)
        assert is_valid is False
        assert "maximum" in msg
    
    def test_validate_string_not_string(self):
        from src.utils.validators.common import validate_string_length
        is_valid, msg = validate_string_length(123)
        assert is_valid is False
        assert "texte" in msg


class TestValidateRequiredFields:
    """Tests pour validate_required_fields"""
    
    def test_all_present(self):
        from src.utils.validators.common import validate_required_fields
        data = {"nom": "Test", "email": "test@test.com"}
        is_valid, missing = validate_required_fields(data, ["nom", "email"])
        assert is_valid is True
        assert missing == []
    
    def test_missing_field(self):
        from src.utils.validators.common import validate_required_fields
        data = {"nom": "Test"}
        is_valid, missing = validate_required_fields(data, ["nom", "email"])
        assert is_valid is False
        assert "email" in missing
    
    def test_empty_field(self):
        from src.utils.validators.common import validate_required_fields
        data = {"nom": "Test", "email": ""}
        is_valid, missing = validate_required_fields(data, ["nom", "email"])
        assert is_valid is False
        assert "email" in missing
    
    def test_none_field(self):
        from src.utils.validators.common import validate_required_fields
        data = {"nom": "Test", "email": None}
        is_valid, missing = validate_required_fields(data, ["nom", "email"])
        assert is_valid is False


class TestValidateChoice:
    """Tests pour validate_choice"""
    
    def test_valid_choice(self):
        from src.utils.validators.common import validate_choice
        is_valid, msg = validate_choice("A", ["A", "B", "C"])
        assert is_valid is True
    
    def test_invalid_choice(self):
        from src.utils.validators.common import validate_choice
        is_valid, msg = validate_choice("D", ["A", "B", "C"])
        assert is_valid is False


# =============================================================================
# Tests validators/dates.py (~26 statements)
# =============================================================================

class TestValidateDateRange:
    """Tests pour validate_date_range"""
    
    def test_valid_range(self):
        from src.utils.validators.dates import validate_date_range
        start = date(2025, 1, 1)
        end = date(2025, 1, 10)
        is_valid, msg = validate_date_range(start, end)
        assert is_valid is True
    
    def test_invalid_range_start_after_end(self):
        from src.utils.validators.dates import validate_date_range
        start = date(2025, 1, 10)
        end = date(2025, 1, 1)
        is_valid, msg = validate_date_range(start, end)
        assert is_valid is False
        assert "avant" in msg
    
    def test_max_days_exceeded(self):
        from src.utils.validators.dates import validate_date_range
        start = date(2025, 1, 1)
        end = date(2025, 2, 1)
        is_valid, msg = validate_date_range(start, end, max_days=7)
        assert is_valid is False
        assert "maximum" in msg


class TestIsFutureDate:
    """Tests pour is_future_date"""
    
    def test_future_date(self):
        from src.utils.validators.dates import is_future_date
        future = date.today() + timedelta(days=30)
        assert is_future_date(future) is True
    
    def test_past_date(self):
        from src.utils.validators.dates import is_future_date
        past = date.today() - timedelta(days=30)
        assert is_future_date(past) is False
    
    def test_today(self):
        from src.utils.validators.dates import is_future_date
        assert is_future_date(date.today()) is False


class TestIsPastDate:
    """Tests pour is_past_date"""
    
    def test_past_date(self):
        from src.utils.validators.dates import is_past_date
        past = date.today() - timedelta(days=30)
        assert is_past_date(past) is True
    
    def test_future_date(self):
        from src.utils.validators.dates import is_past_date
        future = date.today() + timedelta(days=30)
        assert is_past_date(future) is False
    
    def test_today(self):
        from src.utils.validators.dates import is_past_date
        assert is_past_date(date.today()) is False


class TestValidateExpiryDate:
    """Tests pour validate_expiry_date"""
    
    def test_valid_expiry(self):
        from src.utils.validators.dates import validate_expiry_date
        future = date.today() + timedelta(days=30)
        is_valid, msg = validate_expiry_date(future)
        assert is_valid is True
    
    def test_expired(self):
        from src.utils.validators.dates import validate_expiry_date
        past = date.today() - timedelta(days=1)
        is_valid, msg = validate_expiry_date(past)
        assert is_valid is False
        assert "passée" in msg
    
    def test_too_soon(self):
        from src.utils.validators.dates import validate_expiry_date
        tomorrow = date.today() + timedelta(days=1)
        is_valid, msg = validate_expiry_date(tomorrow, min_days_ahead=7)
        assert is_valid is False


class TestDaysUntil:
    """Tests pour days_until"""
    
    def test_days_until_future(self):
        from src.utils.validators.dates import days_until
        target = date.today() + timedelta(days=7)
        assert days_until(target) == 7
    
    def test_days_until_past(self):
        from src.utils.validators.dates import days_until
        target = date.today() - timedelta(days=7)
        assert days_until(target) == -7
    
    def test_days_until_today(self):
        from src.utils.validators.dates import days_until
        assert days_until(date.today()) == 0


class TestIsWithinDays:
    """Tests pour is_within_days"""
    
    def test_within_range(self):
        from src.utils.validators.dates import is_within_days
        target = date.today() + timedelta(days=3)
        assert is_within_days(target, 7) is True
    
    def test_outside_range(self):
        from src.utils.validators.dates import is_within_days
        target = date.today() + timedelta(days=10)
        assert is_within_days(target, 7) is False
    
    def test_past_date(self):
        from src.utils.validators.dates import is_within_days
        target = date.today() - timedelta(days=1)
        assert is_within_days(target, 7) is False
    
    def test_today(self):
        from src.utils.validators.dates import is_within_days
        assert is_within_days(date.today(), 7) is True
