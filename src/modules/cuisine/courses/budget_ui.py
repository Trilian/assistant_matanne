"""
Widget Budget Courses — Suivi hebdomadaire du budget alimentation.

Affiche un résumé compact du budget course de la semaine,
la tendance sur 4 semaines, et un formulaire de saisie rapide.
"""

import logging

import streamlit as st

from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("budget_courses")


def afficher_budget_courses() -> None:
    """Affiche l'onglet budget courses complet."""

    st.subheader("💰 Budget Courses")
    st.caption("Suivi hebdomadaire de vos dépenses alimentation")

    with error_boundary(titre="Erreur chargement budget"):
        _afficher_resume_budget()

    st.divider()

    with error_boundary(titre="Erreur tendance"):
        _afficher_tendance()

    st.divider()

    with error_boundary(titre="Erreur saisie dépense"):
        _afficher_saisie_rapide()


def _afficher_resume_budget() -> None:
    """Affiche le résumé du budget de la semaine en cours."""
    from src.services.cuisine.budget import obtenir_budget_hebdo

    budget = obtenir_budget_hebdo()

    # Métriques
    col1, col2, col3 = st.columns(3)

    statut_emoji = {
        "ok": "🟢",
        "attention": "🟡",
        "depasse": "🔴",
    }.get(budget.statut, "⚪")

    with col1:
        st.metric(
            "Dépensé cette semaine",
            f"{budget.depenses_reelles:.0f} €",
            delta=None,
        )
    with col2:
        st.metric(
            "Budget restant",
            f"{budget.reste:.0f} €",
        )
    with col3:
        st.metric(
            "Statut",
            f"{statut_emoji} {budget.statut.capitalize()}",
        )

    # Barre de progression
    ratio = min(float(budget.depenses_reelles) / max(float(budget.budget_prevu), 1), 1.0)
    st.progress(ratio, text=f"{budget.depenses_reelles:.0f} / {budget.budget_prevu:.0f} €")


def _afficher_tendance() -> None:
    """Affiche la tendance sur les 4 dernières semaines."""
    from src.services.cuisine.budget import obtenir_tendance

    tendance = obtenir_tendance(nb_semaines=4)

    if not tendance.semaines:
        st.info("Pas assez de données pour afficher la tendance.")
        return

    import pandas as pd

    historique = [float(s.depenses_reelles) for s in reversed(tendance.semaines)]
    df = pd.DataFrame(
        {
            "Semaine": [f"S{i + 1}" for i in range(len(historique))],
            "Dépenses (€)": historique,
        }
    )

    tendance_emoji = {
        "hausse": "📈",
        "baisse": "📉",
        "stable": "➡️",
    }.get(tendance.tendance, "")

    st.markdown(f"**Tendance {tendance_emoji}** — Moyenne: {tendance.moyenne_hebdo:.0f} €/sem")

    st.bar_chart(df.set_index("Semaine"))


def _afficher_saisie_rapide() -> None:
    """Formulaire de saisie rapide d'une dépense course."""
    from src.services.cuisine.budget import enregistrer_depense_course

    st.markdown("#### ➕ Ajouter une dépense")

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        magasin = st.text_input(
            "Magasin",
            placeholder="La Fourche, Carrefour...",
            key=_keys("magasin"),
        )
    with col2:
        montant = st.number_input(
            "Montant (€)",
            min_value=0.0,
            step=1.0,
            format="%.2f",
            key=_keys("montant"),
        )
    with col3:
        if st.button(
            "💳 Enregistrer",
            key=_keys("enregistrer"),
            type="primary",
            disabled=montant <= 0,
        ):
            try:
                enregistrer_depense_course(
                    montant=montant,
                    magasin=magasin if magasin else None,
                )
                st.success(f"✅ Dépense de {montant:.2f} € enregistrée !")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erreur: {e}")


__all__ = ["afficher_budget_courses"]
