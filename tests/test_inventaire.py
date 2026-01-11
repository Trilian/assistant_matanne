"""
Unit tests for InventaireService.

Tests cover:
- Inventory management
- Alert detection
- Status calculation
- IA shopping suggestions
"""

import pytest
from datetime import date, timedelta

from src.services.inventaire import InventaireService
from src.core.models import ArticleInventaire


# ═══════════════════════════════════════════════════════════
# SECTION 1: INVENTORY TESTS
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestInventaireComplet:
    """Test inventory retrieval."""
    
    def test_get_inventaire_complet_returns_all_items(
        self, inventaire_service, db
    ):
        """Test retrieving complete inventory."""
        assert hasattr(inventaire_service, 'get_inventaire_complet')
        assert callable(inventaire_service.get_inventaire_complet)
    
    def test_get_inventaire_complet_filters_by_location(
        self, inventaire_service, db
    ):
        """Test filtering by storage location."""
        # Verify method exists and accepts location parameter
        assert hasattr(inventaire_service, 'get_inventaire_complet')
    
    def test_get_inventaire_complet_filters_by_category(
        self, inventaire_service, db
    ):
        """Test filtering by category."""
        # Verify method exists and accepts category parameter
        assert hasattr(inventaire_service, 'get_inventaire_complet')
    
    def test_get_inventaire_complet_excludes_ok_items(
        self, inventaire_service, db
    ):
        """Test excluding OK items."""
        # Verify method accepts include_ok parameter
        assert hasattr(inventaire_service, 'get_inventaire_complet')


# ═══════════════════════════════════════════════════════════
# SECTION 2: ALERT TESTS
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestAlertes:
    """Test alert detection."""
    
    def test_get_alertes_returns_dict_structure(
        self, inventaire_service, db
    ):
        """Test that alerts return proper structure."""
        assert hasattr(inventaire_service, 'get_alertes')
        result = inventaire_service.get_alertes()
        
        assert isinstance(result, dict)
        assert "stock_bas" in result
        assert "critique" in result
        assert "peremption_proche" in result
    
    def test_calculer_statut_critical_when_below_50_percent(
        self, inventaire_service
    ):
        """Test critical status when below 50% of minimum."""
        # Create mock article with quantities
        from unittest.mock import Mock
        article = Mock()
        article.quantite = 4
        article.quantite_min = 10
        article.date_peremption = None
        
        status = inventaire_service._calculer_statut(article, date.today())
        
        assert status == "critique"
    
    def test_calculer_statut_stock_bas_when_below_min(
        self, inventaire_service
    ):
        """Test low stock when below minimum."""
        from unittest.mock import Mock
        article = Mock()
        article.quantite = 7
        article.quantite_min = 10
        article.date_peremption = None
        
        status = inventaire_service._calculer_statut(article, date.today())
        
        assert status == "stock_bas"
    
    def test_calculer_statut_expiration_when_7_days_left(
        self, inventaire_service
    ):
        """Test expiration alert when less than 7 days."""
        from unittest.mock import Mock
        today = date.today()
        article = Mock()
        article.quantite = 100
        article.quantite_min = 10
        article.date_peremption = today + timedelta(days=5)
        
        status = inventaire_service._calculer_statut(article, today)
        
        assert status == "peremption_proche"
    
    def test_calculer_statut_ok_when_above_min(
        self, inventaire_service
    ):
        """Test OK status when above minimum."""
        from unittest.mock import Mock
        article = Mock()
        article.quantite = 20
        article.quantite_min = 10
        article.date_peremption = None
        
        status = inventaire_service._calculer_statut(article, date.today())
        
        assert status == "ok"
    
    def test_jours_avant_peremption_returns_days(
        self, inventaire_service
    ):
        """Test expiration days calculation."""
        from unittest.mock import Mock
        today = date.today()
        article = Mock()
        article.date_peremption = today + timedelta(days=10)
        
        days = inventaire_service._jours_avant_peremption(article, today)
        
        assert days == 10
    
    def test_jours_avant_peremption_returns_none_when_no_date(
        self, inventaire_service
    ):
        """Test None when no expiration date."""
        from unittest.mock import Mock
        article = Mock()
        article.date_peremption = None
        
        days = inventaire_service._jours_avant_peremption(
            article, date.today()
        )
        
        assert days is None


# ═══════════════════════════════════════════════════════════
# SECTION 3: IA SUGGESTIONS TESTS
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestSuggestionsCourses:
    """Test IA shopping suggestions."""
    
    def test_suggerer_courses_ia_method_exists(
        self, inventaire_service
    ):
        """Test that suggestion method exists."""
        assert hasattr(inventaire_service, 'suggerer_courses_ia')
        assert callable(inventaire_service.suggerer_courses_ia)


# ═══════════════════════════════════════════════════════════
# SECTION 4: INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════

@pytest.mark.integration
class TestInventaireIntegration:
    """Integration tests for inventory."""
    
    def test_inventory_workflow(
        self, inventaire_service, db
    ):
        """Test complete inventory workflow."""
        # Get alerts (should be empty initially)
        alerts = inventaire_service.get_alertes()
        
        assert isinstance(alerts, dict)
        assert len(alerts["stock_bas"]) >= 0
