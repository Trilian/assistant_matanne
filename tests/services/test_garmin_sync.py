import importlib
import pytest

def test_import_garmin_sync():
    module = importlib.import_module("src.services.garmin_sync")
    assert module is not None
