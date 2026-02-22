"""Script to rewrite test files for Phase 5 refactoring."""

import os

BASE = r"d:\Projet_streamlit\assistant_matanne"

# ═══════════════════════════════════════════════════
# 1. tests/modules/maison/depenses/test_crud.py
# ═══════════════════════════════════════════════════
test_crud = '''\
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
'''

# ═══════════════════════════════════════════════════
# 2. tests/modules/maison/test_hub_data.py
# ═══════════════════════════════════════════════════
test_hub_data = '''\
"""
Tests pour src/modules/maison/hub/data.py

Apr\\u00e8s refactoring: hub/data.py d\\u00e9l\\u00e8gue au HubDataService.
Les tests mockent get_hub_data_service().
"""

from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pytest


class TestObteniStats:
    """Tests pour obtenir_stats_globales"""

    @patch("src.modules.maison.hub.data.get_hub_data_service")
    def test_stats_sans_donnees(self, mock_factory):
        """Test stats avec base vide."""
        mock_svc = MagicMock()
        mock_svc.obtenir_stats_db.return_value = {
            "zones_jardin": 0,
            "pieces": 0,
            "objets_a_changer": 0,
            "temps_mois_heures": 0,
        }
        mock_factory.return_value = mock_svc

        from src.modules.maison.hub.data import obtenir_stats_globales

        stats = obtenir_stats_globales()

        assert stats["zones_jardin"] == 0
        assert stats["pieces"] == 0
        assert stats["objets_a_changer"] == 0

    @patch("src.modules.maison.hub.data.get_hub_data_service")
    def test_stats_avec_donnees(self, mock_factory):
        """Test stats avec donn\\u00e9es."""
        mock_svc = MagicMock()
        mock_svc.obtenir_stats_db.return_value = {
            "zones_jardin": 3,
            "pieces": 6,
            "objets_a_changer": 2,
            "temps_mois_heures": 5.5,
        }
        mock_factory.return_value = mock_svc

        from src.modules.maison.hub.data import obtenir_stats_globales

        stats = obtenir_stats_globales()

        assert isinstance(stats, dict)
        assert "zones_jardin" in stats
        assert "pieces" in stats

    @patch("src.modules.maison.hub.data.get_hub_data_service")
    def test_stats_gestion_exception(self, mock_factory):
        """Test gestion exception base de donn\\u00e9es."""
        mock_factory.side_effect = Exception("DB Error")

        from src.modules.maison.hub.data import obtenir_stats_globales

        stats = obtenir_stats_globales()

        # Doit retourner des valeurs par d\\u00e9faut sans crash
        assert isinstance(stats, dict)
        assert stats["zones_jardin"] == 0


class TestObteniTachesJour:
    """Tests pour obtenir_taches_jour (mock)"""

    def test_retourne_liste(self):
        """Test retour liste de taches."""
        from src.modules.maison.hub.data import obtenir_taches_jour

        taches = obtenir_taches_jour()

        assert isinstance(taches, list)
        assert len(taches) >= 0
        if taches:
            assert "titre" in taches[0]
            assert "domaine" in taches[0]

    def test_structure_tache(self):
        """Test structure d\'une t\\u00e2che."""
        from src.modules.maison.hub.data import obtenir_taches_jour

        taches = obtenir_taches_jour()

        if taches:
            tache = taches[0]
            assert "id" in tache
            assert "titre" in tache
            assert "domaine" in tache
            assert "duree_min" in tache
            assert "priorite" in tache


class TestObteniAlertes:
    """Tests pour obtenir_alertes"""

    @patch("src.modules.maison.hub.data.get_hub_data_service")
    def test_alertes_base(self, mock_factory):
        """Test alertes de base."""
        mock_svc = MagicMock()
        mock_svc.compter_objets_urgents.return_value = 0
        mock_factory.return_value = mock_svc

        from src.modules.maison.hub.data import obtenir_alertes

        alertes = obtenir_alertes()

        assert isinstance(alertes, list)

    @patch("src.modules.maison.hub.data.get_hub_data_service")
    def test_alertes_objets_urgents(self, mock_factory):
        """Test alerte si objets urgents."""
        mock_svc = MagicMock()
        mock_svc.compter_objets_urgents.return_value = 3
        mock_factory.return_value = mock_svc

        from src.modules.maison.hub.data import obtenir_alertes

        alertes = obtenir_alertes()

        assert isinstance(alertes, list)
        # Doit contenir au moins l\'alerte objets urgents
        assert len(alertes) >= 1

    @patch("src.modules.maison.hub.data.get_hub_data_service")
    def test_alertes_structure(self, mock_factory):
        """Test structure d\'une alerte."""
        mock_svc = MagicMock()
        mock_svc.compter_objets_urgents.return_value = 0
        mock_factory.return_value = mock_svc

        from src.modules.maison.hub.data import obtenir_alertes

        alertes = obtenir_alertes()

        if alertes:
            alerte = alertes[0]
            assert "type" in alerte
            assert "icon" in alerte
            assert "titre" in alerte


class TestCalculerCharge:
    """Tests pour calculer_charge"""

    def test_charge_vide(self):
        """Test charge sans taches."""
        from src.modules.maison.hub.data import calculer_charge

        result = calculer_charge([])

        assert result["temps_min"] == 0
        assert result["pourcent"] == 0
        assert result["niveau"] == "leger"
        assert result["nb_taches"] == 0

    def test_charge_legere(self):
        """Test charge l\\u00e9g\\u00e8re (<50%)."""
        from src.modules.maison.hub.data import calculer_charge

        taches = [{"duree_min": 30}, {"duree_min": 20}]  # 50min sur 120max
        result = calculer_charge(taches)

        assert result["temps_min"] == 50
        assert result["niveau"] == "leger"
        assert result["nb_taches"] == 2

    def test_charge_normale(self):
        """Test charge normale (50-80%)."""
        from src.modules.maison.hub.data import calculer_charge

        taches = [{"duree_min": 35}, {"duree_min": 35}]  # 70min sur 120max = 58%
        result = calculer_charge(taches)

        assert result["niveau"] == "normal"

    def test_charge_elevee(self):
        """Test charge \\u00e9lev\\u00e9e (>80%)."""
        from src.modules.maison.hub.data import calculer_charge

        taches = [{"duree_min": 60}, {"duree_min": 60}, {"duree_min": 30}]  # 150min
        result = calculer_charge(taches)

        assert result["niveau"] == "eleve"
        assert result["pourcent"] == 100  # Plafonn\\u00e9

    def test_format_temps_minutes(self):
        """Test formatage < 1h."""
        from src.modules.maison.hub.data import calculer_charge

        result = calculer_charge([{"duree_min": 45}])
        assert "45 min" in result["temps_str"]

    def test_format_temps_heures(self):
        """Test formatage >= 1h."""
        from src.modules.maison.hub.data import calculer_charge

        result = calculer_charge([{"duree_min": 75}])
        assert "1h15" in result["temps_str"]
'''

# ═══════════════════════════════════════════════════
# Write files
# ═══════════════════════════════════════════════════
files = {
    os.path.join(BASE, "tests", "modules", "maison", "depenses", "test_crud.py"): test_crud,
    os.path.join(BASE, "tests", "modules", "maison", "test_hub_data.py"): test_hub_data,
}

for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"OK: {os.path.basename(path)}")

print("Done!")
