"""
Tests pour src/modules/maison/hub/data.py

Apr\u00e8s refactoring: hub/data.py d\u00e9l\u00e8gue au HubDataService.
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
        """Test stats avec donn\u00e9es."""
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
        """Test gestion exception base de donn\u00e9es."""
        mock_factory.side_effect = Exception("DB Error")

        from src.modules.maison.hub.data import obtenir_stats_globales

        stats = obtenir_stats_globales()

        # Doit retourner des valeurs par d\u00e9faut sans crash
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
        """Test structure d'une t\u00e2che."""
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
        # Doit contenir au moins l'alerte objets urgents
        assert len(alertes) >= 1

    @patch("src.modules.maison.hub.data.get_hub_data_service")
    def test_alertes_structure(self, mock_factory):
        """Test structure d'une alerte."""
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
        """Test charge l\u00e9g\u00e8re (<50%)."""
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
        """Test charge \u00e9lev\u00e9e (>80%)."""
        from src.modules.maison.hub.data import calculer_charge

        taches = [{"duree_min": 60}, {"duree_min": 60}, {"duree_min": 30}]  # 150min
        result = calculer_charge(taches)

        assert result["niveau"] == "eleve"
        assert result["pourcent"] == 100  # Plafonn\u00e9

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
