def test_import_vue_semaine_ui():
    import src.domains.planning.ui.vue_semaine
import importlib
import pytest

def test_import_vue_semaine():
    module = importlib.import_module("src.domains.planning.ui.vue_semaine")
    assert module is not None
