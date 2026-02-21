"""Hub Maison - Styles CSS."""

from src.ui.engine import charger_css


def injecter_css_hub() -> None:
    """Injecte les styles CSS du hub maison."""
    charger_css("hub_maison.css")


CSS = ""  # Deprecated: use injecter_css_hub()
