"""Composants UI pour le module Garanties & SAV."""

from datetime import date

import streamlit as st

from src.core.state import rerun
from src.ui.fragments import ui_fragment
from src.ui.keys import KeyNamespace

from .constants import STATUTS_GARANTIE_LABELS
from .crud import (
    create_garantie,
    delete_garantie,
    get_alertes_garanties,
    get_all_garanties,
    get_stats_garanties,
    update_garantie,
)

_keys = KeyNamespace("garanties")


def afficher_formulaire_garantie(garantie=None) -> None:
    """Formulaire de création/édition d'une garantie."""
    with st.form(key=_keys("form_garantie")):
        nom_appareil = st.text_input("Appareil *", value=getattr(garantie, "nom_appareil", ""))

        col1, col2, col3 = st.columns(3)
        with col1:
            marque = st.text_input("Marque", value=getattr(garantie, "marque", "") or "")
        with col2:
            modele = st.text_input("Modèle", value=getattr(garantie, "modele", "") or "")
        with col3:
            numero_serie = st.text_input(
                "N°série", value=getattr(garantie, "numero_serie", "") or ""
            )

        col4, col5 = st.columns(2)
        with col4:
            date_achat = st.date_input(
                "Date achat *",
                value=getattr(garantie, "date_achat", date.today()),
            )
        with col5:
            duree_mois = st.number_input(
                "Durée garantie (mois)",
                min_value=1,
                value=int(getattr(garantie, "duree_garantie_mois", 24)),
            )

        col6, col7 = st.columns(2)
        with col6:
            lieu_achat = st.text_input(
                "Lieu achat", value=getattr(garantie, "lieu_achat", "") or ""
            )
        with col7:
            prix_achat = st.number_input(
                "Prix achat (€)",
                min_value=0.0,
                value=float(getattr(garantie, "prix_achat", 0) or 0),
                step=10.0,
            )

        piece = st.text_input("Pièce", value=getattr(garantie, "piece", "") or "")
        notes = st.text_area("Notes", value=getattr(garantie, "notes", "") or "")
        submitted = st.form_submit_button("💾 Enregistrer", use_container_width=True)

    if submitted and nom_appareil:
        from datetime import timedelta
        from decimal import Decimal

        date_fin = date_achat + timedelta(days=duree_mois * 30)
        data = {
            "nom_appareil": nom_appareil,
            "marque": marque or None,
            "modele": modele or None,
            "numero_serie": numero_serie or None,
            "date_achat": date_achat,
            "duree_garantie_mois": duree_mois,
            "date_fin_garantie": date_fin,
            "lieu_achat": lieu_achat or None,
            "prix_achat": Decimal(str(prix_achat)) if prix_achat > 0 else None,
            "piece": piece or None,
            "notes": notes or None,
            "statut": "active",
        }
        if garantie:
            update_garantie(garantie.id, data)
            st.success("✅ Garantie mise à jour !")
        else:
            create_garantie(data)
            st.success("✅ Garantie ajoutée !")
        rerun()


@ui_fragment
def afficher_onglet_dashboard() -> None:
    """Onglet dashboard garanties."""
    stats = get_stats_garanties()
    if not stats:
        st.info("Aucune garantie enregistrée.")
        return
    cols = st.columns(4)
    with cols[0]:
        st.metric("Total", stats.get("total", 0))
    with cols[1]:
        st.metric("Actives", stats.get("actives", 0))
    with cols[2]:
        st.metric("Expirées", stats.get("expirees", 0))
    with cols[3]:
        st.metric("Incidents", stats.get("incidents", 0))

    alertes = get_alertes_garanties(jours=60)
    if alertes:
        st.divider()
        st.warning(f"⚠️ {len(alertes)} garantie(s) expirent bientôt")
        for a in alertes[:5]:
            st.caption(f"🔴 {a['nom_appareil']} — expire dans {a['jours_restants']}j")


@ui_fragment
def afficher_onglet_garanties() -> None:
    """Onglet liste des garanties."""
    filtre = st.selectbox(
        "Statut",
        [""] + list(STATUTS_GARANTIE_LABELS.keys()),
        format_func=lambda x: STATUTS_GARANTIE_LABELS.get(x, "Tous") if x else "Tous",
        key=_keys("filtre_statut"),
    )
    garanties = get_all_garanties(filtre_statut=filtre or None)
    if not garanties:
        st.info("Aucune garantie trouvée.")
        return
    for g in garanties:
        statut_label = STATUTS_GARANTIE_LABELS.get(g.statut, g.statut)
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{g.nom_appareil}**")
                st.caption(f"{g.marque or ''} {g.modele or ''} — {statut_label}")
            with col2:
                jours = (g.date_fin_garantie - date.today()).days
                ic = "🔴" if jours < 30 else "🟡" if jours < 90 else "🟢"
                st.caption(f"{ic} Fin: {g.date_fin_garantie:%d/%m/%Y}")
            with col3:
                if st.button("✏️", key=_keys(f"edit_{g.id}")):
                    st.session_state[_keys("edit_id")] = g.id
                    rerun()
                if st.button("🗑️", key=_keys(f"del_{g.id}")):
                    delete_garantie(g.id)
                    rerun()


@ui_fragment
def afficher_onglet_alertes() -> None:
    """Onglet alertes expiration."""
    jours = st.slider("Horizon (jours)", 30, 365, 90, key=_keys("horizon"))
    alertes = get_alertes_garanties(jours=jours)
    if not alertes:
        st.success("✅ Aucune garantie n'expire prochainement.")
        return
    for a in alertes:
        urgence = "🔴" if a["jours_restants"] < 15 else "🟡" if a["jours_restants"] < 30 else "🟢"
        st.warning(
            f"{urgence} **{a['nom_appareil']}** — expire dans **{a['jours_restants']}j** "
            f"({a['date_fin_garantie']:%d/%m/%Y})"
        )
