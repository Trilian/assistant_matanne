def test_import_calendrier_unifie_ui():
    import src.domains.planning.ui.calendrier_unifie
import importlib
import pytest

def test_import_calendrier_unifie():
    module = importlib.import_module("src.domains.planning.ui.calendrier_unifie")
    assert module is not None
