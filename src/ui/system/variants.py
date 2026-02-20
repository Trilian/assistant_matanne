"""
Class Variance Authority (CVA) - Variantes composables et type-safe.

Inspiré de cva/tailwind-variants (JavaScript) adapté pour Streamlit.
Permet de définir des composants avec variantes sans CSS dupliqué.

Usage:
    from src.ui.system.variants import cva, VariantConfig

    button = cva(VariantConfig(
        base="display: inline-flex; align-items: center; justify-content: center;",
        variants={
            "intent": {
                "primary": "background: #4CAF50; color: white;",
                "danger": "background: #FF5722; color: white;",
            },
            "size": {
                "sm": "height: 2rem; padding: 0 0.75rem; font-size: 0.875rem;",
                "md": "height: 2.5rem; padding: 0 1rem;",
                "lg": "height: 3rem; padding: 0 1.5rem; font-size: 1.1rem;",
            },
        },
        compound_variants=[
            {"intent": "danger", "size": "lg", "styles": "font-weight: 700;"},
        ],
        default_variants={"intent": "primary", "size": "md"},
    ))

    styles = button(intent="danger", size="lg")
    # → "display: inline-flex; ... background: #FF5722; ... height: 3rem; ... font-weight: 700;"
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True)
class VariantConfig:
    """Configuration de variantes avec typage strict.

    Attributes:
        base: Styles CSS de base appliqués à tous les cas.
        variants: Dict de variantes {nom_variante: {valeur: styles}}.
        compound_variants: Liste de combinaisons de variantes avec styles additionnels.
        default_variants: Valeurs par défaut pour chaque variante.
    """

    base: str = ""
    variants: dict[str, dict[str, str]] = field(default_factory=dict)
    compound_variants: list[dict[str, Any]] | None = None
    default_variants: dict[str, str] | None = None


def cva(config: VariantConfig) -> Callable[..., str]:
    """Crée un générateur de styles CSS avec variantes.

    Le générateur retourne une chaîne de styles CSS à utiliser
    dans l'attribut style d'un élément HTML.

    Args:
        config: Configuration des variantes.

    Returns:
        Fonction qui génère les styles selon les props passées.

    Example:
        badge = cva(VariantConfig(
            base="padding: 0.25rem 0.75rem; border-radius: 50px; font-size: 0.875rem;",
            variants={
                "variant": {
                    "success": "background: #d4edda; color: #155724;",
                    "warning": "background: #fff3cd; color: #856404;",
                    "danger": "background: #f8d7da; color: #721c24;",
                },
            },
            default_variants={"variant": "success"},
        ))

        style = badge(variant="warning")
    """

    def generator(**props: str) -> str:
        styles: list[str] = []

        # 1. Styles de base
        if config.base:
            styles.append(config.base.strip())

        # 2. Merger avec defaults
        merged = {**(config.default_variants or {}), **props}

        # 3. Appliquer les variantes
        for variant_key, variant_value in merged.items():
            if variant_key in config.variants:
                variant_styles = config.variants[variant_key].get(str(variant_value), "")
                if variant_styles:
                    styles.append(variant_styles.strip())

        # 4. Compound variants (combinaisons)
        if config.compound_variants:
            for compound in config.compound_variants:
                # Vérifier si toutes les conditions sont remplies
                matches = all(
                    str(merged.get(k)) == str(v) for k, v in compound.items() if k != "styles"
                )
                if matches and "styles" in compound:
                    styles.append(compound["styles"].strip())

        # Joindre tous les styles
        return " ".join(styles)

    return generator


# ═══════════════════════════════════════════════════════════
# TAILWIND VARIANTS (TV) - Version avancée avec slots
# ═══════════════════════════════════════════════════════════


@dataclass
class SlotConfig:
    """Configuration d'un slot (partie de composant)."""

    base: str = ""
    variants: dict[str, dict[str, str]] = field(default_factory=dict)


def slot(base: str = "", **variants: dict[str, str]) -> SlotConfig:
    """Helper pour définir un slot.

    Args:
        base: Styles de base du slot.
        **variants: Variantes du slot.

    Example:
        slots = {
            "root": slot("display: flex;", size={"sm": "gap: 0.5rem;", "lg": "gap: 1rem;"}),
            "label": slot("font-weight: 500;", size={"sm": "font-size: 0.8rem;"}),
        }
    """
    return SlotConfig(base=base, variants=variants)


@dataclass
class TVConfig:
    """Configuration Tailwind Variants avec slots multiples.

    Permet de définir des composants complexes avec plusieurs parties
    (root, label, icon, etc.) qui partagent les mêmes variantes.
    """

    slots: dict[str, SlotConfig]
    variants: dict[str, dict[str, dict[str, str]]] = field(default_factory=dict)
    compound_variants: list[dict[str, Any]] | None = None
    default_variants: dict[str, str] | None = None


def tv(config: TVConfig) -> Callable[..., dict[str, str]]:
    """Crée un générateur de styles multi-slots.

    Args:
        config: Configuration TV avec slots.

    Returns:
        Fonction qui retourne un dict {slot_name: styles}.

    Example:
        card = tv(TVConfig(
            slots={
                "root": slot("border-radius: 12px; overflow: hidden;"),
                "header": slot("padding: 1rem; border-bottom: 1px solid #e0e0e0;"),
                "body": slot("padding: 1.5rem;"),
                "footer": slot("padding: 1rem; background: #f8f9fa;"),
            },
            variants={
                "variant": {
                    "elevated": {
                        "root": "box-shadow: 0 4px 12px rgba(0,0,0,0.1);",
                    },
                    "outlined": {
                        "root": "border: 1px solid #e0e0e0;",
                    },
                },
            },
            default_variants={"variant": "elevated"},
        ))

        styles = card(variant="outlined")
        # → {"root": "...", "header": "...", "body": "...", "footer": "..."}
    """

    def generator(**props: str) -> dict[str, str]:
        merged = {**(config.default_variants or {}), **props}
        result: dict[str, str] = {}

        for slot_name, slot_config in config.slots.items():
            styles: list[str] = []

            # Base du slot
            if slot_config.base:
                styles.append(slot_config.base.strip())

            # Variantes du slot local
            for var_name, var_value in merged.items():
                if var_name in slot_config.variants:
                    slot_styles = slot_config.variants[var_name].get(str(var_value), "")
                    if slot_styles:
                        styles.append(slot_styles.strip())

            # Variantes globales qui affectent ce slot
            for var_name, var_options in config.variants.items():
                var_value = merged.get(var_name)
                if var_value and var_value in var_options:
                    slot_styles = var_options[var_value].get(slot_name, "")
                    if slot_styles:
                        styles.append(slot_styles.strip())

            # Compound variants
            if config.compound_variants:
                for compound in config.compound_variants:
                    matches = all(
                        str(merged.get(k)) == str(v)
                        for k, v in compound.items()
                        if k not in ("styles", "slots")
                    )
                    if matches:
                        if "slots" in compound and slot_name in compound["slots"]:
                            styles.append(compound["slots"][slot_name].strip())

            result[slot_name] = " ".join(styles)

        return result

    return generator


# ═══════════════════════════════════════════════════════════
# PRESETS - Variantes prédéfinies pour composants courants
# ═══════════════════════════════════════════════════════════

# Import tokens pour les presets
from src.ui.tokens import Couleur, Espacement, Rayon, Typographie

# Badge preset
BADGE_VARIANTS = VariantConfig(
    base=f"display: inline-flex; padding: {Espacement.XS} 0.75rem; "
    f"border-radius: {Rayon.PILL}; font-size: {Typographie.BODY_SM}; font-weight: 600;",
    variants={
        "variant": {
            "success": f"background: {Couleur.BG_SUCCESS}; color: {Couleur.BADGE_SUCCESS_TEXT};",
            "warning": f"background: {Couleur.BG_WARNING}; color: {Couleur.BADGE_WARNING_TEXT};",
            "danger": f"background: {Couleur.BG_DANGER}; color: {Couleur.BADGE_DANGER_TEXT};",
            "info": f"background: {Couleur.BG_INFO}; color: {Couleur.INFO};",
            "neutral": f"background: {Couleur.BG_SUBTLE}; color: {Couleur.TEXT_SECONDARY};",
            "accent": f"background: {Couleur.ACCENT}; color: white;",
        },
    },
    default_variants={"variant": "success"},
)

# Button preset
BUTTON_VARIANTS = VariantConfig(
    base="display: inline-flex; align-items: center; justify-content: center; "
    f"border: none; cursor: pointer; font-weight: 500; transition: all 0.2s ease; "
    f"border-radius: {Rayon.MD};",
    variants={
        "intent": {
            "primary": f"background: {Couleur.ACCENT}; color: white;",
            "secondary": f"background: {Couleur.BG_SUBTLE}; color: {Couleur.TEXT_PRIMARY}; "
            f"border: 1px solid {Couleur.BORDER};",
            "danger": f"background: {Couleur.DANGER}; color: white;",
            "ghost": f"background: transparent; color: {Couleur.TEXT_PRIMARY};",
        },
        "size": {
            "sm": f"height: 2rem; padding: 0 {Espacement.SM}; font-size: {Typographie.BODY_SM};",
            "md": f"height: 2.5rem; padding: 0 {Espacement.MD};",
            "lg": f"height: 3rem; padding: 0 {Espacement.LG}; font-size: {Typographie.BODY_LG};",
        },
        "fullWidth": {
            "true": "width: 100%;",
            "false": "",
        },
    },
    compound_variants=[
        {"intent": "primary", "size": "lg", "styles": "font-weight: 600;"},
        {"intent": "danger", "size": "lg", "styles": "font-weight: 700;"},
    ],
    default_variants={"intent": "primary", "size": "md", "fullWidth": "false"},
)

# Card preset avec slots
CARD_SLOTS = TVConfig(
    slots={
        "root": slot(
            f"background: {Couleur.BG_SURFACE}; border-radius: {Rayon.LG}; overflow: hidden;"
        ),
        "header": slot(
            f"padding: {Espacement.MD} {Espacement.LG}; "
            f"border-bottom: 1px solid {Couleur.BORDER_LIGHT};"
        ),
        "body": slot(f"padding: {Espacement.LG};"),
        "footer": slot(
            f"padding: {Espacement.MD} {Espacement.LG}; " f"background: {Couleur.BG_SUBTLE};"
        ),
    },
    variants={
        "variant": {
            "elevated": {
                "root": "box-shadow: 0 4px 12px rgba(0,0,0,0.08);",
            },
            "outlined": {
                "root": f"border: 1px solid {Couleur.BORDER};",
            },
            "flat": {
                "root": "",
            },
        },
        "padding": {
            "none": {
                "body": "padding: 0;",
            },
            "sm": {
                "body": f"padding: {Espacement.SM};",
                "header": f"padding: {Espacement.SM};",
            },
            "lg": {
                "body": f"padding: {Espacement.XL};",
            },
        },
    },
    default_variants={"variant": "elevated"},
)


__all__ = [
    "VariantConfig",
    "cva",
    "TVConfig",
    "SlotConfig",
    "slot",
    "tv",
    # Presets
    "BADGE_VARIANTS",
    "BUTTON_VARIANTS",
    "CARD_SLOTS",
]
