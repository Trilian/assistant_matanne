"""
Test minimal d'import pour src/modules/__init__.py
"""
def test_import_domains_init():
    import src.modules
    assert hasattr(src.modules, "cuisine")
