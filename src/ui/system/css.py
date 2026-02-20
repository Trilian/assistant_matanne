"""
Moteur CSS optimisé avec déduplication et injection unique.

Élimine la duplication de CSS en générant des classes atomiques
et en les injectant une seule fois. Réduit considérablement
le nombre d'appels à st.markdown(unsafe_allow_html=True).

Usage:
    from src.ui.system.css import StyleSheet, styled, css_class

    # Créer une classe CSS unique
    class_name = StyleSheet.create_class({
        "display": "flex",
        "gap": "1rem",
        "padding": "1.5rem",
    })
    # → "css-a1b2c3d4"

    # Injecter le CSS accumulé (une fois par render)
    StyleSheet.inject()

    # Helper pour générer du HTML stylé
    html = styled("div",
        display="flex",
        gap="1rem",
        background=Couleur.BG_SUBTLE,
    )
    # → '<div class="css-a1b2c3d4">'
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import ClassVar

import streamlit as st


@dataclass
class StyleSheet:
    """Feuille de style avec déduplication automatique.

    Gère un registre global de classes CSS et assure leur injection
    unique dans la page Streamlit.

    Caractéristiques:
    - Hash MD5 des styles pour déduplication
    - Injection batch pour performance
    - Reset automatique entre sessions
    """

    # Registre global : class_name → css_rule
    _styles: ClassVar[dict[str, str]] = {}

    # Classes déjà injectées dans la page courante
    _injected: ClassVar[set[str]] = set()

    # Clé session_state pour tracking
    _SESSION_KEY: ClassVar[str] = "_stylesheet_injected_v3"

    @classmethod
    def _init_session(cls) -> None:
        """Initialise le tracking de session si nécessaire."""
        if cls._SESSION_KEY not in st.session_state:
            st.session_state[cls._SESSION_KEY] = set()
            cls._injected = set()
        else:
            cls._injected = st.session_state[cls._SESSION_KEY]

    @classmethod
    def create_class(cls, styles: dict[str, str], prefix: str = "css") -> str:
        """Crée une classe CSS unique pour un set de styles.

        Args:
            styles: Dict de propriétés CSS {prop: value}.
            prefix: Préfixe de la classe générée.

        Returns:
            Nom de classe unique (ex: 'css-abc12345').

        Example:
            class_name = StyleSheet.create_class({
                "display": "flex",
                "align-items": "center",
                "gap": "1rem",
            })
        """
        # Normaliser les clés (underscore → tiret)
        normalized = {k.replace("_", "-"): v for k, v in styles.items()}

        # Créer une chaîne déterministe pour le hash
        style_str = ";".join(f"{k}:{v}" for k, v in sorted(normalized.items()))
        hash_value = hashlib.md5(style_str.encode()).hexdigest()[:8]
        class_name = f"{prefix}-{hash_value}"

        # Enregistrer si nouveau
        if class_name not in cls._styles:
            css_props = "; ".join(f"{k}: {v}" for k, v in normalized.items())
            cls._styles[class_name] = f".{class_name} {{ {css_props} }}"

        return class_name

    @classmethod
    def create_from_string(cls, style_string: str, prefix: str = "css") -> str:
        """Crée une classe à partir d'une chaîne de styles.

        Args:
            style_string: Styles CSS en chaîne (ex: "display: flex; gap: 1rem;").
            prefix: Préfixe de classe.

        Returns:
            Nom de classe unique.
        """
        # Parser la chaîne en dict
        styles = {}
        for part in style_string.split(";"):
            part = part.strip()
            if ":" in part:
                key, value = part.split(":", 1)
                styles[key.strip()] = value.strip()

        return cls.create_class(styles, prefix)

    @classmethod
    def inject(cls) -> None:
        """Injecte toutes les classes CSS non encore injectées.

        Doit être appelé une fois par render cycle, idéalement
        dans l'initialisation de l'app.
        """
        cls._init_session()

        to_inject = set(cls._styles.keys()) - cls._injected

        if not to_inject:
            return

        # Construire le CSS
        css_rules = [cls._styles[name] for name in sorted(to_inject)]
        css = "\n".join(css_rules)

        # Injecter
        st.markdown(f"<style>\n{css}\n</style>", unsafe_allow_html=True)

        # Marquer comme injecté
        cls._injected.update(to_inject)
        st.session_state[cls._SESSION_KEY] = cls._injected

    @classmethod
    def get_stats(cls) -> dict[str, int]:
        """Retourne des statistiques sur le StyleSheet.

        Returns:
            Dict avec total_classes, injected_classes, pending_classes.
        """
        cls._init_session()
        return {
            "total_classes": len(cls._styles),
            "injected_classes": len(cls._injected),
            "pending_classes": len(cls._styles) - len(cls._injected),
        }

    @classmethod
    def reset(cls) -> None:
        """Reset complet (pour tests ou debug)."""
        cls._styles.clear()
        cls._injected.clear()
        if cls._SESSION_KEY in st.session_state:
            del st.session_state[cls._SESSION_KEY]

    @classmethod
    def get_all_css(cls) -> str:
        """Retourne tout le CSS généré (pour debug/export)."""
        return "\n".join(cls._styles.values())


def styled(tag: str = "div", **styles: str) -> str:
    """Crée un élément HTML avec styles optimisés.

    Génère une classe CSS unique et retourne la balise ouvrante.
    Le CSS sera injecté lors du prochain appel à StyleSheet.inject().

    Args:
        tag: Tag HTML (div, span, section, etc.).
        **styles: Propriétés CSS (underscore converti en tiret).

    Returns:
        Balise HTML ouvrante avec classe.

    Example:
        html = styled("div",
            display="flex",
            gap="1rem",
            background="#f8f9fa",
            padding="1.5rem",
            border_radius="12px",
        )
        # → '<div class="css-a1b2c3d4">'
    """
    if not styles:
        return f"<{tag}>"

    class_name = StyleSheet.create_class(styles)
    return f'<{tag} class="{class_name}">'


def styled_with_attrs(tag: str = "div", attrs: dict[str, str] | None = None, **styles: str) -> str:
    """Crée un élément avec styles ET attributs HTML.

    Args:
        tag: Tag HTML.
        attrs: Attributs additionnels (id, data-*, aria-*, etc.).
        **styles: Propriétés CSS.

    Returns:
        Balise ouvrante complète.

    Example:
        html = styled_with_attrs("nav",
            attrs={"role": "navigation", "aria-label": "Menu"},
            display="flex",
            gap="1rem",
        )
        # → '<nav class="css-..." role="navigation" aria-label="Menu">'
    """
    parts = [f"<{tag}"]

    if styles:
        class_name = StyleSheet.create_class(styles)
        parts.append(f'class="{class_name}"')

    if attrs:
        for key, value in attrs.items():
            # Échapper les guillemets dans les valeurs
            safe_value = str(value).replace('"', "&quot;")
            parts.append(f'{key}="{safe_value}"')

    return " ".join(parts) + ">"


def css_class(**styles: str) -> str:
    """Crée une classe CSS et retourne son nom.

    Alias pratique pour StyleSheet.create_class avec kwargs.

    Args:
        **styles: Propriétés CSS.

    Returns:
        Nom de la classe générée.

    Example:
        cls = css_class(display="flex", gap="1rem")
        html = f'<div class="{cls}">...</div>'
    """
    return StyleSheet.create_class(styles)


# ═══════════════════════════════════════════════════════════
# KEYFRAMES - Animations CSS
# ═══════════════════════════════════════════════════════════

_KEYFRAMES_REGISTRY: dict[str, str] = {}
_KEYFRAMES_INJECTED: set[str] = set()


def register_keyframes(name: str, keyframes: str) -> str:
    """Enregistre une animation @keyframes.

    Args:
        name: Nom de l'animation.
        keyframes: Contenu des keyframes (sans @keyframes {...}).

    Returns:
        Nom de l'animation (pour référence dans animation CSS).

    Example:
        register_keyframes("fadeIn", '''
            from { opacity: 0; }
            to { opacity: 1; }
        ''')

        # Utiliser dans un style
        class_name = StyleSheet.create_class({
            "animation": "fadeIn 0.3s ease forwards",
        })
    """
    if name not in _KEYFRAMES_REGISTRY:
        _KEYFRAMES_REGISTRY[name] = f"@keyframes {name} {{ {keyframes.strip()} }}"
    return name


def inject_keyframes() -> None:
    """Injecte les @keyframes non encore injectés."""
    global _KEYFRAMES_INJECTED

    to_inject = set(_KEYFRAMES_REGISTRY.keys()) - _KEYFRAMES_INJECTED

    if not to_inject:
        return

    css = "\n".join(_KEYFRAMES_REGISTRY[name] for name in to_inject)

    # Wrapper dans media query pour reduced-motion
    css_with_motion = f"""
@media (prefers-reduced-motion: no-preference) {{
{css}
}}
"""

    st.markdown(f"<style>{css_with_motion}</style>", unsafe_allow_html=True)
    _KEYFRAMES_INJECTED.update(to_inject)


# Pré-enregistrer les animations courantes
register_keyframes("fadeIn", "from { opacity: 0; } to { opacity: 1; }")
register_keyframes("fadeOut", "from { opacity: 1; } to { opacity: 0; }")
register_keyframes(
    "slideUp",
    "from { opacity: 0; transform: translateY(16px); } "
    "to { opacity: 1; transform: translateY(0); }",
)
register_keyframes(
    "slideDown",
    "from { opacity: 0; transform: translateY(-16px); } "
    "to { opacity: 1; transform: translateY(0); }",
)
register_keyframes(
    "scaleIn",
    "from { opacity: 0; transform: scale(0.9); } " "to { opacity: 1; transform: scale(1); }",
)
register_keyframes("pulse", "0%, 100% { opacity: 1; } 50% { opacity: 0.6; }")
register_keyframes(
    "shimmer", "0% { background-position: -200% 0; } 100% { background-position: 200% 0; }"
)
register_keyframes("spin", "from { transform: rotate(0deg); } to { transform: rotate(360deg); }")


__all__ = [
    "StyleSheet",
    "styled",
    "styled_with_attrs",
    "css_class",
    "register_keyframes",
    "inject_keyframes",
]
