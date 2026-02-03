import importlib
import pytest

def test_import_barcode():
    module = importlib.import_module("src.domains.utils.ui.barcode")
    assert module is not None
