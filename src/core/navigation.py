"""
Navigation moderne basée sur st.navigation() + st.Page().

Fournit le routage natif Streamlit avec deep-linking et gestion
des sections de navigation (sidebar automatique).

Les pages sont définies déclarativement dans ``pages_config.py``.
Ce module se contente de les convertir en objets ``st.Page``.

Ce module remplace:
- RouteurOptimise.charger_module() → st.navigation() + st.Page()
- MODULES_MENU dans sidebar.py → sections st.navigation()
- Les boutons sidebar manuels → navigation native Streamlit

Compatibilité:
- GestionnaireEtat.naviguer_vers() continue de fonctionner via st.switch_page()
- Les modules gardent leur fonction app() comme point d'entrée
"""

from __future__ import annotations

import logging

import streamlit as st

from .lazy_loader import ChargeurModuleDiffere
from .pages_config import PAGES

logger = logging.getLogger(__name__)


def _charger_et_executer(module_path: str, module_key: str) -> None:
    """Charge un module et exécute sa fonction app().

    Utilisé comme callable pour st.Page().
    Délègue le cache au ChargeurModuleDiffere (source unique).
    """
    from src.core.state import GestionnaireEtat

    # Mettre à jour l'état pour garder la cohérence
    GestionnaireEtat.naviguer_vers(module_key)

    try:
        module = ChargeurModuleDiffere.charger(module_path)
    except Exception as e:
        logger.exception(f"❌ Erreur chargement {module_path}")
        st.error(f"❌ Erreur chargement module: {e}")
        return

    # Exécuter le point d'entrée du module
    if hasattr(module, "app"):
        module.app()
    elif hasattr(module, "afficher"):
        module.afficher()
    else:
        st.error(f"❌ Module '{module_key}' sans point d'entrée app()/afficher()")


def _creer_page(key: str, path: str, title: str, icon: str = "") -> st.Page:
    """Crée un st.Page pour un module."""
    display_title = f"{icon} {title}" if icon else title

    def _runner():
        _charger_et_executer(path, key)

    return st.Page(
        _runner,
        title=display_title,
        url_path=key.replace(".", "_"),  # Replace dots with underscores to avoid nested paths
        default=(key == "accueil"),
    )


# ═══════════════════════════════════════════════════════════
# CONSTRUCTION DES PAGES DEPUIS LA CONFIG DÉCLARATIVE
# ═══════════════════════════════════════════════════════════


def construire_pages() -> dict[str, list[st.Page]]:
    """Construit les pages groupées par section pour st.navigation().

    Lit la configuration déclarative depuis ``pages_config.PAGES``
    et génère les objets ``st.Page`` correspondants.

    Returns:
        Dict section_name → list[st.Page] pour st.navigation()
    """
    pages: dict[str, list[st.Page]] = {}

    for section in PAGES:
        section_name = section["name"]
        pages[section_name] = [
            _creer_page(
                key=page["key"],
                path=page["path"],
                title=page["title"],
                icon=page.get("icon", ""),
            )
            for page in section["pages"]
        ]

    return pages


# Index inversé: module_key → st.Page (pour st.switch_page)
_pages_index: dict[str, st.Page] = {}


def initialiser_navigation() -> st.Page:
    """Initialise st.navigation() et retourne la page sélectionnée.

    Doit être appelé UNE SEULE FOIS dans app.py, AVANT tout autre output.
    """
    pages = construire_pages()

    # Construire l'index inversé pour switch_page
    for section_pages in pages.values():
        for page in section_pages:
            # Extraire la clé depuis url_path
            url = page.url_path.replace("/", ".")
            _pages_index[url] = page

    # Navigation native Streamlit
    page_selectionnee = st.navigation(pages)

    return page_selectionnee


def obtenir_page(module_key: str) -> st.Page | None:
    """Retourne le st.Page pour un module_key donné (pour switch_page)."""
    return _pages_index.get(module_key)


def obtenir_stats() -> dict:
    """Statistiques de chargement des modules (délègue à ChargeurModuleDiffere)."""
    return ChargeurModuleDiffere.obtenir_statistiques()
