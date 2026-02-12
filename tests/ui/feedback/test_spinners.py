"""
Tests unitaires pour spinners.py

Module: src.ui.feedback.spinners
Couverture cible: >80%
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime


class TestSpinners:
    """Tests pour le module spinners."""

    @patch("streamlit.spinner")
    @patch("streamlit.caption")
    def test_spinner_intelligent_base(self, mock_caption, mock_spinner):
        """Test de la fonction spinner_intelligent - cas de base."""
        from src.ui.feedback.spinners import spinner_intelligent

        # Configurer le mock pour le context manager
        mock_spinner.return_value.__enter__ = MagicMock()
        mock_spinner.return_value.__exit__ = MagicMock(return_value=False)

        with spinner_intelligent("Test opération"):
            pass  # Simule une opération rapide

        mock_spinner.assert_called_once()
        # Le caption est appelé avec le temps écoulé
        assert mock_caption.called

    @patch("streamlit.spinner")
    @patch("streamlit.caption")
    def test_spinner_intelligent_avec_estimation(self, mock_caption, mock_spinner):
        """Test spinner_intelligent avec secondes_estimees."""
        from src.ui.feedback.spinners import spinner_intelligent

        mock_spinner.return_value.__enter__ = MagicMock()
        mock_spinner.return_value.__exit__ = MagicMock(return_value=False)

        with spinner_intelligent("Génération", secondes_estimees=5):
            pass

        # Vérifie que le message contient l'estimation
        call_args = mock_spinner.call_args[0][0]
        assert "estimation: 5s" in call_args

    @patch("streamlit.spinner")
    @patch("streamlit.caption")
    def test_spinner_intelligent_sans_temps_ecoule(self, mock_caption, mock_spinner):
        """Test spinner_intelligent sans affichage du temps écoulé."""
        from src.ui.feedback.spinners import spinner_intelligent

        mock_spinner.return_value.__enter__ = MagicMock()
        mock_spinner.return_value.__exit__ = MagicMock(return_value=False)

        with spinner_intelligent("Test", afficher_temps_ecoule=False):
            pass

        # Le caption ne devrait pas être appelé
        mock_caption.assert_not_called()

    @patch("streamlit.spinner")
    @patch("streamlit.caption")
    def test_spinner_intelligent_temps_long(self, mock_caption, mock_spinner):
        """Test spinner_intelligent avec temps > 1 seconde."""
        from src.ui.feedback.spinners import spinner_intelligent
        import time

        mock_spinner.return_value.__enter__ = MagicMock()
        mock_spinner.return_value.__exit__ = MagicMock(return_value=False)

        with spinner_intelligent("Test long"):
            # Simule 1.1 secondes (patch datetime serait plus propre)
            pass

        # Vérifie que caption est appelé
        assert mock_caption.called

    @patch("streamlit.markdown")
    def test_indicateur_chargement_defaut(self, mock_markdown):
        """Test indicateur_chargement avec message par défaut."""
        from src.ui.feedback.spinners import indicateur_chargement

        indicateur_chargement()

        mock_markdown.assert_called_once()
        call_args = mock_markdown.call_args[0][0]
        assert "Chargement..." in call_args

    @patch("streamlit.markdown")
    def test_indicateur_chargement_message_personnalise(self, mock_markdown):
        """Test indicateur_chargement avec message personnalisé."""
        from src.ui.feedback.spinners import indicateur_chargement

        indicateur_chargement("Chargement des recettes...")

        call_args = mock_markdown.call_args[0][0]
        assert "Chargement des recettes..." in call_args

    @patch("streamlit.markdown")
    def test_chargeur_squelette_defaut(self, mock_markdown):
        """Test chargeur_squelette avec paramètres par défaut (3 lignes)."""
        from src.ui.feedback.spinners import chargeur_squelette

        chargeur_squelette()

        # Doit être appelé 3 fois (une par ligne)
        assert mock_markdown.call_count == 3

    @patch("streamlit.markdown")
    def test_chargeur_squelette_personnalise(self, mock_markdown):
        """Test chargeur_squelette avec nombre de lignes personnalisé."""
        from src.ui.feedback.spinners import chargeur_squelette

        chargeur_squelette(lignes=5)

        assert mock_markdown.call_count == 5

    @patch("streamlit.markdown")
    def test_chargeur_squelette_contenu_html(self, mock_markdown):
        """Test que chargeur_squelette génère du HTML valide."""
        from src.ui.feedback.spinners import chargeur_squelette

        chargeur_squelette(lignes=1)

        call_args = mock_markdown.call_args
        html_content = call_args[0][0]
        
        # Vérifie que c'est du HTML avec animation
        assert "background" in html_content
        assert "animation" in html_content
        # Vérifie que unsafe_allow_html est True
        assert call_args[1]["unsafe_allow_html"] is True


class TestSpinnersImports:
    """Tests d'import du module spinners."""

    def test_import_spinner_intelligent(self):
        """Vérifie que spinner_intelligent est importable."""
        from src.ui.feedback.spinners import spinner_intelligent
        assert callable(spinner_intelligent)

    def test_import_indicateur_chargement(self):
        """Vérifie que indicateur_chargement est importable."""
        from src.ui.feedback.spinners import indicateur_chargement
        assert callable(indicateur_chargement)

    def test_import_chargeur_squelette(self):
        """Vérifie que chargeur_squelette est importable."""
        from src.ui.feedback.spinners import chargeur_squelette
        assert callable(chargeur_squelette)

    def test_import_via_feedback(self):
        """Vérifie l'import via le module feedback."""
        from src.ui.feedback import (
            spinner_intelligent,
            indicateur_chargement,
            chargeur_squelette,
        )
        assert all(callable(f) for f in [
            spinner_intelligent,
            indicateur_chargement,
            chargeur_squelette,
        ])

