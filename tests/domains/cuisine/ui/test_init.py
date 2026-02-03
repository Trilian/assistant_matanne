"""
Test minimal d'import pour src/domains/cuisine/ui/__init__.py
"""
def test_import_cuisine_ui_init():
    import src.domains.cuisine.ui
    assert hasattr(src.domains.cuisine, "ui")
