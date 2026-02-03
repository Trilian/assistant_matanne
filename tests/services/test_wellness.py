import importlib
import pytest

def test_import_wellness():
    module = importlib.import_module("src.services.wellness")
    assert module is not None
