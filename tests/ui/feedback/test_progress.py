"""
Tests unitaires pour progress.py

Module: src.ui.feedback.progress
Couverture cible: >80%
"""

from unittest.mock import MagicMock, patch


class TestSuiviProgression:
    """Tests pour la classe SuiviProgression."""

    @patch("streamlit.empty")
    @patch("streamlit.progress")
    def test_creation_suivi_progression(self, mock_progress, mock_empty):
        """Test de création de SuiviProgression."""
        from src.ui.feedback.progress import SuiviProgression

        mock_empty.return_value = MagicMock()
        mock_progress.return_value = MagicMock()

        suivi = SuiviProgression("Import recettes", total=100)

        assert suivi.operation == "Import recettes"
        assert suivi.total == 100
        assert suivi.courant == 0
        assert suivi.afficher_pourcentage is True

    @patch("streamlit.empty")
    @patch("streamlit.progress")
    def test_suivi_progression_mettre_a_jour(self, mock_progress, mock_empty):
        """Test de la méthode mettre_a_jour."""
        from src.ui.feedback.progress import SuiviProgression

        mock_placeholder = MagicMock()
        mock_empty.return_value = mock_placeholder
        mock_progress.return_value = MagicMock()

        suivi = SuiviProgression("Test", total=10)
        suivi.mettre_a_jour(5, "Étape 5")

        assert suivi.courant == 5

    @patch("streamlit.empty")
    @patch("streamlit.progress")
    def test_suivi_progression_incrementer(self, mock_progress, mock_empty):
        """Test de la méthode incrementer."""
        from src.ui.feedback.progress import SuiviProgression

        mock_empty.return_value = MagicMock()
        mock_progress.return_value = MagicMock()

        suivi = SuiviProgression("Test", total=10)
        suivi.incrementer()
        assert suivi.courant == 1

        suivi.incrementer(pas=3)
        assert suivi.courant == 4

    @patch("streamlit.empty")
    @patch("streamlit.progress")
    def test_suivi_progression_incrementer_limite(self, mock_progress, mock_empty):
        """Test que incrementer ne dépasse pas le total."""
        from src.ui.feedback.progress import SuiviProgression

        mock_empty.return_value = MagicMock()
        mock_progress.return_value = MagicMock()

        suivi = SuiviProgression("Test", total=5)
        suivi.incrementer(pas=10)

        assert suivi.courant == 5  # Ne dépasse pas le total

    @patch("streamlit.empty")
    @patch("streamlit.progress")
    def test_suivi_progression_terminer(self, mock_progress, mock_empty):
        """Test de la méthode terminer."""
        from src.ui.feedback.progress import SuiviProgression

        mock_placeholder = MagicMock()
        mock_empty.return_value = mock_placeholder
        mock_bar = MagicMock()
        mock_progress.return_value = mock_bar

        suivi = SuiviProgression("Test", total=10)
        suivi.terminer("Terminé avec succès")

        assert suivi.courant == suivi.total

    @patch("streamlit.empty")
    @patch("streamlit.progress")
    def test_suivi_progression_terminer_sans_message(self, mock_progress, mock_empty):
        """Test de terminer sans message personnalisé."""
        from src.ui.feedback.progress import SuiviProgression

        mock_placeholder = MagicMock()
        mock_empty.return_value = mock_placeholder
        mock_progress.return_value = MagicMock()

        suivi = SuiviProgression("Test", total=10)
        suivi.terminer()

        assert suivi.courant == suivi.total

    @patch("streamlit.empty")
    @patch("streamlit.progress")
    def test_suivi_progression_erreur(self, mock_progress, mock_empty):
        """Test de la méthode erreur."""
        from src.ui.feedback.progress import SuiviProgression

        mock_placeholder = MagicMock()
        mock_empty.return_value = mock_placeholder
        mock_progress.return_value = MagicMock()

        suivi = SuiviProgression("Test", total=10)
        suivi.erreur("Erreur critique")

        mock_placeholder.error.assert_called()

    @patch("streamlit.empty")
    @patch("streamlit.progress")
    def test_suivi_progression_affichage_pourcentage(self, mock_progress, mock_empty):
        """Test de l'affichage en mode pourcentage."""
        from src.ui.feedback.progress import SuiviProgression

        mock_placeholder = MagicMock()
        mock_empty.return_value = mock_placeholder
        mock_progress.return_value = MagicMock()

        suivi = SuiviProgression("Test", total=100, afficher_pourcentage=True)
        suivi.mettre_a_jour(50)

        # Vérifie que markdown a été appelé avec le pourcentage
        mock_placeholder.markdown.assert_called()

    @patch("streamlit.empty")
    @patch("streamlit.progress")
    def test_suivi_progression_affichage_fraction(self, mock_progress, mock_empty):
        """Test de l'affichage en mode fraction."""
        from src.ui.feedback.progress import SuiviProgression

        mock_placeholder = MagicMock()
        mock_empty.return_value = mock_placeholder
        mock_progress.return_value = MagicMock()

        suivi = SuiviProgression("Test", total=100, afficher_pourcentage=False)
        suivi.mettre_a_jour(50)

        mock_placeholder.markdown.assert_called()

    @patch("streamlit.empty")
    @patch("streamlit.progress")
    def test_suivi_progression_estimation_temps(self, mock_progress, mock_empty):
        """Test de l'estimation du temps restant."""
        from src.ui.feedback.progress import SuiviProgression

        mock_placeholder = MagicMock()
        mock_empty.return_value = mock_placeholder
        mock_progress.return_value = MagicMock()

        suivi = SuiviProgression("Test", total=10)
        # Simule une progression à mi-chemin
        suivi.mettre_a_jour(5, "Traitement...")

        # Le caption devrait être appelé avec l'estimation
        mock_placeholder.caption.assert_called()


class TestEtatChargement:
    """Tests pour la classe EtatChargement."""

    @patch("streamlit.empty")
    def test_creation_etat_chargement(self, mock_empty):
        """Test de création de EtatChargement."""
        from src.ui.feedback.progress import EtatChargement

        mock_empty.return_value = MagicMock()

        etat = EtatChargement("Chargement données")

        assert etat.titre == "Chargement données"
        assert etat.etapes == []
        assert etat.etape_courante is None

    @patch("streamlit.empty")
    def test_etat_chargement_ajouter_etape(self, mock_empty):
        """Test de ajouter_etape."""
        from src.ui.feedback.progress import EtatChargement

        mock_empty.return_value = MagicMock()

        etat = EtatChargement("Test")
        etat.ajouter_etape("Connexion DB")

        assert len(etat.etapes) == 1
        assert etat.etapes[0]["name"] == "Connexion DB"
        assert etat.etapes[0]["completed"] is False

    @patch("streamlit.empty")
    def test_etat_chargement_terminer_etape(self, mock_empty):
        """Test de terminer_etape."""
        from src.ui.feedback.progress import EtatChargement

        mock_empty.return_value = MagicMock()

        etat = EtatChargement("Test")
        etat.ajouter_etape("Étape 1")
        etat.terminer_etape("Étape 1")

        assert etat.etapes[0]["completed"] is True
        assert "OK" in etat.etapes[0]["status"]

    @patch("streamlit.empty")
    def test_etat_chargement_terminer_etape_courante(self, mock_empty):
        """Test de terminer_etape sans nom (étape courante)."""
        from src.ui.feedback.progress import EtatChargement

        mock_empty.return_value = MagicMock()

        etat = EtatChargement("Test")
        etat.ajouter_etape("Étape 1")
        etat.terminer_etape()

        assert etat.etapes[0]["completed"] is True

    @patch("streamlit.empty")
    def test_etat_chargement_terminer_etape_echec(self, mock_empty):
        """Test de terminer_etape avec échec."""
        from src.ui.feedback.progress import EtatChargement

        mock_empty.return_value = MagicMock()

        etat = EtatChargement("Test")
        etat.ajouter_etape("Étape 1")
        etat.terminer_etape("Étape 1", succes=False)

        assert etat.etapes[0]["completed"] is True
        assert "Erreur" in etat.etapes[0]["status"]

    @patch("streamlit.empty")
    def test_etat_chargement_erreur_etape(self, mock_empty):
        """Test de erreur_etape."""
        from src.ui.feedback.progress import EtatChargement

        mock_empty.return_value = MagicMock()

        etat = EtatChargement("Test")
        etat.ajouter_etape("Étape 1")
        etat.erreur_etape("Étape 1", "Timeout")

        assert etat.etapes[0]["completed"] is True
        assert "Timeout" in etat.etapes[0]["status"]

    @patch("streamlit.empty")
    def test_etat_chargement_erreur_etape_sans_message(self, mock_empty):
        """Test de erreur_etape sans message."""
        from src.ui.feedback.progress import EtatChargement

        mock_empty.return_value = MagicMock()

        etat = EtatChargement("Test")
        etat.ajouter_etape("Étape 1")
        etat.erreur_etape()

        assert etat.etapes[0]["completed"] is True
        assert "Erreur" in etat.etapes[0]["status"]

    @patch("streamlit.empty")
    def test_etat_chargement_finaliser(self, mock_empty):
        """Test de finaliser."""
        from src.ui.feedback.progress import EtatChargement

        mock_placeholder = MagicMock()
        mock_empty.return_value = mock_placeholder

        etat = EtatChargement("Test")
        etat.ajouter_etape("Étape 1")
        etat.terminer_etape("Étape 1")
        etat.finaliser("Tout est prêt")

        mock_placeholder.success.assert_called()

    @patch("streamlit.empty")
    def test_etat_chargement_finaliser_sans_message(self, mock_empty):
        """Test de finaliser sans message."""
        from src.ui.feedback.progress import EtatChargement

        mock_placeholder = MagicMock()
        mock_empty.return_value = mock_placeholder

        etat = EtatChargement("Chargement")
        etat.finaliser()

        mock_placeholder.success.assert_called()

    @patch("streamlit.empty")
    def test_etat_chargement_plusieurs_etapes(self, mock_empty):
        """Test avec plusieurs étapes."""
        from src.ui.feedback.progress import EtatChargement

        mock_empty.return_value = MagicMock()

        etat = EtatChargement("Pipeline")
        etat.ajouter_etape("Connexion")
        etat.ajouter_etape("Import")
        etat.ajouter_etape("Validation")

        assert len(etat.etapes) == 3
        assert etat.etape_courante == 2


class TestProgressImports:
    """Tests d'import du module progress."""

    def test_import_suivi_progression(self):
        """Vérifie que SuiviProgression est importable."""
        from src.ui.feedback.progress import SuiviProgression

        assert SuiviProgression is not None

    def test_import_etat_chargement(self):
        """Vérifie que EtatChargement est importable."""
        from src.ui.feedback.progress import EtatChargement

        assert EtatChargement is not None

    def test_import_via_feedback(self):
        """Vérifie l'import via le module feedback."""
        from src.ui.feedback import EtatChargement, SuiviProgression

        assert SuiviProgression is not None
        assert EtatChargement is not None


# ═══════════════════════════════════════════════════════════
# TESTS ADDITIONNELS POUR COUVERTURE
# ═══════════════════════════════════════════════════════════


class TestSuiviProgressionCoverage:
    """Tests additionnels pour SuiviProgression."""

    @patch("streamlit.empty")
    @patch("streamlit.progress")
    def test_suivi_total_zero(self, mock_progress, mock_empty):
        """Test avec total=0 (évite division par zéro)."""
        from src.ui.feedback.progress import SuiviProgression

        mock_empty.return_value = MagicMock()
        mock_bar = MagicMock()
        mock_progress.return_value = mock_bar

        suivi = SuiviProgression("Test", total=0)

        # Ne devrait pas lever d'exception
        suivi.mettre_a_jour(0)
        mock_bar.progress.assert_called_with(0)

    @patch("streamlit.empty")
    @patch("streamlit.progress")
    def test_suivi_mettre_a_jour_avec_statut_seul(self, mock_progress, mock_empty):
        """Test mettre_a_jour à 100% affiche juste le statut."""
        from src.ui.feedback.progress import SuiviProgression

        mock_placeholder = MagicMock()
        mock_empty.return_value = mock_placeholder
        mock_progress.return_value = MagicMock()

        suivi = SuiviProgression("Test", total=10)
        suivi.mettre_a_jour(10, "Terminé")  # 100%

        # Le caption ne devrait pas afficher l'estimation à 100%
        # mais devrait quand même afficher le statut
        mock_placeholder.caption.assert_called()

    @patch("streamlit.empty")
    @patch("streamlit.progress")
    def test_suivi_affichage_fraction_format(self, mock_progress, mock_empty):
        """Test format fraction (X/Y)."""
        from src.ui.feedback.progress import SuiviProgression

        mock_placeholder = MagicMock()
        mock_empty.return_value = mock_placeholder
        mock_progress.return_value = MagicMock()

        suivi = SuiviProgression("Test", total=50, afficher_pourcentage=False)
        suivi.mettre_a_jour(25)

        call_args = str(mock_placeholder.markdown.call_args)
        assert "25/50" in call_args


class TestEtatChargementCoverage:
    """Tests additionnels pour EtatChargement."""

    @patch("streamlit.empty")
    def test_etat_affichage_html_structure(self, mock_empty):
        """Test structure HTML de l'affichage."""
        from src.ui.feedback.progress import EtatChargement

        mock_placeholder = MagicMock()
        mock_empty.return_value = mock_placeholder

        etat = EtatChargement("Test")
        etat.ajouter_etape("Étape 1")

        # Vérifie que markdown a été appelé avec du HTML
        calls = mock_placeholder.markdown.call_args_list
        html_call = [c for c in calls if len(c[0]) > 0 and "unsafe_allow_html" in str(c)]
        assert len(html_call) > 0

    @patch("streamlit.empty")
    def test_terminer_etape_inexistante(self, mock_empty):
        """Test terminer une étape qui n'existe pas."""
        from src.ui.feedback.progress import EtatChargement

        mock_empty.return_value = MagicMock()

        etat = EtatChargement("Test")
        etat.ajouter_etape("Étape 1")

        # Ne devrait pas lever d'exception
        etat.terminer_etape("Étape inexistante")

        # L'étape 1 ne devrait pas être terminée
        assert etat.etapes[0]["completed"] is False

    @patch("streamlit.empty")
    def test_erreur_etape_inexistante(self, mock_empty):
        """Test erreur sur étape qui n'existe pas."""
        from src.ui.feedback.progress import EtatChargement

        mock_empty.return_value = MagicMock()

        etat = EtatChargement("Test")
        etat.ajouter_etape("Étape 1")

        # Ne devrait pas lever d'exception
        etat.erreur_etape("Étape inexistante", "Error")

        # L'étape 1 ne devrait pas être en erreur
        assert "Erreur" not in etat.etapes[0]["status"]

    @patch("streamlit.empty")
    def test_etat_courante_none(self, mock_empty):
        """Test avec etape_courante = None."""
        from src.ui.feedback.progress import EtatChargement

        mock_empty.return_value = MagicMock()

        etat = EtatChargement("Test")
        # Pas d'étape ajoutée, etape_courante est None

        # Ne devrait pas lever d'exception
        etat.terminer_etape()
        etat.erreur_etape()
