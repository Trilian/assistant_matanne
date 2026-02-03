"""
TIER-1 SERVICE IMPORTS AND INSTANTIATION TESTS
Tests that verify services can be imported and instantiated
Simple pattern: create service, verify it works
"""

import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session

# ==============================================================================
# TESTS: SERVICE IMPORTS
# ==============================================================================

class TestServiceImports:
    """Test all service imports"""
    
    def test_import_auth_service(self):
        """Test importing auth service"""
        from src.services.auth import AuthService
        assert AuthService is not None
    
    def test_import_backup_service(self):
        """Test importing backup service"""
        from src.services.backup import BackupService
        assert BackupService is not None
    
    def test_import_budget_service(self):
        """Test importing budget service"""
        from src.services.budget import BudgetService
        assert BudgetService is not None
    
    def test_import_recettes_service(self):
        """Test importing recipes service"""
        from src.services.recettes import RecetteService
        assert RecetteService is not None
    
    def test_import_courses_service(self):
        """Test importing shopping service"""
        from src.services.courses import CoursesService
        assert CoursesService is not None
    
    def test_import_planning_service(self):
        """Test importing planning service"""
        from src.services.planning import PlanningService
        assert PlanningService is not None
    
    def test_import_inventaire_service(self):
        """Test importing inventory service"""
        from src.services.inventaire import InventaireService
        assert InventaireService is not None
    
    def test_import_barcode_service(self):
        """Test importing barcode service"""
        from src.services.barcode import BarcodeService
        assert BarcodeService is not None


class TestServiceBasicInstantiation:
    """Test basic service instantiation"""
    
    def test_backup_service_creation(self):
        """Test creating backup service"""
        from src.services.backup import BackupService
        service = BackupService()
        assert service is not None
    
    def test_budget_service_creation(self):
        """Test creating budget service"""
        from src.services.budget import BudgetService
        service = BudgetService()
        assert service is not None
    
    def test_auth_service_creation(self):
        """Test creating auth service"""
        from src.services.auth import AuthService
        service = AuthService()
        assert service is not None
    
    def test_barcode_service_creation(self):
        """Test creating barcode service"""
        from src.services.barcode import BarcodeService
        service = BarcodeService()
        assert service is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
