import importlib
import pytest

def test_import_notifications():
    module = importlib.import_module("src.services.notifications")
    assert module is not None
