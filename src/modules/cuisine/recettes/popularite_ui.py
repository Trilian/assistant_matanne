"""
Page Popularité des Recettes — Analytics et classement.

Affiche un classement des recettes par score de popularité,
tendances, et statistiques d'utilisation.
"""

import logging

import streamlit as st

from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("popularite")


def afficher_popularite() -> None:
    """Affiche le classement de popularité des recettes."""
    st.subheader("🏆 Popularité des Recettes")
    st.caption("Découvrez vos recettes les plus cuisinées et les tendances")

    with error_boundary(titre="Erreur popularité"):
        _afficher_contenu()


def _afficher_contenu() -> None:
    """Contenu principal de la page popularité."""
    from src.services.cuisine.suggestions.popularite import (
        calculer_popularite,
        generer_resume_popularite,
    )

    # Sélection de la période
    periode = st.selectbox(
        "Période d'analyse",
        options=[30, 60, 90, 180, 365],
        format_func=lambda x: f"{x} derniers jours",
        index=2,
        key=_keys("periode"),
    )

    with st.spinner("Calcul du classement..."):
        classement = calculer_popularite(periode_jours=periode)

    if not classement.recettes:
        st.info("Pas assez de données pour établir un classement. Cuisinez davantage ! 🍳")
        return

    # Résumé textuel
    resume = generer_resume_popularite(classement)
    st.markdown(resume)

    st.divider()

    # Podium top 3
    if classement.top_3:
        st.markdown("### 🏅 Podium")
        cols = st.columns(min(3, len(classement.top_3)))
        medals = ["🥇", "🥈", "🥉"]

        for i, (col, recette) in enumerate(zip(cols, classement.top_3, strict=False)):
            with col:
                st.markdown(f"### {medals[i]}")
                st.markdown(f"**{recette.nom_recette}**")
                st.metric("Score", f"{recette.score_total}/100")
                st.caption(
                    f"Préparé {recette.nb_preparations}× (dont {recette.nb_preparations_30j} ce mois)"
                )

    st.divider()

    # Classement complet
    st.markdown("### 📊 Classement complet")

    import pandas as pd

    df = pd.DataFrame(
        [
            {
                "Rang": i + 1,
                "Recette": r.nom_recette,
                "Score": r.score_total,
                "Préparations": r.nb_preparations,
                "Ce mois": r.nb_preparations_30j,
                "Tendance": {
                    "hausse": "📈",
                    "baisse": "📉",
                    "stable": "➡️",
                    "nouveau": "🆕",
                }.get(r.tendance, ""),
            }
            for i, r in enumerate(classement.recettes[:20])
        ]
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Score": st.column_config.ProgressColumn(
                min_value=0,
                max_value=100,
                format="%.1f",
            ),
        },
    )

    # Recettes jamais préparées
    if classement.nouvelles:
        with st.expander(f"🆕 Pas encore testées ({len(classement.nouvelles)})"):
            for r in classement.nouvelles:
                st.markdown(f"• {r.nom_recette}")


__all__ = ["afficher_popularite"]
