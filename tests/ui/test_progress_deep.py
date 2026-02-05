"""
Tests approfondis pour src/ui/feedback/progress.py
Objectif: Atteindre 80%+ de couverture
"""

import pytest
from unittest.mock import MagicMock, patch


# ═══════════════════════════════════════════════════════════
# TESTS PROGRESS TRACKER
# ═══════════════════════════════════════════════════════════


class TestProgressTrackerInit:
    """Tests pour ProgressTracker.__init__"""
    
    @patch("streamlit.empty")
    @patch("streamlit.progress")
    def test_init_parametres_basiques(self, mock_progress, mock_empty):
        """Test initialisation basique"""
        from src.ui.feedback.progress import ProgressTracker
        
        mock_empty.return_value = MagicMock()
        mock_progress.return_value = MagicMock()
        
        tracker = ProgressTracker("Test", total=100)
        
        assert tracker.operation == "Test"
        assert tracker.total == 100
        assert tracker.current == 0
        assert tracker.show_percentage is True
    
    @patch("streamlit.empty")
    @patch("streamlit.progress")
    def test_init_sans_pourcentage(self, mock_progress, mock_empty):
        """Test initialisation sans pourcentage"""
        from src.ui.feedback.progress import ProgressTracker
        
        mock_empty.return_value = MagicMock()
        mock_progress.return_value = MagicMock()
        
        tracker = ProgressTracker("Test", total=50, show_percentage=False)
        
        assert tracker.show_percentage is False


class TestProgressTrackerUpdate:
    """Tests pour ProgressTracker.update"""
    
    @patch("streamlit.empty")
    @patch("streamlit.progress")
    def test_update_progression(self, mock_progress, mock_empty):
        """Test mise à jour progression"""
        from src.ui.feedback.progress import ProgressTracker
        
        mock_placeholder = MagicMock()
        mock_empty.return_value = mock_placeholder
        mock_bar = MagicMock()
        mock_progress.return_value = mock_bar
        
        tracker = ProgressTracker("Test", total=100)
        tracker.update(50, "À mi-chemin")
        
        assert tracker.current == 50
        mock_bar.progress.assert_called()
    
    @patch("streamlit.empty")
    @patch("streamlit.progress")
    def test_update_sans_status(self, mock_progress, mock_empty):
        """Test mise à jour sans status"""
        from src.ui.feedback.progress import ProgressTracker
        
        mock_empty.return_value = MagicMock()
        mock_progress.return_value = MagicMock()
        
        tracker = ProgressTracker("Test", total=100)
        tracker.update(75)
        
        assert tracker.current == 75


class TestProgressTrackerIncrement:
    """Tests pour ProgressTracker.increment"""
    
    @patch("streamlit.empty")
    @patch("streamlit.progress")
    def test_increment_default(self, mock_progress, mock_empty):
        """Test incrémentation par défaut"""
        from src.ui.feedback.progress import ProgressTracker
        
        mock_empty.return_value = MagicMock()
        mock_progress.return_value = MagicMock()
        
        tracker = ProgressTracker("Test", total=10)
        tracker.increment()
        
        assert tracker.current == 1
    
    @patch("streamlit.empty")
    @patch("streamlit.progress")
    def test_increment_custom_step(self, mock_progress, mock_empty):
        """Test incrémentation avec step personnalisé"""
        from src.ui.feedback.progress import ProgressTracker
        
        mock_empty.return_value = MagicMock()
        mock_progress.return_value = MagicMock()
        
        tracker = ProgressTracker("Test", total=100)
        tracker.increment(step=10)
        
        assert tracker.current == 10
    
    @patch("streamlit.empty")
    @patch("streamlit.progress")
    def test_increment_avec_status(self, mock_progress, mock_empty):
        """Test incrémentation avec status"""
        from src.ui.feedback.progress import ProgressTracker
        
        mock_empty.return_value = MagicMock()
        mock_progress.return_value = MagicMock()
        
        tracker = ProgressTracker("Test", total=10)
        tracker.increment(step=1, status="En cours")
        
        assert tracker.current == 1
    
    @patch("streamlit.empty")
    @patch("streamlit.progress")
    def test_increment_ne_depasse_pas_total(self, mock_progress, mock_empty):
        """Test incrémentation ne dépasse pas total"""
        from src.ui.feedback.progress import ProgressTracker
        
        mock_empty.return_value = MagicMock()
        mock_progress.return_value = MagicMock()
        
        tracker = ProgressTracker("Test", total=10)
        tracker.increment(step=20)
        
        assert tracker.current == 10  # Limité au total


class TestProgressTrackerComplete:
    """Tests pour ProgressTracker.complete"""
    
    @patch("time.sleep")
    @patch("streamlit.empty")
    @patch("streamlit.progress")
    def test_complete_sans_message(self, mock_progress, mock_empty, mock_sleep):
        """Test complétion sans message"""
        from src.ui.feedback.progress import ProgressTracker
        
        mock_placeholder = MagicMock()
        mock_empty.return_value = mock_placeholder
        mock_progress.return_value = MagicMock()
        
        tracker = ProgressTracker("Test", total=100)
        tracker.complete()
        
        assert tracker.current == 100
        mock_placeholder.success.assert_called()
    
    @patch("time.sleep")
    @patch("streamlit.empty")
    @patch("streamlit.progress")
    def test_complete_avec_message(self, mock_progress, mock_empty, mock_sleep):
        """Test complétion avec message"""
        from src.ui.feedback.progress import ProgressTracker
        
        mock_placeholder = MagicMock()
        mock_empty.return_value = mock_placeholder
        mock_progress.return_value = MagicMock()
        
        tracker = ProgressTracker("Test", total=100)
        tracker.complete("Import réussi!")
        
        assert tracker.current == 100
        # Vérifier que le message personnalisé est utilisé
        call_args = mock_placeholder.success.call_args
        assert "Import réussi" in str(call_args)


class TestProgressTrackerError:
    """Tests pour ProgressTracker.error"""
    
    @patch("streamlit.empty")
    @patch("streamlit.progress")
    def test_error_message(self, mock_progress, mock_empty):
        """Test affichage erreur"""
        from src.ui.feedback.progress import ProgressTracker
        
        mock_placeholder = MagicMock()
        mock_empty.return_value = mock_placeholder
        mock_progress.return_value = MagicMock()
        
        tracker = ProgressTracker("Test", total=100)
        tracker.error("Une erreur est survenue")
        
        mock_placeholder.error.assert_called()


class TestProgressTrackerUpdateDisplay:
    """Tests pour ProgressTracker._update_display"""
    
    @patch("streamlit.empty")
    @patch("streamlit.progress")
    def test_update_display_avec_pourcentage(self, mock_progress, mock_empty):
        """Test affichage avec pourcentage"""
        from src.ui.feedback.progress import ProgressTracker
        
        mock_placeholder = MagicMock()
        mock_empty.return_value = mock_placeholder
        mock_bar = MagicMock()
        mock_progress.return_value = mock_bar
        
        tracker = ProgressTracker("Import", total=100, show_percentage=True)
        tracker.current = 50
        tracker._update_display()
        
        # Vérifier affichage pourcentage
        call_args = mock_placeholder.markdown.call_args
        assert "50%" in str(call_args)
    
    @patch("streamlit.empty")
    @patch("streamlit.progress")
    def test_update_display_sans_pourcentage(self, mock_progress, mock_empty):
        """Test affichage sans pourcentage (fraction)"""
        from src.ui.feedback.progress import ProgressTracker
        
        mock_placeholder = MagicMock()
        mock_empty.return_value = mock_placeholder
        mock_bar = MagicMock()
        mock_progress.return_value = mock_bar
        
        tracker = ProgressTracker("Import", total=100, show_percentage=False)
        tracker.current = 50
        tracker._update_display()
        
        # Vérifier affichage fraction
        call_args = mock_placeholder.markdown.call_args
        assert "50/100" in str(call_args)
    
    @patch("streamlit.empty")
    @patch("streamlit.progress")
    def test_update_display_temps_restant(self, mock_progress, mock_empty):
        """Test affichage temps restant"""
        from src.ui.feedback.progress import ProgressTracker
        from datetime import datetime, timedelta
        
        mock_placeholder = MagicMock()
        mock_empty.return_value = mock_placeholder
        mock_bar = MagicMock()
        mock_progress.return_value = mock_bar
        
        tracker = ProgressTracker("Import", total=100)
        # Simuler du temps écoulé
        tracker.start_time = datetime.now() - timedelta(seconds=10)
        tracker.current = 50
        tracker._update_display("En cours")
        
        # Vérifier que le temps restant est affiché
        mock_placeholder.caption.assert_called()
    
    @patch("streamlit.empty")
    @patch("streamlit.progress")
    def test_update_display_total_zero(self, mock_progress, mock_empty):
        """Test affichage avec total zéro"""
        from src.ui.feedback.progress import ProgressTracker
        
        mock_placeholder = MagicMock()
        mock_empty.return_value = mock_placeholder
        mock_bar = MagicMock()
        mock_progress.return_value = mock_bar
        
        tracker = ProgressTracker("Import", total=0)
        tracker._update_display()
        
        # Ne doit pas lever d'erreur de division
        mock_bar.progress.assert_called_with(0)


# ═══════════════════════════════════════════════════════════
# TESTS LOADING STATE
# ═══════════════════════════════════════════════════════════


class TestLoadingStateInit:
    """Tests pour LoadingState.__init__"""
    
    @patch("streamlit.empty")
    def test_init_basique(self, mock_empty):
        """Test initialisation basique"""
        from src.ui.feedback.progress import LoadingState
        
        mock_empty.return_value = MagicMock()
        
        loader = LoadingState("Chargement données")
        
        assert loader.title == "Chargement données"
        assert loader.steps == []
        assert loader.current_step is None


class TestLoadingStateAddStep:
    """Tests pour LoadingState.add_step"""
    
    @patch("streamlit.empty")
    def test_add_step(self, mock_empty):
        """Test ajout étape"""
        from src.ui.feedback.progress import LoadingState
        
        mock_empty.return_value = MagicMock()
        
        loader = LoadingState("Test")
        loader.add_step("Connexion DB")
        
        assert len(loader.steps) == 1
        assert loader.steps[0]["name"] == "Connexion DB"
        assert loader.steps[0]["completed"] is False
        assert loader.current_step == 0
    
    @patch("streamlit.empty")
    def test_add_multiple_steps(self, mock_empty):
        """Test ajout plusieurs étapes"""
        from src.ui.feedback.progress import LoadingState
        
        mock_empty.return_value = MagicMock()
        
        loader = LoadingState("Test")
        loader.add_step("Étape 1")
        loader.add_step("Étape 2")
        loader.add_step("Étape 3")
        
        assert len(loader.steps) == 3
        assert loader.current_step == 2


class TestLoadingStateCompleteStep:
    """Tests pour LoadingState.complete_step"""
    
    @patch("streamlit.empty")
    def test_complete_step_par_nom(self, mock_empty):
        """Test complétion étape par nom"""
        from src.ui.feedback.progress import LoadingState
        
        mock_empty.return_value = MagicMock()
        
        loader = LoadingState("Test")
        loader.add_step("Connexion DB")
        loader.complete_step("Connexion DB")
        
        assert loader.steps[0]["completed"] is True
        assert "✅" in loader.steps[0]["status"]
    
    @patch("streamlit.empty")
    def test_complete_step_current(self, mock_empty):
        """Test complétion étape courante"""
        from src.ui.feedback.progress import LoadingState
        
        mock_empty.return_value = MagicMock()
        
        loader = LoadingState("Test")
        loader.add_step("Étape courante")
        loader.complete_step()
        
        assert loader.steps[0]["completed"] is True
    
    @patch("streamlit.empty")
    def test_complete_step_echec(self, mock_empty):
        """Test complétion étape en échec"""
        from src.ui.feedback.progress import LoadingState
        
        mock_empty.return_value = MagicMock()
        
        loader = LoadingState("Test")
        loader.add_step("Étape")
        loader.complete_step("Étape", success=False)
        
        assert loader.steps[0]["completed"] is True
        assert "❌" in loader.steps[0]["status"]
    
    @patch("streamlit.empty")
    def test_complete_step_inexistant(self, mock_empty):
        """Test complétion étape inexistante"""
        from src.ui.feedback.progress import LoadingState
        
        mock_empty.return_value = MagicMock()
        
        loader = LoadingState("Test")
        loader.add_step("Étape réelle")
        
        # Ne doit pas lever d'erreur
        loader.complete_step("Étape inexistante")


class TestLoadingStateErrorStep:
    """Tests pour LoadingState.error_step"""
    
    @patch("streamlit.empty")
    def test_error_step_avec_message(self, mock_empty):
        """Test erreur étape avec message"""
        from src.ui.feedback.progress import LoadingState
        
        mock_empty.return_value = MagicMock()
        
        loader = LoadingState("Test")
        loader.add_step("Connexion")
        loader.error_step("Connexion", "Timeout")
        
        assert "❌" in loader.steps[0]["status"]
        assert "Timeout" in loader.steps[0]["status"]
    
    @patch("streamlit.empty")
    def test_error_step_sans_message(self, mock_empty):
        """Test erreur étape sans message"""
        from src.ui.feedback.progress import LoadingState
        
        mock_empty.return_value = MagicMock()
        
        loader = LoadingState("Test")
        loader.add_step("Étape")
        loader.error_step()
        
        assert "❌" in loader.steps[0]["status"]
    
    @patch("streamlit.empty")
    def test_error_step_inexistant(self, mock_empty):
        """Test erreur étape inexistante"""
        from src.ui.feedback.progress import LoadingState
        
        mock_empty.return_value = MagicMock()
        
        loader = LoadingState("Test")
        
        # Ne doit pas lever d'erreur
        loader.error_step("Inexistant", "Message")


class TestLoadingStateFinish:
    """Tests pour LoadingState.finish"""
    
    @patch("time.sleep")
    @patch("streamlit.empty")
    def test_finish_sans_message(self, mock_empty, mock_sleep):
        """Test fin sans message"""
        from src.ui.feedback.progress import LoadingState
        
        mock_placeholder = MagicMock()
        mock_empty.return_value = mock_placeholder
        
        loader = LoadingState("Import données")
        loader.finish()
        
        mock_placeholder.success.assert_called()
    
    @patch("time.sleep")
    @patch("streamlit.empty")
    def test_finish_avec_message(self, mock_empty, mock_sleep):
        """Test fin avec message personnalisé"""
        from src.ui.feedback.progress import LoadingState
        
        mock_placeholder = MagicMock()
        mock_empty.return_value = mock_placeholder
        
        loader = LoadingState("Import")
        loader.finish("Import réussi avec 100 éléments")
        
        call_args = mock_placeholder.success.call_args
        assert "100 éléments" in str(call_args)


class TestLoadingStateUpdateDisplay:
    """Tests pour LoadingState._update_display"""
    
    @patch("streamlit.empty")
    def test_update_display_with_steps(self, mock_empty):
        """Test affichage avec étapes"""
        from src.ui.feedback.progress import LoadingState
        
        mock_placeholder = MagicMock()
        mock_empty.return_value = mock_placeholder
        
        loader = LoadingState("Test")
        loader.add_step("Étape 1")
        loader.add_step("Étape 2")
        loader.complete_step("Étape 1")
        loader._update_display()
        
        # Vérifier que markdown est appelé
        mock_placeholder.markdown.assert_called()
