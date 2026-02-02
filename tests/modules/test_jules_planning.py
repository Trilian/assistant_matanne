"""
Tests pour le module Planning Jules (activités d'éveil).
"""

import pytest
from datetime import date
from unittest.mock import patch, MagicMock

# Import du module à tester
from src.domains.famille.ui.jules_planning import (
    CATEGORIES_ACTIVITES,
    PLANNING_SEMAINE_TYPE,
    JOURS_SEMAINE,
    get_age_jules_mois,
    generer_activites_jour,
    get_planning_semaine,
)


class TestConstantes:
    """Tests des constantes du module."""
    
    def test_categories_activites_existe(self):
        """Vérifie que les catégories d'activités sont définies."""
        assert len(CATEGORIES_ACTIVITES) >= 5
        assert "motricite" in CATEGORIES_ACTIVITES
        assert "langage" in CATEGORIES_ACTIVITES
        assert "creativite" in CATEGORIES_ACTIVITES
    
    def test_chaque_categorie_a_activites(self):
        """Vérifie que chaque catégorie a des activités."""
        for cat, info in CATEGORIES_ACTIVITES.items():
            assert "emoji" in info, f"Catégorie {cat} manque emoji"
            assert "activites" in info, f"Catégorie {cat} manque activites"
            assert len(info["activites"]) >= 3, f"Catégorie {cat} a trop peu d'activités"
    
    def test_planning_semaine_complet(self):
        """Vérifie que le planning couvre tous les jours."""
        assert len(PLANNING_SEMAINE_TYPE) == 7
        for jour in range(7):
            assert jour in PLANNING_SEMAINE_TYPE
            assert len(PLANNING_SEMAINE_TYPE[jour]) >= 2
    
    def test_jours_semaine(self):
        """Vérifie les jours de la semaine."""
        assert len(JOURS_SEMAINE) == 7
        assert JOURS_SEMAINE[0] == "Lundi"
        assert JOURS_SEMAINE[6] == "Dimanche"


class TestAgeJules:
    """Tests pour le calcul de l'âge de Jules."""
    
    @patch("src.domains.famille.ui.jules_planning.get_db_context")
    def test_age_depuis_db(self, mock_db_context):
        """Test récupération âge depuis la base."""
        mock_child = MagicMock()
        mock_child.date_of_birth = date(2024, 6, 22)
        mock_child.actif = True
        mock_child.name = "Jules"
        
        mock_session = MagicMock()
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_child
        mock_db_context.return_value.__enter__.return_value = mock_session
        
        age = get_age_jules_mois()
        assert age > 0
    
    def test_age_defaut(self):
        """Test âge par défaut si DB échoue."""
        with patch("src.domains.famille.ui.jules_planning.get_db_context", side_effect=Exception):
            age = get_age_jules_mois()
            # Né le 22/06/2024, donc > 18 mois en février 2026
            assert age >= 18


class TestGenerationActivites:
    """Tests pour la génération d'activités."""
    
    def test_generer_activites_lundi(self):
        """Génère les activités du lundi."""
        activites = generer_activites_jour(0, seed=42)
        assert len(activites) >= 2
        
        for act in activites:
            assert "nom" in act
            assert "duree" in act
            assert "emoji" in act
    
    def test_generer_activites_tous_jours(self):
        """Génère les activités pour tous les jours."""
        for jour in range(7):
            activites = generer_activites_jour(jour, seed=100)
            assert len(activites) >= 2
    
    def test_seed_reproductible(self):
        """Vérifie que le seed produit des résultats reproductibles."""
        act1 = generer_activites_jour(0, seed=123)
        act2 = generer_activites_jour(0, seed=123)
        
        assert act1[0]["nom"] == act2[0]["nom"]


class TestPlanningSemaine:
    """Tests pour le planning hebdomadaire."""
    
    def test_planning_complet(self):
        """Vérifie que le planning a 7 jours."""
        planning = get_planning_semaine()
        assert len(planning) == 7
    
    def test_planning_consistent(self):
        """Vérifie que le planning est consistent (même semaine = même planning)."""
        planning1 = get_planning_semaine()
        planning2 = get_planning_semaine()
        
        # Même jour = mêmes activités
        assert planning1[0][0]["nom"] == planning2[0][0]["nom"]
    
    def test_chaque_jour_a_activites(self):
        """Vérifie que chaque jour a des activités."""
        planning = get_planning_semaine()
        
        for jour, activites in planning.items():
            assert len(activites) >= 2, f"Jour {jour} a trop peu d'activités"


class TestStructureActivite:
    """Tests de la structure des activités."""
    
    def test_structure_activite(self):
        """Vérifie la structure d'une activité."""
        activites = generer_activites_jour(0, seed=1)
        act = activites[0]
        
        required_keys = ["nom", "duree", "desc", "emoji", "categorie", "couleur"]
        for key in required_keys:
            assert key in act, f"Clé {key} manquante dans activité"
    
    def test_duree_raisonnable(self):
        """Vérifie que les durées sont raisonnables."""
        for cat, info in CATEGORIES_ACTIVITES.items():
            for act in info["activites"]:
                assert 5 <= act["duree"] <= 60, f"Durée hors limites: {act['nom']}"
