"""
Composants d'analyse et graphiques pour le Calendrier Familial.

Intègre les fonctionnalités de vue_ensemble.py et vue_semaine.py:
- Graphique charge semaine (Plotly)
- Graphique répartition activités (Pie)
- Actions prioritaires / alertes
- Métriques clés
- Suggestions d'amélioration
"""

import logging
from datetime import date

import plotly.graph_objects as go
import streamlit as st

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

EMOJIS_CHARGE = {
    "faible": "🚀",
    "normal": "👶",
    "intense": "❌",
}

JOURS_NOMS_COURTS = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]


# ═══════════════════════════════════════════════════════════
# GRAPHIQUES PLOTLY
# ═══════════════════════════════════════════════════════════


def render_graphique_charge_semaine(jours: dict) -> None:
    """Graphique en barres de la charge familiale par jour."""
    jours_list = list(jours.values())
    charges = [j.charge_score for j in jours_list]

    fig = go.Figure(
        data=[
            go.Bar(
                x=JOURS_NOMS_COURTS,
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

    fig.add_hline(y=50, line_dash="dash", line_color="orange", annotation_text="Normal")
    fig.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="Surcharge")

    fig.update_layout(
        title="📊 Charge familiale par jour",
        xaxis_title="Jour",
        yaxis_title="Score (0-100)",
        height=350,
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True, key="analytics_charge_daily")


def render_graphique_repartition(stats: dict) -> None:
    """Graphique camembert de répartition des événements."""
    labels = ["Repas", "Activités", "Projets", "Événements"]
    values = [
        stats.get("total_repas", 0),
        stats.get("total_activites", 0),
        stats.get("total_projets", 0),
        stats.get("total_events", 0),
    ]

    if sum(values) == 0:
        st.info("Aucun événement cette semaine")
        return

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3)])
    fig.update_layout(title="🎯 Répartition des événements", height=350)

    st.plotly_chart(fig, use_container_width=True, key="analytics_repartition")


# ═══════════════════════════════════════════════════════════
# ACTIONS PRIORITAIRES
# ═══════════════════════════════════════════════════════════


def render_actions_prioritaires(alertes: list[str]) -> None:
    """Affiche les actions critiques."""
    if not alertes:
        st.success("✅ Semaine bien équilibrée")
        return

    st.markdown("#### 🎯 Actions à Prendre")
    for alerte in alertes[:5]:
        parts = alerte.split(" - ") if " - " in alerte else [alerte]
        st.warning(parts[-1])


# ═══════════════════════════════════════════════════════════
# MÉTRIQUES CLÉS
# ═══════════════════════════════════════════════════════════


def render_metriques_detaillees(stats: dict, charge_globale: str) -> None:
    """Affiche les KPIs principaux en détail."""
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("🍽️ Repas", stats.get("total_repas", 0))
    with col2:
        st.metric("🎨 Activités", stats.get("total_activites", 0))
    with col3:
        st.metric("👶 Pour Jules", stats.get("activites_jules", 0))
    with col4:
        st.metric("📋 Projets", stats.get("total_projets", 0))
    with col5:
        st.metric("💰 Budget", f"{stats.get('budget_total', 0):.0f}€")

    charge_emoji = EMOJIS_CHARGE.get(charge_globale, "⚫")
    charge_score = stats.get("charge_moyenne", 50)
    st.markdown(f"**{charge_emoji} Charge globale: {charge_globale.upper()}**")
    st.progress(min(charge_score / 100, 1.0))


# ═══════════════════════════════════════════════════════════
# SUGGESTIONS
# ═══════════════════════════════════════════════════════════


def render_suggestions(stats: dict) -> None:
    """Suggère automatiquement des améliorations."""
    suggestions = []

    activites_jules = stats.get("activites_jules", 0)
    if activites_jules == 0:
        suggestions.append(("💡", "Aucune activité pour Jules", "Planifier 2-3 activités adaptées"))
    elif activites_jules < 2:
        suggestions.append(
            ("💡", "Peu d'activités Jules", f"Actuellement {activites_jules} — Recommandé: 3+")
        )

    budget_total = stats.get("budget_total", 0)
    if budget_total > 500:
        suggestions.append(("💰", "Budget élevé", f"{budget_total:.0f}€ cette semaine"))

    if stats.get("total_repas", 0) == 0:
        suggestions.append(("🍽️", "Aucun repas planifié", "Prévoir le planning culinaire"))

    if suggestions:
        for emoji, titre, description in suggestions:
            st.info(f"{emoji} **{titre}**: {description}")
    else:
        st.success("✅ Semaine bien équilibrée")


# ═══════════════════════════════════════════════════════════
# OBSERVATIONS
# ═══════════════════════════════════════════════════════════


def render_observations(jours: dict) -> None:
    """Affiche les observations sur la semaine."""
    jours_list = list(jours.values())
    jours_noms = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]

    jour_max = max(jours_list, key=lambda j: j.charge_score)
    idx_max = jours_list.index(jour_max)
    st.error(
        f"❌ Jour le plus chargé: **{jours_noms[idx_max].capitalize()}** ({jour_max.charge_score}/100)"
    )

    jour_min = min(jours_list, key=lambda j: j.charge_score)
    idx_min = jours_list.index(jour_min)
    st.success(
        f"🚀 Jour le plus calme: **{jours_noms[idx_min].capitalize()}** ({jour_min.charge_score}/100)"
    )


# ═══════════════════════════════════════════════════════════
# OPTIMISATION IA
# ═══════════════════════════════════════════════════════════


def render_formulaire_optimisation_ia(week_start: date) -> None:
    """Formulaire pour générer une semaine optimisée par IA."""
    st.info("L'IA peut générer une semaine optimale basée sur vos contraintes")

    with st.form("form_optimize_ia"):
        col1, col2 = st.columns(2)

        with col1:
            budget = st.number_input("Budget semaine (€)", 100, 1000, 400)
            energie = st.selectbox("Énergie famille", ["faible", "normal", "elevee"])

        with col2:
            objectifs = st.multiselect(
                "Objectifs santé",
                ["Cardio", "Yoga", "Détente", "Temps famille", "Sommeil"],
            )
            priorites = st.multiselect(
                "Priorités",
                ["Activités Jules", "Repos", "Projets", "Social"],
                default=["Activités Jules"],
            )

        submitted = st.form_submit_button("🤖 Générer optimisation", type="primary")

        if submitted:
            with st.spinner("🤖 L'IA analyse..."):
                # Import différé pour éviter les dépendances circulaires
                from src.services.cuisine.planning import get_planning_unified_service

                service = get_planning_unified_service()
                result = service.generer_semaine_ia(
                    date_debut=week_start,
                    contraintes={"budget": budget, "energie": energie},
                    contexte={
                        "objectifs_sante": objectifs,
                        "priorites": priorites,
                        "jules_age_mois": 19,
                    },
                )

                if result:
                    st.success("✅ Optimisation générée!")
                    st.markdown(f"**Philosophie**: {result.harmonie_description}")
                    with st.expander("Pourquoi cette approche?"):
                        for raison in result.raisons:
                            st.write(f"• {raison}")
                else:
                    st.error("❌ Erreur lors de la génération")


# ═══════════════════════════════════════════════════════════
# RÉÉQUILIBRAGE
# ═══════════════════════════════════════════════════════════


def render_reequilibrage(jours: dict) -> None:
    """Propose le rééquilibrage des jours surchargés."""
    jours_list = list(jours.values())
    jours_noms = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    jours_charges = [(i, j) for i, j in enumerate(jours_list) if j.charge_score >= 75]

    if not jours_charges:
        st.success("✅ Semaine bien équilibrée — Aucun rééquilibrage nécessaire")
        return

    st.info("🔄 Les jours très chargés peuvent être rééquilibrés")

    for idx, jour_charge in jours_charges[:3]:
        jour_nom = jours_noms[idx]

        with st.expander(f"❌ {jour_nom} — Surcharge ({jour_charge.charge_score}/100)"):
            st.write(f"Activités: {len(jour_charge.activites)} | Repas: {len(jour_charge.repas)}")

            if st.button("💡 Proposer répartition", key=f"reequilibrer_{idx}"):
                jour_min = min(jours_list, key=lambda j: j.charge_score)
                idx_min = jours_list.index(jour_min)
                st.info(f"💡 Suggestion: Déplacer 1-2 activités vers {jours_noms[idx_min]}")


__all__ = [
    "EMOJIS_CHARGE",
    "render_graphique_charge_semaine",
    "render_graphique_repartition",
    "render_actions_prioritaires",
    "render_metriques_detaillees",
    "render_suggestions",
    "render_observations",
    "render_formulaire_optimisation_ia",
    "render_reequilibrage",
]
