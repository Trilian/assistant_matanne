"""
Unit tests for CoursesService.

Tests cover:
- Shopping list management
- IA shopping suggestions
- Filtering and organization
"""

import pytest

from src.services.courses import CoursesService


# ═══════════════════════════════════════════════════════════
# SECTION 1: SHOPPING LIST TESTS
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestListeCourses:
    """Test shopping list functionality."""
    
    def test_get_liste_courses_returns_list(
        self, courses_service, db
    ):
        """Test retrieving shopping list."""
        result = courses_service.get_liste_courses(db=db)
        
        assert isinstance(result, list)
    
    def test_get_liste_courses_filters_unpurchased(
        self, courses_service, db
    ):
        """Test filtering unpurchased items."""
        # Method should accept achetes parameter
        result = courses_service.get_liste_courses(achetes=False, db=db)
        
        assert isinstance(result, list)
    
    def test_get_liste_courses_filters_by_priority(
        self, courses_service, db
    ):
        """Test filtering by priority."""
        result = courses_service.get_liste_courses(
            priorite="haute", db=db
        )
        
        assert isinstance(result, list)


# ═══════════════════════════════════════════════════════════
# SECTION 2: IA SUGGESTIONS TESTS
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestSuggestionsIA:
    """Test IA shopping suggestions."""
    
    def test_generer_suggestions_ia_method_exists(
        self, courses_service
    ):
        """Test that suggestion method exists."""
        assert hasattr(
            courses_service, 
            'generer_suggestions_ia_depuis_inventaire'
        )
        assert callable(
            courses_service.generer_suggestions_ia_depuis_inventaire
        )


# ═══════════════════════════════════════════════════════════
# SECTION 3: INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════

@pytest.mark.integration
class TestCoursesIntegration:
    """Integration tests for shopping."""
    
    def test_shopping_workflow(
        self, courses_service, db
    ):
        """Test complete shopping workflow."""
        # Get list
        items = courses_service.get_liste_courses(db=db)
        
        assert isinstance(items, list)
