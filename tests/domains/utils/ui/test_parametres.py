def test_import_parametres_ui():
    import src.domains.utils.ui.parametres
import importlib
import pytest

def test_import_parametres():
    module = importlib.import_module("src.domains.utils.ui.parametres")
    assert module is not None
