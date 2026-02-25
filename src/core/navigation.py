"""
Navigation moderne basée sur st.navigation() + st.Page().

Fournit le routage natif Streamlit avec deep-linking et gestion
des sections de navigation (sidebar automatique).

Ce module remplace:
- RouteurOptimise.charger_module() → st.navigation() + st.Page()
- MODULES_MENU dans sidebar.py → sections st.navigation()
- Les boutons sidebar manuels → navigation native Streamlit

Compatibilité:
- GestionnaireEtat.naviguer_vers() continue de fonctionner via st.switch_page()
- Les modules gardent leur fonction app() comme point d'entrée
"""

from __future__ import annotations

import importlib
import logging
import time
from typing import Any

import streamlit as st

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CACHE DES MODULES CHARGÉS
# ═══════════════════════════════════════════════════════════

_module_cache: dict[str, Any] = {}
_load_times: dict[str, float] = {}


def _charger_et_executer(module_path: str, module_key: str) -> None:
    """Charge un module et exécute sa fonction app().

    Utilisé comme callable pour st.Page().
    """
    from src.core.state import GestionnaireEtat

    # Mettre à jour l'état pour garder la cohérence
    GestionnaireEtat.naviguer_vers(module_key)

    start = time.time()

    if module_path not in _module_cache:
        try:
            module = importlib.import_module(module_path)
            _module_cache[module_path] = module
            _load_times[module_path] = time.time() - start
            logger.info(
                f"📦 Module chargé: {module_path} ({_load_times[module_path] * 1000:.0f}ms)"
            )
        except Exception as e:
            logger.exception(f"❌ Erreur chargement {module_path}")
            st.error(f"❌ Erreur chargement module: {e}")
            return
    else:
        module = _module_cache[module_path]

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
# DÉFINITION DES PAGES — Structure de navigation
# ═══════════════════════════════════════════════════════════


def construire_pages() -> dict[str, list[st.Page]]:
    """Construit les pages groupées par section pour st.navigation().

    Returns:
        Dict section_name → list[st.Page] pour st.navigation()
    """
    pages: dict[str, list[st.Page]] = {}

    # ── Accueil ──
    pages[""] = [
        _creer_page("accueil", "src.modules.accueil", "Accueil", "🏠"),
    ]

    # ── Planning ──
    pages["📅 Planning"] = [
        _creer_page(
            "planning.cockpit",
            "src.modules.planning.cockpit_familial",
            "Cockpit Familial",
            "🎯",
        ),
        _creer_page("planning.calendrier", "src.modules.planning.calendrier", "Calendrier", "📅"),
        _creer_page(
            "planning.templates_ui", "src.modules.planning.templates_ui", "Templates", "📋"
        ),
        _creer_page("planning.timeline_ui", "src.modules.planning.timeline_ui", "Timeline", "📊"),
    ]

    # ── Cuisine ──
    pages["🍳 Cuisine"] = [
        _creer_page(
            "cuisine.planificateur_repas",
            "src.modules.cuisine.planificateur_repas",
            "Planifier Repas",
            "🍽️",
        ),
        _creer_page(
            "cuisine.batch_cooking_detaille",
            "src.modules.cuisine.batch_cooking_detaille",
            "Batch Cooking",
            "🍳",
        ),
        _creer_page("cuisine.courses", "src.modules.cuisine.courses", "Courses", "🛒"),
        _creer_page("cuisine.recettes", "src.modules.cuisine.recettes", "Recettes", "📋"),
        _creer_page("cuisine.inventaire", "src.modules.cuisine.inventaire", "Inventaire", "🥫"),
    ]

    # ── Famille ──
    pages["👨‍👩‍👧‍👦 Famille"] = [
        _creer_page("famille.hub", "src.modules.famille.hub_famille", "Hub Famille", "🏠"),
        _creer_page("famille.jules", "src.modules.famille.jules", "Jules", "👶"),
        _creer_page(
            "famille.jules_planning", "src.modules.famille.jules_planning", "Planning Jules", "📅"
        ),
        _creer_page("famille.suivi_perso", "src.modules.famille.suivi_perso", "Mon Suivi", "💪"),
        _creer_page("famille.weekend", "src.modules.famille.weekend", "Weekend", "🎉"),
        _creer_page("famille.achats_famille", "src.modules.famille.achats_famille", "Achats", "🛍️"),
        _creer_page("famille.activites", "src.modules.famille.activites", "Activités", "🎭"),
        _creer_page("famille.routines", "src.modules.famille.routines", "Routines", "⏰"),
    ]

    # ── Maison ──
    pages["🏠 Maison"] = [
        _creer_page("maison.hub", "src.modules.maison.hub", "Hub Maison", "🏠"),
        _creer_page("maison.jardin", "src.modules.maison.jardin", "Jardin", "🌱"),
        _creer_page("maison.jardin_zones", "src.modules.maison.jardin_zones", "Zones Jardin", "🌿"),
        _creer_page("maison.entretien", "src.modules.maison.entretien", "Entretien", "🏡"),
        _creer_page("maison.charges", "src.modules.maison.charges", "Charges", "💡"),
        _creer_page("maison.depenses", "src.modules.maison.depenses", "Dépenses", "💰"),
        _creer_page("maison.eco_tips", "src.modules.maison.eco_tips", "Éco-Tips", "🌿"),
        _creer_page("maison.energie", "src.modules.maison.energie", "Énergie", "⚡"),
        _creer_page("maison.meubles", "src.modules.maison.meubles", "Meubles", "🪑"),
        _creer_page("maison.projets", "src.modules.maison.projets", "Projets", "🏗️"),
    ]

    # ── Jeux ──
    pages["🎲 Jeux"] = [
        _creer_page("jeux.paris", "src.modules.jeux.paris", "Paris Sportifs", "⚽"),
        _creer_page("jeux.loto", "src.modules.jeux.loto", "Loto", "🎰"),
    ]

    # ── Outils ──
    pages["🔧 Outils"] = [
        _creer_page("barcode", "src.modules.utilitaires.barcode", "Code-barres", "📱"),
        _creer_page(
            "scan_factures", "src.modules.utilitaires.scan_factures", "Scan Factures", "🧾"
        ),
        _creer_page(
            "recherche_produits", "src.modules.utilitaires.recherche_produits", "Produits", "🔍"
        ),
        _creer_page("rapports", "src.modules.utilitaires.rapports", "Rapports", "📊"),
        _creer_page(
            "notifications_push",
            "src.modules.utilitaires.notifications_push",
            "Notifications",
            "🔔",
        ),
        _creer_page("chat_ia", "src.modules.utilitaires.chat_ia", "Chat IA", "💬"),
    ]

    # ── Paramètres ──
    pages["⚙️ Configuration"] = [
        _creer_page("parametres", "src.modules.parametres", "Paramètres", "⚙️"),
        _creer_page("design_system", "src.modules.design_system", "Design System", "🎨"),
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
    """Statistiques de chargement des modules."""
    return {
        "cached_modules": len(_module_cache),
        "total_load_time": sum(_load_times.values()),
        "average_load_time": (sum(_load_times.values()) / len(_load_times) if _load_times else 0),
        "load_times": _load_times,
    }
