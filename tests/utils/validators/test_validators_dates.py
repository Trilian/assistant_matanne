"""
Tests unitaires pour dates.py

Module: src.utils.validators.dates
"""

import pytest
from datetime import date, timedelta
from src.utils.validators.dates import (
    valider_plage_dates,
    est_date_future,
    est_date_passee,
    valider_date_peremption,
    jours_jusqua,
    est_dans_x_jours,
)


class TestDates:
    """Tests pour le module dates."""

    def test_valider_plage_dates(self):
        """Test de la fonction valider_plage_dates."""
        is_valid, msg = valider_plage_dates(date(2025, 1, 1), date(2025, 1, 10))
        assert is_valid is True
        assert msg == ""
        
        is_valid, msg = valider_plage_dates(date(2025, 1, 10), date(2025, 1, 1))
        assert is_valid is False

    def test_est_date_future(self):
        """Test de la fonction est_date_future."""
        future = date.today() + timedelta(days=10)
        past = date.today() - timedelta(days=10)
        assert est_date_future(future) is True
        assert est_date_future(past) is False

    def test_est_date_passee(self):
        """Test de la fonction est_date_passee."""
        future = date.today() + timedelta(days=10)
        past = date.today() - timedelta(days=10)
        assert est_date_passee(past) is True
        assert est_date_passee(future) is False

    def test_valider_date_peremption(self):
        """Test de la fonction valider_date_peremption."""
        valid_date = date.today() + timedelta(days=30)
        is_valid, msg = valider_date_peremption(valid_date)
        assert is_valid is True
        
        past_date = date.today() - timedelta(days=1)
        is_valid, msg = valider_date_peremption(past_date)
        assert is_valid is False

    def test_jours_jusqua(self):
        """Test de la fonction jours_jusqua."""
        target = date.today() + timedelta(days=7)
        assert jours_jusqua(target) == 7

    def test_est_dans_x_jours(self):
        """Test de la fonction est_dans_x_jours."""
        target = date.today() + timedelta(days=3)
        assert est_dans_x_jours(target, 7) is True
        assert est_dans_x_jours(target, 2) is False
