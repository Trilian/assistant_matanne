"""
Test minimal d'import pour src/modules/maison/__init__.py
"""


def test_import_maison_init():
    import src.modules.maison

    assert hasattr(src.modules, "maison")
