def test_import_energie_ui():
    import src.domains.maison.ui.energie
import importlib
import pytest

def test_import_energie():
    module = importlib.import_module("src.domains.maison.ui.energie")
    assert module is not None
