import importlib
import pytest

def test_import_eco_tips():
    module = importlib.import_module("src.domains.maison.ui.eco_tips")
    assert module is not None
