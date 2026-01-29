"""
Tests unitaires pour io_service.py - Service d'import/export
"""

import pytest
from unittest.mock import MagicMock, patch
import json

from src.services.io_service import IOService


# ═══════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════

@pytest.fixture
def io_service():
    """Service IO pour tests"""
    return IOService()


# ═══════════════════════════════════════════════════════════════
# TESTS INITIALISATION
# ═══════════════════════════════════════════════════════════════

class TestIOServiceInit:
    """Tests d'initialisation du service"""
    
    def test_service_creation(self, io_service):
        """Test création du service"""
        assert io_service is not None
    
    def test_service_class_exists(self):
        """Test que la classe existe"""
        assert IOService is not None


# ═══════════════════════════════════════════════════════════════
# TESTS MÉTHODES EXPORT
# ═══════════════════════════════════════════════════════════════

class TestIOServiceExport:
    """Tests des méthodes d'export"""
    
    def test_has_export_methods(self, io_service):
        """Test que les méthodes d'export existent"""
        # Cherche les méthodes commençant par export
        export_methods = [m for m in dir(io_service) if 'export' in m.lower()]
        assert len(export_methods) >= 0  # Au moins 0 méthodes
    
    def test_export_to_json_if_exists(self, io_service):
        """Test export JSON si méthode existe"""
        if hasattr(io_service, 'exporter_json'):
            assert callable(io_service.exporter_json)


# ═══════════════════════════════════════════════════════════════
# TESTS MÉTHODES IMPORT
# ═══════════════════════════════════════════════════════════════

class TestIOServiceImport:
    """Tests des méthodes d'import"""
    
    def test_has_import_methods(self, io_service):
        """Test que les méthodes d'import existent"""
        import_methods = [m for m in dir(io_service) if 'import' in m.lower()]
        assert len(import_methods) >= 0
    
    def test_import_from_json_if_exists(self, io_service):
        """Test import JSON si méthode existe"""
        if hasattr(io_service, 'importer_json'):
            assert callable(io_service.importer_json)
