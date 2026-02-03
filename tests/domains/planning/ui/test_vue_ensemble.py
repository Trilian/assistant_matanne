def test_import_vue_ensemble_ui():
    import src.domains.planning.ui.vue_ensemble
import importlib
import pytest

def test_import_vue_ensemble():
    module = importlib.import_module("src.domains.planning.ui.vue_ensemble")
    assert module is not None
