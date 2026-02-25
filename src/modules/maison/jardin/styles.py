"""Styles CSS pour le module Jardin."""

from src.ui.engine import charger_css


def injecter_css_jardin() -> None:
    """Injecte les styles CSS du module jardin."""
    charger_css("jardin.css")
