def test_import_notifications_push_ui():
    import src.domains.utils.ui.notifications_push
import importlib
import pytest

def test_import_notifications_push():
    module = importlib.import_module("src.domains.utils.ui.notifications_push")
    assert module is not None
