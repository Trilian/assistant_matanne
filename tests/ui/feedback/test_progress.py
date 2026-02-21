"""
Tests unitaires pour progress_v2.py (SuiviProgression, EtatChargement via st.status).

Module: src.ui.feedback.progress_v2
Couverture cible: >80%
"""

from unittest.mock import MagicMock, patch

import pytest


class TestSuiviProgression:
    """Tests pour la classe SuiviProgression (st.status)."""

    @patch("src.ui.feedback.progress_v2.st")
    def test_creation_suivi_progression(self, mock_st):
        """Test de création de SuiviProgression."""
        mock_status = MagicMock()
        mock_status.empty.return_value = MagicMock()
        mock_status.progress.return_value = MagicMock()
        mock_st.status.return_value = mock_status

        from src.ui.feedback.progress_v2 import SuiviProgression

        suivi = SuiviProgression("Import recettes", total=100)

        assert suivi.operation == "Import recettes"
        assert suivi.total == 100
        assert suivi.courant == 0
        assert suivi.afficher_pourcentage is True
        mock_st.status.assert_called_once_with("Import recettes", expanded=True)

    @patch("src.ui.feedback.progress_v2.st")
    def test_suivi_progression_mettre_a_jour(self, mock_st):
        """Test de la méthode mettre_a_jour."""
        mock_status = MagicMock()
        mock_status.empty.return_value = MagicMock()
        mock_progress_bar = MagicMock()
        mock_status.progress.return_value = mock_progress_bar
        mock_st.status.return_value = mock_status

        from src.ui.feedback.progress_v2 import SuiviProgression

        suivi = SuiviProgression("Test", total=10)
        suivi.mettre_a_jour(5, "Étape 5")

        assert suivi.courant == 5
        mock_progress_bar.progress.assert_called()

    @patch("src.ui.feedback.progress_v2.st")
    def test_suivi_progression_mettre_a_jour_ne_depasse_pas_total(self, mock_st):
        """Test que mettre_a_jour ne dépasse pas le total."""
        mock_status = MagicMock()
        mock_status.empty.return_value = MagicMock()
        mock_status.progress.return_value = MagicMock()
        mock_st.status.return_value = mock_status

        from src.ui.feedback.progress_v2 import SuiviProgression

        suivi = SuiviProgression("Test", total=5)
        suivi.mettre_a_jour(10)

        assert suivi.courant == 5

    @patch("src.ui.feedback.progress_v2.st")
    def test_suivi_progression_terminer(self, mock_st):
        """Test de la méthode terminer."""
        mock_status = MagicMock()
        mock_status.empty.return_value = MagicMock()
        mock_status.progress.return_value = MagicMock()
        mock_st.status.return_value = mock_status

        from src.ui.feedback.progress_v2 import EtatProgression, SuiviProgression

        suivi = SuiviProgression("Test", total=10)
        suivi.terminer("Terminé")

        assert suivi.courant == suivi.total
        assert suivi._etat == EtatProgression.TERMINE
        mock_status.update.assert_called()

    @patch("src.ui.feedback.progress_v2.st")
    def test_suivi_progression_erreur(self, mock_st):
        """Test de la méthode erreur."""
        mock_status = MagicMock()
        mock_status.empty.return_value = MagicMock()
        mock_status.progress.return_value = MagicMock()
        mock_st.status.return_value = mock_status

        from src.ui.feedback.progress_v2 import EtatProgression, SuiviProgression

        suivi = SuiviProgression("Test", total=10)
        suivi.erreur("Erreur critique")

        assert suivi._etat == EtatProgression.ERREUR
        mock_status.update.assert_called()

    @patch("src.ui.feedback.progress_v2.st")
    def test_suivi_progression_context_manager_succes(self, mock_st):
        """Test context manager avec succès."""
        mock_status = MagicMock()
        mock_status.empty.return_value = MagicMock()
        mock_status.progress.return_value = MagicMock()
        mock_st.status.return_value = mock_status

        from src.ui.feedback.progress_v2 import EtatProgression, SuiviProgression

        with SuiviProgression("Test", total=5) as suivi:
            suivi.mettre_a_jour(5)

        assert suivi._etat == EtatProgression.TERMINE

    @patch("src.ui.feedback.progress_v2.st")
    def test_suivi_progression_context_manager_erreur(self, mock_st):
        """Test context manager avec exception."""
        mock_status = MagicMock()
        mock_status.empty.return_value = MagicMock()
        mock_status.progress.return_value = MagicMock()
        mock_st.status.return_value = mock_status

        from src.ui.feedback.progress_v2 import EtatProgression, SuiviProgression

        with pytest.raises(ValueError):
            with SuiviProgression("Test", total=5) as suivi:
                raise ValueError("Boom")

        assert suivi._etat == EtatProgression.ERREUR

    @patch("src.ui.feedback.progress_v2.st")
    def test_suivi_progression_affichage_pourcentage(self, mock_st):
        """Test affichage en mode pourcentage."""
        mock_status = MagicMock()
        mock_status_text = MagicMock()
        mock_status.empty.return_value = mock_status_text
        mock_status.progress.return_value = MagicMock()
        mock_st.status.return_value = mock_status

        from src.ui.feedback.progress_v2 import SuiviProgression

        suivi = SuiviProgression("Test", total=100, afficher_pourcentage=True)
        suivi.mettre_a_jour(50)

        call_args = str(mock_status_text.markdown.call_args)
        assert "50%" in call_args

    @patch("src.ui.feedback.progress_v2.st")
    def test_suivi_progression_affichage_fraction(self, mock_st):
        """Test affichage en mode fraction."""
        mock_status = MagicMock()
        mock_status_text = MagicMock()
        mock_status.empty.return_value = mock_status_text
        mock_status.progress.return_value = MagicMock()
        mock_st.status.return_value = mock_status

        from src.ui.feedback.progress_v2 import SuiviProgression

        suivi = SuiviProgression("Test", total=50, afficher_pourcentage=False)
        suivi.mettre_a_jour(25)

        call_args = str(mock_status_text.markdown.call_args)
        assert "25/50" in call_args

    @patch("src.ui.feedback.progress_v2.st")
    def test_suivi_total_zero(self, mock_st):
        """Test avec total=0 (évite division par zéro)."""
        mock_status = MagicMock()
        mock_status.empty.return_value = MagicMock()
        mock_progress_bar = MagicMock()
        mock_status.progress.return_value = mock_progress_bar
        mock_st.status.return_value = mock_status

        from src.ui.feedback.progress_v2 import SuiviProgression

        suivi = SuiviProgression("Test", total=0)
        suivi.mettre_a_jour(0)

        mock_progress_bar.progress.assert_called_with(0)


class TestEtatChargement:
    """Tests pour la classe EtatChargement (st.status)."""

    @patch("src.ui.feedback.progress_v2.st")
    def test_creation_etat_chargement(self, mock_st):
        """Test de création de EtatChargement."""
        mock_status = MagicMock()
        mock_st.status.return_value = mock_status

        from src.ui.feedback.progress_v2 import EtatChargement

        etat = EtatChargement("Chargement données")

        assert etat.titre == "Chargement données"
        mock_st.status.assert_called_once()

    @patch("src.ui.feedback.progress_v2.st")
    def test_etat_chargement_ajouter_etape(self, mock_st):
        """Test de ajouter_etape."""
        mock_status = MagicMock()
        mock_st.status.return_value = mock_status

        from src.ui.feedback.progress_v2 import EtatChargement

        etat = EtatChargement("Test")
        etat.ajouter_etape("Connexion DB")

        assert len(etat.etapes) == 1

    @patch("src.ui.feedback.progress_v2.st")
    def test_etat_chargement_context_manager(self, mock_st):
        """Test context manager."""
        mock_status = MagicMock()
        mock_st.status.return_value = mock_status

        from src.ui.feedback.progress_v2 import EtatChargement

        with EtatChargement("Pipeline") as etat:
            etat.ajouter_etape("Étape 1")

        mock_status.update.assert_called()


class TestProgressImports:
    """Tests d'import du module progress."""

    def test_import_suivi_progression(self):
        """Vérifie que SuiviProgression est importable depuis feedback."""
        from src.ui.feedback import SuiviProgression

        assert SuiviProgression is not None

    def test_import_etat_chargement(self):
        """Vérifie que EtatChargement est importable depuis feedback."""
        from src.ui.feedback import EtatChargement

        assert EtatChargement is not None

    def test_import_etat_progression(self):
        """Vérifie que EtatProgression (enum) est importable."""
        from src.ui.feedback import EtatProgression

        assert EtatProgression is not None

    def test_import_etape_progression(self):
        """Vérifie que EtapeProgression (dataclass) est importable."""
        from src.ui.feedback import EtapeProgression

        assert EtapeProgression is not None

    def test_import_via_progress_v2_direct(self):
        """Vérifie l'import direct depuis progress_v2."""
        from src.ui.feedback.progress_v2 import EtatChargement, SuiviProgression

        assert SuiviProgression is not None
        assert EtatChargement is not None
