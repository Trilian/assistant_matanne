"""
Tests pour src/modules/jeux/loto/sync.py

Tests complets pour sync_tirages_loto().
"""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest


class TestSyncTiragesLoto:
    """Tests pour sync_tirages_loto()"""

    @pytest.fixture
    def mock_service(self):
        """Fixture pour mocker le service loto crud"""
        with patch("src.modules.jeux.loto.sync.get_loto_crud_service") as mock_factory:
            mock_svc = MagicMock()
            mock_factory.return_value = mock_svc
            mock_svc.sync_tirages.return_value = 0
            yield mock_svc

    @pytest.fixture
    def mock_charger_tirages(self):
        """Fixture pour mocker charger_tirages_loto"""
        with patch("src.modules.jeux.loto.sync.charger_tirages_loto") as mock:
            yield mock

    @pytest.fixture
    def mock_logger(self):
        """Fixture pour mocker le logger"""
        with patch("src.modules.jeux.loto.sync.logger") as mock:
            yield mock

    def test_retourne_zero_sans_donnees_api(self, mock_service, mock_charger_tirages, mock_logger):
        """Teste le retour 0 quand l'API ne retourne rien"""
        mock_charger_tirages.return_value = None

        from src.modules.jeux.loto.sync import sync_tirages_loto

        result = sync_tirages_loto(limite=10)

        assert result == 0
        mock_logger.warning.assert_called()

    def test_retourne_zero_liste_vide(self, mock_service, mock_charger_tirages, mock_logger):
        """Teste le retour 0 quand l'API retourne une liste vide"""
        mock_charger_tirages.return_value = []

        from src.modules.jeux.loto.sync import sync_tirages_loto

        result = sync_tirages_loto(limite=10)

        assert result == 0

    def test_ajoute_nouveau_tirage_format_date_iso(
        self, mock_service, mock_charger_tirages, mock_logger
    ):
        """Teste l'ajout d'un tirage avec date au format ISO"""
        tirages_api = [
            {
                "date": "2025-01-06",
                "numeros": [7, 12, 23, 34, 45],
                "numero_chance": 8,
                "jackpot": 5000000,
            }
        ]
        mock_charger_tirages.return_value = tirages_api
        mock_service.sync_tirages.return_value = 1

        from src.modules.jeux.loto.sync import sync_tirages_loto

        result = sync_tirages_loto(limite=10)

        assert result == 1
        mock_service.sync_tirages.assert_called_once_with(tirages_api)

    def test_ajoute_nouveau_tirage_format_date_fr(
        self, mock_service, mock_charger_tirages, mock_logger
    ):
        """Teste l'ajout d'un tirage avec date au format français"""
        tirages_api = [
            {
                "date": "06/01/2025",
                "numeros": [1, 2, 3, 4, 5],
                "numero_chance": 1,
                "jackpot": 1000000,
            }
        ]
        mock_charger_tirages.return_value = tirages_api
        mock_service.sync_tirages.return_value = 1

        from src.modules.jeux.loto.sync import sync_tirages_loto

        result = sync_tirages_loto(limite=10)

        assert result == 1
        mock_service.sync_tirages.assert_called_once_with(tirages_api)

    def test_ajoute_tirage_avec_date_objet(self, mock_service, mock_charger_tirages, mock_logger):
        """Teste l'ajout d'un tirage avec objet date Python"""
        tirages_api = [
            {
                "date": date(2025, 1, 6),
                "numeros": [10, 20, 30, 40, 49],
                "numero_chance": 5,
                "jackpot": 2000000,
            }
        ]
        mock_charger_tirages.return_value = tirages_api
        mock_service.sync_tirages.return_value = 1

        from src.modules.jeux.loto.sync import sync_tirages_loto

        result = sync_tirages_loto(limite=10)

        assert result == 1

    def test_ignore_tirage_existant(self, mock_service, mock_charger_tirages, mock_logger):
        """Teste que les tirages existants sont gérés par le service"""
        tirages_api = [
            {
                "date": "2025-01-06",
                "numeros": [7, 12, 23, 34, 45],
                "numero_chance": 8,
                "jackpot": 5000000,
            }
        ]
        mock_charger_tirages.return_value = tirages_api
        mock_service.sync_tirages.return_value = 0

        from src.modules.jeux.loto.sync import sync_tirages_loto

        result = sync_tirages_loto(limite=10)

        assert result == 0

    def test_ignore_tirage_sans_5_numeros(self, mock_service, mock_charger_tirages, mock_logger):
        """Teste que les tirages invalides sont gérés par le service"""
        tirages_api = [
            {
                "date": "2025-01-06",
                "numeros": [1, 2, 3, 4],
                "numero_chance": 8,
                "jackpot": 5000000,
            }
        ]
        mock_charger_tirages.return_value = tirages_api
        mock_service.sync_tirages.return_value = 0

        from src.modules.jeux.loto.sync import sync_tirages_loto

        result = sync_tirages_loto(limite=10)

        assert result == 0

    def test_ignore_tirage_sans_numero_chance(
        self, mock_service, mock_charger_tirages, mock_logger
    ):
        """Teste que les tirages sans numéro chance sont gérés par le service"""
        tirages_api = [
            {
                "date": "2025-01-06",
                "numeros": [1, 2, 3, 4, 5],
                "numero_chance": None,
                "jackpot": 5000000,
            }
        ]
        mock_charger_tirages.return_value = tirages_api
        mock_service.sync_tirages.return_value = 0

        from src.modules.jeux.loto.sync import sync_tirages_loto

        result = sync_tirages_loto(limite=10)

        assert result == 0

    def test_ignore_tirage_date_invalide(self, mock_service, mock_charger_tirages, mock_logger):
        """Teste que les tirages avec date invalide sont gérés par le service"""
        tirages_api = [
            {
                "date": "invalid-date",
                "numeros": [1, 2, 3, 4, 5],
                "numero_chance": 8,
                "jackpot": 5000000,
            }
        ]
        mock_charger_tirages.return_value = tirages_api
        mock_service.sync_tirages.return_value = 0

        from src.modules.jeux.loto.sync import sync_tirages_loto

        result = sync_tirages_loto(limite=10)

        assert result == 0

    def test_donnees_brutes_passees_au_service(
        self, mock_service, mock_charger_tirages, mock_logger
    ):
        """Teste que les données brutes sont passées au service"""
        tirages_api = [
            {
                "date": "2025-01-06",
                "numeros": [45, 12, 7, 34, 23],
                "numero_chance": 8,
                "jackpot": 5000000,
            }
        ]
        mock_charger_tirages.return_value = tirages_api
        mock_service.sync_tirages.return_value = 1

        from src.modules.jeux.loto.sync import sync_tirages_loto

        result = sync_tirages_loto(limite=10)

        assert result == 1
        mock_service.sync_tirages.assert_called_once_with(tirages_api)

    def test_plusieurs_tirages_mixtes(self, mock_service, mock_charger_tirages, mock_logger):
        """Teste avec plusieurs tirages (gérés par le service)"""
        tirages_api = [
            {
                "date": "2025-01-06",
                "numeros": [1, 2, 3, 4, 5],
                "numero_chance": 1,
                "jackpot": 1000000,
            },
            {
                "date": "2025-01-08",
                "numeros": [10, 20, 30, 40, 49],
                "numero_chance": 5,
                "jackpot": 2000000,
            },
        ]
        mock_charger_tirages.return_value = tirages_api
        mock_service.sync_tirages.return_value = 1

        from src.modules.jeux.loto.sync import sync_tirages_loto

        result = sync_tirages_loto(limite=10)

        assert result == 1

    def test_gere_erreur_service(self, mock_service, mock_charger_tirages, mock_logger):
        """Teste la gestion d'erreur du service"""
        tirages_api = [
            {
                "date": "2025-01-06",
                "numeros": [1, 2, 3, 4, 5],
                "numero_chance": 1,
                "jackpot": 1000000,
            }
        ]
        mock_charger_tirages.return_value = tirages_api
        mock_service.sync_tirages.side_effect = Exception("Commit error")

        from src.modules.jeux.loto.sync import sync_tirages_loto

        result = sync_tirages_loto(limite=10)

        assert result == 0
        mock_logger.error.assert_called()

    def test_gere_exception_generale(self, mock_charger_tirages, mock_logger):
        """Teste la gestion d'exception générale"""
        mock_charger_tirages.side_effect = Exception("API Error")

        from src.modules.jeux.loto.sync import sync_tirages_loto

        result = sync_tirages_loto(limite=10)

        assert result == 0
        mock_logger.error.assert_called()

    def test_limite_par_defaut(self, mock_service, mock_charger_tirages, mock_logger):
        """Teste la limite par défaut de 50"""
        mock_charger_tirages.return_value = []

        from src.modules.jeux.loto.sync import sync_tirages_loto

        sync_tirages_loto()

        mock_charger_tirages.assert_called_once_with(limite=50)

    def test_limite_personnalisee(self, mock_service, mock_charger_tirages, mock_logger):
        """Teste une limite personnalisée"""
        mock_charger_tirages.return_value = []

        from src.modules.jeux.loto.sync import sync_tirages_loto

        sync_tirages_loto(limite=25)

        mock_charger_tirages.assert_called_once_with(limite=25)

    def test_tirage_avec_plus_de_5_numeros(self, mock_service, mock_charger_tirages, mock_logger):
        """Teste que les données brutes sont passées au service"""
        tirages_api = [
            {
                "date": "2025-01-06",
                "numeros": [1, 2, 3, 4, 5, 6, 7],
                "numero_chance": 8,
                "jackpot": 5000000,
            }
        ]
        mock_charger_tirages.return_value = tirages_api
        mock_service.sync_tirages.return_value = 1

        from src.modules.jeux.loto.sync import sync_tirages_loto

        result = sync_tirages_loto(limite=10)

        assert result == 1
        mock_service.sync_tirages.assert_called_once_with(tirages_api)


class TestSyncTiragesLotoIntegration:
    """Tests d'intégration pour sync_tirages_loto"""

    def test_import_module(self):
        """Vérifie que le module s'importe correctement"""
        from src.modules.jeux.loto.sync import sync_tirages_loto

        assert callable(sync_tirages_loto)

    def test_signature_fonction(self):
        """Vérifie la signature de la fonction"""
        import inspect

        from src.modules.jeux.loto.sync import sync_tirages_loto

        sig = inspect.signature(sync_tirages_loto)
        params = list(sig.parameters.keys())
        assert "limite" in params

    def test_valeur_defaut_limite(self):
        """Vérifie la valeur par défaut du paramètre limite"""
        import inspect

        from src.modules.jeux.loto.sync import sync_tirages_loto

        sig = inspect.signature(sync_tirages_loto)
        assert sig.parameters["limite"].default == 50
