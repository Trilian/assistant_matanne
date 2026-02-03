import importlib
import pytest

def test_import_user_preferences():
    module = importlib.import_module("src.services.user_preferences")
    assert module is not None
