def test_import_scan_factures_ui():
    import src.domains.maison.ui.scan_factures
import importlib
import pytest

def test_import_scan_factures():
    module = importlib.import_module("src.domains.maison.ui.scan_factures")
    assert module is not None
