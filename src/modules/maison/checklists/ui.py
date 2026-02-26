"""Composants UI pour le module Checklists."""

from datetime import date

import streamlit as st

from src.core.state import rerun
from src.ui.fragments import ui_fragment
from src.ui.keys import KeyNamespace

from .constants import CATEGORIES_ITEMS_LABELS, QUAND_LABELS, TYPES_VOYAGE_LABELS
from .crud import (
    add_item,
    create_checklist,
    create_from_template,
    delete_checklist,
    get_all_checklists,
    toggle_item,
)

_keys = KeyNamespace("checklists")


def afficher_checklist_detail(checklist) -> None:
    """Affiche le détail d'une checklist avec items cochables."""
    items = getattr(checklist, "items", [])
    total = len(items)
    faits = sum(1 for i in items if i.fait)
    pct = int(faits / total * 100) if total > 0 else 0

    st.subheader(f"📋 {checklist.nom}")
    st.progress(pct / 100, text=f"{faits}/{total} — {pct}%")

    # Grouper par catégorie
    par_cat: dict = {}
    for item in sorted(items, key=lambda x: x.ordre):
        cat = item.categorie
        par_cat.setdefault(cat, []).append(item)

    for cat, cat_items in par_cat.items():
        label = CATEGORIES_ITEMS_LABELS.get(cat, cat)
        cat_faits = sum(1 for i in cat_items if i.fait)
        with st.expander(f"{label} ({cat_faits}/{len(cat_items)})", expanded=True):
            for item in cat_items:
                col1, col2 = st.columns([4, 1])
                with col1:
                    checked = st.checkbox(
                        item.libelle,
                        value=item.fait,
                        key=_keys(f"item_{item.id}"),
                    )
                    if checked != item.fait:
                        toggle_item(item.id)
                        rerun()
                with col2:
                    quand = getattr(item, "quand", None)
                    if quand:
                        st.caption(QUAND_LABELS.get(quand, quand))

    # Ajouter un item
    st.divider()
    with st.form(key=_keys("add_item")):
        st.markdown("**Ajouter un item**")
        col1, col2 = st.columns(2)
        with col1:
            libelle = st.text_input("Libellé")
        with col2:
            categorie = st.selectbox(
                "Catégorie",
                list(CATEGORIES_ITEMS_LABELS.keys()),
                format_func=lambda x: CATEGORIES_ITEMS_LABELS[x],
            )
        submitted = st.form_submit_button("➕ Ajouter")
    if submitted and libelle:
        add_item(
            {
                "checklist_id": checklist.id,
                "libelle": libelle,
                "categorie": categorie,
                "ordre": total + 1,
            }
        )
        rerun()


def afficher_formulaire_checklist() -> None:
    """Formulaire de création d'une checklist vide."""
    with st.form(key=_keys("form_new")):
        nom = st.text_input("Nom *")
        type_voyage = st.selectbox(
            "Type de voyage",
            list(TYPES_VOYAGE_LABELS.keys()),
            format_func=lambda x: TYPES_VOYAGE_LABELS[x],
        )
        col1, col2 = st.columns(2)
        with col1:
            date_depart = st.date_input("Date départ", value=date.today())
        with col2:
            duree = st.number_input("Durée (jours)", min_value=1, value=7)
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("💾 Créer", use_container_width=True)

    if submitted and nom:
        from datetime import timedelta

        data = {
            "nom": nom,
            "type_voyage": type_voyage,
            "date_depart": date_depart,
            "date_retour": date_depart + timedelta(days=duree),
            "duree_jours": duree,
            "notes": notes or None,
        }
        create_checklist(data)
        st.success("✅ Checklist créée !")
        rerun()


@ui_fragment
def afficher_onglet_checklists() -> None:
    """Liste des checklists existantes."""
    checklists = get_all_checklists()
    if not checklists:
        st.info("Aucune checklist. Créez-en une ou utilisez un template.")
        return

    for cl in checklists:
        items = getattr(cl, "items", [])
        total = len(items)
        faits = sum(1 for i in items if i.fait)
        pct = int(faits / total * 100) if total > 0 else 0
        type_label = TYPES_VOYAGE_LABELS.get(cl.type_voyage, cl.type_voyage)

        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{cl.nom}** — {type_label}")
                st.progress(pct / 100, text=f"{faits}/{total}")
            with col2:
                depart = getattr(cl, "date_depart", None)
                if depart:
                    st.caption(f"📅 {depart:%d/%m/%Y}")
            with col3:
                if st.button("Ouvrir", key=_keys(f"open_{cl.id}")):
                    st.session_state[_keys("detail_id")] = cl.id
                    rerun()
                if st.button("🗑️", key=_keys(f"del_{cl.id}")):
                    delete_checklist(cl.id)
                    rerun()


@ui_fragment
def afficher_onglet_templates() -> None:
    """Créer une checklist depuis un template prédéfini."""
    from src.services.maison.checklists_crud_service import TEMPLATES_CHECKLIST

    st.markdown("Choisissez un template pour démarrer rapidement :")
    for key, template in TEMPLATES_CHECKLIST.items():
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{template['nom']}**")
                nb_items = sum(len(items) for items in template["items"].values())
                st.caption(f"{nb_items} items prédéfinis")
            with col2:
                if st.button("Utiliser", key=_keys(f"tpl_{key}")):
                    create_from_template(key)
                    st.success(f"✅ Checklist '{template['nom']}' créée !")
                    rerun()
