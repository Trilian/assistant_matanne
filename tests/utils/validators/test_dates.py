"""
Tests pour src/utils/validators/dates.py
"""

from datetime import date, timedelta

from src.utils.validators.dates import (
    est_dans_x_jours,
    est_date_future,
    est_date_passee,
    jours_jusqua,
    valider_date_peremption,
    valider_plage_dates,
)


class TestValiderPlageDates:
    """Tests pour valider_plage_dates (retourne tuple[bool, str])."""

    def test_valider_range_valid(self):
        """Plage valide (start < end)."""
        is_valid, msg = valider_plage_dates(date(2025, 1, 1), date(2025, 1, 31))
        assert is_valid is True
        assert msg == ""

    def test_valider_range_same_day(self):
        """Même jour = valide."""
        d = date(2025, 1, 1)
        is_valid, msg = valider_plage_dates(d, d)
        assert is_valid is True

    def test_valider_range_invalid(self):
        """Start > end = invalide."""
        is_valid, msg = valider_plage_dates(date(2025, 1, 31), date(2025, 1, 1))
        assert is_valid is False


class TestEstDateFuture:
    """Tests pour est_date_future."""

    def test_est_date_future_tomorrow(self):
        """Demain = futur."""
        tomorrow = date.today() + timedelta(days=1)
        assert est_date_future(tomorrow) is True

    def test_est_date_future_today(self):
        """Aujourd'hui = pas futur."""
        assert est_date_future(date.today()) is False

    def test_est_date_future_yesterday(self):
        """Hier = pas futur."""
        yesterday = date.today() - timedelta(days=1)
        assert est_date_future(yesterday) is False

    def test_est_date_future_next_year(self):
        """Année prochaine = futur."""
        next_year = date(date.today().year + 1, 1, 1)
        assert est_date_future(next_year) is True


class TestEstDatePassee:
    """Tests pour est_date_passee."""

    def test_est_date_passee_yesterday(self):
        """Hier = passé."""
        yesterday = date.today() - timedelta(days=1)
        assert est_date_passee(yesterday) is True

    def test_est_date_passee_today(self):
        """Aujourd'hui = pas passé."""
        assert est_date_passee(date.today()) is False

    def test_est_date_passee_tomorrow(self):
        """Demain = pas passé."""
        tomorrow = date.today() + timedelta(days=1)
        assert est_date_passee(tomorrow) is False


class TestValiderDatePeremption:
    """Tests pour valider_date_peremption (retourne tuple[bool, str])."""

    def test_valider_peremption_future(self):
        """Date future = valide."""
        future = date.today() + timedelta(days=30)
        is_valid, msg = valider_date_peremption(future)
        assert is_valid is True

    def test_valider_peremption_today(self):
        """Aujourd'hui avec min_days_ahead=1 = invalide."""
        is_valid, msg = valider_date_peremption(date.today())
        assert is_valid is False  # Doit être au moins 1 jour dans le futur

    def test_valider_peremption_past(self):
        """Date passée = expiré."""
        past = date.today() - timedelta(days=1)
        is_valid, msg = valider_date_peremption(past)
        assert is_valid is False


class TestJoursJusqua:
    """Tests pour jours_jusqua."""

    def test_jours_jusqua_tomorrow(self):
        """Jours jusqu'à demain = 1."""
        tomorrow = date.today() + timedelta(days=1)
        assert jours_jusqua(tomorrow) == 1

    def test_jours_jusqua_next_week(self):
        """Jours jusqu'à semaine prochaine = 7."""
        next_week = date.today() + timedelta(days=7)
        assert jours_jusqua(next_week) == 7

    def test_jours_jusqua_today(self):
        """Jours jusqu'à aujourd'hui = 0."""
        assert jours_jusqua(date.today()) == 0

    def test_jours_jusqua_past(self):
        """Jours jusqu'à date passée = négatif."""
        yesterday = date.today() - timedelta(days=1)
        assert jours_jusqua(yesterday) == -1


class TestEstDansXJours:
    """Tests pour est_dans_x_jours."""

    def test_est_dans_x_jours_true(self):
        """Date dans les N jours."""
        target = date.today() + timedelta(days=3)
        assert est_dans_x_jours(target, 5) is True

    def test_est_dans_x_jours_false(self):
        """Date hors des N jours."""
        target = date.today() + timedelta(days=10)
        assert est_dans_x_jours(target, 5) is False

    def test_est_dans_x_jours_exact(self):
        """Date exactement à N jours."""
        target = date.today() + timedelta(days=5)
        assert est_dans_x_jours(target, 5) is True

    def test_est_dans_x_jours_today(self):
        """Aujourd'hui = dans les N jours."""
        assert est_dans_x_jours(date.today(), 5) is True

    def test_est_dans_x_jours_past(self):
        """Date passée = pas dans les N jours futurs."""
        yesterday = date.today() - timedelta(days=1)
        assert est_dans_x_jours(yesterday, 5) is False
