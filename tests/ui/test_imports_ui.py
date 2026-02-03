import pytest
import importlib

@pytest.mark.parametrize("module_path", [
    "src.ui.components.atoms",
    "src.ui.components.camera_scanner",
    "src.ui.components.dashboard_widgets",
    "src.ui.components.data",
    "src.ui.components.dynamic",
    "src.ui.components.forms",
    "src.ui.components.google_calendar_sync",
    "src.ui.components.layouts",
    "src.ui.core.base_form",
    "src.ui.core.base_io",
    "src.ui.core.base_module",
    "src.ui.domain",
    "src.ui.feedback.progress",
    "src.ui.feedback.spinners",
    "src.ui.feedback.toasts",
    "src.ui.layout.footer",
    "src.ui.layout.header",
    "src.ui.layout.sidebar",
    "src.ui.layout.init",
    "src.ui.layout.styles",
    "src.ui.tablet_mode",
])
def test_import_ui_module(module_path):
    module = importlib.import_module(module_path)
    assert module is not None
