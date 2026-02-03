import importlib
import pytest

def test_import_batch_cooking():
    module = importlib.import_module("src.services.batch_cooking")
    assert module is not None
