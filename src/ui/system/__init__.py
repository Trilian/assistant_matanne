"""
UI System - Design System Core.

Fournit les fondations du Design System via le moteur CSS unifié.

Usage:
    from src.ui.engine import StyleSheet, styled
"""

from src.ui.engine import StyleSheet, css_class, styled, styled_with_attrs

__all__ = [
    "StyleSheet",
    "styled",
    "styled_with_attrs",
    "css_class",
]
