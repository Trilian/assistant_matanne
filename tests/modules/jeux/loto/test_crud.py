"""
Tests pour src/modules/jeux/loto/crud.py

Tests complets pour ajouter_tirage et enregistrer_grille.
"""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest


class TestAjouterTirage:
    """Tests pour ajouter_tirage()"""

    @pytest.fixture
    def mock_st(self):
        """Mock streamlit"""
        with patch("src.modules.jeux.loto.crud.st") as mock:
            yield mock

    @pytest.fixture
    def mock_db(self):
        """Mock contexte DB"""
        with patch("src.modules.jeux.loto.crud.obtenir_contexte_db") as mock_ctx:
            mock_session = MagicMock()
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
            yield mock_session, mock_ctx

    @pytest.fixture
    def mock_verifier_grille(self):
        """Mock verifier_grille"""
        with patch("src.modules.jeux.loto.crud.verifier_grille") as mock:
            mock.return_value = {
                "bons_numeros": 3,
                "chance_ok": False,
                "rang": 6,
                "gain": 20,
            }
            yield mock

    def test_retourne_false_si_moins_de_5_numeros(self, mock_st, mock_db):
        """Valide qu'il faut exactement 5 numéros"""
        from src.modules.jeux.loto.crud import ajouter_tirage

        result = ajouter_tirage(date(2025, 1, 6), [1, 2, 3, 4], 5)

        assert result is False
        mock_st.error.assert_called()

    def test_retourne_false_si_plus_de_5_numeros(self, mock_st, mock_db):
        """Valide qu'il faut exactement 5 numéros"""
        from src.modules.jeux.loto.crud import ajouter_tirage

        result = ajouter_tirage(date(2025, 1, 6), [1, 2, 3, 4, 5, 6], 5)

        assert result is False
        mock_st.error.assert_called()

    def test_trie_numeros_avant_insertion(self, mock_st, mock_db, mock_verifier_grille):
        """Vérifie que les numéros sont triés"""
        mock_session, _ = mock_db
        mock_session.query.return_value.filter.return_value.all.return_value = []

        from src.modules.jeux.loto.crud import ajouter_tirage

        result = ajouter_tirage(date(2025, 1, 6), [45, 12, 7, 34, 23], 8)

        assert result is True
        # Vérifie que add a été appelé
        mock_session.add.assert_called_once()
        tirage = mock_session.add.call_args[0][0]
        assert tirage.numero_1 == 7
        assert tirage.numero_2 == 12
        assert tirage.numero_3 == 23
        assert tirage.numero_4 == 34
        assert tirage.numero_5 == 45

    def test_enregistre_tirage_avec_jackpot(self, mock_st, mock_db, mock_verifier_grille):
        """Teste l'enregistrement avec jackpot"""
        mock_session, _ = mock_db
        mock_session.query.return_value.filter.return_value.all.return_value = []

        from src.modules.jeux.loto.crud import ajouter_tirage

        result = ajouter_tirage(date(2025, 1, 6), [1, 2, 3, 4, 5], 8, jackpot=5000000)

        assert result is True
        tirage = mock_session.add.call_args[0][0]
        assert tirage.jackpot_euros == 5000000

    def test_met_a_jour_grilles_en_attente(self, mock_st, mock_db, mock_verifier_grille):
        """Vérifie la mise à jour des grilles en attente"""
        mock_session, _ = mock_db

        # Mock grille en attente
        mock_grille = MagicMock()
        mock_grille.tirage_id = None
        mock_grille.numeros = [1, 2, 3, 4, 5]
        mock_grille.numero_chance = 8
        mock_session.query.return_value.filter.return_value.all.return_value = [mock_grille]

        from src.modules.jeux.loto.crud import ajouter_tirage

        result = ajouter_tirage(date(2025, 1, 6), [1, 2, 3, 4, 5], 8)

        assert result is True
        mock_verifier_grille.assert_called_once()
        assert mock_grille.rang == 6
        assert mock_grille.gain == 20

    def test_affiche_succes_apres_ajout(self, mock_st, mock_db, mock_verifier_grille):
        """Vérifie le message de succès"""
        mock_session, _ = mock_db
        mock_session.query.return_value.filter.return_value.all.return_value = []

        from src.modules.jeux.loto.crud import ajouter_tirage

        ajouter_tirage(date(2025, 1, 6), [1, 2, 3, 4, 5], 8)

        mock_st.success.assert_called()

    def test_gere_exception_db(self, mock_st, mock_db):
        """Teste la gestion d'erreur DB"""
        mock_session, mock_ctx = mock_db
        mock_ctx.return_value.__enter__ = MagicMock(side_effect=Exception("DB Error"))

        from src.modules.jeux.loto.crud import ajouter_tirage

        result = ajouter_tirage(date(2025, 1, 6), [1, 2, 3, 4, 5], 8)

        assert result is False
        mock_st.error.assert_called()


class TestEnregistrerGrille:
    """Tests pour enregistrer_grille()"""

    @pytest.fixture
    def mock_st(self):
        """Mock streamlit"""
        with patch("src.modules.jeux.loto.crud.st") as mock:
            yield mock

    @pytest.fixture
    def mock_db(self):
        """Mock contexte DB"""
        with patch("src.modules.jeux.loto.crud.obtenir_contexte_db") as mock_ctx:
            mock_session = MagicMock()
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
            yield mock_session, mock_ctx

    def test_retourne_false_si_pas_5_numeros(self, mock_st, mock_db):
        """Valide qu'il faut exactement 5 numéros"""
        from src.modules.jeux.loto.crud import enregistrer_grille

        result = enregistrer_grille([1, 2, 3], 5)

        assert result is False
        mock_st.error.assert_called()

    def test_trie_numeros_avant_insertion(self, mock_st, mock_db):
        """Vérifie que les numéros sont triés"""
        mock_session, _ = mock_db

        from src.modules.jeux.loto.crud import enregistrer_grille

        result = enregistrer_grille([49, 25, 7, 1, 33], 5)

        assert result is True
        grille = mock_session.add.call_args[0][0]
        assert grille.numero_1 == 1
        assert grille.numero_2 == 7
        assert grille.numero_3 == 25
        assert grille.numero_4 == 33
        assert grille.numero_5 == 49

    def test_enregistre_source_et_type_par_defaut(self, mock_st, mock_db):
        """Teste les valeurs par défaut"""
        mock_session, _ = mock_db

        from src.modules.jeux.loto.crud import enregistrer_grille

        enregistrer_grille([1, 2, 3, 4, 5], 8)

        grille = mock_session.add.call_args[0][0]
        assert grille.source_prediction == "manuel"
        assert grille.est_virtuelle is True

    def test_enregistre_source_personnalisee(self, mock_st, mock_db):
        """Teste une source personnalisée"""
        mock_session, _ = mock_db

        from src.modules.jeux.loto.crud import enregistrer_grille

        enregistrer_grille([1, 2, 3, 4, 5], 8, source="ia", est_virtuelle=False)

        grille = mock_session.add.call_args[0][0]
        assert grille.source_prediction == "ia"
        assert grille.est_virtuelle is False

    def test_affiche_succes_apres_enregistrement(self, mock_st, mock_db):
        """Vérifie le message de succès"""
        mock_session, _ = mock_db

        from src.modules.jeux.loto.crud import enregistrer_grille

        enregistrer_grille([1, 2, 3, 4, 5], 8)

        mock_st.success.assert_called()
        call_arg = mock_st.success.call_args[0][0]
        assert "1-2-3-4-5" in call_arg
        assert "N°8" in call_arg

    def test_gere_exception_db(self, mock_st, mock_db):
        """Teste la gestion d'erreur DB"""
        mock_session, mock_ctx = mock_db
        mock_ctx.return_value.__enter__ = MagicMock(side_effect=Exception("DB Error"))

        from src.modules.jeux.loto.crud import enregistrer_grille

        result = enregistrer_grille([1, 2, 3, 4, 5], 8)

        assert result is False
        mock_st.error.assert_called()


class TestCrudIntegration:
    """Tests d'intégration pour le module crud"""

    def test_import_ajouter_tirage(self):
        """Vérifie que ajouter_tirage est importable"""
        from src.modules.jeux.loto.crud import ajouter_tirage

        assert callable(ajouter_tirage)

    def test_import_enregistrer_grille(self):
        """Vérifie que enregistrer_grille est importable"""
        from src.modules.jeux.loto.crud import enregistrer_grille

        assert callable(enregistrer_grille)
