import importlib
import pytest

def test_import_recettes():
    module = importlib.import_module("src.services.recettes")
    assert module is not None
