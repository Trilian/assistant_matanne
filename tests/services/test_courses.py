import importlib
import pytest

def test_import_courses():
    module = importlib.import_module("src.services.courses")
    assert module is not None
