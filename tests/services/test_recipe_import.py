import importlib
import pytest

def test_import_recipe_import():
    module = importlib.import_module("src.services.recipe_import")
    assert module is not None
