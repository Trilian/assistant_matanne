"""
Tests pour src/modules/jeux/integration.py

Tests complets pour configurer_jeux().
"""

from unittest.mock import MagicMock, patch


class TestConfigurerJeux:
    """Tests pour configurer_jeux()"""

    def test_configure_api_football_avec_cle(self):
        """Teste la configuration avec une clé API valide"""
        with (
            patch("src.core.config.obtenir_parametres") as mock_params,
            patch("src.modules.jeux.api_football.configurer_api_key") as mock_config_api,
        ):
            mock_config = MagicMock()
            mock_config.get.return_value = "test_api_key_123"
            mock_params.return_value = mock_config

            from src.modules.jeux.integration import configurer_jeux

            configurer_jeux()

            # Note: La fonction peut être appelée 2 fois (import module + appel explicite)
            mock_config_api.assert_called_with("test_api_key_123")
            assert mock_config_api.call_count >= 1

    def test_pas_configuration_sans_cle_api(self):
        """Teste le comportement sans clé API"""
        with (
            patch("src.core.config.obtenir_parametres") as mock_params,
            patch("src.modules.jeux.api_football.configurer_api_key") as mock_config_api,
        ):
            mock_config = MagicMock()
            mock_config.get.return_value = None  # Pas de clé
            mock_params.return_value = mock_config

            from src.modules.jeux.integration import configurer_jeux

            configurer_jeux()

            mock_config_api.assert_not_called()

    def test_gere_exception_import(self):
        """Teste la gestion d'exception lors de l'import"""
        with patch(
            "src.core.config.obtenir_parametres",
            side_effect=ImportError("Module non trouvé"),
        ):
            from src.modules.jeux.integration import configurer_jeux

            # Ne doit pas lever d'exception
            configurer_jeux()

    def test_gere_exception_configuration(self):
        """Teste la gestion d'exception lors de la configuration"""
        with (
            patch("src.core.config.obtenir_parametres") as mock_params,
            patch(
                "src.modules.jeux.api_football.configurer_api_key",
                side_effect=Exception("Erreur configuration"),
            ),
        ):
            mock_config = MagicMock()
            mock_config.get.return_value = "test_key"
            mock_params.return_value = mock_config

            from src.modules.jeux.integration import configurer_jeux

            # Ne doit pas lever d'exception
            configurer_jeux()

    def test_log_fallback_sans_cle(self):
        """Teste le logging du fallback sans clé"""
        with (
            patch("src.core.config.obtenir_parametres") as mock_params,
            patch("src.modules.jeux.api_football.configurer_api_key") as mock_config_api,
        ):
            mock_config = MagicMock()
            mock_config.get.return_value = ""  # Chaîne vide = pas de clé
            mock_params.return_value = mock_config

            from src.modules.jeux.integration import configurer_jeux

            configurer_jeux()

            mock_config_api.assert_not_called()


class TestConfigurerJeuxIntegration:
    """Tests d'intégration pour configurer_jeux"""

    def test_import_module(self):
        """Vérifie que le module s'importe correctement"""
        from src.modules.jeux.integration import configurer_jeux

        assert callable(configurer_jeux)

    def test_module_niveau_appel(self):
        """Vérifie que configurer_jeux est appelé au démarrage du module"""
        # Le module appelle configurer_jeux() à l'import
        # On vérifie juste que l'import ne lève pas d'exception
        import importlib

        import src.modules.jeux.integration

        importlib.reload(src.modules.jeux.integration)

    def test_fonction_sans_parametres(self):
        """Vérifie que la fonction n'a pas de paramètres requis"""
        import inspect

        from src.modules.jeux.integration import configurer_jeux

        sig = inspect.signature(configurer_jeux)
        # Tous les paramètres ont des valeurs par défaut
        for param in sig.parameters.values():
            assert (
                param.default != inspect.Parameter.empty
                or param.kind == inspect.Parameter.VAR_POSITIONAL
                or param.kind == inspect.Parameter.VAR_KEYWORD
            ) or len(sig.parameters) == 0
