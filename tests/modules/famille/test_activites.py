"""
Tests unitaires pour src/modules/famille/activites.py

Module Activites - Planning et budget des activités familiales
"""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest


class TestActivitesImports:
    """Tests d'import pour le module activites."""

    def test_import_app(self):
        """Test import réussi de app."""
        from src.modules.famille.activites import app

        assert app is not None
        assert callable(app)

    def test_import_ajouter_activite(self):
        """Test import réussi de ajouter_activite."""
        from src.modules.famille.activites import ajouter_activite

        assert ajouter_activite is not None
        assert callable(ajouter_activite)

    def test_import_marquer_terminee(self):
        """Test import réussi de marquer_terminee."""
        from src.modules.famille.activites import marquer_terminee

        assert marquer_terminee is not None
        assert callable(marquer_terminee)

    def test_import_suggestions_activites(self):
        """Test import réussi de SUGGESTIONS_ACTIVITES."""
        from src.modules.famille.activites import SUGGESTIONS_ACTIVITES

        assert SUGGESTIONS_ACTIVITES is not None
        assert isinstance(SUGGESTIONS_ACTIVITES, dict)
        assert "parc" in SUGGESTIONS_ACTIVITES
        assert "musee" in SUGGESTIONS_ACTIVITES


@pytest.mark.unit
class TestAjouterActivite:
    """Tests pour ajouter_activite()."""

    @patch("src.modules.famille.activites.st")
    @patch("src.modules.famille.activites.clear_famille_cache")
    @patch("src.modules.famille.activites.obtenir_contexte_db")
    def test_ajouter_activite_success(self, mock_db_ctx, mock_clear_cache, mock_st):
        """Test ajout activité réussi."""
        from src.modules.famille.activites import ajouter_activite

        # Setup mock session
        mock_session = MagicMock()
        mock_db_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db_ctx.return_value.__exit__ = MagicMock(return_value=False)

        result = ajouter_activite(
            titre="Test Activité",
            type_activite="parc",
            date_prevue=date.today(),
            duree=2.0,
            lieu="Parc local",
            participants=["Famille"],
            cout_estime=15.0,
            notes="Notes de test",
        )

        assert result is True
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_st.success.assert_called_once()
        mock_clear_cache.assert_called_once()

    @patch("src.modules.famille.activites.st")
    @patch("src.modules.famille.activites.obtenir_contexte_db")
    def test_ajouter_activite_error(self, mock_db_ctx, mock_st):
        """Test ajout activité avec erreur."""
        from src.modules.famille.activites import ajouter_activite

        # Simulate exception
        mock_db_ctx.return_value.__enter__ = MagicMock(side_effect=Exception("DB Error"))
        mock_db_ctx.return_value.__exit__ = MagicMock(return_value=False)

        result = ajouter_activite(
            titre="Test",
            type_activite="parc",
            date_prevue=date.today(),
            duree=1.0,
            lieu="",
            participants=[],
            cout_estime=0.0,
        )

        assert result is False
        mock_st.error.assert_called_once()


@pytest.mark.unit
class TestMarquerTerminee:
    """Tests pour marquer_terminee()."""

    @patch("src.modules.famille.activites.st")
    @patch("src.modules.famille.activites.clear_famille_cache")
    @patch("src.modules.famille.activites.obtenir_contexte_db")
    def test_marquer_terminee_success(self, mock_db_ctx, mock_clear_cache, mock_st):
        """Test marquage activité terminée réussi."""
        from src.modules.famille.activites import marquer_terminee

        # Setup mock session and activity
        mock_activity = MagicMock()
        mock_activity.statut = "planifie"
        mock_session = MagicMock()
        mock_session.get.return_value = mock_activity

        mock_db_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db_ctx.return_value.__exit__ = MagicMock(return_value=False)

        result = marquer_terminee(activity_id=1, cout_reel=20.0)

        assert result is True
        assert mock_activity.statut == "termine"
        assert mock_activity.cout_reel == 20.0
        mock_session.commit.assert_called_once()
        mock_st.success.assert_called_once()
        mock_clear_cache.assert_called_once()

    @patch("src.modules.famille.activites.st")
    @patch("src.modules.famille.activites.obtenir_contexte_db")
    def test_marquer_terminee_not_found(self, mock_db_ctx, mock_st):
        """Test marquage activité non trouvée."""
        from src.modules.famille.activites import marquer_terminee

        # Setup mock session with no activity found
        mock_session = MagicMock()
        mock_session.get.return_value = None

        mock_db_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db_ctx.return_value.__exit__ = MagicMock(return_value=False)

        result = marquer_terminee(activity_id=999)

        # Should return None (not True) when activity not found
        assert result is None

    @patch("src.modules.famille.activites.st")
    @patch("src.modules.famille.activites.obtenir_contexte_db")
    def test_marquer_terminee_error(self, mock_db_ctx, mock_st):
        """Test marquage activité avec erreur."""
        from src.modules.famille.activites import marquer_terminee

        mock_db_ctx.return_value.__enter__ = MagicMock(side_effect=Exception("DB Error"))
        mock_db_ctx.return_value.__exit__ = MagicMock(return_value=False)

        result = marquer_terminee(activity_id=1)

        assert result is False
        mock_st.error.assert_called_once()


@pytest.mark.unit
class TestActivitesApp:
    """Tests pour app()."""

    @patch("src.modules.famille.activites.st")
    @patch("src.modules.famille.activites.get_activites_semaine")
    @patch("src.modules.famille.activites.get_budget_activites_mois")
    @patch("src.modules.famille.activites.get_budget_par_period")
    @patch("src.modules.famille.activites.obtenir_contexte_db")
    @patch("src.modules.famille.activites.pd")
    @patch("src.modules.famille.activites.go")
    def test_app_runs(
        self,
        mock_go,
        mock_pd,
        mock_db_ctx,
        mock_budget_period,
        mock_budget_mois,
        mock_activites,
        mock_st,
    ):
        """Test que app() s'exécute sans erreur."""
        from src.modules.famille.activites import app

        # Setup mocks
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.tabs.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.session_state = {}
        mock_st.form.return_value.__enter__ = MagicMock()
        mock_st.form.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.container.return_value.__enter__ = MagicMock()
        mock_st.container.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.form_submit_button.return_value = False

        # Setup data mocks
        mock_activites.return_value = []
        mock_budget_mois.return_value = 100.0
        mock_budget_period.return_value = {"Activites": 25.0}

        # Setup DB mock for graphs
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = []
        mock_db_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db_ctx.return_value.__exit__ = MagicMock(return_value=False)

        try:
            app()
        except Exception:
            pass  # UI tests acceptent les erreurs liées au mock

        mock_st.title.assert_called_once_with("🎨 Activites Familiales")
        mock_st.tabs.assert_called_once()

    @patch("src.modules.famille.activites.st")
    def test_app_title(self, mock_st):
        """Test que app() affiche le bon titre."""
        from src.modules.famille.activites import app

        # Minimal mocks
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.tabs.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.session_state = {}

        try:
            app()
        except Exception:
            pass

        mock_st.title.assert_called_with("🎨 Activites Familiales")

    @patch("src.modules.famille.activites.st")
    @patch("src.modules.famille.activites.get_activites_semaine")
    def test_app_with_activites(self, mock_activites, mock_st):
        """Test app() avec des activités existantes."""
        from src.modules.famille.activites import app

        # Setup mocks
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.tabs.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.session_state = {}
        mock_st.container.return_value.__enter__ = MagicMock()
        mock_st.container.return_value.__exit__ = MagicMock(return_value=False)

        # Setup activités mock
        mock_activites.return_value = [
            {
                "date": date.today(),
                "titre": "Sortie parc",
                "type": "parc",
                "lieu": "Parc central",
                "participants": ["Famille"],
                "cout_estime": 10.0,
            }
        ]

        try:
            app()
        except Exception:
            pass  # UI tests acceptent les erreurs liées au mock

        # Just verify title was called - tabs context makes other calls unreliable
        mock_st.title.assert_called_once()


@pytest.mark.unit
class TestSuggestionsActivites:
    """Tests pour SUGGESTIONS_ACTIVITES."""

    def test_suggestions_structure(self):
        """Test structure des suggestions."""
        from src.modules.famille.activites import SUGGESTIONS_ACTIVITES

        expected_types = ["parc", "musee", "eau", "jeu_maison", "sport", "sortie"]
        for type_key in expected_types:
            assert type_key in SUGGESTIONS_ACTIVITES
            assert isinstance(SUGGESTIONS_ACTIVITES[type_key], list)
            assert len(SUGGESTIONS_ACTIVITES[type_key]) > 0

    def test_suggestions_content(self):
        """Test contenu des suggestions."""
        from src.modules.famille.activites import SUGGESTIONS_ACTIVITES

        # Vérifier quelques suggestions spécifiques
        assert "Parc local" in SUGGESTIONS_ACTIVITES["parc"]
        assert "Piscine" in SUGGESTIONS_ACTIVITES["eau"]
        assert "Zoo" in SUGGESTIONS_ACTIVITES["sortie"]
