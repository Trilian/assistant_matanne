import importlib
import pytest

@pytest.mark.unit
def test_import_rapports_pdf():
    module = importlib.import_module("src.services.rapports_pdf")
    assert module is not None
