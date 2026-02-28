"""Maison - Styles CSS."""

from src.ui.engine import charger_css


def injecter_css_hub() -> None:
    """Injecte les styles CSS de la Maison."""
    charger_css("hub_maison.css")
