"""
Test minimal d'import pour src/modules/cuisine/__init__.py
"""
def test_import_cuisine_init():
    import src.modules.cuisine
    assert hasattr(src.modules, "cuisine")
