import importlib
import pytest

def test_import_wellness_v3():
    module = importlib.import_module("src.services.wellness_v3")
    assert module is not None
