"""
Composants UI pour le module Énergie.
"""

from datetime import date

import pandas as pd
import streamlit as st

from src.ui.fragments import cached_fragment
from src.ui.keys import KeyNamespace

from .constants import ENERGIES, TYPES_ENERGIE
from .data import get_stats_energie
from .graphiques import graphique_comparaison_annees, graphique_evolution

_keys = KeyNamespace("energie")


def afficher_metric_energie(type_energie: str) -> None:
    """Affiche les métriques pour un type d'énergie.

    Args:
        type_energie: Type d'énergie.
    """
    stats = get_stats_energie(type_energie)
    config = ENERGIES.get(type_energie, {})

    with st.container(border=True):
        st.markdown(f"**{config.get('emoji', '')} {config.get('label', type_energie)}**")
        cols = st.columns(3)
        with cols[0]:
            st.metric("Dernier mois", f"{stats['dernier_montant']:.0f}€")
        with cols[1]:
            st.metric("Moyenne", f"{stats['moyenne_mensuelle']:.0f}€/mois")
        with cols[2]:
            st.metric(
                "Consommation",
                f"{stats['derniere_conso']:.0f} {config.get('unite', '')}",
                delta=f"{stats['delta_conso']:+.0f}",
            )


def afficher_dashboard_global() -> None:
    """Affiche le dashboard global énergie."""
    st.subheader("📊 Vue d'ensemble")

    cols = st.columns(2)
    for i, (type_id, _) in enumerate(ENERGIES.items()):
        with cols[i % 2]:
            afficher_metric_energie(type_id)


def afficher_detail_energie(type_energie: str) -> None:
    """Affiche le détail pour un type d'énergie.

    Args:
        type_energie: Type d'énergie.
    """
    config = ENERGIES.get(type_energie, {})
    stats = get_stats_energie(type_energie)

    st.subheader(f"{config.get('emoji', '')} {config.get('label', type_energie)}")

    cols = st.columns(4)
    with cols[0]:
        st.metric("Total annuel", f"{stats['total_annuel']:.0f}€")
    with cols[1]:
        st.metric("Moyenne", f"{stats['moyenne_mensuelle']:.0f}€/mois")
    with cols[2]:
        st.metric("Conso totale", f"{stats['conso_totale']:.0f} {config.get('unite', '')}")
    with cols[3]:
        st.metric("Prix unitaire", f"{stats['prix_unitaire']:.4f}€/{config.get('unite', '')}")

    tab1, tab2 = st.tabs(["📈 Évolution", "📊 Comparaison"])
    with tab1:
        fig = graphique_evolution(type_energie)
        st.plotly_chart(fig, use_container_width=True)
    with tab2:
        fig = graphique_comparaison_annees(type_energie)
        st.plotly_chart(fig, use_container_width=True)


def afficher_alertes() -> None:
    """Affiche les alertes de consommation."""
    alertes = []

    for type_id, config in ENERGIES.items():
        stats = get_stats_energie(type_id)
        moyenne = stats["moyenne_mensuelle"]
        dernier = stats["dernier_montant"]
        delta_conso = stats["delta_conso"]
        conso_moyenne = stats["conso_moyenne"]

        # Alerte si dépassement > 120% de la moyenne
        if moyenne > 0 and dernier > moyenne * 1.2:
            pct = (dernier / moyenne - 1) * 100
            alertes.append(
                {
                    "type": "warning",
                    "message": (
                        f"⚠️ {config['label']}: dernier mois à {dernier:.0f}€ "
                        f"(+{pct:.0f}% vs moyenne)"
                    ),
                }
            )

        # Alerte si forte hausse consommation (> 30% de la moyenne)
        if conso_moyenne > 0 and delta_conso > conso_moyenne * 0.3:
            alertes.append(
                {
                    "type": "error",
                    "message": (
                        f"🔴 {config['label']}: hausse consommation de "
                        f"{delta_conso:+.0f} {config['unite']}"
                    ),
                }
            )

    if not alertes:
        st.success("✅ Aucune alerte — consommation dans les normes.")
        return

    for alerte in alertes:
        if alerte["type"] == "warning":
            st.warning(alerte["message"])
        elif alerte["type"] == "error":
            st.error(alerte["message"])


def afficher_onglet_dashboard() -> None:
    """Dashboard de consommation."""
    consommations = st.session_state.get(_keys("consommations"), [])

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
        df = pd.DataFrame(consommations)
        st.dataframe(
            df[["date", "type", "valeur", "cout"]].sort_values("date", ascending=False),
            use_container_width=True,
            hide_index=True,
        )


def afficher_onglet_saisie() -> None:
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
        if _keys("consommations") not in st.session_state:
            st.session_state[_keys("consommations")] = []
        st.session_state[_keys("consommations")].append(consommation)
        st.success(
            f"✅ Relevé enregistré: {valeur} {config['unite']} "
            f"({cout}€) le {date_releve.strftime('%d/%m/%Y')}"
        )


@cached_fragment(ttl=300)
def _build_energie_line(dates: tuple, valeurs: tuple, label: str, unite: str, color: str):
    """Construit le line chart d'évolution énergie (caché 5 min)."""
    import plotly.express as px

    df = pd.DataFrame({"date": list(dates), "valeur": list(valeurs)})
    fig = px.line(
        df,
        x="date",
        y="valeur",
        title=f"Évolution {label}",
        labels={"valeur": unite, "date": "Date"},
        color_discrete_sequence=[color],
    )
    return fig


@cached_fragment(ttl=300)
def _build_energie_bar(dates: tuple, couts: tuple, label: str, color: str):
    """Construit le bar chart des coûts énergie (caché 5 min)."""
    import plotly.express as px

    df = pd.DataFrame({"date": list(dates), "cout": list(couts)})
    fig = px.bar(
        df,
        x="date",
        y="cout",
        title=f"Coûts {label}",
        labels={"cout": "€", "date": "Date"},
        color_discrete_sequence=[color],
    )
    return fig


def afficher_onglet_tendances() -> None:
    """Graphiques de tendances de consommation."""
    consommations = st.session_state.get(_keys("consommations"), [])

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

    df = pd.DataFrame(releves).sort_values("date")

    # Graphique évolution
    try:
        config = TYPES_ENERGIE[type_graphe]
        fig = _build_energie_line(
            tuple(df["date"]),
            tuple(df["valeur"]),
            config["label"],
            config["unite"],
            config["color"],
        )
        st.plotly_chart(fig, use_container_width=True)

        # Coûts
        if df["cout"].sum() > 0:
            fig_cout = _build_energie_bar(
                tuple(df["date"]),
                tuple(df["cout"]),
                config["label"],
                config["color"],
            )
            st.plotly_chart(fig_cout, use_container_width=True)

    except ImportError:
        st.warning("Plotly non disponible pour les graphiques.")
        st.dataframe(df[["date", "valeur", "cout"]], use_container_width=True)


def afficher_onglet_objectifs() -> None:
    """Gestion des objectifs de réduction."""
    st.subheader("🎯 Objectifs de réduction")
    st.caption("Fixez et suivez vos objectifs d'économie d'énergie.")

    consommations = st.session_state.get(_keys("consommations"), [])

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
                "Objectif de réduction (%)",
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
