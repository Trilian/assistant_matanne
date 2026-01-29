"""
Tests pour src/utils/helpers/dates.py - Fonctions de manipulation de dates.
"""

from datetime import date, timedelta

import pytest

from src.utils.helpers.dates import (
    add_business_days,
    date_range,
    get_month_bounds,
    get_quarter,
    get_week_bounds,
    is_weekend,
    weeks_between,
)


# ═══════════════════════════════════════════════════════════
# TESTS GET_WEEK_BOUNDS
# ═══════════════════════════════════════════════════════════


class TestGetWeekBounds:
    """Tests pour get_week_bounds."""

    def test_wednesday(self):
        """Test avec un mercredi."""
        # 8 janvier 2025 est un mercredi
        d = date(2025, 1, 8)
        monday, sunday = get_week_bounds(d)
        
        assert monday == date(2025, 1, 6)  # Lundi
        assert sunday == date(2025, 1, 12)  # Dimanche

    def test_monday(self):
        """Test avec un lundi."""
        d = date(2025, 1, 6)  # Lundi
        monday, sunday = get_week_bounds(d)
        
        assert monday == date(2025, 1, 6)
        assert sunday == date(2025, 1, 12)

    def test_sunday(self):
        """Test avec un dimanche."""
        d = date(2025, 1, 12)  # Dimanche
        monday, sunday = get_week_bounds(d)
        
        assert monday == date(2025, 1, 6)
        assert sunday == date(2025, 1, 12)

    def test_across_year(self):
        """Test semaine chevauchant l'année."""
        d = date(2025, 1, 1)  # Mercredi 1er janvier
        monday, sunday = get_week_bounds(d)
        
        assert monday == date(2024, 12, 30)  # Lundi avant
        assert sunday == date(2025, 1, 5)

    def test_february_leap_year(self):
        """Test en février année bissextile."""
        d = date(2024, 2, 29)  # Jeudi (année bissextile)
        monday, sunday = get_week_bounds(d)
        
        assert monday == date(2024, 2, 26)
        assert sunday == date(2024, 3, 3)


# ═══════════════════════════════════════════════════════════
# TESTS DATE_RANGE
# ═══════════════════════════════════════════════════════════


class TestDateRange:
    """Tests pour date_range."""

    def test_three_days(self):
        """Test avec 3 jours."""
        result = date_range(date(2025, 1, 1), date(2025, 1, 3))
        
        assert len(result) == 3
        assert result[0] == date(2025, 1, 1)
        assert result[1] == date(2025, 1, 2)
        assert result[2] == date(2025, 1, 3)

    def test_same_day(self):
        """Test même jour."""
        result = date_range(date(2025, 1, 1), date(2025, 1, 1))
        
        assert len(result) == 1
        assert result[0] == date(2025, 1, 1)

    def test_week(self):
        """Test une semaine."""
        result = date_range(date(2025, 1, 6), date(2025, 1, 12))
        
        assert len(result) == 7

    def test_across_month(self):
        """Test chevauchant le mois."""
        result = date_range(date(2025, 1, 30), date(2025, 2, 2))
        
        assert len(result) == 4
        assert result[0] == date(2025, 1, 30)
        assert result[-1] == date(2025, 2, 2)

    def test_returns_list(self):
        """Test retourne une liste."""
        result = date_range(date(2025, 1, 1), date(2025, 1, 5))
        
        assert isinstance(result, list)
        assert all(isinstance(d, date) for d in result)


# ═══════════════════════════════════════════════════════════
# TESTS GET_MONTH_BOUNDS
# ═══════════════════════════════════════════════════════════


class TestGetMonthBounds:
    """Tests pour get_month_bounds."""

    def test_january(self):
        """Test janvier (31 jours)."""
        first, last = get_month_bounds(date(2025, 1, 15))
        
        assert first == date(2025, 1, 1)
        assert last == date(2025, 1, 31)

    def test_february_normal(self):
        """Test février non bissextile."""
        first, last = get_month_bounds(date(2025, 2, 15))
        
        assert first == date(2025, 2, 1)
        assert last == date(2025, 2, 28)

    def test_february_leap_year(self):
        """Test février bissextile."""
        first, last = get_month_bounds(date(2024, 2, 15))
        
        assert first == date(2024, 2, 1)
        assert last == date(2024, 2, 29)

    def test_april(self):
        """Test avril (30 jours)."""
        first, last = get_month_bounds(date(2025, 4, 10))
        
        assert first == date(2025, 4, 1)
        assert last == date(2025, 4, 30)

    def test_december(self):
        """Test décembre (fin d'année)."""
        first, last = get_month_bounds(date(2025, 12, 25))
        
        assert first == date(2025, 12, 1)
        assert last == date(2025, 12, 31)

    def test_first_day_of_month(self):
        """Test avec le premier jour du mois."""
        first, last = get_month_bounds(date(2025, 3, 1))
        
        assert first == date(2025, 3, 1)
        assert last == date(2025, 3, 31)

    def test_last_day_of_month(self):
        """Test avec le dernier jour du mois."""
        first, last = get_month_bounds(date(2025, 3, 31))
        
        assert first == date(2025, 3, 1)
        assert last == date(2025, 3, 31)


# ═══════════════════════════════════════════════════════════
# TESTS ADD_BUSINESS_DAYS
# ═══════════════════════════════════════════════════════════


class TestAddBusinessDays:
    """Tests pour add_business_days."""

    def test_monday_plus_five(self):
        """Test lundi + 5 jours ouvrés = lundi suivant."""
        # 6 janvier 2025 est un lundi
        result = add_business_days(date(2025, 1, 6), 5)
        
        assert result == date(2025, 1, 13)  # Lundi suivant

    def test_friday_plus_one(self):
        """Test vendredi + 1 = lundi."""
        # 10 janvier 2025 est un vendredi
        result = add_business_days(date(2025, 1, 10), 1)
        
        assert result == date(2025, 1, 13)  # Lundi

    def test_skip_weekend(self):
        """Test saute le weekend."""
        # 9 janvier 2025 est un jeudi
        result = add_business_days(date(2025, 1, 9), 2)
        
        assert result == date(2025, 1, 13)  # Lundi (skip weekend)

    def test_zero_days(self):
        """Test 0 jours."""
        d = date(2025, 1, 6)
        result = add_business_days(d, 0)
        
        assert result == d

    def test_ten_business_days(self):
        """Test 10 jours ouvrés = 2 semaines."""
        result = add_business_days(date(2025, 1, 6), 10)
        
        assert result == date(2025, 1, 20)  # 2 semaines plus tard


# ═══════════════════════════════════════════════════════════
# TESTS WEEKS_BETWEEN
# ═══════════════════════════════════════════════════════════


class TestWeeksBetween:
    """Tests pour weeks_between."""

    def test_two_weeks(self):
        """Test 2 semaines."""
        result = weeks_between(date(2025, 1, 1), date(2025, 1, 15))
        
        assert result == 2

    def test_one_week(self):
        """Test 1 semaine."""
        result = weeks_between(date(2025, 1, 1), date(2025, 1, 8))
        
        assert result == 1

    def test_same_day(self):
        """Test même jour."""
        result = weeks_between(date(2025, 1, 1), date(2025, 1, 1))
        
        assert result == 0

    def test_less_than_week(self):
        """Test moins d'une semaine."""
        result = weeks_between(date(2025, 1, 1), date(2025, 1, 5))
        
        assert result == 0

    def test_partial_week(self):
        """Test semaine partielle."""
        result = weeks_between(date(2025, 1, 1), date(2025, 1, 10))
        
        assert result == 1  # 9 jours = 1 semaine + 2 jours


# ═══════════════════════════════════════════════════════════
# TESTS IS_WEEKEND
# ═══════════════════════════════════════════════════════════


class TestIsWeekend:
    """Tests pour is_weekend."""

    def test_saturday(self):
        """Test samedi."""
        # 11 janvier 2025 est un samedi
        assert is_weekend(date(2025, 1, 11)) is True

    def test_sunday(self):
        """Test dimanche."""
        # 12 janvier 2025 est un dimanche
        assert is_weekend(date(2025, 1, 12)) is True

    def test_monday(self):
        """Test lundi."""
        assert is_weekend(date(2025, 1, 6)) is False

    def test_friday(self):
        """Test vendredi."""
        assert is_weekend(date(2025, 1, 10)) is False

    def test_wednesday(self):
        """Test mercredi."""
        assert is_weekend(date(2025, 1, 8)) is False


# ═══════════════════════════════════════════════════════════
# TESTS GET_QUARTER
# ═══════════════════════════════════════════════════════════


class TestGetQuarter:
    """Tests pour get_quarter."""

    def test_january(self):
        """Test janvier = Q1."""
        assert get_quarter(date(2025, 1, 1)) == 1

    def test_march(self):
        """Test mars = Q1."""
        assert get_quarter(date(2025, 3, 31)) == 1

    def test_april(self):
        """Test avril = Q2."""
        assert get_quarter(date(2025, 4, 1)) == 2

    def test_june(self):
        """Test juin = Q2."""
        assert get_quarter(date(2025, 6, 15)) == 2

    def test_july(self):
        """Test juillet = Q3."""
        assert get_quarter(date(2025, 7, 1)) == 3

    def test_september(self):
        """Test septembre = Q3."""
        assert get_quarter(date(2025, 9, 30)) == 3

    def test_october(self):
        """Test octobre = Q4."""
        assert get_quarter(date(2025, 10, 1)) == 4

    def test_december(self):
        """Test décembre = Q4."""
        assert get_quarter(date(2025, 12, 31)) == 4

    def test_all_months(self):
        """Test tous les mois."""
        quarters = {
            1: 1, 2: 1, 3: 1,
            4: 2, 5: 2, 6: 2,
            7: 3, 8: 3, 9: 3,
            10: 4, 11: 4, 12: 4,
        }
        
        for month, expected_quarter in quarters.items():
            assert get_quarter(date(2025, month, 15)) == expected_quarter
