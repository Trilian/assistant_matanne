"""
CSSManager — Pipeline CSS unifié avec déduplication et injection batch.

Centralise TOUTES les injections CSS (styles, thème, tokens sémantiques,
accessibilité, animations, tablette) en un seul ``st.markdown``.

Élimine les 5+ appels ``st.markdown("<style>...")`` par cycle Streamlit.

Usage:
    from src.ui.css import CSSManager, charger_css

    # Enregistrement (chaque source une fois) :
    CSSManager.register("app-styles", css_string)

    # Injection batch (une fois par render) :
    CSSManager.inject_all()
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

import streamlit as st

logger = logging.getLogger(__name__)

_CSS_DIR = Path(__file__).resolve().parent.parent.parent / "static" / "css"
_CSS_CACHE: dict[str, str] = {}


class CSSManager:
    """Pipeline CSS unifié avec déduplication et injection batch.

    Toutes les sources CSS de l'application s'enregistrent via
    ``register(name, css)``. L'injection dans la page est effectuée
    en un seul appel ``st.markdown`` via ``inject_all()``.

    Caractéristiques :
    - Déduplication par nom de bloc + hash MD5
    - Injection batch unique par cycle de rendu Streamlit
    - Invalidation conditionnelle (changement de thème/mode tablette)
    - Intégration avec ``StyleSheet`` pour les classes atomiques
    """

    # Registre global : name → css_string
    _registry: dict[str, str] = {}

    # Hash du dernier CSS injecté (pour détecter les changements)
    _SESSION_KEY = "_css_manager_hash_v2"

    @classmethod
    def register(cls, name: str, css: str) -> None:
        """Enregistre un bloc CSS sous un nom unique.

        Si le même nom est enregistré à nouveau avec un contenu différent,
        il est mis à jour et ``inject_all()`` le réinjectera.

        Args:
            name: Identifiant unique du bloc (ex: 'app-styles', 'theme', 'a11y').
            css: Contenu CSS brut (sans ``<style>``).
        """
        cls._registry[name] = css.strip()

    @classmethod
    def unregister(cls, name: str) -> None:
        """Retire un bloc CSS du registre."""
        cls._registry.pop(name, None)

    @classmethod
    def inject_all(cls) -> None:
        """Injecte tous les blocs CSS enregistrés en un seul appel.

        Utilise un hash MD5 du CSS complet pour éviter la réinjection
        si le contenu n'a pas changé entre deux cycles de rendu.
        """
        if not cls._registry:
            return

        # Aussi injecter les classes atomiques de StyleSheet
        from src.ui.system.css import StyleSheet

        # Construire le CSS complet
        parts = [f"/* [{name}] */\n{css}" for name, css in sorted(cls._registry.items())]

        # Ajouter les classes atomiques en attente
        stylesheet_css = StyleSheet.get_all_css()
        if stylesheet_css:
            parts.append(f"/* [stylesheet-atomic] */\n{stylesheet_css}")

        full_css = "\n\n".join(parts)

        # Hash pour déduplication inter-cycles
        css_hash = hashlib.md5(full_css.encode()).hexdigest()

        if cls._SESSION_KEY not in st.session_state:
            st.session_state[cls._SESSION_KEY] = ""

        if st.session_state[cls._SESSION_KEY] != css_hash:
            st.markdown(f"<style>\n{full_css}\n</style>", unsafe_allow_html=True)
            st.session_state[cls._SESSION_KEY] = css_hash

            # Marquer les classes atomiques comme injectées
            StyleSheet.mark_all_injected()

            logger.debug(
                "CSSManager: injecté %d blocs (%d octets, hash=%s)",
                len(cls._registry),
                len(full_css),
                css_hash[:8],
            )
        else:
            logger.debug("CSSManager: CSS inchangé, skip injection")

    @classmethod
    def invalidate(cls) -> None:
        """Force la réinjection au prochain ``inject_all()``.

        À appeler lors d'un changement de thème ou de mode tablette.
        """
        if cls._SESSION_KEY in st.session_state:
            st.session_state[cls._SESSION_KEY] = ""

    @classmethod
    def get_stats(cls) -> dict[str, int]:
        """Statistiques du pipeline CSS."""
        total_size = sum(len(css) for css in cls._registry.values())
        return {
            "registered_blocks": len(cls._registry),
            "total_size_bytes": total_size,
        }

    @classmethod
    def reset(cls) -> None:
        """Reset complet (pour tests)."""
        cls._registry.clear()
        if cls._SESSION_KEY in st.session_state:
            del st.session_state[cls._SESSION_KEY]


def charger_css(nom_fichier: str) -> None:
    """Charge et enregistre un fichier CSS depuis static/css/.

    Le CSS est enregistré dans le CSSManager et sera injecté
    lors du prochain appel à ``CSSManager.inject_all()``.

    Args:
        nom_fichier: Nom du fichier CSS (ex: 'jardin.css')
    """
    if nom_fichier not in _CSS_CACHE:
        chemin = _CSS_DIR / nom_fichier
        if chemin.exists():
            _CSS_CACHE[nom_fichier] = chemin.read_text(encoding="utf-8")
        else:
            return  # Silently skip missing files

    if nom_fichier in _CSS_CACHE:
        CSSManager.register(f"file-{nom_fichier}", _CSS_CACHE[nom_fichier])


__all__ = ["CSSManager", "charger_css"]
