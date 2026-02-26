"""Composants UI pour le module Entretien Saisonnier."""

from __future__ import annotations

from datetime import date

import streamlit as st

from src.core.state import rerun
from src.modules._framework import ui_fragment
from src.ui.keys import KeyNamespace

from .constants import CATEGORIES_ENTRETIEN, SAISONS_LABELS
from .crud import get_alertes_saisonnieres, get_all_entretiens, marquer_fait

_keys = KeyNamespace("entretien_saison_ui")


def _saison_courante() -> str:
    """Détecte la saison actuelle."""
    mois = date.today().month
    if mois in (3, 4, 5):
        return "printemps"
    elif mois in (6, 7, 8):
        return "ete"
    elif mois in (9, 10, 11):
        return "automne"
    else:
        return "hiver"


# ---------------------------------------------------------------------------
# Onglet alertes (à faire maintenant)
# ---------------------------------------------------------------------------
@ui_fragment
def afficher_onglet_alertes():
    """Affiche les entretiens à faire pour la saison en cours."""
    saison = _saison_courante()
    st.subheader(f"{SAISONS_LABELS.get(saison, saison)} — Entretiens recommandés")

    alertes = get_alertes_saisonnieres()

    if not alertes:
        st.success("✅ Tous les entretiens saisonniers sont à jour !")
        return

    # Séparer : jamais fait vs anciennement fait
    jamais_fait = [e for e in alertes if not e.derniere_realisation]
    a_refaire = [e for e in alertes if e.derniere_realisation]

    if jamais_fait:
        st.markdown("### 🔴 Jamais réalisé")
        for e in jamais_fait:
            cat_label = CATEGORIES_ENTRETIEN.get(e.categorie, e.categorie) if e.categorie else ""
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{e.tache}** {cat_label}")
                if e.description:
                    st.caption(e.description)
            with col2:
                if st.button("✅ Fait", key=_keys(f"alerte_fait_{e.id}")):
                    marquer_fait(e.id)
                    st.toast(f"'{e.tache}' marqué comme fait !")
                    rerun()

    if a_refaire:
        st.markdown("### 🟡 À refaire")
        for e in a_refaire:
            cat_label = CATEGORIES_ENTRETIEN.get(e.categorie, e.categorie) if e.categorie else ""
            jours_depuis = (
                (date.today() - e.derniere_realisation).days if e.derniere_realisation else "?"
            )
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{e.tache}** {cat_label}")
                st.caption(f"Dernière fois : {e.derniere_realisation} ({jours_depuis} jours)")
            with col2:
                if st.button("✅ Fait", key=_keys(f"refaire_fait_{e.id}")):
                    marquer_fait(e.id)
                    st.toast(f"'{e.tache}' marqué comme fait !")
                    rerun()


# ---------------------------------------------------------------------------
# Onglet calendrier complet
# ---------------------------------------------------------------------------
@ui_fragment
def afficher_onglet_calendrier():
    """Affiche le calendrier complet des entretiens par saison."""
    # Filtre optionnel par saison
    filtre_saison = st.selectbox(
        "Saison",
        ["Toutes"] + list(SAISONS_LABELS.keys()),
        format_func=lambda k: SAISONS_LABELS.get(k, "📊 Toutes"),
        key=_keys("cal_saison"),
    )

    saison_filtre = filtre_saison if filtre_saison != "Toutes" else None
    entretiens = get_all_entretiens(saison=saison_filtre)

    if not entretiens:
        st.info("Aucun entretien saisonnier enregistré.")
        return

    # Regrouper par saison
    par_saison: dict[str, list] = {}
    for e in entretiens:
        key = e.saison or "autre"
        par_saison.setdefault(key, []).append(e)

    for saison_key in ["printemps", "ete", "automne", "hiver", "toute_annee"]:
        items = par_saison.get(saison_key, [])
        if not items:
            continue

        saison_label = SAISONS_LABELS.get(saison_key, saison_key)
        is_current = saison_key == _saison_courante() or saison_key == "toute_annee"
        badge = " ← Saison actuelle" if saison_key == _saison_courante() else ""

        st.subheader(f"{saison_label}{badge}")

        for e in items:
            cat_label = CATEGORIES_ENTRETIEN.get(e.categorie, "") if e.categorie else ""
            statut_icon = "✅" if e.derniere_realisation else "⬜"
            derniere = f" (dernier : {e.derniere_realisation})" if e.derniere_realisation else ""

            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"{statut_icon} **{e.tache}** {cat_label}{derniere}")
                if e.description:
                    st.caption(e.description)
            with col2:
                if is_current and st.button("✅ Fait", key=_keys(f"cal_fait_{e.id}")):
                    marquer_fait(e.id)
                    st.toast(f"'{e.tache}' marqué comme fait !")
                    rerun()
