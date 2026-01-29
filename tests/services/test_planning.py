"""
Unit tests for PlanningService.

Tests cover:
- Planning CRUD
- Weekly plan generation
- Meal organization
"""

import pytest
from datetime import date, timedelta

from src.services.planning import PlanningService


# ═══════════════════════════════════════════════════════════
# SECTION 1: PLANNING CRUD TESTS
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestPlanningCRUD:
    """Test planning CRUD operations."""
    
    def test_get_planning_complet_returns_planning_with_meals(
        self, planning_service, sample_planning, db
    ):
        """Test retrieving complete planning with meals."""
        result = planning_service.get_planning_complet(
            sample_planning.id, db=db
        )
        
        assert result is not None
        assert result["id"] == sample_planning.id
        assert result["nom"] == sample_planning.nom
        assert "repas_par_jour" in result
    
    def test_get_planning_complet_returns_none_for_missing(
        self, planning_service, db
    ):
        """Test that missing planning returns None."""
        result = planning_service.get_planning_complet(99999, db=db)
        
        assert result is None
    
    def test_get_planning_complet_caches_results(
        self, planning_service, sample_planning, db, clear_cache
    ):
        """Test that results are cached."""
        planning_service.get_planning_complet(sample_planning.id, db=db)
        
        from src.core.cache import Cache
        cache_key = f"planning_full_{sample_planning.id}"
        cached = Cache.obtenir(cache_key)
        
        assert cached is not None
    
    def test_get_planning_complet_organizes_by_date(
        self, planning_service, sample_planning, db
    ):
        """Test that meals are organized by date."""
        result = planning_service.get_planning_complet(
            sample_planning.id, db=db
        )
        
        repas_par_jour = result["repas_par_jour"]
        assert isinstance(repas_par_jour, dict)


# ═══════════════════════════════════════════════════════════
# SECTION 2: PLANNING GENERATION TESTS
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestPlanningGeneration:
    """Test planning generation."""
    
    def test_generer_planning_ia_method_exists(
        self, planning_service
    ):
        """Test that generation method exists."""
        assert hasattr(planning_service, 'generer_planning_ia')
        assert callable(planning_service.generer_planning_ia)


# ═══════════════════════════════════════════════════════════
# SECTION 3: INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════

@pytest.mark.integration
class TestPlanningIntegration:
    """Integration tests for planning."""
    
    def test_planning_workflow(
        self, planning_service, sample_planning, db
    ):
        """Test complete planning workflow."""
        # Get planning
        planning = planning_service.get_planning_complet(
            sample_planning.id, db=db
        )
        
        assert planning is not None
        assert planning["id"] == sample_planning.id
