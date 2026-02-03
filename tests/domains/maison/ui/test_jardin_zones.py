import importlib
import pytest

def test_import_jardin_zones():
    module = importlib.import_module("src.domains.maison.ui.jardin_zones")
    assert module is not None
