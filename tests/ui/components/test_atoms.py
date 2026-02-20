"""
Tests unitaires pour atoms.py

Module: src.ui.components.atoms
Couverture cible: >80%
"""

from unittest.mock import patch


class TestBadge:
    """Tests pour la fonction badge."""

    @patch("streamlit.markdown")
    def test_badge_defaut(self, mock_markdown):
        """Test badge avec couleur par défaut."""
        from src.ui.components.atoms import badge

        badge("Actif")

        mock_markdown.assert_called_once()
        call_args = mock_markdown.call_args[0][0]
        assert "Actif" in call_args
        assert "#4CAF50" in call_args  # Couleur par défaut

    @patch("streamlit.markdown")
    def test_badge_couleur_personnalisee(self, mock_markdown):
        """Test badge avec couleur personnalisée."""
        from src.ui.components.atoms import badge

        badge("Important", couleur="#FF0000")

        call_args = mock_markdown.call_args[0][0]
        assert "Important" in call_args
        assert "#FF0000" in call_args

    @patch("streamlit.markdown")
    def test_badge_html_valide(self, mock_markdown):
        """Test que badge génère du HTML valide."""
        from src.ui.components.atoms import badge

        badge("Test")

        call_args = mock_markdown.call_args
        assert call_args[1]["unsafe_allow_html"] is True


class TestEtatVide:
    """Tests pour la fonction etat_vide."""

    @patch("streamlit.markdown")
    def test_etat_vide_message_seul(self, mock_markdown):
        """Test etat_vide avec message seul."""
        from src.ui.components.atoms import etat_vide

        etat_vide("Aucune recette")

        mock_markdown.assert_called_once()
        call_args = mock_markdown.call_args[0][0]
        assert "Aucune recette" in call_args
        assert "📭" in call_args  # Icône par défaut

    @patch("streamlit.markdown")
    def test_etat_vide_avec_icone(self, mock_markdown):
        """Test etat_vide avec icône personnalisée."""
        from src.ui.components.atoms import etat_vide

        etat_vide("Aucune recette", icone="🍽️")

        call_args = mock_markdown.call_args[0][0]
        assert "🍽️" in call_args

    @patch("streamlit.markdown")
    def test_etat_vide_avec_sous_texte(self, mock_markdown):
        """Test etat_vide avec sous-texte."""
        from src.ui.components.atoms import etat_vide

        etat_vide("Aucune recette", sous_texte="Ajoutez-en une")

        call_args = mock_markdown.call_args[0][0]
        assert "Aucune recette" in call_args
        assert "Ajoutez-en une" in call_args

    @patch("streamlit.markdown")
    def test_etat_vide_sans_sous_texte(self, mock_markdown):
        """Test etat_vide sans sous-texte (None)."""
        from src.ui.components.atoms import etat_vide

        etat_vide("Message", sous_texte=None)

        call_args = mock_markdown.call_args[0][0]
        assert "Message" in call_args


class TestCarteMetrique:
    """Tests pour la fonction carte_metrique."""

    @patch("streamlit.markdown")
    def test_carte_metrique_base(self, mock_markdown):
        """Test carte_metrique de base."""
        from src.ui.components.atoms import carte_metrique

        carte_metrique("Total", "42")

        mock_markdown.assert_called_once()
        call_args = mock_markdown.call_args[0][0]
        assert "Total" in call_args
        assert "42" in call_args

    @patch("streamlit.markdown")
    def test_carte_metrique_avec_delta(self, mock_markdown):
        """Test carte_metrique avec delta."""
        from src.ui.components.atoms import carte_metrique

        carte_metrique("Total", "42", delta="+5")

        call_args = mock_markdown.call_args[0][0]
        assert "+5" in call_args

    @patch("streamlit.markdown")
    def test_carte_metrique_sans_delta(self, mock_markdown):
        """Test carte_metrique sans delta."""
        from src.ui.components.atoms import carte_metrique

        carte_metrique("Total", "42")

        call_args = mock_markdown.call_args[0][0]
        assert "Total" in call_args

    @patch("streamlit.markdown")
    def test_carte_metrique_couleur_personnalisee(self, mock_markdown):
        """Test carte_metrique avec couleur personnalisée."""
        from src.ui.components.atoms import carte_metrique

        carte_metrique("Total", "42", couleur="#f0f0f0")

        call_args = mock_markdown.call_args[0][0]
        assert "#f0f0f0" in call_args


class TestNotificationsFeedback:
    """Tests pour le système de notifications (anciennement notification() déprécié)."""

    @patch("streamlit.toast")
    def test_afficher_succes_utilise_toast(self, mock_toast):
        """Test que afficher_succes utilise st.toast."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        # Reset le state pour éviter la déduplication
        GestionnaireNotifications._STATE_KEY = "_notif_test_1"
        GestionnaireNotifications.afficher("Opération réussie", "success")

        mock_toast.assert_called_once_with("Opération réussie", icon="✅")

    @patch("streamlit.toast")
    def test_afficher_erreur_utilise_toast(self, mock_toast):
        """Test que afficher_erreur utilise st.toast."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        GestionnaireNotifications._STATE_KEY = "_notif_test_2"
        GestionnaireNotifications.afficher("Erreur!", "error")

        mock_toast.assert_called_once_with("Erreur!", icon="❌")

    @patch("streamlit.toast")
    def test_afficher_warning_utilise_toast(self, mock_toast):
        """Test que afficher_warning utilise st.toast."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        GestionnaireNotifications._STATE_KEY = "_notif_test_3"
        GestionnaireNotifications.afficher("Attention", "warning")

        mock_toast.assert_called_once_with("Attention", icon="⚠️")

    @patch("streamlit.toast")
    def test_afficher_info_utilise_toast(self, mock_toast):
        """Test que afficher_info utilise st.toast."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        GestionnaireNotifications._STATE_KEY = "_notif_test_4"
        GestionnaireNotifications.afficher("Information", "info")

        mock_toast.assert_called_once_with("Information", icon="ℹ️")


class TestSeparateur:
    """Tests pour la fonction separateur."""

    @patch("streamlit.markdown")
    def test_separateur_sans_texte(self, mock_markdown):
        """Test separateur sans texte."""
        from src.ui.components.atoms import separateur

        separateur()

        mock_markdown.assert_called_once_with("---")

    @patch("streamlit.markdown")
    def test_separateur_avec_texte(self, mock_markdown):
        """Test separateur avec texte."""
        from src.ui.components.atoms import separateur

        separateur("OU")

        call_args = mock_markdown.call_args[0][0]
        assert "OU" in call_args
        assert call_args != "---"


class TestBoiteInfo:
    """Tests pour la fonction boite_info."""

    @patch("streamlit.markdown")
    def test_boite_info_base(self, mock_markdown):
        """Test boite_info de base."""
        from src.ui.components.atoms import boite_info

        boite_info("Astuce", "Conseil utile")

        mock_markdown.assert_called_once()
        call_args = mock_markdown.call_args[0][0]
        assert "Astuce" in call_args
        assert "Conseil utile" in call_args
        assert "ℹ️" in call_args  # Icône par défaut

    @patch("streamlit.markdown")
    def test_boite_info_icone_personnalisee(self, mock_markdown):
        """Test boite_info avec icône personnalisée."""
        from src.ui.components.atoms import boite_info

        boite_info("Astuce", "Conseil", icone="💡")

        call_args = mock_markdown.call_args[0][0]
        assert "💡" in call_args

    @patch("streamlit.markdown")
    def test_boite_info_html_valide(self, mock_markdown):
        """Test que boite_info génère du HTML valide."""
        from src.ui.components.atoms import boite_info

        boite_info("Titre", "Contenu")

        call_args = mock_markdown.call_args
        assert call_args[1]["unsafe_allow_html"] is True


class TestAtomsImports:
    """Tests d'import des atomes."""

    def test_import_badge(self):
        """Vérifie que badge est importable."""
        from src.ui.components.atoms import badge

        assert callable(badge)

    def test_import_etat_vide(self):
        """Vérifie que etat_vide est importable."""
        from src.ui.components.atoms import etat_vide

        assert callable(etat_vide)

    def test_import_carte_metrique(self):
        """Vérifie que carte_metrique est importable."""
        from src.ui.components.atoms import carte_metrique

        assert callable(carte_metrique)

    def test_import_notifications_feedback(self):
        """Vérifie que le système de notifications est importable via feedback."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        assert hasattr(GestionnaireNotifications, "afficher")

    def test_import_separateur(self):
        """Vérifie que separateur est importable."""
        from src.ui.components.atoms import separateur

        assert callable(separateur)

    def test_import_boite_info(self):
        """Vérifie que boite_info est importable."""
        from src.ui.components.atoms import boite_info

        assert callable(boite_info)

    def test_import_via_components(self):
        """Vérifie l'import via le module components."""
        from src.ui.components import (
            badge,
            boite_info,
            carte_metrique,
            etat_vide,
            separateur,
        )

        assert all(
            callable(f)
            for f in [
                badge,
                etat_vide,
                carte_metrique,
                separateur,
                boite_info,
            ]
        )

    def test_import_via_ui(self):
        """Vérifie l'import via le module ui."""
        from src.ui import (
            badge,
            boite_info,
            carte_metrique,
            etat_vide,
            separateur,
        )

        assert all(
            callable(f)
            for f in [
                badge,
                etat_vide,
                carte_metrique,
                separateur,
                boite_info,
            ]
        )
