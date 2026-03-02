"""
Dashboard - Résumés par module
Cartes de résumé compactes pour chaque module métier (design auto-portant).

Chaque card génère un bloc HTML unique pour le titre + métriques, puis
un bouton Streamlit pour la navigation. Pas de st.columns imbriqués
(évite la troncature dans des colonnes étroites).
"""

from datetime import date

import streamlit as st

from src.ui.keys import KeyNamespace
from src.ui.tokens import Couleur
from src.ui.tokens_semantic import Sem

_keys = KeyNamespace("tableau_de_bord")


def _card_css(border_color: str) -> str:
    return (
        f"background:{Sem.SURFACE_ALT};border-radius:12px;"
        f"border-left:4px solid {border_color};"
        f"padding:1rem 1.2rem 0.8rem 1.2rem;margin-bottom:0.5rem;"
    )


def _metric_html(label: str, value: str, sub: str = "") -> str:
    """Génère une mini-metric en HTML (flex item)."""
    sub_html = (
        f'<div style="font-size:0.7rem;color:{Sem.ON_SURFACE_SECONDARY};'
        f'margin-top:1px;white-space:nowrap;">{sub}</div>'
        if sub
        else ""
    )
    return (
        f'<div style="flex:1;min-width:0;text-align:center;">'
        f'<div style="font-size:1.3rem;font-weight:700;line-height:1.2;">{value}</div>'
        f'<div style="font-size:0.72rem;color:{Sem.ON_SURFACE_SECONDARY};'
        f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{label}</div>'
        f"{sub_html}"
        f"</div>"
    )


def _metrics_row(*metrics_html: str) -> str:
    items = "".join(metrics_html)
    return f'<div style="display:flex;gap:6px;margin:0.5rem 0;">{items}</div>'


# ═══════════════════════════════════════════════════════════
# CARDS
# ═══════════════════════════════════════════════════════════


def afficher_cuisine_summary():
    """Résumé module Cuisine."""
    from src.core.state import GestionnaireEtat, rerun
    from src.services.cuisine.recettes import obtenir_service_recettes

    try:
        stats = obtenir_service_recettes().get_stats(
            count_filters={
                "rapides": {"temps_preparation": {"lte": 30}},
                "bebe": {"compatible_bebe": True},
            }
        )
        total = stats.get("total", 0)
        rapides = stats.get("rapides", 0)
        bebe = stats.get("bebe", 0)
    except Exception:
        total = rapides = bebe = "—"

    st.markdown(
        f'<div style="{_card_css(Couleur.SUCCESS)}">'
        f'<div style="font-weight:600;font-size:0.95rem;margin-bottom:0.4rem;">💡 Recettes</div>'
        + _metrics_row(
            _metric_html("Total", str(total)),
            _metric_html("⚡ Rapides", str(rapides)),
            _metric_html("👶 Bébé", str(bebe)),
        )
        + "</div>",
        unsafe_allow_html=True,
    )
    if st.button(
        "Voir les recettes →",
        key=_keys("nav_recettes"),
        use_container_width=True,
        help="Accéder à la liste des recettes",
    ):
        GestionnaireEtat.naviguer_vers("cuisine.recettes")
        rerun()


def afficher_inventaire_summary():
    """Résumé Inventaire."""
    from src.core.state import GestionnaireEtat, rerun
    from src.services.inventaire import obtenir_service_inventaire

    try:
        inventaire = obtenir_service_inventaire().get_inventaire_complet()
        total_art = len(inventaire)
        stock_bas = len([a for a in inventaire if a.get("statut") == "sous_seuil"])
        critiques = len([a for a in inventaire if a.get("statut") == "critique"])
        peremption = len([a for a in inventaire if a.get("statut") == "peremption_proche"])
    except Exception:
        total_art = stock_bas = critiques = peremption = "—"

    alerte_sub = "⚠️ urgent" if isinstance(critiques, int) and critiques > 0 else ""
    peri_sub = f"⏳ {peremption} périme" if isinstance(peremption, int) and peremption > 0 else ""

    st.markdown(
        f'<div style="{_card_css(Couleur.INFO)}">'
        f'<div style="font-weight:600;font-size:0.95rem;margin-bottom:0.4rem;">📦 Inventaire</div>'
        + _metrics_row(
            _metric_html("Articles", str(total_art)),
            _metric_html("Stock bas", str(stock_bas), peri_sub),
            _metric_html("Critiques", str(critiques), alerte_sub),
        )
        + "</div>",
        unsafe_allow_html=True,
    )
    if st.button(
        "Gérer l'inventaire →",
        key=_keys("nav_inventaire"),
        use_container_width=True,
        help="Voir et gérer le stock",
    ):
        GestionnaireEtat.naviguer_vers("cuisine.inventaire")
        rerun()


def afficher_courses_summary():
    """Résumé Courses."""
    from src.core.state import GestionnaireEtat, rerun
    from src.services.cuisine.courses import obtenir_service_courses

    try:
        liste = obtenir_service_courses().get_liste_courses()
        total_c = len(liste)
        haute = len([a for a in liste if a.get("priorite") == "haute"])
        moyenne = len([a for a in liste if a.get("priorite") == "moyenne"])
        top_art = [a.get("ingredient_nom", "?") for a in liste if a.get("priorite") == "haute"][:3]
    except Exception:
        total_c = haute = moyenne = "—"
        top_art = []

    top_html = ""
    if top_art:
        items = ", ".join(top_art)
        top_html = (
            f'<div style="font-size:0.75rem;color:{Sem.ON_SURFACE_SECONDARY};'
            f'margin-top:4px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" '
            f'title="{items}">🔴 {items}</div>'
        )

    st.markdown(
        f'<div style="{_card_css(Couleur.WARNING)}">'
        f'<div style="font-weight:600;font-size:0.95rem;margin-bottom:0.4rem;">🛒 Courses</div>'
        + _metrics_row(
            _metric_html("Total", str(total_c)),
            _metric_html("Urgent", str(haute)),
            _metric_html("Normal", str(moyenne)),
        )
        + top_html
        + "</div>",
        unsafe_allow_html=True,
    )
    if st.button(
        "Voir la liste →",
        key=_keys("nav_courses"),
        use_container_width=True,
        help="Accéder à la liste de courses",
    ):
        GestionnaireEtat.naviguer_vers("cuisine.courses")
        rerun()


def afficher_planning_summary():
    """Résumé Planning semaine."""
    from src.core.state import GestionnaireEtat, rerun
    from src.services.cuisine.planning import obtenir_service_planning

    try:
        planning = obtenir_service_planning().get_planning()
        if planning and planning.repas:
            total_repas = len(planning.repas)
            repas_bebe = len([r for r in planning.repas if getattr(r, "compatible_bebe", False)])
            aujourd_hui = date.today()
            repas_auj = [
                getattr(r, "recette_nom", None) or getattr(r, "type_repas", "?")
                for r in planning.repas
                if hasattr(r, "date") and r.date == aujourd_hui
            ]
        else:
            total_repas = 0
            repas_bebe = 0
            repas_auj = []
    except Exception:
        total_repas = repas_bebe = "—"
        repas_auj = []

    auj_html = ""
    if repas_auj:
        auj_text = " · ".join(str(r) for r in repas_auj[:2])
        auj_html = (
            f'<div style="font-size:0.75rem;color:{Sem.ON_SURFACE_SECONDARY};'
            f'margin-top:4px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" '
            f'title="{auj_text}">📅 {auj_text}</div>'
        )
    elif total_repas == 0:
        auj_html = (
            f'<div style="font-size:0.75rem;color:{Sem.ON_SURFACE_SECONDARY};'
            f'margin-top:4px;">Aucun repas planifié</div>'
        )

    st.markdown(
        f'<div style="{_card_css(Couleur.ACCENT)}">'
        f'<div style="font-weight:600;font-size:0.95rem;margin-bottom:0.4rem;">🍽️ Planning semaine</div>'
        + _metrics_row(
            _metric_html("Repas", str(total_repas)),
            _metric_html("👶 Bébé", str(repas_bebe)),
        )
        + auj_html
        + "</div>",
        unsafe_allow_html=True,
    )
    if st.button(
        "Voir le planning →",
        key=_keys("nav_planning"),
        use_container_width=True,
        help="Planification des repas de la semaine",
    ):
        GestionnaireEtat.naviguer_vers("cuisine_repas")
        rerun()
