"""
Tests unitaires pour toasts.py (notifications)

Module: src.ui.feedback.toasts
Couverture cible: >80%
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch


class TestGestionnaireNotifications:
    """Tests pour la classe GestionnaireNotifications."""

    @patch("streamlit.session_state", {})
    def test_init_gestionnaire(self):
        """Test d'initialisation du gestionnaire."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        GestionnaireNotifications._init()

        import streamlit as st

        assert GestionnaireNotifications.CLE_NOTIFICATIONS in st.session_state

    @patch("streamlit.session_state", {})
    def test_afficher_notification_success(self):
        """Test d'affichage d'une notification success."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        GestionnaireNotifications.afficher("Test réussi", "success", duree=3)

        import streamlit as st

        notifications = st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS]

        assert len(notifications) == 1
        assert notifications[0]["message"] == "Test réussi"
        assert notifications[0]["type"] == "success"

    @patch("streamlit.session_state", {})
    def test_afficher_notification_error(self):
        """Test d'affichage d'une notification error."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        GestionnaireNotifications.afficher("Erreur!", "error")

        import streamlit as st

        notifications = st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS]

        assert notifications[0]["type"] == "error"

    @patch("streamlit.session_state", {})
    def test_afficher_notification_warning(self):
        """Test d'affichage d'une notification warning."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        GestionnaireNotifications.afficher("Attention", "warning")

        import streamlit as st

        notifications = st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS]

        assert notifications[0]["type"] == "warning"

    @patch("streamlit.session_state", {})
    def test_afficher_notification_info(self):
        """Test d'affichage d'une notification info."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        GestionnaireNotifications.afficher("Info", "info")

        import streamlit as st

        notifications = st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS]

        assert notifications[0]["type"] == "info"

    @patch("streamlit.session_state", {})
    def test_notification_expiration(self):
        """Test que les notifications ont une date d'expiration."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        GestionnaireNotifications.afficher("Test", duree=5)

        import streamlit as st

        notifications = st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS]

        assert "expires_at" in notifications[0]
        assert notifications[0]["expires_at"] > datetime.now()

    @patch("streamlit.container")
    @patch("streamlit.success")
    @patch("streamlit.session_state", {})
    def test_rendre_notifications_actives(self, mock_success, mock_container):
        """Test du rendu des notifications actives."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock(return_value=False)

        # Ajouter une notification
        GestionnaireNotifications.afficher("Test", "success")

        # Rendre
        GestionnaireNotifications.rendre()

        mock_success.assert_called_with("Test")

    @patch("streamlit.container")
    @patch("streamlit.error")
    @patch("streamlit.session_state", {})
    def test_rendre_notification_error(self, mock_error, mock_container):
        """Test du rendu d'une notification error."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock(return_value=False)

        GestionnaireNotifications.afficher("Erreur test", "error")
        GestionnaireNotifications.rendre()

        mock_error.assert_called_with("Erreur test")

    @patch("streamlit.container")
    @patch("streamlit.warning")
    @patch("streamlit.session_state", {})
    def test_rendre_notification_warning(self, mock_warning, mock_container):
        """Test du rendu d'une notification warning."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock(return_value=False)

        GestionnaireNotifications.afficher("Attention test", "warning")
        GestionnaireNotifications.rendre()

        mock_warning.assert_called_with("Attention test")

    @patch("streamlit.container")
    @patch("streamlit.info")
    @patch("streamlit.session_state", {})
    def test_rendre_notification_info(self, mock_info, mock_container):
        """Test du rendu d'une notification info."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock(return_value=False)

        GestionnaireNotifications.afficher("Info test", "info")
        GestionnaireNotifications.rendre()

        mock_info.assert_called_with("Info test")

    @patch("streamlit.session_state", {})
    def test_rendre_filtre_expirees(self):
        """Test que rendre filtre les notifications expirées."""
        import streamlit as st

        from src.ui.feedback.toasts import GestionnaireNotifications

        # Ajouter une notification expirée manuellement
        GestionnaireNotifications._init()
        st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS] = [
            {
                "message": "Expirée",
                "type": "info",
                "created_at": datetime.now() - timedelta(seconds=10),
                "expires_at": datetime.now() - timedelta(seconds=5),
            }
        ]

        GestionnaireNotifications.rendre()

        # La notification expirée doit être supprimée
        assert len(st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS]) == 0

    @patch("streamlit.container")
    @patch("streamlit.success")
    @patch("streamlit.session_state", {})
    def test_rendre_max_trois_notifications(self, mock_success, mock_container):
        """Test que rendre affiche max 3 notifications."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock(return_value=False)

        # Ajouter 5 notifications
        for i in range(5):
            GestionnaireNotifications.afficher(f"Message {i}", "success")

        GestionnaireNotifications.rendre()

        # Seulement les 3 dernières doivent être affichées
        assert mock_success.call_count == 3


class TestHelpersFonctions:
    """Tests pour les fonctions raccourcis."""

    @patch("streamlit.session_state", {})
    def test_afficher_succes(self):
        """Test de afficher_succes."""
        from src.ui.feedback.toasts import GestionnaireNotifications, afficher_succes

        afficher_succes("Opération réussie")

        import streamlit as st

        notifications = st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS]

        assert len(notifications) == 1
        assert notifications[0]["type"] == "success"
        assert notifications[0]["message"] == "Opération réussie"

    @patch("streamlit.session_state", {})
    def test_afficher_succes_duree(self):
        """Test de afficher_succes avec durée personnalisée."""
        from src.ui.feedback.toasts import GestionnaireNotifications, afficher_succes

        afficher_succes("Test", duree=10)

        import streamlit as st

        notifications = st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS]

        # Vérifie que la durée est respectée (environ 10s)
        diff = (notifications[0]["expires_at"] - notifications[0]["created_at"]).total_seconds()
        assert 9.5 < diff < 10.5

    @patch("streamlit.session_state", {})
    def test_afficher_erreur(self):
        """Test de afficher_erreur."""
        from src.ui.feedback.toasts import GestionnaireNotifications, afficher_erreur

        afficher_erreur("Erreur critique")

        import streamlit as st

        notifications = st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS]

        assert notifications[0]["type"] == "error"
        assert notifications[0]["message"] == "Erreur critique"

    @patch("streamlit.session_state", {})
    def test_afficher_erreur_duree_defaut(self):
        """Test que afficher_erreur a une durée par défaut de 5s."""
        from src.ui.feedback.toasts import GestionnaireNotifications, afficher_erreur

        afficher_erreur("Erreur")

        import streamlit as st

        notifications = st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS]

        diff = (notifications[0]["expires_at"] - notifications[0]["created_at"]).total_seconds()
        assert 4.5 < diff < 5.5

    @patch("streamlit.session_state", {})
    def test_afficher_avertissement(self):
        """Test de afficher_avertissement."""
        from src.ui.feedback.toasts import GestionnaireNotifications, afficher_avertissement

        afficher_avertissement("Attention!")

        import streamlit as st

        notifications = st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS]

        assert notifications[0]["type"] == "warning"
        assert notifications[0]["message"] == "Attention!"

    @patch("streamlit.session_state", {})
    def test_afficher_avertissement_duree_defaut(self):
        """Test que afficher_avertissement a une durée par défaut de 4s."""
        from src.ui.feedback.toasts import GestionnaireNotifications, afficher_avertissement

        afficher_avertissement("Warning")

        import streamlit as st

        notifications = st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS]

        diff = (notifications[0]["expires_at"] - notifications[0]["created_at"]).total_seconds()
        assert 3.5 < diff < 4.5

    @patch("streamlit.session_state", {})
    def test_afficher_info(self):
        """Test de afficher_info."""
        from src.ui.feedback.toasts import GestionnaireNotifications, afficher_info

        afficher_info("Information")

        import streamlit as st

        notifications = st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS]

        assert notifications[0]["type"] == "info"
        assert notifications[0]["message"] == "Information"


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


class TestGestionnaireNotificationsRendre:
    """Tests complets pour la méthode rendre()."""

    @patch("streamlit.container")
    @patch("streamlit.success")
    @patch("streamlit.session_state", {})
    def test_rendre_success_notification(self, mock_success, mock_container):
        """Test rendu notification success."""
        from datetime import datetime, timedelta

        from src.ui.feedback.toasts import GestionnaireNotifications

        GestionnaireNotifications._init()

        import streamlit as st

        st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS] = [
            {
                "message": "Test success",
                "type": "success",
                "created_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(seconds=60),
            }
        ]

        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock()

        GestionnaireNotifications.rendre()

        mock_success.assert_called_with("Test success")

    @patch("streamlit.container")
    @patch("streamlit.error")
    @patch("streamlit.session_state", {})
    def test_rendre_error_notification(self, mock_error, mock_container):
        """Test rendu notification error."""
        from datetime import datetime, timedelta

        from src.ui.feedback.toasts import GestionnaireNotifications

        GestionnaireNotifications._init()

        import streamlit as st

        st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS] = [
            {
                "message": "Test error",
                "type": "error",
                "created_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(seconds=60),
            }
        ]

        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock()

        GestionnaireNotifications.rendre()

        mock_error.assert_called_with("Test error")

    @patch("streamlit.container")
    @patch("streamlit.warning")
    @patch("streamlit.session_state", {})
    def test_rendre_warning_notification(self, mock_warning, mock_container):
        """Test rendu notification warning."""
        from datetime import datetime, timedelta

        from src.ui.feedback.toasts import GestionnaireNotifications

        GestionnaireNotifications._init()

        import streamlit as st

        st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS] = [
            {
                "message": "Test warning",
                "type": "warning",
                "created_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(seconds=60),
            }
        ]

        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock()

        GestionnaireNotifications.rendre()

        mock_warning.assert_called_with("Test warning")

    @patch("streamlit.container")
    @patch("streamlit.info")
    @patch("streamlit.session_state", {})
    def test_rendre_info_notification(self, mock_info, mock_container):
        """Test rendu notification info."""
        from datetime import datetime, timedelta

        from src.ui.feedback.toasts import GestionnaireNotifications

        GestionnaireNotifications._init()

        import streamlit as st

        st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS] = [
            {
                "message": "Test info",
                "type": "info",
                "created_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(seconds=60),
            }
        ]

        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock()

        GestionnaireNotifications.rendre()

        mock_info.assert_called_with("Test info")

    @patch("streamlit.container")
    @patch("streamlit.info")
    @patch("streamlit.session_state", {})
    def test_rendre_unknown_type_falls_back_to_info(self, mock_info, mock_container):
        """Test type inconnu utilise st.info par défaut."""
        from datetime import datetime, timedelta

        from src.ui.feedback.toasts import GestionnaireNotifications

        GestionnaireNotifications._init()

        import streamlit as st

        st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS] = [
            {
                "message": "Test unknown type",
                "type": "unknown_type",
                "created_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(seconds=60),
            }
        ]

        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock()

        GestionnaireNotifications.rendre()

        mock_info.assert_called_with("Test unknown type")

    @patch("streamlit.session_state", {})
    def test_rendre_expired_notifications_filtered(self):
        """Test que les notifications expirées sont filtrées."""
        from datetime import datetime, timedelta

        from src.ui.feedback.toasts import GestionnaireNotifications

        GestionnaireNotifications._init()

        import streamlit as st

        # Notification expirée
        st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS] = [
            {
                "message": "Expired",
                "type": "info",
                "created_at": datetime.now() - timedelta(seconds=120),
                "expires_at": datetime.now() - timedelta(seconds=60),
            }
        ]

        GestionnaireNotifications.rendre()

        # La notification expirée devrait être supprimée
        assert len(st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS]) == 0

    @patch("streamlit.container")
    @patch("streamlit.success")
    @patch("streamlit.session_state", {})
    def test_rendre_max_3_notifications(self, mock_success, mock_container):
        """Test que max 3 notifications sont affichées."""
        from datetime import datetime, timedelta

        from src.ui.feedback.toasts import GestionnaireNotifications

        GestionnaireNotifications._init()

        import streamlit as st

        # 5 notifications actives
        st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS] = [
            {
                "message": f"Test {i}",
                "type": "success",
                "created_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(seconds=60),
            }
            for i in range(5)
        ]

        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock()

        GestionnaireNotifications.rendre()

        # Seulement les 3 derniers affichés
        assert mock_success.call_count == 3

    @patch("streamlit.session_state", {})
    def test_rendre_empty_notifications(self):
        """Test rendu sans notifications."""
        from src.ui.feedback.toasts import GestionnaireNotifications

        GestionnaireNotifications._init()

        # Ne devrait pas lever d'exception
        GestionnaireNotifications.rendre()

        import streamlit as st

        assert st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS] == []


class TestHelpersAvecDureeCustom:
    """Tests helpers avec durées personnalisées."""

    @patch("streamlit.session_state", {})
    def test_afficher_succes_duree_custom(self):
        """Test afficher_succes avec durée custom."""
        from src.ui.feedback.toasts import GestionnaireNotifications, afficher_succes

        afficher_succes("Message custom", duree=10)

        import streamlit as st

        notifications = st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS]
        diff = (notifications[0]["expires_at"] - notifications[0]["created_at"]).total_seconds()
        assert 9.5 < diff < 10.5

    @patch("streamlit.session_state", {})
    def test_afficher_erreur_duree_custom(self):
        """Test afficher_erreur avec durée custom."""
        from src.ui.feedback.toasts import GestionnaireNotifications, afficher_erreur

        afficher_erreur("Erreur custom", duree=15)

        import streamlit as st

        notifications = st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS]
        diff = (notifications[0]["expires_at"] - notifications[0]["created_at"]).total_seconds()
        assert 14.5 < diff < 15.5

    @patch("streamlit.session_state", {})
    def test_afficher_avertissement_duree_custom(self):
        """Test afficher_avertissement avec durée custom."""
        from src.ui.feedback.toasts import GestionnaireNotifications, afficher_avertissement

        afficher_avertissement("Warning custom", duree=8)

        import streamlit as st

        notifications = st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS]
        diff = (notifications[0]["expires_at"] - notifications[0]["created_at"]).total_seconds()
        assert 7.5 < diff < 8.5

    @patch("streamlit.session_state", {})
    def test_afficher_info_duree_custom(self):
        """Test afficher_info avec durée custom."""
        from src.ui.feedback.toasts import GestionnaireNotifications, afficher_info

        afficher_info("Info custom", duree=2)

        import streamlit as st

        notifications = st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS]
        diff = (notifications[0]["expires_at"] - notifications[0]["created_at"]).total_seconds()
        assert 1.5 < diff < 2.5
