import importlib
import pytest

def test_import_calendar_sync():
    module = importlib.import_module("src.services.calendar_sync")
    assert module is not None
