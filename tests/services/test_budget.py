import importlib
import pytest

def test_import_budget():
    module = importlib.import_module("src.services.budget")
    assert module is not None
