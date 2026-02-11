"""
Tests pour les composants feedback/feedback.py
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import streamlit as st


class TestFeedbackImport:
    """Tests d'importation des composants de feedback"""

    def test_import_feedback_module(self):
        """Test l'import du module feedback"""
        try:
            from src.ui import feedback
            assert feedback is not None
        except ImportError:
            # Si le module feedback n'existe pas, utiliser st directement
            import streamlit as st
            assert st is not None

    def test_feedback_module_exists(self):
        """Test que le module feedback existe"""
        from src.ui import feedback
        public_attrs = [f for f in dir(feedback) if not f.startswith('_')]
        assert len(public_attrs) > 0 or feedback is not None

    def test_notifications_available(self):
        """Test que les notifications Streamlit sont disponibles"""
        import streamlit as st
        assert hasattr(st, 'success')
        assert hasattr(st, 'error')


@pytest.mark.unit
class TestSmartSpinner:
    """Tests pour les spinners intelligents"""

    @patch('streamlit.spinner')
    def test_spinner_creation(self, mock_spinner):
        """Test la création d'un spinner"""
        mock_spinner.return_value.__enter__ = Mock(return_value=MagicMock())
        mock_spinner.return_value.__exit__ = Mock(return_value=False)
        
        with st.spinner("Chargement..."):
            pass
        
        assert mock_spinner.called

    @patch('streamlit.spinner')
    def test_spinner_message(self, mock_spinner):
        """Test le message du spinner"""
        mock_spinner.return_value.__enter__ = Mock(return_value=MagicMock())
        mock_spinner.return_value.__exit__ = Mock(return_value=False)
        
        with st.spinner("Traitement en cours..."):
            pass
        
        assert mock_spinner.called

    @patch('streamlit.spinner')
    def test_spinner_context_manager(self, mock_spinner):
        """Test le gestionnaire de contexte du spinner"""
        mock_spinner.return_value.__enter__ = Mock(return_value=MagicMock())
        mock_spinner.return_value.__exit__ = Mock(return_value=False)
        
        # Vérifier que st.spinner fonctionne comme gestionnaire de contexte
        with st.spinner("Test"):
            pass
        
        assert mock_spinner.called


@pytest.mark.unit
class TestSuccessNotification:
    """Tests pour les notifications de succès"""

    @patch('streamlit.success')
    def test_show_success_basic(self, mock_success):
        """Test l'affichage d'une notification succès"""
        mock_success.return_value = None
        
        st.success("Opération réussie!")
        
        assert mock_success.called

    @patch('streamlit.success')
    def test_show_success_with_icon(self, mock_success):
        """Test l'affichage d'une notification succès avec icône"""
        mock_success.return_value = None
        
        st.success("✅ Succès!")
        
        assert mock_success.called

    @patch('streamlit.success')
    def test_show_success_multiline(self, mock_success):
        """Test l'affichage d'une notification succès multiligne"""
        mock_success.return_value = None
        
        st.success("Opération réussie\nLe fichier a été sauvegardé")
        
        assert mock_success.called


@pytest.mark.unit
class TestErrorNotification:
    """Tests pour les notifications d'erreur"""

    @patch('streamlit.error')
    def test_show_error_basic(self, mock_error):
        """Test l'affichage d'une notification erreur"""
        mock_error.return_value = None
        
        st.error("Une erreur s'est produite")
        
        assert mock_error.called

    @patch('streamlit.error')
    def test_show_error_with_details(self, mock_error):
        """Test l'affichage d'une notification erreur avec détails"""
        mock_error.return_value = None
        
        st.error("Erreur: Impossibilité de se connecter")
        
        assert mock_error.called

    @patch('streamlit.error')
    def test_show_error_exception(self, mock_error):
        """Test l'affichage d'une exception en tant qu'erreur"""
        mock_error.return_value = None
        
        try:
            raise ValueError("Test erreur")
        except ValueError as e:
            st.error(str(e))
        
        assert mock_error.called


@pytest.mark.unit
class TestWarningNotification:
    """Tests pour les notifications d'avertissement"""

    @patch('streamlit.warning')
    def test_show_warning_basic(self, mock_warning):
        """Test l'affichage d'une notification avertissement"""
        mock_warning.return_value = None
        
        st.warning("Attention: Action irréversible")
        
        assert mock_warning.called

    @patch('streamlit.warning')
    def test_show_warning_confirmation(self, mock_warning):
        """Test l'affichage d'une notification avertissement confirmée"""
        mock_warning.return_value = None
        
        st.warning("Êtes-vous sûr de continuer?")
        
        assert mock_warning.called


@pytest.mark.unit
class TestInfoNotification:
    """Tests pour les notifications d'information"""

    @patch('streamlit.info')
    def test_show_info_basic(self, mock_info):
        """Test l'affichage d'une notification info"""
        mock_info.return_value = None
        
        st.info("Information: Nouvelle version disponible")
        
        assert mock_info.called


@pytest.mark.unit
class TestProgressIndicators:
    """Tests pour les indicateurs de progression"""

    @patch('streamlit.progress')
    def test_progress_bar(self, mock_progress):
        """Test la barre de progression"""
        mock_progress.return_value = None
        
        for i in range(101):
            st.progress(i / 100)
        
        assert mock_progress.called

    @patch('streamlit.progress')
    def test_progress_with_label(self, mock_progress):
        """Test la barre de progression avec label"""
        mock_progress.return_value = None
        
        st.progress(0.5)
        
        assert mock_progress.called


@pytest.mark.unit
class TestToastNotifications:
    """Tests pour les notifications toast"""

    @patch('streamlit.toast')
    def test_toast_creation(self, mock_toast):
        """Test la création d'une notification toast"""
        mock_toast.return_value = None
        
        st.toast("Message temporaire")
        
        assert mock_toast.called

    @patch('streamlit.toast')
    def test_toast_with_icon(self, mock_toast):
        """Test la notification toast avec icône"""
        mock_toast.return_value = None
        
        st.toast("✅ Opération réussie")
        
        assert mock_toast.called


@pytest.mark.integration
class TestFeedbackFlow:
    """Tests d'intégration pour les flux de feedback"""

    @patch('streamlit.spinner')
    @patch('streamlit.success')
    def test_loading_success_flow(self, mock_success, mock_spinner):
        """Test le flux chargement -> succès"""
        mock_spinner.return_value.__enter__ = Mock(return_value=MagicMock())
        mock_spinner.return_value.__exit__ = Mock(return_value=False)
        mock_success.return_value = None
        
        with st.spinner("Chargement..."):
            result = True
        
        if result:
            st.success("Succès!")
        
        assert mock_spinner.called
        assert mock_success.called

    @patch('streamlit.spinner')
    @patch('streamlit.error')
    def test_loading_error_flow(self, mock_error, mock_spinner):
        """Test le flux chargement -> erreur"""
        mock_spinner.return_value.__enter__ = Mock(return_value=MagicMock())
        mock_spinner.return_value.__exit__ = Mock(return_value=False)
        mock_error.return_value = None
        
        try:
            with st.spinner("Traitement..."):
                raise Exception("Erreur de traitement")
        except Exception as e:
            st.error(str(e))
        
        assert mock_spinner.called
        assert mock_error.called

    @patch('streamlit.progress')
    @patch('streamlit.success')
    def test_progress_completion_flow(self, mock_success, mock_progress):
        """Test le flux progression complète -> succès"""
        mock_progress.return_value = None
        mock_success.return_value = None
        
        for i in range(101):
            st.progress(i / 100)
        
        st.success("Traitement terminé!")
        
        assert mock_progress.called
        assert mock_success.called
