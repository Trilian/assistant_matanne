def test_import_projets_ui():
    import src.domains.maison.ui.projets
import importlib
import pytest

def test_import_projets():
    module = importlib.import_module("src.domains.maison.ui.projets")
    assert module is not None
