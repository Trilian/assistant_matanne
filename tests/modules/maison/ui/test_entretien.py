def test_import_entretien_ui():
    import src.domains.maison.ui.entretien
import importlib
import pytest

def test_import_entretien():
    module = importlib.import_module("src.domains.maison.ui.entretien")
    assert module is not None
