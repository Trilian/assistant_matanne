"""
Hub Maison - Composants UI.
"""

from datetime import date

import streamlit as st

from src.core.state import GestionnaireEtat


def render_header():
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


def render_taches(taches: list[dict], charge: dict):
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


def render_alertes(alertes: list[dict]):
    """Affiche les alertes actives."""
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


def render_modules(stats: dict):
    """Affiche la navigation vers les modules."""
    st.markdown("#### 📂 Modules")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button(
            "🌳\n\n**Jardin**\n\n" + "Potager", use_container_width=True, key="btn_jardin"
        ):
            GestionnaireEtat.naviguer_vers("maison.jardin")
            st.rerun()

        st.markdown(
            """
            <div style="text-align: center; margin-top: -0.5rem;">
                <span class="module-highlight highlight-success">Tâches auto</span>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        if st.button(
            "🏡\n\n**Entretien**\n\n" + "Équipements", use_container_width=True, key="btn_entretien"
        ):
            GestionnaireEtat.naviguer_vers("maison.entretien")
            st.rerun()

        st.markdown(
            """
            <div style="text-align: center; margin-top: -0.5rem;">
                <span class="module-highlight highlight-info">Score maison</span>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        if st.button(
            "💡\n\n**Charges**\n\nÉnergie & contrats", use_container_width=True, key="btn_charges"
        ):
            GestionnaireEtat.naviguer_vers("maison.charges")
            st.rerun()

        st.markdown(
            """
            <div style="text-align: center; margin-top: -0.5rem;">
                <span class="module-highlight highlight-info">Suivi factures</span>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with col4:
        if st.button(
            "💰\n\n**Dépenses**\n\nBudget maison", use_container_width=True, key="btn_depenses"
        ):
            GestionnaireEtat.naviguer_vers("maison.depenses")
            st.rerun()

        st.markdown(
            """
            <div style="text-align: center; margin-top: -0.5rem;">
                <span class="module-highlight highlight-success">Voir budget</span>
            </div>
        """,
            unsafe_allow_html=True,
        )


def render_stats_mois(stats: dict):
    """Affiche les mini stats du mois."""
    heures = stats.get("temps_mois_heures", 0)

    st.markdown(
        f"""
        <div class="stats-mini">
            <div class="stat-item">
                <div class="stat-value">{heures:.1f}h</div>
                <div class="stat-label">Ce mois</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{stats.get("zones_jardin", 0)}</div>
                <div class="stat-label">Zones jardin</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{stats.get("pieces", 0)}</div>
                <div class="stat-label">Pièces</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{stats.get("autonomie_pourcent", 0)}%</div>
                <div class="stat-label">Autonomie</div>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )
