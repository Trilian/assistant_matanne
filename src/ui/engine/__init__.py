"""
CSS Engine — Moteur CSS unifié.

Fusionne CSSManager (blocs CSS) et StyleSheet (classes atomiques)
en une seule API cohérente avec injection batch optimisée.
"""

from src.ui.engine.css import (
    CSSEngine,
    # Backward compat aliases
    CSSManager,
    StyleSheet,
    charger_css,
    css_class,
    inject_all,
    register_keyframes,
    styled,
    styled_with_attrs,
)

__all__ = [
    "CSSEngine",
    "styled",
    "styled_with_attrs",
    "css_class",
    "register_keyframes",
    "inject_all",
    "charger_css",
    # Backward compat
    "CSSManager",
    "StyleSheet",
]
