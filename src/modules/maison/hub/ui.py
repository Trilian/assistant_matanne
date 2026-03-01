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
    """Affiche la navigation vers les modules via composant HTML/JS."""
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

    html = """
    <style>
    .modules-grid{display:flex;gap:12px;flex-wrap:wrap;margin-top:8px}
    .tile{flex:1 1 140px;min-width:120px;max-width:220px;padding:12px;border-radius:8px;background:#ffffff;border:1px solid rgba(0,0,0,0.06);text-align:center;text-decoration:none;color:inherit;box-shadow:0 1px 3px rgba(0,0,0,0.04);transition:transform .12s ease,box-shadow .12s ease}
    .tile .icon{font-size:26px;display:block;margin-bottom:6px}
    .tile .title{font-weight:600}
    .tile .subtitle{font-size:12px;color:#6b7280;margin-top:4px}
    .tile:hover{transform:translateY(-4px);box-shadow:0 8px 18px rgba(0,0,0,0.08)}
    </style>
    <div class="modules-grid">
    """
    for m in modules:
        key_q = urllib.parse.quote(m["key"], safe="")
        html += (
            f'<a class="tile" href="?navigate={key_q}" title="{m["title"]} - {m["subtitle"]}">'
            + f'<span class="icon">{m["icon"]}</span>'
            + f'<span class="title">{m["title"]}</span>'
            + f'<div class="subtitle">{m["subtitle"]}</div>'
            + "</a>"
        )

    html += "</div>"

    # Height augmenté pour éviter coupe sur petits écrans
    components.html(html, height=220, scrolling=False)


def afficher_modules_fallback(stats: dict):
    """Fallback Streamlit si le composant HTML/JS ne s'affiche pas."""
    st.markdown("#### 🏠 Sections (Fallback)")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("🌳 Jardin — Potager", key="btn_jardin_fb", use_container_width=True):
            GestionnaireEtat.naviguer_vers("maison.jardin")
            rerun()
    with col2:
        if st.button(
            "🏡 Entretien — Équipements", key="btn_entretien_fb", use_container_width=True
        ):
            GestionnaireEtat.naviguer_vers("maison.entretien")
            rerun()
    with col3:
        if st.button(
            "💡 Charges — Énergie & contrats", key="btn_charges_fb", use_container_width=True
        ):
            GestionnaireEtat.naviguer_vers("maison.charges")
            rerun()
    with col4:
        if st.button(
            "💰 Dépenses — Budget maison", key="btn_depenses_fb", use_container_width=True
        ):
            GestionnaireEtat.naviguer_vers("maison.depenses")
            rerun()
    with col5:
        if st.button("🏘️ Plan — Visualisation", key="btn_plan_fb", use_container_width=True):
            GestionnaireEtat.naviguer_vers("maison.visualisation")
            rerun()


@auto_refresh(seconds=120)
def afficher_stats_mois(stats: dict):
    """Affiche les mini stats du mois (auto-refresh 120s)."""
    heures = stats.get("temps_mois_heures", 0)
    zones = stats.get("zones_jardin", 0)
    pieces = stats.get("pieces", 0)
    autonomie = stats.get("autonomie_pourcent", None)

    def pretty_num(v, fmt="{:.0f}"):
        return fmt.format(v) if v else "—"

    heures_display = pretty_num(heures, "{:.1f} h")
    zones_display = pretty_num(zones, "{:.0f}")
    pieces_display = pretty_num(pieces, "{:.0f}")
    autonomie_display = (f"{autonomie} %") if autonomie else "—"

    st.markdown(
        f"""
        <div class="stats-mini">
            <div class="stat-item">
                <div class="stat-value">{heures_display}</div>
                <div class="stat-label">Ce mois</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{zones_display}</div>
                <div class="stat-label">Zones jardin</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{pieces_display}</div>
                <div class="stat-label">Pièces</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{autonomie_display}</div>
                <div class="stat-label">Autonomie</div>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )
