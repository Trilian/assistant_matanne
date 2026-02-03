def test_import_pdf_export_module():
    """Vérifie que le module pdf_export s'importe sans erreur."""
    import importlib
    module = importlib.import_module("src.services.pdf_export")
    assert module is not None

@pytest.mark.unit
def test_import_pdf_export_service():
    """Vérifie que le module pdf_export s'importe sans erreur."""
    module = importlib.import_module("src.services.pdf_export")
    assert module is not None

# Ajoutez ici des tests pour les fonctions principales du service
