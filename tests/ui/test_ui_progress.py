"""
Tests pour src/ui/feedback/progress.py
Tracking de progression pour opÃ©rations longues
"""

from datetime import datetime
from unittest.mock import MagicMock, patch
import time

import pytest


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FIXTURES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.fixture
def mock_streamlit():
    """Mock Streamlit"""
    with patch("src.ui.feedback.progress.st") as mock_st:
        mock_st.empty.return_value = MagicMock()
        mock_st.progress.return_value = MagicMock()
        yield mock_st


@pytest.fixture
def mock_time():
    """Mock time.sleep"""
    with patch("src.ui.feedback.progress.time") as mock_t:
        mock_t.sleep = MagicMock()
        yield mock_t


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS PROGRESS TRACKER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestProgressTracker:
    """Tests pour ProgressTracker"""

    def test_init_basic(self, mock_streamlit):
        """Test initialisation basique"""
        from src.ui.feedback.progress import ProgressTracker

        tracker = ProgressTracker("Test opÃ©ration", total=100)

        assert tracker.operation == "Test opÃ©ration"
        assert tracker.total == 100
        assert tracker.current == 0
        assert tracker.show_percentage is True

    def test_init_creates_ui_elements(self, mock_streamlit):
        """Test crÃ©ation Ã©lÃ©ments UI"""
        from src.ui.feedback.progress import ProgressTracker

        ProgressTracker("Test", total=50)

        # Doit crÃ©er 2 placeholders et 1 progress bar
        assert mock_streamlit.empty.call_count == 2
        mock_streamlit.progress.assert_called_once_with(0)

    def test_update_sets_current(self, mock_streamlit):
        """Test update() met Ã  jour current"""
        from src.ui.feedback.progress import ProgressTracker

        tracker = ProgressTracker("Test", total=100)
        tracker.update(50)

        assert tracker.current == 50

    def test_update_with_status(self, mock_streamlit):
        """Test update() avec message de statut"""
        from src.ui.feedback.progress import ProgressTracker

        tracker = ProgressTracker("Test", total=100)
        tracker.update(25, status="Traitement item 25")

        # Le statut doit Ãªtre affichÃ© via caption
        tracker.status_placeholder.caption.assert_called()

    def test_increment_single_step(self, mock_streamlit):
        """Test increment() avec un pas"""
        from src.ui.feedback.progress import ProgressTracker

        tracker = ProgressTracker("Test", total=100)
        tracker.increment()

        assert tracker.current == 1

    def test_increment_custom_step(self, mock_streamlit):
        """Test increment() avec pas personnalisÃ©"""
        from src.ui.feedback.progress import ProgressTracker

        tracker = ProgressTracker("Test", total=100)
        tracker.increment(step=10)

        assert tracker.current == 10

    def test_increment_respects_max(self, mock_streamlit):
        """Test increment() ne dÃ©passe pas total"""
        from src.ui.feedback.progress import ProgressTracker

        tracker = ProgressTracker("Test", total=100)
        tracker.current = 95
        tracker.increment(step=10)

        assert tracker.current == 100  # Pas 105

    def test_complete_sets_to_total(self, mock_streamlit, mock_time):
        """Test complete() met current Ã  total"""
        from src.ui.feedback.progress import ProgressTracker

        tracker = ProgressTracker("Test", total=100)
        tracker.complete()

        assert tracker.current == 100

    def test_complete_shows_success(self, mock_streamlit, mock_time):
        """Test complete() affiche succÃ¨s"""
        from src.ui.feedback.progress import ProgressTracker

        tracker = ProgressTracker("Test", total=100)
        tracker.complete()

        tracker.status_placeholder.success.assert_called()

    def test_complete_with_message(self, mock_streamlit, mock_time):
        """Test complete() avec message personnalisÃ©"""
        from src.ui.feedback.progress import ProgressTracker

        tracker = ProgressTracker("Test", total=100)
        tracker.complete(message="Import terminÃ©")

        call_args = tracker.status_placeholder.success.call_args[0][0]
        assert "Import terminÃ©" in call_args

    def test_complete_clears_ui(self, mock_streamlit, mock_time):
        """Test complete() nettoie l'UI aprÃ¨s dÃ©lai"""
        from src.ui.feedback.progress import ProgressTracker

        tracker = ProgressTracker("Test", total=100)
        tracker.complete()

        # time.sleep doit Ãªtre appelÃ©
        mock_time.sleep.assert_called_with(2)
        # Placeholders doivent Ãªtre vidÃ©s
        tracker.title_placeholder.empty.assert_called()
        tracker.progress_bar.empty.assert_called()

    def test_error_shows_error_message(self, mock_streamlit):
        """Test error() affiche erreur"""
        from src.ui.feedback.progress import ProgressTracker

        tracker = ProgressTracker("Test", total=100)
        tracker.error("Une erreur est survenue")

        tracker.status_placeholder.error.assert_called_once()
        call_args = tracker.status_placeholder.error.call_args[0][0]
        assert "Une erreur est survenue" in call_args

    def test_update_display_percentage(self, mock_streamlit):
        """Test affichage pourcentage"""
        from src.ui.feedback.progress import ProgressTracker

        tracker = ProgressTracker("Test", total=100, show_percentage=True)
        tracker.current = 50
        tracker._update_display()

        # Le titre doit contenir 50%
        call_args = tracker.title_placeholder.markdown.call_args[0][0]
        assert "50%" in call_args

    def test_update_display_count(self, mock_streamlit):
        """Test affichage compteur"""
        from src.ui.feedback.progress import ProgressTracker

        tracker = ProgressTracker("Test", total=100, show_percentage=False)
        tracker.current = 50
        tracker._update_display()

        # Le titre doit contenir 50/100
        call_args = tracker.title_placeholder.markdown.call_args[0][0]
        assert "50/100" in call_args


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS LOADING STATE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestLoadingState:
    """Tests pour LoadingState"""

    def test_init_basic(self, mock_streamlit):
        """Test initialisation basique"""
        from src.ui.feedback.progress import LoadingState

        loading = LoadingState("Chargement")

        assert loading.title == "Chargement"
        assert loading.steps == []
        assert loading.current_step is None

    def test_init_creates_ui(self, mock_streamlit):
        """Test crÃ©ation Ã©lÃ©ments UI"""
        from src.ui.feedback.progress import LoadingState

        LoadingState("Test")

        assert mock_streamlit.empty.call_count == 2

    def test_add_step_creates_step(self, mock_streamlit):
        """Test add_step() crÃ©e une Ã©tape"""
        from src.ui.feedback.progress import LoadingState

        loading = LoadingState("Test")
        loading.add_step("Connexion DB")

        assert len(loading.steps) == 1
        assert loading.steps[0]["name"] == "Connexion DB"
        assert loading.steps[0]["completed"] is False

    def test_add_step_sets_current(self, mock_streamlit):
        """Test add_step() dÃ©finit current_step"""
        from src.ui.feedback.progress import LoadingState

        loading = LoadingState("Test")
        loading.add_step("Ã‰tape 1")

        assert loading.current_step == 0

    def test_add_multiple_steps(self, mock_streamlit):
        """Test ajout de plusieurs Ã©tapes"""
        from src.ui.feedback.progress import LoadingState

        loading = LoadingState("Test")
        loading.add_step("Ã‰tape 1")
        loading.add_step("Ã‰tape 2")
        loading.add_step("Ã‰tape 3")

        assert len(loading.steps) == 3
        assert loading.current_step == 2

    def test_complete_step_by_name(self, mock_streamlit):
        """Test complete_step() par nom"""
        from src.ui.feedback.progress import LoadingState

        loading = LoadingState("Test")
        loading.add_step("Connexion")
        loading.complete_step("Connexion")

        # Chercher l'Ã©tape complÃ©tÃ©e
        step = next(s for s in loading.steps if s["name"] == "Connexion")
        assert step["completed"] is True

    def test_complete_step_current(self, mock_streamlit):
        """Test complete_step() sur Ã©tape courante"""
        from src.ui.feedback.progress import LoadingState

        loading = LoadingState("Test")
        loading.add_step("Ã‰tape 1")
        loading.complete_step()

        assert loading.steps[0]["completed"] is True

    def test_complete_step_success_status(self, mock_streamlit):
        """Test complete_step() avec succÃ¨s"""
        from src.ui.feedback.progress import LoadingState

        loading = LoadingState("Test")
        loading.add_step("Ã‰tape")
        loading.complete_step(success=True)

        assert "âœ…" in loading.steps[0]["status"]

    def test_complete_step_error_status(self, mock_streamlit):
        """Test complete_step() avec erreur"""
        from src.ui.feedback.progress import LoadingState

        loading = LoadingState("Test")
        loading.add_step("Ã‰tape")
        loading.complete_step(success=False)

        assert "âŒ" in loading.steps[0]["status"]

