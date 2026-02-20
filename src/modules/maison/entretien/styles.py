"""Entretien - Styles CSS du module."""

from src.ui.css import charger_css


def injecter_css_entretien() -> None:
    """Injecte les styles CSS du module entretien."""
    charger_css("entretien.css")


ENTRETIEN_CSS = ""  # Deprecated: use injecter_css_entretien()
