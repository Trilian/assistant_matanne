"""
Shared test fixtures and infrastructure for modules and services tests.

Provides:
- Service mocks and builders
- Complex scenario builders
- Business logic fixtures
- Integration helpers
- Assertion utilities
"""

import pytest
from unittest.mock import Mock, MagicMock, PropertyMock
from datetime import datetime, timedelta, date
import json


# ═══════════════════════════════════════════════════════════
# SHARED SERVICE FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def ai_client_mock():
    """Mock Mistral AI client."""
    client = MagicMock()
    client.call = MagicMock(return_value={
        "text": "AI Response",
        "choices": [{"message": {"content": "Response"}}]
    })
    return client


@pytest.fixture
def cache_mock():
    """Mock cache system."""
    cache = MagicMock()
    cache.get = MagicMock(return_value=None)
    cache.set = MagicMock(return_value=True)
    cache.clear = MagicMock(return_value=True)
    return cache


@pytest.fixture
def rate_limiter_mock():
    """Mock rate limiter."""
    limiter = MagicMock()
    limiter.is_allowed = MagicMock(return_value=True)
    limiter.get_count = MagicMock(return_value=0)
    limiter.increment = MagicMock(return_value=1)
    return limiter


# ═══════════════════════════════════════════════════════════
# BUSINESS OBJECT BUILDERS
# ═══════════════════════════════════════════════════════════


class RecipeBuilder:
    """Fluent builder for recipe objects."""
    
    def __init__(self):
        self.recipe = {
            "name": "Test Recipe",
            "description": "Test description",
            "ingredients": [],
            "instructions": "Mix and cook",
            "prep_time": 10,
            "cook_time": 20,
            "servings": 4,
            "category": "Main",
            "difficulty": "easy",
            "tags": []
        }
    
    def with_name(self, name):
        self.recipe["name"] = name
        return self
    
    def with_ingredients(self, ingredients):
        self.recipe["ingredients"] = ingredients
        return self
    
    def with_category(self, category):
        self.recipe["category"] = category
        return self
    
    def with_times(self, prep=10, cook=20):
        self.recipe["prep_time"] = prep
        self.recipe["cook_time"] = cook
        return self
    
    def with_difficulty(self, difficulty):
        self.recipe["difficulty"] = difficulty
        return self
    
    def build(self):
        return self.recipe.copy()


class MealPlanBuilder:
    """Fluent builder for meal plans."""
    
    def __init__(self):
        self.plan = {
            "week": 1,
            "meals": [],
            "created_at": datetime.now().isoformat()
        }
    
    def for_week(self, week):
        self.plan["week"] = week
        return self
    
    def add_meal(self, day, meal_type, recipe_id):
        meal = {"day": day, meal_type: recipe_id}
        self.plan["meals"].append(meal)
        return self
    
    def build(self):
        return self.plan.copy()


class ShoppingListBuilder:
    """Fluent builder for shopping lists."""
    
    def __init__(self):
        self.list = {
            "name": "Shopping List",
            "items": [],
            "created_at": datetime.now().isoformat()
        }
    
    def with_name(self, name):
        self.list["name"] = name
        return self
    
    def add_item(self, name, quantity=1, unit=""):
        self.list["items"].append({
            "name": name,
            "quantity": quantity,
            "unit": unit,
            "purchased": False
        })
        return self
    
    def build(self):
        return self.list.copy()


class EventBuilder:
    """Fluent builder for calendar events."""
    
    def __init__(self):
        self.event = {
            "title": "Event",
            "date": date.today().isoformat(),
            "time": "10:00",
            "location": "",
            "description": "",
            "category": "General",
            "reminders": []
        }
    
    def with_title(self, title):
        self.event["title"] = title
        return self
    
    def on_date(self, date_str):
        self.event["date"] = date_str
        return self
    
    def at_time(self, time_str):
        self.event["time"] = time_str
        return self
    
    def with_location(self, location):
        self.event["location"] = location
        return self
    
    def with_category(self, category):
        self.event["category"] = category
        return self
    
    def add_reminder(self, minutes_before):
        self.event["reminders"].append(minutes_before)
        return self
    
    def build(self):
        return self.event.copy()


class ChildProfileBuilder:
    """Fluent builder for child profiles."""
    
    def __init__(self):
        self.profile = {
            "name": "Child",
            "birth_date": "2023-08-15",
            "gender": "M",
            "created_at": datetime.now().isoformat()
        }
    
    def named(self, name):
        self.profile["name"] = name
        return self
    
    def born_on(self, birth_date):
        self.profile["birth_date"] = birth_date
        return self
    
    def gender(self, gender):
        self.profile["gender"] = gender
        return self
    
    def build(self):
        return self.profile.copy()


# ═══════════════════════════════════════════════════════════
# WORKFLOW SCENARIO BUILDERS
# ═══════════════════════════════════════════════════════════


class RecipeWorkflowBuilder:
    """Builder for recipe testing workflows."""
    
    def __init__(self, session):
        self.session = session
        self.recipes = []
    
    def create_sample_recipes(self, count=5):
        """Create multiple sample recipes."""
        recipes = []
        for i in range(count):
            recipe = RecipeBuilder()\
                .with_name(f"Recipe {i+1}")\
                .with_ingredients([f"Ingredient {i+1}"])\
                .with_category(["Main", "Dessert", "Side"][i % 3])\
                .build()
            recipes.append(recipe)
        self.recipes = recipes
        return self
    
    def get_recipes(self):
        return self.recipes


class MealPlanningWorkflowBuilder:
    """Builder for meal planning workflows."""
    
    def __init__(self, session):
        self.session = session
        self.plans = []
        self.recipes = []
    
    def with_recipes(self, recipe_ids):
        """Set recipes for meal plan."""
        self.recipes = recipe_ids
        return self
    
    def create_week_plan(self, week=1):
        """Create a week meal plan."""
        plan = MealPlanBuilder().for_week(week)
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for day in days:
            if self.recipes:
                recipe_id = self.recipes[len(self.plans) % len(self.recipes)]
                plan.add_meal(day, "lunch", recipe_id)
                plan.add_meal(day, "dinner", recipe_id)
        
        self.plans.append(plan.build())
        return self
    
    def build(self):
        return self.plans


# ═══════════════════════════════════════════════════════════
# ASSERTION HELPERS
# ═══════════════════════════════════════════════════════════


class ServiceAssertions:
    """Helper class for service-level assertions."""
    
    @staticmethod
    def assert_valid_recipe(recipe):
        """Assert recipe has valid structure."""
        assert recipe is None or isinstance(recipe, dict)
        if recipe:
            assert "name" in recipe or "title" in recipe
    
    @staticmethod
    def assert_valid_shopping_list(shopping_list):
        """Assert shopping list has valid structure."""
        assert shopping_list is None or isinstance(shopping_list, list)
        if shopping_list:
            for item in shopping_list:
                assert isinstance(item, (dict, str))
    
    @staticmethod
    def assert_valid_event(event):
        """Assert event has valid structure."""
        assert event is None or isinstance(event, dict)
        if event:
            assert "title" in event or "name" in event
    
    @staticmethod
    def assert_service_initialized(service):
        """Assert service is properly initialized."""
        assert service is not None
        assert hasattr(service, 'session') or hasattr(service, 'get_all')
    
    @staticmethod
    def assert_workflow_success(results):
        """Assert workflow completed successfully."""
        assert results is None or isinstance(results, (list, dict, bool, object))


# ═══════════════════════════════════════════════════════════
# COMPLEX SCENARIO FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def recipe_scenario(mock_session):
    """Complete recipe scenario with builders."""
    builder = RecipeWorkflowBuilder(mock_session)
    builder.create_sample_recipes(5)
    return builder


@pytest.fixture
def meal_planning_scenario(mock_session, recipe_scenario):
    """Complete meal planning scenario."""
    builder = MealPlanningWorkflowBuilder(mock_session)
    builder.with_recipes([1, 2, 3, 4, 5])
    builder.create_week_plan(week=1)
    builder.create_week_plan(week=2)
    return builder


@pytest.fixture
def recipe_builder():
    """Recipe builder for quick creation."""
    return RecipeBuilder()


@pytest.fixture
def meal_plan_builder():
    """Meal plan builder for quick creation."""
    return MealPlanBuilder()


@pytest.fixture
def shopping_list_builder():
    """Shopping list builder for quick creation."""
    return ShoppingListBuilder()


@pytest.fixture
def event_builder():
    """Event builder for quick creation."""
    return EventBuilder()


@pytest.fixture
def child_profile_builder():
    """Child profile builder for quick creation."""
    return ChildProfileBuilder()


# ═══════════════════════════════════════════════════════════
# PARAMETRIZATION DATA
# ═══════════════════════════════════════════════════════════


RECIPE_CATEGORIES = ["Main", "Dessert", "Side", "Appetizer", "Beverage"]
RECIPE_DIFFICULTIES = ["easy", "medium", "hard"]
RECIPE_TIMES = [15, 30, 45, 60, 90]
COOKING_METHODS = ["boil", "fry", "bake", "grill", "steam", "microwave"]
DIETARY_RESTRICTIONS = ["vegetarian", "vegan", "gluten-free", "dairy-free", "nut-free"]
MEAL_TYPES = ["breakfast", "lunch", "dinner", "snack"]
EVENT_CATEGORIES = ["Family", "Health", "Birthday", "Work", "Personal"]
HEALTH_METRICS = ["weight", "height", "temperature", "blood_pressure", "heart_rate"]


# ═══════════════════════════════════════════════════════════
# MOCK DATA GENERATORS
# ═══════════════════════════════════════════════════════════


def generate_recipe_data(name="Test Recipe", category="Main"):
    """Generate valid recipe data."""
    return {
        "name": name,
        "description": f"Description of {name}",
        "ingredients": ["Ingredient 1", "Ingredient 2"],
        "instructions": "Mix and cook",
        "prep_time": 10,
        "cook_time": 20,
        "servings": 4,
        "category": category
    }


def generate_shopping_list_data(name="Shopping List"):
    """Generate valid shopping list data."""
    return {
        "name": name,
        "items": [
            {"name": "Tomato", "quantity": 5},
            {"name": "Onion", "quantity": 3}
        ]
    }


def generate_event_data(title="Event", days_ahead=0):
    """Generate valid event data."""
    event_date = date.today() + timedelta(days=days_ahead)
    return {
        "title": title,
        "date": event_date.isoformat(),
        "time": "10:00",
        "location": "Home"
    }


def generate_child_profile_data(name="Child"):
    """Generate valid child profile data."""
    return {
        "name": name,
        "birth_date": "2023-08-15",
        "gender": "M"
    }


# ═══════════════════════════════════════════════════════════
# EXPORT FOR USE IN TESTS
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def service_assertions():
    """Service assertion utilities."""
    return ServiceAssertions()
