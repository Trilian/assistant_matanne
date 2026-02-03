import importlib
import pytest

@pytest.mark.unit
def test_import_users():
    module = importlib.import_module("src.services.users")
    assert module is not None
