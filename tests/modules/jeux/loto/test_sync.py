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
    def mock_db_context(self):
        """Fixture pour mocker le contexte DB"""
        with patch("src.modules.jeux.loto.sync.obtenir_contexte_db") as mock_ctx:
            mock_session = MagicMock()
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
            yield mock_session, mock_ctx

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

    def test_retourne_zero_sans_donnees_api(
        self, mock_db_context, mock_charger_tirages, mock_logger
    ):
        """Teste le retour 0 quand l'API ne retourne rien"""
        mock_charger_tirages.return_value = None

        from src.modules.jeux.loto.sync import sync_tirages_loto

        result = sync_tirages_loto(limite=10)

        assert result == 0
        mock_logger.warning.assert_called()

    def test_retourne_zero_liste_vide(self, mock_db_context, mock_charger_tirages, mock_logger):
        """Teste le retour 0 quand l'API retourne une liste vide"""
        mock_charger_tirages.return_value = []

        from src.modules.jeux.loto.sync import sync_tirages_loto

        result = sync_tirages_loto(limite=10)

        assert result == 0

    def test_ajoute_nouveau_tirage_format_date_iso(
        self, mock_db_context, mock_charger_tirages, mock_logger
    ):
        """Teste l'ajout d'un tirage avec date au format ISO"""
        mock_session, _ = mock_db_context
        mock_session.query.return_value.filter.return_value.first.return_value = None

        mock_charger_tirages.return_value = [
            {
                "date": "2025-01-06",
                "numeros": [7, 12, 23, 34, 45],
                "numero_chance": 8,
                "jackpot": 5000000,
            }
        ]

        from src.modules.jeux.loto.sync import sync_tirages_loto

        result = sync_tirages_loto(limite=10)

        assert result == 1
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_ajoute_nouveau_tirage_format_date_fr(
        self, mock_db_context, mock_charger_tirages, mock_logger
    ):
        """Teste l'ajout d'un tirage avec date au format français"""
        mock_session, _ = mock_db_context
        mock_session.query.return_value.filter.return_value.first.return_value = None

        mock_charger_tirages.return_value = [
            {
                "date": "06/01/2025",
                "numeros": [1, 2, 3, 4, 5],
                "numero_chance": 1,
                "jackpot": 1000000,
            }
        ]

        from src.modules.jeux.loto.sync import sync_tirages_loto

        result = sync_tirages_loto(limite=10)

        assert result == 1

    def test_ajoute_tirage_avec_date_objet(
        self, mock_db_context, mock_charger_tirages, mock_logger
    ):
        """Teste l'ajout d'un tirage avec objet date Python"""
        mock_session, _ = mock_db_context
        mock_session.query.return_value.filter.return_value.first.return_value = None

        mock_charger_tirages.return_value = [
            {
                "date": date(2025, 1, 6),
                "numeros": [10, 20, 30, 40, 49],
                "numero_chance": 5,
                "jackpot": 2000000,
            }
        ]

        from src.modules.jeux.loto.sync import sync_tirages_loto

        result = sync_tirages_loto(limite=10)

        assert result == 1

    def test_ignore_tirage_existant(self, mock_db_context, mock_charger_tirages, mock_logger):
        """Teste que les tirages existants sont ignorés"""
        mock_session, _ = mock_db_context

        # Tirage existant en DB
        existing_tirage = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = existing_tirage

        mock_charger_tirages.return_value = [
            {
                "date": "2025-01-06",
                "numeros": [7, 12, 23, 34, 45],
                "numero_chance": 8,
                "jackpot": 5000000,
            }
        ]

        from src.modules.jeux.loto.sync import sync_tirages_loto

        result = sync_tirages_loto(limite=10)

        assert result == 0
        mock_session.add.assert_not_called()

    def test_ignore_tirage_sans_5_numeros(self, mock_db_context, mock_charger_tirages, mock_logger):
        """Teste que les tirages avec moins de 5 numéros sont ignorés"""
        mock_session, _ = mock_db_context
        mock_session.query.return_value.filter.return_value.first.return_value = None

        mock_charger_tirages.return_value = [
            {
                "date": "2025-01-06",
                "numeros": [1, 2, 3, 4],  # Seulement 4 numéros
                "numero_chance": 8,
                "jackpot": 5000000,
            }
        ]

        from src.modules.jeux.loto.sync import sync_tirages_loto

        result = sync_tirages_loto(limite=10)

        assert result == 0

    def test_ignore_tirage_sans_numero_chance(
        self, mock_db_context, mock_charger_tirages, mock_logger
    ):
        """Teste que les tirages sans numéro chance sont ignorés"""
        mock_session, _ = mock_db_context
        mock_session.query.return_value.filter.return_value.first.return_value = None

        mock_charger_tirages.return_value = [
            {
                "date": "2025-01-06",
                "numeros": [1, 2, 3, 4, 5],
                "numero_chance": None,  # Pas de numéro chance
                "jackpot": 5000000,
            }
        ]

        from src.modules.jeux.loto.sync import sync_tirages_loto

        result = sync_tirages_loto(limite=10)

        assert result == 0

    def test_ignore_tirage_date_invalide(self, mock_db_context, mock_charger_tirages, mock_logger):
        """Teste que les tirages avec date invalide sont ignorés"""
        mock_session, _ = mock_db_context
        mock_session.query.return_value.filter.return_value.first.return_value = None

        mock_charger_tirages.return_value = [
            {
                "date": "invalid-date",
                "numeros": [1, 2, 3, 4, 5],
                "numero_chance": 8,
                "jackpot": 5000000,
            }
        ]

        from src.modules.jeux.loto.sync import sync_tirages_loto

        result = sync_tirages_loto(limite=10)

        assert result == 0

    def test_tri_numeros_avant_insertion(self, mock_db_context, mock_charger_tirages, mock_logger):
        """Teste que les numéros sont triés avant insertion"""
        mock_session, _ = mock_db_context
        mock_session.query.return_value.filter.return_value.first.return_value = None

        mock_charger_tirages.return_value = [
            {
                "date": "2025-01-06",
                "numeros": [45, 12, 7, 34, 23],  # Non triés
                "numero_chance": 8,
                "jackpot": 5000000,
            }
        ]

        from src.modules.jeux.loto.sync import sync_tirages_loto

        result = sync_tirages_loto(limite=10)

        assert result == 1
        # Vérifie que add a été appelé avec un tirage
        args, kwargs = mock_session.add.call_args
        tirage = args[0]
        assert tirage.numero_1 == 7
        assert tirage.numero_2 == 12
        assert tirage.numero_3 == 23
        assert tirage.numero_4 == 34
        assert tirage.numero_5 == 45

    def test_plusieurs_tirages_mixtes(self, mock_db_context, mock_charger_tirages, mock_logger):
        """Teste avec plusieurs tirages (nouveaux et existants)"""
        mock_session, _ = mock_db_context

        call_count = [0]

        def first_side_effect():
            call_count[0] += 1
            # Premier tirage existe, deuxième non
            return MagicMock() if call_count[0] == 1 else None

        mock_session.query.return_value.filter.return_value.first = first_side_effect

        mock_charger_tirages.return_value = [
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

        from src.modules.jeux.loto.sync import sync_tirages_loto

        result = sync_tirages_loto(limite=10)

        # Seulement 1 nouveau tirage (le deuxième)
        assert result == 1

    def test_rollback_sur_erreur_commit(self, mock_db_context, mock_charger_tirages, mock_logger):
        """Teste le rollback en cas d'erreur au commit"""
        mock_session, _ = mock_db_context
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_session.commit.side_effect = Exception("Commit error")

        mock_charger_tirages.return_value = [
            {
                "date": "2025-01-06",
                "numeros": [1, 2, 3, 4, 5],
                "numero_chance": 1,
                "jackpot": 1000000,
            }
        ]

        from src.modules.jeux.loto.sync import sync_tirages_loto

        sync_tirages_loto(limite=10)

        mock_session.rollback.assert_called_once()
        mock_logger.error.assert_called()

    def test_gere_exception_generale(self, mock_charger_tirages, mock_logger):
        """Teste la gestion d'exception générale"""
        mock_charger_tirages.side_effect = Exception("API Error")

        from src.modules.jeux.loto.sync import sync_tirages_loto

        result = sync_tirages_loto(limite=10)

        assert result == 0
        mock_logger.error.assert_called()

    def test_limite_par_defaut(self, mock_db_context, mock_charger_tirages, mock_logger):
        """Teste la limite par défaut de 50"""
        mock_charger_tirages.return_value = []

        from src.modules.jeux.loto.sync import sync_tirages_loto

        sync_tirages_loto()

        mock_charger_tirages.assert_called_once_with(limite=50)

    def test_limite_personnalisee(self, mock_db_context, mock_charger_tirages, mock_logger):
        """Teste une limite personnalisée"""
        mock_charger_tirages.return_value = []

        from src.modules.jeux.loto.sync import sync_tirages_loto

        sync_tirages_loto(limite=25)

        mock_charger_tirages.assert_called_once_with(limite=25)

    def test_tirage_avec_plus_de_5_numeros(
        self, mock_db_context, mock_charger_tirages, mock_logger
    ):
        """Teste qu'on prend seulement les 5 premiers numéros triés"""
        mock_session, _ = mock_db_context
        mock_session.query.return_value.filter.return_value.first.return_value = None

        mock_charger_tirages.return_value = [
            {
                "date": "2025-01-06",
                "numeros": [1, 2, 3, 4, 5, 6, 7],  # Plus de 5 numéros
                "numero_chance": 8,
                "jackpot": 5000000,
            }
        ]

        from src.modules.jeux.loto.sync import sync_tirages_loto

        result = sync_tirages_loto(limite=10)

        assert result == 1
        args, kwargs = mock_session.add.call_args
        tirage = args[0]
        # Vérifie qu'on a bien les 5 premiers triés
        assert tirage.numero_5 == 5  # Pas 6 ou 7


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
