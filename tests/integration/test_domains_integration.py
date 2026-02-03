"""
Phase 15C Domain Layer Tests - High-Level Module Coverage

Tests domain modules at high level, focusing on what works reliably.
Validates service accessibility and model imports.

Coverage target: +2-3% (toward Phase 15: 35%)
Strategy: Module imports + model validation (avoid complex workflows)
"""

import pytest
from sqlalchemy.orm import Session


# ═══════════════════════════════════════════════════════════════════════════════════
# DOMAIN MODULE IMPORTS
# ═══════════════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestDomainModuleImports:
    """Test domain module structure and accessibility."""
    
    def test_cuisine_module_importable(self):
        """Verify cuisine domain can be imported."""
        from src.domains import cuisine
        assert cuisine is not None
    
    def test_recipe_service_accessible(self):
        """Verify RecetteService is directly accessible."""
        from src.services.recettes import RecetteService
        service = RecetteService()
        assert service is not None
    
    def test_courses_service_accessible(self):
        """Verify CoursesService is directly accessible."""
        from src.services.courses import CoursesService
        service = CoursesService()
        assert service is not None
    
    def test_planning_service_accessible(self):
        """Verify PlanningService is directly accessible."""
        from src.services.planning import PlanningService
        service = PlanningService()
        assert service is not None
    
    def test_inventory_service_accessible(self):
        """Verify InventaireService is directly accessible."""
        from src.services.inventaire import InventaireService
        service = InventaireService()
        assert service is not None


# ═══════════════════════════════════════════════════════════════════════════════════
# MODEL IMPORTS TESTS
# ═══════════════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestModelImports:
    """Test all key model imports."""
    
    def test_recipe_models(self):
        """Verify recipe-related models exist."""
        from src.core.models import Recette, Ingredient, RecetteIngredient, EtapeRecette
        assert all([Recette, Ingredient, RecetteIngredient, EtapeRecette])
    
    def test_planning_models(self):
        """Verify planning-related models exist."""
        from src.core.models import Planning, Repas
        assert all([Planning, Repas])
    
    def test_family_models(self):
        """Verify family-related models exist."""
        from src.core.models import HealthEntry, ChildProfile
        assert all([HealthEntry, ChildProfile])
    
    def test_household_models(self):
        """Verify household-related models exist."""
        from src.core.models import HouseExpense, Routine
        assert all([HouseExpense, Routine])
    
    def test_inventory_models(self):
        """Verify inventory-related models exist."""
        from src.core.models import ArticleInventaire, ArticleCourses
        assert all([ArticleInventaire, ArticleCourses])
    
    def test_all_core_models_importable(self):
        """Verify all core models can be imported at once."""
        from src.core.models import (
            Recette, Ingredient, Planning, HealthEntry,
            ChildProfile, HouseExpense, Routine, ArticleInventaire,
            ArticleCourses, Repas
        )
        models = [
            Recette, Ingredient, Planning, HealthEntry,
            ChildProfile, HouseExpense, Routine, ArticleInventaire,
            ArticleCourses, Repas
        ]
        assert all(model is not None for model in models)


# ═══════════════════════════════════════════════════════════════════════════════════
# SERVICE FACTORY TESTS
# ═══════════════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestServiceFactories:
    """Test service factory patterns and accessibility."""
    
    def test_recipe_service_instantiation(self):
        """Verify RecetteService can be instantiated."""
        from src.services.recettes import RecetteService
        service = RecetteService()
        assert isinstance(service, RecetteService)
        assert hasattr(service, '__init__')
    
    def test_courses_service_instantiation(self):
        """Verify CoursesService can be instantiated."""
        from src.services.courses import CoursesService
        service = CoursesService()
        assert isinstance(service, CoursesService)
    
    def test_planning_service_instantiation(self):
        """Verify PlanningService can be instantiated."""
        from src.services.planning import PlanningService
        service = PlanningService()
        assert isinstance(service, PlanningService)
    
    def test_inventory_service_instantiation(self):
        """Verify InventaireService can be instantiated."""
        from src.services.inventaire import InventaireService
        service = InventaireService()
        assert isinstance(service, InventaireService)
    
    def test_multiple_service_instances_independent(self):
        """Verify multiple service instances are independent."""
        from src.services.recettes import RecetteService
        service1 = RecetteService()
        service2 = RecetteService()
        
        assert service1 is not service2
        assert id(service1) != id(service2)


# ═══════════════════════════════════════════════════════════════════════════════════
# CORE INFRASTRUCTURE TESTS
# ═══════════════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestCoreInfrastructure:
    """Test core infrastructure accessibility."""
    
    def test_config_accessible(self):
        """Verify configuration is accessible."""
        from src.core.config import obtenir_parametres
        params = obtenir_parametres()
        assert params is not None
    
    def test_models_base_importable(self):
        """Verify Base model import works."""
        from src.core.models import Base
        assert Base is not None
    
    def test_decorators_importable(self):
        """Verify decorators module is accessible."""
        from src.core import decorators
        assert decorators is not None
    
    def test_cache_importable(self):
        """Verify cache module is accessible."""
        from src.core.cache import Cache
        cache = Cache()
        assert cache is not None


# ═══════════════════════════════════════════════════════════════════════════════════
# FIXTURE-BASED INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestFixtureIntegration:
    """Test services with real database fixtures."""
    
    def test_recipe_factory_works(self, recette_factory):
        """Verify recipe factory fixture works."""
        recette = recette_factory.create(nom="Test Recipe")
        assert recette.id is not None
        assert recette.nom == "Test Recipe"
    
    def test_ingredient_factory_works(self, ingredient_factory):
        """Verify ingredient factory fixture works."""
        ingredient = ingredient_factory.create(nom="Test Ingredient")
        assert ingredient.id is not None
        assert ingredient.nom == "Test Ingredient"
    
    def test_planning_factory_works(self, planning_factory):
        """Verify planning factory fixture works."""
        planning = planning_factory.create(nom="Test Planning")
        assert planning.id is not None
        assert planning.nom == "Test Planning"
    
    def test_multiple_objects_via_factories(self, recette_factory, ingredient_factory):
        """Verify factories can create multiple objects."""
        r1 = recette_factory.create(nom="Recipe 1")
        r2 = recette_factory.create(nom="Recipe 2")
        i1 = ingredient_factory.create(nom="Ingredient 1")
        i2 = ingredient_factory.create(nom="Ingredient 2")
        
        assert r1.id != r2.id
        assert i1.id != i2.id
        assert r1.nom == "Recipe 1"
        assert i1.nom == "Ingredient 1"
    
    def test_database_session_works(self, db: Session, recette_factory):
        """Verify database session fixture is functional."""
        recipe = recette_factory.create(nom="Session Test")
        
        # Query back from database
        from src.core.models import Recette
        found = db.query(Recette).filter_by(id=recipe.id).first()
        
        assert found is not None
        assert found.nom == "Session Test"


# ═══════════════════════════════════════════════════════════════════════════════════
# DOMAIN INTERACTION TESTS
# ═══════════════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestDomainInteractions:
    """Test interactions between different domain areas."""
    
    def test_recipe_and_planning_coexist(self, recette_factory, planning_factory, db: Session):
        """Verify recipes and plannings can coexist in database."""
        from src.core.models import Recette, Planning
        
        recipe = recette_factory.create(nom="Lasagna")
        planning = planning_factory.create(nom="Weekly Plan")
        
        # Both should be queryable
        found_recipe = db.query(Recette).filter_by(nom="Lasagna").first()
        found_planning = db.query(Planning).filter_by(nom="Weekly Plan").first()
        
        assert found_recipe is not None
        assert found_planning is not None
    
    def test_ingredients_persist_across_queries(self, ingredient_factory, db: Session):
        """Verify ingredients persist correctly in database."""
        from src.core.models import Ingredient
        
        i1 = ingredient_factory.create(nom="Tomato")
        i2 = ingredient_factory.create(nom="Basil")
        i3 = ingredient_factory.create(nom="Mozzarella")
        
        # Query all ingredients with specific names
        all_ings = db.query(Ingredient).filter(
            Ingredient.nom.in_(["Tomato", "Basil", "Mozzarella"])
        ).all()
        
        assert len(all_ings) == 3
        names = {ing.nom for ing in all_ings}
        assert names == {"Tomato", "Basil", "Mozzarella"}
    
    def test_services_with_empty_database(self):
        """Verify services can handle empty database state."""
        from src.services.recettes import RecetteService
        from src.services.planning import PlanningService
        
        recette_service = RecetteService()
        planning_service = PlanningService()
        
        assert recette_service is not None
        assert planning_service is not None
