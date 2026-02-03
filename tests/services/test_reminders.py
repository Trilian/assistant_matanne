import importlib
import pytest

@pytest.mark.unit
def test_import_reminders():
    module = importlib.import_module("src.services.reminders")
    assert module is not None
