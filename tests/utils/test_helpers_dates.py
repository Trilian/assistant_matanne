"""
Tests pour src/utils/helpers/dates.py
"""
import pytest
from datetime import date, timedelta
from src.utils.helpers.dates import (
    get_week_bounds,
    date_range,
    get_month_bounds,
    add_business_days,
    weeks_between,
    is_weekend,
)


class TestGetWeekBounds:
    """Tests pour get_week_bounds."""

    def test_week_bounds_wednesday(self):
        """Trouve les bornes depuis un mercredi."""
        d = date(2025, 1, 8)  # Mercredi
        monday, sunday = get_week_bounds(d)
        assert monday == date(2025, 1, 6)
        assert sunday == date(2025, 1, 12)

    def test_week_bounds_monday(self):
        """Lundi retourne lui-même comme début."""
        d = date(2025, 1, 6)  # Lundi
        monday, sunday = get_week_bounds(d)
        assert monday == d
        assert monday.weekday() == 0

    def test_week_bounds_sunday(self):
        """Dimanche retourne lui-même comme fin."""
        d = date(2025, 1, 12)  # Dimanche
        monday, sunday = get_week_bounds(d)
        assert sunday == d
        assert sunday.weekday() == 6


class TestDateRange:
    """Tests pour date_range."""

    def test_date_range_basic(self):
        """Génère une plage de dates."""
        result = date_range(date(2025, 1, 1), date(2025, 1, 3))
        assert len(result) == 3
        assert result[0] == date(2025, 1, 1)
        assert result[-1] == date(2025, 1, 3)

    def test_date_range_same_day(self):
        """Même jour = liste avec un élément."""
        d = date(2025, 1, 1)
        result = date_range(d, d)
        assert len(result) == 1
        assert result[0] == d

    def test_date_range_week(self):
        """Plage d'une semaine."""
        result = date_range(date(2025, 1, 6), date(2025, 1, 12))
        assert len(result) == 7


class TestGetMonthBounds:
    """Tests pour get_month_bounds."""

    def test_month_bounds_february(self):
        """Février non-bissextile."""
        first, last = get_month_bounds(date(2025, 2, 15))
        assert first == date(2025, 2, 1)
        assert last == date(2025, 2, 28)

    def test_month_bounds_february_leap(self):
        """Février bissextile."""
        first, last = get_month_bounds(date(2024, 2, 15))
        assert last == date(2024, 2, 29)

    def test_month_bounds_january(self):
        """Janvier = 31 jours."""
        first, last = get_month_bounds(date(2025, 1, 15))
        assert first == date(2025, 1, 1)
        assert last == date(2025, 1, 31)

    def test_month_bounds_december(self):
        """Décembre passe à l'année suivante."""
        first, last = get_month_bounds(date(2025, 12, 15))
        assert first == date(2025, 12, 1)
        assert last == date(2025, 12, 31)


class TestAddBusinessDays:
    """Tests pour add_business_days."""

    def test_add_business_days_no_weekend(self):
        """Ajoute jours sans traverser weekend."""
        result = add_business_days(date(2025, 1, 6), 3)  # Lundi + 3
        assert result == date(2025, 1, 9)  # Jeudi

    def test_add_business_days_over_weekend(self):
        """Ajoute jours en traversant weekend."""
        result = add_business_days(date(2025, 1, 6), 5)  # Lundi + 5
        assert result == date(2025, 1, 13)  # Lundi suivant

    def test_add_business_days_from_friday(self):
        """Vendredi + 1 = Lundi."""
        result = add_business_days(date(2025, 1, 10), 1)  # Vendredi
        assert result == date(2025, 1, 13)  # Lundi


class TestWeeksBetween:
    """Tests pour weeks_between."""

    def test_weeks_between_exact(self):
        """Semaines exactes."""
        assert weeks_between(date(2025, 1, 1), date(2025, 1, 15)) == 2

    def test_weeks_between_zero(self):
        """Même semaine = 0."""
        assert weeks_between(date(2025, 1, 1), date(2025, 1, 3)) == 0

    def test_weeks_between_one_week(self):
        """Une semaine exacte."""
        assert weeks_between(date(2025, 1, 1), date(2025, 1, 8)) == 1


class TestIsWeekend:
    """Tests pour is_weekend."""

    def test_is_weekend_saturday(self):
        """Samedi = weekend."""
        assert is_weekend(date(2025, 1, 11)) is True

    def test_is_weekend_sunday(self):
        """Dimanche = weekend."""
        assert is_weekend(date(2025, 1, 12)) is True

    def test_is_weekend_monday(self):
        """Lundi = pas weekend."""
        assert is_weekend(date(2025, 1, 6)) is False

    def test_is_weekend_friday(self):
        """Vendredi = pas weekend."""
        assert is_weekend(date(2025, 1, 10)) is False
