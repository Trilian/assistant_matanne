import importlib
import pytest

def test_import_auth():
    module = importlib.import_module("src.services.auth")
    assert module is not None
