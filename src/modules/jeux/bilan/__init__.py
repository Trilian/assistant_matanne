"""
Module Bilan Global Jeux — Dashboard consolidé gains/pertes

Fonctionnalités:
- Vue consolidée cross-jeux (Paris + Loto + Euromillions)
- Graphique profit cumulé temporel (Plotly)
- KPIs: ROI global, meilleur/pire mois, streaks
- Répartition des mises par type (pie chart)
- Jauge de mise responsable
"""

import logging
from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.core.decorators import avec_session_db
from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.core.fragments import cached_fragment
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

logger = logging.getLogger(__name__)
_keys = KeyNamespace("bilan_jeux")


@avec_session_db
def _charger_historique(jours: int = 365, db=None) -> list[dict]:
    """Charge l'historique des jeux depuis la BD."""
    from src.core.models.jeux import HistoriqueJeux

    date_debut = date.today() - timedelta(days=jours)
    rows = (
        db.query(HistoriqueJeux)
        .filter(HistoriqueJeux.date >= date_debut)
        .order_by(HistoriqueJeux.date.asc())
        .all()
    )
    return [
        {
            "date": r.date,
            "type_jeu": r.type_jeu,
            "nb_paris": r.nb_paris,
            "mises": float(r.mises_totales),
            "gains": float(r.gains_totaux),
            "profit": float(r.gains_totaux - r.mises_totales),
            "paris_gagnes": r.paris_gagnes,
            "paris_perdus": r.paris_perdus,
        }
        for r in rows
    ]


@cached_fragment(ttl=300)
def _build_profit_cumule(df: pd.DataFrame) -> go.Figure:
    """Graphique du profit cumulé par type de jeu."""
    fig = go.Figure()

    for type_jeu in df["type_jeu"].unique():
        df_jeu = df[df["type_jeu"] == type_jeu].copy()
        df_jeu["profit_cumule"] = df_jeu["profit"].cumsum()

        fig.add_trace(
            go.Scatter(
                x=df_jeu["date"],
                y=df_jeu["profit_cumule"],
                mode="lines+markers",
                name=type_jeu.capitalize(),
                line={"width": 2},
            )
        )

    # Total
    df_total = df.groupby("date")["profit"].sum().cumsum().reset_index()
    df_total.columns = ["date", "profit_cumule"]
    fig.add_trace(
        go.Scatter(
            x=df_total["date"],
            y=df_total["profit_cumule"],
            mode="lines",
            name="Total",
            line={"width": 3, "dash": "dash", "color": "white"},
        )
    )

    fig.update_layout(
        title="📈 Profit cumulé par type de jeu",
        xaxis_title="Date",
        yaxis_title="Profit (€)",
        height=450,
        hovermode="x unified",
    )
    return fig


def _afficher_kpis(data: list[dict]) -> None:
    """Affiche les KPIs globaux."""
    if not data:
        st.info("Aucune donnée disponible")
        return

    total_mises = sum(d["mises"] for d in data)
    total_gains = sum(d["gains"] for d in data)
    profit = total_gains - total_mises
    roi = (profit / total_mises * 100) if total_mises > 0 else 0

    paris_g = sum(d["paris_gagnes"] for d in data)
    paris_p = sum(d["paris_perdus"] for d in data)
    taux = (paris_g / (paris_g + paris_p) * 100) if (paris_g + paris_p) > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Mises totales", f"{total_mises:,.2f} €")
    col2.metric("🏆 Gains totaux", f"{total_gains:,.2f} €")
    col3.metric(
        "📊 Profit/Perte",
        f"{profit:+,.2f} €",
        delta=f"{roi:+.1f}% ROI",
        delta_color="normal",
    )
    col4.metric("🎯 Taux réussite", f"{taux:.1f}%", delta=f"{paris_g}G / {paris_p}P")


def _afficher_repartition(data: list[dict]) -> None:
    """Pie chart de répartition des mises."""
    if not data:
        return

    df = pd.DataFrame(data)
    repartition = df.groupby("type_jeu")["mises"].sum().reset_index()
    repartition.columns = ["Type", "Mises"]

    fig = px.pie(
        repartition,
        values="Mises",
        names="Type",
        title="Répartition des mises par type de jeu",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)


def _afficher_tableau_mensuel(data: list[dict]) -> None:
    """Tableau mensuel détaillé."""
    if not data:
        return

    df = pd.DataFrame(data)
    df["mois"] = pd.to_datetime(df["date"]).dt.to_period("M").astype(str)

    mensuel = (
        df.groupby(["mois", "type_jeu"])
        .agg(
            mises=("mises", "sum"),
            gains=("gains", "sum"),
            nb_paris=("nb_paris", "sum"),
        )
        .reset_index()
    )
    mensuel["profit"] = mensuel["gains"] - mensuel["mises"]
    mensuel["roi"] = (mensuel["profit"] / mensuel["mises"] * 100).round(1)

    st.dataframe(
        mensuel.rename(
            columns={
                "mois": "Mois",
                "type_jeu": "Type",
                "mises": "Mises (€)",
                "gains": "Gains (€)",
                "profit": "Profit (€)",
                "roi": "ROI (%)",
                "nb_paris": "Nb paris",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )


def _afficher_meilleurs_pires(data: list[dict]) -> None:
    """Affiche les meilleurs et pires mois."""
    if not data:
        return

    df = pd.DataFrame(data)
    df["mois"] = pd.to_datetime(df["date"]).dt.to_period("M").astype(str)

    mensuel = df.groupby("mois")["profit"].sum().reset_index()

    if len(mensuel) == 0:
        return

    meilleur = mensuel.loc[mensuel["profit"].idxmax()]
    pire = mensuel.loc[mensuel["profit"].idxmin()]

    col1, col2 = st.columns(2)
    with col1:
        st.success(f"🏆 **Meilleur mois**: {meilleur['mois']} — {meilleur['profit']:+,.2f}€")
    with col2:
        st.error(f"📉 **Pire mois**: {pire['mois']} — {pire['profit']:+,.2f}€")


def _afficher_jauge_responsable() -> None:
    """Affiche la jauge de mise responsable."""
    try:
        from src.services.jeux._internal.responsable_gaming import get_responsable_gaming_service

        service = get_responsable_gaming_service()
        suivi = service.obtenir_suivi_mensuel()

        pct = suivi["pourcentage"]
        limite = suivi["limite_mensuelle"]
        utilise = suivi["mises_cumulees"]
        reste = suivi["reste_disponible"]

        st.subheader("🛡️ Mise responsable — mois en cours")

        # Jauge colorée
        if pct >= 100:
            color = "red"
            status = "🔴 LIMITE ATTEINTE"
        elif pct >= 90:
            color = "red"
            status = "🟠 Attention critique"
        elif pct >= 75:
            color = "orange"
            status = "🟡 Prudence"
        elif pct >= 50:
            color = "yellow"
            status = "🟢 Mi-parcours"
        else:
            color = "green"
            status = "🟢 OK"

        st.progress(min(pct / 100, 1.0), text=f"{status} — {pct:.0f}% utilisé")

        cols = st.columns(3)
        cols[0].metric("Budget mensuel", f"{limite:.2f} €")
        cols[1].metric("Dépensé", f"{utilise:.2f} €")
        cols[2].metric("Reste", f"{reste:.2f} €")

        if suivi["est_bloque"]:
            st.error("⛔ Mises bloquées — Limite atteinte ou auto-exclusion active")

        # Message rappel
        st.caption(service.obtenir_message_rappel())

    except Exception as e:
        logger.debug(f"Jauge responsable indisponible: {e}")
        st.info("🛡️ Configurez votre limite mensuelle dans les paramètres.")


@profiler_rerun("bilan_jeux")
def app():
    """Point d'entrée du module Bilan Global Jeux"""

    st.title("📊 Bilan Global — Jeux")
    st.caption("Vue consolidée de vos performances Paris + Loto + Euromillions")

    # ── Outils d'analyse ──
    _c1, _c2, _c3, _c4, _c5 = st.columns(5)
    with _c1:
        if st.button("📈 ROI", key="bil_nav_roi", use_container_width=True):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.naviguer_vers("jeux.comparatif_roi")
            from src.core.state import rerun

            rerun()
    with _c2:
        if st.button("🔔 Alertes", key="bil_nav_alt", use_container_width=True):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.naviguer_vers("jeux.alertes")
            from src.core.state import rerun

            rerun()
    with _c3:
        if st.button("🧠 Biais", key="bil_nav_biais", use_container_width=True):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.naviguer_vers("jeux.biais")
            from src.core.state import rerun

            rerun()
    with _c4:
        if st.button("📅 Calendrier", key="bil_nav_cal", use_container_width=True):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.naviguer_vers("jeux.calendrier")
            from src.core.state import rerun

            rerun()
    with _c5:
        if st.button("🎓 Éducatif", key="bil_nav_edu", use_container_width=True):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.naviguer_vers("jeux.educatif")
            from src.core.state import rerun

            rerun()

    TAB_LABELS = [
        "📈 Vue globale",
        "📊 Détail mensuel",
        "🛡️ Mise responsable",
    ]
    tab_index = tabs_with_url(TAB_LABELS, param="tab")
    tabs = st.tabs(TAB_LABELS)

    # Charger données
    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        jours = st.selectbox(
            "Période",
            [30, 90, 180, 365],
            index=3,
            format_func=lambda x: f"{x} jours",
            key=_keys("periode"),
        )

    data = _charger_historique(jours=jours)

    with tabs[0]:
        with error_boundary("bilan_global"):
            _afficher_kpis(data)
            st.divider()

            if data:
                df = pd.DataFrame(data)
                fig = _build_profit_cumule(df)
                st.plotly_chart(fig, use_container_width=True)

                col1, col2 = st.columns(2)
                with col1:
                    _afficher_repartition(data)
                with col2:
                    _afficher_meilleurs_pires(data)
            else:
                st.info(
                    "Aucune donnée historique. Les données s'accumulent "
                    "automatiquement quand vous utilisez les modules Paris, Loto et Euromillions."
                )

    with tabs[1]:
        with error_boundary("bilan_mensuel"):
            _afficher_tableau_mensuel(data)

    with tabs[2]:
        with error_boundary("bilan_responsable"):
            _afficher_jauge_responsable()


def main():
    app()


__all__ = ["app", "main"]
