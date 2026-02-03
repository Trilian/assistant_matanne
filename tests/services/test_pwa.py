import importlib
import pytest

@pytest.mark.unit
def test_import_pwa():
    module = importlib.import_module("src.services.pwa")
    assert module is not None
