"""
Tests pour src/modules/maison/depenses/crud.py

Après refactoring: crud.py délègue au DepensesCrudService.
Les tests mockent get_depenses_crud_service().
"""

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest


class TestImports:
    def test_import_get_depenses_mois(self):
        from src.modules.maison.depenses.crud import get_depenses_mois

        assert callable(get_depenses_mois)

    def test_import_get_depenses_annee(self):
        from src.modules.maison.depenses.crud import get_depenses_annee

        assert callable(get_depenses_annee)

    def test_import_create_depense(self):
        from src.modules.maison.depenses.crud import create_depense

        assert callable(create_depense)

    def test_import_update_depense(self):
        from src.modules.maison.depenses.crud import update_depense

        assert callable(update_depense)

    def test_import_delete_depense(self):
        from src.modules.maison.depenses.crud import delete_depense

        assert callable(delete_depense)

    def test_import_get_stats_globales(self):
        from src.modules.maison.depenses.crud import get_stats_globales

        assert callable(get_stats_globales)

    def test_import_get_depense_by_id(self):
        from src.modules.maison.depenses.crud import get_depense_by_id

        assert callable(get_depense_by_id)

    def test_import_get_historique_categorie(self):
        from src.modules.maison.depenses.crud import get_historique_categorie

        assert callable(get_historique_categorie)


@pytest.mark.unit
class TestGetDepensesMois:
    @patch("src.modules.maison.depenses.crud.get_depenses_crud_service")
    def test_get_depenses_mois_vide(self, mock_factory):
        from src.modules.maison.depenses.crud import get_depenses_mois

        mock_svc = MagicMock()
        mock_svc.get_depenses_mois.return_value = []
        mock_factory.return_value = mock_svc
        result = get_depenses_mois(2, 2026)
        assert result == []
        mock_svc.get_depenses_mois.assert_called_once_with(2, 2026)

    @patch("src.modules.maison.depenses.crud.get_depenses_crud_service")
    def test_get_depenses_mois_avec_resultats(self, mock_factory):
        from src.modules.maison.depenses.crud import get_depenses_mois

        dep1 = MagicMock()
        dep1.montant = Decimal("100")
        mock_svc = MagicMock()
        mock_svc.get_depenses_mois.return_value = [dep1]
        mock_factory.return_value = mock_svc
        result = get_depenses_mois(2, 2026)
        assert len(result) == 1


@pytest.mark.unit
class TestGetDepensesAnnee:
    @patch("src.modules.maison.depenses.crud.get_depenses_crud_service")
    def test_get_depenses_annee_vide(self, mock_factory):
        from src.modules.maison.depenses.crud import get_depenses_annee

        mock_svc = MagicMock()
        mock_svc.get_depenses_annee.return_value = []
        mock_factory.return_value = mock_svc
        result = get_depenses_annee(2026)
        assert result == []


@pytest.mark.unit
class TestGetDepenseById:
    @patch("src.modules.maison.depenses.crud.get_depenses_crud_service")
    def test_get_depense_by_id_existe(self, mock_factory):
        from src.modules.maison.depenses.crud import get_depense_by_id

        dep = MagicMock()
        dep.id = 1
        mock_svc = MagicMock()
        mock_svc.get_depense_by_id.return_value = dep
        mock_factory.return_value = mock_svc
        result = get_depense_by_id(1)
        assert result is not None
        assert result.id == 1

    @patch("src.modules.maison.depenses.crud.get_depenses_crud_service")
    def test_get_depense_by_id_non_existe(self, mock_factory):
        from src.modules.maison.depenses.crud import get_depense_by_id

        mock_svc = MagicMock()
        mock_svc.get_depense_by_id.return_value = None
        mock_factory.return_value = mock_svc
        result = get_depense_by_id(999)
        assert result is None


@pytest.mark.unit
class TestCreateDepense:
    @patch("src.modules.maison.depenses.crud.get_depenses_crud_service")
    def test_create_depense_simple(self, mock_factory):
        from src.modules.maison.depenses.crud import create_depense

        mock_svc = MagicMock()
        mock_svc.create_depense.return_value = MagicMock()
        mock_factory.return_value = mock_svc
        data = {"categorie": "assurance", "montant": 80.00, "mois": 2, "annee": 2026}
        create_depense(data)
        mock_svc.create_depense.assert_called_once_with(data)

    @patch("src.modules.maison.depenses.crud.get_depenses_crud_service")
    def test_create_depense_energie(self, mock_factory):
        from src.modules.maison.depenses.crud import create_depense

        mock_svc = MagicMock()
        mock_svc.create_depense.return_value = MagicMock()
        mock_factory.return_value = mock_svc
        data = {
            "categorie": "electricite",
            "montant": 125.50,
            "consommation": 350,
            "mois": 2,
            "annee": 2026,
        }
        create_depense(data)
        mock_svc.create_depense.assert_called_once_with(data)


@pytest.mark.unit
class TestUpdateDepense:
    @patch("src.modules.maison.depenses.crud.get_depenses_crud_service")
    def test_update_depense_existe(self, mock_factory):
        from src.modules.maison.depenses.crud import update_depense

        dep = MagicMock()
        dep.id = 1
        dep.montant = Decimal("200")
        mock_svc = MagicMock()
        mock_svc.update_depense.return_value = dep
        mock_factory.return_value = mock_svc
        result = update_depense(1, {"montant": 200.0})
        mock_svc.update_depense.assert_called_once_with(1, {"montant": 200.0})
        assert result is not None


@pytest.mark.unit
class TestDeleteDepense:
    @patch("src.modules.maison.depenses.crud.get_depenses_crud_service")
    def test_delete_depense_existe(self, mock_factory):
        from src.modules.maison.depenses.crud import delete_depense

        mock_svc = MagicMock()
        mock_svc.delete_depense.return_value = True
        mock_factory.return_value = mock_svc
        result = delete_depense(1)
        assert result is True
        mock_svc.delete_depense.assert_called_once_with(1)


@pytest.mark.unit
class TestGetStatsGlobales:
    @patch("src.modules.maison.depenses.crud.get_depenses_crud_service")
    def test_get_stats_globales_sans_depenses(self, mock_factory):
        from src.modules.maison.depenses.crud import get_stats_globales

        mock_svc = MagicMock()
        mock_svc.get_stats_globales.return_value = {
            "total_mois": 0,
            "total_prec": 0,
            "delta": 0,
            "delta_pct": 0,
            "moyenne_mensuelle": 0,
            "nb_categories": 0,
        }
        mock_factory.return_value = mock_svc
        result = get_stats_globales()
        assert "total_mois" in result
        assert result["total_mois"] == 0

    @patch("src.modules.maison.depenses.crud.get_depenses_crud_service")
    def test_get_stats_globales_avec_depenses(self, mock_factory):
        from src.modules.maison.depenses.crud import get_stats_globales

        mock_svc = MagicMock()
        mock_svc.get_stats_globales.return_value = {
            "total_mois": 300,
            "total_prec": 250,
            "delta": 50,
            "delta_pct": 20.0,
            "moyenne_mensuelle": 275,
            "nb_categories": 2,
        }
        mock_factory.return_value = mock_svc
        result = get_stats_globales()
        assert result["total_mois"] == 300
