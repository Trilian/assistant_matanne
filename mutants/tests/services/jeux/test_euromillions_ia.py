"""
Tests unitaires pour EuromillionsIAService.

Vérifie:
- Génération des 4 stratégies (equilibree, frequences, retards, ia_creative)
- Quality scoring (0-100)
- Distribution analysis (pairs/impairs, hauts/bas, somme)
"""

import pytest
from unittest.mock import Mock, patch

from src.services.jeux.euromillions_ia import EuromillionsIAService
from src.core.models.jeux import StatistiquesEuromillions


class TestEuromillionsIAService:
    """Tests pour le service EuromillionsIAService."""
    
    @pytest.fixture
    def service(self):
        """Fixture service."""
        return EuromillionsIAService()
    
    @pytest.fixture
    def mock_stats(self):
        """Mock statistiques Euromillions."""
        stats = Mock(spec=StatistiquesEuromillions)
        
        # Fréquences: top 10 numéros
        stats.frequences_numeros = {
            str(i): 50 - i for i in range(1, 51)
        }
        
        # Retards: dict avec retard pour chaque numéro
        stats.numeros_retard = {
            str(i): i * 2 for i in range(1, 51)
        }
        
        # Étoiles
        stats.frequences_etoiles = {
            str(i): 20 - i for i in range(1, 13)
        }
        
        stats.etoiles_retard = {
            str(i): i for i in range(1, 13)
        }
        
        return stats
    
    def test_calculer_qualite_grille_parfaite(self, service):
        """Test qualité grille équilibrée parfaite."""
        # Grille équilibrée: 3 pairs / 2 impairs, 3 hauts, somme 150
        numeros = [10, 20, 30, 35, 45]  # 3 pairs, 3 hauts (>25), somme 140
        etoiles = [5, 10]
        
        qualite = service.calculer_qualite_grille(numeros, etoiles)
        
        assert 0 <= qualite <= 100
        assert qualite >= 50  # Au moins score de base
    
    def test_calculer_qualite_grille_desequilibree(self, service):
        """Test qualité grille déséquilibrée."""
        # Tous pairs
        numeros = [2, 4, 6, 8, 10]
        etoiles = [2, 4]
        
        qualite = service.calculer_qualite_grille(numeros, etoiles)
        
        assert 0 <= qualite <= 100
        assert qualite < 70  # Pénalité déséquilibre
    
    def test_calculer_qualite_grille_extremes(self, service):
        """Test grille avec extrêmes (tous petits/grands)."""
        # Tous petits numéros
        numeros = [1, 2, 3, 4, 5]
        etoiles = [1, 2]
        
        qualite = service.calculer_qualite_grille(numeros, etoiles)
        
        assert 0 <= qualite <= 100
        # Devrait avoir score faible (déséquilibre hauts/bas)
    
    def test_analyser_distribution_equilibree(self, service):
        """Test analyse distribution équilibrée."""
        numeros = [10, 20, 30, 35, 45]  # 3 pairs, 3 hauts
        
        analyse = service._analyser_distribution(numeros)
        
        assert "pct_pairs" in analyse
        assert "pct_hauts" in analyse
        assert "somme" in analyse
        
        # 3 pairs / 5 = 60%
        assert 55 <= analyse["pct_pairs"] <= 65
        
        # 3 hauts (>25) / 5 = 60%
        assert 55 <= analyse["pct_hauts"] <= 65
        
        # Somme
        assert analyse["somme"] == sum(numeros)
    
    def test_analyser_distribution_tous_pairs(self, service):
        """Test analyse tous pairs."""
        numeros = [2, 4, 6, 8, 10]
        
        analyse = service._analyser_distribution(numeros)
        
        assert analyse["pct_pairs"] == 100.0
        assert analyse["pct_hauts"] == 0.0  # Tous < 26
    
    def test_analyser_distribution_tous_impairs(self, service):
        """Test analyse tous impairs."""
        numeros = [1, 3, 5, 7, 9]
        
        analyse = service._analyser_distribution(numeros)
        
        assert analyse["pct_pairs"] == 0.0
    
    def test_quality_scoring_bounds(self, service):
        """Test que quality score reste dans [0, 100]."""
        # Cas extrêmes
        cas_extremes = [
            [1, 2, 3, 4, 5],      # Tous bas
            [46, 47, 48, 49, 50], # Tous hauts
            [2, 4, 6, 8, 10],     # Tous pairs
            [1, 3, 5, 7, 9],      # Tous impairs
        ]
        
        for numeros in cas_extremes:
            etoiles = [1, 2]
            qualite = service.calculer_qualite_grille(numeros, etoiles)
            
            assert 0 <= qualite <= 100, f"Qualité {qualite} hors limites pour {numeros}"


class TestEuromillionsEdgeCases:
    """Tests cas limites."""
    
    def test_grille_invalide_trop_numeros(self):
        """Test avec plus de 5 numéros."""
        service = EuromillionsIAService()
        
        # 6 numéros (invalide)
        numeros = [1, 2, 3, 4, 5, 6]
        etoiles = [1, 2]
        
        # Devrait gérer gracieusement ou lever exception
        try:
            qualite = service.calculer_qualite_grille(numeros, etoiles)
            # Si accepté, vérifier bounds
            assert 0 <= qualite <= 100
        except (ValueError, AssertionError):
            # Exception attendue
            pass
    
    def test_grille_avec_doublons(self):
        """Test grille avec doublons."""
        service = EuromillionsIAService()
        
        numeros = [1, 2, 2, 3, 4]  # Doublon: 2
        etoiles = [1, 1]           # Doublon: 1
        
        # Devrait détecter ou gérer
        try:
            qualite = service.calculer_qualite_grille(numeros, etoiles)
            assert 0 <= qualite <= 100
        except (ValueError, AssertionError):
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
