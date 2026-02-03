import importlib
import pytest

def test_import_calendrier_unifie():
    module = importlib.import_module("src.domains.planning.ui.calendrier_unifie")
    assert module is not None
