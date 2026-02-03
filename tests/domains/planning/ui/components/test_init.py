"""
Test minimal d'import pour src/domains/planning/ui/components/__init__.py
"""
def test_import_planning_ui_components_init():
    import src.domains.planning.ui.components
    assert hasattr(src.domains.planning.ui, "components")
