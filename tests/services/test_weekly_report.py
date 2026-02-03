import importlib
import pytest

@pytest.mark.unit
def test_import_weekly_report():
    module = importlib.import_module("src.services.weekly_report")
    assert module is not None
