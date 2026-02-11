"""
Tests unitaires pour toasts.py (notifications)

Module: src.ui.feedback.toasts
Couverture cible: >80%
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta


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
        from src.ui.feedback.toasts import GestionnaireNotifications

        import streamlit as st

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
        from src.ui.feedback.toasts import afficher_succes, GestionnaireNotifications

        afficher_succes("Opération réussie")

        import streamlit as st
        notifications = st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS]
        
        assert len(notifications) == 1
        assert notifications[0]["type"] == "success"
        assert notifications[0]["message"] == "Opération réussie"

    @patch("streamlit.session_state", {})
    def test_afficher_succes_duree(self):
        """Test de afficher_succes avec durée personnalisée."""
        from src.ui.feedback.toasts import afficher_succes, GestionnaireNotifications

        afficher_succes("Test", duree=10)

        import streamlit as st
        notifications = st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS]
        
        # Vérifie que la durée est respectée (environ 10s)
        diff = (notifications[0]["expires_at"] - notifications[0]["created_at"]).total_seconds()
        assert 9.5 < diff < 10.5

    @patch("streamlit.session_state", {})
    def test_afficher_erreur(self):
        """Test de afficher_erreur."""
        from src.ui.feedback.toasts import afficher_erreur, GestionnaireNotifications

        afficher_erreur("Erreur critique")

        import streamlit as st
        notifications = st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS]
        
        assert notifications[0]["type"] == "error"
        assert notifications[0]["message"] == "Erreur critique"

    @patch("streamlit.session_state", {})
    def test_afficher_erreur_duree_defaut(self):
        """Test que afficher_erreur a une durée par défaut de 5s."""
        from src.ui.feedback.toasts import afficher_erreur, GestionnaireNotifications

        afficher_erreur("Erreur")

        import streamlit as st
        notifications = st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS]
        
        diff = (notifications[0]["expires_at"] - notifications[0]["created_at"]).total_seconds()
        assert 4.5 < diff < 5.5

    @patch("streamlit.session_state", {})
    def test_afficher_avertissement(self):
        """Test de afficher_avertissement."""
        from src.ui.feedback.toasts import afficher_avertissement, GestionnaireNotifications

        afficher_avertissement("Attention!")

        import streamlit as st
        notifications = st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS]
        
        assert notifications[0]["type"] == "warning"
        assert notifications[0]["message"] == "Attention!"

    @patch("streamlit.session_state", {})
    def test_afficher_avertissement_duree_defaut(self):
        """Test que afficher_avertissement a une durée par défaut de 4s."""
        from src.ui.feedback.toasts import afficher_avertissement, GestionnaireNotifications

        afficher_avertissement("Warning")

        import streamlit as st
        notifications = st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS]
        
        diff = (notifications[0]["expires_at"] - notifications[0]["created_at"]).total_seconds()
        assert 3.5 < diff < 4.5

    @patch("streamlit.session_state", {})
    def test_afficher_info(self):
        """Test de afficher_info."""
        from src.ui.feedback.toasts import afficher_info, GestionnaireNotifications

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
            afficher_succes,
            afficher_erreur,
            afficher_avertissement,
            afficher_info,
        )
        assert all([
            GestionnaireNotifications is not None,
            callable(afficher_succes),
            callable(afficher_erreur),
            callable(afficher_avertissement),
            callable(afficher_info),
        ])
