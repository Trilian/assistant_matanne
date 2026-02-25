import importlib

import pytest


@pytest.mark.parametrize(
    "module_path",
    [
        # Components
        "src.ui.components.alertes",
        "src.ui.components.atoms",
        "src.ui.components.charts",
        "src.ui.components.data",
        "src.ui.components.dynamic",
        "src.ui.components.forms",
        "src.ui.components.layouts",
        "src.ui.components.metrics",
        "src.ui.components.system",
        # Feedback
        "src.ui.feedback.progress_v2",
        "src.ui.feedback.spinners",
        "src.ui.feedback.toasts",
        # Layout
        "src.ui.layout.footer",
        "src.ui.layout.header",
        "src.ui.layout.initialisation",
        "src.ui.layout.styles",
        # Integrations
        "src.ui.integrations.google_calendar",
        # Tablet
        "src.ui.tablet",
        "src.ui.tablet.config",
        "src.ui.tablet.kitchen",
        "src.ui.tablet.styles",
        "src.ui.tablet.widgets",
        # Views
        "src.ui.views",
        "src.ui.views.authentification",
        "src.ui.views.historique",
        "src.ui.views.import_recettes",
        "src.ui.views.jeux",
        "src.ui.views.meteo",
        "src.ui.views.notifications",
        "src.ui.views.pwa",
        "src.ui.views.sauvegarde",
        "src.ui.views.synchronisation",
    ],
)
def test_import_ui_module(module_path):
    module = importlib.import_module(module_path)
    assert module is not None
