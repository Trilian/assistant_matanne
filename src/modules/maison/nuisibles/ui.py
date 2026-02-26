"""Composants UI pour le module Nuisibles."""

from datetime import date

import streamlit as st

from src.core.state import rerun
from src.ui.fragments import ui_fragment
from src.ui.keys import KeyNamespace

from .constants import EFFICACITE_LABELS, METHODES_LABELS, TYPES_NUISIBLE_LABELS
from .crud import (
    create_traitement,
    delete_traitement,
    get_all_traitements,
    update_traitement,
)

_keys = KeyNamespace("nuisibles")


def afficher_formulaire_traitement(traitement=None) -> None:
    """Formulaire de création/édition d'un traitement."""
    with st.form(key=_keys("form_traitement")):
        types_list = list(TYPES_NUISIBLE_LABELS.keys())
        idx = 0
        if (
            traitement
            and hasattr(traitement, "type_nuisible")
            and traitement.type_nuisible in types_list
        ):
            idx = types_list.index(traitement.type_nuisible)
        type_nuisible = st.selectbox(
            "Type *",
            types_list,
            format_func=lambda x: TYPES_NUISIBLE_LABELS[x],
            index=idx,
        )

        col1, col2 = st.columns(2)
        with col1:
            zone = st.text_input("Zone", value=getattr(traitement, "zone", "") or "")
        with col2:
            est_preventif = st.checkbox(
                "Préventif", value=getattr(traitement, "est_preventif", False)
            )

        produit = st.text_input("Produit utilisé", value=getattr(traitement, "produit", "") or "")

        methodes_list = list(METHODES_LABELS.keys())
        idx_m = 0
        if traitement and hasattr(traitement, "methode") and traitement.methode in methodes_list:
            idx_m = methodes_list.index(traitement.methode)
        methode = st.selectbox(
            "Méthode",
            methodes_list,
            format_func=lambda x: METHODES_LABELS[x],
            index=idx_m,
        )

        col3, col4 = st.columns(2)
        with col3:
            date_traitement = st.date_input(
                "Date *",
                value=getattr(traitement, "date_traitement", date.today()),
            )
        with col4:
            frequence_jours = st.number_input(
                "Renouvellement (jours)",
                min_value=0,
                value=int(getattr(traitement, "frequence_jours", 0) or 0),
            )

        col5, col6 = st.columns(2)
        with col5:
            est_bio = st.checkbox("Bio/naturel", value=getattr(traitement, "est_bio", False))
        with col6:
            efficacite = st.slider(
                "Efficacité",
                1,
                5,
                value=int(getattr(traitement, "efficacite", 3) or 3),
            )

        cout = st.number_input(
            "Coût (€)",
            min_value=0.0,
            value=float(getattr(traitement, "cout", 0) or 0),
            step=5.0,
        )
        notes = st.text_area("Notes", value=getattr(traitement, "notes", "") or "")
        submitted = st.form_submit_button("💾 Enregistrer", use_container_width=True)

    if submitted:
        from datetime import timedelta
        from decimal import Decimal

        data = {
            "type_nuisible": type_nuisible,
            "zone": zone or None,
            "est_preventif": est_preventif,
            "produit": produit or None,
            "methode": methode,
            "date_traitement": date_traitement,
            "date_prochain_traitement": (
                (date_traitement + timedelta(days=frequence_jours)) if frequence_jours > 0 else None
            ),
            "frequence_jours": frequence_jours if frequence_jours > 0 else None,
            "est_bio": est_bio,
            "efficacite": efficacite,
            "cout": Decimal(str(cout)) if cout > 0 else None,
            "notes": notes or None,
        }
        if traitement:
            update_traitement(traitement.id, data)
            st.success("✅ Traitement mis à jour !")
        else:
            create_traitement(data)
            st.success("✅ Traitement enregistré !")
        rerun()


@ui_fragment
def afficher_onglet_dashboard() -> None:
    """Onglet récap nuisibles."""
    traitements = get_all_traitements()
    if not traitements:
        st.info("Aucun traitement enregistré.")
        return
    total = len(traitements)
    preventifs = sum(1 for t in traitements if t.est_preventif)
    resolus = sum(1 for t in traitements if t.probleme_resolu)
    cols = st.columns(3)
    with cols[0]:
        st.metric("Traitements", total)
    with cols[1]:
        st.metric("Préventifs", preventifs)
    with cols[2]:
        st.metric("Problèmes résolus", resolus)

    # Prochains traitements
    prochains = [
        t
        for t in traitements
        if t.date_prochain_traitement and t.date_prochain_traitement >= date.today()
    ]
    prochains.sort(key=lambda t: t.date_prochain_traitement)
    if prochains:
        st.divider()
        st.markdown("**🔜 Prochains traitements :**")
        for t in prochains[:5]:
            jours = (t.date_prochain_traitement - date.today()).days
            label = TYPES_NUISIBLE_LABELS.get(t.type_nuisible, t.type_nuisible)
            st.caption(f"{label} — dans {jours}j ({t.date_prochain_traitement:%d/%m/%Y})")


@ui_fragment
def afficher_onglet_historique() -> None:
    """Onglet historique traitements."""
    filtre = st.selectbox(
        "Type",
        [""] + list(TYPES_NUISIBLE_LABELS.keys()),
        format_func=lambda x: TYPES_NUISIBLE_LABELS.get(x, "Tous") if x else "Tous",
        key=_keys("filtre_type"),
    )
    traitements = get_all_traitements(filtre_type=filtre or None)
    if not traitements:
        st.info("Aucun traitement trouvé.")
        return
    for t in traitements:
        label = TYPES_NUISIBLE_LABELS.get(t.type_nuisible, t.type_nuisible)
        eff = EFFICACITE_LABELS.get(t.efficacite, "") if t.efficacite else ""
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{label}** — {t.methode or ''}")
                st.caption(
                    f"📅 {t.date_traitement:%d/%m/%Y}"
                    + (f" | {t.produit}" if t.produit else "")
                    + (" | 🌿 Bio" if t.est_bio else "")
                )
            with col2:
                if eff:
                    st.caption(eff)
            with col3:
                if st.button("✏️", key=_keys(f"edit_{t.id}")):
                    st.session_state[_keys("edit_id")] = t.id
                    rerun()
                if st.button("🗑️", key=_keys(f"del_{t.id}")):
                    delete_traitement(t.id)
                    rerun()
