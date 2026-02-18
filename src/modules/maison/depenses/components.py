"""
Module Depenses Maison - Composants UI

Fonctionnalités:
- Dashboard stats
- Graphiques Plotly interactifs
- Export PDF/CSV
- Prévisions IA
"""

import io

import pandas as pd

try:
    import plotly.express as px
    import plotly.graph_objects as go

    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

from .crud import (
    create_depense,
    delete_depense,
    get_depenses_annee,
    get_depenses_mois,
    get_historique_categorie,
    get_stats_globales,
    update_depense,
)
from .utils import CATEGORY_LABELS, MOIS_FR, Decimal, HouseExpense, Optional, date, st


def render_stats_dashboard():
    """Affiche le dashboard de stats"""
    stats = get_stats_globales()
    today = date.today()

    st.subheader(f"📊 Resume {MOIS_FR[today.month]} {today.year}")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        delta_str = f"{stats['delta']:+.0f}€" if stats["delta"] != 0 else None
        st.metric("Ce mois", f"{stats['total_mois']:.0f}€", delta=delta_str, delta_color="inverse")

    with col2:
        st.metric("Mois precedent", f"{stats['total_prec']:.0f}€")

    with col3:
        st.metric("Moyenne mensuelle", f"{stats['moyenne_mensuelle']:.0f}€")

    with col4:
        st.metric("Categories", stats["nb_categories"])


def render_depense_card(depense: HouseExpense):
    """Affiche une card de depense"""
    with st.container(border=True):
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            cat_label = CATEGORY_LABELS.get(depense.categorie, depense.categorie)
            st.markdown(f"**{cat_label}**")

            if depense.note:
                st.caption(depense.note)

            if depense.consommation:
                unite = (
                    "kWh"
                    if depense.categorie == "electricite"
                    else "m³"
                    if depense.categorie in ["gaz", "eau"]
                    else ""
                )
                st.caption(f"📏 {depense.consommation} {unite}")

        with col2:
            st.metric("Montant", f"{depense.montant:.2f}€")

        with col3:
            col_edit, col_del = st.columns(2)
            with col_edit:
                if st.button("✏️", key=f"edit_{depense.id}", help="Modifier"):
                    st.session_state["edit_depense_id"] = depense.id
                    st.rerun()
            with col_del:
                if st.button("🗑️", key=f"del_{depense.id}", help="Supprimer"):
                    delete_depense(depense.id)
                    st.rerun()


def render_formulaire(depense: Optional[HouseExpense] = None):
    """Formulaire d'ajout/edition"""
    is_edit = depense is not None
    prefix = "edit" if is_edit else "new"
    today = date.today()

    with st.form(f"form_depense_{prefix}"):
        col1, col2 = st.columns(2)

        with col1:
            categories = list(CATEGORY_LABELS.keys())
            cat_index = (
                categories.index(depense.categorie)
                if is_edit and depense.categorie in categories
                else 0
            )
            categorie = st.selectbox(
                "Categorie *",
                options=categories,
                format_func=lambda x: CATEGORY_LABELS.get(x, x),
                index=cat_index,
            )

            montant = st.number_input(
                "Montant (€) *",
                min_value=0.0,
                value=float(depense.montant) if is_edit else 0.0,
                step=0.01,
            )

            # Consommation (pour gaz, eau, electricite)
            if categorie in ["gaz", "eau", "electricite"]:
                unite = "kWh" if categorie == "electricite" else "m³"
                consommation = st.number_input(
                    f"Consommation ({unite})",
                    min_value=0.0,
                    value=float(depense.consommation) if is_edit and depense.consommation else 0.0,
                    step=1.0,
                )
            else:
                consommation = 0.0

        with col2:
            col_mois, col_annee = st.columns(2)
            with col_mois:
                mois = st.selectbox(
                    "Mois",
                    options=range(1, 13),
                    format_func=lambda x: MOIS_FR[x],
                    index=(depense.mois - 1) if is_edit else (today.month - 1),
                )
            with col_annee:
                annee = st.number_input(
                    "Annee",
                    min_value=2020,
                    max_value=2030,
                    value=depense.annee if is_edit else today.year,
                )

            note = st.text_area(
                "Note",
                value=depense.note if is_edit else "",
                placeholder="Commentaire, reference facture...",
            )

        submitted = st.form_submit_button(
            "💾 Enregistrer" if is_edit else "➕ Ajouter", use_container_width=True, type="primary"
        )

        if submitted:
            if montant <= 0:
                st.error("Le montant doit être superieur à 0!")
                return

            data = {
                "categorie": categorie,
                "montant": Decimal(str(montant)),
                "consommation": Decimal(str(consommation)) if consommation > 0 else None,
                "mois": mois,
                "annee": int(annee),
                "note": note or None,
            }

            if is_edit:
                update_depense(depense.id, data)
                st.success("✅ Depense mise à jour!")
            else:
                create_depense(data)
                st.success("✅ Depense ajoutee!")

            st.rerun()


def render_graphique_evolution():
    """Affiche le graphique d'evolution avec Plotly"""
    st.subheader("📈 Évolution")

    # Selection categorie
    categorie = st.selectbox(
        "Categorie à afficher",
        options=["total"] + list(CATEGORY_LABELS.keys()),
        format_func=lambda x: (
            "📊 Total toutes categories" if x == "total" else CATEGORY_LABELS.get(x, x)
        ),
    )

    today = date.today()

    if categorie == "total":
        # Calculer le total par mois
        data = []
        for i in range(12):
            mois = today.month - i
            annee = today.year
            while mois <= 0:
                mois += 12
                annee -= 1

            depenses = get_depenses_mois(mois, annee)
            total = sum(float(d.montant) for d in depenses)
            data.append(
                {
                    "Mois": f"{MOIS_FR[mois][:3]} {annee}",
                    "Montant": total,
                    "mois_num": mois,
                    "annee": annee,
                }
            )
        data = list(reversed(data))
    else:
        historique = get_historique_categorie(categorie, 12)
        data = [{"Mois": h["label"], "Montant": h["montant"]} for h in historique]

    if data:
        df = pd.DataFrame(data)

        if PLOTLY_AVAILABLE:
            # Graphique Plotly interactif
            fig = px.bar(
                df,
                x="Mois",
                y="Montant",
                title=f"Évolution {'totale' if categorie == 'total' else CATEGORY_LABELS.get(categorie, categorie)}",
                text="Montant",
                color_discrete_sequence=["#8e44ad"],
            )

            fig.update_traces(texttemplate="%{text:.0f}€", textposition="outside")

            fig.update_layout(
                xaxis_title="",
                yaxis_title="Montant (€)",
                showlegend=False,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="system-ui", size=12),
                margin=dict(t=50, b=50, l=50, r=20),
            )

            st.plotly_chart(fig, use_container_width=True)

            # Graphique tendance (ligne)
            if len(df) >= 3:
                fig_line = px.line(df, x="Mois", y="Montant", title="Tendance", markers=True)
                fig_line.update_traces(line_color="#27ae60")
                fig_line.update_layout(
                    showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig_line, use_container_width=True)
        else:
            # Fallback: graphique Streamlit natif
            st.bar_chart(df.set_index("Mois")["Montant"])


def render_graphique_repartition():
    """Affiche un graphique camembert de répartition par catégorie."""
    st.subheader("🥧 Répartition par catégorie")

    today = date.today()

    col1, col2 = st.columns(2)
    with col1:
        mois = st.selectbox(
            "Mois",
            options=range(1, 13),
            format_func=lambda x: MOIS_FR[x],
            index=today.month - 1,
            key="repartition_mois",
        )
    with col2:
        annee = st.number_input(
            "Année", min_value=2020, max_value=2030, value=today.year, key="repartition_annee"
        )

    depenses = get_depenses_mois(mois, int(annee))

    if not depenses:
        st.info(f"Aucune dépense pour {MOIS_FR[mois]} {annee}")
        return

    # Grouper par catégorie
    par_cat = {}
    for d in depenses:
        cat = CATEGORY_LABELS.get(d.categorie, d.categorie)
        par_cat[cat] = par_cat.get(cat, 0) + float(d.montant)

    df = pd.DataFrame([{"Catégorie": k, "Montant": v} for k, v in par_cat.items()])

    if PLOTLY_AVAILABLE and not df.empty:
        fig = px.pie(
            df,
            values="Montant",
            names="Catégorie",
            title=f"Répartition {MOIS_FR[mois]} {annee}",
            color_discrete_sequence=px.colors.qualitative.Set3,
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>%{value:.0f}€<br>%{percent}",
        )

        fig.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.3))

        st.plotly_chart(fig, use_container_width=True)
    else:
        # Fallback simple
        for cat, montant in par_cat.items():
            st.write(f"{cat}: {montant:.0f}€")


def render_export_section():
    """Section d'export PDF/CSV des dépenses."""
    st.subheader("📥 Export des données")

    today = date.today()

    col1, col2 = st.columns(2)
    with col1:
        annee_export = st.selectbox(
            "Année à exporter", options=range(today.year, 2019, -1), key="export_annee"
        )
    with col2:
        format_export = st.selectbox("Format", options=["CSV", "Excel"], key="export_format")

    if st.button("📥 Générer l'export", type="primary", use_container_width=True):
        # Récupérer toutes les dépenses de l'année
        toutes_depenses = get_depenses_annee(int(annee_export))

        if not toutes_depenses:
            st.warning(f"Aucune dépense trouvée pour {annee_export}")
            return

        # Convertir en DataFrame
        data = []
        for d in toutes_depenses:
            data.append(
                {
                    "Mois": MOIS_FR[d.mois],
                    "Année": d.annee,
                    "Catégorie": CATEGORY_LABELS.get(d.categorie, d.categorie),
                    "Montant (€)": float(d.montant),
                    "Consommation": float(d.consommation) if d.consommation else "",
                    "Note": d.note or "",
                }
            )

        df = pd.DataFrame(data)

        # Total par mois
        st.markdown(f"**{len(data)} dépenses** pour un total de **{df['Montant (€)'].sum():.2f}€**")

        # Exporter
        if format_export == "CSV":
            csv = df.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                label="⬇️ Télécharger CSV",
                data=csv,
                file_name=f"depenses_maison_{annee_export}.csv",
                mime="text/csv",
            )
        else:
            # Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="Dépenses", index=False)

                # Résumé par catégorie
                resume = df.groupby("Catégorie")["Montant (€)"].sum().reset_index()
                resume.columns = ["Catégorie", "Total (€)"]
                resume.to_excel(writer, sheet_name="Résumé", index=False)

            output.seek(0)

            st.download_button(
                label="⬇️ Télécharger Excel",
                data=output.getvalue(),
                file_name=f"depenses_maison_{annee_export}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        st.success("✅ Export généré avec succès !")


def render_previsions_ia():
    """Affiche les prévisions IA pour les prochains mois."""
    st.subheader("🤖 Prévisions IA")

    st.markdown("""
    Basé sur votre historique, l'IA estime vos dépenses pour les prochains mois.
    """)

    today = date.today()

    # Récupérer données des 6 derniers mois
    historique = []
    for i in range(6):
        mois = today.month - i
        annee = today.year
        while mois <= 0:
            mois += 12
            annee -= 1

        depenses = get_depenses_mois(mois, annee)
        total = sum(float(d.montant) for d in depenses)
        historique.append({"mois": mois, "annee": annee, "total": total})

    historique = list(reversed(historique))

    if not historique or all(h["total"] == 0 for h in historique):
        st.info("📊 Ajoutez des dépenses pour obtenir des prévisions personnalisées.")
        return

    # Calculs de prévision (moyenne mobile + saisonnalité simplifiée)
    moyenne = sum(h["total"] for h in historique) / len(historique)
    tendance = (
        (historique[-1]["total"] - historique[0]["total"]) / len(historique)
        if len(historique) > 1
        else 0
    )

    # Prévisions pour les 3 prochains mois
    previsions = []
    for i in range(1, 4):
        mois_prev = today.month + i
        annee_prev = today.year
        while mois_prev > 12:
            mois_prev -= 12
            annee_prev += 1

        # Estimation: moyenne + tendance + facteur saisonnier
        facteur_saison = 1.0
        if mois_prev in [1, 2, 12]:  # Mois froids = plus de chauffage
            facteur_saison = 1.15
        elif mois_prev in [7, 8]:  # Été = moins
            facteur_saison = 0.9

        estimation = (moyenne + tendance * i) * facteur_saison
        estimation = max(0, estimation)  # Pas de négatif

        previsions.append(
            {
                "Mois": f"{MOIS_FR[mois_prev]} {annee_prev}",
                "Estimation": estimation,
                "mois_num": mois_prev,
            }
        )

    # Affichage
    col1, col2, col3 = st.columns(3)

    for i, (col, prev) in enumerate(zip([col1, col2, col3], previsions, strict=False)):
        with col:
            variation = ""
            if historique:
                last_total = historique[-1]["total"]
                if last_total > 0:
                    pct = ((prev["Estimation"] - last_total) / last_total) * 100
                    variation = f"{pct:+.0f}%"

            st.metric(
                prev["Mois"], f"{prev['Estimation']:.0f}€", delta=variation, delta_color="inverse"
            )

    # Graphique prévisionnel
    if PLOTLY_AVAILABLE:
        # Combiner historique et prévisions
        df_hist = pd.DataFrame(
            [
                {"Mois": f"{MOIS_FR[h['mois']][:3]}", "Montant": h["total"], "Type": "Réel"}
                for h in historique
            ]
        )

        df_prev = pd.DataFrame(
            [
                {"Mois": p["Mois"][:3], "Montant": p["Estimation"], "Type": "Prévision"}
                for p in previsions
            ]
        )

        fig = go.Figure()

        # Historique
        fig.add_trace(
            go.Bar(x=df_hist["Mois"], y=df_hist["Montant"], name="Réel", marker_color="#8e44ad")
        )

        # Prévisions (hachuré)
        fig.add_trace(
            go.Bar(
                x=df_prev["Mois"],
                y=df_prev["Montant"],
                name="Prévision",
                marker_color="#9b59b6",
                marker_pattern_shape="/",
            )
        )

        fig.update_layout(
            title="Historique et prévisions",
            xaxis_title="",
            yaxis_title="Montant (€)",
            barmode="group",
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        )

        st.plotly_chart(fig, use_container_width=True)

    # Insights IA
    st.divider()
    st.markdown("### 💡 Insights")

    insights = []

    if tendance > 20:
        insights.append(
            "📈 **Tendance haussière** : Vos dépenses augmentent. Surveillez les postes en hausse."
        )
    elif tendance < -20:
        insights.append(
            "📉 **Tendance baissière** : Bravo ! Vos efforts de réduction portent leurs fruits."
        )
    else:
        insights.append("➡️ **Tendance stable** : Vos dépenses sont relativement constantes.")

    # Mois le plus cher
    if historique:
        mois_max = max(historique, key=lambda h: h["total"])
        if mois_max["total"] > 0:
            insights.append(
                f"💰 Mois le plus cher : **{MOIS_FR[mois_max['mois']]} {mois_max['annee']}** ({mois_max['total']:.0f}€)"
            )

    # Estimation annuelle
    estimation_annuelle = moyenne * 12
    insights.append(
        f"📅 Budget annuel estimé : **{estimation_annuelle:.0f}€** ({estimation_annuelle / 12:.0f}€/mois)"
    )

    for insight in insights:
        st.markdown(insight)


def render_comparaison_mois():
    """Compare les depenses de 2 mois"""
    st.subheader("⚖️ Comparaison")

    today = date.today()

    col1, col2 = st.columns(2)

    with col1:
        st.caption("Mois 1")
        mois1 = st.selectbox(
            "Mois",
            range(1, 13),
            format_func=lambda x: MOIS_FR[x],
            index=today.month - 1,
            key="mois1",
        )
        annee1 = st.number_input("Annee", 2020, 2030, today.year, key="annee1")

    with col2:
        st.caption("Mois 2")
        mois_prec = today.month - 1 if today.month > 1 else 12
        annee_prec = today.year if today.month > 1 else today.year - 1
        mois2 = st.selectbox(
            "Mois", range(1, 13), format_func=lambda x: MOIS_FR[x], index=mois_prec - 1, key="mois2"
        )
        annee2 = st.number_input("Annee", 2020, 2030, annee_prec, key="annee2")

    if st.button("Comparer", type="primary"):
        dep1 = get_depenses_mois(mois1, int(annee1))
        dep2 = get_depenses_mois(mois2, int(annee2))

        # Grouper par categorie
        par_cat1 = {d.categorie: float(d.montant) for d in dep1}
        par_cat2 = {d.categorie: float(d.montant) for d in dep2}

        all_cats = set(par_cat1.keys()) | set(par_cat2.keys())

        st.divider()

        for cat in sorted(all_cats):
            val1 = par_cat1.get(cat, 0)
            val2 = par_cat2.get(cat, 0)
            delta = val1 - val2

            col_a, col_b, col_c = st.columns([2, 1, 1])
            with col_a:
                st.markdown(f"**{CATEGORY_LABELS.get(cat, cat)}**")
            with col_b:
                st.caption(f"{MOIS_FR[mois1]}: {val1:.0f}€")
                st.caption(f"{MOIS_FR[mois2]}: {val2:.0f}€")
            with col_c:
                if delta != 0:
                    color = "🔴" if delta > 0 else "🟢"
                    st.markdown(f"{color} {delta:+.0f}€")

        st.divider()
        total1 = sum(par_cat1.values())
        total2 = sum(par_cat2.values())
        delta_total = total1 - total2

        st.markdown(f"**TOTAL**: {total1:.0f}€ vs {total2:.0f}€ = **{delta_total:+.0f}€**")


def render_onglet_mois():
    """Onglet depenses du mois"""
    today = date.today()

    col1, col2 = st.columns(2)
    with col1:
        mois = st.selectbox(
            "Mois", options=range(1, 13), format_func=lambda x: MOIS_FR[x], index=today.month - 1
        )
    with col2:
        annee = st.number_input("Annee", min_value=2020, max_value=2030, value=today.year)

    depenses = get_depenses_mois(mois, int(annee))

    if not depenses:
        st.info(f"Aucune dépense enregistrée pour {MOIS_FR[mois]} {annee}")
        return

    # Total
    total = sum(float(d.montant) for d in depenses)
    st.metric(f"Total {MOIS_FR[mois]} {annee}", f"{total:.2f}€")

    st.divider()

    for depense in depenses:
        render_depense_card(depense)


def render_onglet_ajouter():
    """Onglet ajout"""
    st.subheader("➕ Ajouter une depense")
    render_formulaire(None)


def render_onglet_analyse():
    """Onglet analyse et graphiques enrichie avec Plotly, export et prévisions IA."""

    # Sous-onglets pour organisation
    sub_tab1, sub_tab2, sub_tab3, sub_tab4 = st.tabs(
        ["📈 Évolution", "🥧 Répartition", "🤖 Prévisions IA", "📥 Export"]
    )

    with sub_tab1:
        render_graphique_evolution()
        st.divider()
        render_comparaison_mois()

    with sub_tab2:
        render_graphique_repartition()

    with sub_tab3:
        render_previsions_ia()

    with sub_tab4:
        render_export_section()
