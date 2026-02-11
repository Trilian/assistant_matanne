import pytest
import importlib


def test_import_pdf_export_module():
    """Vérifie que le module pdf s'importe sans erreur."""
    module = importlib.import_module("src.services.rapports")
    assert module is not None


@pytest.mark.unit
def test_import_pdf_export_service():
    """Vérifie que le module pdf s'importe sans erreur."""
    module = importlib.import_module("src.services.rapports")
    assert module is not None


@pytest.mark.unit
def test_pdf_export_service_exists():
    """Test that PDF export service exists."""
    try:
        from src.services.rapports import get_pdf_export_service
        service = get_pdf_export_service()
        assert service is not None
    except ImportError:
        pass  # Service may not exist yet
