"""
UI System - Design System Core.

Fournit les fondations du Design System:
- css: Moteur CSS optimisé avec déduplication (StyleSheet, styled)

Usage:
    from src.ui.system import StyleSheet, styled
"""

from .css import StyleSheet, css_class, inject_keyframes, styled, styled_with_attrs

__all__ = [
    "StyleSheet",
    "styled",
    "styled_with_attrs",
    "css_class",
    "inject_keyframes",
]
