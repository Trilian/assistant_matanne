"""Script to rewrite jeux test files for Phase 4 service refactoring."""

import pathlib

BASE = pathlib.Path(r"d:\Projet_streamlit\assistant_matanne")


def write_test_crud():
    """Rewrite tests/modules/jeux/loto/test_crud.py"""
    content = '''\
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
        """Valide qu'il faut exactement 5 num\u00e9ros"""
        from src.modules.jeux.loto.crud import ajouter_tirage

        result = ajouter_tirage(date(2025, 1, 6), [1, 2, 3, 4], 5)

        assert result is False
        mock_st.error.assert_called()

    def test_retourne_false_si_plus_de_5_numeros(self, mock_st, mock_service):
        """Valide qu'il faut exactement 5 num\u00e9ros"""
        from src.modules.jeux.loto.crud import ajouter_tirage

        result = ajouter_tirage(date(2025, 1, 6), [1, 2, 3, 4, 5, 6], 5)

        assert result is False
        mock_st.error.assert_called()

    def test_delegue_au_service_avec_bons_args(self, mock_st, mock_service):
        """V\u00e9rifie que le service est appel\u00e9 avec les bons arguments"""
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
        """V\u00e9rifie que verifier_fn est pass\u00e9e au service"""
        from src.modules.jeux.loto.crud import ajouter_tirage

        result = ajouter_tirage(date(2025, 1, 6), [1, 2, 3, 4, 5], 8)

        assert result is True
        call_kwargs = mock_service.ajouter_tirage.call_args[1]
        assert call_kwargs["verifier_fn"] is not None

    def test_affiche_succes_apres_ajout(self, mock_st, mock_service):
        """V\u00e9rifie le message de succ\u00e8s"""
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
        """Valide qu'il faut exactement 5 num\u00e9ros"""
        from src.modules.jeux.loto.crud import enregistrer_grille

        result = enregistrer_grille([1, 2, 3], 5)

        assert result is False
        mock_st.error.assert_called()

    def test_delegue_au_service_avec_bons_args(self, mock_st, mock_service):
        """V\u00e9rifie que le service est appel\u00e9 avec les bons arguments"""
        from src.modules.jeux.loto.crud import enregistrer_grille

        result = enregistrer_grille([49, 25, 7, 1, 33], 5)

        assert result is True
        mock_service.enregistrer_grille.assert_called_once()
        call_kwargs = mock_service.enregistrer_grille.call_args[1]
        assert call_kwargs["numeros"] == [49, 25, 7, 1, 33]
        assert call_kwargs["chance"] == 5

    def test_enregistre_source_et_type_par_defaut(self, mock_st, mock_service):
        """Teste les valeurs par d\u00e9faut"""
        from src.modules.jeux.loto.crud import enregistrer_grille

        enregistrer_grille([1, 2, 3, 4, 5], 8)

        call_kwargs = mock_service.enregistrer_grille.call_args[1]
        assert call_kwargs["source"] == "manuel"
        assert call_kwargs["est_virtuelle"] is True

    def test_enregistre_source_personnalisee(self, mock_st, mock_service):
        """Teste une source personnalis\u00e9e"""
        from src.modules.jeux.loto.crud import enregistrer_grille

        enregistrer_grille([1, 2, 3, 4, 5], 8, source="ia", est_virtuelle=False)

        call_kwargs = mock_service.enregistrer_grille.call_args[1]
        assert call_kwargs["source"] == "ia"
        assert call_kwargs["est_virtuelle"] is False

    def test_affiche_succes_apres_enregistrement(self, mock_st, mock_service):
        """V\u00e9rifie le message de succ\u00e8s"""
        from src.modules.jeux.loto.crud import enregistrer_grille

        enregistrer_grille([1, 2, 3, 4, 5], 8)

        mock_st.success.assert_called()
        call_arg = mock_st.success.call_args[0][0]
        assert "1-2-3-4-5" in call_arg
        assert "N\u00b08" in call_arg

    def test_gere_exception_db(self, mock_st, mock_service):
        """Teste la gestion d'erreur DB"""
        mock_service.enregistrer_grille.side_effect = Exception("DB Error")

        from src.modules.jeux.loto.crud import enregistrer_grille

        result = enregistrer_grille([1, 2, 3, 4, 5], 8)

        assert result is False
        mock_st.error.assert_called()


class TestCrudIntegration:
    """Tests d'int\u00e9gration pour le module crud"""

    def test_import_ajouter_tirage(self):
        """V\u00e9rifie que ajouter_tirage est importable"""
        from src.modules.jeux.loto.crud import ajouter_tirage

        assert callable(ajouter_tirage)

    def test_import_enregistrer_grille(self):
        """V\u00e9rifie que enregistrer_grille est importable"""
        from src.modules.jeux.loto.crud import enregistrer_grille

        assert callable(enregistrer_grille)
'''
    path = BASE / "tests" / "modules" / "jeux" / "loto" / "test_crud.py"
    path.write_text(content, encoding="utf-8")
    print(f"  OK: {path.name} ({len(content.splitlines())} lines)")


def write_test_sync():
    """Rewrite tests/modules/jeux/loto/test_sync.py"""
    content = '''\
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

    def test_retourne_zero_sans_donnees_api(
        self, mock_service, mock_charger_tirages, mock_logger
    ):
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
        """Teste l'ajout d'un tirage avec date au format fran\u00e7ais"""
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

    def test_ajoute_tirage_avec_date_objet(
        self, mock_service, mock_charger_tirages, mock_logger
    ):
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
        """Teste que les tirages existants sont g\u00e9r\u00e9s par le service"""
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
        """Teste que les tirages invalides sont g\u00e9r\u00e9s par le service"""
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
        """Teste que les tirages sans num\u00e9ro chance sont g\u00e9r\u00e9s par le service"""
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
        """Teste que les tirages avec date invalide sont g\u00e9r\u00e9s par le service"""
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

    def test_donnees_brutes_passees_au_service(self, mock_service, mock_charger_tirages, mock_logger):
        """Teste que les donn\u00e9es brutes sont pass\u00e9es au service"""
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
        """Teste avec plusieurs tirages (g\u00e9r\u00e9s par le service)"""
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
        """Teste la gestion d'exception g\u00e9n\u00e9rale"""
        mock_charger_tirages.side_effect = Exception("API Error")

        from src.modules.jeux.loto.sync import sync_tirages_loto

        result = sync_tirages_loto(limite=10)

        assert result == 0
        mock_logger.error.assert_called()

    def test_limite_par_defaut(self, mock_service, mock_charger_tirages, mock_logger):
        """Teste la limite par d\u00e9faut de 50"""
        mock_charger_tirages.return_value = []

        from src.modules.jeux.loto.sync import sync_tirages_loto

        sync_tirages_loto()

        mock_charger_tirages.assert_called_once_with(limite=50)

    def test_limite_personnalisee(self, mock_service, mock_charger_tirages, mock_logger):
        """Teste une limite personnalis\u00e9e"""
        mock_charger_tirages.return_value = []

        from src.modules.jeux.loto.sync import sync_tirages_loto

        sync_tirages_loto(limite=25)

        mock_charger_tirages.assert_called_once_with(limite=25)

    def test_tirage_avec_plus_de_5_numeros(
        self, mock_service, mock_charger_tirages, mock_logger
    ):
        """Teste que les donn\u00e9es brutes sont pass\u00e9es au service"""
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
    """Tests d'int\u00e9gration pour sync_tirages_loto"""

    def test_import_module(self):
        """V\u00e9rifie que le module s'importe correctement"""
        from src.modules.jeux.loto.sync import sync_tirages_loto

        assert callable(sync_tirages_loto)

    def test_signature_fonction(self):
        """V\u00e9rifie la signature de la fonction"""
        import inspect

        from src.modules.jeux.loto.sync import sync_tirages_loto

        sig = inspect.signature(sync_tirages_loto)
        params = list(sig.parameters.keys())
        assert "limite" in params

    def test_valeur_defaut_limite(self):
        """V\u00e9rifie la valeur par d\u00e9faut du param\u00e8tre limite"""
        import inspect

        from src.modules.jeux.loto.sync import sync_tirages_loto

        sig = inspect.signature(sync_tirages_loto)
        assert sig.parameters["limite"].default == 50
'''
    path = BASE / "tests" / "modules" / "jeux" / "loto" / "test_sync.py"
    path.write_text(content, encoding="utf-8")
    print(f"  OK: {path.name} ({len(content.splitlines())} lines)")


def write_test_paris_utils():
    """Rewrite tests/modules/jeux/paris/test_utils.py"""
    content = '''\
"""
Tests pour src/modules/jeux/paris/utils.py

Tests des fonctions utilitaires pour le module paris sportifs.
"""

from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

# ============================================================
# Fixtures (dicts retourn\u00e9s par les services)
# ============================================================


@pytest.fixture
def equipe_dict():
    """Fixture pour une \u00e9quipe en dict (tel que retourn\u00e9 par le service)"""
    return {
        "id": 1,
        "nom": "Paris Saint-Germain",
        "championnat": "Ligue 1",
        "matchs_joues": 20,
        "victoires": 15,
        "nuls": 3,
        "defaites": 2,
        "buts_marques": 45,
        "buts_encaisses": 12,
        "points": 48,
    }


@pytest.fixture
def equipe_minimale_dict():
    """Fixture pour une \u00e9quipe avec valeurs z\u00e9ro"""
    return {
        "id": 2,
        "nom": "Nouveau Club",
        "championnat": "Ligue 1",
        "matchs_joues": 0,
        "victoires": 0,
        "nuls": 0,
        "defaites": 0,
        "buts_marques": 0,
        "buts_encaisses": 0,
        "points": 0,
    }


@pytest.fixture
def match_a_venir_dict():
    """Fixture pour un match \u00e0 venir en dict"""
    return {
        "id": 100,
        "date_match": str(date.today() + timedelta(days=3)),
        "heure": "20:00",
        "championnat": "Ligue 1",
        "equipe_domicile_id": 1,
        "equipe_exterieur_id": 2,
        "dom_nom": "PSG",
        "ext_nom": "OM",
        "cote_dom": 1.5,
        "cote_nul": 4.0,
        "cote_ext": 6.0,
        "joue": False,
    }


@pytest.fixture
def match_joue_dict():
    """Fixture pour un match jou\u00e9 en dict"""
    return {
        "id": 50,
        "date_match": str(date.today() - timedelta(days=5)),
        "equipe_domicile_id": 1,
        "equipe_exterieur_id": 2,
        "score_domicile": 2,
        "score_exterieur": 1,
        "joue": True,
    }


@pytest.fixture
def pari_dict():
    """Fixture pour un pari sportif en dict"""
    return {
        "id": 200,
        "match_id": 100,
        "type_pari": "1X2",
        "prediction": "1",
        "cote": 1.8,
        "mise": 10.0,
        "statut": "en_attente",
        "gain": None,
        "est_virtuel": True,
        "cree_le": str(datetime.now()),
    }


# ============================================================
# Tests charger_championnats_disponibles
# ============================================================


class TestChargerChampionnatsDisponibles:
    """Tests pour charger_championnats_disponibles"""

    def test_retourne_liste_championnats(self):
        """V\u00e9rifie que la fonction retourne la liste des championnats"""
        from src.modules.jeux.paris.utils import charger_championnats_disponibles

        result = charger_championnats_disponibles()

        assert isinstance(result, list)
        assert len(result) > 0
        assert "Ligue 1" in result

    def test_contient_championnats_majeurs(self):
        """V\u00e9rifie que les 5 grands championnats sont pr\u00e9sents"""
        from src.modules.jeux.paris.utils import charger_championnats_disponibles

        result = charger_championnats_disponibles()

        expected = ["Ligue 1", "Premier League", "La Liga", "Serie A", "Bundesliga"]
        for champ in expected:
            assert champ in result


# ============================================================
# Tests charger_equipes
# ============================================================


class TestChargerEquipes:
    """Tests pour charger_equipes"""

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.get_paris_crud_service")
    def test_charge_toutes_equipes(self, mock_factory, mock_st, equipe_dict):
        """Test chargement de toutes les \u00e9quipes sans filtre"""
        mock_factory.return_value.charger_equipes.return_value = [equipe_dict]

        from src.modules.jeux.paris.utils import charger_equipes

        result = charger_equipes()

        assert len(result) == 1
        assert result[0]["nom"] == "Paris Saint-Germain"
        assert result[0]["points"] == 48

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.get_paris_crud_service")
    def test_charge_equipes_avec_filtre_championnat(self, mock_factory, mock_st, equipe_dict):
        """Test chargement des \u00e9quipes filtr\u00e9es par championnat"""
        mock_factory.return_value.charger_equipes.return_value = [equipe_dict]

        from src.modules.jeux.paris.utils import charger_equipes

        result = charger_equipes(championnat="Ligue 1")

        assert len(result) == 1
        mock_factory.return_value.charger_equipes.assert_called_once_with("Ligue 1")

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.get_paris_crud_service")
    def test_equipe_avec_valeurs_none(self, mock_factory, mock_st, equipe_minimale_dict):
        """Test gestion des \u00e9quipes avec statistiques z\u00e9ro"""
        mock_factory.return_value.charger_equipes.return_value = [equipe_minimale_dict]

        from src.modules.jeux.paris.utils import charger_equipes

        result = charger_equipes()

        assert len(result) == 1
        assert result[0]["matchs_joues"] == 0
        assert result[0]["victoires"] == 0
        assert result[0]["points"] == 0

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.get_paris_crud_service")
    def test_erreur_retourne_liste_vide(self, mock_factory, mock_st):
        """Test que les erreurs retournent une liste vide"""
        mock_factory.side_effect = Exception("DB error")

        from src.modules.jeux.paris.utils import charger_equipes

        result = charger_equipes()

        assert result == []
        mock_st.error.assert_called_once()


# ============================================================
# Tests charger_matchs_a_venir
# ============================================================


class TestChargerMatchsAVenir:
    """Tests pour charger_matchs_a_venir"""

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.get_paris_crud_service")
    def test_charge_matchs_prochains_7_jours(self, mock_factory, mock_st, match_a_venir_dict):
        """Test chargement des matchs des 7 prochains jours"""
        mock_factory.return_value.charger_matchs_a_venir.return_value = [match_a_venir_dict]

        from src.modules.jeux.paris.utils import charger_matchs_a_venir

        result = charger_matchs_a_venir()

        assert len(result) == 1
        assert result[0]["dom_nom"] == "PSG"
        assert result[0]["ext_nom"] == "OM"
        assert result[0]["cote_dom"] == 1.5

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.get_paris_crud_service")
    def test_charge_matchs_avec_filtre_championnat(self, mock_factory, mock_st, match_a_venir_dict):
        """Test chargement des matchs filtr\u00e9s par championnat"""
        mock_factory.return_value.charger_matchs_a_venir.return_value = [match_a_venir_dict]

        from src.modules.jeux.paris.utils import charger_matchs_a_venir

        result = charger_matchs_a_venir(jours=14, championnat="Ligue 1")

        assert len(result) == 1
        mock_factory.return_value.charger_matchs_a_venir.assert_called_once_with(14, "Ligue 1")

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.get_paris_crud_service")
    def test_match_sans_equipes(self, mock_factory, mock_st):
        """Test match avec \u00e9quipes inconnues"""
        match_dict = {
            "id": 100,
            "date_match": str(date.today() + timedelta(days=1)),
            "heure": None,
            "championnat": "Ligue 1",
            "equipe_domicile_id": 1,
            "equipe_exterieur_id": 2,
            "dom_nom": "?",
            "ext_nom": "?",
            "cote_dom": None,
            "cote_nul": None,
            "cote_ext": None,
            "joue": False,
        }
        mock_factory.return_value.charger_matchs_a_venir.return_value = [match_dict]

        from src.modules.jeux.paris.utils import charger_matchs_a_venir

        result = charger_matchs_a_venir()

        assert result[0]["dom_nom"] == "?"
        assert result[0]["ext_nom"] == "?"

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.get_paris_crud_service")
    def test_erreur_retourne_liste_vide(self, mock_factory, mock_st):
        """Test que les erreurs retournent une liste vide"""
        mock_factory.side_effect = Exception("DB error")

        from src.modules.jeux.paris.utils import charger_matchs_a_venir

        result = charger_matchs_a_venir()

        assert result == []
        mock_st.error.assert_called_once()


# ============================================================
# Tests charger_matchs_recents
# ============================================================


class TestChargerMatchsRecents:
    """Tests pour charger_matchs_recents"""

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.get_paris_crud_service")
    def test_charge_matchs_recents_equipe(self, mock_factory, mock_st, match_joue_dict):
        """Test chargement des matchs r\u00e9cents d'une \u00e9quipe"""
        mock_factory.return_value.charger_matchs_recents.return_value = [match_joue_dict]

        from src.modules.jeux.paris.utils import charger_matchs_recents

        result = charger_matchs_recents(equipe_id=1)

        assert len(result) == 1
        assert result[0]["score_domicile"] == 2
        assert result[0]["score_exterieur"] == 1

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.get_paris_crud_service")
    def test_charge_matchs_avec_limite_personnalisee(self, mock_factory, mock_st, match_joue_dict):
        """Test chargement avec nombre de matchs personnalis\u00e9"""
        mock_factory.return_value.charger_matchs_recents.return_value = [match_joue_dict]

        from src.modules.jeux.paris.utils import charger_matchs_recents

        result = charger_matchs_recents(equipe_id=1, nb_matchs=5)

        assert len(result) == 1
        mock_factory.return_value.charger_matchs_recents.assert_called_once_with(1, 5)

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.get_paris_crud_service")
    def test_erreur_retourne_liste_vide(self, mock_factory, mock_st):
        """Test que les erreurs retournent une liste vide"""
        mock_factory.side_effect = Exception("DB error")

        from src.modules.jeux.paris.utils import charger_matchs_recents

        result = charger_matchs_recents(equipe_id=1)

        assert result == []
        mock_st.error.assert_called_once()


# ============================================================
# Tests charger_paris_utilisateur
# ============================================================


class TestChargerParisUtilisateur:
    """Tests pour charger_paris_utilisateur"""

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.get_paris_crud_service")
    def test_charge_tous_paris(self, mock_factory, mock_st, pari_dict):
        """Test chargement de tous les paris sans filtre"""
        mock_factory.return_value.charger_paris_utilisateur.return_value = [pari_dict]

        from src.modules.jeux.paris.utils import charger_paris_utilisateur

        result = charger_paris_utilisateur()

        assert len(result) == 1
        assert result[0]["type_pari"] == "1X2"
        assert result[0]["mise"] == 10.0
        assert result[0]["est_virtuel"] is True

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.get_paris_crud_service")
    def test_charge_paris_par_statut(self, mock_factory, mock_st, pari_dict):
        """Test chargement des paris filtr\u00e9s par statut"""
        mock_factory.return_value.charger_paris_utilisateur.return_value = [pari_dict]

        from src.modules.jeux.paris.utils import charger_paris_utilisateur

        result = charger_paris_utilisateur(statut="gagne")

        assert len(result) == 1
        mock_factory.return_value.charger_paris_utilisateur.assert_called_once_with("gagne")

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.get_paris_crud_service")
    def test_erreur_retourne_liste_vide(self, mock_factory, mock_st):
        """Test que les erreurs retournent une liste vide"""
        mock_factory.side_effect = Exception("DB error")

        from src.modules.jeux.paris.utils import charger_paris_utilisateur

        result = charger_paris_utilisateur()

        assert result == []
        mock_st.error.assert_called_once()

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.get_paris_crud_service")
    def test_paris_liste_vide(self, mock_factory, mock_st):
        """Test quand aucun pari n'existe"""
        mock_factory.return_value.charger_paris_utilisateur.return_value = []

        from src.modules.jeux.paris.utils import charger_paris_utilisateur

        result = charger_paris_utilisateur()

        assert result == []
'''
    path = BASE / "tests" / "modules" / "jeux" / "paris" / "test_utils.py"
    path.write_text(content, encoding="utf-8")
    print(f"  OK: {path.name} ({len(content.splitlines())} lines)")


def write_test_jeux_utils():
    """Rewrite tests/modules/jeux/test_utils.py"""
    content = '''\
"""
Tests pour src/modules/jeux/utils.py

Tests des fonctions utilitaires avec fallback API/BD pour le module jeux.
"""

import sys
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pytest

# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def mock_match_api():
    """Fixture pour un match depuis l'API"""
    return {
        "id": 1,
        "date": "2026-02-15",
        "heure": "21:00",
        "championnat": "Ligue 1",
        "dom_nom": "PSG",
        "ext_nom": "Lyon",
        "cote_dom": 1.5,
        "cote_nul": 4.0,
        "cote_ext": 6.0,
        "source": "API",
    }


@pytest.fixture
def match_bd_dict():
    """Fixture pour un match depuis la BD (dict retourn\u00e9 par le service)"""
    return {
        "id": 2,
        "date_match": str(date.today() + timedelta(days=2)),
        "heure": "20:00",
        "championnat": "Ligue 1",
        "dom_nom": "Marseille",
        "ext_nom": "Monaco",
        "cote_dom": 2.0,
        "cote_nul": 3.2,
        "cote_ext": 3.5,
        "joue": False,
    }


@pytest.fixture
def equipe_bd_dict():
    """Fixture pour une \u00e9quipe depuis la BD (dict retourn\u00e9 par le service)"""
    return {
        "nom": "PSG",
        "matchs_joues": 25,
        "victoires": 18,
        "nuls": 4,
        "defaites": 3,
        "buts_marques": 55,
        "buts_encaisses": 20,
        "points": 58,
    }


@pytest.fixture
def historique_bd_dict():
    """Fixture pour un match historique depuis la BD (dict retourn\u00e9 par le service)"""
    return {
        "date_match": str(date.today() - timedelta(days=5)),
        "equipe_domicile": "PSG",
        "equipe_exterieur": "Lille",
        "score_domicile": 3,
        "score_exterieur": 0,
    }


@pytest.fixture
def tirage_bd_dict():
    """Fixture pour un tirage Loto depuis la BD (dict retourn\u00e9 par le service)"""
    return {
        "date": str(date.today() - timedelta(days=1)),
        "numeros": [5, 12, 23, 34, 45],
        "numero_chance": 7,
    }


@pytest.fixture
def stat_bd_dict():
    """Fixture pour des statistiques Loto depuis la BD (dict retourn\u00e9 par le service)"""
    return {"num_5": 45, "num_12": 38, "num_23": 42}


# ============================================================
# Tests charger_matchs_avec_fallback
# ============================================================


class TestChargerMatchsAvecFallback:
    """Tests pour charger_matchs_avec_fallback"""

    def test_charge_depuis_api_success(self, mock_match_api):
        """Test chargement r\u00e9ussi depuis l'API"""
        mock_services_jeux = MagicMock()
        mock_services_jeux.charger_matchs_a_venir.return_value = [mock_match_api]

        with patch.dict(sys.modules, {"src.services.jeux": mock_services_jeux}):
            from src.modules.jeux.utils import charger_matchs_avec_fallback

            result, source = charger_matchs_avec_fallback.__wrapped__(
                "Ligue 1", jours=7, prefer_api=True
            )

            assert source == "API"
            assert len(result) == 1
            assert result[0]["dom_nom"] == "PSG"

    def test_fallback_bd_quand_prefer_api_false(self, match_bd_dict):
        """Test fallback vers BD quand prefer_api=False"""
        mock_services_jeux = MagicMock()
        mock_services_jeux.get_paris_crud_service.return_value.charger_matchs_fallback.return_value = [match_bd_dict]

        with patch.dict(sys.modules, {"src.services.jeux": mock_services_jeux}):
            from src.modules.jeux.utils import charger_matchs_avec_fallback

            result, source = charger_matchs_avec_fallback.__wrapped__(
                "Ligue 1", jours=7, prefer_api=False
            )

            assert isinstance(result, list)
            assert source == "BD"
            assert len(result) == 1

    def test_api_echoue_fallback_bd(self, match_bd_dict):
        """Test que l'erreur API d\u00e9clenche le fallback BD"""
        mock_services_jeux = MagicMock()
        mock_services_jeux.charger_matchs_a_venir.side_effect = Exception("API error")
        mock_services_jeux.get_paris_crud_service.return_value.charger_matchs_fallback.return_value = [match_bd_dict]

        with patch.dict(sys.modules, {"src.services.jeux": mock_services_jeux}):
            from src.modules.jeux.utils import charger_matchs_avec_fallback

            result, source = charger_matchs_avec_fallback.__wrapped__(
                "Ligue 1", jours=7, prefer_api=True
            )

            assert isinstance(result, list)
            assert source == "BD"

    def test_tout_echoue_retourne_liste_vide(self):
        """Test que la fonction retourne liste vide si tout \u00e9choue"""
        mock_services_jeux = MagicMock()
        mock_services_jeux.charger_matchs_a_venir.side_effect = Exception("API error")
        mock_services_jeux.get_paris_crud_service.side_effect = Exception("DB error")

        with patch.dict(sys.modules, {"src.services.jeux": mock_services_jeux}):
            from src.modules.jeux.utils import charger_matchs_avec_fallback

            result, source = charger_matchs_avec_fallback.__wrapped__(
                "Ligue 1", jours=7, prefer_api=True
            )

            assert result == []

    def test_api_retourne_vide_resultat_vide(self, mock_match_api):
        """Test que la fonction g\u00e8re les r\u00e9sultats vides gracieusement"""
        mock_services_jeux = MagicMock()
        mock_services_jeux.charger_matchs_a_venir.return_value = []

        with patch.dict(sys.modules, {"src.services.jeux": mock_services_jeux}):
            from src.modules.jeux.utils import charger_matchs_avec_fallback

            result, source = charger_matchs_avec_fallback.__wrapped__(
                "Ligue 1", jours=7, prefer_api=True
            )

            assert isinstance(result, list)


# ============================================================
# Tests charger_classement_avec_fallback
# ============================================================


class TestChargerClassementAvecFallback:
    """Tests pour charger_classement_avec_fallback"""

    def test_charge_classement_api_success(self):
        """Test chargement du classement depuis l'API"""
        classement_api = [
            {"position": 1, "nom": "PSG", "points": 58},
            {"position": 2, "nom": "Monaco", "points": 52},
        ]

        mock_services_jeux = MagicMock()
        mock_services_jeux.charger_classement.return_value = classement_api

        with patch.dict(sys.modules, {"src.services.jeux": mock_services_jeux}):
            from src.modules.jeux.utils import charger_classement_avec_fallback

            result, source = charger_classement_avec_fallback.__wrapped__("Ligue 1")

            assert source == "API"
            assert len(result) == 2
            assert result[0]["nom"] == "PSG"

    def test_fallback_bd_classement(self, equipe_bd_dict):
        """Test fallback BD pour le classement"""
        mock_services_jeux = MagicMock()
        mock_services_jeux.charger_classement.side_effect = Exception("API error")
        mock_services_jeux.get_paris_crud_service.return_value.charger_classement_fallback.return_value = [equipe_bd_dict]

        with patch.dict(sys.modules, {"src.services.jeux": mock_services_jeux}):
            from src.modules.jeux.utils import charger_classement_avec_fallback

            result, source = charger_classement_avec_fallback.__wrapped__("Ligue 1")

            assert source == "BD"
            assert len(result) == 1
            assert result[0]["nom"] == "PSG"
            assert result[0]["points"] == 58

    def test_api_retourne_vide_fallback_bd(self, equipe_bd_dict):
        """Test fallback BD quand API retourne vide"""
        mock_services_jeux = MagicMock()
        mock_services_jeux.charger_classement.return_value = []
        mock_services_jeux.get_paris_crud_service.return_value.charger_classement_fallback.return_value = [equipe_bd_dict]

        with patch.dict(sys.modules, {"src.services.jeux": mock_services_jeux}):
            from src.modules.jeux.utils import charger_classement_avec_fallback

            result, source = charger_classement_avec_fallback.__wrapped__("Ligue 1")

            assert source == "BD"

    def test_classement_tout_echoue(self):
        """Test que la fonction g\u00e8re tout \u00e9choue"""
        mock_services_jeux = MagicMock()
        mock_services_jeux.charger_classement.side_effect = Exception("API error")
        mock_services_jeux.get_paris_crud_service.side_effect = Exception("DB error")

        with patch.dict(sys.modules, {"src.services.jeux": mock_services_jeux}):
            from src.modules.jeux.utils import charger_classement_avec_fallback

            result, source = charger_classement_avec_fallback.__wrapped__("Championnat inconnu")

            assert result == []


# ============================================================
# Tests charger_historique_equipe_avec_fallback
# ============================================================


class TestChargerHistoriqueEquipeAvecFallback:
    """Tests pour charger_historique_equipe_avec_fallback"""

    def test_charge_historique_api_success(self):
        """Test chargement de l'historique depuis l'API"""
        historique_api = [
            {
                "date": "2026-02-10",
                "equipe_domicile": "PSG",
                "equipe_exterieur": "Lille",
                "score_domicile": 3,
                "score_exterieur": 0,
            }
        ]

        mock_services_jeux = MagicMock()
        mock_services_jeux.charger_historique_equipe.return_value = historique_api

        with patch.dict(sys.modules, {"src.services.jeux": mock_services_jeux}):
            from src.modules.jeux.utils import charger_historique_equipe_avec_fallback

            result, source = charger_historique_equipe_avec_fallback.__wrapped__("PSG")

            assert source == "API"
            assert len(result) == 1
            assert result[0]["score_domicile"] == 3

    def test_fallback_bd_historique(self, historique_bd_dict):
        """Test fallback BD pour l'historique"""
        mock_services_jeux = MagicMock()
        mock_services_jeux.charger_historique_equipe.side_effect = Exception("API error")
        mock_services_jeux.get_paris_crud_service.return_value.charger_historique_equipe_fallback.return_value = [historique_bd_dict]

        with patch.dict(sys.modules, {"src.services.jeux": mock_services_jeux}):
            from src.modules.jeux.utils import charger_historique_equipe_avec_fallback

            result, source = charger_historique_equipe_avec_fallback.__wrapped__("PSG")

            assert source == "BD"
            assert len(result) == 1

    def test_api_retourne_vide_fallback_bd(self, historique_bd_dict):
        """Test fallback BD quand API retourne vide"""
        mock_services_jeux = MagicMock()
        mock_services_jeux.charger_historique_equipe.return_value = []
        mock_services_jeux.get_paris_crud_service.return_value.charger_historique_equipe_fallback.return_value = [historique_bd_dict]

        with patch.dict(sys.modules, {"src.services.jeux": mock_services_jeux}):
            from src.modules.jeux.utils import charger_historique_equipe_avec_fallback

            result, source = charger_historique_equipe_avec_fallback.__wrapped__("PSG")

            assert source == "BD"

    def test_historique_tout_echoue(self):
        """Test historique tout \u00e9choue"""
        mock_services_jeux = MagicMock()
        mock_services_jeux.charger_historique_equipe.side_effect = Exception("API error")
        mock_services_jeux.get_paris_crud_service.side_effect = Exception("DB error")

        with patch.dict(sys.modules, {"src.services.jeux": mock_services_jeux}):
            from src.modules.jeux.utils import charger_historique_equipe_avec_fallback

            result, source = charger_historique_equipe_avec_fallback.__wrapped__("Equipe Fantome")

            assert result == []


# ============================================================
# Tests charger_tirages_loto_avec_fallback
# ============================================================


class TestChargerTiragesLotoAvecFallback:
    """Tests pour charger_tirages_loto_avec_fallback"""

    def test_charge_tirages_scraper_success(self):
        """Test chargement des tirages depuis le scraper FDJ"""
        tirages_scraper = [
            {"date": "2026-02-12", "numeros": [7, 14, 21, 35, 42], "numero_chance": 3}
        ]

        mock_scraper = MagicMock()
        mock_scraper.charger_tirages_loto.return_value = tirages_scraper

        with patch.dict(sys.modules, {"src.modules.jeux.scraper_loto": mock_scraper}):
            from src.modules.jeux.utils import charger_tirages_loto_avec_fallback

            result, source = charger_tirages_loto_avec_fallback.__wrapped__(limite=50)

            assert source == "Scraper FDJ"
            assert len(result) == 1
            assert result[0]["numeros"] == [7, 14, 21, 35, 42]

    def test_fallback_bd_tirages(self, tirage_bd_dict):
        """Test fallback BD pour les tirages"""
        mock_scraper = MagicMock()
        mock_scraper.charger_tirages_loto.side_effect = Exception("Scraper error")

        mock_services_jeux = MagicMock()
        mock_services_jeux.get_loto_crud_service.return_value.charger_tirages_fallback.return_value = [tirage_bd_dict]

        with patch.dict(
            sys.modules,
            {
                "src.modules.jeux.scraper_loto": mock_scraper,
                "src.services.jeux": mock_services_jeux,
            },
        ):
            from src.modules.jeux.utils import charger_tirages_loto_avec_fallback

            result, source = charger_tirages_loto_avec_fallback.__wrapped__(limite=10)

            assert source == "BD"
            assert len(result) == 1
            assert result[0]["numero_chance"] == 7

    def test_scraper_vide_fallback_bd(self, tirage_bd_dict):
        """Test fallback BD quand scraper retourne vide"""
        mock_scraper = MagicMock()
        mock_scraper.charger_tirages_loto.return_value = []

        mock_services_jeux = MagicMock()
        mock_services_jeux.get_loto_crud_service.return_value.charger_tirages_fallback.return_value = [tirage_bd_dict]

        with patch.dict(
            sys.modules,
            {
                "src.modules.jeux.scraper_loto": mock_scraper,
                "src.services.jeux": mock_services_jeux,
            },
        ):
            from src.modules.jeux.utils import charger_tirages_loto_avec_fallback

            result, source = charger_tirages_loto_avec_fallback.__wrapped__(limite=100)

            assert source == "BD"

    def test_tirages_tout_echoue(self):
        """Test quand tout \u00e9choue pour les tirages"""
        mock_scraper = MagicMock()
        mock_scraper.charger_tirages_loto.side_effect = Exception("Scraper error")

        mock_services_jeux = MagicMock()
        mock_services_jeux.get_loto_crud_service.side_effect = Exception("DB error")

        with patch.dict(
            sys.modules,
            {
                "src.modules.jeux.scraper_loto": mock_scraper,
                "src.services.jeux": mock_services_jeux,
            },
        ):
            from src.modules.jeux.utils import charger_tirages_loto_avec_fallback

            result, source = charger_tirages_loto_avec_fallback.__wrapped__(limite=100)

            assert result == []


# ============================================================
# Tests charger_stats_loto_avec_fallback
# ============================================================


class TestChargerStatsLotoAvecFallback:
    """Tests pour charger_stats_loto_avec_fallback"""

    def test_charge_stats_scraper_success(self):
        """Test chargement des stats depuis le scraper"""
        stats_scraper = {"frequences": {"5": 45, "12": 38}, "derniere_maj": "2026-02-12"}

        mock_scraper = MagicMock()
        mock_scraper.obtenir_statistiques_loto.return_value = stats_scraper

        with patch.dict(sys.modules, {"src.modules.jeux.scraper_loto": mock_scraper}):
            from src.modules.jeux.utils import charger_stats_loto_avec_fallback

            result, source = charger_stats_loto_avec_fallback.__wrapped__(limite=50)

            assert source == "Scraper FDJ"
            assert "frequences" in result

    def test_fallback_bd_stats(self, stat_bd_dict):
        """Test fallback BD pour les statistiques"""
        mock_scraper = MagicMock()
        mock_scraper.obtenir_statistiques_loto.side_effect = Exception("Scraper error")

        mock_services_jeux = MagicMock()
        mock_services_jeux.get_loto_crud_service.return_value.charger_stats_fallback.return_value = stat_bd_dict

        with patch.dict(
            sys.modules,
            {
                "src.modules.jeux.scraper_loto": mock_scraper,
                "src.services.jeux": mock_services_jeux,
            },
        ):
            from src.modules.jeux.utils import charger_stats_loto_avec_fallback

            result, source = charger_stats_loto_avec_fallback.__wrapped__()

            assert source == "BD"
            assert result["num_5"] == 45

    def test_scraper_vide_fallback_bd(self, stat_bd_dict):
        """Test fallback BD quand scraper retourne vide"""
        mock_scraper = MagicMock()
        mock_scraper.obtenir_statistiques_loto.return_value = {}

        mock_services_jeux = MagicMock()
        mock_services_jeux.get_loto_crud_service.return_value.charger_stats_fallback.return_value = stat_bd_dict

        with patch.dict(
            sys.modules,
            {
                "src.modules.jeux.scraper_loto": mock_scraper,
                "src.services.jeux": mock_services_jeux,
            },
        ):
            from src.modules.jeux.utils import charger_stats_loto_avec_fallback

            result, source = charger_stats_loto_avec_fallback.__wrapped__()

            assert source == "BD"

    def test_stats_tout_echoue(self):
        """Test quand aucune statistique n'est disponible"""
        mock_scraper = MagicMock()
        mock_scraper.obtenir_statistiques_loto.side_effect = Exception("Scraper error")

        mock_services_jeux = MagicMock()
        mock_services_jeux.get_loto_crud_service.side_effect = Exception("DB error")

        with patch.dict(
            sys.modules,
            {
                "src.modules.jeux.scraper_loto": mock_scraper,
                "src.services.jeux": mock_services_jeux,
            },
        ):
            from src.modules.jeux.utils import charger_stats_loto_avec_fallback

            result, source = charger_stats_loto_avec_fallback.__wrapped__()

            assert result == {}


# ============================================================
# Tests bouton_actualiser_api
# ============================================================


class TestBoutonActualiserApi:
    """Tests pour bouton_actualiser_api"""

    @patch("src.modules.jeux.utils.st")
    def test_bouton_non_clique(self, mock_st):
        """Test quand le bouton n'est pas cliqu\u00e9"""
        mock_st.button.return_value = False
        mock_st.session_state = {}

        from src.modules.jeux.utils import bouton_actualiser_api

        result = bouton_actualiser_api("matchs_test")

        assert result is False
        mock_st.button.assert_called_once()

    @patch("src.modules.jeux.utils.st")
    def test_bouton_clique_nettoie_cache(self, mock_st):
        """Test que le clic nettoie le cache et retourne True"""
        mock_st.button.return_value = True
        mock_st.session_state = {}
        mock_st.cache_data = MagicMock()

        from src.modules.jeux.utils import bouton_actualiser_api

        result = bouton_actualiser_api("test_key")

        assert result is True
        mock_st.cache_data.clear.assert_called_once()
        assert mock_st.session_state["test_key_updated"] is True


# ============================================================
# Tests message_source_donnees
# ============================================================


class TestMessageSourceDonnees:
    """Tests pour message_source_donnees"""

    @patch("src.modules.jeux.utils.st")
    def test_affiche_source_api(self, mock_st):
        """Test affichage pour source API"""
        from src.modules.jeux.utils import message_source_donnees

        message_source_donnees("API")

        mock_st.caption.assert_called_once()
        call_args = mock_st.caption.call_args[0][0]
        assert "\\U0001f310" in call_args
        assert "API" in call_args

    @patch("src.modules.jeux.utils.st")
    def test_affiche_source_bd(self, mock_st):
        """Test affichage pour source BD"""
        from src.modules.jeux.utils import message_source_donnees

        message_source_donnees("BD")

        call_args = mock_st.caption.call_args[0][0]
        assert "\\U0001f4be" in call_args
        assert "BD" in call_args

    @patch("src.modules.jeux.utils.st")
    def test_affiche_source_scraper(self, mock_st):
        """Test affichage pour source Scraper"""
        from src.modules.jeux.utils import message_source_donnees

        message_source_donnees("Scraper FDJ")

        call_args = mock_st.caption.call_args[0][0]
        assert "\\U0001f577\\ufe0f" in call_args
        assert "Scraper FDJ" in call_args

    @patch("src.modules.jeux.utils.st")
    def test_affiche_source_inconnue(self, mock_st):
        """Test affichage pour source inconnue"""
        from src.modules.jeux.utils import message_source_donnees

        message_source_donnees("Autre")

        call_args = mock_st.caption.call_args[0][0]
        assert "\\U0001f577\\ufe0f" in call_args
'''
    path = BASE / "tests" / "modules" / "jeux" / "test_utils.py"
    path.write_text(content, encoding="utf-8")
    print(f"  OK: {path.name} ({len(content.splitlines())} lines)")


if __name__ == "__main__":
    print("Writing test files for Phase 4 (jeux)...")
    write_test_crud()
    write_test_sync()
    write_test_paris_utils()
    write_test_jeux_utils()
    print("Done!")
