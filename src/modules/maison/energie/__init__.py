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

import plotly.graph_objects as go
import streamlit as st

from src.core.db import obtenir_contexte_db
from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.fragments import cached_fragment
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

# Constante attendue par les tests — structure avec emoji/couleur/prix_moyen
ENERGIES = {
    "electricite": {
        "emoji": "⚡",
        "couleur": "#FFD600",
        "unite": "kWh",
        "label": "Électricité",
        "prix_moyen": 0.2276,
    },
    "gaz": {
        "emoji": "🔥",
        "couleur": "#FF6D00",
        "unite": "m³",
        "label": "Gaz",
        "prix_moyen": 0.1284,
    },
    "eau": {
        "emoji": "💧",
        "couleur": "#2196F3",
        "unite": "m³",
        "label": "Eau",
        "prix_moyen": 4.34,
    },
}

# MOIS_FR: index 0 vide, puis abréviations 1-12
MOIS_FR = [
    "",
    "Jan",
    "Fev",
    "Mar",
    "Avr",
    "Mai",
    "Jun",
    "Jul",
    "Aou",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]

MOIS_NOMS = [
    "Janvier",
    "Février",
    "Mars",
    "Avril",
    "Mai",
    "Juin",
    "Juillet",
    "Août",
    "Septembre",
    "Octobre",
    "Novembre",
    "Décembre",
]


# ═══════════════════════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════════════════════


@st.cache_data(ttl=300)
def charger_historique_energie(type_energie: str, nb_mois: int = 12) -> list[dict]:
    """Charge l'historique de consommation énergétique depuis la DB.

    Args:
        type_energie: Type d'énergie (electricite, gaz, eau).
        nb_mois: Nombre de mois d'historique.

    Returns:
        Liste de dicts avec mois, annee, label, montant, consommation.
    """
    today = date.today()
    result = []

    try:
        with obtenir_contexte_db() as db:
            for i in range(nb_mois):
                # Calculer le mois cible (en remontant depuis aujourd'hui)
                mois_offset = nb_mois - 1 - i
                mois = today.month - mois_offset
                annee = today.year
                while mois <= 0:
                    mois += 12
                    annee -= 1

                label = MOIS_FR[mois] if 1 <= mois <= 12 else f"M{mois}"

                # Requête DB pour ce mois
                try:
                    from src.core.models import DepenseMaison
                except ImportError:
                    DepenseMaison = None

                montant = None
                consommation = None

                if DepenseMaison is not None:
                    depense = (
                        db.query(DepenseMaison)
                        .filter(
                            DepenseMaison.categorie == type_energie,
                            DepenseMaison.mois == mois,
                            DepenseMaison.annee == annee,
                        )
                        .first()
                    )
                    if depense:
                        montant = depense.montant
                        consommation = getattr(depense, "consommation", None)

                result.append(
                    {
                        "mois": mois,
                        "annee": annee,
                        "label": label,
                        "montant": montant,
                        "consommation": consommation,
                    }
                )
    except Exception as e:
        logger.error(f"Erreur chargement historique {type_energie}: {e}")
        # Retourner des entrées vides en cas d'erreur
        for i in range(nb_mois):
            mois_offset = nb_mois - 1 - i
            mois = today.month - mois_offset
            annee = today.year
            while mois <= 0:
                mois += 12
                annee -= 1
            label = MOIS_FR[mois] if 1 <= mois <= 12 else f"M{mois}"
            result.append(
                {
                    "mois": mois,
                    "annee": annee,
                    "label": label,
                    "montant": None,
                    "consommation": None,
                }
            )

    return result


def get_stats_energie(type_energie: str) -> dict:
    """Calcule les statistiques pour un type d'énergie.

    Args:
        type_energie: Type d'énergie.

    Returns:
        Dict avec total_annuel, moyenne_mensuelle, conso_totale, etc.
    """
    historique = charger_historique_energie(type_energie)

    montants = [h["montant"] for h in historique if h["montant"] is not None]
    consos = [h["consommation"] for h in historique if h["consommation"] is not None]

    total_annuel = sum(montants) if montants else 0
    moyenne_mensuelle = total_annuel / len(montants) if montants else 0
    conso_totale = sum(consos) if consos else 0
    conso_moyenne = conso_totale / len(consos) if consos else 0

    dernier_montant = montants[-1] if montants else 0
    derniere_conso = consos[-1] if consos else 0
    avant_dernier_montant = montants[-2] if len(montants) >= 2 else dernier_montant
    avant_derniere_conso = consos[-2] if len(consos) >= 2 else derniere_conso

    delta_montant = dernier_montant - avant_dernier_montant
    delta_conso = derniere_conso - avant_derniere_conso
    prix_unitaire = (total_annuel / conso_totale) if conso_totale > 0 else 0

    return {
        "total_annuel": total_annuel,
        "moyenne_mensuelle": moyenne_mensuelle,
        "conso_totale": conso_totale,
        "conso_moyenne": conso_moyenne,
        "dernier_montant": dernier_montant,
        "derniere_conso": derniere_conso,
        "delta_montant": delta_montant,
        "delta_conso": delta_conso,
        "prix_unitaire": prix_unitaire,
    }


# ═══════════════════════════════════════════════════════════
# GRAPHIQUES
# ═══════════════════════════════════════════════════════════


def graphique_evolution(type_energie: str, afficher_conso: bool = True) -> go.Figure:
    """Crée un graphique d'évolution des consommations.

    Args:
        type_energie: Type d'énergie.
        afficher_conso: Afficher la consommation en plus du montant.

    Returns:
        Figure Plotly.
    """
    historique = charger_historique_energie(type_energie)
    labels = [h["label"] for h in historique]
    montants = [h["montant"] or 0 for h in historique]

    config = ENERGIES.get(type_energie, {})
    couleur = config.get("couleur", "#333")

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=labels,
            y=montants,
            mode="lines+markers",
            name="Montant (€)",
            line={"color": couleur},
        )
    )

    if afficher_conso:
        consos = [h["consommation"] or 0 for h in historique]
        fig.add_trace(
            go.Scatter(
                x=labels,
                y=consos,
                mode="lines+markers",
                name=f"Consommation ({config.get('unite', '')})",
                yaxis="y2",
            )
        )
        fig.update_layout(
            yaxis2={"title": config.get("unite", ""), "overlaying": "y", "side": "right"}
        )

    fig.update_layout(
        title=f"Évolution {config.get('label', type_energie)}",
        xaxis_title="Mois",
        yaxis_title="€",
    )

    return fig


def graphique_comparaison_annees(type_energie: str) -> go.Figure:
    """Crée un graphique de comparaison N vs N-1.

    Args:
        type_energie: Type d'énergie.

    Returns:
        Figure Plotly.
    """
    historique = charger_historique_energie(type_energie, nb_mois=24)
    config = ENERGIES.get(type_energie, {})

    annee_courante = date.today().year
    donnees_n = [h for h in historique if h["annee"] == annee_courante]
    donnees_n1 = [h for h in historique if h["annee"] == annee_courante - 1]

    fig = go.Figure()

    if donnees_n:
        fig.add_trace(
            go.Bar(
                x=[h["label"] for h in donnees_n],
                y=[h["montant"] or 0 for h in donnees_n],
                name=str(annee_courante),
            )
        )

    if donnees_n1:
        fig.add_trace(
            go.Bar(
                x=[h["label"] for h in donnees_n1],
                y=[h["montant"] or 0 for h in donnees_n1],
                name=str(annee_courante - 1),
            )
        )

    fig.update_layout(
        title=f"Comparaison {config.get('label', type_energie)} — {annee_courante} vs {annee_courante - 1}",
        barmode="group",
    )

    return fig


def graphique_repartition() -> go.Figure:
    """Crée un graphique de répartition des coûts par type d'énergie.

    Returns:
        Figure Plotly (camembert).
    """
    labels = []
    values = []
    colors = []

    for type_id, config in ENERGIES.items():
        stats = get_stats_energie(type_id)
        if stats["total_annuel"] > 0:
            labels.append(config["label"])
            values.append(stats["total_annuel"])
            colors.append(config["couleur"])

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                marker={"colors": colors},
                textinfo="label+percent",
            )
        ]
    )
    fig.update_layout(title="Répartition des coûts énergétiques")

    return fig


# ═══════════════════════════════════════════════════════════
# UI COMPONENTS
# ═══════════════════════════════════════════════════════════


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
        "⚡ Électricité",
        "🔥 Gaz",
        "💧 Eau",
        "🚨 Alertes",
    ]
    tabs_with_url(TAB_LABELS, param="tab")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(TAB_LABELS)

    with tab1:
        with error_boundary(titre="Erreur dashboard énergie"):
            afficher_dashboard_global()
            col1, col2 = st.columns(2)
            with col1:
                fig = graphique_repartition()
                st.plotly_chart(fig, use_container_width=True)

    with tab2:
        with error_boundary(titre="Erreur détail électricité"):
            afficher_detail_energie("electricite")

    with tab3:
        with error_boundary(titre="Erreur détail gaz"):
            afficher_detail_energie("gaz")

    with tab4:
        with error_boundary(titre="Erreur détail eau"):
            afficher_detail_energie("eau")

    with tab5:
        with error_boundary(titre="Erreur alertes"):
            afficher_alertes()


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


@cached_fragment(ttl=300)
def _build_energie_line(dates: tuple, valeurs: tuple, label: str, unite: str, color: str):
    """Construit le line chart d'évolution énergie (caché 5 min)."""
    import pandas as pd
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
    import pandas as pd
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
