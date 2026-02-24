"""
Module Énergie - Suivi détaillé de la consommation énergétique.

Complète le module Charges en offrant:
- Suivi mensuel des consommations (kWh, m³, L)
- Graphiques de tendances
- Comparaison année N vs N-1
- Objectifs de réduction
- Alertes sur-consommation
"""

import logging
from datetime import date, datetime

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

__all__ = ["app"]

_keys = KeyNamespace("energie")
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

TYPES_ENERGIE = {
    "electricite": {"label": "⚡ Électricité", "unite": "kWh", "icon": "⚡", "color": "#FFD600"},
    "gaz": {"label": "🔥 Gaz", "unite": "m³", "icon": "🔥", "color": "#FF6D00"},
    "eau": {"label": "💧 Eau", "unite": "m³", "icon": "💧", "color": "#2196F3"},
    "fioul": {"label": "🛢️ Fioul", "unite": "L", "icon": "🛢️", "color": "#795548"},
}

MOIS_NOMS = [
    "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre",
]


@profiler_rerun("energie")
def app():
    """Point d'entrée du module Énergie."""
    st.title("⚡ Suivi Énergie")
    st.caption("Suivez et optimisez votre consommation énergétique mensuelle.")

    # Init session state
    if _keys("consommations") not in st.session_state:
        st.session_state[_keys("consommations")] = []

    TAB_LABELS = [
        "📊 Dashboard",
        "📝 Saisir",
        "📈 Tendances",
        "🎯 Objectifs",
    ]
    tabs_with_url(TAB_LABELS, param="tab")
    tab1, tab2, tab3, tab4 = st.tabs(TAB_LABELS)

    with tab1:
        with error_boundary(titre="Erreur dashboard énergie"):
            _onglet_dashboard()

    with tab2:
        with error_boundary(titre="Erreur saisie"):
            _onglet_saisie()

    with tab3:
        with error_boundary(titre="Erreur tendances"):
            _onglet_tendances()

    with tab4:
        with error_boundary(titre="Erreur objectifs"):
            _onglet_objectifs()


def _onglet_dashboard():
    """Dashboard de consommation."""
    consommations = st.session_state[_keys("consommations")]

    if not consommations:
        st.info(
            "Aucune donnée de consommation. "
            "Commencez par saisir vos relevés dans l'onglet '📝 Saisir'."
        )
        return

    # Métriques par type d'énergie
    cols = st.columns(len(TYPES_ENERGIE))
    for i, (type_id, config) in enumerate(TYPES_ENERGIE.items()):
        with cols[i]:
            releves = [c for c in consommations if c["type"] == type_id]
            if releves:
                total = sum(c["valeur"] for c in releves)
                dernier = releves[-1]["valeur"]
                st.metric(
                    config["label"],
                    f"{dernier} {config['unite']}",
                    delta=f"Total: {total:.0f}",
                )
            else:
                st.metric(config["label"], "—")

    # Tableau récapitulatif
    if consommations:
        import pandas as pd

        df = pd.DataFrame(consommations)
        st.dataframe(
            df[["date", "type", "valeur", "cout"]].sort_values("date", ascending=False),
            use_container_width=True,
            hide_index=True,
        )


def _onglet_saisie():
    """Formulaire de saisie de consommation."""
    st.subheader("📝 Saisir un relevé")

    with st.form(key=_keys("form_saisie")):
        col1, col2 = st.columns(2)
        with col1:
            type_energie = st.selectbox(
                "Type d'énergie",
                list(TYPES_ENERGIE.keys()),
                format_func=lambda x: TYPES_ENERGIE[x]["label"],
                key=_keys("type_energie"),
            )
        with col2:
            date_releve = st.date_input(
                "Date du relevé",
                value=date.today(),
                key=_keys("date_releve"),
            )

        config = TYPES_ENERGIE[type_energie]
        col3, col4 = st.columns(2)
        with col3:
            valeur = st.number_input(
                f"Consommation ({config['unite']})",
                min_value=0.0,
                step=1.0,
                key=_keys("valeur"),
            )
        with col4:
            cout = st.number_input(
                "Coût (€)",
                min_value=0.0,
                step=0.01,
                key=_keys("cout"),
            )

        notes = st.text_input("Notes (optionnel)", key=_keys("notes"))
        submitted = st.form_submit_button("💾 Enregistrer", use_container_width=True)

    if submitted and valeur > 0:
        consommation = {
            "date": date_releve.isoformat(),
            "type": type_energie,
            "valeur": valeur,
            "cout": cout,
            "notes": notes,
        }
        st.session_state[_keys("consommations")].append(consommation)
        st.success(
            f"✅ Relevé enregistré: {valeur} {config['unite']} "
            f"({cout}€) le {date_releve.strftime('%d/%m/%Y')}"
        )


def _onglet_tendances():
    """Graphiques de tendances de consommation."""
    consommations = st.session_state[_keys("consommations")]

    if len(consommations) < 2:
        st.info("Il faut au moins 2 relevés pour afficher les tendances.")
        return

    type_graphe = st.selectbox(
        "Type d'énergie",
        list(TYPES_ENERGIE.keys()),
        format_func=lambda x: TYPES_ENERGIE[x]["label"],
        key=_keys("type_tendance"),
    )

    releves = [c for c in consommations if c["type"] == type_graphe]
    if len(releves) < 2:
        st.info(f"Pas assez de données pour {TYPES_ENERGIE[type_graphe]['label']}.")
        return

    import pandas as pd

    df = pd.DataFrame(releves).sort_values("date")

    # Graphique évolution
    try:
        import plotly.express as px

        config = TYPES_ENERGIE[type_graphe]
        fig = px.line(
            df,
            x="date",
            y="valeur",
            title=f"Évolution {config['label']}",
            labels={"valeur": config["unite"], "date": "Date"},
            color_discrete_sequence=[config["color"]],
        )
        st.plotly_chart(fig, use_container_width=True)

        # Coûts
        if df["cout"].sum() > 0:
            fig_cout = px.bar(
                df,
                x="date",
                y="cout",
                title=f"Coûts {config['label']}",
                labels={"cout": "€", "date": "Date"},
                color_discrete_sequence=[config["color"]],
            )
            st.plotly_chart(fig_cout, use_container_width=True)

    except ImportError:
        st.warning("Plotly non disponible pour les graphiques.")
        st.dataframe(df[["date", "valeur", "cout"]], use_container_width=True)


def _onglet_objectifs():
    """Gestion des objectifs de réduction."""
    st.subheader("🎯 Objectifs de réduction")
    st.caption("Fixez et suivez vos objectifs d'économie d'énergie.")

    consommations = st.session_state[_keys("consommations")]

    for type_id, config in TYPES_ENERGIE.items():
        releves = [c for c in consommations if c["type"] == type_id]
        if not releves:
            continue

        with st.container(border=True):
            st.markdown(f"**{config['label']}**")

            # Moyenne actuelle
            moyenne = sum(c["valeur"] for c in releves) / len(releves)
            st.caption(f"Moyenne actuelle: {moyenne:.1f} {config['unite']}/relevé")

            # Slider objectif de réduction
            reduction = st.slider(
                f"Objectif de réduction (%)",
                min_value=0,
                max_value=50,
                value=10,
                key=_keys(f"objectif_{type_id}"),
            )

            objectif = moyenne * (1 - reduction / 100)
            economie_mensuelle = (moyenne - objectif) * (
                sum(c["cout"] for c in releves) / sum(c["valeur"] for c in releves)
                if sum(c["valeur"] for c in releves) > 0
                else 0
            )

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Objectif", f"{objectif:.1f} {config['unite']}")
            with col2:
                st.metric("Économie estimée", f"{economie_mensuelle:.0f}€/mois")
