"""
Page Restes Créatifs — Interface IA pour cuisiner les restes.

Permet à l'utilisateur de saisir ce qu'il a en restes
et reçoit des suggestions de recettes créatives via Mistral.
"""

import logging

import streamlit as st

from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("restes_creatifs")


def afficher_restes_creatifs() -> None:
    """Affiche l'interface complète des restes créatifs."""
    st.subheader("♻️ Cuisine tes restes !")
    st.caption("Indique ce que tu as en reste, et l'IA te propose des idées créatives.")

    # Saisie des restes
    col1, col2 = st.columns([3, 1])
    with col1:
        restes_texte = st.text_area(
            "Qu'est-ce que tu as en restes ?",
            placeholder="Ex: 200g de poulet cuit, du riz, des courgettes, de la crème...",
            key=_keys("restes_input"),
            height=100,
        )
    with col2:
        nb_convives = st.number_input(
            "Convives",
            min_value=1,
            max_value=10,
            value=2,
            key=_keys("nb_convives"),
        )
        difficulte = st.selectbox(
            "Difficulté",
            ["Facile", "Moyen", "Avancé"],
            key=_keys("difficulte"),
        )

    # Bouton de génération
    if st.button(
        "✨ Suggère des recettes !",
        key=_keys("generer"),
        type="primary",
        disabled=not restes_texte,
    ):
        with error_boundary(titre="Erreur suggestion restes"):
            _generer_suggestions(restes_texte, nb_convives, difficulte)


def _generer_suggestions(
    restes_texte: str,
    nb_convives: int,
    difficulte: str,
) -> None:
    """Génère et affiche les suggestions de recettes à partir des restes."""
    from src.services.cuisine.suggestions.restes import (
        ResteDisponible,
        suggerer_recettes_restes,
    )

    # Parser les restes (simple split)
    restes_bruts = [r.strip() for r in restes_texte.replace("\n", ",").split(",") if r.strip()]
    restes = [ResteDisponible(nom=r, quantite_estimee="non précisée") for r in restes_bruts]

    with st.spinner("🧠 L'IA réfléchit à des combinaisons créatives..."):
        suggestions = suggerer_recettes_restes(
            restes=restes,
            nb_convives=nb_convives,
        )

    if not suggestions:
        st.info("Pas de suggestion trouvée. Essaye avec d'autres ingrédients !")
        return

    st.success(f"💡 {len(suggestions)} idée(s) trouvée(s) !")

    for i, s in enumerate(suggestions):
        with st.expander(f"🍽️ {s.nom_recette}", expanded=(i == 0)):
            col_info, col_temps = st.columns([3, 1])
            with col_info:
                st.markdown(f"**{s.nom_recette}**")
                if hasattr(s, "description") and s.description:
                    st.write(s.description)
            with col_temps:
                if hasattr(s, "temps_estime") and s.temps_estime:
                    st.metric("Temps", f"{s.temps_estime} min")

            # Ingrédients utilisés
            if hasattr(s, "ingredients_utilises") and s.ingredients_utilises:
                st.markdown("**Ingrédients des restes utilisés:**")
                for ing in s.ingredients_utilises:
                    st.markdown(f"  ✅ {ing}")

            # Étapes
            if hasattr(s, "etapes") and s.etapes:
                st.markdown("**Étapes:**")
                for j, etape in enumerate(s.etapes, 1):
                    st.markdown(f"{j}. {etape}")

            # Bouton TTS
            try:
                from src.ui.components.tts import (
                    lecteur_vocal_recette,
                    preparer_texte_recette,
                )

                etapes = getattr(s, "etapes", []) or []
                if etapes:
                    textes = preparer_texte_recette(s.nom_recette, etapes)
                    lecteur_vocal_recette(textes, key=f"tts_reste_{i}")
            except ImportError:
                pass


__all__ = ["afficher_restes_creatifs"]
