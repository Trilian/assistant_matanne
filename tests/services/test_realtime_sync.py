import importlib
import pytest

@pytest.mark.unit
def test_import_realtime_sync():
    module = importlib.import_module("src.services.realtime_sync")
    assert module is not None
