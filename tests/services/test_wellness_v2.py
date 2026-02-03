import importlib
import pytest

def test_import_wellness_v2():
    module = importlib.import_module("src.services.wellness_v2")
    assert module is not None
