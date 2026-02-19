"""
Tests pour src/modules/outils/notifications_push.py

Tests du module de gestion des notifications push via ntfy.sh.
"""

from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pytest

# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def mock_st():
    """Mock Streamlit complet."""
    with patch("src.modules.utilitaires.notifications_push.st") as mock:
        mock.session_state = {}
        # Retourne le bon nombre de colonnes selon l'argument
        mock.columns.side_effect = lambda x: [
            MagicMock() for _ in range(x if isinstance(x, int) else len(x))
        ]
        mock.tabs.return_value = [MagicMock() for _ in range(5)]
        mock.form.return_value.__enter__ = MagicMock()
        mock.form.return_value.__exit__ = MagicMock(return_value=False)
        mock.container.return_value.__enter__ = MagicMock()
        mock.container.return_value.__exit__ = MagicMock(return_value=False)
        yield mock


@pytest.fixture
def mock_config():
    """Configuration de notification mockée."""
    config = MagicMock()
    config.topic = "test-topic"
    config.actif = True
    config.rappels_taches = True
    config.rappels_courses = False
    config.heure_digest = 8
    return config


@pytest.fixture
def mock_service():
    """Service de notification mocké."""
    service = MagicMock()
    service.get_subscribe_qr_url.return_value = "https://qr.example.com/test"
    service.get_web_url.return_value = "https://ntfy.sh/test-topic"
    service.test_connexion_sync.return_value = MagicMock(
        succes=True, message="Test réussi", notification_id="123"
    )
    service.envoyer_sync.return_value = MagicMock(succes=True, message="Envoyé")
    service.envoyer_digest_quotidien.return_value = MagicMock(succes=True, message="Digest envoyé")
    service.obtenir_taches_en_retard.return_value = []
    service.obtenir_taches_du_jour.return_value = []
    return service


@pytest.fixture
def mock_tache_retard():
    """Tâche en retard mockée."""
    tache = MagicMock()
    tache.id = 1
    tache.titre = "Tâche test"
    tache.nom = "Tâche test"
    tache.date_echeance = date.today() - timedelta(days=5)
    tache.prochaine_fois = date.today() - timedelta(days=5)
    return tache


# ═══════════════════════════════════════════════════════════
# TESTS - IMPORTS
# ═══════════════════════════════════════════════════════════


class TestImports:
    """Tests des imports du module."""

    def test_import_module(self):
        """Test que le module s'importe correctement."""
        from src.modules.utilitaires import notifications_push

        assert notifications_push is not None

    def test_import_app(self):
        """Test que la fonction app() est importable."""
        from src.modules.utilitaires.notifications_push import app

        assert callable(app)

    def test_import_constants(self):
        """Test que les constantes sont importables."""
        from src.modules.utilitaires.notifications_push import HELP_NTFY

        assert "ntfy.sh" in HELP_NTFY

    def test_import_helpers(self):
        """Test que les helpers sont importables."""
        from src.modules.utilitaires.notifications_push import (
            charger_config,
            sauvegarder_config,
        )

        assert callable(charger_config)
        assert callable(sauvegarder_config)

    def test_import_render_functions(self):
        """Test que les fonctions de rendu sont importables."""
        from src.modules.utilitaires.notifications_push import (
            render_abonnement,
            render_aide,
            render_configuration,
            render_taches_retard,
            render_test,
        )

        assert callable(render_configuration)
        assert callable(render_abonnement)
        assert callable(render_test)
        assert callable(render_taches_retard)
        assert callable(render_aide)


# ═══════════════════════════════════════════════════════════
# TESTS - HELPERS
# ═══════════════════════════════════════════════════════════


class TestHelpers:
    """Tests des fonctions helper."""

    def test_charger_config_cree_config_defaut(self, mock_st):
        """Test que charger_config crée une config par défaut si absente."""
        from src.modules.utilitaires.notifications_push import charger_config

        config = charger_config()

        assert config is not None
        assert "notif_config" in mock_st.session_state

    def test_charger_config_retourne_config_existante(self, mock_st, mock_config):
        """Test que charger_config retourne la config existante."""
        from src.modules.utilitaires.notifications_push import charger_config

        mock_st.session_state["notif_config"] = mock_config

        config = charger_config()

        assert config == mock_config

    def test_sauvegarder_config(self, mock_st, mock_config):
        """Test que sauvegarder_config stocke la config."""
        from src.modules.utilitaires.notifications_push import sauvegarder_config

        sauvegarder_config(mock_config)

        assert mock_st.session_state["notif_config"] == mock_config


# ═══════════════════════════════════════════════════════════
# TESTS - RENDER FUNCTIONS
# ═══════════════════════════════════════════════════════════


class TestRenderConfiguration:
    """Tests de la fonction render_configuration."""

    @patch("src.modules.utilitaires.notifications_push.obtenir_service_ntfy")
    @patch("src.modules.utilitaires.notifications_push.charger_config")
    def test_render_configuration_affiche_formulaire(
        self, mock_charger_config, mock_get_service, mock_st, mock_config
    ):
        """Test que render_configuration affiche le formulaire."""
        from src.modules.utilitaires.notifications_push import render_configuration

        mock_charger_config.return_value = mock_config
        mock_st.form_submit_button.return_value = False

        render_configuration()

        mock_st.subheader.assert_called_once()
        mock_st.form.assert_called_once_with("config_notif")

    @patch("src.modules.utilitaires.notifications_push.sauvegarder_config")
    @patch("src.modules.utilitaires.notifications_push.charger_config")
    def test_render_configuration_soumission_formulaire(
        self, mock_charger_config, mock_sauvegarder, mock_st, mock_config
    ):
        """Test la soumission du formulaire de configuration."""
        from src.modules.utilitaires.notifications_push import render_configuration

        mock_charger_config.return_value = mock_config
        mock_st.form_submit_button.return_value = True
        mock_st.text_input.return_value = "nouveau-topic"
        mock_st.toggle.side_effect = [True, True, False]  # actif, rappels_taches, rappels_courses
        mock_st.slider.return_value = 10

        render_configuration()

        mock_sauvegarder.assert_called_once()
        mock_st.success.assert_called()


class TestRenderAbonnement:
    """Tests de la fonction render_abonnement."""

    @patch("src.modules.utilitaires.notifications_push.obtenir_service_ntfy")
    @patch("src.modules.utilitaires.notifications_push.charger_config")
    def test_render_abonnement_affiche_qr_code(
        self, mock_charger_config, mock_get_service, mock_st, mock_config, mock_service
    ):
        """Test que render_abonnement affiche le QR code."""
        from src.modules.utilitaires.notifications_push import render_abonnement

        mock_charger_config.return_value = mock_config
        mock_get_service.return_value = mock_service

        render_abonnement()

        mock_st.subheader.assert_called_once()
        mock_service.get_subscribe_qr_url.assert_called_once()
        mock_st.image.assert_called()

    @patch("src.modules.utilitaires.notifications_push.obtenir_service_ntfy")
    @patch("src.modules.utilitaires.notifications_push.charger_config")
    def test_render_abonnement_affiche_urls(
        self, mock_charger_config, mock_get_service, mock_st, mock_config, mock_service
    ):
        """Test que render_abonnement affiche les URLs."""
        from src.modules.utilitaires.notifications_push import render_abonnement

        mock_charger_config.return_value = mock_config
        mock_get_service.return_value = mock_service

        render_abonnement()

        mock_service.get_web_url.assert_called_once()
        mock_st.markdown.assert_called()


class TestRenderTest:
    """Tests de la fonction render_test."""

    @patch("src.modules.utilitaires.notifications_push.obtenir_service_ntfy")
    @patch("src.modules.utilitaires.notifications_push.charger_config")
    def test_render_test_affiche_boutons(
        self, mock_charger_config, mock_get_service, mock_st, mock_config, mock_service
    ):
        """Test que render_test affiche les boutons de test."""
        from src.modules.utilitaires.notifications_push import render_test

        mock_charger_config.return_value = mock_config
        mock_get_service.return_value = mock_service
        mock_st.toggle.return_value = False  # Mode réel (pas démo)
        mock_st.button.return_value = False
        mock_st.form_submit_button.return_value = False

        render_test()

        mock_st.subheader.assert_called_once()
        assert mock_st.button.call_count >= 2

    @patch("src.modules.utilitaires.notifications_push.obtenir_service_ntfy")
    @patch("src.modules.utilitaires.notifications_push.charger_config")
    def test_render_test_envoie_notification_test(
        self, mock_charger_config, mock_get_service, mock_st, mock_config, mock_service
    ):
        """Test l'envoi d'une notification de test."""
        from src.modules.utilitaires.notifications_push import render_test

        mock_charger_config.return_value = mock_config
        mock_get_service.return_value = mock_service
        mock_st.toggle.return_value = False  # Mode réel (pas démo)
        mock_st.button.side_effect = [True, False]  # Premier bouton cliqué
        mock_st.form_submit_button.return_value = False

        render_test()

        mock_service.test_connexion_sync.assert_called_once()
        mock_st.success.assert_called()

    @patch("src.modules.utilitaires.notifications_push.obtenir_service_ntfy")
    @patch("src.modules.utilitaires.notifications_push.charger_config")
    def test_render_test_affiche_erreur(
        self, mock_charger_config, mock_get_service, mock_st, mock_config, mock_service
    ):
        """Test l'affichage d'erreur si test échoue."""
        from src.modules.utilitaires.notifications_push import render_test

        mock_charger_config.return_value = mock_config
        mock_service.test_connexion_sync.return_value = MagicMock(
            succes=False, message="Erreur connexion"
        )
        mock_get_service.return_value = mock_service
        mock_st.toggle.return_value = False  # Mode réel (pas démo)
        mock_st.button.side_effect = [True, False]
        mock_st.form_submit_button.return_value = False

        render_test()

        mock_st.error.assert_called()

    @patch("src.modules.utilitaires.notifications_push.obtenir_service_ntfy")
    @patch("src.modules.utilitaires.notifications_push.charger_config")
    def test_render_test_mode_demo(
        self, mock_charger_config, mock_get_service, mock_st, mock_config, mock_service
    ):
        """Test le mode démo est disponible via toggle."""
        from src.modules.utilitaires.notifications_push import render_test

        mock_charger_config.return_value = mock_config
        mock_get_service.return_value = mock_service
        mock_st.toggle.return_value = False  # Mode réel par défaut
        mock_st.button.return_value = False
        mock_st.form_submit_button.return_value = False

        render_test()

        # Vérifier que le toggle mode démo est affiché
        mock_st.toggle.assert_called_once()
        call_args = mock_st.toggle.call_args
        assert "démo" in call_args[0][0].lower() or "demo" in str(call_args).lower()


class TestRenderTachesRetard:
    """Tests de la fonction render_taches_retard."""

    @patch("src.modules.utilitaires.notifications_push.obtenir_service_ntfy")
    @patch("src.modules.utilitaires.notifications_push.charger_config")
    def test_render_taches_retard_sans_taches(
        self, mock_charger_config, mock_get_service, mock_st, mock_config, mock_service
    ):
        """Test l'affichage sans tâches en retard."""
        from src.modules.utilitaires.notifications_push import render_taches_retard

        mock_charger_config.return_value = mock_config
        mock_get_service.return_value = mock_service
        mock_service.obtenir_taches_en_retard.return_value = []
        mock_service.obtenir_taches_du_jour.return_value = []

        render_taches_retard()

        mock_st.success.assert_called()  # "Aucune tâche en retard"

    @patch("src.modules.utilitaires.notifications_push.obtenir_service_ntfy")
    @patch("src.modules.utilitaires.notifications_push.charger_config")
    def test_render_taches_retard_avec_taches(
        self,
        mock_charger_config,
        mock_get_service,
        mock_st,
        mock_config,
        mock_service,
        mock_tache_retard,
    ):
        """Test l'affichage avec tâches en retard."""
        from src.modules.utilitaires.notifications_push import render_taches_retard

        mock_charger_config.return_value = mock_config
        mock_service.obtenir_taches_en_retard.return_value = [mock_tache_retard]
        mock_service.obtenir_taches_du_jour.return_value = []
        mock_get_service.return_value = mock_service
        mock_st.button.return_value = False

        render_taches_retard()

        mock_st.metric.assert_called()
        mock_st.container.assert_called()

    @patch("src.modules.utilitaires.notifications_push.obtenir_service_ntfy")
    @patch("src.modules.utilitaires.notifications_push.charger_config")
    def test_render_taches_retard_affiche_metriques(
        self, mock_charger_config, mock_get_service, mock_st, mock_config, mock_service
    ):
        """Test l'affichage des métriques."""
        from src.modules.utilitaires.notifications_push import render_taches_retard

        mock_charger_config.return_value = mock_config
        mock_get_service.return_value = mock_service

        render_taches_retard()

        assert mock_st.metric.call_count == 3  # En retard, Aujourd'hui, Total


class TestRenderAide:
    """Tests de la fonction render_aide."""

    def test_render_aide_affiche_aide(self, mock_st):
        """Test que render_aide affiche l'aide."""
        from src.modules.utilitaires.notifications_push import render_aide

        render_aide()

        mock_st.subheader.assert_called_once()
        mock_st.markdown.assert_called()


# ═══════════════════════════════════════════════════════════
# TESTS - POINT D'ENTRÉE APP
# ═══════════════════════════════════════════════════════════


class TestApp:
    """Tests de la fonction app() point d'entrée."""

    @patch("src.modules.utilitaires.notifications_push.render_aide")
    @patch("src.modules.utilitaires.notifications_push.render_test")
    @patch("src.modules.utilitaires.notifications_push.render_taches_retard")
    @patch("src.modules.utilitaires.notifications_push.render_configuration")
    @patch("src.modules.utilitaires.notifications_push.render_abonnement")
    def test_app_affiche_titre(
        self,
        mock_render_abonnement,
        mock_render_config,
        mock_render_taches,
        mock_render_test,
        mock_render_aide,
        mock_st,
    ):
        """Test que app() affiche le titre."""
        from src.modules.utilitaires.notifications_push import app

        app()

        mock_st.title.assert_called_once_with("🔔 Notifications Push")
        mock_st.caption.assert_called()

    @patch("src.modules.utilitaires.notifications_push.render_aide")
    @patch("src.modules.utilitaires.notifications_push.render_test")
    @patch("src.modules.utilitaires.notifications_push.render_taches_retard")
    @patch("src.modules.utilitaires.notifications_push.render_configuration")
    @patch("src.modules.utilitaires.notifications_push.render_abonnement")
    def test_app_cree_tabs(
        self,
        mock_render_abonnement,
        mock_render_config,
        mock_render_taches,
        mock_render_test,
        mock_render_aide,
        mock_st,
    ):
        """Test que app() crée les onglets."""
        from src.modules.utilitaires.notifications_push import app

        app()

        mock_st.tabs.assert_called_once()
        # Vérifie que 5 onglets sont créés
        args = mock_st.tabs.call_args[0][0]
        assert len(args) == 5

    @patch("src.modules.utilitaires.notifications_push.render_aide")
    @patch("src.modules.utilitaires.notifications_push.render_test")
    @patch("src.modules.utilitaires.notifications_push.render_taches_retard")
    @patch("src.modules.utilitaires.notifications_push.render_configuration")
    @patch("src.modules.utilitaires.notifications_push.render_abonnement")
    def test_app_appelle_toutes_les_fonctions_render(
        self,
        mock_render_abonnement,
        mock_render_config,
        mock_render_taches,
        mock_render_test,
        mock_render_aide,
        mock_st,
    ):
        """Test que app() appelle toutes les fonctions de rendu."""
        from src.modules.utilitaires.notifications_push import app

        app()

        mock_render_abonnement.assert_called_once()
        mock_render_config.assert_called_once()
        mock_render_taches.assert_called_once()
        mock_render_test.assert_called_once()
        mock_render_aide.assert_called_once()

    def test_app_callable(self):
        """Test que app() est callable sans erreur."""
        from src.modules.utilitaires.notifications_push import app

        assert callable(app)


# ═══════════════════════════════════════════════════════════
# TESTS - INTÉGRATION
# ═══════════════════════════════════════════════════════════


class TestIntegration:
    """Tests d'intégration."""

    @patch("src.modules.utilitaires.notifications_push.obtenir_service_ntfy")
    def test_workflow_configuration_to_test(
        self, mock_get_service, mock_st, mock_config, mock_service
    ):
        """Test le workflow configuration → test."""
        from src.modules.utilitaires.notifications_push import (
            charger_config,
            sauvegarder_config,
        )

        # Sauvegarder une config
        sauvegarder_config(mock_config)

        # Recharger et vérifier
        config = charger_config()
        assert config == mock_config

    @patch("src.modules.utilitaires.notifications_push.obtenir_service_ntfy")
    def test_constante_help_ntfy_contenu(self, mock_get_service):
        """Test le contenu de la constante HELP_NTFY."""
        from src.modules.utilitaires.notifications_push import HELP_NTFY

        assert "ntfy.sh" in HELP_NTFY
        assert "Android" in HELP_NTFY or "téléphone" in HELP_NTFY
        assert "Gratuit" in HELP_NTFY or "gratuit" in HELP_NTFY
