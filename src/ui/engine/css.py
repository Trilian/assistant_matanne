"""
CSSEngine — Moteur CSS unifié avec déduplication et injection batch.

Combine les fonctionnalités de CSSManager (blocs CSS nommés) et
StyleSheet (classes atomiques hashées) en une seule API optimisée.

Architecture:
- Registre de blocs CSS nommés (thèmes, modules, fichiers)
- Classes atomiques générées à la volée avec hash MD5
- Keyframes avec support prefers-reduced-motion
- Injection batch unique par cycle de rendu

**Thread-safety**: Les registres CSS sont stockés dans st.session_state
pour éviter les collisions cross-session en environnement multi-worker
(Streamlit crée un process/thread par utilisateur).

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

import streamlit as st

logger = logging.getLogger(__name__)

_CSS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "static" / "css"
_FILE_CACHE: dict[str, str] = {}

# Session state keys pour les registres CSS (un par session utilisateur)
_SK_BLOCKS = "_css_engine_blocks_v2"
_SK_CLASSES = "_css_engine_classes_v2"
_SK_KEYFRAMES = "_css_engine_keyframes_v2"
_SK_HASH = "_css_engine_hash_v2"
_SK_INJECTED = "_css_engine_injected_v2"


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
    - Session-scoped (thread-safe multi-worker)

    Note:
        Les registres CSS sont stockés dans st.session_state pour éviter
        les collisions entre sessions utilisateur en environnement multi-worker.
    """

    # ═══════════════════════════════════════════════════════════
    # Accesseurs session-scoped (remplace ClassVar mutable)
    # ═══════════════════════════════════════════════════════════

    @classmethod
    def _get_blocks(cls) -> dict[str, str]:
        """Accès au registre de blocs CSS de la session courante."""
        if _SK_BLOCKS not in st.session_state:
            st.session_state[_SK_BLOCKS] = {}
        return st.session_state[_SK_BLOCKS]

    @classmethod
    def _get_classes(cls) -> dict[str, str]:
        """Accès au registre de classes atomiques de la session courante."""
        if _SK_CLASSES not in st.session_state:
            st.session_state[_SK_CLASSES] = {}
        return st.session_state[_SK_CLASSES]

    @classmethod
    def _get_keyframes(cls) -> dict[str, str]:
        """Accès au registre de keyframes de la session courante."""
        if _SK_KEYFRAMES not in st.session_state:
            st.session_state[_SK_KEYFRAMES] = {}
        return st.session_state[_SK_KEYFRAMES]

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
        cls._get_blocks()[name] = css.strip()

    @classmethod
    def unregister(cls, name: str) -> None:
        """Retire un bloc CSS du registre."""
        cls._get_blocks().pop(name, None)

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
        classes = cls._get_classes()
        if class_name not in classes:
            props = "; ".join(f"{k}: {v}" for k, v in normalized.items())
            classes[class_name] = f".{class_name} {{ {props} }}"

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
        kf = cls._get_keyframes()
        if name not in kf:
            kf[name] = f"@keyframes {name} {{ {keyframes.strip()} }}"
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
        blocks = cls._get_blocks()
        classes = cls._get_classes()
        keyframes = cls._get_keyframes()

        parts: list[str] = []

        # 1. Blocs nommés
        for name, css in sorted(blocks.items()):
            parts.append(f"/* [{name}] */\n{css}")

        # 2. Classes atomiques
        if classes:
            atomic_css = "\n".join(classes.values())
            parts.append(f"/* [atomic-classes] */\n{atomic_css}")

        # 3. Keyframes (avec prefers-reduced-motion)
        if keyframes:
            kf_css = "\n".join(keyframes.values())
            parts.append(
                f"/* [keyframes] */\n"
                f"@media (prefers-reduced-motion: no-preference) {{\n{kf_css}\n}}"
            )

        if not parts:
            return

        full_css = "\n\n".join(parts)
        css_hash = hashlib.md5(full_css.encode()).hexdigest()

        # Vérifier si changement
        if _SK_HASH not in st.session_state:
            st.session_state[_SK_HASH] = ""

        if st.session_state[_SK_HASH] != css_hash:
            st.markdown(f"<style>\n{full_css}\n</style>", unsafe_allow_html=True)
            st.session_state[_SK_HASH] = css_hash
            logger.debug(
                "CSSEngine: injecté %d blocs + %d classes + %d keyframes (hash=%s)",
                len(blocks),
                len(classes),
                len(keyframes),
                css_hash[:8],
            )

    @classmethod
    def invalidate(cls) -> None:
        """Force la réinjection au prochain inject_all().

        À appeler lors d'un changement de thème ou mode.
        """
        if _SK_HASH in st.session_state:
            st.session_state[_SK_HASH] = ""

    @classmethod
    def get_stats(cls) -> dict[str, int]:
        """Statistiques du moteur CSS."""
        blocks = cls._get_blocks()
        classes = cls._get_classes()
        keyframes = cls._get_keyframes()
        blocks_size = sum(len(css) for css in blocks.values())
        classes_size = sum(len(css) for css in classes.values())
        return {
            "blocks": len(blocks),
            "classes": len(classes),
            "keyframes": len(keyframes),
            "total_bytes": blocks_size + classes_size,
        }

    @classmethod
    def reset(cls) -> None:
        """Reset complet (pour tests)."""
        cls._get_blocks().clear()
        cls._get_classes().clear()
        cls._get_keyframes().clear()
        for key in (_SK_HASH, _SK_INJECTED):
            if key in st.session_state:
                del st.session_state[key]

    # ═══════════════════════════════════════════════════════════
    # Méthodes de compat StyleSheet
    # ═══════════════════════════════════════════════════════════

    @classmethod
    def get_all_css(cls) -> str:
        """Retourne tout le CSS généré (pour debug/export)."""
        blocks = cls._get_blocks()
        classes = cls._get_classes()
        parts = list(blocks.values()) + list(classes.values())
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


# NOTE: Keyframes pré-enregistrées centralisées dans src/ui/animations.py
# Utiliser register_keyframes() pour des keyframes ad-hoc uniquement.


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
