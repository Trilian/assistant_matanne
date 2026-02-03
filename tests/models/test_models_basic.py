"""
MODEL INSTANTIATION TESTS
Test that all ORM models can be imported and instantiated
Simple pattern: import model, create instance, verify
"""

import pytest
from datetime import datetime

# ==============================================================================
# TESTS: MODEL IMPORTS AND INSTANTIATION
# ==============================================================================

class TestRecipeModels:
    """Recipe-related model tests"""
    
    def test_import_recette_model(self):
        """Test importing Recette model"""
        from src.core.models import Recette
        assert Recette is not None
    
    def test_import_ingredient_model(self):
        """Test importing Ingredient model"""
        from src.core.models import Ingredient
        assert Ingredient is not None
    
    def test_import_recipe_ingredient_model(self):
        """Test importing RecetteIngredient model"""
        from src.core.models import RecetteIngredient
        assert RecetteIngredient is not None
    
    def test_import_etape_recette_model(self):
        """Test importing EtapeRecette model"""
        from src.core.models import EtapeRecette
        assert EtapeRecette is not None


class TestInventoryModels:
    """Inventory-related model tests"""
    
    def test_import_article_inventaire_model(self):
        """Test importing ArticleInventaire model"""
        from src.core.models import ArticleInventaire
        assert ArticleInventaire is not None
    
    def test_import_article_courses_model(self):
        """Test importing ArticleCourses model"""
        from src.core.models import ArticleCourses
        assert ArticleCourses is not None
    
    def test_import_historique_inventaire_model(self):
        """Test importing HistoriqueInventaire model"""
        from src.core.models import HistoriqueInventaire
        assert HistoriqueInventaire is not None


class TestPlanningModels:
    """Planning-related model tests"""
    
    def test_import_planning_model(self):
        """Test importing Planning model"""
        from src.core.models import Planning
        assert Planning is not None
    
    def test_import_repas_model(self):
        """Test importing Repas model"""
        from src.core.models import Repas
        assert Repas is not None
    
    def test_import_routine_model(self):
        """Test importing Routine model"""
        from src.core.models import Routine
        assert Routine is not None
    
    def test_import_routine_task_model(self):
        """Test importing RoutineTask model"""
        from src.core.models import RoutineTask
        assert RoutineTask is not None


class TestFamilyModels:
    """Family-related model tests"""
    
    def test_import_child_profile_model(self):
        """Test importing ChildProfile model"""
        from src.core.models import ChildProfile
        assert ChildProfile is not None
    
    def test_import_milestone_model(self):
        """Test importing Milestone model"""
        from src.core.models import Milestone
        assert Milestone is not None
    
    def test_import_family_activity_model(self):
        """Test importing FamilyActivity model"""
        from src.core.models import FamilyActivity
        assert FamilyActivity is not None
    
    def test_import_family_budget_model(self):
        """Test importing FamilyBudget model"""
        from src.core.models import FamilyBudget
        assert FamilyBudget is not None


class TestHealthModels:
    """Health-related model tests"""
    
    def test_import_wellbeing_entry_model(self):
        """Test importing WellbeingEntry model"""
        from src.core.models import WellbeingEntry
        assert WellbeingEntry is not None
    
    def test_import_health_routine_model(self):
        """Test importing HealthRoutine model"""
        from src.core.models import HealthRoutine
        assert HealthRoutine is not None
    
    def test_import_health_objective_model(self):
        """Test importing HealthObjective model"""
        from src.core.models import HealthObjective
        assert HealthObjective is not None
    
    def test_import_health_entry_model(self):
        """Test importing HealthEntry model"""
        from src.core.models import HealthEntry
        assert HealthEntry is not None


class TestProjectModels:
    """Project-related model tests"""
    
    def test_import_project_model(self):
        """Test importing Project model"""
        from src.core.models import Project
        assert Project is not None
    
    def test_import_project_task_model(self):
        """Test importing ProjectTask model"""
        from src.core.models import ProjectTask
        assert ProjectTask is not None


class TestHouseModels:
    """House-related model tests"""
    
    def test_import_house_expense_model(self):
        """Test importing HouseExpense model"""
        from src.core.models import HouseExpense
        assert HouseExpense is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
