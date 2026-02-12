"""
Test minimal d'import pour src/modules/famille/__init__.py
"""
def test_import_famille_init():
    import src.modules.famille
    assert hasattr(src.modules, "famille")
