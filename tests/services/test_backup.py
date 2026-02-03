import importlib
import pytest

def test_import_backup():
    module = importlib.import_module("src.services.backup")
    assert module is not None
