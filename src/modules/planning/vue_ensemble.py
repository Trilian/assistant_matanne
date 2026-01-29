"""
Module Vue d'Ensemble Planning - Dashboard d'actions prioritaires

Affiche les actions critiques et suggère automatiquement ce qui doit être fait
Utilise PlanningAIService pour détection intelligente des alertes
"""

from datetime import date, datetime, timedelta

import streamlit as st

from src.services.planning_unified import get_planning_service

# Logique métier pure
from src.modules.planning.vue_ensemble_logic import (
    calculer_statistiques_planning,
    generer_resume_periode
)
from src.core.state import get_state

logger = __import__("logging").getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# HELPERS UI
# ═══════════════════════════════════════════════════════════


def afficher_actions_prioritaires(alertes_semaine: list) -> None:
    """Affiche les actions prioritaires en tableau"""
    if not alertes_semaine:
        st.success("✅ Semaine bien équilibrée - Aucune action urgente")
        return

    st.markdown("### 🎯 Actions à Prendre")

    for alerte in alertes_semaine:
        # Parser l'alerte pour extraire emoji et message
        parts = alerte.split(" - ") if " - " in alerte else [alerte]
        emoji = parts[0] if len(parts) > 1 else "⚠️"
        message = parts[-1]

        col_msg, col_action = st.columns([3, 1])

        with col_msg:
            st.warning(message, icon=emoji)

        with col_action:
            if "👶" in emoji:
                if st.button("→ Activités", key=f"alerte_{alerte[:20]}", use_container_width=True):
                    st.session_state.planning_view = "activites"

            elif "💰" in emoji:
                if st.button("→ Budget", key=f"alerte_{alerte[:20]}", use_container_width=True):
                    st.session_state.planning_view = "budget"

            elif "⚠️" in emoji:
                if st.button("→ Voir", key=f"alerte_{alerte[:20]}", use_container_width=True):
                    pass


def afficher_metriques_cles(stats: dict, charge_globale: str) -> None:
    """Affiche les KPIs principaux"""
    st.markdown("### 📊 Métriques Clés")

    col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)

    with col_m1:
        st.metric("🍽️ Repas", stats.get("total_repas", 0))

    with col_m2:
        st.metric("🎨 Activités", stats.get("total_activites", 0))

    with col_m3:
        st.metric("👶 Pour Jules", stats.get("activites_jules", 0))

    with col_m4:
        st.metric("🏗️ Projets", stats.get("total_projets", 0))

    with col_m5:
        budget = stats.get("budget_total", 0)
        st.metric("💰 Budget", f"{budget:.0f}€")

    st.markdown("---")

    # Charge globale
    charge_emoji = {
        "faible": "🟢",
        "normal": "🟡",
        "intense": "🔴",
    }.get(charge_globale, "⚪")

    st.markdown(f"### {charge_emoji} Charge Globale: **{charge_globale.upper()}**")

    charge_score = stats.get("charge_moyenne", 50)
    st.progress(min(charge_score / 100, 1.0))

    if charge_score >= 80:
        st.warning("⚠️ Charge familiale très élevée - À prendre en compte pour le bien-être")
    elif charge_score >= 70:
        st.info("ℹ️ Charge normale - Veiller au repos et temps de qualité")
    else:
        st.success("✅ Charge faible - Bonne semaine équilibrée")


def afficher_synthese_jours(jours: dict) -> None:
    """Affiche synthèse visuelle des jours"""
    st.markdown("### 📅 Synthèse par jour")

    jours_noms = ["lun", "mar", "mer", "jeu", "ven", "sam", "dim"]
    jours_list = list(jours.values())

    cols = st.columns(7)

    for i, col in enumerate(cols):
        with col:
            jour = jours_list[i]
            jour_nom = jours_noms[i]

            # Badge avec charge
            charge_emoji = {
                "faible": "🟢",
                "normal": "🟡",
                "intense": "🔴",
            }.get(jour.charge, "⚪")

            st.markdown(
                f"""
                <div style="text-align: center; padding: 10px; border-radius: 8px; background: #f0f2f6;">
                    <h4>{charge_emoji}</h4>
                    <p style="margin: 5px 0; font-size: 12px;"><strong>{jour_nom.upper()}</strong></p>
                    <p style="margin: 5px 0; font-size: 11px;">{jour.charge_score}/100</p>
                    <p style="margin: 5px 0; font-size: 11px;">
                        🍽️{len(jour.repas)} 🎨{len(jour.activites)}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def afficher_opportunities(semaine_data: dict) -> None:
    """Suggère automatiquement des améliorations"""
    st.markdown("### 💡 Suggestions d'Amélioration")

    suggestions = []

    # Jules: activités
    activites_jules = semaine_data.get("activites_jules", 0)
    if activites_jules == 0:
        suggestions.append(
            ("👶 Aucune activité pour Jules", 
             "Planifier au moins 2-3 activités adaptées à 19m par semaine")
        )
    elif activites_jules < 2:
        suggestions.append(
            ("👶 Peu d'activités pour Jules",
             f"Actuellement {activites_jules} - Recommandé: 3+")
        )

    # Budget
    budget_total = semaine_data.get("budget_total", 0)
    budget_limite = 500  # À adapter à votre budget
    if budget_total > budget_limite:
        suggestions.append(
            ("💰 Budget elevé",
             f"{budget_total:.0f}€ > {budget_limite}€ - Revoir les dépenses")
        )

    # Pas de repas
    if semaine_data.get("total_repas", 0) == 0:
        suggestions.append(
            ("🍽️ Aucun repas planifié",
             "Prévoir le planning culinaire de la semaine")
        )

    if suggestions:
        for emoji_title, description in suggestions:
            with st.container():
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.write("💡")
                with col2:
                    st.write(f"**{emoji_title}**: {description}")
    else:
        st.success("✅ Semaine bien équilibrée - Aucune suggestion")


# ═══════════════════════════════════════════════════════════
# MODULE PRINCIPAL
# ═══════════════════════════════════════════════════════════


def app():
    """Module Vue d'Ensemble - Actions prioritaires"""

    st.title("🎯 Vue d'Ensemble Planning")
    st.caption("Actions prioritaires et suggestions intelligentes pour la semaine")

    # ═══════════════════════════════════════════════════════════
    # NAVIGATION SEMAINE
    # ═══════════════════════════════════════════════════════════

    if "ensemble_week_start" not in st.session_state:
        today = date.today()
        st.session_state.ensemble_week_start = today - timedelta(days=today.weekday())

    col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])

    with col_nav1:
        if st.button("⬅️ Semaine précédente", key="prev_ensemble"):
            st.session_state.ensemble_week_start -= timedelta(days=7)
            st.rerun()

    with col_nav2:
        week_start = st.session_state.ensemble_week_start
        week_end = week_start + timedelta(days=6)
        st.markdown(
            f"<h3 style='text-align: center;'>{week_start.strftime('%d/%m')} — {week_end.strftime('%d/%m/%Y')}</h3>",
            unsafe_allow_html=True,
        )

    with col_nav3:
        if st.button("Semaine suivante ➡️", key="next_ensemble"):
            st.session_state.ensemble_week_start += timedelta(days=7)
            st.rerun()

    st.markdown("---")

    # ═══════════════════════════════════════════════════════════
    # CHARGEMENT DONNÉES
    # ═══════════════════════════════════════════════════════════

    service = get_planning_service()
    semaine = service.get_semaine_complete(st.session_state.ensemble_week_start)

    if not semaine:
        st.error("❌ Erreur lors du chargement de la semaine")
        return

    # ═══════════════════════════════════════════════════════════
    # ACTIONS PRIORITAIRES (TOP)
    # ═══════════════════════════════════════════════════════════

    if semaine.alertes_semaine:
        st.markdown("### 🚨 Actions Critiques")
        afficher_actions_prioritaires(semaine.alertes_semaine)
        st.markdown("---")

    # ═══════════════════════════════════════════════════════════
    # MÉTRIQUES CLÉS
    # ═══════════════════════════════════════════════════════════

    afficher_metriques_cles(semaine.stats_semaine, semaine.charge_globale)

    # ═══════════════════════════════════════════════════════════
    # SYNTHÈSE JOURS
    # ═══════════════════════════════════════════════════════════

    afficher_synthese_jours(semaine.jours)

    st.markdown("---")

    # ═══════════════════════════════════════════════════════════
    # SUGGESTIONS & OPPORTUNITIES
    # ═══════════════════════════════════════════════════════════

    afficher_opportunities(semaine.stats_semaine)

    st.markdown("---")

    # ═══════════════════════════════════════════════════════════
    # ONGLETS DÉTAILS
    # ═══════════════════════════════════════════════════════════

    tab1, tab2, tab3 = st.tabs(["🔄 Rééquilibrer", "🤖 Optimiser avec IA", "📋 Détails"])

    with tab1:
        st.subheader("🔄 Rééquilibrer la semaine")

        st.info(
            "💡 Les jours très chargés peuvent être rééquilibrés en déplaçant certaines activités"
        )

        # Identifier jours chargés
        jours_list = list(semaine.jours.values())
        jours_charges = [
            (i, j) for i, j in enumerate(jours_list) if j.charge_score >= 75
        ]

        if jours_charges:
            for idx, jour_charge in jours_charges[:2]:
                jour_names = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
                jour_nom = jour_names[idx]

                with st.expander(f"🔴 {jour_nom} - Surchargé ({jour_charge.charge_score}/100)"):
                    st.write(f"Activités: {len(jour_charge.activites)} | Repas: {len(jour_charge.repas)}")

                    if st.button(f"Proposer répartition", key=f"reequilibrer_{idx}"):
                        st.info("💡 Suggestion: Déplacer 1-2 activités vers jour plus calme")

        else:
            st.success("✅ Semaine bien équilibrée - Aucun rééquilibrage nécessaire")

    with tab2:
        st.subheader("🤖 Optimiser avec IA")

        st.info("L'IA peut générer une semaine optimale basée sur vos contraintes")

        with st.form("form_optimize"):
            col_o1, col_o2 = st.columns(2)

            with col_o1:
                budget = st.number_input("Budget semaine (€)", 100, 1000, 400)
                energie = st.selectbox("Énergie famille", ["faible", "normal", "élevée"])

            with col_o2:
                objectifs = st.multiselect(
                    "Objectifs santé",
                    ["Cardio", "Yoga", "Détente", "Temps famille", "Sommeil"],
                )
                priorites = st.multiselect(
                    "Priorités",
                    ["Activités Jules", "Repos", "Projets", "Social"],
                    default=["Activités Jules"],
                )

            submitted = st.form_submit_button("🚀 Générer optimisation", type="primary")

            if submitted:
                with st.spinner("🤖 L'IA analyse..."):
                    result = service.generer_semaine_ia(
                        date_debut=st.session_state.ensemble_week_start,
                        contraintes={
                            "budget": budget,
                            "energie": energie,
                        },
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

                        st.info("💡 Vous pouvez créer ces éléments dans votre planning")
                    else:
                        st.error("❌ Erreur génération")

    with tab3:
        st.subheader("📋 Détails Semaine")

        jours_semaine = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]

        selected_jour = st.selectbox("Sélectionner un jour", jours_semaine, key="ensemble_jour_select")

        jour_idx = jours_semaine.index(selected_jour)
        jour_date = st.session_state.ensemble_week_start + timedelta(days=jour_idx)
        jour_str = jour_date.isoformat()

        jour_data = semaine.jours.get(jour_str)

        if jour_data:
            jour_data_dict = jour_data.dict()

            st.markdown(f"### {selected_jour.capitalize()} {jour_date.strftime('%d/%m')}")

            col_d1, col_d2, col_d3 = st.columns(3)

            with col_d1:
                charge_emoji = {
                    "faible": "🟢",
                    "normal": "🟡",
                    "intense": "🔴",
                }.get(jour_data_dict["charge"], "⚪")
                st.metric("Charge", f"{charge_emoji} {jour_data_dict['charge_score']}/100")

            with col_d2:
                st.metric("Événements", len(jour_data_dict["repas"]) + len(jour_data_dict["activites"]))

            with col_d3:
                st.metric("Budget", f"{jour_data_dict['budget_jour']:.0f}€")

            st.write(f"**Repas**: {len(jour_data_dict['repas'])}")
            st.write(f"**Activités**: {len(jour_data_dict['activites'])}")
            st.write(f"**Projets**: {len(jour_data_dict['projets'])}")

            if jour_data_dict.get("alertes"):
                st.warning("**Alertes du jour**:")
                for alerte in jour_data_dict["alertes"]:
                    st.write(f"• {alerte}")
