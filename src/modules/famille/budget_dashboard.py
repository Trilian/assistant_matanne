"""
Tableau de bord budget familial - Interface Streamlit.

Fonctionnalités:
- Vue d'ensemble des dépenses
- Ajout de dépenses
- Graphiques de tendances
- Configuration des budgets mensuels
"""

from datetime import date as date_type

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.services.famille.budget import (
    CategorieDepense,
    Depense,
    get_budget_service,
)


def render_budget_dashboard():
    """Affiche le tableau de bord budget dans Streamlit."""
    st.subheader("💰 Budget Familial")

    service = get_budget_service()

    # Sélecteur de période
    col1, col2 = st.columns([2, 1])
    with col1:
        aujourd_hui = date_type.today()
        mois_options = [(f"{m:02d}/{aujourd_hui.year}", m, aujourd_hui.year) for m in range(1, 13)]
        mois_select = st.selectbox(
            "Période",
            options=mois_options,
            index=aujourd_hui.month - 1,
            format_func=lambda x: x[0],
            key="budget_mois",
        )
        _, mois, annee = mois_select

    # Récupérer le résumé
    resume = service.get_resume_mensuel(mois, annee)

    # Alertes
    if resume.categories_depassees:
        st.error(f"⚠️ Budgets dépassés: {', '.join(resume.categories_depassees)}")
    if resume.categories_a_risque:
        st.warning(f"⚠️ À surveiller (>80%): {', '.join(resume.categories_a_risque)}")

    # Métriques principales
    _render_metrics(resume)

    st.markdown("---")

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📊 Vue d'ensemble", "➕ Ajouter", "📝ˆ Tendances", "⚙️ Budgets"]
    )

    with tab1:
        _render_overview_tab(service, resume, mois, annee)

    with tab2:
        _render_add_expense_tab(service)

    with tab3:
        _render_trends_tab(service, mois, annee)

    with tab4:
        _render_budgets_config_tab(service, mois, annee)


def _render_metrics(resume):
    """Affiche les métriques principales."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "💸 Dépenses",
            f"{resume.total_depenses:.0f}€",
            delta=f"{resume.variation_vs_mois_precedent:+.1f}% vs mois préc.",
            delta_color="inverse",
        )

    with col2:
        st.metric("📊 Budget Total", f"{resume.total_budget:.0f}€")

    with col3:
        reste = resume.total_budget - resume.total_depenses
        st.metric(
            "💰 Reste",
            f"{reste:.0f}€",
            delta="OK" if reste >= 0 else "Dépassé!",
            delta_color="normal" if reste >= 0 else "inverse",
        )

    with col4:
        st.metric("📊 Moyenne 6 mois", f"{resume.moyenne_6_mois:.0f}€")


def _render_overview_tab(service, resume, mois, annee):
    """Onglet vue d'ensemble."""
    # Graphique dépenses par catégorie
    if resume.depenses_par_categorie:
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            # Camembert
            fig_pie = px.pie(
                values=list(resume.depenses_par_categorie.values()),
                names=list(resume.depenses_par_categorie.keys()),
                title="Répartition des dépenses",
                hole=0.4,
            )
            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig_pie, width="stretch", key="budget_expenses_pie")

        with col_chart2:
            # Barres budget vs dépenses
            categories = []
            budgets_vals = []
            depenses_vals = []

            for cat_key, budget in resume.budgets_par_categorie.items():
                categories.append(cat_key)
                budgets_vals.append(budget.budget_prevu)
                depenses_vals.append(budget.depense_reelle)

            fig_bar = go.Figure(
                data=[
                    go.Bar(name="Budget", x=categories, y=budgets_vals, marker_color="lightblue"),
                    go.Bar(name="Dépensé", x=categories, y=depenses_vals, marker_color="coral"),
                ]
            )
            fig_bar.update_layout(title="Budget vs Dépenses", barmode="group", xaxis_tickangle=-45)
            st.plotly_chart(fig_bar, width="stretch", key="budget_vs_expenses_bar")

    # Liste des dépenses récentes
    st.markdown("### 📋 Dernières dépenses")
    depenses = service.get_depenses_mois(mois, annee)

    if depenses:
        for dep in depenses[:10]:
            col_d1, col_d2, col_d3 = st.columns([2, 3, 1])
            with col_d1:
                st.caption(dep.date.strftime("%d/%m"))
            with col_d2:
                st.write(f"**{dep.categorie.value}** - {dep.description or 'Sans description'}")
            with col_d3:
                st.write(f"**{dep.montant:.0f}€**")
    else:
        st.info("Aucune dépense ce mois-ci")


def _render_add_expense_tab(service):
    """Onglet d'ajout de dépense."""
    st.markdown("### ➕ Nouvelle dépense")

    with st.form("add_expense_form"):
        col_f1, col_f2 = st.columns(2)

        with col_f1:
            montant = st.number_input("Montant (€)", min_value=0.0, step=1.0, key="expense_amount")
            categorie = st.selectbox(
                "Catégorie",
                options=list(CategorieDepense),
                format_func=lambda x: x.value.title(),
                key="expense_cat",
            )

        with col_f2:
            date_depense = st.date_input("Date", value=date_type.today(), key="expense_date")
            description = st.text_input("Description", key="expense_desc")

        magasin = st.text_input("Magasin (optionnel)", key="expense_shop")

        est_recurrente = st.checkbox("Dépense récurrente", key="expense_recurring")

        if st.form_submit_button("💾 Enregistrer", type="primary", use_container_width=True):
            if montant > 0:
                depense = Depense(
                    date=date_depense,
                    montant=montant,
                    categorie=categorie,
                    description=description,
                    magasin=magasin,
                    est_recurrente=est_recurrente,
                )

                service.ajouter_depense(depense)
                st.success(f"✅ Dépense de {montant}€ ajoutée!")
                st.rerun()
            else:
                st.error("Le montant doit être supérieur à 0")


def _render_trends_tab(service, mois, annee):
    """Onglet des tendances."""
    st.markdown("### 📝ˆ Évolution sur 6 mois")

    tendances = service.get_tendances(nb_mois=6)

    if tendances.get("mois"):
        fig_trend = go.Figure()

        fig_trend.add_trace(
            go.Scatter(
                x=tendances["mois"],
                y=tendances["total"],
                mode="lines+markers",
                name="Total",
                line=dict(width=3, color="blue"),
            )
        )

        # Top 3 catégories
        moyennes_cat = {
            cat: sum(tendances.get(cat.value, [])) / max(1, len(tendances.get(cat.value, [])))
            for cat in CategorieDepense
        }
        top_cats = sorted(moyennes_cat.items(), key=lambda x: x[1], reverse=True)[:3]

        colors = ["green", "orange", "red"]
        for i, (cat, _) in enumerate(top_cats):
            if tendances.get(cat.value):
                fig_trend.add_trace(
                    go.Scatter(
                        x=tendances["mois"],
                        y=tendances[cat.value],
                        mode="lines",
                        name=cat.value.title(),
                        line=dict(dash="dash", color=colors[i]),
                    )
                )

        fig_trend.update_layout(
            title="Évolution des dépenses",
            xaxis_title="Mois",
            yaxis_title="Montant (€)",
            hovermode="x unified",
        )

        st.plotly_chart(fig_trend, width="stretch", key="budget_expenses_trend")

    # Prévisions
    st.markdown("### 🔮 Prévisions mois prochain")
    mois_prochain = mois + 1 if mois < 12 else 1
    annee_prochain = annee if mois < 12 else annee + 1

    previsions = service.prevoir_depenses(mois_prochain, annee_prochain)

    if previsions:
        total_prevu = sum(p.montant_prevu for p in previsions)
        st.metric("Total prévu", f"{total_prevu:.0f}€")

        for prev in previsions[:5]:
            col_p1, col_p2, col_p3 = st.columns([2, 2, 1])
            with col_p1:
                st.write(f"**{prev.categorie.value.title()}**")
            with col_p2:
                st.write(f"{prev.montant_prevu:.0f}€")
            with col_p3:
                confiance_color = (
                    "🟢" if prev.confiance > 0.7 else "🟡" if prev.confiance > 0.4 else "🔴"
                )
                st.write(f"{confiance_color} {prev.confiance:.0%}")


def _render_budgets_config_tab(service, mois, annee):
    """Onglet de configuration des budgets."""
    st.markdown("### ⚙️ Définir les budgets mensuels")

    budgets_actuels = service.get_tous_budgets(mois, annee)

    with st.form("budget_config_form"):
        cols = st.columns(3)

        new_budgets = {}
        for i, cat in enumerate(CategorieDepense):
            if cat == CategorieDepense.AUTRE:
                continue

            with cols[i % 3]:
                budget_actuel = budgets_actuels.get(cat, service.BUDGETS_DEFAUT.get(cat, 0))
                new_budgets[cat] = st.number_input(
                    f"{cat.value.title()}",
                    min_value=0.0,
                    value=float(budget_actuel),
                    step=10.0,
                    key=f"budget_{cat.value}",
                )

        if st.form_submit_button("💾 Enregistrer les budgets", use_container_width=True):
            for cat, montant in new_budgets.items():
                service.definir_budget(cat, montant, mois, annee)

            st.success("✅ Budgets mis à jour!")
            st.rerun()
