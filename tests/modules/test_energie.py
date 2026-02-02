"""
Tests pour le Dashboard Énergie.
"""

import pytest
from datetime import date
from unittest.mock import patch, MagicMock

from src.domains.maison.ui.energie import (
    ENERGIES,
    MOIS_FR,
    charger_historique_energie,
    get_stats_energie,
)


class TestConstantes:
    """Tests des constantes."""
    
    def test_energies_definies(self):
        """Vérifie que les énergies sont définies."""
        assert len(ENERGIES) >= 3
        assert "electricite" in ENERGIES
        assert "gaz" in ENERGIES
        assert "eau" in ENERGIES
    
    def test_energie_structure(self):
        """Vérifie la structure de chaque énergie."""
        for energie, info in ENERGIES.items():
            assert "emoji" in info
            assert "couleur" in info
            assert "unite" in info
            assert "label" in info
            assert "prix_moyen" in info
    
    def test_mois_francais(self):
        """Vérifie les mois en français."""
        assert len(MOIS_FR) == 13  # Index 0 vide + 12 mois
        assert MOIS_FR[1] == "Jan"
        assert MOIS_FR[12] == "Déc"


class TestChargementHistorique:
    """Tests du chargement d'historique."""
    
    @patch("src.domains.maison.ui.energie.get_db_context")
    def test_charger_historique_vide(self, mock_db):
        """Test avec historique vide."""
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_db.return_value.__enter__.return_value = mock_session
        
        # Clear le cache pour ce test
        charger_historique_energie.clear()
        
        historique = charger_historique_energie("electricite", nb_mois=3)
        
        assert len(historique) == 3
        for h in historique:
            assert "mois" in h
            assert "annee" in h
            assert "montant" in h
    
    @patch("src.domains.maison.ui.energie.get_db_context")
    def test_charger_historique_avec_donnees(self, mock_db):
        """Test avec données."""
        mock_depense = MagicMock()
        mock_depense.montant = 150.0
        mock_depense.consommation = 200.0
        
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_depense
        mock_db.return_value.__enter__.return_value = mock_session
        
        charger_historique_energie.clear()
        
        historique = charger_historique_energie("gaz", nb_mois=2)
        
        assert len(historique) == 2
        assert historique[-1]["montant"] == 150.0


class TestStatsEnergie:
    """Tests des statistiques énergie."""
    
    @patch("src.domains.maison.ui.energie.charger_historique_energie")
    def test_stats_energie_basique(self, mock_historique):
        """Test calcul stats basique."""
        mock_historique.return_value = [
            {"mois": 1, "annee": 2026, "montant": 100, "consommation": 50, "label": "Jan 2026"},
            {"mois": 2, "annee": 2026, "montant": 120, "consommation": 60, "label": "Fév 2026"},
        ]
        
        stats = get_stats_energie("electricite")
        
        assert "total_annuel" in stats
        assert "moyenne_mensuelle" in stats
        assert "prix_unitaire" in stats
        assert stats["total_annuel"] == 220
    
    @patch("src.domains.maison.ui.energie.charger_historique_energie")
    def test_stats_vide(self, mock_historique):
        """Test stats avec données vides."""
        mock_historique.return_value = [
            {"mois": 1, "annee": 2026, "montant": None, "consommation": None, "label": "Jan 2026"},
        ]
        
        stats = get_stats_energie("eau")
        
        assert stats["total_annuel"] == 0
        assert stats["moyenne_mensuelle"] == 0


class TestPrixUnitaire:
    """Tests du prix unitaire."""
    
    def test_prix_moyen_defaut(self):
        """Vérifie les prix moyens par défaut."""
        assert ENERGIES["electricite"]["prix_moyen"] > 0
        assert ENERGIES["gaz"]["prix_moyen"] > 0
        assert ENERGIES["eau"]["prix_moyen"] > 0
    
    def test_prix_eau_plus_cher(self):
        """L'eau au m³ est plus chère que le gaz."""
        assert ENERGIES["eau"]["prix_moyen"] > ENERGIES["gaz"]["prix_moyen"]


class TestUnites:
    """Tests des unités."""
    
    def test_unite_electricite(self):
        """L'électricité est en kWh."""
        assert ENERGIES["electricite"]["unite"] == "kWh"
    
    def test_unite_gaz(self):
        """Le gaz est en m³."""
        assert ENERGIES["gaz"]["unite"] == "m³"
    
    def test_unite_eau(self):
        """L'eau est en m³."""
        assert ENERGIES["eau"]["unite"] == "m³"
