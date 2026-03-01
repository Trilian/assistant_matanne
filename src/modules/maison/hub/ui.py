"""
Maison - Composants UI.
"""

import urllib.parse
from datetime import date

import streamlit as st
import streamlit.components.v1 as components

from src.core.state import GestionnaireEtat, rerun
from src.ui.fragments import auto_refresh


def afficher_header():
    """Affiche l'en-tête principal."""
    aujourdhui = date.today()
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    mois = [
        "janvier",
        "février",
        "mars",
        "avril",
        "mai",
        "juin",
        "juillet",
        "août",
        "septembre",
        "octobre",
        "novembre",
        "décembre",
    ]

    date_str = f"{jours[aujourdhui.weekday()]} {aujourdhui.day} {mois[aujourdhui.month - 1]} {aujourdhui.year}"

    st.markdown(
        f"""
        <div class="hub-main-header">
            <h1>🏠 Maison</h1>
            <div class="hub-date">📅 {date_str}</div>
        </div>
    """,
        unsafe_allow_html=True,
    )


def afficher_taches(taches: list[dict], charge: dict):
    """Affiche la section des tâches du jour."""
    niveau_class = f"charge-{charge['niveau']}"
    jauge_class = f"jauge-{charge['niveau']}"

    st.markdown(
        f"""
        <div class="taches-section">
            <div class="taches-header">
                <span class="taches-title">📋 Aujourd'hui</span>
                <span class="charge-badge {niveau_class}">
                    {charge["nb_taches"]} tâches • {charge["temps_str"]}
                </span>
            </div>
            <div class="jauge-container">
                <div class="jauge-fill {jauge_class}" style="width: {charge["pourcent"]}%"></div>
            </div>
    """,
        unsafe_allow_html=True,
    )

    # Liste des tâches
    domaine_icons = {
        "jardin": ("🌳", "tache-jardin"),
        "entretien": ("🏡", "tache-entretien"),
        "charges": ("💡", "tache-charges"),
        "depenses": ("💰", "tache-depenses"),
    }

    for tache in taches:
        icon, icon_class = domaine_icons.get(tache["domaine"], ("📝", ""))
        meta_parts = []
        if "zone" in tache:
            meta_parts.append(tache["zone"])
        if "piece" in tache:
            meta_parts.append(tache["piece"])
        if "contrat" in tache:
            meta_parts.append(tache["contrat"])
        meta = " • ".join(meta_parts) if meta_parts else tache["domaine"].capitalize()

        st.markdown(
            f"""
            <div class="tache-item">
                <div class="tache-icon {icon_class}">{icon}</div>
                <div class="tache-content">
                    <div class="tache-titre">{tache["titre"]}</div>
                    <div class="tache-meta">{meta}</div>
                </div>
                <div class="tache-duree">{tache["duree_min"]} min</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


@auto_refresh(seconds=60)
def afficher_alertes(alertes: list[dict]):
    """Affiche les alertes actives (auto-refresh 60s)."""
    if not alertes:
        return

    st.markdown("#### 🚨 À noter")

    for alerte in alertes:
        type_class = f"alerte-{alerte['type']}"
        st.markdown(
            f"""
            <div class="alerte-card {type_class}">
                <span class="alerte-icon">{alerte["icon"]}</span>
                <div class="alerte-content">
                    <div class="alerte-titre">{alerte["titre"]}</div>
                    <div class="alerte-desc">{alerte["description"]}</div>
                </div>
            </div>
        """,
            unsafe_allow_html=True,
        )


def afficher_modules(stats: dict):
    """Affiche la navigation vers les modules."""
    st.markdown("#### 🏠 Sections")

    modules = [
        {"key": "maison.jardin", "icon": "🌳", "title": "Jardin", "subtitle": "Potager"},
        {"key": "maison.entretien", "icon": "🏡", "title": "Entretien", "subtitle": "Équipements"},
        {
            "key": "maison.charges",
            "icon": "💡",
            "title": "Charges",
            "subtitle": "Énergie & contrats",
        },
        {"key": "maison.depenses", "icon": "💰", "title": "Dépenses", "subtitle": "Budget maison"},
        {"key": "maison.visualisation", "icon": "🏘️", "title": "Plan", "subtitle": "Visualisation"},
    ]

    cols = st.columns(3)
    for i, m in enumerate(modules):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"**{m['icon']} {m['title']}**")
                st.caption(m["subtitle"])
                if st.button("Ouvrir", key=f"btn_nav_{m['key']}", use_container_width=True):
                    from src.core.state import GestionnaireEtat, rerun

                    GestionnaireEtat.naviguer_vers(m["key"])
                    rerun()


def afficher_modules_fallback(stats: dict):
    pass


@auto_refresh(seconds=120)
def afficher_stats_mois(stats: dict):
    """Affiche les mini stats du mois (auto-refresh 120s)."""
    heures = stats.get("temps_mois_heures", 0)
    zones = stats.get("zones_jardin", 0)
    pieces = stats.get("pieces", 0)
    autonomie = stats.get("autonomie_pourcent", None)

    heures_display = f"{heures:.1f} h" if heures else "—"
    zones_display = f"{zones:.0f}" if zones else "—"
    pieces_display = f"{pieces:.0f}" if pieces else "—"
    autonomie_display = f"{autonomie} %" if autonomie else "—"

    st.markdown("#### 📊 Statistiques")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Ce mois", heures_display)
    with col2:
        st.metric("Zones jardin", zones_display)
    with col3:
        st.metric("Pièces", pieces_display)
    with col4:
        st.metric("Autonomie", autonomie_display)
