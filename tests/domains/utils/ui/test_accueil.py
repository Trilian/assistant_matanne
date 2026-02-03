import importlib
import pytest

def test_import_accueil():
    module = importlib.import_module("src.domains.utils.ui.accueil")
    assert module is not None
