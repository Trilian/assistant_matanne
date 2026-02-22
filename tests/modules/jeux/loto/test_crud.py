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
    def mock_service(self):
        """Mock service loto crud"""
        with patch("src.modules.jeux.loto.crud.get_loto_crud_service") as mock_factory:
            mock_svc = MagicMock()
            mock_factory.return_value = mock_svc
            mock_svc.ajouter_tirage.return_value = True
            yield mock_svc

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

    def test_retourne_false_si_moins_de_5_numeros(self, mock_st, mock_service):
        """Valide qu'il faut exactement 5 numéros"""
        from src.modules.jeux.loto.crud import ajouter_tirage

        result = ajouter_tirage(date(2025, 1, 6), [1, 2, 3, 4], 5)

        assert result is False
        mock_st.error.assert_called()

    def test_retourne_false_si_plus_de_5_numeros(self, mock_st, mock_service):
        """Valide qu'il faut exactement 5 numéros"""
        from src.modules.jeux.loto.crud import ajouter_tirage

        result = ajouter_tirage(date(2025, 1, 6), [1, 2, 3, 4, 5, 6], 5)

        assert result is False
        mock_st.error.assert_called()

    def test_delegue_au_service_avec_bons_args(self, mock_st, mock_service):
        """Vérifie que le service est appelé avec les bons arguments"""
        from src.modules.jeux.loto.crud import ajouter_tirage

        result = ajouter_tirage(date(2025, 1, 6), [45, 12, 7, 34, 23], 8)

        assert result is True
        mock_service.ajouter_tirage.assert_called_once()
        call_kwargs = mock_service.ajouter_tirage.call_args[1]
        assert call_kwargs["numeros"] == [45, 12, 7, 34, 23]
        assert call_kwargs["chance"] == 8
        assert call_kwargs["date_t"] == date(2025, 1, 6)

    def test_enregistre_tirage_avec_jackpot(self, mock_st, mock_service):
        """Teste l'enregistrement avec jackpot"""
        from src.modules.jeux.loto.crud import ajouter_tirage

        result = ajouter_tirage(date(2025, 1, 6), [1, 2, 3, 4, 5], 8, jackpot=5000000)

        assert result is True
        call_kwargs = mock_service.ajouter_tirage.call_args[1]
        assert call_kwargs["jackpot"] == 5000000

    def test_passe_verifier_fn_au_service(self, mock_st, mock_service, mock_verifier_grille):
        """Vérifie que verifier_fn est passée au service"""
        from src.modules.jeux.loto.crud import ajouter_tirage

        result = ajouter_tirage(date(2025, 1, 6), [1, 2, 3, 4, 5], 8)

        assert result is True
        call_kwargs = mock_service.ajouter_tirage.call_args[1]
        assert call_kwargs["verifier_fn"] is not None

    def test_affiche_succes_apres_ajout(self, mock_st, mock_service):
        """Vérifie le message de succès"""
        from src.modules.jeux.loto.crud import ajouter_tirage

        ajouter_tirage(date(2025, 1, 6), [1, 2, 3, 4, 5], 8)

        mock_st.success.assert_called()

    def test_gere_exception_db(self, mock_st, mock_service):
        """Teste la gestion d'erreur DB"""
        mock_service.ajouter_tirage.side_effect = Exception("DB Error")

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
    def mock_service(self):
        """Mock service loto crud"""
        with patch("src.modules.jeux.loto.crud.get_loto_crud_service") as mock_factory:
            mock_svc = MagicMock()
            mock_factory.return_value = mock_svc
            mock_svc.enregistrer_grille.return_value = True
            yield mock_svc

    def test_retourne_false_si_pas_5_numeros(self, mock_st, mock_service):
        """Valide qu'il faut exactement 5 numéros"""
        from src.modules.jeux.loto.crud import enregistrer_grille

        result = enregistrer_grille([1, 2, 3], 5)

        assert result is False
        mock_st.error.assert_called()

    def test_delegue_au_service_avec_bons_args(self, mock_st, mock_service):
        """Vérifie que le service est appelé avec les bons arguments"""
        from src.modules.jeux.loto.crud import enregistrer_grille

        result = enregistrer_grille([49, 25, 7, 1, 33], 5)

        assert result is True
        mock_service.enregistrer_grille.assert_called_once()
        call_kwargs = mock_service.enregistrer_grille.call_args[1]
        assert call_kwargs["numeros"] == [49, 25, 7, 1, 33]
        assert call_kwargs["chance"] == 5

    def test_enregistre_source_et_type_par_defaut(self, mock_st, mock_service):
        """Teste les valeurs par défaut"""
        from src.modules.jeux.loto.crud import enregistrer_grille

        enregistrer_grille([1, 2, 3, 4, 5], 8)

        call_kwargs = mock_service.enregistrer_grille.call_args[1]
        assert call_kwargs["source"] == "manuel"
        assert call_kwargs["est_virtuelle"] is True

    def test_enregistre_source_personnalisee(self, mock_st, mock_service):
        """Teste une source personnalisée"""
        from src.modules.jeux.loto.crud import enregistrer_grille

        enregistrer_grille([1, 2, 3, 4, 5], 8, source="ia", est_virtuelle=False)

        call_kwargs = mock_service.enregistrer_grille.call_args[1]
        assert call_kwargs["source"] == "ia"
        assert call_kwargs["est_virtuelle"] is False

    def test_affiche_succes_apres_enregistrement(self, mock_st, mock_service):
        """Vérifie le message de succès"""
        from src.modules.jeux.loto.crud import enregistrer_grille

        enregistrer_grille([1, 2, 3, 4, 5], 8)

        mock_st.success.assert_called()
        call_arg = mock_st.success.call_args[0][0]
        assert "1-2-3-4-5" in call_arg
        assert "N°8" in call_arg

    def test_gere_exception_db(self, mock_st, mock_service):
        """Teste la gestion d'erreur DB"""
        mock_service.enregistrer_grille.side_effect = Exception("DB Error")

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
