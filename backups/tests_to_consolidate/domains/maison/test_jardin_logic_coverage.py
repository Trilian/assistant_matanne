"""
Tests de couverture complÃ©mentaires pour jardin_logic.py
Objectif: atteindre 80%+ de couverture
Couvre les lignes non testÃ©es: 37, 39, 41, 205, 222-235
"""
import pytest
from datetime import date
from unittest.mock import patch


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS GET_SAISON_ACTUELLE - branches manquantes
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestGetSaisonActuelle:
    """Tests pour les diffÃ©rentes saisons."""

    def test_saison_ete_juin(self):
        """Teste retour Ã‰tÃ© en juin."""
        from src.modules.maison.logic.jardin_logic import get_saison_actuelle
        
        with patch("src.modules.maison.logic.jardin_logic.date") as mock_date:
            mock_date.today.return_value = date(2026, 6, 15)
            
            result = get_saison_actuelle()
            
            assert result == "Ã‰tÃ©"

    def test_saison_ete_juillet(self):
        """Teste retour Ã‰tÃ© en juillet."""
        from src.modules.maison.logic.jardin_logic import get_saison_actuelle
        
        with patch("src.modules.maison.logic.jardin_logic.date") as mock_date:
            mock_date.today.return_value = date(2026, 7, 15)
            
            result = get_saison_actuelle()
            
            assert result == "Ã‰tÃ©"

    def test_saison_ete_aout(self):
        """Teste retour Ã‰tÃ© en aoÃ»t."""
        from src.modules.maison.logic.jardin_logic import get_saison_actuelle
        
        with patch("src.modules.maison.logic.jardin_logic.date") as mock_date:
            mock_date.today.return_value = date(2026, 8, 15)
            
            result = get_saison_actuelle()
            
            assert result == "Ã‰tÃ©"

    def test_saison_automne_septembre(self):
        """Teste retour Automne en septembre."""
        from src.modules.maison.logic.jardin_logic import get_saison_actuelle
        
        with patch("src.modules.maison.logic.jardin_logic.date") as mock_date:
            mock_date.today.return_value = date(2026, 9, 15)
            
            result = get_saison_actuelle()
            
            assert result == "Automne"

    def test_saison_automne_octobre(self):
        """Teste retour Automne en octobre."""
        from src.modules.maison.logic.jardin_logic import get_saison_actuelle
        
        with patch("src.modules.maison.logic.jardin_logic.date") as mock_date:
            mock_date.today.return_value = date(2026, 10, 15)
            
            result = get_saison_actuelle()
            
            assert result == "Automne"

    def test_saison_automne_novembre(self):
        """Teste retour Automne en novembre."""
        from src.modules.maison.logic.jardin_logic import get_saison_actuelle
        
        with patch("src.modules.maison.logic.jardin_logic.date") as mock_date:
            mock_date.today.return_value = date(2026, 11, 15)
            
            result = get_saison_actuelle()
            
            assert result == "Automne"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS FILTRER_PAR_STATUS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestFiltrerParStatus:
    """Tests pour filtrer_par_status."""

    def test_filtrer_par_status_actif(self):
        """Filtre les plantes actives."""
        from src.modules.maison.logic.jardin_logic import filtrer_par_status
        
        plantes = [
            {"nom": "Tomate", "status": "actif"},
            {"nom": "Basilic", "status": "inactif"},
            {"nom": "Courgette", "status": "actif"},
        ]
        
        result = filtrer_par_status(plantes, "actif")
        
        assert len(result) == 2
        assert all(p["status"] == "actif" for p in result)

    def test_filtrer_par_status_inactif(self):
        """Filtre les plantes inactives."""
        from src.modules.maison.logic.jardin_logic import filtrer_par_status
        
        plantes = [
            {"nom": "Tomate", "status": "inactif"},
            {"nom": "Basilic", "status": "actif"},
        ]
        
        result = filtrer_par_status(plantes, "inactif")
        
        assert len(result) == 1
        assert result[0]["nom"] == "Tomate"

    def test_filtrer_par_status_vide(self):
        """Liste vide retourne liste vide."""
        from src.modules.maison.logic.jardin_logic import filtrer_par_status
        
        result = filtrer_par_status([], "actif")
        
        assert result == []

    def test_filtrer_par_status_aucun_match(self):
        """Aucun match retourne liste vide."""
        from src.modules.maison.logic.jardin_logic import filtrer_par_status
        
        plantes = [{"nom": "Tomate", "status": "actif"}]
        
        result = filtrer_par_status(plantes, "inconnu")
        
        assert result == []


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS VALIDER_PLANTE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestValiderPlante:
    """Tests pour valider_plante."""

    def test_plante_valide(self):
        """Plante avec nom valide."""
        from src.modules.maison.logic.jardin_logic import valider_plante
        
        data = {"nom": "Tomate", "categorie": "LÃ©gumes", "frequence_arrosage": 3}
        
        valide, erreurs = valider_plante(data)
        
        assert valide is True
        assert len(erreurs) == 0

    def test_plante_sans_nom(self):
        """Plante sans nom invalide."""
        from src.modules.maison.logic.jardin_logic import valider_plante
        
        data = {"categorie": "LÃ©gumes"}
        
        valide, erreurs = valider_plante(data)
        
        assert valide is False
        assert "nom" in erreurs[0].lower()

    def test_plante_nom_vide(self):
        """Plante avec nom vide invalide."""
        from src.modules.maison.logic.jardin_logic import valider_plante
        
        data = {"nom": "", "categorie": "LÃ©gumes"}
        
        valide, erreurs = valider_plante(data)
        
        assert valide is False
        assert "nom" in erreurs[0].lower()

    def test_plante_categorie_invalide(self):
        """CatÃ©gorie non autorisÃ©e."""
        from src.modules.maison.logic.jardin_logic import valider_plante
        
        data = {"nom": "Test", "categorie": "CatÃ©gorieInconnue"}
        
        valide, erreurs = valider_plante(data)
        
        assert valide is False
        assert any("catÃ©gorie" in e.lower() for e in erreurs)

    def test_plante_frequence_arrosage_zero(self):
        """FrÃ©quence d'arrosage Ã  0 invalide."""
        from src.modules.maison.logic.jardin_logic import valider_plante
        
        data = {"nom": "Tomate", "frequence_arrosage": 0}
        
        valide, erreurs = valider_plante(data)
        
        assert valide is False
        assert any("frÃ©quence" in e.lower() for e in erreurs)

    def test_plante_frequence_arrosage_negative(self):
        """FrÃ©quence d'arrosage nÃ©gative invalide."""
        from src.modules.maison.logic.jardin_logic import valider_plante
        
        data = {"nom": "Tomate", "frequence_arrosage": -5}
        
        valide, erreurs = valider_plante(data)
        
        assert valide is False
        assert any("frÃ©quence" in e.lower() or "arrosage" in e.lower() for e in erreurs)

    def test_plante_frequence_arrosage_non_int(self):
        """FrÃ©quence d'arrosage non-entier invalide."""
        from src.modules.maison.logic.jardin_logic import valider_plante
        
        data = {"nom": "Tomate", "frequence_arrosage": "deux"}
        
        valide, erreurs = valider_plante(data)
        
        assert valide is False
        assert any("frÃ©quence" in e.lower() or "arrosage" in e.lower() for e in erreurs)

    def test_plante_multiple_erreurs(self):
        """Plusieurs erreurs Ã  la fois."""
        from src.modules.maison.logic.jardin_logic import valider_plante
        
        data = {"categorie": "Inconnu", "frequence_arrosage": -1}
        
        valide, erreurs = valider_plante(data)
        
        assert valide is False
        assert len(erreurs) >= 2
