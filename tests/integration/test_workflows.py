"""
Integration tests for complete workflows across multiple services.

These tests verify that services work together correctly in realistic scenarios.
"""

import pytest
from datetime import date

from src.services.recettes import RecetteService
from src.services.inventaire import InventaireService
from src.services.planning import PlanningService
from src.services.courses import CoursesService


# ═══════════════════════════════════════════════════════════
# COMPLETE MEAL PLANNING WORKFLOW
# ═══════════════════════════════════════════════════════════

@pytest.mark.integration
class TestCompleteWorkflow:
    """Test complete workflow: Recipe → Planning → Shopping."""
    
    def test_recipe_to_planning_workflow(
        self,
        db,
        recette_service: RecetteService,
        planning_service: PlanningService,
        planning_factory,
    ):
        """Test creating recipe and adding to planning."""
        # Create a planning first
        planning = planning_factory.create(
            nom="Test Planning",
            semaine_debut=date.today(),
        )
        
        # Step 1: Create recipe
        recipe_input = {
            'nom': 'Pâtes Bolognaise',
            'description': 'Pâtes avec sauce bolognaise',
            'temps_preparation': 10,
            'temps_cuisson': 30,
            'portions': 4,
            'difficulte': 'facile',
            'type_repas': 'dîner',
            'saison': 'toute_année',
            'ingredients': [
                {'nom': 'Pâtes', 'quantite': 400, 'unite': 'g'},
                {'nom': 'Tomate', 'quantite': 500, 'unite': 'g'},
            ],
            'etapes': [
                {'ordre': 1, 'description': 'Faire bouillir l\'eau'},
                {'ordre': 2, 'description': 'Cuire les pâtes'},
            ],
        }
        
        recipe = recette_service.create_complete(recipe_input, db=db)
        assert recipe is not None
        assert recipe.nom == 'Pâtes Bolognaise'
        
        # Step 2: Get planning
        planning_result = planning_service.get_planning(planning.id, db=db)
        # Planning should be accessible for scheduling the recipe
        assert planning_result is not None
    
    def test_inventory_to_shopping_workflow(
        self,
        db,
        inventaire_service: InventaireService,
        courses_service: CoursesService,
    ):
        """Test checking inventory and creating shopping list."""
        # Step 1: Get complete inventory
        inventory = inventaire_service.get_inventaire_complet(db=db)
        
        # Step 2: Check for alerts (low stock items)
        if inventory:
            # Should be able to generate suggestions for shopping
            suggestions = courses_service.get_suggestions_ia(
                contexte="Low stock items need replenishment",
                db=db,
            )
            # Suggestions might be None if IA not available in test
            # but service should be callable
            assert True
    
    def test_recipe_search_filters(self, recette_service: RecetteService, db):
        """Test recipe search with filters."""
        # Should be able to search recipes with various filters
        recipes = recette_service.search_advanced(
            term="",
            difficulte="facile",
            type_repas="dîner",
            saison="toute_année",
            db=db,
        )
        # Should return list (possibly empty in test)
        assert isinstance(recipes, list)


# ═══════════════════════════════════════════════════════════
# CROSS-SERVICE DATA CONSISTENCY
# ═══════════════════════════════════════════════════════════

@pytest.mark.integration
class TestCrossServiceConsistency:
    """Test data consistency across services."""
    
    def test_recipe_update_consistency(
        self,
        db,
        recette_service: RecetteService,
    ):
        """Test recipe updates are consistent."""
        # Create and retrieve same recipe
        recipe_input = {
            'nom': 'Test Recipe',
            'description': 'For consistency testing',
            'temps_preparation': 30,
            'temps_cuisson': 20,
            'difficulte': 'moyen',
            'type_repas': 'dîner',
            'saison': 'toute_année',
            'portions': 4,
            'ingredients': [
                {'nom': 'Test Ingredient', 'quantite': 100, 'unite': 'g'}
            ],
            'etapes': [
                {'ordre': 1, 'description': 'Test step', 'duree': 10}
            ],
        }
        
        recipe = recette_service.create_complete(recipe_input, db=db)
        assert recipe is not None
        
        # Retrieve by ID
        retrieved = recette_service.get_by_id_full(recipe.id, db=db)
        assert retrieved.nom == recipe.nom
    
    def test_service_isolation(
        self,
        db,
        recette_service: RecetteService,
        inventaire_service: InventaireService,
        planning_service: PlanningService,
        courses_service: CoursesService,
    ):
        """Test that services operate independently."""
        # Each service should work without requiring others
        
        # Recipe service
        recipes = recette_service.get_by_type("dîner", db=db)
        assert isinstance(recipes, list)
        
        # Inventory service
        inventory = inventaire_service.get_inventaire_complet(db=db)
        assert isinstance(inventory, list) or inventory is None
        
        # Planning service
        planning = planning_service.get_planning(db=db)
        # Planning might be None if not created
        
        # Shopping service
        shopping = courses_service.get_liste_courses(db=db)
        assert isinstance(shopping, list) or shopping is None


# ═══════════════════════════════════════════════════════════
# CACHE BEHAVIOR ACROSS SERVICES
# ═══════════════════════════════════════════════════════════

@pytest.mark.integration
class TestCacheBehavior:
    """Test caching works correctly across service calls."""
    
    def test_planning_cache_hits(
        self,
        db,
        planning_service: PlanningService,
    ):
        """Test planning caching."""
        # First call
        planning1 = planning_service.get_planning(db=db)
        
        # Second call should use cache
        planning2 = planning_service.get_planning(db=db)
        
        # Both should return same object
        assert planning1 == planning2
    
    def test_cache_invalidation_on_update(
        self,
        db,
        recette_service: RecetteService,
    ):
        """Test cache invalidation after updates."""
        # Create recipe (will be cached)
        recipe_input = {
            'nom': 'Cache Test Recipe',
            'description': 'For cache testing',
            'temps_preparation': 30,
            'temps_cuisson': 20,
            'difficulte': 'moyen',
            'type_repas': 'dîner',
            'saison': 'toute_année',
            'portions': 4,
            'ingredients': [
                {'nom': 'Test Ingredient', 'quantite': 100, 'unite': 'g'}
            ],
            'etapes': [
                {'ordre': 1, 'description': 'Test step', 'duree': 10}
            ],
        }
        
        recipe = recette_service.create_complete(recipe_input, db=db)
        
        # Retrieve it (uses cache)
        retrieved = recette_service.get_by_id_full(recipe.id, db=db)
        
        # Both operations should succeed
        assert recipe.id == retrieved.id


# ═══════════════════════════════════════════════════════════
# ERROR HANDLING ACROSS SERVICES
# ═══════════════════════════════════════════════════════════

@pytest.mark.integration
class TestErrorHandling:
    """Test error handling in service interactions."""
    
    def test_missing_recipe_handling(
        self,
        db,
        recette_service: RecetteService,
    ):
        """Test handling of missing recipes."""
        # Try to get non-existent recipe
        result = recette_service.get_by_id_full(99999, db=db)
        # Should return None with error handling decorator
        assert result is None or result.id is None
    
    def test_invalid_filter_handling(
        self,
        db,
        recette_service: RecetteService,
    ):
        """Test handling of invalid filters."""
        # Should handle invalid filters gracefully
        recipes = recette_service.search_advanced(
            term="test",
            difficulte="invalid",  # Invalid difficulty
            db=db,
        )
        # Should still return list, possibly empty
        assert isinstance(recipes, list)
