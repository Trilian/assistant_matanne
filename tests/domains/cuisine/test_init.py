"""
Test minimal d'import pour src/domains/cuisine/__init__.py
"""
def test_import_cuisine_init():
    import src.domains.cuisine
    assert hasattr(src.domains, "cuisine")
