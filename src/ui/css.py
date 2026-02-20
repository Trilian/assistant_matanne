"""Chargeur de fichiers CSS statiques pour les modules Streamlit."""

from pathlib import Path

import streamlit as st

_CSS_DIR = Path(__file__).resolve().parent.parent.parent / "static" / "css"
_CSS_CACHE: dict[str, str] = {}


def charger_css(nom_fichier: str) -> None:
    """Charge et injecte un fichier CSS depuis static/css/.

    Args:
        nom_fichier: Nom du fichier CSS (ex: 'jardin.css')
    """
    if nom_fichier not in _CSS_CACHE:
        chemin = _CSS_DIR / nom_fichier
        if chemin.exists():
            _CSS_CACHE[nom_fichier] = chemin.read_text(encoding="utf-8")
        else:
            return  # Silently skip missing files

    st.markdown(f"<style>{_CSS_CACHE[nom_fichier]}</style>", unsafe_allow_html=True)
