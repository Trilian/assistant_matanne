import pytest
import importlib

@pytest.mark.parametrize("module_path", [
    "src.domains.utils.ui.barcode",
    "src.domains.utils.ui.accueil",
    "src.domains.utils.ui.notifications_push",
    "src.domains.utils.ui.rapports",
    "src.domains.utils.ui.parametres",
])
def test_import_utils_ui_module(module_path):
    module = importlib.import_module(module_path)
    assert module is not None
