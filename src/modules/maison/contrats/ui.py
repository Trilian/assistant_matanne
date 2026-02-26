"""Composants UI pour le module Contrats."""

from datetime import date

import streamlit as st

from src.core.state import rerun
from src.ui.fragments import ui_fragment
from src.ui.keys import KeyNamespace

from .constants import STATUTS_CONTRAT_LABELS, TYPES_CONTRAT_LABELS
from .crud import (
    create_contrat,
    delete_contrat,
    get_alertes_contrats,
    get_all_contrats,
    get_resume_financier,
    update_contrat,
)

_keys = KeyNamespace("contrats")


def afficher_formulaire_contrat(contrat=None) -> None:
    """Formulaire de création/édition d'un contrat."""
    with st.form(key=_keys("form_contrat")):
        nom = st.text_input("Nom du contrat *", value=getattr(contrat, "nom", ""))

        col1, col2 = st.columns(2)
        with col1:
            types_list = list(TYPES_CONTRAT_LABELS.keys())
            idx_type = 0
            if contrat and hasattr(contrat, "type_contrat") and contrat.type_contrat in types_list:
                idx_type = types_list.index(contrat.type_contrat)
            type_contrat = st.selectbox(
                "Type",
                types_list,
                format_func=lambda x: TYPES_CONTRAT_LABELS[x],
                index=idx_type,
            )
        with col2:
            fournisseur = st.text_input("Fournisseur *", value=getattr(contrat, "fournisseur", ""))

        col3, col4 = st.columns(2)
        with col3:
            numero_contrat = st.text_input(
                "N° contrat", value=getattr(contrat, "numero_contrat", "") or ""
            )
        with col4:
            numero_client = st.text_input(
                "N° client", value=getattr(contrat, "numero_client", "") or ""
            )

        st.markdown("**📅 Dates**")
        col5, col6, col7 = st.columns(3)
        with col5:
            date_debut = st.date_input(
                "Date début *",
                value=getattr(contrat, "date_debut", date.today()),
            )
        with col6:
            date_fin = st.date_input(
                "Date fin",
                value=getattr(contrat, "date_fin", None),
            )
        with col7:
            date_renouvellement = st.date_input(
                "Date renouvellement",
                value=getattr(contrat, "date_renouvellement", None),
            )

        st.markdown("**💰 Financier**")
        col8, col9 = st.columns(2)
        with col8:
            montant_mensuel = st.number_input(
                "Montant mensuel (€)",
                min_value=0.0,
                value=float(getattr(contrat, "montant_mensuel", 0) or 0),
                step=1.0,
            )
        with col9:
            montant_annuel = st.number_input(
                "Montant annuel (€)",
                min_value=0.0,
                value=float(getattr(contrat, "montant_annuel", 0) or 0),
                step=1.0,
            )

        col10, col11 = st.columns(2)
        with col10:
            tacite_reconduction = st.checkbox(
                "Tacite reconduction",
                value=getattr(contrat, "tacite_reconduction", True),
            )
        with col11:
            preavis_jours = st.number_input(
                "Préavis résiliation (jours)",
                min_value=0,
                value=int(getattr(contrat, "preavis_resiliation_jours", 0) or 0),
            )

        st.markdown("**📞 Contact**")
        col12, col13 = st.columns(2)
        with col12:
            telephone = st.text_input("Téléphone", value=getattr(contrat, "telephone", "") or "")
        with col13:
            email = st.text_input("Email", value=getattr(contrat, "email", "") or "")

        espace_client_url = st.text_input(
            "URL espace client", value=getattr(contrat, "espace_client_url", "") or ""
        )
        notes = st.text_area("Notes", value=getattr(contrat, "notes", "") or "")

        submitted = st.form_submit_button("💾 Enregistrer", use_container_width=True)

    if submitted and nom and fournisseur:
        from decimal import Decimal

        data = {
            "nom": nom,
            "type_contrat": type_contrat,
            "fournisseur": fournisseur,
            "numero_contrat": numero_contrat or None,
            "numero_client": numero_client or None,
            "date_debut": date_debut,
            "date_fin": date_fin if date_fin else None,
            "date_renouvellement": date_renouvellement if date_renouvellement else None,
            "montant_mensuel": Decimal(str(montant_mensuel)) if montant_mensuel > 0 else None,
            "montant_annuel": Decimal(str(montant_annuel)) if montant_annuel > 0 else None,
            "tacite_reconduction": tacite_reconduction,
            "preavis_resiliation_jours": preavis_jours if preavis_jours > 0 else None,
            "telephone": telephone or None,
            "email": email or None,
            "espace_client_url": espace_client_url or None,
            "notes": notes or None,
            "statut": "actif",
        }
        if contrat:
            update_contrat(contrat.id, data)
            st.success("✅ Contrat mis à jour !")
        else:
            create_contrat(data)
            st.success("✅ Contrat ajouté !")
        rerun()


def _afficher_contrat_card(contrat) -> None:
    """Affiche une carte pour un contrat."""
    type_label = TYPES_CONTRAT_LABELS.get(getattr(contrat, "type_contrat", ""), "")
    statut_label = STATUTS_CONTRAT_LABELS.get(getattr(contrat, "statut", ""), "")

    with st.container(border=True):
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"**{contrat.nom}**")
            st.caption(f"{type_label} — {contrat.fournisseur}")
            st.caption(statut_label)
        with col2:
            mensuel = getattr(contrat, "montant_mensuel", None)
            if mensuel:
                st.metric("€/mois", f"{float(mensuel):.0f}€")
        with col3:
            renouvellement = getattr(contrat, "date_renouvellement", None)
            if renouvellement:
                jours = (renouvellement - date.today()).days
                couleur = "🔴" if jours < 30 else "🟡" if jours < 60 else "🟢"
                st.caption(f"{couleur} {renouvellement:%d/%m/%Y}")

        col_edit, col_del = st.columns(2)
        with col_edit:
            if st.button("✏️ Modifier", key=_keys(f"edit_{contrat.id}")):
                st.session_state[_keys("edit_id")] = contrat.id
                rerun()
        with col_del:
            if st.button("🗑️ Supprimer", key=_keys(f"del_{contrat.id}")):
                delete_contrat(contrat.id)
                rerun()


@ui_fragment
def afficher_onglet_dashboard() -> None:
    """Onglet dashboard avec résumé financier."""
    resume = get_resume_financier()
    if not resume:
        st.info("Aucun contrat actif.")
        return

    cols = st.columns(3)
    with cols[0]:
        st.metric("Contrats actifs", resume.get("nb_contrats", 0))
    with cols[1]:
        st.metric("Total mensuel", f"{resume.get('total_mensuel', 0):.0f}€")
    with cols[2]:
        st.metric("Total annuel", f"{resume.get('total_annuel', 0):.0f}€")

    par_type = resume.get("par_type", {})
    if par_type:
        st.markdown("**Répartition par type :**")
        for type_key, data in par_type.items():
            label = TYPES_CONTRAT_LABELS.get(type_key, type_key)
            st.caption(f"{label}: {data['count']} contrat(s) — {data['total_mensuel']:.0f}€/mois")

    # Alertes rapides
    alertes = get_alertes_contrats(jours_horizon=60)
    if alertes:
        st.divider()
        st.markdown(f"**🔔 {len(alertes)} alerte(s) à venir**")
        for a in alertes[:5]:
            st.warning(
                f"**{a['nom']}** — {a['action']} dans **{a['jours_restants']}j** "
                f"({a['date_echeance']:%d/%m/%Y})"
            )


@ui_fragment
def afficher_onglet_contrats() -> None:
    """Onglet liste des contrats avec filtres."""
    col1, col2 = st.columns(2)
    with col1:
        filtre_type = st.selectbox(
            "Type",
            [""] + list(TYPES_CONTRAT_LABELS.keys()),
            format_func=lambda x: TYPES_CONTRAT_LABELS.get(x, "Tous") if x else "Tous",
            key=_keys("filtre_type"),
        )
    with col2:
        filtre_statut = st.selectbox(
            "Statut",
            [""] + list(STATUTS_CONTRAT_LABELS.keys()),
            format_func=lambda x: STATUTS_CONTRAT_LABELS.get(x, "Tous") if x else "Tous",
            key=_keys("filtre_statut"),
        )

    contrats = get_all_contrats(
        filtre_type=filtre_type or None,
        filtre_statut=filtre_statut or None,
    )

    if not contrats:
        st.info("Aucun contrat trouvé.")
        return

    st.caption(f"{len(contrats)} contrat(s)")
    for c in contrats:
        _afficher_contrat_card(c)


@ui_fragment
def afficher_onglet_alertes() -> None:
    """Onglet alertes de renouvellement."""
    jours = st.slider("Horizon (jours)", 30, 365, 90, key=_keys("horizon_alertes"))
    alertes = get_alertes_contrats(jours_horizon=jours)

    if not alertes:
        st.success("✅ Aucune alerte dans les prochains jours.")
        return

    for a in alertes:
        urgence = "🔴" if a["jours_restants"] < 15 else "🟡" if a["jours_restants"] < 30 else "🟢"
        with st.container(border=True):
            st.markdown(
                f"{urgence} **{a['nom']}** — "
                f"À {a['action']} dans **{a['jours_restants']} jours** "
                f"({a['date_echeance']:%d/%m/%Y})"
            )
