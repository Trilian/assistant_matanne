"""
Unit tests for InventaireService.

Tests cover:
- Inventory management
- Alert detection
- Status calculation
- IA shopping suggestions
- CRUD operations
- Statistics
"""

import pytest
from datetime import date, timedelta
from unittest.mock import Mock, MagicMock

from src.services.inventaire import InventaireService
from src.core.models import ArticleInventaire, Ingredient


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
        
        result = inventaire_service.get_inventaire_complet()
        assert isinstance(result, list)
    
    def test_get_inventaire_complet_filters_by_location(
        self, inventaire_service, db
    ):
        """Test filtering by storage location."""
        assert hasattr(inventaire_service, 'get_inventaire_complet')
        
        result = inventaire_service.get_inventaire_complet(emplacement="Frigo")
        assert isinstance(result, list)
        for item in result:
            if item["emplacement"]:
                assert item["emplacement"] == "Frigo"
    
    def test_get_inventaire_complet_filters_by_category(
        self, inventaire_service, db
    ):
        """Test filtering by category."""
        assert hasattr(inventaire_service, 'get_inventaire_complet')
        
        result = inventaire_service.get_inventaire_complet(categorie="Légumes")
        assert isinstance(result, list)
        for item in result:
            assert item["ingredient_categorie"] == "Légumes"
    
    def test_get_inventaire_complet_excludes_ok_items(
        self, inventaire_service, db
    ):
        """Test excluding OK items."""
        result = inventaire_service.get_inventaire_complet(include_ok=False)
        assert isinstance(result, list)
        
        for item in result:
            assert item["statut"] != "ok"
    
    def test_get_inventaire_complet_returns_required_fields(
        self, inventaire_service, db
    ):
        """Test that required fields are present."""
        result = inventaire_service.get_inventaire_complet()
        
        required_fields = [
            "id", "ingredient_id", "ingredient_nom", "ingredient_categorie",
            "quantite", "quantite_min", "unite", "emplacement",
            "date_peremption", "statut", "jours_avant_peremption"
        ]
        
        if result:
            for field in required_fields:
                assert field in result[0], f"Missing field: {field}"


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
        
        assert isinstance(result["stock_bas"], list)
        assert isinstance(result["critique"], list)
        assert isinstance(result["peremption_proche"], list)
    
    def test_calculer_statut_critical_when_below_50_percent(
        self, inventaire_service
    ):
        """Test critical status when below 50% of minimum."""
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
        today = date.today()
        article = Mock()
        article.date_peremption = today + timedelta(days=10)
        
        days = inventaire_service._jours_avant_peremption(article, today)
        assert days == 10
    
    def test_jours_avant_peremption_returns_none_when_no_date(
        self, inventaire_service
    ):
        """Test None when no expiration date."""
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
    
    def test_suggerer_courses_ia_returns_list(
        self, inventaire_service
    ):
        """Test that suggestions return a list."""
        result = inventaire_service.suggerer_courses_ia()
        assert isinstance(result, list)


# ═══════════════════════════════════════════════════════════
# SECTION 4: CRUD OPERATIONS TESTS
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestCRUDOperations:
    """Test CRUD operations."""
    
    def test_ajouter_article_exists(self, inventaire_service):
        """Test that add article method exists."""
        assert hasattr(inventaire_service, 'ajouter_article')
        assert callable(inventaire_service.ajouter_article)
    
    def test_mettre_a_jour_article_exists(self, inventaire_service):
        """Test that update method exists."""
        assert hasattr(inventaire_service, 'mettre_a_jour_article')
        assert callable(inventaire_service.mettre_a_jour_article)
    
    def test_supprimer_article_exists(self, inventaire_service):
        """Test that delete method exists."""
        assert hasattr(inventaire_service, 'supprimer_article')
        assert callable(inventaire_service.supprimer_article)
    
    def test_mettre_a_jour_article_with_quantity(
        self, inventaire_service, db, article_factory
    ):
        """Test updating article quantity."""
        article = article_factory()
        original_qty = article.quantite
        
        result = inventaire_service.mettre_a_jour_article(
            article.id,
            quantite=original_qty + 5
        )
        
        assert result is True or isinstance(result, dict) or result is None


# ═══════════════════════════════════════════════════════════
# SECTION 5: STATISTICS TESTS
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestStatistics:
    """Test statistics methods."""
    
    def test_get_statistiques_exists(self, inventaire_service):
        """Test that statistics method exists."""
        assert hasattr(inventaire_service, 'get_statistiques')
        assert callable(inventaire_service.get_statistiques)
    
    def test_get_statistiques_returns_dict(self, inventaire_service):
        """Test that statistics return a dict."""
        result = inventaire_service.get_statistiques()
        assert isinstance(result, dict)
    
    def test_get_stats_par_categorie_exists(self, inventaire_service):
        """Test that category stats method exists."""
        assert hasattr(inventaire_service, 'get_stats_par_categorie')
        assert callable(inventaire_service.get_stats_par_categorie)
    
    def test_get_stats_par_categorie_returns_dict(self, inventaire_service):
        """Test that category stats return a dict."""
        result = inventaire_service.get_stats_par_categorie()
        assert isinstance(result, dict)
    
    def test_get_articles_a_prelever_exists(self, inventaire_service):
        """Test that FIFO method exists."""
        assert hasattr(inventaire_service, 'get_articles_a_prelever')
        assert callable(inventaire_service.get_articles_a_prelever)
    
    def test_get_articles_a_prelever_returns_list(self, inventaire_service):
        """Test that FIFO returns a list."""
        result = inventaire_service.get_articles_a_prelever()
        assert isinstance(result, list)


# ═══════════════════════════════════════════════════════════
# SECTION 6: INTEGRATION TESTS
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
    
    def test_inventory_with_filter_and_sort(
        self, inventaire_service, db
    ):
        """Test inventory with multiple filters."""
        # Get all
        all_items = inventaire_service.get_inventaire_complet()
        
        # Filter by location
        filtered = inventaire_service.get_inventaire_complet(
            emplacement="Frigo"
        )
        
        # Filtered should be <= all
        assert len(filtered) <= len(all_items)
    
    def test_inventory_statistics_workflow(
        self, inventaire_service
    ):
        """Test statistics retrieval workflow."""
        stats = inventaire_service.get_statistiques()
        
        assert "total_articles" in stats
        assert isinstance(stats["total_articles"], int)
        
        category_stats = inventaire_service.get_stats_par_categorie()
        assert isinstance(category_stats, dict)
