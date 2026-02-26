"""Composants UI pour le module Artisans."""

from datetime import date

import streamlit as st

from src.core.state import rerun
from src.ui.fragments import ui_fragment
from src.ui.keys import KeyNamespace

from .constants import METIERS_LABELS, NOTE_LABELS
from .crud import (
    create_artisan,
    create_intervention,
    delete_artisan,
    get_all_artisans,
    get_interventions_artisan,
    get_stats_artisans,
    update_artisan,
)

_keys = KeyNamespace("artisans")


def afficher_formulaire_artisan(artisan=None) -> None:
    """Formulaire de création/édition d'un artisan."""
    with st.form(key=_keys("form_artisan")):
        nom = st.text_input("Nom *", value=getattr(artisan, "nom", ""))

        col1, col2 = st.columns(2)
        with col1:
            metiers_list = list(METIERS_LABELS.keys())
            idx = 0
            if artisan and hasattr(artisan, "metier") and artisan.metier in metiers_list:
                idx = metiers_list.index(artisan.metier)
            metier = st.selectbox(
                "Métier *",
                metiers_list,
                format_func=lambda x: METIERS_LABELS[x],
                index=idx,
            )
        with col2:
            entreprise = st.text_input("Entreprise", value=getattr(artisan, "entreprise", "") or "")

        col3, col4 = st.columns(2)
        with col3:
            telephone = st.text_input("Téléphone *", value=getattr(artisan, "telephone", "") or "")
        with col4:
            email = st.text_input("Email", value=getattr(artisan, "email", "") or "")

        adresse = st.text_input("Adresse", value=getattr(artisan, "adresse", "") or "")
        site_web = st.text_input("Site web", value=getattr(artisan, "site_web", "") or "")

        col5, col6 = st.columns(2)
        with col5:
            recommande = st.checkbox("Recommandé", value=getattr(artisan, "recommande", True))
        with col6:
            assurance_decennale = st.checkbox(
                "Assurance décennale",
                value=getattr(artisan, "assurance_decennale", False),
            )

        qualifications = st.text_input(
            "Qualifications (RGE, Qualibat...)",
            value=getattr(artisan, "qualifications", "") or "",
        )
        notes = st.text_area("Notes", value=getattr(artisan, "notes", "") or "")

        submitted = st.form_submit_button("💾 Enregistrer", use_container_width=True)

    if submitted and nom and telephone:
        data = {
            "nom": nom,
            "metier": metier,
            "entreprise": entreprise or None,
            "telephone": telephone,
            "email": email or None,
            "adresse": adresse or None,
            "site_web": site_web or None,
            "recommande": recommande,
            "assurance_decennale": assurance_decennale,
            "qualifications": qualifications or None,
            "notes": notes or None,
        }
        if artisan:
            update_artisan(artisan.id, data)
            st.success("✅ Artisan mis à jour !")
        else:
            create_artisan(data)
            st.success("✅ Artisan ajouté !")
        rerun()


def afficher_formulaire_intervention(artisan_id: int = None) -> None:
    """Formulaire d'ajout d'une intervention."""
    artisans = get_all_artisans()
    if not artisans:
        st.info("Ajoutez d'abord un artisan.")
        return

    with st.form(key=_keys("form_intervention")):
        if artisan_id:
            a = next((a for a in artisans if a.id == artisan_id), None)
            st.markdown(f"**Artisan : {a.nom if a else artisan_id}**")
        else:
            artisan_id = st.selectbox(
                "Artisan *",
                [a.id for a in artisans],
                format_func=lambda x: next(
                    (
                        f"{a.nom} ({METIERS_LABELS.get(a.metier, a.metier)})"
                        for a in artisans
                        if a.id == x
                    ),
                    str(x),
                ),
            )

        date_intervention = st.date_input("Date *", value=date.today())
        description = st.text_area("Description *")
        piece = st.text_input("Pièce concernée")

        col1, col2 = st.columns(2)
        with col1:
            montant_devis = st.number_input("Montant devis (€)", min_value=0.0, step=10.0)
        with col2:
            montant_facture = st.number_input("Montant facture (€)", min_value=0.0, step=10.0)

        satisfaction = st.slider("Satisfaction", 1, 5, 3)
        commentaire = st.text_area("Commentaire")

        submitted = st.form_submit_button("💾 Enregistrer", use_container_width=True)

    if submitted and description:
        from decimal import Decimal

        data = {
            "artisan_id": artisan_id,
            "date_intervention": date_intervention,
            "description": description,
            "piece": piece or None,
            "montant_devis": Decimal(str(montant_devis)) if montant_devis > 0 else None,
            "montant_facture": Decimal(str(montant_facture)) if montant_facture > 0 else None,
            "satisfaction": satisfaction,
            "commentaire": commentaire or None,
        }
        create_intervention(data)
        st.success("✅ Intervention enregistrée !")
        rerun()


def _afficher_artisan_card(artisan) -> None:
    """Affiche une carte pour un artisan."""
    metier_label = METIERS_LABELS.get(getattr(artisan, "metier", ""), "")
    recommande = "👍" if getattr(artisan, "recommande", False) else ""

    with st.container(border=True):
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"**{artisan.nom}** {recommande}")
            ent = getattr(artisan, "entreprise", None)
            st.caption(f"{metier_label}" + (f" — {ent}" if ent else ""))
            tel = getattr(artisan, "telephone", None)
            if tel:
                st.caption(f"📞 {tel}")
        with col2:
            note = getattr(artisan, "note", None)
            if note:
                st.caption(NOTE_LABELS.get(note, f"{note}/5"))
        with col3:
            decennale = getattr(artisan, "assurance_decennale", False)
            if decennale:
                st.caption("🛡️ Décennale")

        col_edit, col_del, col_interv = st.columns(3)
        with col_edit:
            if st.button("✏️", key=_keys(f"edit_{artisan.id}")):
                st.session_state[_keys("edit_id")] = artisan.id
                rerun()
        with col_del:
            if st.button("🗑️", key=_keys(f"del_{artisan.id}")):
                delete_artisan(artisan.id)
                rerun()
        with col_interv:
            if st.button("🔧 Intervention", key=_keys(f"interv_{artisan.id}")):
                st.session_state[_keys("interv_artisan")] = artisan.id
                rerun()


@ui_fragment
def afficher_onglet_dashboard() -> None:
    """Onglet récap artisans."""
    stats = get_stats_artisans()
    if not stats:
        st.info("Aucun artisan enregistré.")
        return

    cols = st.columns(3)
    with cols[0]:
        st.metric("Total artisans", stats.get("total", 0))
    with cols[1]:
        st.metric("Recommandés", stats.get("recommandes", 0))
    with cols[2]:
        st.metric("Interventions", stats.get("interventions", 0))

    par_metier = stats.get("par_metier", {})
    if par_metier:
        st.markdown("**Par métier :**")
        for metier, count in sorted(par_metier.items(), key=lambda x: -x[1]):
            label = METIERS_LABELS.get(metier, metier)
            st.caption(f"{label}: {count}")


@ui_fragment
def afficher_onglet_artisans() -> None:
    """Onglet liste des artisans avec filtres."""
    filtre_metier = st.selectbox(
        "Métier",
        [""] + list(METIERS_LABELS.keys()),
        format_func=lambda x: METIERS_LABELS.get(x, "Tous") if x else "Tous",
        key=_keys("filtre_metier"),
    )

    artisans = get_all_artisans(filtre_metier=filtre_metier or None)
    if not artisans:
        st.info("Aucun artisan trouvé.")
        return

    st.caption(f"{len(artisans)} artisan(s)")
    for a in artisans:
        _afficher_artisan_card(a)


@ui_fragment
def afficher_onglet_interventions() -> None:
    """Onglet ajout d'intervention."""
    interv_artisan = st.session_state.get(_keys("interv_artisan"))
    afficher_formulaire_intervention(artisan_id=interv_artisan)

    # Historique récent
    artisans = get_all_artisans()
    for a in artisans:
        interventions = get_interventions_artisan(a.id)
        if interventions:
            with st.expander(f"{a.nom} — {len(interventions)} intervention(s)"):
                for i in interventions:
                    st.caption(
                        f"📅 {i.date_intervention:%d/%m/%Y} — {i.description[:80]}"
                        + (f" — {float(i.montant_facture):.0f}€" if i.montant_facture else "")
                    )
