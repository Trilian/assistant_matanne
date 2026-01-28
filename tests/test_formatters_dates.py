"""
Tests pour les formatters de dates
"""

import pytest
from datetime import date, datetime, timedelta

from src.utils.formatters.dates import (
    format_date,
    format_datetime,
    format_relative_date,
    format_time,
    format_duration,
)


class TestFormatDate:
    """Tests pour format_date"""

    def test_format_date_none(self):
        """Test avec None"""
        assert format_date(None) == "—"

    def test_format_date_short(self):
        """Test format short"""
        d = date(2025, 12, 1)
        result = format_date(d, "short")
        assert result == "01/12"

    def test_format_date_medium(self):
        """Test format medium"""
        d = date(2025, 12, 1)
        result = format_date(d, "medium")
        assert result == "01/12/2025"

    def test_format_date_long_french(self):
        """Test format long français"""
        d = date(2025, 12, 1)
        result = format_date(d, "long", "fr")
        assert result == "1 décembre 2025"

    def test_format_date_long_january(self):
        """Test format long janvier"""
        d = date(2025, 1, 15)
        result = format_date(d, "long", "fr")
        assert result == "15 janvier 2025"

    def test_format_date_long_english(self):
        """Test format long anglais"""
        d = date(2025, 12, 1)
        result = format_date(d, "long", "en")
        # Le format anglais utilise strftime
        assert "2025" in result

    def test_format_date_datetime_input(self):
        """Test avec datetime en entrée"""
        dt = datetime(2025, 12, 1, 14, 30)
        result = format_date(dt, "medium")
        assert result == "01/12/2025"

    def test_format_date_unknown_format(self):
        """Test avec format inconnu (fallback)"""
        d = date(2025, 12, 1)
        result = format_date(d, "unknown")
        assert result == "01/12/2025"


class TestFormatDatetime:
    """Tests pour format_datetime"""

    def test_format_datetime_none(self):
        """Test avec None"""
        assert format_datetime(None) == "—"

    def test_format_datetime_short(self):
        """Test format short"""
        dt = datetime(2025, 12, 1, 14, 30)
        result = format_datetime(dt, "short")
        assert result == "01/12 14:30"

    def test_format_datetime_medium(self):
        """Test format medium"""
        dt = datetime(2025, 12, 1, 14, 30)
        result = format_datetime(dt, "medium")
        assert result == "01/12/2025 14:30"

    def test_format_datetime_long(self):
        """Test format long"""
        dt = datetime(2025, 12, 1, 14, 30)
        result = format_datetime(dt, "long")
        assert "1 décembre 2025" in result
        assert "14:30" in result

    def test_format_datetime_unknown_format(self):
        """Test avec format inconnu (fallback)"""
        dt = datetime(2025, 12, 1, 14, 30)
        result = format_datetime(dt, "unknown")
        assert result == "01/12/2025 14:30"


class TestFormatRelativeDate:
    """Tests pour format_relative_date"""

    def test_format_relative_today(self):
        """Test aujourd'hui"""
        result = format_relative_date(date.today())
        assert result == "Aujourd'hui"

    def test_format_relative_tomorrow(self):
        """Test demain"""
        result = format_relative_date(date.today() + timedelta(days=1))
        assert result == "Demain"

    def test_format_relative_yesterday(self):
        """Test hier"""
        result = format_relative_date(date.today() - timedelta(days=1))
        assert result == "Hier"

    def test_format_relative_in_3_days(self):
        """Test dans 3 jours"""
        result = format_relative_date(date.today() + timedelta(days=3))
        assert result == "Dans 3 jours"

    def test_format_relative_3_days_ago(self):
        """Test il y a 3 jours"""
        result = format_relative_date(date.today() - timedelta(days=3))
        assert result == "Il y a 3 jours"

    def test_format_relative_distant_future(self):
        """Test date lointaine"""
        result = format_relative_date(date.today() + timedelta(days=30))
        # Doit retourner format medium
        assert "/" in result

    def test_format_relative_datetime_input(self):
        """Test avec datetime en entrée"""
        dt = datetime.now()
        result = format_relative_date(dt)
        assert result == "Aujourd'hui"


class TestFormatTime:
    """Tests pour format_time (durée en minutes)"""

    def test_format_time_none(self):
        """Test avec None"""
        assert format_time(None) == "0min"

    def test_format_time_zero(self):
        """Test avec 0"""
        assert format_time(0) == "0min"

    def test_format_time_minutes_only(self):
        """Test minutes seules"""
        assert format_time(45) == "45min"

    def test_format_time_one_hour(self):
        """Test une heure exacte"""
        assert format_time(60) == "1h"

    def test_format_time_hours_minutes(self):
        """Test heures et minutes"""
        assert format_time(90) == "1h30"

    def test_format_time_two_hours_30(self):
        """Test 2h30"""
        assert format_time(150) == "2h30"

    def test_format_time_invalid(self):
        """Test valeur invalide"""
        assert format_time("invalid") == "0min"


class TestFormatDuration:
    """Tests pour format_duration (durée en secondes)"""

    def test_format_duration_none(self):
        """Test avec None"""
        assert format_duration(None) == "0 seconde"

    def test_format_duration_none_short(self):
        """Test avec None format court"""
        assert format_duration(None, short=True) == "0s"

    def test_format_duration_zero(self):
        """Test avec 0"""
        assert format_duration(0) == "0 seconde"

    def test_format_duration_seconds_short(self):
        """Test secondes format court"""
        assert format_duration(45, short=True) == "45s"

    def test_format_duration_seconds_long(self):
        """Test secondes format long"""
        result = format_duration(45)
        assert "45 seconde" in result

    def test_format_duration_minutes_short(self):
        """Test minutes format court"""
        result = format_duration(120, short=True)
        assert "2min" in result

    def test_format_duration_hours_minutes_seconds_short(self):
        """Test heures/minutes/secondes format court"""
        result = format_duration(3665, short=True)
        assert "1h" in result
        assert "1min" in result
        assert "5s" in result

    def test_format_duration_hours_long(self):
        """Test heures format long"""
        result = format_duration(7200)  # 2 heures
        assert "2 heures" in result

    def test_format_duration_invalid(self):
        """Test valeur invalide"""
        assert format_duration("invalid") == "0s"
