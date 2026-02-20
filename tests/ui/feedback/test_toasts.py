"""
Tests unitaires pour toasts.py (notifications)

Module: src.ui.feedback.toasts
Couverture cible: >80%

Le GestionnaireNotifications utilise st.toast() (Streamlit ≥ 1.32)
avec déduplication automatique (fenêtre de 3 secondes) et historique.
Fallback sur st.success/st.error/st.warning/st.info si st.toast absent.
"""

from unittest.mock import MagicMock, patch


class TestGestionnaireNotifications:
    """Tests pour la classe GestionnaireNotifications."""

    def test_import_gestionnaire(self):
        """Test d'import du gestionnaire."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        assert GestionnaireNotifications is not None

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_notification_success(self, mock_st):
        """Test d'affichage d'une notification success."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        mock_st.session_state = {}
        mock_st.toast = MagicMock()
        GestionnaireNotifications._STATE_KEY = "_test_notif_1"
        GestionnaireNotifications.afficher("Test réussi", "success")

        mock_st.toast.assert_called_once_with("Test réussi", icon="✅")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_notification_error(self, mock_st):
        """Test d'affichage d'une notification error."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        mock_st.session_state = {}
        mock_st.toast = MagicMock()
        GestionnaireNotifications._STATE_KEY = "_test_notif_2"
        GestionnaireNotifications.afficher("Erreur!", "error")

        mock_st.toast.assert_called_once_with("Erreur!", icon="❌")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_notification_warning(self, mock_st):
        """Test d'affichage d'une notification warning."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        mock_st.session_state = {}
        mock_st.toast = MagicMock()
        GestionnaireNotifications._STATE_KEY = "_test_notif_3"
        GestionnaireNotifications.afficher("Attention", "warning")

        mock_st.toast.assert_called_once_with("Attention", icon="⚠️")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_notification_info(self, mock_st):
        """Test d'affichage d'une notification info."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        mock_st.session_state = {}
        mock_st.toast = MagicMock()
        GestionnaireNotifications._STATE_KEY = "_test_notif_4"
        GestionnaireNotifications.afficher("Info", "info")

        mock_st.toast.assert_called_once_with("Info", icon="ℹ️")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_type_inconnu_fallback_info(self, mock_st):
        """Test type inconnu utilise l'icône info par défaut."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        mock_st.session_state = {}
        mock_st.toast = MagicMock()
        GestionnaireNotifications._STATE_KEY = "_test_notif_5"
        GestionnaireNotifications.afficher("Autre", "unknown_type")

        mock_st.toast.assert_called_once_with("Autre", icon="ℹ️")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_type_defaut_info(self, mock_st):
        """Test que le type par défaut est info."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        mock_st.session_state = {}
        mock_st.toast = MagicMock()
        GestionnaireNotifications._STATE_KEY = "_test_notif_6"
        GestionnaireNotifications.afficher("Message")

        mock_st.toast.assert_called_once_with("Message", icon="ℹ️")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_multiple_notifications(self, mock_st):
        """Test d'affichage de plusieurs notifications différentes."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        mock_st.session_state = {}
        mock_st.toast = MagicMock()
        GestionnaireNotifications._STATE_KEY = "_test_notif_7"

        GestionnaireNotifications.afficher("Msg1", "success")
        GestionnaireNotifications.afficher("Msg2", "error")
        GestionnaireNotifications.afficher("Msg3", "warning")

        assert mock_st.toast.call_count == 3


class TestHelpersFonctions:
    """Tests pour les fonctions raccourcis."""

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_succes(self, mock_st):
        """Test de afficher_succes."""
        from src.ui.feedback.toasts import GestionnaireNotifications, afficher_succes

        mock_st.session_state = {}
        mock_st.toast = MagicMock()
        GestionnaireNotifications._STATE_KEY = "_test_helper_1"
        afficher_succes("Opération réussie")

        mock_st.toast.assert_called_once_with("Opération réussie", icon="✅")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_succes_duree(self, mock_st):
        """Test de afficher_succes avec durée (paramètre accepté)."""
        from src.ui.feedback.toasts import GestionnaireNotifications, afficher_succes

        mock_st.session_state = {}
        mock_st.toast = MagicMock()
        GestionnaireNotifications._STATE_KEY = "_test_helper_2"
        afficher_succes("Test", duree=10)

        mock_st.toast.assert_called_once_with("Test", icon="✅")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_erreur(self, mock_st):
        """Test de afficher_erreur."""
        from src.ui.feedback.toasts import GestionnaireNotifications, afficher_erreur

        mock_st.session_state = {}
        mock_st.toast = MagicMock()
        GestionnaireNotifications._STATE_KEY = "_test_helper_3"
        afficher_erreur("Erreur critique")

        mock_st.toast.assert_called_once_with("Erreur critique", icon="❌")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_erreur_duree_defaut(self, mock_st):
        """Test que afficher_erreur fonctionne avec durée par défaut."""
        from src.ui.feedback.toasts import GestionnaireNotifications, afficher_erreur

        mock_st.session_state = {}
        mock_st.toast = MagicMock()
        GestionnaireNotifications._STATE_KEY = "_test_helper_4"
        afficher_erreur("Erreur")

        mock_st.toast.assert_called_once_with("Erreur", icon="❌")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_avertissement(self, mock_st):
        """Test de afficher_avertissement."""
        from src.ui.feedback.toasts import GestionnaireNotifications, afficher_avertissement

        mock_st.session_state = {}
        mock_st.toast = MagicMock()
        GestionnaireNotifications._STATE_KEY = "_test_helper_5"
        afficher_avertissement("Attention!")

        mock_st.toast.assert_called_once_with("Attention!", icon="⚠️")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_avertissement_duree_defaut(self, mock_st):
        """Test que afficher_avertissement fonctionne avec durée par défaut."""
        from src.ui.feedback.toasts import GestionnaireNotifications, afficher_avertissement

        mock_st.session_state = {}
        mock_st.toast = MagicMock()
        GestionnaireNotifications._STATE_KEY = "_test_helper_6"
        afficher_avertissement("Warning")

        mock_st.toast.assert_called_once_with("Warning", icon="⚠️")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_info(self, mock_st):
        """Test de afficher_info."""
        from src.ui.feedback.toasts import GestionnaireNotifications, afficher_info

        mock_st.session_state = {}
        mock_st.toast = MagicMock()
        GestionnaireNotifications._STATE_KEY = "_test_helper_7"
        afficher_info("Information")

        mock_st.toast.assert_called_once_with("Information", icon="ℹ️")


class TestNotificationsImports:
    """Tests d'import du module notifications."""

    def test_import_gestionnaire_notifications(self):
        """Vérifie que GestionnaireNotifications est importable."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        assert GestionnaireNotifications is not None

    def test_import_afficher_succes(self):
        """Vérifie que afficher_succes est importable."""
        from src.ui.feedback.toasts import afficher_succes

        assert callable(afficher_succes)

    def test_import_afficher_erreur(self):
        """Vérifie que afficher_erreur est importable."""
        from src.ui.feedback.toasts import afficher_erreur

        assert callable(afficher_erreur)

    def test_import_afficher_avertissement(self):
        """Vérifie que afficher_avertissement est importable."""
        from src.ui.feedback.toasts import afficher_avertissement

        assert callable(afficher_avertissement)

    def test_import_afficher_info(self):
        """Vérifie que afficher_info est importable."""
        from src.ui.feedback.toasts import afficher_info

        assert callable(afficher_info)

    def test_import_via_feedback(self):
        """Vérifie l'import via le module feedback."""
        from src.ui.feedback import (
            GestionnaireNotifications,
            afficher_avertissement,
            afficher_erreur,
            afficher_info,
            afficher_succes,
        )

        assert all(
            [
                GestionnaireNotifications is not None,
                callable(afficher_succes),
                callable(afficher_erreur),
                callable(afficher_avertissement),
                callable(afficher_info),
            ]
        )


# ═══════════════════════════════════════════════════════════
# TESTS ADDITIONNELS POUR COUVERTURE
# ═══════════════════════════════════════════════════════════


class TestGestionnaireNotificationsAffichage:
    """Tests complets pour la méthode afficher()."""

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_success_notification(self, mock_st):
        """Test affichage notification success."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        mock_st.session_state = {}
        mock_st.toast = MagicMock()
        GestionnaireNotifications._STATE_KEY = "_test_extra_1"
        GestionnaireNotifications.afficher("Test success", "success")

        mock_st.toast.assert_called_with("Test success", icon="✅")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_error_notification(self, mock_st):
        """Test affichage notification error."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        mock_st.session_state = {}
        mock_st.toast = MagicMock()
        GestionnaireNotifications._STATE_KEY = "_test_extra_2"
        GestionnaireNotifications.afficher("Test error", "error")

        mock_st.toast.assert_called_with("Test error", icon="❌")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_warning_notification(self, mock_st):
        """Test affichage notification warning."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        mock_st.session_state = {}
        mock_st.toast = MagicMock()
        GestionnaireNotifications._STATE_KEY = "_test_extra_3"
        GestionnaireNotifications.afficher("Test warning", "warning")

        mock_st.toast.assert_called_with("Test warning", icon="⚠️")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_info_notification(self, mock_st):
        """Test affichage notification info."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        mock_st.session_state = {}
        mock_st.toast = MagicMock()
        GestionnaireNotifications._STATE_KEY = "_test_extra_4"
        GestionnaireNotifications.afficher("Test info", "info")

        mock_st.toast.assert_called_with("Test info", icon="ℹ️")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_unknown_type_falls_back_to_info(self, mock_st):
        """Test type inconnu utilise l'icône info par défaut."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        mock_st.session_state = {}
        mock_st.toast = MagicMock()
        GestionnaireNotifications._STATE_KEY = "_test_extra_5"
        GestionnaireNotifications.afficher("Test unknown type", "unknown_type")

        mock_st.toast.assert_called_with("Test unknown type", icon="ℹ️")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_empty_message(self, mock_st):
        """Test avec message vide."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        mock_st.session_state = {}
        mock_st.toast = MagicMock()
        GestionnaireNotifications._STATE_KEY = "_test_extra_6"
        GestionnaireNotifications.afficher("", "info")

        mock_st.toast.assert_called_with("", icon="ℹ️")


class TestHelpersAvecDureeCustom:
    """Tests helpers avec durées personnalisées (paramètre duree accepté)."""

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_succes_duree_custom(self, mock_st):
        """Test afficher_succes avec durée custom."""
        from src.ui.feedback.toasts import GestionnaireNotifications, afficher_succes

        mock_st.session_state = {}
        mock_st.toast = MagicMock()
        GestionnaireNotifications._STATE_KEY = "_test_duree_1"
        afficher_succes("Message custom", duree=10)

        mock_st.toast.assert_called_once_with("Message custom", icon="✅")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_erreur_duree_custom(self, mock_st):
        """Test afficher_erreur avec durée custom."""
        from src.ui.feedback.toasts import GestionnaireNotifications, afficher_erreur

        mock_st.session_state = {}
        mock_st.toast = MagicMock()
        GestionnaireNotifications._STATE_KEY = "_test_duree_2"
        afficher_erreur("Erreur custom", duree=15)

        mock_st.toast.assert_called_once_with("Erreur custom", icon="❌")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_avertissement_duree_custom(self, mock_st):
        """Test afficher_avertissement avec durée custom."""
        from src.ui.feedback.toasts import GestionnaireNotifications, afficher_avertissement

        mock_st.session_state = {}
        mock_st.toast = MagicMock()
        GestionnaireNotifications._STATE_KEY = "_test_duree_3"
        afficher_avertissement("Warning custom", duree=8)

        mock_st.toast.assert_called_once_with("Warning custom", icon="⚠️")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_info_duree_custom(self, mock_st):
        """Test afficher_info avec durée custom."""
        from src.ui.feedback.toasts import GestionnaireNotifications, afficher_info

        mock_st.session_state = {}
        mock_st.toast = MagicMock()
        GestionnaireNotifications._STATE_KEY = "_test_duree_4"
        afficher_info("Info custom", duree=2)

        mock_st.toast.assert_called_once_with("Info custom", icon="ℹ️")
