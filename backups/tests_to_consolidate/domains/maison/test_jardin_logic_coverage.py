"""
Tests de couverture complémentaires pour jardin_logic.py
Objectif: atteindre 80%+ de couverture
Couvre les lignes non testées: 37, 39, 41, 205, 222-235
"""
import pytest
from datetime import date
from unittest.mock import patch


# ═══════════════════════════════════════════════════════════
# TESTS GET_SAISON_ACTUELLE - branches manquantes
# ═══════════════════════════════════════════════════════════

class TestGetSaisonActuelle:
    """Tests pour les différentes saisons."""

    def test_saison_ete_juin(self):
        """Teste retour Été en juin."""
        from src.domains.maison.logic.jardin_logic import get_saison_actuelle
        
        with patch("src.domains.maison.logic.jardin_logic.date") as mock_date:
            mock_date.today.return_value = date(2026, 6, 15)
            
            result = get_saison_actuelle()
            
            assert result == "Été"

    def test_saison_ete_juillet(self):
        """Teste retour Été en juillet."""
        from src.domains.maison.logic.jardin_logic import get_saison_actuelle
        
        with patch("src.domains.maison.logic.jardin_logic.date") as mock_date:
            mock_date.today.return_value = date(2026, 7, 15)
            
            result = get_saison_actuelle()
            
            assert result == "Été"

    def test_saison_ete_aout(self):
        """Teste retour Été en août."""
        from src.domains.maison.logic.jardin_logic import get_saison_actuelle
        
        with patch("src.domains.maison.logic.jardin_logic.date") as mock_date:
            mock_date.today.return_value = date(2026, 8, 15)
            
            result = get_saison_actuelle()
            
            assert result == "Été"

    def test_saison_automne_septembre(self):
        """Teste retour Automne en septembre."""
        from src.domains.maison.logic.jardin_logic import get_saison_actuelle
        
        with patch("src.domains.maison.logic.jardin_logic.date") as mock_date:
            mock_date.today.return_value = date(2026, 9, 15)
            
            result = get_saison_actuelle()
            
            assert result == "Automne"

    def test_saison_automne_octobre(self):
        """Teste retour Automne en octobre."""
        from src.domains.maison.logic.jardin_logic import get_saison_actuelle
        
        with patch("src.domains.maison.logic.jardin_logic.date") as mock_date:
            mock_date.today.return_value = date(2026, 10, 15)
            
            result = get_saison_actuelle()
            
            assert result == "Automne"

    def test_saison_automne_novembre(self):
        """Teste retour Automne en novembre."""
        from src.domains.maison.logic.jardin_logic import get_saison_actuelle
        
        with patch("src.domains.maison.logic.jardin_logic.date") as mock_date:
            mock_date.today.return_value = date(2026, 11, 15)
            
            result = get_saison_actuelle()
            
            assert result == "Automne"


# ═══════════════════════════════════════════════════════════
# TESTS FILTRER_PAR_STATUS
# ═══════════════════════════════════════════════════════════

class TestFiltrerParStatus:
    """Tests pour filtrer_par_status."""

    def test_filtrer_par_status_actif(self):
        """Filtre les plantes actives."""
        from src.domains.maison.logic.jardin_logic import filtrer_par_status
        
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
        from src.domains.maison.logic.jardin_logic import filtrer_par_status
        
        plantes = [
            {"nom": "Tomate", "status": "inactif"},
            {"nom": "Basilic", "status": "actif"},
        ]
        
        result = filtrer_par_status(plantes, "inactif")
        
        assert len(result) == 1
        assert result[0]["nom"] == "Tomate"

    def test_filtrer_par_status_vide(self):
        """Liste vide retourne liste vide."""
        from src.domains.maison.logic.jardin_logic import filtrer_par_status
        
        result = filtrer_par_status([], "actif")
        
        assert result == []

    def test_filtrer_par_status_aucun_match(self):
        """Aucun match retourne liste vide."""
        from src.domains.maison.logic.jardin_logic import filtrer_par_status
        
        plantes = [{"nom": "Tomate", "status": "actif"}]
        
        result = filtrer_par_status(plantes, "inconnu")
        
        assert result == []


# ═══════════════════════════════════════════════════════════
# TESTS VALIDER_PLANTE
# ═══════════════════════════════════════════════════════════

class TestValiderPlante:
    """Tests pour valider_plante."""

    def test_plante_valide(self):
        """Plante avec nom valide."""
        from src.domains.maison.logic.jardin_logic import valider_plante
        
        data = {"nom": "Tomate", "categorie": "Légumes", "frequence_arrosage": 3}
        
        valide, erreurs = valider_plante(data)
        
        assert valide is True
        assert len(erreurs) == 0

    def test_plante_sans_nom(self):
        """Plante sans nom invalide."""
        from src.domains.maison.logic.jardin_logic import valider_plante
        
        data = {"categorie": "Légumes"}
        
        valide, erreurs = valider_plante(data)
        
        assert valide is False
        assert "nom" in erreurs[0].lower()

    def test_plante_nom_vide(self):
        """Plante avec nom vide invalide."""
        from src.domains.maison.logic.jardin_logic import valider_plante
        
        data = {"nom": "", "categorie": "Légumes"}
        
        valide, erreurs = valider_plante(data)
        
        assert valide is False
        assert "nom" in erreurs[0].lower()

    def test_plante_categorie_invalide(self):
        """Catégorie non autorisée."""
        from src.domains.maison.logic.jardin_logic import valider_plante
        
        data = {"nom": "Test", "categorie": "CatégorieInconnue"}
        
        valide, erreurs = valider_plante(data)
        
        assert valide is False
        assert any("catégorie" in e.lower() for e in erreurs)

    def test_plante_frequence_arrosage_zero(self):
        """Fréquence d'arrosage à 0 invalide."""
        from src.domains.maison.logic.jardin_logic import valider_plante
        
        data = {"nom": "Tomate", "frequence_arrosage": 0}
        
        valide, erreurs = valider_plante(data)
        
        assert valide is False
        assert any("fréquence" in e.lower() for e in erreurs)

    def test_plante_frequence_arrosage_negative(self):
        """Fréquence d'arrosage négative invalide."""
        from src.domains.maison.logic.jardin_logic import valider_plante
        
        data = {"nom": "Tomate", "frequence_arrosage": -5}
        
        valide, erreurs = valider_plante(data)
        
        assert valide is False
        assert any("fréquence" in e.lower() or "arrosage" in e.lower() for e in erreurs)

    def test_plante_frequence_arrosage_non_int(self):
        """Fréquence d'arrosage non-entier invalide."""
        from src.domains.maison.logic.jardin_logic import valider_plante
        
        data = {"nom": "Tomate", "frequence_arrosage": "deux"}
        
        valide, erreurs = valider_plante(data)
        
        assert valide is False
        assert any("fréquence" in e.lower() or "arrosage" in e.lower() for e in erreurs)

    def test_plante_multiple_erreurs(self):
        """Plusieurs erreurs à la fois."""
        from src.domains.maison.logic.jardin_logic import valider_plante
        
        data = {"categorie": "Inconnu", "frequence_arrosage": -1}
        
        valide, erreurs = valider_plante(data)
        
        assert valide is False
        assert len(erreurs) >= 2
