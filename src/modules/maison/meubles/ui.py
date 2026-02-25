"""
Composants UI pour le module Meubles.
"""

from decimal import Decimal

import streamlit as st

from src.ui.keys import KeyNamespace

from .constants import PIECES_LABELS, PRIORITES_LABELS, STATUTS_LABELS
from .crud import (
    create_meuble,
    delete_meuble,
    get_all_meubles,
    get_budget_resume,
    update_meuble,
)

_keys = KeyNamespace("meubles")


def afficher_formulaire(meuble=None) -> None:
    """Affiche le formulaire de création/édition d'un meuble."""
    with st.form(key=_keys("form_meuble")):
        nom = st.text_input("Nom *", value=getattr(meuble, "nom", ""))

        col1, col2 = st.columns(2)
        with col1:
            pieces_list = list(PIECES_LABELS.keys())
            idx_piece = 0
            if meuble and hasattr(meuble, "piece") and meuble.piece in pieces_list:
                idx_piece = pieces_list.index(meuble.piece)
            piece = st.selectbox(
                "Pièce",
                pieces_list,
                format_func=lambda x: PIECES_LABELS[x],
                index=idx_piece,
            )
        with col2:
            priorites_list = list(PRIORITES_LABELS.keys())
            idx_prio = priorites_list.index("normale")
            if meuble and hasattr(meuble, "priorite") and meuble.priorite in priorites_list:
                idx_prio = priorites_list.index(meuble.priorite)
            priorite = st.selectbox(
                "Priorité",
                priorites_list,
                format_func=lambda x: PRIORITES_LABELS[x],
                index=idx_prio,
            )

        description = st.text_area("Description", value=getattr(meuble, "description", "") or "")
        prix_estime = st.number_input(
            "Prix estimé (€)",
            min_value=0.0,
            value=float(getattr(meuble, "prix_estime", 0) or 0),
        )
        prix_max = st.number_input(
            "Prix max (€)",
            min_value=0.0,
            value=float(getattr(meuble, "prix_max", 0) or 0),
        )
        magasin = st.text_input("Magasin", value=getattr(meuble, "magasin", "") or "")
        url = st.text_input("URL", value=getattr(meuble, "url", "") or "")
        dimensions = st.text_input("Dimensions", value=getattr(meuble, "dimensions", "") or "")

        submitted = st.form_submit_button("💾 Enregistrer", use_container_width=True)

    if submitted and nom:
        data = {
            "nom": nom,
            "piece": piece,
            "priorite": priorite,
            "description": description or None,
            "prix_estime": Decimal(str(prix_estime)) if prix_estime > 0 else None,
            "prix_max": Decimal(str(prix_max)) if prix_max > 0 else None,
            "magasin": magasin or None,
            "url": url or None,
            "dimensions": dimensions or None,
            "statut": "souhaite",
        }
        if meuble:
            update_meuble(meuble.id, data)
            st.success("✅ Meuble mis à jour !")
        else:
            create_meuble(data)
            st.success("✅ Meuble ajouté !")
        st.rerun()


def afficher_meuble_card(meuble) -> None:
    """Affiche une carte pour un meuble."""
    piece_label = PIECES_LABELS.get(getattr(meuble, "piece", ""), "")
    statut_label = STATUTS_LABELS.get(getattr(meuble, "statut", ""), "")
    priorite_label = PRIORITES_LABELS.get(getattr(meuble, "priorite", ""), "")

    with st.container(border=True):
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"**{meuble.nom}**")
            desc = getattr(meuble, "description", None)
            if desc:
                if len(desc) > 100:
                    desc = desc[:100] + "…"
                st.caption(desc)
            st.caption(f"{piece_label} | {statut_label} | {priorite_label}")
        with col2:
            prix = getattr(meuble, "prix_estime", None)
            if prix:
                st.metric("Prix estimé", f"{float(prix):.0f}€")
        with col3:
            magasin = getattr(meuble, "magasin", None)
            if magasin:
                st.caption(f"🏪 {magasin}")

        col_edit, col_del = st.columns(2)
        with col_edit:
            if st.button("✏️ Modifier", key=f"edit_m_{meuble.id}"):
                st.session_state[_keys("edit_id")] = meuble.id
                st.rerun()
        with col_del:
            if st.button("🗑️ Supprimer", key=f"del_m_{meuble.id}"):
                delete_meuble(meuble.id)
                st.rerun()


def afficher_budget_summary() -> None:
    """Affiche le résumé budget."""
    st.subheader("💰 Résumé budget")
    resume = get_budget_resume()

    cols = st.columns(3)
    with cols[0]:
        st.metric("Articles", resume["nb_articles"])
    with cols[1]:
        st.metric("Total estimé", f"{resume['total_estime']:.0f}€")
    with cols[2]:
        st.metric("Budget max", f"{resume['total_max']:.0f}€")

    if resume["par_piece"]:
        st.markdown("**Par pièce:**")
        for piece, data in resume["par_piece"].items():
            label = PIECES_LABELS.get(piece, piece)
            st.caption(f"{label}: {data['count']} articles — ~{data['total_estime']:.0f}€")


def afficher_vue_par_piece() -> None:
    """Affiche la vue groupée par pièce."""
    meubles = get_all_meubles()
    if not meubles:
        st.info("Aucun meuble enregistré.")
        return

    # Grouper par pièce
    par_piece: dict = {}
    for m in meubles:
        piece = getattr(m, "piece", "autre")
        par_piece.setdefault(piece, []).append(m)

    for piece, items in sorted(par_piece.items()):
        label = PIECES_LABELS.get(piece, piece)
        with st.expander(f"{label} ({len(items)})"):
            for item in items:
                afficher_meuble_card(item)


def afficher_onglet_wishlist() -> None:
    """Affiche l'onglet wishlist avec filtres."""
    col1, col2 = st.columns(2)
    with col1:
        filtre_statut = st.selectbox(
            "Statut",
            [""] + list(STATUTS_LABELS.keys()),
            format_func=lambda x: STATUTS_LABELS.get(x, "Tous") if x else "Tous",
        )
    with col2:
        filtre_piece = st.selectbox(
            "Pièce",
            [""] + list(PIECES_LABELS.keys()),
            format_func=lambda x: PIECES_LABELS.get(x, "Toutes") if x else "Toutes",
        )

    meubles = get_all_meubles(
        filtre_statut=filtre_statut or None,
        filtre_piece=filtre_piece or None,
    )

    if not meubles:
        st.info("Aucun meuble trouvé avec ces critères.")
        return

    st.caption(f"{len(meubles)} meuble(s) trouvé(s)")
    for m in meubles:
        afficher_meuble_card(m)


def afficher_onglet_ajouter() -> None:
    """Affiche l'onglet ajout."""
    st.subheader("➕ Ajouter un meuble")
    afficher_formulaire(None)


def afficher_onglet_budget() -> None:
    """Affiche l'onglet budget."""
    afficher_budget_summary()
    st.divider()
    afficher_vue_par_piece()
