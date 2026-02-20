"""Styles CSS pour le module Jardin."""

from src.ui.css import charger_css


def injecter_css_jardin() -> None:
    """Injecte les styles CSS du module jardin."""
    charger_css("jardin.css")


# Backward compatibility — used by __init__.py via st.markdown(CSS, unsafe_allow_html=True)
# TODO: Migrate callers to use injecter_css_jardin() directly
CSS = ""  # Deprecated: use injecter_css_jardin()
