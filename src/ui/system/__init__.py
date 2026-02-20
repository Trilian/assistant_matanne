"""
UI System - Design System Core.

Fournit les fondations du Design System 3.0:
- variants: Système de variantes type-safe (CVA-style)
- css: Moteur CSS optimisé avec déduplication
- theme: ThemeProvider et tokens

Usage:
    from src.ui.system import cva, VariantConfig, StyleSheet, styled
"""

from .css import StyleSheet, css_class, inject_keyframes, styled, styled_with_attrs
from .variants import (
    BADGE_VARIANTS,
    BUTTON_VARIANTS,
    CARD_SLOTS,
    SlotConfig,
    TVConfig,
    VariantConfig,
    cva,
    slot,
    tv,
)

__all__ = [
    # Variants
    "cva",
    "tv",
    "slot",
    "VariantConfig",
    "TVConfig",
    "SlotConfig",
    # Presets
    "BADGE_VARIANTS",
    "BUTTON_VARIANTS",
    "CARD_SLOTS",
    # CSS
    "StyleSheet",
    "styled",
    "styled_with_attrs",
    "css_class",
    "inject_keyframes",
]
