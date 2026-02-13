"""
Tests approfondis pour src/ui/
Objectif: Atteindre 80%+ de couverture

Couvre:
- components/atoms.py: badge, empty_state, metric_card, toast
- feedback/toasts.py: ToastManager, show_success, show_error, etc.
- feedback/spinners.py: smart_spinner, loading_indicator, skeleton_loader
- feedback/progress.py: ProgressTracker
- tablet_mode.py: TabletMode, get_tablet_mode, set_tablet_mode
- domain.py, core/base_form.py, core/base_io.py, core/base_module.py
"""

from unittest.mock import MagicMock, patch

import pytest

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FIXTURES STREAMLIT MOCK
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.fixture
def mock_streamlit():
    """Fixture pour mocker Streamlit"""
    with patch.dict("sys.modules", {"streamlit": MagicMock()}):
        import streamlit as st

        st.session_state = {}
        st.markdown = MagicMock()
        st.success = MagicMock()
        st.error = MagicMock()
        st.warning = MagicMock()
        st.info = MagicMock()
        st.spinner = MagicMock()
        st.progress = MagicMock(return_value=MagicMock())
        st.empty = MagicMock(return_value=MagicMock())
        st.container = MagicMock(return_value=MagicMock())
        st.caption = MagicMock()
        yield st


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS TABLET MODE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestTabletMode:
    """Tests pour tablet_mode.py"""

    def test_tablet_mode_enum(self):
        """Test enum TabletMode"""
        from src.ui.tablet_mode import TabletMode

        assert TabletMode.NORMAL == "normal"
        assert TabletMode.TABLET == "tablet"
        assert TabletMode.KITCHEN == "kitchen"

    @patch("streamlit.session_state", {})
    def test_get_tablet_mode_default(self):
        """Test mode par dÃ©faut"""
        # Reset session state
        import streamlit as st

        from src.ui.tablet_mode import TabletMode, get_tablet_mode

        st.session_state = {}

        result = get_tablet_mode()
        assert result == TabletMode.NORMAL

    @patch("streamlit.session_state", {"tablet_mode": "tablet"})
    def test_get_tablet_mode_tablet(self):
        """Test mode tablette"""
        from src.ui.tablet_mode import TabletMode, get_tablet_mode

        result = get_tablet_mode()
        assert result == TabletMode.TABLET

    @patch("streamlit.session_state", {})
    def test_set_tablet_mode(self):
        """Test dÃ©finir mode tablette"""
        import streamlit as st

        from src.ui.tablet_mode import TabletMode, set_tablet_mode

        st.session_state = {}

        set_tablet_mode(TabletMode.KITCHEN)

        assert st.session_state.get("tablet_mode") == TabletMode.KITCHEN

    def test_tablet_css_exists(self):
        """Test que le CSS tablette est dÃ©fini"""
        from src.ui.tablet_mode import TABLET_CSS

        assert TABLET_CSS is not None
        assert "tablet" in TABLET_CSS.lower()
        assert "style" in TABLET_CSS.lower()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ATOMS COMPONENTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestBadge:
    """Tests pour badge()"""

    @patch("streamlit.markdown")
    def test_badge_simple(self, mock_markdown):
        """Test badge simple"""
        from src.ui.components.atoms import badge

        badge("Actif", "#4CAF50")

        mock_markdown.assert_called_once()
        call_args = mock_markdown.call_args[0][0]
        assert "Actif" in call_args
        assert "#4CAF50" in call_args

    @patch("streamlit.markdown")
    def test_badge_couleur_par_defaut(self, mock_markdown):
        """Test badge avec couleur par dÃ©faut"""
        from src.ui.components.atoms import badge

        badge("Test")

        mock_markdown.assert_called_once()
        call_args = mock_markdown.call_args[0][0]
        assert "Test" in call_args
        assert "#4CAF50" in call_args  # Couleur par dÃ©faut


class TestEmptyState:
    """Tests pour empty_state()"""

    @patch("streamlit.markdown")
    def test_empty_state_simple(self, mock_markdown):
        """Test Ã©tat vide simple"""
        from src.ui.components.atoms import empty_state

        empty_state("Aucune recette", "ðŸ½ï¸")

        mock_markdown.assert_called_once()
        call_args = mock_markdown.call_args[0][0]
        assert "Aucune recette" in call_args
        assert "ðŸ½ï¸" in call_args

    @patch("streamlit.markdown")
    def test_empty_state_avec_subtext(self, mock_markdown):
        """Test Ã©tat vide avec sous-texte"""
        from src.ui.components.atoms import empty_state

        empty_state("Aucune recette", "ðŸ½ï¸", "Ajoutez-en une")

        call_args = mock_markdown.call_args[0][0]
        assert "Ajoutez-en une" in call_args


class TestMetricCard:
    """Tests pour metric_card()"""

    @patch("streamlit.markdown")
    def test_metric_card_simple(self, mock_markdown):
        """Test carte mÃ©trique simple"""
        from src.ui.components.atoms import metric_card

        metric_card("Total", "42")

        mock_markdown.assert_called_once()
        call_args = mock_markdown.call_args[0][0]
        assert "Total" in call_args
        assert "42" in call_args

    @patch("streamlit.markdown")
    def test_metric_card_avec_delta(self, mock_markdown):
        """Test carte mÃ©trique avec delta"""
        from src.ui.components.atoms import metric_card

        metric_card("Total", "42", "+5")

        call_args = mock_markdown.call_args[0][0]
        assert "+5" in call_args

    @patch("streamlit.markdown")
    def test_metric_card_avec_couleur(self, mock_markdown):
        """Test carte mÃ©trique avec couleur"""
        from src.ui.components.atoms import metric_card

        metric_card("Total", "42", color="#f0f0f0")

        call_args = mock_markdown.call_args[0][0]
        assert "#f0f0f0" in call_args


class TestToast:
    """Tests pour toast()"""

    @patch("streamlit.success")
    def test_toast_success(self, mock_success):
        """Test toast succÃ¨s"""
        from src.ui.components.atoms import toast

        toast("Sauvegarde rÃ©ussie", "success")

        mock_success.assert_called_once_with("Sauvegarde rÃ©ussie")

    @patch("streamlit.error")
    def test_toast_error(self, mock_error):
        """Test toast erreur"""
        from src.ui.components.atoms import toast

        toast("Erreur!", "error")

        mock_error.assert_called_once_with("Erreur!")

    @patch("streamlit.warning")
    def test_toast_warning(self, mock_warning):
        """Test toast warning"""
        from src.ui.components.atoms import toast

        toast("Attention!", "warning")

        mock_warning.assert_called_once_with("Attention!")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS TOAST MANAGER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestToastManager:
    """Tests pour ToastManager"""

    @patch("streamlit.session_state", {})
    def test_toast_manager_init(self):
        """Test initialisation"""
        import streamlit as st

        from src.ui.feedback.toasts import ToastManager

        st.session_state = {}

        ToastManager._init()

        assert ToastManager.TOAST_KEY in st.session_state

    @patch("streamlit.session_state", {})
    def test_toast_manager_show(self):
        """Test ajout toast"""
        import streamlit as st

        from src.ui.feedback.toasts import ToastManager

        st.session_state = {}

        ToastManager.show("Test message", "success", 3)

        toasts = st.session_state[ToastManager.TOAST_KEY]
        assert len(toasts) == 1
        assert toasts[0]["message"] == "Test message"
        assert toasts[0]["type"] == "success"

    @patch("streamlit.session_state", {})
    @patch("streamlit.container")
    @patch("streamlit.success")
    def test_toast_manager_render(self, mock_success, mock_container):
        """Test rendu toasts"""
        import streamlit as st

        from src.ui.feedback.toasts import ToastManager

        st.session_state = {}
        mock_container.return_value.__enter__ = MagicMock(return_value=None)
        mock_container.return_value.__exit__ = MagicMock(return_value=False)

        # Ajouter un toast
        ToastManager.show("Test", "success", 60)

        # Render
        ToastManager.render()

        # VÃ©rifier que le toast a Ã©tÃ© affichÃ©
        mock_success.assert_called()


class TestToastHelpers:
    """Tests pour les helpers toast"""

    @patch("streamlit.session_state", {})
    def test_show_success(self):
        """Test show_success"""
        import streamlit as st

        from src.ui.feedback.toasts import ToastManager, show_success

        st.session_state = {}

        show_success("OK!", 3)

        toasts = st.session_state[ToastManager.TOAST_KEY]
        assert toasts[0]["type"] == "success"

    @patch("streamlit.session_state", {})
    def test_show_error(self):
        """Test show_error"""
        import streamlit as st

        from src.ui.feedback.toasts import ToastManager, show_error

        st.session_state = {}

        show_error("Erreur!", 5)

        toasts = st.session_state[ToastManager.TOAST_KEY]
        assert toasts[0]["type"] == "error"

    @patch("streamlit.session_state", {})
    def test_show_warning(self):
        """Test show_warning"""
        import streamlit as st

        from src.ui.feedback.toasts import ToastManager, show_warning

        st.session_state = {}

        show_warning("Attention!", 4)

        toasts = st.session_state[ToastManager.TOAST_KEY]
        assert toasts[0]["type"] == "warning"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS SPINNERS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestSmartSpinner:
    """Tests pour smart_spinner"""

    @patch("streamlit.spinner")
    @patch("streamlit.caption")
    def test_smart_spinner_simple(self, mock_caption, mock_spinner):
        """Test spinner simple"""
        from src.ui.feedback.spinners import smart_spinner

        mock_spinner.return_value.__enter__ = MagicMock(return_value=None)
        mock_spinner.return_value.__exit__ = MagicMock(return_value=False)

        with smart_spinner("Test operation"):
            pass

        mock_spinner.assert_called_once()
        mock_caption.assert_called()

    @patch("streamlit.spinner")
    @patch("streamlit.caption")
    def test_smart_spinner_avec_estimation(self, mock_caption, mock_spinner):
        """Test spinner avec estimation"""
        from src.ui.feedback.spinners import smart_spinner

        mock_spinner.return_value.__enter__ = MagicMock(return_value=None)
        mock_spinner.return_value.__exit__ = MagicMock(return_value=False)

        with smart_spinner("Test", estimated_seconds=5):
            pass

        call_args = mock_spinner.call_args[0][0]
        assert "estimation" in call_args


class TestLoadingIndicator:
    """Tests pour loading_indicator"""

    @patch("streamlit.markdown")
    def test_loading_indicator(self, mock_markdown):
        """Test indicateur de chargement"""
        from src.ui.feedback.spinners import loading_indicator

        loading_indicator("Chargement...")

        mock_markdown.assert_called_once()
        call_args = mock_markdown.call_args[0][0]
        assert "Chargement" in call_args


class TestSkeletonLoader:
    """Tests pour skeleton_loader"""

    @patch("streamlit.markdown")
    def test_skeleton_loader(self, mock_markdown):
        """Test skeleton loader"""
        from src.ui.feedback.spinners import skeleton_loader

        skeleton_loader(lines=3)

        assert mock_markdown.call_count == 3


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS PROGRESS TRACKER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestProgressTracker:
    """Tests pour ProgressTracker"""

    @patch("streamlit.empty")
    @patch("streamlit.progress")
    def test_progress_tracker_init(self, mock_progress, mock_empty):
        """Test initialisation"""
        from src.ui.feedback.progress import ProgressTracker

        mock_empty.return_value = MagicMock()
        mock_progress.return_value = MagicMock()

        tracker = ProgressTracker("Test", total=100)

        assert tracker.operation == "Test"
        assert tracker.total == 100
        assert tracker.current == 0

    @patch("streamlit.empty")
    @patch("streamlit.progress")
    def test_progress_tracker_update(self, mock_progress, mock_empty):
        """Test mise Ã  jour progression"""
        from src.ui.feedback.progress import ProgressTracker

        mock_empty.return_value = MagicMock()
        mock_progress.return_value = MagicMock()

        tracker = ProgressTracker("Test", total=100)
        tracker.update(50, "Mi-parcours")

        assert tracker.current == 50

    @patch("streamlit.empty")
    @patch("streamlit.progress")
    def test_progress_tracker_increment(self, mock_progress, mock_empty):
        """Test incrÃ©mentation"""
        from src.ui.feedback.progress import ProgressTracker

        mock_empty.return_value = MagicMock()
        mock_progress.return_value = MagicMock()

        tracker = ProgressTracker("Test", total=100)
        tracker.increment(10)

        assert tracker.current == 10

        tracker.increment(5)
        assert tracker.current == 15

    @patch("streamlit.empty")
    @patch("streamlit.progress")
    @patch("time.sleep")
    def test_progress_tracker_complete(self, mock_sleep, mock_progress, mock_empty):
        """Test complÃ©tion"""
        from src.ui.feedback.progress import ProgressTracker

        mock_empty.return_value = MagicMock()
        mock_progress.return_value = MagicMock()

        tracker = ProgressTracker("Test", total=100)
        tracker.complete("TerminÃ©!")

        assert tracker.current == 100

    @patch("streamlit.empty")
    @patch("streamlit.progress")
    def test_progress_tracker_error(self, mock_progress, mock_empty):
        """Test erreur"""
        from src.ui.feedback.progress import ProgressTracker

        status_mock = MagicMock()
        mock_empty.return_value = status_mock
        mock_progress.return_value = MagicMock()

        tracker = ProgressTracker("Test", total=100)
        tracker.error("Erreur critique")

        # VÃ©rifier que error() a Ã©tÃ© appelÃ© sur le placeholder
        status_mock.error.assert_called()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS DOMAIN
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestDomain:
    """Tests pour domain.py"""

    def test_import_domain(self):
        """Test import du module domain"""
        from src.ui import domain

        assert domain is not None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CORE MODULES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestBaseForm:
    """Tests pour core/base_form.py"""

    def test_import_base_form(self):
        """Test import du module base_form"""
        from src.ui.core import base_form

        assert base_form is not None


class TestBaseIO:
    """Tests pour core/base_io.py"""

    def test_import_base_io(self):
        """Test import du module base_io"""
        from src.ui.core import base_io

        assert base_io is not None


class TestBaseModule:
    """Tests pour core/base_module.py"""

    def test_import_base_module(self):
        """Test import du module base_module"""
        from src.ui.core import base_module

        assert base_module is not None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS COMPONENTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestComponentsImports:
    """Tests pour les imports des composants"""

    def test_import_components(self):
        """Test import du package components"""
        from src.ui import components

        assert components is not None

    def test_import_atoms(self):
        """Test import atoms"""
        from src.ui.components import atoms

        assert atoms is not None
        assert hasattr(atoms, "badge")
        assert hasattr(atoms, "empty_state")
        assert hasattr(atoms, "metric_card")

    def test_import_data(self):
        """Test import data"""
        from src.ui.components import data

        assert data is not None

    def test_import_dynamic(self):
        """Test import dynamic"""
        from src.ui.components import dynamic

        assert dynamic is not None

    def test_import_forms(self):
        """Test import forms"""
        from src.ui.components import forms

        assert forms is not None

    def test_import_layouts(self):
        """Test import layouts"""
        from src.ui.components import layouts

        assert layouts is not None


class TestFeedbackImports:
    """Tests pour les imports feedback"""

    def test_import_feedback(self):
        """Test import du package feedback"""
        from src.ui import feedback

        assert feedback is not None

    def test_import_progress(self):
        """Test import progress"""
        from src.ui.feedback import progress

        assert progress is not None
        assert hasattr(progress, "ProgressTracker")

    def test_import_spinners(self):
        """Test import spinners"""
        from src.ui.feedback import spinners

        assert spinners is not None
        assert hasattr(spinners, "smart_spinner")

    def test_import_toasts(self):
        """Test import toasts"""
        from src.ui.feedback import toasts

        assert toasts is not None
        assert hasattr(toasts, "ToastManager")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS LAYOUT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestLayoutImports:
    """Tests pour les imports layout"""

    def test_import_layout(self):
        """Test import du package layout"""
        from src.ui import layout

        assert layout is not None

    def test_import_header(self):
        """Test import header"""
        from src.ui.layout import header

        assert header is not None

    def test_import_footer(self):
        """Test import footer"""
        from src.ui.layout import footer

        assert footer is not None

    def test_import_sidebar(self):
        """Test import sidebar"""
        from src.ui.layout import sidebar

        assert sidebar is not None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS COMPONENTS ADDITIONNELS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestCameraScanner:
    """Tests pour camera_scanner.py"""

    def test_import_camera_scanner(self):
        """Test import camera_scanner"""
        from src.ui.components import camera_scanner

        assert camera_scanner is not None


class TestDashboardWidgets:
    """Tests pour dashboard_widgets.py"""

    def test_import_dashboard_widgets(self):
        """Test import dashboard_widgets"""
        from src.ui.components import dashboard_widgets

        assert dashboard_widgets is not None


class TestGoogleCalendarSync:
    """Tests pour google_calendar_sync.py"""

    def test_import_google_calendar_sync(self):
        """Test import google_calendar_sync"""
        from src.ui.components import google_calendar_sync

        assert google_calendar_sync is not None
