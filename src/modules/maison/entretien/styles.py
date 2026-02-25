"""Entretien - Styles CSS du module."""

from src.ui.engine import charger_css


def injecter_css_entretien() -> None:
    """Injecte les styles CSS du module entretien."""
    charger_css("entretien.css")
