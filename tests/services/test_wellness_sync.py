import importlib
import pytest

def test_import_wellness_sync():
    module = importlib.import_module("src.services.wellness_sync")
    assert module is not None
