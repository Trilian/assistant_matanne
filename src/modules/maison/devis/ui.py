"""Composants UI pour le module Devis Comparatifs."""

from __future__ import annotations

from datetime import date

import streamlit as st

from src.core.state import rerun
from src.modules._framework import ui_fragment
from src.ui.keys import KeyNamespace

from .constants import STATUTS_DEVIS_LABELS
from .crud import choisir_devis, create_devis, delete_devis, get_all_devis, update_devis

_keys = KeyNamespace("devis_ui")


# ---------------------------------------------------------------------------
# Onglet liste des devis
# ---------------------------------------------------------------------------
@ui_fragment
def afficher_onglet_devis():
    """Affiche la liste de tous les devis avec filtres."""
    devis_list = get_all_devis()

    if not devis_list:
        st.info("Aucun devis enregistré. Ajoutez-en un via l'onglet ➕.")
        return

    # Filtres
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        filtre_statut = st.selectbox(
            "Statut",
            ["Tous"] + list(STATUTS_DEVIS_LABELS.values()),
            key=_keys("filtre_statut"),
        )
    with col_f2:
        filtre_objet = st.text_input("🔍 Rechercher (objet)", key=_keys("filtre_objet"))

    # Application des filtres
    filtered = devis_list
    if filtre_statut != "Tous":
        statut_key = next((k for k, v in STATUTS_DEVIS_LABELS.items() if v == filtre_statut), None)
        if statut_key:
            filtered = [d for d in filtered if d.statut == statut_key]
    if filtre_objet:
        filtre_lower = filtre_objet.lower()
        filtered = [d for d in filtered if filtre_lower in (d.objet or "").lower()]

    st.markdown(f"**{len(filtered)} devis trouvé(s)**")

    for devis in filtered:
        statut_label = STATUTS_DEVIS_LABELS.get(devis.statut, devis.statut)
        montant_str = f"{devis.montant_ttc:,.2f} €" if devis.montant_ttc else "N/C"

        with st.expander(f"{statut_label} | {devis.objet or 'Sans objet'} — {montant_str}"):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Montant TTC", montant_str)
            with c2:
                st.write(f"**Artisan** : {devis.artisan.nom if devis.artisan else 'N/C'}")
                st.write(f"**Date** : {devis.date_devis or 'N/C'}")
            with c3:
                validite = devis.date_validite
                if (
                    validite
                    and validite < date.today()
                    and devis.statut not in ("accepte", "refuse")
                ):
                    st.warning("⚠️ Devis expiré")
                st.write(f"**Validité** : {validite or 'N/C'}")

            if devis.notes:
                st.caption(devis.notes)

            # Lignes du devis
            if devis.lignes:
                st.markdown("**Détail des lignes :**")
                for ligne in devis.lignes:
                    total_ligne = (ligne.quantite or 1) * (ligne.prix_unitaire or 0)
                    st.write(
                        f"- {ligne.designation} : {ligne.quantite or 1} × "
                        f"{ligne.prix_unitaire or 0:.2f} € = **{total_ligne:.2f} €**"
                    )

            # Actions
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if devis.statut not in ("accepte",) and st.button(
                    "✅ Choisir ce devis", key=_keys(f"choisir_{devis.id}")
                ):
                    choisir_devis(devis.id)
                    st.toast("Devis accepté !")
                    rerun()
            with col_b:
                if st.button("✏️ Modifier", key=_keys(f"edit_{devis.id}")):
                    st.session_state[_keys("edit_id")] = devis.id
                    rerun()
            with col_c:
                if st.button("🗑️ Supprimer", key=_keys(f"del_{devis.id}")):
                    delete_devis(devis.id)
                    st.toast("Devis supprimé.")
                    rerun()


# ---------------------------------------------------------------------------
# Onglet comparaison
# ---------------------------------------------------------------------------
@ui_fragment
def afficher_onglet_comparaison():
    """Compare côte à côte les devis d'un même projet."""
    devis_list = get_all_devis()
    if len(devis_list) < 2:
        st.info("Il faut au moins 2 devis pour comparer.")
        return

    # Regrouper par projet
    projets: dict[str, list] = {}
    for d in devis_list:
        key = d.objet or "Sans objet"
        projets.setdefault(key, []).append(d)

    projet_choisi = st.selectbox(
        "Projet / Objet",
        list(projets.keys()),
        key=_keys("compare_projet"),
    )

    candidats = projets.get(projet_choisi, [])
    if len(candidats) < 2:
        st.info("Un seul devis pour ce projet — pas de comparaison possible.")
        return

    # Tri par montant
    candidats_tries = sorted(candidats, key=lambda d: d.montant_ttc or float("inf"))
    cols = st.columns(len(candidats_tries))

    for i, (col, devis) in enumerate(zip(cols, candidats_tries, strict=False)):
        with col:
            badge = "🥇" if i == 0 else ("🥈" if i == 1 else "")
            statut_label = STATUTS_DEVIS_LABELS.get(devis.statut, devis.statut)
            st.markdown(f"### {badge} {devis.artisan.nom if devis.artisan else 'Artisan ?'}")
            st.metric("Montant TTC", f"{devis.montant_ttc:,.2f} €" if devis.montant_ttc else "N/C")
            st.write(f"**Statut** : {statut_label}")
            st.write(f"**Date** : {devis.date_devis or 'N/C'}")
            st.write(f"**Validité** : {devis.date_validite or 'N/C'}")
            if devis.notes:
                st.caption(devis.notes)

            if devis.statut != "accepte":
                if st.button("✅ Choisir", key=_keys(f"cmp_choisir_{devis.id}")):
                    choisir_devis(devis.id)
                    st.toast("Devis accepté !")
                    rerun()

    # Écart
    if len(candidats_tries) >= 2:
        prix_min = candidats_tries[0].montant_ttc or 0
        prix_max = candidats_tries[-1].montant_ttc or 0
        ecart = prix_max - prix_min
        if prix_min > 0:
            pct = ecart / prix_min * 100
            st.info(f"💡 Écart : {ecart:,.2f} € ({pct:.0f}%) entre le moins cher et le plus cher.")


# ---------------------------------------------------------------------------
# Formulaire ajout / édition
# ---------------------------------------------------------------------------
@ui_fragment
def afficher_formulaire_devis(devis=None):
    """Formulaire de création ou modification d'un devis."""
    is_edit = devis is not None
    prefix = "edit" if is_edit else "new"

    with st.form(_keys(f"form_{prefix}"), clear_on_submit=not is_edit):
        st.subheader("📝 Nouveau devis" if not is_edit else "✏️ Modifier le devis")

        col1, col2 = st.columns(2)
        with col1:
            objet = st.text_input(
                "Objet / Projet *",
                value=devis.objet if is_edit else "",
                key=_keys(f"{prefix}_objet"),
            )
            montant_ttc = st.number_input(
                "Montant TTC (€)",
                min_value=0.0,
                step=50.0,
                value=float(devis.montant_ttc) if is_edit and devis.montant_ttc else 0.0,
                key=_keys(f"{prefix}_montant"),
            )
        with col2:
            statuts_keys = list(STATUTS_DEVIS_LABELS.keys())
            statut_idx = (
                statuts_keys.index(devis.statut) if is_edit and devis.statut in statuts_keys else 0
            )
            statut = st.selectbox(
                "Statut",
                statuts_keys,
                format_func=lambda k: STATUTS_DEVIS_LABELS[k],
                index=statut_idx,
                key=_keys(f"{prefix}_statut"),
            )
            date_devis = st.date_input(
                "Date du devis",
                value=devis.date_devis if is_edit and devis.date_devis else date.today(),
                key=_keys(f"{prefix}_date"),
            )
            date_validite = st.date_input(
                "Date de validité",
                value=devis.date_validite if is_edit and devis.date_validite else None,
                key=_keys(f"{prefix}_validite"),
            )

        notes = st.text_area(
            "Notes",
            value=devis.notes if is_edit else "",
            key=_keys(f"{prefix}_notes"),
        )

        submitted = st.form_submit_button("💾 Enregistrer" if is_edit else "➕ Ajouter")

        if submitted:
            if not objet:
                st.error("L'objet est obligatoire.")
                return

            data = {
                "objet": objet,
                "montant_ttc": montant_ttc or None,
                "statut": statut,
                "date_devis": date_devis,
                "date_validite": date_validite if date_validite else None,
                "notes": notes or None,
            }

            if is_edit:
                update_devis(devis.id, data)
                st.success("Devis mis à jour !")
                if _keys("edit_id") in st.session_state:
                    del st.session_state[_keys("edit_id")]
            else:
                create_devis(data)
                st.success("Devis ajouté !")
            rerun()
