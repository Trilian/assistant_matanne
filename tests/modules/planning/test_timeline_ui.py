"""Tests pour le module timeline."""

from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest


class TestTimelineHelpers:
    """Tests pour les helpers de timeline."""

    def test_obtenir_debut_semaine_lundi(self):
        """obtenir_debut_semaine retourne lundi si déjà lundi."""
        from src.core.date_utils import obtenir_debut_semaine

        lundi = date(2026, 2, 16)  # Lundi
        assert obtenir_debut_semaine(lundi) == lundi

    def test_obtenir_debut_semaine_autre_jour(self):
        """obtenir_debut_semaine retourne le lundi de la semaine."""
        from src.core.date_utils import obtenir_debut_semaine

        mercredi = date(2026, 2, 18)  # Mercredi
        lundi = date(2026, 2, 16)
        assert obtenir_debut_semaine(mercredi) == lundi

    def test_couleurs_types(self):
        """COULEURS_TYPES contient les couleurs par défaut."""
        from src.modules.planning.timeline_ui import COULEURS_TYPES

        assert "rdv" in COULEURS_TYPES
        assert "activité" in COULEURS_TYPES
        assert "repas" in COULEURS_TYPES

    def test_jours_semaine(self):
        """JOURS_SEMAINE contient 7 jours."""
        from src.modules.planning.timeline_ui import JOURS_SEMAINE

        assert len(JOURS_SEMAINE) == 7
        assert JOURS_SEMAINE[0] == "Lundi"


class TestChargerEventsPeriode:
    """Tests pour charger_events_periode."""

    @patch("src.modules.planning.timeline_ui.obtenir_contexte_db")
    def test_charger_events_vide(self, mock_db):
        """charger_events_periode retourne liste vide si pas d'events."""
        from src.modules.planning.timeline_ui import charger_events_periode

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = []
        mock_db.return_value.__enter__.return_value = mock_session

        result = charger_events_periode(date.today(), date.today())
        assert isinstance(result, list)


class TestCreerTimeline:
    """Tests pour la création de timelines."""

    def test_creer_timeline_jour_vide(self):
        """creer_timeline_jour avec liste vide retourne figure."""
        import plotly.graph_objects as go

        from src.modules.planning.timeline_ui import creer_timeline_jour

        fig = creer_timeline_jour([], date.today())
        assert isinstance(fig, go.Figure)

    def test_creer_timeline_semaine_vide(self):
        """creer_timeline_semaine avec liste vide retourne figure."""
        import plotly.graph_objects as go

        from src.modules.planning.timeline_ui import creer_timeline_semaine

        lundi = date(2026, 2, 16)
        fig = creer_timeline_semaine([], lundi)
        assert isinstance(fig, go.Figure)
