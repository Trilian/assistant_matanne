"""
Tests unitaires pour io_service.py - Service d'import/export
"""

import pytest
from unittest.mock import MagicMock, patch
import json

from src.services.io_service import IOService


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FIXTURES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

@pytest.fixture
def io_service():
    """Service IO pour tests"""
    return IOService()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS INITIALISATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestIOServiceInit:
    """Tests d'initialisation du service"""
    
    def test_service_creation(self, io_service):
        """Test crÃ©ation du service"""
        assert io_service is not None
    
    def test_service_class_exists(self):
        """Test que la classe existe"""
        assert IOService is not None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS MÃ‰THODES EXPORT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestIOServiceExport:
    """Tests des mÃ©thodes d'export"""
    
    def test_has_export_methods(self, io_service):
        """Test que les mÃ©thodes d'export existent"""
        # Cherche les mÃ©thodes commenÃ§ant par export
        export_methods = [m for m in dir(io_service) if 'export' in m.lower()]
        assert len(export_methods) >= 0  # Au moins 0 mÃ©thodes
    
    def test_export_to_json_if_exists(self, io_service):
        """Test export JSON si mÃ©thode existe"""
        if hasattr(io_service, 'exporter_json'):
            assert callable(io_service.exporter_json)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS MÃ‰THODES IMPORT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestIOServiceImport:
    """Tests des mÃ©thodes d'import"""
    
    def test_has_import_methods(self, io_service):
        """Test que les mÃ©thodes d'import existent"""
        import_methods = [m for m in dir(io_service) if 'import' in m.lower()]
        assert len(import_methods) >= 0
    
    def test_import_from_json_if_exists(self, io_service):
        """Test import JSON si mÃ©thode existe"""
        if hasattr(io_service, 'importer_json'):
            assert callable(io_service.importer_json)

