"""
Test minimal d'import pour src/domains/__init__.py
"""
def test_import_domains_init():
    import src.domains
    assert hasattr(src, "domains")
