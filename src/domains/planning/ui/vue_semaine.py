"""
Module Vue Semaine - Dashboard détaillé de la semaine

Vue intelligente jour par jour avec :
- Charge équilibrée
- Alertes contextuelles
- Suggestions d'amélioration
- Vue globale charge familiale
"""

from datetime import date, datetime, timedelta

import streamlit as st
import plotly.graph_objects as go

from src.services.planning_unified import get_planning_service

# Logique métier pure
from src.domains.planning.logic.vue_semaine_logic import (
    get_debut_semaine,
    get_jours_semaine,
    calculer_charge_semaine
)

logger = __import__("logging").getLogger(__name__)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# GRAPHIQUES & VISUALISATIONS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def afficher_graphique_charge_semaine(jours: dict) -> None:
    """Affiche graphique de charge semaine"""
    jours_list = list(jours.values())

    jours_noms = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
    charges = [j.charge_score for j in jours_list]

    fig = go.Figure(
        data=[
            go.Bar(
                x=jours_noms,
                y=charges,
                marker=dict(
                    color=charges,
                    colorscale="RdYlGn_r",
                    cmin=0,
                    cmax=100,
                    colorbar=dict(title="Charge"),
                ),
                text=charges,
                textposition="outside",
            )
        ]
    )

    fig.add_hline(y=50, line_dash="dash", line_color="orange", annotation_text="Charge normale")
    fig.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="Surcharge")

    fig.update_layout(
        title="📊 Charge familiale par jour",
        xaxis_title="Jour",
        yaxis_title="Score de charge (0-100)",
        height=400,
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True)


def afficher_graphique_repartition_activites(stats: dict) -> None:
    """Pie chart répartition activités"""
    labels = ["Repas", "Activités", "Projets", "Événements"]
    values = [
        stats.get("total_repas", 0),
        stats.get("total_activites", 0),
        stats.get("total_projets", 0),
        stats.get("total_events", 0),
    ]

    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])

    fig.update_layout(title="🎯 Répartition des événements", height=400)

    st.plotly_chart(fig, use_container_width=True)


def afficher_timeline_jour(jour_complet: dict, jour: date) -> None:
    """Affiche timeline des événements du jour"""
    jour_nom = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"][
        jour.weekday()
    ]

    st.markdown(f"### {jour_nom.capitalize()} {jour.strftime('%d/%m')}")

    # Charge du jour
    charge = jour_complet.get("charge_score", 0)
    charge_label = jour_complet.get("charge", "normal")
    charge_emoji = {"faible": "🎨", "normal": "💰", "intense": "❌"}.get(charge_label, "⚫")

    col1, col2, col3 = st.columns([2, 1, 2])

    with col1:
        st.metric("Charge du jour", f"{charge}/100")

    with col2:
        st.metric("Statut", charge_emoji + " " + charge_label.upper())

    with col3:
        budget = jour_complet.get("budget_jour", 0)
        st.metric("Budget", f"{budget:.0f}€")

    st.markdown("---")

    # Événements triés par type
    st.markdown("#### 🎯 Événements du jour")

    events_grouped = {
        "📷 Repas": jour_complet.get("repas", []),
        "🎨 Activités": jour_complet.get("activites", []),
        "🧹 Projets": jour_complet.get("projets", []),
        "⏰ Routines": jour_complet.get("routines", []),
        "📱… Événements": jour_complet.get("events", []),
    }

    for groupe_nom, events in events_grouped.items():
        if events:
            with st.expander(f"{groupe_nom} ({len(events)})"):
                for event in events:
                    # Affichage flexible selon le type
                    if groupe_nom == "📷 Repas":
                        st.write(f"**{event['type'].capitalize()}**: {event['recette']}")
                        st.caption(f"{event['portions']} portions | {event.get('temps_total', 0)} min")

                    elif groupe_nom == "🎨 Activités":
                        label = "👶" if event.get("pour_jules") else "📅"
                        st.write(f"{label} **{event['titre']}** ({event['type']})")
                        if event.get("budget"):
                            st.caption(f"📋 {event['budget']:.0f}€")

                    elif groupe_nom == "🧹 Projets":
                        priorite_emoji = {
                            "basse": "🎨",
                            "moyenne": "💰",
                            "haute": "❌",
                        }.get(event.get("priorite", "moyenne"), "⚫")
                        st.write(f"{priorite_emoji} **{event['nom']}** ({event['statut']})")

                    elif groupe_nom == "📱… Événements":
                        debut = (
                            event["debut"].strftime("%H:%M")
                            if isinstance(event["debut"], datetime)
                            else "–"
                        )
                        st.write(f"⏰ **{event['titre']}** ({debut})")
                        if event.get("lieu"):
                            st.caption(f"📱 {event['lieu']}")

                    elif groupe_nom == "⏰ Routines":
                        status = "✅" if event.get("fait") else "◯"
                        st.write(f"{status} **{event['nom']}** ({event.get('heure', '–')})")

    # Alertes jour
    if jour_complet.get("alertes"):
        st.markdown("#### âš ï¸ Alertes")
        for alerte in jour_complet["alertes"]:
            st.warning(alerte)

    st.markdown("---")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# MODULE PRINCIPAL
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def app():
    """Module Vue Semaine - Dashboard détaillé"""

    st.title("📊 Vue Semaine Détaillée")
    st.caption("Analyse complète de la charge familiale et répartition des événements")

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # NAVIGATION SEMAINE
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    if "semaine_view_start" not in st.session_state:
        today = date.today()
        st.session_state.semaine_view_start = today - timedelta(days=today.weekday())

    col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])

    with col_nav1:
        if st.button("â¬…ï¸ Semaine précédente", key="prev_semaine_view"):
            st.session_state.semaine_view_start -= timedelta(days=7)
            st.rerun()

    with col_nav2:
        week_start = st.session_state.semaine_view_start
        week_end = week_start + timedelta(days=6)
        st.markdown(
            f"<h3 style='text-align: center;'>{week_start.strftime('%d/%m')} â€” {week_end.strftime('%d/%m/%Y')}</h3>",
            unsafe_allow_html=True,
        )

    with col_nav3:
        if st.button("Semaine suivante âž¡ï¸", key="next_semaine_view"):
            st.session_state.semaine_view_start += timedelta(days=7)
            st.rerun()

    st.markdown("---")

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # CHARGEMENT DONNÉES
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    service = get_planning_service()
    semaine = service.get_semaine_complete(st.session_state.semaine_view_start)

    if not semaine:
        st.error("❌ Erreur lors du chargement de la semaine")
        return

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # ONGLETS VUE
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    tab1, tab2, tab3 = st.tabs(["📱ˆ Analyse Charge", "🎯 Répartition", "📱… Détail Jours"])

    with tab1:
        st.subheader("📱ˆ Analyse de la charge familiale")

        # Graphique charge semaine
        afficher_graphique_charge_semaine(semaine.jours)

        st.markdown("---")

        # Analyses textuelles
        st.markdown("### 🔔 Observations")

        stats = semaine.stats_semaine
        jours_list = list(semaine.jours.values())

        # Jour le plus chargé
        jour_max = max(jours_list, key=lambda j: j.charge_score)
        jour_max_nom = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"][
            (st.session_state.semaine_view_start + timedelta(days=list(semaine.jours.values()).index(jour_max))).weekday()
        ]

        st.info(f"❌ Jour le plus chargé: **{jour_max_nom.capitalize()}** ({jour_max.charge_score}/100)")

        # Jour le moins chargé
        jour_min = min(jours_list, key=lambda j: j.charge_score)
        jour_min_nom = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"][
            (st.session_state.semaine_view_start + timedelta(days=list(semaine.jours.values()).index(jour_min))).weekday()
        ]

        st.success(f"🎨 Jour le plus calme: **{jour_min_nom.capitalize()}** ({jour_min.charge_score}/100)")

        # Couverture Jules
        st.write(
            f"🍽️ **Activités Jules**: {stats.get('activites_jules', 0)} activités "
            f"({stats.get('total_activites', 0)} au total)"
        )

        # Budget
        st.write(f"📋 **Budget semaine**: {stats.get('budget_total', 0):.0f}€")

    with tab2:
        st.subheader("🎯 Répartition des événements")

        col_r1, col_r2 = st.columns(2)

        with col_r1:
            afficher_graphique_repartition_activites(stats)

        with col_r2:
            st.markdown("### 🎯 Résumé")

            st.metric("📷 Repas planifiés", stats.get("total_repas", 0))
            st.metric("🎨 Activités", stats.get("total_activites", 0))
            st.metric("🧹 Projets", stats.get("total_projets", 0))
            st.metric("📱… Événements", stats.get("total_events", 0))

    with tab3:
        st.subheader("📱… Détail par jour")

        jours_semaine = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]

        # Sélection du jour
        jour_select = st.selectbox(
            "Sélectionner un jour",
            jours_semaine,
        )

        jour_index = jours_semaine.index(jour_select)
        jour = st.session_state.semaine_view_start + timedelta(days=jour_index)
        jour_str = jour.isoformat()

        jour_complet = semaine.jours.get(jour_str)

        if jour_complet:
            afficher_timeline_jour(jour_complet.dict(), jour)
        else:
            st.warning(f"Pas de données pour {jour_select.capitalize()}")

    st.markdown("---")

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # ALERTES SEMAINE GLOBALES
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    if semaine.alertes_semaine:
        st.markdown("### ⚠️ Alertes Semaine")
        for alerte in semaine.alertes_semaine:
            st.warning(alerte, icon="âš ï¸")

