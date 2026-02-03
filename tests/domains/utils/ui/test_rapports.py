import importlib
import pytest

def test_import_rapports():
    module = importlib.import_module("src.domains.utils.ui.rapports")
    assert module is not None
