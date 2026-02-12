import importlib
import pytest

def test_import_calendrier_unifie_logic():
    module = importlib.import_module("src.domains.planning.logic.calendrier_unifie_logic")
    assert module is not None
