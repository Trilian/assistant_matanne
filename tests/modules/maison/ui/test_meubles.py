def test_import_meubles_ui():
    import src.domains.maison.ui.meubles
import importlib
import pytest

def test_import_meubles():
    module = importlib.import_module("src.domains.maison.ui.meubles")
    assert module is not None
