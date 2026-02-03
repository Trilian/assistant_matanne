import importlib
import pytest

def test_import_barcode():
    module = importlib.import_module("src.services.barcode")
    assert module is not None
