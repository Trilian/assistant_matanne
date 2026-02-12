"""
Tests unitaires pour stats.py

Module: src.utils.helpers.stats
"""

import pytest
from src.utils.helpers.stats import (
    calculer_moyenne,
    calculer_mediane,
    calculer_variance,
    calculer_ecart_type,
    calculer_percentile,
    calculer_mode,
    calculer_etendue,
    moyenne_mobile,
)


class TestStats:
    """Tests pour le module stats."""

    def test_calculer_moyenne(self):
        """Test de la fonction calculer_moyenne."""
        assert calculer_moyenne([1, 2, 3, 4, 5]) == 3.0
        assert calculer_moyenne([10]) == 10.0
        assert calculer_moyenne([]) == 0.0

    def test_calculer_mediane(self):
        """Test de la fonction calculer_mediane."""
        assert calculer_mediane([1, 2, 3, 4, 5]) == 3.0
        assert calculer_mediane([1, 2, 3, 4]) == 2.5
        assert calculer_mediane([]) == 0.0

    def test_calculer_variance(self):
        """Test de la fonction calculer_variance."""
        assert calculer_variance([1, 2, 3, 4, 5]) == 2.5
        assert calculer_variance([]) == 0.0
        assert calculer_variance([5]) == 0.0  # Besoin d'au moins 2 valeurs

    def test_calculer_ecart_type(self):
        """Test de la fonction calculer_ecart_type."""
        result = calculer_ecart_type([1, 2, 3, 4, 5])
        assert 1.58 <= result <= 1.59  # ~1.5811
        assert calculer_ecart_type([]) == 0.0

    def test_calculer_percentile(self):
        """Test de la fonction calculer_percentile."""
        assert calculer_percentile([1, 2, 3, 4, 5], 50) == 3.0
        assert calculer_percentile([1, 2, 3, 4, 5], 0) == 1.0
        assert calculer_percentile([1, 2, 3, 4, 5], 100) == 5.0
        assert calculer_percentile([], 50) == 0.0

    def test_calculer_mode(self):
        """Test de la fonction calculer_mode."""
        assert calculer_mode([1, 2, 2, 3, 3, 3]) == 3
        assert calculer_mode([]) is None

    def test_calculer_etendue(self):
        """Test de la fonction calculer_etendue."""
        assert calculer_etendue([1, 2, 3, 4, 5]) == 4.0
        assert calculer_etendue([5, 5, 5]) == 0.0
        assert calculer_etendue([]) == 0.0

    def test_moyenne_mobile(self):
        """Test de la fonction moyenne_mobile."""
        assert moyenne_mobile([1, 2, 3, 4, 5], 3) == [2.0, 3.0, 4.0]
        assert moyenne_mobile([1, 2], 3) == []  # Fenêtre trop grande
