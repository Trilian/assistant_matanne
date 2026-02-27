"""
Navigation moderne basée sur st.navigation() + st.Page().

Fournit le routage natif Streamlit avec deep-linking et gestion
des sections de navigation (sidebar automatique).

Les pages sont définies déclarativement dans ``pages_config.py``.
Ce module se contente de les convertir en objets ``st.Page``.

Fonctionnalités v2 (pages cachées):
- Les pages ``hidden=True`` sont enregistrées dans st.navigation()
  (donc routables via URL et switch_page) mais masquées de la sidebar
  via injection CSS ciblée.
- Un bouton « ⬅️ Retour » est automatiquement affiché en haut de
  chaque page cachée, pointant vers la page ``parent``.

Compatibilité:
- GestionnaireEtat.naviguer_vers() continue de fonctionner via st.switch_page()
- Les modules gardent leur fonction app() comme point d'entrée
"""

from __future__ import annotations

import logging

import streamlit as st

from .lazy_loader import ChargeurModuleDiffere
from .pages_config import PAGES, PageConfig

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# REGISTRE DES PAGES CACHÉES
# ═══════════════════════════════════════════════════════════

# url_path → parent module_key (pour le bouton retour)
_hidden_url_paths: dict[str, str] = {}

# Toutes les configs par key (pour lookup icône/titre parent)
_pages_config_by_key: dict[str, PageConfig] = {}


def _charger_et_executer(module_path: str, module_key: str) -> None:
    """Charge un module et exécute sa fonction app().

    Utilisé comme callable pour st.Page().
    Délègue le cache au ChargeurModuleDiffere (source unique).

    Si la page est cachée (hidden), affiche automatiquement un
    bouton « ⬅️ Retour » vers le hub parent.
    """
    from src.core.state import GestionnaireEtat

    # Mettre à jour l'état de navigation (sans switch_page, on est déjà dessus)
    etat = GestionnaireEtat.obtenir()
    if etat.module_actuel != module_key:
        etat.module_precedent = etat.module_actuel
        etat.historique_navigation.append(module_key)
        if len(etat.historique_navigation) > 50:
            etat.historique_navigation = etat.historique_navigation[-50:]
    etat.module_actuel = module_key

    # ── Bouton retour automatique pour pages cachées ──────
    url_path = module_key.replace(".", "_")
    if url_path in _hidden_url_paths:
        parent_key = _hidden_url_paths[url_path]
        parent_cfg = _pages_config_by_key.get(parent_key, {})
        parent_icon = parent_cfg.get("icon", "")
        parent_title = parent_cfg.get("title", "Retour")
        label = f"⬅️ {parent_icon} {parent_title}"

        if st.button(label, key=f"_retour_{module_key}"):
            page = obtenir_page(parent_key)
            if page:
                st.switch_page(page)
            return

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
        url_path=key.replace(".", "_"),
        default=(key == "accueil"),
    )


# ═══════════════════════════════════════════════════════════
# CSS POUR MASQUER LES PAGES CACHÉES DE LA SIDEBAR
# ═══════════════════════════════════════════════════════════


def _injecter_css_pages_cachees() -> None:
    """Injecte du CSS ciblé pour masquer les pages hidden de la sidebar.

    Cible chaque page par son ``url_path`` dans les liens du nav sidebar.
    Pattern déjà validé dans ``src/ui/components/mode_focus.py``.
    """
    if not _hidden_url_paths:
        return

    selecteurs = []
    for url_path in _hidden_url_paths:
        # Streamlit génère des liens comme href="/famille_jules"
        selecteurs.append(f'[data-testid="stSidebarNav"] a[href$="/{url_path}"]')

    # Par blocs de 20 sélecteurs max pour éviter les CSS trop longs
    css_parts = []
    for i in range(0, len(selecteurs), 20):
        batch = selecteurs[i : i + 20]
        css_parts.append(",\n".join(batch) + " { display: none !important; }")

    css = "\n".join(css_parts)
    st.markdown(f"<style>\n{css}\n</style>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# CONSTRUCTION DES PAGES DEPUIS LA CONFIG DÉCLARATIVE
# ═══════════════════════════════════════════════════════════


def construire_pages() -> dict[str, list[st.Page]]:
    """Construit les pages groupées par section pour st.navigation().

    Toutes les pages (visibles ET cachées) sont incluses dans le dict
    retourné — elles doivent être enregistrées pour que ``st.switch_page``
    et les URL directes fonctionnent. Le masquage est purement visuel (CSS).

    Returns:
        Dict section_name → list[st.Page] pour st.navigation()
    """
    pages: dict[str, list[st.Page]] = {}

    for section in PAGES:
        section_name = section["name"]
        section_pages: list[st.Page] = []

        for page_cfg in section["pages"]:
            key = page_cfg["key"]
            url_path = key.replace(".", "_")

            # Enregistrer dans le registre de lookup
            _pages_config_by_key[key] = page_cfg

            # Enregistrer les pages cachées pour le CSS + bouton retour
            if page_cfg.get("hidden", False):
                parent = page_cfg.get("parent", "accueil")
                _hidden_url_paths[url_path] = parent

            section_pages.append(
                _creer_page(
                    key=key,
                    path=page_cfg["path"],
                    title=page_cfg["title"],
                    icon=page_cfg.get("icon", ""),
                )
            )
            # Associer key → st.Page pour obtenir_page() / switch_page
            _pages_index[key] = section_pages[-1]

        if section_pages:
            pages[section_name] = section_pages

    return pages


# Index inversé: module_key → st.Page (pour st.switch_page)
_pages_index: dict[str, st.Page] = {}


def initialiser_navigation() -> st.Page:
    """Initialise st.navigation() et retourne la page sélectionnée.

    Doit être appelé UNE SEULE FOIS dans app.py, AVANT tout autre output.

    1. Construit toutes les pages (visibles + cachées)
    2. Passe tout à st.navigation() (nécessaire pour le routage)
    3. Injecte le CSS pour masquer les pages cachées de la sidebar
    """
    pages = construire_pages()

    # NOTE: _pages_index est déjà peuplé par construire_pages()
    # (voir le bloc ci-dessus qui associe key → st.Page)

    # Navigation native Streamlit (inclut pages cachées pour le routage)
    page_selectionnee = st.navigation(pages)

    # Masquer les pages cachées de la sidebar (CSS ciblé)
    _injecter_css_pages_cachees()

    return page_selectionnee


def obtenir_page(module_key: str) -> st.Page | None:
    """Retourne le st.Page pour un module_key donné (pour switch_page)."""
    return _pages_index.get(module_key)


def obtenir_stats() -> dict:
    """Statistiques de chargement des modules (délègue à ChargeurModuleDiffere)."""
    return ChargeurModuleDiffere.obtenir_statistiques()
