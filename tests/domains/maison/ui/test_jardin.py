import importlib
import pytest

def test_import_jardin():
    module = importlib.import_module("src.domains.maison.ui.jardin")
    assert module is not None
