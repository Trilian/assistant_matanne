"""
Tests unitaires pour toasts.py (notifications)

Module: src.ui.feedback.toasts
Couverture cible: >80%

Le GestionnaireNotifications utilise les fonctions Streamlit natives
(st.success, st.error, st.warning, st.info) pour afficher les notifications
immédiatement sans stockage en session_state.
"""

from unittest.mock import patch


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

        GestionnaireNotifications.afficher("Test réussi", "success")

        mock_st.success.assert_called_once_with("Test réussi")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_notification_error(self, mock_st):
        """Test d'affichage d'une notification error."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        GestionnaireNotifications.afficher("Erreur!", "error")

        mock_st.error.assert_called_once_with("Erreur!")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_notification_warning(self, mock_st):
        """Test d'affichage d'une notification warning."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        GestionnaireNotifications.afficher("Attention", "warning")

        mock_st.warning.assert_called_once_with("Attention")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_notification_info(self, mock_st):
        """Test d'affichage d'une notification info."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        GestionnaireNotifications.afficher("Info", "info")

        mock_st.info.assert_called_once_with("Info")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_type_inconnu_fallback_info(self, mock_st):
        """Test type inconnu utilise st.info par défaut."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        GestionnaireNotifications.afficher("Autre", "unknown_type")

        mock_st.info.assert_called_once_with("Autre")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_type_defaut_info(self, mock_st):
        """Test que le type par défaut est info."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        GestionnaireNotifications.afficher("Message")

        mock_st.info.assert_called_once_with("Message")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_multiple_notifications(self, mock_st):
        """Test d'affichage de plusieurs notifications."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        GestionnaireNotifications.afficher("Msg1", "success")
        GestionnaireNotifications.afficher("Msg2", "error")
        GestionnaireNotifications.afficher("Msg3", "warning")

        mock_st.success.assert_called_once_with("Msg1")
        mock_st.error.assert_called_once_with("Msg2")
        mock_st.warning.assert_called_once_with("Msg3")


class TestHelpersFonctions:
    """Tests pour les fonctions raccourcis."""

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_succes(self, mock_st):
        """Test de afficher_succes."""
        from src.ui.feedback.toasts import afficher_succes

        afficher_succes("Opération réussie")

        mock_st.success.assert_called_once_with("Opération réussie")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_succes_duree(self, mock_st):
        """Test de afficher_succes avec durée (paramètre ignoré mais accepté)."""
        from src.ui.feedback.toasts import afficher_succes

        afficher_succes("Test", duree=10)

        mock_st.success.assert_called_once_with("Test")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_erreur(self, mock_st):
        """Test de afficher_erreur."""
        from src.ui.feedback.toasts import afficher_erreur

        afficher_erreur("Erreur critique")

        mock_st.error.assert_called_once_with("Erreur critique")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_erreur_duree_defaut(self, mock_st):
        """Test que afficher_erreur accepte le paramètre durée."""
        from src.ui.feedback.toasts import afficher_erreur

        afficher_erreur("Erreur")

        mock_st.error.assert_called_once_with("Erreur")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_avertissement(self, mock_st):
        """Test de afficher_avertissement."""
        from src.ui.feedback.toasts import afficher_avertissement

        afficher_avertissement("Attention!")

        mock_st.warning.assert_called_once_with("Attention!")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_avertissement_duree_defaut(self, mock_st):
        """Test que afficher_avertissement accepte le paramètre durée."""
        from src.ui.feedback.toasts import afficher_avertissement

        afficher_avertissement("Warning")

        mock_st.warning.assert_called_once_with("Warning")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_info(self, mock_st):
        """Test de afficher_info."""
        from src.ui.feedback.toasts import afficher_info

        afficher_info("Information")

        mock_st.info.assert_called_once_with("Information")


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

        GestionnaireNotifications.afficher("Test success", "success")

        mock_st.success.assert_called_with("Test success")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_error_notification(self, mock_st):
        """Test affichage notification error."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        GestionnaireNotifications.afficher("Test error", "error")

        mock_st.error.assert_called_with("Test error")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_warning_notification(self, mock_st):
        """Test affichage notification warning."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        GestionnaireNotifications.afficher("Test warning", "warning")

        mock_st.warning.assert_called_with("Test warning")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_info_notification(self, mock_st):
        """Test affichage notification info."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        GestionnaireNotifications.afficher("Test info", "info")

        mock_st.info.assert_called_with("Test info")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_unknown_type_falls_back_to_info(self, mock_st):
        """Test type inconnu utilise st.info par défaut."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        GestionnaireNotifications.afficher("Test unknown type", "unknown_type")

        mock_st.info.assert_called_with("Test unknown type")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_empty_message(self, mock_st):
        """Test avec message vide."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        GestionnaireNotifications.afficher("", "info")

        mock_st.info.assert_called_with("")


class TestHelpersAvecDureeCustom:
    """Tests helpers avec durées personnalisées (paramètre duree accepté mais ignoré)."""

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_succes_duree_custom(self, mock_st):
        """Test afficher_succes avec durée custom."""
        from src.ui.feedback.toasts import afficher_succes

        afficher_succes("Message custom", duree=10)

        mock_st.success.assert_called_once_with("Message custom")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_erreur_duree_custom(self, mock_st):
        """Test afficher_erreur avec durée custom."""
        from src.ui.feedback.toasts import afficher_erreur

        afficher_erreur("Erreur custom", duree=15)

        mock_st.error.assert_called_once_with("Erreur custom")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_avertissement_duree_custom(self, mock_st):
        """Test afficher_avertissement avec durée custom."""
        from src.ui.feedback.toasts import afficher_avertissement

        afficher_avertissement("Warning custom", duree=8)

        mock_st.warning.assert_called_once_with("Warning custom")

    @patch("src.ui.feedback.toasts.st")
    def test_afficher_info_duree_custom(self, mock_st):
        """Test afficher_info avec durée custom."""
        from src.ui.feedback.toasts import afficher_info

        afficher_info("Info custom", duree=2)

        mock_st.info.assert_called_once_with("Info custom")
