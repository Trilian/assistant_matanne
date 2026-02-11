"""
Tests unitaires pour atoms.py

Module: src.ui.components.atoms
Couverture cible: >80%
"""

import pytest
from unittest.mock import MagicMock, patch


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


class TestNotification:
    """Tests pour la fonction notification."""

    @patch("streamlit.success")
    def test_notification_success(self, mock_success):
        """Test notification type success."""
        from src.ui.components.atoms import notification

        notification("Opération réussie", type="success")

        mock_success.assert_called_once_with("Opération réussie")

    @patch("streamlit.error")
    def test_notification_error(self, mock_error):
        """Test notification type error."""
        from src.ui.components.atoms import notification

        notification("Erreur!", type="error")

        mock_error.assert_called_once_with("Erreur!")

    @patch("streamlit.warning")
    def test_notification_warning(self, mock_warning):
        """Test notification type warning."""
        from src.ui.components.atoms import notification

        notification("Attention", type="warning")

        mock_warning.assert_called_once_with("Attention")

    @patch("streamlit.info")
    def test_notification_info(self, mock_info):
        """Test notification type info."""
        from src.ui.components.atoms import notification

        notification("Information", type="info")

        mock_info.assert_called_once_with("Information")

    @patch("streamlit.info")
    def test_notification_type_inconnu(self, mock_info):
        """Test notification avec type inconnu utilise info."""
        from src.ui.components.atoms import notification

        notification("Message", type="autre")

        mock_info.assert_called_once_with("Message")


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

    def test_import_notification(self):
        """Vérifie que notification est importable."""
        from src.ui.components.atoms import notification
        assert callable(notification)

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
            etat_vide,
            carte_metrique,
            notification,
            separateur,
            boite_info,
        )
        assert all(callable(f) for f in [
            badge,
            etat_vide,
            carte_metrique,
            notification,
            separateur,
            boite_info,
        ])

    def test_import_via_ui(self):
        """Vérifie l'import via le module ui."""
        from src.ui import (
            badge,
            etat_vide,
            carte_metrique,
            notification,
            separateur,
            boite_info,
        )
        assert all(callable(f) for f in [
            badge,
            etat_vide,
            carte_metrique,
            notification,
            separateur,
            boite_info,
        ])
