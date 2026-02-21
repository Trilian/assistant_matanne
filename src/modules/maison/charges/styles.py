"""Charges - Styles CSS du module."""

from src.ui.engine import charger_css


def injecter_css_charges() -> None:
    """Injecte les styles CSS du module charges."""
    charger_css("charges.css")


CHARGES_CSS = ""  # Deprecated: use injecter_css_charges()
