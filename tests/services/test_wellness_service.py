import importlib
import pytest

def test_import_wellness():
    module = importlib.import_module("src.services.wellness")
    assert module is not None

def test_import_wellness_sync():
    module = importlib.import_module("src.services.wellness_sync")
    assert module is not None

def test_import_wellness_utils():
    module = importlib.import_module("src.services.wellness_utils")
    assert module is not None

def test_import_wellness_v2():
    module = importlib.import_module("src.services.wellness_v2")
    assert module is not None

def test_import_wellness_v3():
    module = importlib.import_module("src.services.wellness_v3")
    assert module is not None
