def test_import_models():
    import importlib

    mod = importlib.import_module("src.core.models")
    assert mod is not None
