import importlib
import pytest

def test_import_wellness_utils():
    module = importlib.import_module("src.services.wellness_utils")
    assert module is not None
