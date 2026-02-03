import importlib
import pytest

@pytest.mark.unit
def test_import_telegram():
    module = importlib.import_module("src.services.telegram")
    assert module is not None
