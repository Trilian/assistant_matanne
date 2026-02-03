"""
Test minimal d'import pour src/domains/maison/__init__.py
"""
def test_import_maison_init():
    import src.domains.maison
    assert hasattr(src.domains, "maison")
