import importlib
import pytest

def test_import_inventaire():
    module = importlib.import_module("src.services.inventaire")
    assert module is not None
