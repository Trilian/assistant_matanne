import pytest
import importlib

@pytest.mark.parametrize("module_path", [
    "src.domains.maison.ui.jardin_zones",
    "src.domains.maison.ui.scan_factures",
    "src.domains.maison.ui.projets",
    "src.domains.maison.ui.meubles",
    "src.domains.maison.ui.jardin",
    "src.domains.maison.ui.hub_maison",
    "src.domains.maison.ui.entretien",
    "src.domains.maison.ui.energie",
    "src.domains.maison.ui.eco_tips",
])
def test_import_maison_ui_module(module_path):
    module = importlib.import_module(module_path)
    assert module is not None
