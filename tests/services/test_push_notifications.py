import importlib
import pytest

def test_import_push_notifications():
    module = importlib.import_module("src.services.push_notifications")
    assert module is not None
