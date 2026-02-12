"""
Test minimal d'import pour src/domains/famille/__init__.py
"""
def test_import_famille_init():
    import src.domains.famille
    assert hasattr(src.domains, "famille")
