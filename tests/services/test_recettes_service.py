"""
Tests pour RecetteService - Service critique
Tests complets pour CRUD, recherche et intégration IA
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from src.services.recettes import RecetteService, get_recette_service


# ═══════════════════════════════════════════════════════════
# TESTS INSTANCIATION ET FACTORY
# ═══════════════════════════════════════════════════════════

class TestRecetteServiceFactory:
    """Tests pour la factory et l'instanciation du service."""
    
    def test_get_recette_service_returns_instance(self):
        """La factory retourne une instance de RecetteService."""
        service = get_recette_service()
        assert service is not None
        assert isinstance(service, RecetteService)
    
    def test_get_recette_service_singleton(self):
        """La factory retourne la même instance (singleton)."""
        service1 = get_recette_service()
        service2 = get_recette_service()
        assert service1 is service2


# ═══════════════════════════════════════════════════════════
# TESTS CRUD - CREATE
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestRecetteServiceCreate:
    """Tests pour la création de recettes."""
    
    def test_creer_recette_simple(self, db, recette_service):
        """Créer une recette avec données minimales."""
        data = {
            "nom": "Tarte aux pommes",
            "description": "Une délicieuse tarte",
            "temps_preparation": 30,
            "temps_cuisson": 45,
            "portions": 6,
        }
        
        recette = recette_service.creer_recette(data, db=db)
        
        assert recette is not None
        assert recette.id is not None
        assert recette.nom == "Tarte aux pommes"
        assert recette.temps_preparation == 30
    
    def test_creer_recette_complete(self, db, recette_service):
        """Créer une recette avec tous les champs."""
        data = {
            "nom": "Poulet rôti aux herbes",
            "description": "Poulet fermier rôti avec herbes de Provence",
            "temps_preparation": 15,
            "temps_cuisson": 90,
            "portions": 6,
            "difficulte": "facile",
            "type_repas": "dîner",
            "saison": "toute_année",
            "bio": True,
            "adapte_robots": False,
        }
        
        recette = recette_service.creer_recette(data, db=db)
        
        assert recette.difficulte == "facile"
        assert recette.type_repas == "dîner"
        assert recette.bio is True
    
    def test_creer_recette_validation_nom_vide(self, db, recette_service):
        """La création échoue si le nom est vide."""
        data = {
            "nom": "",
            "description": "Description",
            "temps_preparation": 30,
            "temps_cuisson": 30,
        }
        
        with pytest.raises(Exception):  # ErreurValidation
            recette_service.creer_recette(data, db=db)
    
    def test_creer_recette_avec_ingredients(self, db, recette_service, ingredient_factory):
        """Créer une recette avec des ingrédients."""
        # Créer des ingrédients
        poulet = ingredient_factory.create(nom="Poulet", categorie="Protéines")
        thym = ingredient_factory.create(nom="Thym", categorie="Épices")
        
        data = {
            "nom": "Poulet au thym",
            "description": "Simple et savoureux",
            "temps_preparation": 10,
            "temps_cuisson": 60,
            "ingredients": [
                {"ingredient_id": poulet.id, "quantite": 1.5, "unite": "kg"},
                {"ingredient_id": thym.id, "quantite": 5, "unite": "g"},
            ]
        }
        
        recette = recette_service.creer_recette(data, db=db)
        
        assert len(recette.recette_ingredients) == 2


# ═══════════════════════════════════════════════════════════
# TESTS CRUD - READ
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestRecetteServiceRead:
    """Tests pour la lecture de recettes."""
    
    def test_obtenir_recette_par_id(self, db, sample_recipe, recette_service):
        """Récupérer une recette par son ID."""
        recette = recette_service.obtenir_par_id(sample_recipe.id, db=db)
        
        assert recette is not None
        assert recette.id == sample_recipe.id
        assert recette.nom == sample_recipe.nom
    
    def test_obtenir_recette_inexistante(self, db, recette_service):
        """Retourne None pour un ID inexistant."""
        recette = recette_service.obtenir_par_id(99999, db=db)
        assert recette is None
    
    def test_lister_recettes(self, db, recette_factory, recette_service):
        """Lister toutes les recettes."""
        # Créer plusieurs recettes
        recette_factory.create(nom="Recette 1")
        recette_factory.create(nom="Recette 2")
        recette_factory.create(nom="Recette 3")
        
        recettes = recette_service.lister_toutes(db=db)
        
        assert len(recettes) >= 3
    
    def test_lister_recettes_avec_pagination(self, db, recette_factory, recette_service):
        """Lister les recettes avec pagination."""
        # Créer 10 recettes
        for i in range(10):
            recette_factory.create(nom=f"Recette {i}")
        
        page1 = recette_service.lister_toutes(page=1, par_page=5, db=db)
        page2 = recette_service.lister_toutes(page=2, par_page=5, db=db)
        
        assert len(page1) == 5
        assert len(page2) >= 5


# ═══════════════════════════════════════════════════════════
# TESTS CRUD - UPDATE
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestRecetteServiceUpdate:
    """Tests pour la mise à jour de recettes."""
    
    def test_modifier_recette_nom(self, db, sample_recipe, recette_service):
        """Modifier le nom d'une recette."""
        nouveau_nom = "Nouveau nom de recette"
        
        recette = recette_service.modifier_recette(
            sample_recipe.id, 
            {"nom": nouveau_nom},
            db=db
        )
        
        assert recette.nom == nouveau_nom
    
    def test_modifier_recette_temps(self, db, sample_recipe, recette_service):
        """Modifier les temps de préparation/cuisson."""
        recette = recette_service.modifier_recette(
            sample_recipe.id,
            {"temps_preparation": 45, "temps_cuisson": 120},
            db=db
        )
        
        assert recette.temps_preparation == 45
        assert recette.temps_cuisson == 120
    
    def test_modifier_recette_inexistante(self, db, recette_service):
        """Modifier une recette inexistante lève une erreur."""
        with pytest.raises(Exception):  # ErreurNonTrouve
            recette_service.modifier_recette(99999, {"nom": "Test"}, db=db)


# ═══════════════════════════════════════════════════════════
# TESTS CRUD - DELETE
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestRecetteServiceDelete:
    """Tests pour la suppression de recettes."""
    
    def test_supprimer_recette(self, db, recette_factory, recette_service):
        """Supprimer une recette existante."""
        recette = recette_factory.create(nom="À supprimer")
        recette_id = recette.id
        
        resultat = recette_service.supprimer_recette(recette_id, db=db)
        
        assert resultat is True
        assert recette_service.obtenir_par_id(recette_id, db=db) is None
    
    def test_supprimer_recette_inexistante(self, db, recette_service):
        """Supprimer une recette inexistante."""
        resultat = recette_service.supprimer_recette(99999, db=db)
        assert resultat is False


# ═══════════════════════════════════════════════════════════
# TESTS RECHERCHE
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestRecetteServiceRecherche:
    """Tests pour la recherche de recettes."""
    
    def test_rechercher_par_nom(self, db, recette_factory, recette_service):
        """Rechercher des recettes par nom."""
        recette_factory.create(nom="Tarte aux pommes")
        recette_factory.create(nom="Tarte au citron")
        recette_factory.create(nom="Poulet rôti")
        
        resultats = recette_service.rechercher(query="tarte", db=db)
        
        assert len(resultats) >= 2
        for r in resultats:
            assert "tarte" in r.nom.lower()
    
    def test_rechercher_par_type_repas(self, db, recette_factory, recette_service):
        """Filtrer les recettes par type de repas."""
        recette_factory.create(nom="Petit-déj", type_repas="petit_déjeuner")
        recette_factory.create(nom="Déjeuner", type_repas="déjeuner")
        recette_factory.create(nom="Dîner", type_repas="dîner")
        
        resultats = recette_service.rechercher(type_repas="dîner", db=db)
        
        for r in resultats:
            assert r.type_repas == "dîner"
    
    def test_rechercher_par_difficulte(self, db, recette_factory, recette_service):
        """Filtrer les recettes par difficulté."""
        recette_factory.create(nom="Facile", difficulte="facile")
        recette_factory.create(nom="Moyen", difficulte="moyen")
        recette_factory.create(nom="Difficile", difficulte="difficile")
        
        resultats = recette_service.rechercher(difficulte="facile", db=db)
        
        for r in resultats:
            assert r.difficulte == "facile"
    
    def test_rechercher_combinaison_filtres(self, db, recette_factory, recette_service):
        """Recherche avec plusieurs filtres combinés."""
        recette_factory.create(
            nom="Salade légère", 
            type_repas="déjeuner", 
            difficulte="facile"
        )
        
        resultats = recette_service.rechercher(
            query="salade",
            type_repas="déjeuner",
            difficulte="facile",
            db=db
        )
        
        assert len(resultats) >= 1


# ═══════════════════════════════════════════════════════════
# TESTS STATISTIQUES
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestRecetteServiceStats:
    """Tests pour les statistiques de recettes."""
    
    def test_compter_recettes(self, db, recette_factory, recette_service):
        """Compter le nombre total de recettes."""
        initial = recette_service.compter(db=db)
        
        recette_factory.create()
        recette_factory.create()
        
        final = recette_service.compter(db=db)
        
        assert final == initial + 2
    
    def test_statistiques_par_difficulte(self, db, recette_factory, recette_service):
        """Obtenir les statistiques par difficulté."""
        recette_factory.create(difficulte="facile")
        recette_factory.create(difficulte="facile")
        recette_factory.create(difficulte="moyen")
        
        stats = recette_service.statistiques_par_difficulte(db=db)
        
        assert "facile" in stats
        assert stats["facile"] >= 2


# ═══════════════════════════════════════════════════════════
# TESTS INTÉGRATION IA (avec mocks)
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestRecetteServiceIA:
    """Tests pour l'intégration IA du service recettes."""
    
    @patch('src.services.recettes.RecetteService.call_with_list_parsing_sync')
    def test_generer_suggestions_ia(self, mock_ia, recette_service):
        """Générer des suggestions de recettes via IA."""
        mock_ia.return_value = [
            Mock(nom="Salade César", temps_preparation=15),
            Mock(nom="Pasta primavera", temps_preparation=25),
        ]
        
        suggestions = recette_service.generer_suggestions(
            contexte="repas léger pour le déjeuner"
        )
        
        assert len(suggestions) == 2
        mock_ia.assert_called_once()
    
    @patch('src.services.recettes.RecetteService.call_with_parsing_sync')
    def test_generer_version_bebe(self, mock_ia, db, sample_recipe, recette_service):
        """Générer une version bébé d'une recette."""
        mock_ia.return_value = Mock(
            instructions_modifiees="Version mixée pour bébé",
            notes_bebe="Adapter la texture",
            age_minimum_mois=8
        )
        
        version = recette_service.generer_version_bebe(
            sample_recipe.id,
            db=db
        )
        
        assert version is not None
        assert version.age_minimum_mois == 8
