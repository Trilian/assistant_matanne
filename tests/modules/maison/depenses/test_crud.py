"""
Tests pour src/modules/maison/depenses/crud.py
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


def create_mock_session(query_result=None, first_result=None):
    session = MagicMock()
    query_chain = MagicMock()
    query_chain.filter.return_value = query_chain
    query_chain.order_by.return_value = query_chain
    query_chain.all.return_value = query_result if query_result else []
    query_chain.first.return_value = first_result
    session.query.return_value = query_chain
    return session


@pytest.mark.unit
class TestGetDepensesMois:
    @patch("src.modules.maison.depenses.crud.obtenir_contexte_db")
    def test_get_depenses_mois_vide(self, mock_db):
        from src.modules.maison.depenses.crud import get_depenses_mois

        session = create_mock_session(query_result=[])
        mock_db.return_value.__enter__ = MagicMock(return_value=session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)
        result = get_depenses_mois(2, 2026)
        assert result == []

    @patch("src.modules.maison.depenses.crud.obtenir_contexte_db")
    def test_get_depenses_mois_avec_resultats(self, mock_db):
        from src.modules.maison.depenses.crud import get_depenses_mois

        dep1 = MagicMock()
        dep1.montant = Decimal("100")
        session = create_mock_session(query_result=[dep1])
        mock_db.return_value.__enter__ = MagicMock(return_value=session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)
        result = get_depenses_mois(2, 2026)
        assert len(result) == 1


@pytest.mark.unit
class TestGetDepensesAnnee:
    @patch("src.modules.maison.depenses.crud.obtenir_contexte_db")
    def test_get_depenses_annee_vide(self, mock_db):
        from src.modules.maison.depenses.crud import get_depenses_annee

        session = create_mock_session(query_result=[])
        mock_db.return_value.__enter__ = MagicMock(return_value=session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)
        result = get_depenses_annee(2026)
        assert result == []


@pytest.mark.unit
class TestGetDepenseById:
    @patch("src.modules.maison.depenses.crud.obtenir_contexte_db")
    def test_get_depense_by_id_existe(self, mock_db):
        from src.modules.maison.depenses.crud import get_depense_by_id

        dep = MagicMock()
        dep.id = 1
        session = create_mock_session(first_result=dep)
        mock_db.return_value.__enter__ = MagicMock(return_value=session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)
        result = get_depense_by_id(1)
        assert result is not None
        assert result.id == 1

    @patch("src.modules.maison.depenses.crud.obtenir_contexte_db")
    def test_get_depense_by_id_non_existe(self, mock_db):
        from src.modules.maison.depenses.crud import get_depense_by_id

        session = create_mock_session(first_result=None)
        mock_db.return_value.__enter__ = MagicMock(return_value=session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)
        result = get_depense_by_id(999)
        assert result is None


@pytest.mark.unit
class TestCreateDepense:
    @patch("src.modules.maison.depenses.crud.obtenir_contexte_db")
    def test_create_depense_simple(self, mock_db):
        from src.modules.maison.depenses.crud import create_depense

        session = create_mock_session()
        mock_db.return_value.__enter__ = MagicMock(return_value=session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)
        create_depense({"categorie": "assurance", "montant": 80.00, "mois": 2, "annee": 2026})
        session.add.assert_called_once()
        session.commit.assert_called_once()

    @patch("src.modules.maison.depenses.crud.get_budget_service")
    @patch("src.modules.maison.depenses.crud.obtenir_contexte_db")
    def test_create_depense_energie(self, mock_db, mock_service):
        from src.modules.maison.depenses.crud import create_depense

        session = create_mock_session()
        mock_db.return_value.__enter__ = MagicMock(return_value=session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)
        mock_svc = MagicMock()
        mock_service.return_value = mock_svc
        create_depense(
            {
                "categorie": "electricite",
                "montant": 125.50,
                "consommation": 350,
                "mois": 2,
                "annee": 2026,
            }
        )
        mock_svc.ajouter_facture_maison.assert_called_once()
        session.add.assert_called_once()


@pytest.mark.unit
class TestUpdateDepense:
    @patch("src.modules.maison.depenses.crud.obtenir_contexte_db")
    def test_update_depense_existe(self, mock_db):
        from src.modules.maison.depenses.crud import update_depense

        dep = MagicMock()
        dep.id = 1
        dep.montant = Decimal("100")
        session = create_mock_session(first_result=dep)
        mock_db.return_value.__enter__ = MagicMock(return_value=session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)
        result = update_depense(1, {"montant": 200.0})
        session.commit.assert_called_once()
        assert dep.montant == 200.0


@pytest.mark.unit
class TestDeleteDepense:
    @patch("src.modules.maison.depenses.crud.obtenir_contexte_db")
    def test_delete_depense_existe(self, mock_db):
        from src.modules.maison.depenses.crud import delete_depense

        dep = MagicMock()
        dep.id = 1
        session = create_mock_session(first_result=dep)
        mock_db.return_value.__enter__ = MagicMock(return_value=session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)
        result = delete_depense(1)
        session.delete.assert_called_once_with(dep)
        session.commit.assert_called_once()
        assert result is True


@pytest.mark.unit
class TestGetStatsGlobales:
    @patch("src.modules.maison.depenses.crud.get_depenses_mois")
    def test_get_stats_globales_sans_depenses(self, mock_get):
        from src.modules.maison.depenses.crud import get_stats_globales

        mock_get.return_value = []
        result = get_stats_globales()
        assert "total_mois" in result
        assert result["total_mois"] == 0

    @patch("src.modules.maison.depenses.crud.get_depenses_mois")
    def test_get_stats_globales_avec_depenses(self, mock_get):
        from src.modules.maison.depenses.crud import get_stats_globales

        dep1 = MagicMock()
        dep1.montant = Decimal("100")
        dep1.categorie = "electricite"
        dep2 = MagicMock()
        dep2.montant = Decimal("200")
        dep2.categorie = "assurance"
        mock_get.return_value = [dep1, dep2]
        result = get_stats_globales()
        assert result["total_mois"] == 300
