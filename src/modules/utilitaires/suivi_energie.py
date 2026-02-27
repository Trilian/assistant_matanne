"""
Module Suivi Énergie — Tracking consommation électricité, gaz, eau.

Saisie des relevés mensuels, graphiques d'évolution, comparaison
inter-mois et calcul des coûts estimés.
"""

import logging
from datetime import date

import streamlit as st

from src.core.models.utilitaires import CategorieEnergie
from src.core.monitoring import profiler_rerun
from src.modules._framework import error_boundary
from src.services.utilitaires.service import get_energie_service
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("suivi_energie")

# Prix unitaires moyens (France 2024-2025, à adapter)
PRIX_UNITAIRES = {
    "electricite": {"unite": "kWh", "prix": 0.2516, "emoji": "⚡"},
    "gaz": {"unite": "kWh", "prix": 0.1284, "emoji": "🔥"},
    "eau": {"unite": "m³", "prix": 4.34, "emoji": "💧"},
}


@profiler_rerun("suivi_energie")
def app():
    """Point d'entrée module Suivi Énergie."""
    st.title("⚡ Suivi Consommation Énergie")
    st.caption("Électricité, gaz et eau — relevés et graphiques")

    with error_boundary(titre="Erreur énergie"):
        service = get_energie_service()

        tab1, tab2, tab3 = st.tabs(["📝 Saisie relevé", "📊 Graphiques", "💰 Coûts estimés"])

        with tab1:
            _onglet_saisie(service)
        with tab2:
            _onglet_graphiques(service)
        with tab3:
            _onglet_couts(service)


def _onglet_saisie(service):
    """Formulaire de saisie d'un nouveau relevé."""
    st.subheader("📝 Nouveau relevé")

    with st.form("form_releve", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            type_energie = st.selectbox(
                "Type",
                options=[c.value for c in CategorieEnergie],
                format_func=lambda x: f"{PRIX_UNITAIRES.get(x, {}).get('emoji', '')} {x.capitalize()}",
                key=_keys("new_cat"),
            )
        with col2:
            mois = st.number_input(
                "Mois", min_value=1, max_value=12, value=date.today().month, key=_keys("new_mois")
            )
        with col3:
            annee = st.number_input(
                "Année",
                min_value=2020,
                max_value=2030,
                value=date.today().year,
                key=_keys("new_annee"),
            )

        col_a, col_b = st.columns(2)
        with col_a:
            unite = PRIX_UNITAIRES.get(type_energie, {}).get("unite", "unité")
            consommation = st.number_input(
                f"Consommation ({unite})",
                min_value=0.0,
                step=1.0,
                key=_keys("new_valeur"),
            )
        with col_b:
            montant = st.number_input(
                "Montant facturé (€, optionnel)",
                min_value=0.0,
                step=0.01,
                value=0.0,
                key=_keys("new_cout"),
            )

        notes = st.text_input(
            "Notes",
            placeholder="Période de facturation...",
            key=_keys("new_notes"),
        )

        if st.form_submit_button("💾 Enregistrer", use_container_width=True):
            if consommation > 0:
                try:
                    service.creer(
                        type_energie=type_energie,
                        mois=mois,
                        annee=annee,
                        consommation=consommation,
                        unite=unite,
                        montant=montant if montant > 0 else None,
                        notes=notes or None,
                    )
                    st.success("Relevé enregistré !")
                    st.rerun()
                except Exception as e:
                    logger.exception("Erreur en créant le relevé énergie")
                    st.error(
                        "Erreur lors de l'enregistrement du relevé. Voir le détail ci-dessous."
                    )
                    st.exception(e)
            else:
                st.warning("La consommation doit être supérieure à 0.")

    # Derniers relevés
    st.divider()
    st.subheader("📋 Derniers relevés")

    try:
        releves = service.lister()
    except Exception as e:
        logger.exception("Erreur chargement des relevés énergie")
        st.error("Impossible de charger les relevés énergie. Voir le détail ci-dessous.")
        st.exception(e)
        releves = []

    if releves:
        for r in releves[:20]:
            info = PRIX_UNITAIRES.get(r.type_energie, {})
            emoji = info.get("emoji", "📊")
            unite_r = r.unite or info.get("unite", "")
            montant_str = f" — {r.montant:.2f}€" if r.montant else ""
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.markdown(
                        f"{emoji} **{r.type_energie.capitalize()}** — " f"{r.mois:02d}/{r.annee}"
                    )
                with col2:
                    conso = float(r.consommation) if r.consommation else 0
                    st.markdown(f"**{conso:.1f} {unite_r}**{montant_str}")
                with col3:
                    if st.button("🗑️", key=_keys("del", str(r.id))):
                        service.supprimer(r.id)
                        st.rerun()
    else:
        st.info("Aucun relevé enregistré.")


def _onglet_graphiques(service):
    """Graphiques d'évolution de la consommation."""
    st.subheader("📊 Évolution de la consommation")

    type_energie = st.selectbox(
        "Type d'énergie",
        options=[c.value for c in CategorieEnergie],
        format_func=lambda x: f"{PRIX_UNITAIRES.get(x, {}).get('emoji', '')} {x.capitalize()}",
        key=_keys("graph_cat"),
    )

    try:
        releves = service.lister(type_energie=type_energie)
    except Exception as e:
        logger.exception("Erreur chargement des relevés pour graphiques énergie")
        st.error("Impossible de charger les relevés pour le graphique. Voir le détail ci-dessous.")
        st.exception(e)
        releves = []

    if not releves or len(releves) < 2:
        st.info("Pas assez de données pour afficher un graphique (minimum 2 relevés).")
        return

    import pandas as pd

    df = pd.DataFrame(
        [
            {"Période": f"{r.mois:02d}/{r.annee}", "Consommation": float(r.consommation or 0)}
            for r in releves
        ]
    )
    df = df.sort_values("Période")

    unite = PRIX_UNITAIRES.get(type_energie, {}).get("unite", "")
    st.line_chart(df.set_index("Période"), y="Consommation")
    st.caption(f"Unité: {unite}")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Moyenne", f"{df['Consommation'].mean():.1f} {unite}")
    with col2:
        st.metric("Maximum", f"{df['Consommation'].max():.1f} {unite}")
    with col3:
        st.metric("Minimum", f"{df['Consommation'].min():.1f} {unite}")


def _onglet_couts(service):
    """Estimation des coûts basée sur les relevés."""
    st.subheader("💰 Estimation des coûts")

    st.info(
        "💡 Les prix unitaires sont des moyennes France 2024-2025. " "Ajustez selon votre contrat."
    )

    with st.expander("⚙️ Personnaliser les prix unitaires"):
        prix_custom = {}
        for cat, info in PRIX_UNITAIRES.items():
            prix_custom[cat] = st.number_input(
                f"{info['emoji']} {cat.capitalize()} (€/{info['unite']})",
                value=info["prix"],
                step=0.01,
                format="%.4f",
                key=_keys("prix", cat),
            )

    st.divider()

    for cat, info in PRIX_UNITAIRES.items():
        try:
            releves = service.lister(type_energie=cat)
        except Exception as e:
            logger.exception("Erreur chargement des relevés pour coûts énergie")
            st.error(f"Impossible de charger les relevés pour {cat}. Voir le détail ci-dessous.")
            st.exception(e)
            continue

        releves = releves[:12]  # Limiter aux 12 derniers
        if not releves:
            continue

        emoji = info["emoji"]
        unite = info["unite"]
        prix = prix_custom.get(cat, info["prix"])

        total_conso = sum(float(r.consommation or 0) for r in releves)
        total_cout_estime = total_conso * prix
        total_cout_reel = sum(float(r.montant or 0) for r in releves if r.montant)
        nb_releves = len(releves)

        with st.container(border=True):
            st.markdown(f"### {emoji} {cat.capitalize()}")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Relevés", nb_releves)
            with col2:
                st.metric("Total conso", f"{total_conso:.1f} {unite}")
            with col3:
                st.metric("Coût estimé", f"{total_cout_estime:.2f} €")
            with col4:
                if total_cout_reel > 0:
                    st.metric("Coût réel", f"{total_cout_reel:.2f} €")
                else:
                    st.caption("Pas de coût réel saisi")
