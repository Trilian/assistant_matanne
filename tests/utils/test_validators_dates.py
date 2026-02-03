"""
Tests pour src/utils/validators/dates.py
"""
import pytest
from datetime import date, timedelta
from src.utils.validators.dates import (
    validate_date_range,
    is_future_date,
    is_past_date,
    validate_expiry_date,
    days_until,
    is_within_days,
)


class TestValidateDateRange:
    """Tests pour validate_date_range (retourne tuple[bool, str])."""

    def test_validate_range_valid(self):
        """Plage valide (start < end)."""
        is_valid, msg = validate_date_range(date(2025, 1, 1), date(2025, 1, 31))
        assert is_valid is True
        assert msg == ""

    def test_validate_range_same_day(self):
        """Même jour = valide."""
        d = date(2025, 1, 1)
        is_valid, msg = validate_date_range(d, d)
        assert is_valid is True

    def test_validate_range_invalid(self):
        """Start > end = invalide."""
        is_valid, msg = validate_date_range(date(2025, 1, 31), date(2025, 1, 1))
        assert is_valid is False


class TestIsFutureDate:
    """Tests pour is_future_date."""

    def test_is_future_date_tomorrow(self):
        """Demain = futur."""
        tomorrow = date.today() + timedelta(days=1)
        assert is_future_date(tomorrow) is True

    def test_is_future_date_today(self):
        """Aujourd'hui = pas futur."""
        assert is_future_date(date.today()) is False

    def test_is_future_date_yesterday(self):
        """Hier = pas futur."""
        yesterday = date.today() - timedelta(days=1)
        assert is_future_date(yesterday) is False

    def test_is_future_date_next_year(self):
        """Année prochaine = futur."""
        next_year = date(date.today().year + 1, 1, 1)
        assert is_future_date(next_year) is True


class TestIsPastDate:
    """Tests pour is_past_date."""

    def test_is_past_date_yesterday(self):
        """Hier = passé."""
        yesterday = date.today() - timedelta(days=1)
        assert is_past_date(yesterday) is True

    def test_is_past_date_today(self):
        """Aujourd'hui = pas passé."""
        assert is_past_date(date.today()) is False

    def test_is_past_date_tomorrow(self):
        """Demain = pas passé."""
        tomorrow = date.today() + timedelta(days=1)
        assert is_past_date(tomorrow) is False


class TestValidateExpiryDate:
    """Tests pour validate_expiry_date (retourne tuple[bool, str])."""

    def test_validate_expiry_future(self):
        """Date future = valide."""
        future = date.today() + timedelta(days=30)
        is_valid, msg = validate_expiry_date(future)
        assert is_valid is True

    def test_validate_expiry_today(self):
        """Aujourd'hui avec min_days_ahead=1 = invalide."""
        is_valid, msg = validate_expiry_date(date.today())
        assert is_valid is False  # Doit être au moins 1 jour dans le futur

    def test_validate_expiry_past(self):
        """Date passée = expiré."""
        past = date.today() - timedelta(days=1)
        is_valid, msg = validate_expiry_date(past)
        assert is_valid is False


class TestDaysUntil:
    """Tests pour days_until."""

    def test_days_until_tomorrow(self):
        """Jours jusqu'à demain = 1."""
        tomorrow = date.today() + timedelta(days=1)
        assert days_until(tomorrow) == 1

    def test_days_until_next_week(self):
        """Jours jusqu'à semaine prochaine = 7."""
        next_week = date.today() + timedelta(days=7)
        assert days_until(next_week) == 7

    def test_days_until_today(self):
        """Jours jusqu'à aujourd'hui = 0."""
        assert days_until(date.today()) == 0

    def test_days_until_past(self):
        """Jours jusqu'à date passée = négatif."""
        yesterday = date.today() - timedelta(days=1)
        assert days_until(yesterday) == -1


class TestIsWithinDays:
    """Tests pour is_within_days."""

    def test_is_within_days_true(self):
        """Date dans les N jours."""
        target = date.today() + timedelta(days=3)
        assert is_within_days(target, 5) is True

    def test_is_within_days_false(self):
        """Date hors des N jours."""
        target = date.today() + timedelta(days=10)
        assert is_within_days(target, 5) is False

    def test_is_within_days_exact(self):
        """Date exactement à N jours."""
        target = date.today() + timedelta(days=5)
        assert is_within_days(target, 5) is True

    def test_is_within_days_today(self):
        """Aujourd'hui = dans les N jours."""
        assert is_within_days(date.today(), 5) is True

    def test_is_within_days_past(self):
        """Date passée = pas dans les N jours futurs."""
        yesterday = date.today() - timedelta(days=1)
        assert is_within_days(yesterday, 5) is False
