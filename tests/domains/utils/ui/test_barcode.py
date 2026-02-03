def test_import_barcode_ui():
    import src.domains.utils.ui.barcode
import importlib
import pytest

def test_import_barcode():
    module = importlib.import_module("src.domains.utils.ui.barcode")
    assert module is not None
