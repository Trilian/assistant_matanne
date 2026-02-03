import pytest
import importlib

@pytest.mark.parametrize("module_path", [
    "src.domains.planning.ui.vue_semaine",
    "src.domains.planning.ui.vue_ensemble",
    "src.domains.planning.ui.calendrier_unifie",
])
def test_import_planning_ui_module(module_path):
    module = importlib.import_module(module_path)
    assert module is not None
