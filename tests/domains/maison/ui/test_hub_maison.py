def test_import_hub_maison_ui():
    import src.domains.maison.ui.hub_maison
import importlib
import pytest

def test_import_hub_maison():
    module = importlib.import_module("src.domains.maison.ui.hub_maison")
    assert module is not None
