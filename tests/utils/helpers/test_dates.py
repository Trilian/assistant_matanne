"""
Tests pour src/utils/helpers/dates.py
"""

from datetime import date

from src.utils.helpers.dates import (
    ajouter_jours_ouvres,
    est_weekend,
    obtenir_bornes_mois,
    obtenir_bornes_semaine,
    plage_dates,
    semaines_entre,
)


class TestObtenirBornesSemaine:
    """Tests pour obtenir_bornes_semaine."""

    def test_week_bounds_wednesday(self):
        """Trouve les bornes depuis un mercredi."""
        d = date(2025, 1, 8)  # Mercredi
        monday, sunday = obtenir_bornes_semaine(d)
        assert monday == date(2025, 1, 6)
        assert sunday == date(2025, 1, 12)

    def test_week_bounds_monday(self):
        """Lundi retourne lui-même comme début."""
        d = date(2025, 1, 6)  # Lundi
        monday, sunday = obtenir_bornes_semaine(d)
        assert monday == d
        assert monday.weekday() == 0

    def test_week_bounds_sunday(self):
        """Dimanche retourne lui-même comme fin."""
        d = date(2025, 1, 12)  # Dimanche
        monday, sunday = obtenir_bornes_semaine(d)
        assert sunday == d
        assert sunday.weekday() == 6


class TestPlageDates:
    """Tests pour plage_dates."""

    def test_plage_dates_basic(self):
        """Génère une plage de dates."""
        result = plage_dates(date(2025, 1, 1), date(2025, 1, 3))
        assert len(result) == 3
        assert result[0] == date(2025, 1, 1)
        assert result[-1] == date(2025, 1, 3)

    def test_plage_dates_same_day(self):
        """Même jour = liste avec un élément."""
        d = date(2025, 1, 1)
        result = plage_dates(d, d)
        assert len(result) == 1
        assert result[0] == d

    def test_plage_dates_week(self):
        """Plage d'une semaine."""
        result = plage_dates(date(2025, 1, 6), date(2025, 1, 12))
        assert len(result) == 7


class TestObtenirBornesMois:
    """Tests pour obtenir_bornes_mois."""

    def test_month_bounds_february(self):
        """Février non-bissextile."""
        first, last = obtenir_bornes_mois(date(2025, 2, 15))
        assert first == date(2025, 2, 1)
        assert last == date(2025, 2, 28)

    def test_month_bounds_february_leap(self):
        """Février bissextile."""
        first, last = obtenir_bornes_mois(date(2024, 2, 15))
        assert last == date(2024, 2, 29)

    def test_month_bounds_january(self):
        """Janvier = 31 jours."""
        first, last = obtenir_bornes_mois(date(2025, 1, 15))
        assert first == date(2025, 1, 1)
        assert last == date(2025, 1, 31)

    def test_month_bounds_december(self):
        """Décembre passe à l'année suivante."""
        first, last = obtenir_bornes_mois(date(2025, 12, 15))
        assert first == date(2025, 12, 1)
        assert last == date(2025, 12, 31)


class TestAjouterJoursOuvres:
    """Tests pour ajouter_jours_ouvres."""

    def test_add_business_days_no_weekend(self):
        """Ajoute jours sans traverser weekend."""
        result = ajouter_jours_ouvres(date(2025, 1, 6), 3)  # Lundi + 3
        assert result == date(2025, 1, 9)  # Jeudi

    def test_add_business_days_over_weekend(self):
        """Ajoute jours en traversant weekend."""
        result = ajouter_jours_ouvres(date(2025, 1, 6), 5)  # Lundi + 5
        assert result == date(2025, 1, 13)  # Lundi suivant

    def test_add_business_days_from_friday(self):
        """Vendredi + 1 = Lundi."""
        result = ajouter_jours_ouvres(date(2025, 1, 10), 1)  # Vendredi
        assert result == date(2025, 1, 13)  # Lundi


class TestSemainesEntre:
    """Tests pour semaines_entre."""

    def test_semaines_entre_exact(self):
        """Semaines exactes."""
        assert semaines_entre(date(2025, 1, 1), date(2025, 1, 15)) == 2

    def test_semaines_entre_zero(self):
        """Même semaine = 0."""
        assert semaines_entre(date(2025, 1, 1), date(2025, 1, 3)) == 0

    def test_semaines_entre_one_week(self):
        """Une semaine exacte."""
        assert semaines_entre(date(2025, 1, 1), date(2025, 1, 8)) == 1


class TestEstWeekend:
    """Tests pour est_weekend."""

    def test_est_weekend_saturday(self):
        """Samedi = weekend."""
        assert est_weekend(date(2025, 1, 11)) is True

    def test_est_weekend_sunday(self):
        """Dimanche = weekend."""
        assert est_weekend(date(2025, 1, 12)) is True

    def test_est_weekend_monday(self):
        """Lundi = pas weekend."""
        assert est_weekend(date(2025, 1, 6)) is False

    def test_est_weekend_friday(self):
        """Vendredi = pas weekend."""
        assert est_weekend(date(2025, 1, 10)) is False
