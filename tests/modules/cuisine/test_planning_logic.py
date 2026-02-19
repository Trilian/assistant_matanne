"""
Tests pour les utilitaires de dates (date_utils).
Les fonctions de planning_utils ont été supprimées (code mort).
Seuls les tests pour date_utils sont conservés.
"""

from datetime import date


class TestGetFinSemaine:
    """Tests pour get_fin_semaine."""

    def test_fin_semaine_dimanche(self):
        """Dimanche retourne lui-même."""
        from src.core.date_utils import obtenir_fin_semaine

        dimanche = date(2025, 2, 9)
        result = obtenir_fin_semaine(dimanche)
        assert result == dimanche
        assert result.weekday() == 6  # Dimanche

    def test_fin_semaine_lundi(self):
        """Lundi retourne le dimanche suivant."""
        from src.core.date_utils import obtenir_fin_semaine

        lundi = date(2025, 2, 3)
        result = obtenir_fin_semaine(lundi)
        assert result == date(2025, 2, 9)  # Dimanche
