"""Composants UI pour le module Relevés Compteurs."""

from __future__ import annotations

from datetime import date

import streamlit as st

from src.core.state import rerun
from src.modules._framework import ui_fragment
from src.ui.keys import KeyNamespace

from .constants import TYPES_COMPTEUR_LABELS, UNITES_COMPTEUR
from .crud import create_releve, get_all_releves, get_stats_releves

_keys = KeyNamespace("releves_ui")


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
@ui_fragment
def afficher_onglet_dashboard():
    """Affiche le dashboard des consommations par compteur."""
    type_compteur = st.selectbox(
        "Type de compteur",
        list(TYPES_COMPTEUR_LABELS.keys()),
        format_func=lambda k: TYPES_COMPTEUR_LABELS[k],
        key=_keys("dash_type"),
    )

    stats = get_stats_releves(type_compteur)
    unite = UNITES_COMPTEUR.get(type_compteur, "")

    if not stats or not stats.get("releves"):
        st.info(f"Aucun relevé {TYPES_COMPTEUR_LABELS[type_compteur]} enregistré.")
        return

    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Relevés", stats.get("nb_releves", 0))
    with col2:
        conso_moy = stats.get("consommation_moyenne")
        st.metric(
            "Conso moyenne",
            f"{conso_moy:,.1f} {unite}" if conso_moy is not None else "N/C",
        )
    with col3:
        conso_total = stats.get("consommation_totale")
        st.metric(
            "Conso totale",
            f"{conso_total:,.1f} {unite}" if conso_total is not None else "N/C",
        )
    with col4:
        anomalies = stats.get("anomalies", 0)
        st.metric("Anomalies", anomalies, delta_color="inverse" if anomalies else "off")

    # Graphique d'évolution
    releves = stats.get("releves", [])
    if len(releves) >= 2:
        import pandas as pd

        df = pd.DataFrame(
            [
                {
                    "Date": r.date_releve,
                    "Index": r.valeur_index,
                    "Consommation": r.consommation,
                }
                for r in releves
                if r.date_releve
            ]
        ).sort_values("Date")

        if not df.empty and "Consommation" in df.columns:
            st.subheader("📈 Évolution de la consommation")
            chart_df = df[df["Consommation"].notna()]
            if not chart_df.empty:
                st.line_chart(chart_df.set_index("Date")["Consommation"])

    # Alertes d'anomalies
    releves_anomalies = [r for r in releves if getattr(r, "anomalie", False)]
    if releves_anomalies:
        st.subheader("⚠️ Anomalies détectées")
        for r in releves_anomalies:
            st.warning(
                f"Relevé du {r.date_releve} — Consommation : {r.consommation} {unite} "
                f"(notes : {r.notes or 'aucune'})"
            )


# ---------------------------------------------------------------------------
# Historique
# ---------------------------------------------------------------------------
@ui_fragment
def afficher_onglet_historique():
    """Affiche l'historique complet des relevés."""
    type_compteur = st.selectbox(
        "Filtrer par type",
        ["Tous"] + list(TYPES_COMPTEUR_LABELS.keys()),
        format_func=lambda k: TYPES_COMPTEUR_LABELS.get(k, "📊 Tous"),
        key=_keys("hist_type"),
    )

    type_filtre = type_compteur if type_compteur != "Tous" else None
    releves = get_all_releves(type_compteur=type_filtre)

    if not releves:
        st.info("Aucun relevé enregistré.")
        return

    st.markdown(f"**{len(releves)} relevé(s)**")

    for releve in releves:
        type_label = TYPES_COMPTEUR_LABELS.get(releve.type_compteur, releve.type_compteur)
        unite = UNITES_COMPTEUR.get(releve.type_compteur, "")
        conso_str = f"{releve.consommation:,.1f} {unite}" if releve.consommation else "—"
        anomalie_badge = " 🔴" if getattr(releve, "anomalie", False) else ""

        with st.expander(
            f"{type_label} | {releve.date_releve or '?'} — Index: {releve.valeur_index}{anomalie_badge}"
        ):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Index", f"{releve.valeur_index:,.1f}" if releve.valeur_index else "N/C")
            with c2:
                st.metric("Consommation", conso_str)
            with c3:
                if releve.cout:
                    st.metric("Coût", f"{releve.cout:,.2f} €")
                else:
                    st.metric("Coût", "N/C")

            if releve.notes:
                st.caption(releve.notes)


# ---------------------------------------------------------------------------
# Formulaire ajout
# ---------------------------------------------------------------------------
@ui_fragment
def afficher_formulaire_releve():
    """Formulaire d'ajout d'un relevé de compteur."""
    with st.form(_keys("form_new"), clear_on_submit=True):
        st.subheader("📝 Nouveau relevé")

        col1, col2 = st.columns(2)
        with col1:
            type_compteur = st.selectbox(
                "Type de compteur *",
                list(TYPES_COMPTEUR_LABELS.keys()),
                format_func=lambda k: TYPES_COMPTEUR_LABELS[k],
                key=_keys("new_type"),
            )
            valeur_index = st.number_input(
                f"Valeur index ({UNITES_COMPTEUR.get(type_compteur, '')}) *",
                min_value=0.0,
                step=1.0,
                key=_keys("new_index"),
            )
        with col2:
            date_releve = st.date_input(
                "Date du relevé",
                value=date.today(),
                key=_keys("new_date"),
            )
            cout = st.number_input(
                "Coût (€)",
                min_value=0.0,
                step=1.0,
                value=0.0,
                key=_keys("new_cout"),
            )

        notes = st.text_area("Notes", key=_keys("new_notes"))

        # Champs optionnels supplémentaires
        col3, col4, col5 = st.columns([1, 2, 2])
        with col3:
            etat_note = st.slider("État (note)", 1, 5, 3, key=_keys("new_etat_note"))
        with col4:
            objectif = st.text_input("Objectif (optionnel)", key=_keys("new_objectif"))
        with col5:
            programmer = st.checkbox("Programmer une action", key=_keys("new_enable_next"))
            if programmer:
                date_prochaine_action = st.date_input(
                    "Date prochaine action",
                    value=date.today(),
                    key=_keys("new_date_next"),
                )
            else:
                date_prochaine_action = None

        photos = st.file_uploader(
            "Photos (optionnel)",
            accept_multiple_files=True,
            type=["png", "jpg", "jpeg", "pdf"],
            key=_keys("new_photos"),
        )

        submitted = st.form_submit_button("➕ Ajouter le relevé")

        if submitted:
            if not valeur_index:
                st.error("La valeur d'index est obligatoire.")
                return

            photos_list = [f.name for f in photos] if photos else None

            data = {
                "type_compteur": type_compteur,
                "valeur_index": valeur_index,
                "date_releve": date_releve,
                "cout": cout or None,
                "notes": notes or None,
                "etat_note": int(etat_note),
                "objectif": objectif or None,
                "date_prochaine_action": date_prochaine_action,
                "photos": photos_list,
            }
            create_releve(data)
            st.success("Relevé ajouté !")
            rerun()
