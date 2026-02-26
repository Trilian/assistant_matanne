"""Composants UI pour le module Diagnostics."""

from datetime import date

import streamlit as st

from src.core.state import rerun
from src.ui.fragments import ui_fragment
from src.ui.keys import KeyNamespace

from .constants import SCORES_DPE, SOURCES_ESTIMATION, TYPES_DIAGNOSTIC_LABELS, VALIDITE_DIAGNOSTICS
from .crud import (
    create_diagnostic,
    create_estimation,
    delete_diagnostic,
    get_alertes_diagnostics,
    get_all_diagnostics,
    get_all_estimations,
    update_diagnostic,
)

_keys = KeyNamespace("diagnostics")


def afficher_formulaire_diagnostic(diag=None) -> None:
    """Formulaire de création/édition d'un diagnostic."""
    with st.form(key=_keys("form_diag")):
        types_list = list(TYPES_DIAGNOSTIC_LABELS.keys())
        idx = 0
        if diag and hasattr(diag, "type_diagnostic") and diag.type_diagnostic in types_list:
            idx = types_list.index(diag.type_diagnostic)
        type_diagnostic = st.selectbox(
            "Type *",
            types_list,
            format_func=lambda x: TYPES_DIAGNOSTIC_LABELS[x],
            index=idx,
        )

        col1, col2 = st.columns(2)
        with col1:
            date_realisation = st.date_input(
                "Date réalisation *",
                value=getattr(diag, "date_realisation", date.today()),
            )
        with col2:
            diagnostiqueur = st.text_input(
                "Diagnostiqueur", value=getattr(diag, "diagnostiqueur", "") or ""
            )

        resultat = st.text_input("Résultat", value=getattr(diag, "resultat", "") or "")

        # DPE specific
        score_energie = None
        score_ges = None
        conso = None
        if type_diagnostic == "dpe":
            st.markdown("**🏠 Scores DPE**")
            col3, col4 = st.columns(2)
            with col3:
                idx_e = 3
                if diag and diag.score_energie in SCORES_DPE:
                    idx_e = SCORES_DPE.index(diag.score_energie)
                score_energie = st.selectbox("Énergie", SCORES_DPE, index=idx_e)
            with col4:
                idx_g = 3
                if diag and diag.score_ges in SCORES_DPE:
                    idx_g = SCORES_DPE.index(diag.score_ges)
                score_ges = st.selectbox("GES", SCORES_DPE, index=idx_g)
            conso = st.number_input(
                "Conso kWh/m²/an",
                min_value=0.0,
                value=float(getattr(diag, "consommation_kwh_m2", 0) or 0),
            )

        recommandations = st.text_area(
            "Recommandations", value=getattr(diag, "recommandations", "") or ""
        )
        notes = st.text_area("Notes", value=getattr(diag, "notes", "") or "")
        submitted = st.form_submit_button("💾 Enregistrer", use_container_width=True)

    if submitted:
        validite_ans = VALIDITE_DIAGNOSTICS.get(type_diagnostic)
        date_validite = None
        if validite_ans:
            from datetime import timedelta

            date_validite = date_realisation + timedelta(days=int(validite_ans * 365))

        data = {
            "type_diagnostic": type_diagnostic,
            "date_realisation": date_realisation,
            "diagnostiqueur": diagnostiqueur or None,
            "resultat": resultat or None,
            "date_validite": date_validite,
            "score_energie": score_energie,
            "score_ges": score_ges,
            "consommation_kwh_m2": conso,
            "recommandations": recommandations or None,
            "notes": notes or None,
        }
        if diag:
            update_diagnostic(diag.id, data)
            st.success("✅ Diagnostic mis à jour !")
        else:
            create_diagnostic(data)
            st.success("✅ Diagnostic ajouté !")
        rerun()


def afficher_formulaire_estimation() -> None:
    """Formulaire d'estimation immobilière."""
    with st.form(key=_keys("form_estimation")):
        sources_list = list(SOURCES_ESTIMATION.keys())
        source = st.selectbox("Source *", sources_list, format_func=lambda x: SOURCES_ESTIMATION[x])
        date_estimation = st.date_input("Date *", value=date.today())

        col1, col2, col3 = st.columns(3)
        with col1:
            valeur_basse = st.number_input("Valeur basse (€)", min_value=0, step=5000)
        with col2:
            valeur_moyenne = st.number_input("Valeur moyenne (€) *", min_value=0, step=5000)
        with col3:
            valeur_haute = st.number_input("Valeur haute (€)", min_value=0, step=5000)

        col4, col5 = st.columns(2)
        with col4:
            surface_m2 = st.number_input("Surface m²", min_value=0.0, step=1.0)
        with col5:
            nb_pieces = st.number_input("Nb pièces", min_value=0, step=1)

        notes = st.text_area("Notes")
        submitted = st.form_submit_button("💾 Enregistrer", use_container_width=True)

    if submitted and valeur_moyenne > 0:
        from decimal import Decimal

        data = {
            "source": source,
            "date_estimation": date_estimation,
            "valeur_basse": Decimal(str(valeur_basse)) if valeur_basse > 0 else None,
            "valeur_moyenne": Decimal(str(valeur_moyenne)),
            "valeur_haute": Decimal(str(valeur_haute)) if valeur_haute > 0 else None,
            "prix_m2": (Decimal(str(int(valeur_moyenne / surface_m2))) if surface_m2 > 0 else None),
            "surface_m2": surface_m2 if surface_m2 > 0 else None,
            "nb_pieces": nb_pieces if nb_pieces > 0 else None,
            "notes": notes or None,
        }
        create_estimation(data)
        st.success("✅ Estimation enregistrée !")
        rerun()


@ui_fragment
def afficher_onglet_dashboard() -> None:
    """Vue d'ensemble : dernier DPE + alertes + dernière estimation."""
    diags = get_all_diagnostics()
    if not diags:
        st.info("Aucun diagnostic enregistré.")
        return

    # Dernier DPE
    dpes = [d for d in diags if d.type_diagnostic == "dpe"]
    if dpes:
        dpe = dpes[-1]
        cols = st.columns(3)
        with cols[0]:
            st.metric("DPE Énergie", dpe.score_energie or "—")
        with cols[1]:
            st.metric("DPE GES", dpe.score_ges or "—")
        with cols[2]:
            st.metric("Conso kWh/m²", f"{dpe.consommation_kwh_m2 or 0:.0f}")

    st.markdown(f"**{len(diags)} diagnostic(s) enregistré(s)**")
    alertes = get_alertes_diagnostics(jours=180)
    if alertes:
        st.warning(f"⚠️ {len(alertes)} diagnostic(s) à renouveler prochainement")

    # Dernière estimation
    estimations = get_all_estimations()
    if estimations:
        est = estimations[-1]
        st.divider()
        st.subheader("💰 Dernière estimation")
        cols = st.columns(3)
        with cols[0]:
            st.metric("Valeur", f"{float(est.valeur_moyenne):,.0f}€")
        with cols[1]:
            if est.prix_m2:
                st.metric("€/m²", f"{float(est.prix_m2):,.0f}")
        with cols[2]:
            st.caption(f"Source: {SOURCES_ESTIMATION.get(est.source, est.source)}")


@ui_fragment
def afficher_onglet_diagnostics() -> None:
    """Onglet liste des diagnostics."""
    filtre = st.selectbox(
        "Type",
        [""] + list(TYPES_DIAGNOSTIC_LABELS.keys()),
        format_func=lambda x: TYPES_DIAGNOSTIC_LABELS.get(x, "Tous") if x else "Tous",
        key=_keys("filtre_type"),
    )
    diags = get_all_diagnostics(filtre_type=filtre or None)
    if not diags:
        st.info("Aucun diagnostic.")
        return
    for d in diags:
        label = TYPES_DIAGNOSTIC_LABELS.get(d.type_diagnostic, d.type_diagnostic)
        validite = d.date_validite
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{label}**")
                st.caption(
                    f"Réalisé le {d.date_realisation:%d/%m/%Y}"
                    + (f" — Résultat: {d.resultat}" if d.resultat else "")
                )
            with col2:
                if validite:
                    jours = (validite - date.today()).days
                    ic = "🔴" if jours < 60 else "🟡" if jours < 365 else "🟢"
                    st.caption(f"{ic} Valide jusqu'au {validite:%d/%m/%Y}")
                else:
                    st.caption("♾️ Illimité")
            with col3:
                if st.button("✏️", key=_keys(f"edit_{d.id}")):
                    st.session_state[_keys("edit_id")] = d.id
                    rerun()
                if st.button("🗑️", key=_keys(f"del_{d.id}")):
                    delete_diagnostic(d.id)
                    rerun()


@ui_fragment
def afficher_onglet_estimation() -> None:
    """Onglet estimation immobilière."""
    estimations = get_all_estimations()
    if not estimations:
        st.info("Aucune estimation. Ajoutez-en une ci-dessous.")
    else:
        for e in reversed(estimations):
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.markdown(f"**{float(e.valeur_moyenne):,.0f}€**")
                    if e.valeur_basse and e.valeur_haute:
                        st.caption(
                            f"Fourchette: {float(e.valeur_basse):,.0f}€ — "
                            f"{float(e.valeur_haute):,.0f}€"
                        )
                with col2:
                    st.caption(f"📅 {e.date_estimation:%d/%m/%Y}")
                    st.caption(SOURCES_ESTIMATION.get(e.source, e.source))
                with col3:
                    if e.prix_m2:
                        st.metric("€/m²", f"{float(e.prix_m2):,.0f}")

    st.divider()
    afficher_formulaire_estimation()


@ui_fragment
def afficher_onglet_alertes() -> None:
    """Onglet alertes de validité des diagnostics."""
    jours = st.slider("Horizon (jours)", 30, 730, 180, key=_keys("horizon"))
    alertes = get_alertes_diagnostics(jours=jours)
    if not alertes:
        st.success("✅ Tous les diagnostics sont à jour.")
        return
    for a in alertes:
        label = TYPES_DIAGNOSTIC_LABELS.get(a["type_diagnostic"], a["type_diagnostic"])
        urgence = "🔴" if a["jours_restants"] < 30 else "🟡" if a["jours_restants"] < 90 else "🟢"
        st.warning(
            f"{urgence} **{label}** expire dans **{a['jours_restants']}j** "
            f"({a['date_validite']:%d/%m/%Y})"
        )
