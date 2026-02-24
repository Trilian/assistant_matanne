"""
CSSEngine — Moteur CSS unifié avec déduplication et injection batch.

Combine les fonctionnalités de CSSManager (blocs CSS nommés) et
StyleSheet (classes atomiques hashées) en une seule API optimisée.

Architecture:
- Registre de blocs CSS nommés (thèmes, modules, fichiers)
- Classes atomiques générées à la volée avec hash MD5
- Keyframes avec support prefers-reduced-motion
- Injection batch unique par cycle de rendu

Usage:
    from src.ui.engine import CSSEngine, styled, css_class

    # Enregistrer un bloc CSS
    CSSEngine.register("mon-module", '''
        .mon-module { padding: 1rem; }
    ''')

    # Créer une classe atomique
    cls = css_class(display="flex", gap="1rem")
    html = f'<div class="{cls}">...</div>'

    # Helper styled
    html = styled("section", padding="2rem", background="#f8f9fa")

    # Injection (une fois par render)
    CSSEngine.inject_all()
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import ClassVar

import streamlit as st

logger = logging.getLogger(__name__)

_CSS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "static" / "css"
_FILE_CACHE: dict[str, str] = {}


class CSSEngine:
    """Moteur CSS unifié avec déduplication et injection batch.

    Centralise TOUTES les sources CSS de l'application :
    - Blocs nommés (thèmes, modules, fichiers externes)
    - Classes atomiques générées dynamiquement
    - Animations @keyframes

    Caractéristiques :
    - Déduplication par hash MD5
    - Injection batch unique via st.markdown
    - Invalidation conditionnelle (changement thème/mode)
    - Thread-safe via session_state
    """

    # ═══════════════════════════════════════════════════════════
    # Registres globaux
    # ═══════════════════════════════════════════════════════════

    # Blocs CSS nommés : name → css_string
    _blocks: ClassVar[dict[str, str]] = {}

    # Classes atomiques : class_name → css_rule
    _classes: ClassVar[dict[str, str]] = {}

    # Keyframes : name → @keyframes rule
    _keyframes: ClassVar[dict[str, str]] = {}

    # Session keys
    _HASH_KEY: ClassVar[str] = "_css_engine_hash_v1"
    _INJECTED_KEY: ClassVar[str] = "_css_engine_injected_v1"

    # ═══════════════════════════════════════════════════════════
    # Blocs CSS nommés
    # ═══════════════════════════════════════════════════════════

    @classmethod
    def register(cls, name: str, css: str) -> None:
        """Enregistre un bloc CSS sous un nom unique.

        Args:
            name: Identifiant unique (ex: 'theme', 'jardin', 'tablette')
            css: Contenu CSS brut (sans balises <style>)
        """
        cls._blocks[name] = css.strip()

    @classmethod
    def unregister(cls, name: str) -> None:
        """Retire un bloc CSS du registre."""
        cls._blocks.pop(name, None)

    @classmethod
    def register_file(cls, filename: str) -> None:
        """Charge et enregistre un fichier CSS depuis static/css/.

        Args:
            filename: Nom du fichier (ex: 'jardin.css')
        """
        if filename not in _FILE_CACHE:
            path = _CSS_DIR / filename
            if path.exists():
                _FILE_CACHE[filename] = path.read_text(encoding="utf-8")
            else:
                logger.warning("Fichier CSS non trouvé: %s", path)
                return

        if filename in _FILE_CACHE:
            cls.register(f"file:{filename}", _FILE_CACHE[filename])

    # ═══════════════════════════════════════════════════════════
    # Classes atomiques
    # ═══════════════════════════════════════════════════════════

    @classmethod
    def create_class(cls, styles: dict[str, str], prefix: str = "css") -> str:
        """Crée une classe CSS unique pour un set de styles.

        Args:
            styles: Dict de propriétés CSS {prop: value}
            prefix: Préfixe de la classe générée

        Returns:
            Nom de classe unique (ex: 'css-abc12345')

        Example:
            cls_name = CSSEngine.create_class({
                "display": "flex",
                "gap": "1rem",
            })
        """
        # Normaliser underscore → tiret
        normalized = {k.replace("_", "-"): v for k, v in styles.items()}

        # Hash déterministe
        style_str = ";".join(f"{k}:{v}" for k, v in sorted(normalized.items()))
        hash_val = hashlib.md5(style_str.encode()).hexdigest()[:8]
        class_name = f"{prefix}-{hash_val}"

        # Enregistrer si nouveau
        if class_name not in cls._classes:
            props = "; ".join(f"{k}: {v}" for k, v in normalized.items())
            cls._classes[class_name] = f".{class_name} {{ {props} }}"

        return class_name

    @classmethod
    def create_from_string(cls, style_string: str, prefix: str = "css") -> str:
        """Crée une classe à partir d'une chaîne de styles.

        Args:
            style_string: Styles CSS (ex: "display: flex; gap: 1rem;")
            prefix: Préfixe de classe

        Returns:
            Nom de classe unique
        """
        styles = {}
        for part in style_string.split(";"):
            part = part.strip()
            if ":" in part:
                key, value = part.split(":", 1)
                styles[key.strip()] = value.strip()
        return cls.create_class(styles, prefix)

    # ═══════════════════════════════════════════════════════════
    # Keyframes
    # ═══════════════════════════════════════════════════════════

    @classmethod
    def register_keyframes(cls, name: str, keyframes: str) -> str:
        """Enregistre une animation @keyframes.

        Args:
            name: Nom de l'animation
            keyframes: Contenu (sans @keyframes {...})

        Returns:
            Nom de l'animation pour référence
        """
        if name not in cls._keyframes:
            cls._keyframes[name] = f"@keyframes {name} {{ {keyframes.strip()} }}"
        return name

    # ═══════════════════════════════════════════════════════════
    # Injection batch
    # ═══════════════════════════════════════════════════════════

    @classmethod
    def inject_all(cls) -> None:
        """Injecte tout le CSS en un seul appel st.markdown.

        Utilise un hash MD5 pour éviter la réinjection si le
        contenu n'a pas changé entre deux cycles de rendu.
        """
        parts: list[str] = []

        # 1. Blocs nommés
        for name, css in sorted(cls._blocks.items()):
            parts.append(f"/* [{name}] */\n{css}")

        # 2. Classes atomiques
        if cls._classes:
            atomic_css = "\n".join(cls._classes.values())
            parts.append(f"/* [atomic-classes] */\n{atomic_css}")

        # 3. Keyframes (avec prefers-reduced-motion)
        if cls._keyframes:
            kf_css = "\n".join(cls._keyframes.values())
            parts.append(
                f"/* [keyframes] */\n"
                f"@media (prefers-reduced-motion: no-preference) {{\n{kf_css}\n}}"
            )

        if not parts:
            return

        full_css = "\n\n".join(parts)
        css_hash = hashlib.md5(full_css.encode()).hexdigest()

        # Vérifier si changement
        if cls._HASH_KEY not in st.session_state:
            st.session_state[cls._HASH_KEY] = ""

        if st.session_state[cls._HASH_KEY] != css_hash:
            st.markdown(f"<style>\n{full_css}\n</style>", unsafe_allow_html=True)
            st.session_state[cls._HASH_KEY] = css_hash
            logger.debug(
                "CSSEngine: injecté %d blocs + %d classes + %d keyframes (hash=%s)",
                len(cls._blocks),
                len(cls._classes),
                len(cls._keyframes),
                css_hash[:8],
            )

    @classmethod
    def invalidate(cls) -> None:
        """Force la réinjection au prochain inject_all().

        À appeler lors d'un changement de thème ou mode.
        """
        if cls._HASH_KEY in st.session_state:
            st.session_state[cls._HASH_KEY] = ""

    @classmethod
    def get_stats(cls) -> dict[str, int]:
        """Statistiques du moteur CSS."""
        blocks_size = sum(len(css) for css in cls._blocks.values())
        classes_size = sum(len(css) for css in cls._classes.values())
        return {
            "blocks": len(cls._blocks),
            "classes": len(cls._classes),
            "keyframes": len(cls._keyframes),
            "total_bytes": blocks_size + classes_size,
        }

    @classmethod
    def reset(cls) -> None:
        """Reset complet (pour tests)."""
        cls._blocks.clear()
        cls._classes.clear()
        cls._keyframes.clear()
        for key in (cls._HASH_KEY, cls._INJECTED_KEY):
            if key in st.session_state:
                del st.session_state[key]

    # ═══════════════════════════════════════════════════════════
    # Méthodes de compat StyleSheet
    # ═══════════════════════════════════════════════════════════

    @classmethod
    def get_all_css(cls) -> str:
        """Retourne tout le CSS généré (pour debug/export)."""
        parts = list(cls._blocks.values()) + list(cls._classes.values())
        return "\n".join(parts)

    @classmethod
    def inject(cls) -> None:
        """Alias pour inject_all() (compat StyleSheet)."""
        cls.inject_all()

    @classmethod
    def mark_all_injected(cls) -> None:
        """No-op pour compat CSSManager."""
        pass


# ═══════════════════════════════════════════════════════════
# Helpers de haut niveau
# ═══════════════════════════════════════════════════════════


def styled(tag: str = "div", **styles: str) -> str:
    """Crée un élément HTML avec styles optimisés.

    Args:
        tag: Tag HTML (div, span, section...)
        **styles: Propriétés CSS (underscore → tiret)

    Returns:
        Balise HTML ouvrante avec classe

    Example:
        html = styled("div", display="flex", gap="1rem")
        # → '<div class="css-a1b2c3d4">'
    """
    if not styles:
        return f"<{tag}>"
    class_name = CSSEngine.create_class(styles)
    return f'<{tag} class="{class_name}">'


def styled_with_attrs(tag: str = "div", attrs: dict[str, str] | None = None, **styles: str) -> str:
    """Crée un élément avec styles ET attributs HTML.

    Args:
        tag: Tag HTML
        attrs: Attributs additionnels (id, data-*, aria-*...)
        **styles: Propriétés CSS

    Returns:
        Balise ouvrante complète
    """
    parts = [f"<{tag}"]

    if styles:
        class_name = CSSEngine.create_class(styles)
        parts.append(f'class="{class_name}"')

    if attrs:
        for key, value in attrs.items():
            safe_value = str(value).replace('"', "&quot;")
            parts.append(f'{key}="{safe_value}"')

    return " ".join(parts) + ">"


def css_class(**styles: str) -> str:
    """Crée une classe CSS et retourne son nom.

    Args:
        **styles: Propriétés CSS

    Returns:
        Nom de la classe générée

    Example:
        cls = css_class(display="flex", gap="1rem")
        html = f'<div class="{cls}">...</div>'
    """
    return CSSEngine.create_class(styles)


def register_keyframes(name: str, keyframes: str) -> str:
    """Enregistre une animation @keyframes.

    Args:
        name: Nom de l'animation
        keyframes: Contenu des keyframes

    Returns:
        Nom de l'animation
    """
    return CSSEngine.register_keyframes(name, keyframes)


def inject_all() -> None:
    """Injecte tout le CSS (wrapper pour CSSEngine.inject_all)."""
    CSSEngine.inject_all()


def charger_css(nom_fichier: str) -> None:
    """Charge un fichier CSS depuis static/css/ (compat ancien API)."""
    CSSEngine.register_file(nom_fichier)


# ═══════════════════════════════════════════════════════════
# Backward compatibility aliases
# ═══════════════════════════════════════════════════════════

# CSSManager et StyleSheet pointent vers CSSEngine
CSSManager = CSSEngine
StyleSheet = CSSEngine


# ═══════════════════════════════════════════════════════════
# Keyframes pré-enregistrées
# ═══════════════════════════════════════════════════════════

CSSEngine.register_keyframes("fadeIn", "from { opacity: 0; } to { opacity: 1; }")
CSSEngine.register_keyframes("fadeOut", "from { opacity: 1; } to { opacity: 0; }")
CSSEngine.register_keyframes(
    "slideUp",
    "from { opacity: 0; transform: translateY(16px); } "
    "to { opacity: 1; transform: translateY(0); }",
)
CSSEngine.register_keyframes(
    "slideDown",
    "from { opacity: 0; transform: translateY(-16px); } "
    "to { opacity: 1; transform: translateY(0); }",
)
CSSEngine.register_keyframes(
    "scaleIn",
    "from { opacity: 0; transform: scale(0.9); } to { opacity: 1; transform: scale(1); }",
)
CSSEngine.register_keyframes("pulse", "0%, 100% { opacity: 1; } 50% { opacity: 0.6; }")
CSSEngine.register_keyframes(
    "shimmer",
    "0% { background-position: -200% 0; } 100% { background-position: 200% 0; }",
)
CSSEngine.register_keyframes(
    "spin", "from { transform: rotate(0deg); } to { transform: rotate(360deg); }"
)


__all__ = [
    "CSSEngine",
    "styled",
    "styled_with_attrs",
    "css_class",
    "register_keyframes",
    "inject_all",
    "charger_css",
    "CSSManager",
    "StyleSheet",
]
