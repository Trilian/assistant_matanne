"""
Tests pour src/ui/feedback/spinners.py
Spinners et indicateurs de chargement
"""

from datetime import datetime
from unittest.mock import MagicMock, patch
import time

import pytest


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def mock_streamlit():
    """Mock Streamlit"""
    with patch("src.ui.feedback.spinners.st") as mock_st:
        # Mock spinner comme context manager
        mock_spinner = MagicMock()
        mock_spinner.__enter__ = MagicMock(return_value=None)
        mock_spinner.__exit__ = MagicMock(return_value=None)
        mock_st.spinner.return_value = mock_spinner
        mock_st.caption = MagicMock()
        mock_st.markdown = MagicMock()
        yield mock_st


# ═══════════════════════════════════════════════════════════
# TESTS SMART_SPINNER
# ═══════════════════════════════════════════════════════════


class TestSmartSpinner:
    """Tests pour smart_spinner()"""

    def test_smart_spinner_basic(self, mock_streamlit):
        """Test smart_spinner basique"""
        from src.ui.feedback.spinners import smart_spinner

        with smart_spinner("Test opération"):
            pass

        mock_streamlit.spinner.assert_called_once()
        call_args = mock_streamlit.spinner.call_args[0][0]
        assert "Test opération" in call_args

    def test_smart_spinner_shows_elapsed_time(self, mock_streamlit):
        """Test affichage temps écoulé"""
        from src.ui.feedback.spinners import smart_spinner

        with smart_spinner("Test", show_elapsed=True):
            time.sleep(0.01)  # Petit délai pour avoir du temps

        mock_streamlit.caption.assert_called_once()
        caption_text = mock_streamlit.caption.call_args[0][0]
        assert "✅ Terminé" in caption_text

    def test_smart_spinner_no_elapsed_time(self, mock_streamlit):
        """Test sans temps écoulé"""
        from src.ui.feedback.spinners import smart_spinner

        with smart_spinner("Test", show_elapsed=False):
            pass

        mock_streamlit.caption.assert_not_called()

    def test_smart_spinner_with_estimation(self, mock_streamlit):
        """Test avec estimation de temps"""
        from src.ui.feedback.spinners import smart_spinner

        with smart_spinner("Test", estimated_seconds=5):
            pass

        call_args = mock_streamlit.spinner.call_args[0][0]
        assert "estimation: 5s" in call_args

    def test_smart_spinner_without_estimation(self, mock_streamlit):
        """Test sans estimation"""
        from src.ui.feedback.spinners import smart_spinner

        with smart_spinner("Test", estimated_seconds=None):
            pass

        call_args = mock_streamlit.spinner.call_args[0][0]
        assert "estimation" not in call_args

    def test_smart_spinner_fast_operation_shows_ms(self, mock_streamlit):
        """Test opération rapide affiche en ms"""
        from src.ui.feedback.spinners import smart_spinner

        with smart_spinner("Test rapide"):
            pass  # Très rapide, moins d'1 seconde

        mock_streamlit.caption.assert_called_once()
        caption_text = mock_streamlit.caption.call_args[0][0]
        assert "ms" in caption_text

    def test_smart_spinner_handles_exception(self, mock_streamlit):
        """Test gestion des exceptions"""
        from src.ui.feedback.spinners import smart_spinner

        with pytest.raises(ValueError):
            with smart_spinner("Test"):
                raise ValueError("Test error")

        # Caption doit quand même être appelé (dans finally)
        mock_streamlit.caption.assert_called_once()


# ═══════════════════════════════════════════════════════════
# TESTS LOADING_INDICATOR
# ═══════════════════════════════════════════════════════════


class TestLoadingIndicator:
    """Tests pour loading_indicator()"""

    def test_loading_indicator_default(self, mock_streamlit):
        """Test indicateur par défaut"""
        from src.ui.feedback.spinners import loading_indicator

        loading_indicator()

        mock_streamlit.markdown.assert_called_once()
        call_args = mock_streamlit.markdown.call_args
        assert "Chargement..." in call_args[0][0]
        assert call_args[1]["unsafe_allow_html"] is True

    def test_loading_indicator_custom_message(self, mock_streamlit):
        """Test message personnalisé"""
        from src.ui.feedback.spinners import loading_indicator

        loading_indicator("Chargement des recettes...")

        call_args = mock_streamlit.markdown.call_args[0][0]
        assert "Chargement des recettes..." in call_args

    def test_loading_indicator_contains_spinner_icon(self, mock_streamlit):
        """Test contient icône spinner"""
        from src.ui.feedback.spinners import loading_indicator

        loading_indicator()

        call_args = mock_streamlit.markdown.call_args[0][0]
        assert "⏳" in call_args


# ═══════════════════════════════════════════════════════════
# TESTS SKELETON_LOADER
# ═══════════════════════════════════════════════════════════


class TestSkeletonLoader:
    """Tests pour skeleton_loader()"""

    def test_skeleton_loader_default_lines(self, mock_streamlit):
        """Test lignes par défaut"""
        from src.ui.feedback.spinners import skeleton_loader

        skeleton_loader()

        # 3 lignes par défaut
        assert mock_streamlit.markdown.call_count == 3

    def test_skeleton_loader_custom_lines(self, mock_streamlit):
        """Test nombre de lignes personnalisé"""
        from src.ui.feedback.spinners import skeleton_loader

        skeleton_loader(lines=5)

        assert mock_streamlit.markdown.call_count == 5

    def test_skeleton_loader_single_line(self, mock_streamlit):
        """Test une seule ligne"""
        from src.ui.feedback.spinners import skeleton_loader

        skeleton_loader(lines=1)

        assert mock_streamlit.markdown.call_count == 1

    def test_skeleton_loader_zero_lines(self, mock_streamlit):
        """Test zéro ligne"""
        from src.ui.feedback.spinners import skeleton_loader

        skeleton_loader(lines=0)

        mock_streamlit.markdown.assert_not_called()

    def test_skeleton_loader_html_content(self, mock_streamlit):
        """Test contenu HTML"""
        from src.ui.feedback.spinners import skeleton_loader

        skeleton_loader(lines=1)

        call_args = mock_streamlit.markdown.call_args
        html_content = call_args[0][0]

        # Vérifier éléments de style
        assert "background" in html_content
        assert "animation" in html_content
        assert call_args[1]["unsafe_allow_html"] is True
