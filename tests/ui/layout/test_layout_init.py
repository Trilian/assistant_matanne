"""
Tests unitaires pour src/ui/layout/initialisation.py
"""

from unittest.mock import MagicMock, patch

import pytest


class TestInitialiserApp:
    """Tests pour initialiser_app()."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.layout.initialisation import initialiser_app

        assert initialiser_app is not None

    @patch("src.core.ai.obtenir_client_ia")
    @patch("src.ui.layout.initialisation.st")
    @patch("src.ui.layout.initialisation.obtenir_etat")
    @patch("src.ui.layout.initialisation.verifier_connexion", return_value=True)
    @patch("src.ui.layout.initialisation.GestionnaireEtat")
    def test_initialiser_success(self, mock_gest, mock_conn, mock_etat, mock_st, mock_ia):
        """Test initialisation réussie."""
        from src.ui.layout.initialisation import initialiser_app

        mock_etat.return_value = MagicMock(agent_ia=None)
        mock_ia.return_value = MagicMock()

        result = initialiser_app()

        assert result is True
        mock_gest.initialiser.assert_called_once()

    @patch("src.ui.layout.initialisation.st")
    @patch("src.ui.layout.initialisation.obtenir_etat")
    @patch("src.ui.layout.initialisation.verifier_connexion", return_value=False)
    @patch("src.ui.layout.initialisation.GestionnaireEtat")
    def test_initialiser_db_fail(self, mock_gest, mock_conn, mock_etat, mock_st):
        """Test échec connexion DB."""
        from src.ui.layout.initialisation import initialiser_app

        # st.stop() raises an exception
        mock_st.stop.side_effect = SystemExit

        with pytest.raises(SystemExit):
            initialiser_app()

        mock_st.error.assert_called()

    @patch("src.core.ai.obtenir_client_ia", side_effect=Exception("IA Error"))
    @patch("src.ui.layout.initialisation.st")
    @patch("src.ui.layout.initialisation.obtenir_etat")
    @patch("src.ui.layout.initialisation.verifier_connexion", return_value=True)
    @patch("src.ui.layout.initialisation.GestionnaireEtat")
    def test_initialiser_ia_error(self, mock_gest, mock_conn, mock_etat, mock_st, mock_ia):
        """Test erreur client IA - continue sans bloquer."""
        from src.ui.layout.initialisation import initialiser_app

        mock_etat.return_value = MagicMock(agent_ia=None)

        result = initialiser_app()

        # Should still succeed even if IA fails
        assert result is True
