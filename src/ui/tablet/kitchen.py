"""
Mode cuisine - Interface step-by-step pour recettes.

Fournit une interface tactile simplifiée pour:
- Suivre les étapes d'une recette
- Timer intégré
- Navigation par gestes/boutons
"""

from typing import Any

import streamlit as st

from .config import ModeTablette, definir_mode_tablette, obtenir_mode_tablette


def afficher_vue_recette_cuisine(
    recette: dict[str, Any],
    cle: str = "kitchen_recipe",
):
    """
    Affiche une recette en mode cuisine (step-by-step).

    Args:
        recette: Dict avec nom, ingredients, instructions
        cle: Clé unique
    """
    # État
    if f"{cle}_etape" not in st.session_state:
        st.session_state[f"{cle}_etape"] = 0

    etape_courante = st.session_state[f"{cle}_etape"]
    instructions = recette.get("instructions", [])
    total_etapes = len(instructions)

    # Timer (si défini)
    if f"{cle}_minuteur" in st.session_state and st.session_state[f"{cle}_minuteur"] > 0:
        st.markdown(
            f"""
            <div class="kitchen-timer active">
                ⏱️ {st.session_state[f"{cle}_minuteur"]} min
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Titre de la recette
    st.markdown(f"## 👨‍🍳 {recette.get('nom', 'Recette')}")

    # Navigation par onglets
    tab1, tab2 = st.tabs(["📝 Étapes", "🥕 Ingrédients"])

    with tab1:
        if etape_courante == 0:
            # Écran d'accueil
            st.markdown("### 🚀 Prêt à cuisiner ?")
            st.markdown(f"**{total_etapes} étapes** à suivre")

            # Temps
            temps_prep = recette.get("temps_preparation", 0)
            temps_cuisson = recette.get("temps_cuisson", 0)
            if temps_prep or temps_cuisson:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("⏱️ Préparation", f"{temps_prep} min")
                with col2:
                    st.metric("🔥 Cuisson", f"{temps_cuisson} min")

            if st.button(
                "▶️ Commencer", key=f"{cle}_demarrer", type="primary", use_container_width=True
            ):
                st.session_state[f"{cle}_etape"] = 1
                st.rerun()

        elif etape_courante > total_etapes:
            # Fin de la recette
            st.markdown("### 🎉 Bravo !")
            st.markdown("Votre plat est prêt. Bon appétit !")
            st.balloons()

            if st.button("🔄 Recommencer", key=f"{cle}_recommencer", use_container_width=True):
                st.session_state[f"{cle}_etape"] = 0
                st.rerun()

        else:
            # Étape courante
            instruction = instructions[etape_courante - 1]

            st.markdown(
                f"""
                <div class="kitchen-step-card kitchen-step-transition">
                    <span class="kitchen-step-number">{etape_courante}</span>
                    <span style="font-size: 1.4rem;">{instruction}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Barre de progression
            progression = etape_courante / total_etapes
            st.progress(progression, text=f"Étape {etape_courante}/{total_etapes}")

            # Timer rapide
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("⏱️ 1 min", key=f"{cle}_minuteur_1"):
                    st.session_state[f"{cle}_minuteur"] = 1
            with col2:
                if st.button("⏱️ 5 min", key=f"{cle}_minuteur_5"):
                    st.session_state[f"{cle}_minuteur"] = 5
            with col3:
                if st.button("⏱️ 10 min", key=f"{cle}_minuteur_10"):
                    st.session_state[f"{cle}_minuteur"] = 10

    with tab2:
        # Liste des ingrédients
        ingredients = recette.get("ingredients", [])

        st.markdown("### 🥕 Ingrédients")

        for i, ing in enumerate(ingredients):
            if isinstance(ing, dict):
                quantite = ing.get("quantite", "")
                unite = ing.get("unite", "")
                nom = ing.get("nom", ing.get("ingredient", ""))
                etiquette = f"{quantite} {unite} {nom}".strip()
            else:
                etiquette = str(ing)

            st.checkbox(etiquette, key=f"{cle}_ing_{i}")

    # Navigation fixe en bas
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if etape_courante > 1:
            if st.button("◀️ Précédent", key=f"{cle}_prec", use_container_width=True):
                st.session_state[f"{cle}_etape"] = etape_courante - 1
                st.rerun()

    with col2:
        if st.button("❌ Quitter", key=f"{cle}_quitter", use_container_width=True):
            st.session_state[f"{cle}_etape"] = 0

    with col3:
        if etape_courante >= 1 and etape_courante <= total_etapes:
            btn_label = "✅ Terminé" if etape_courante == total_etapes else "Suivant ▶️"
            if st.button(btn_label, key=f"{cle}_suiv", type="primary", use_container_width=True):
                st.session_state[f"{cle}_etape"] = etape_courante + 1
                st.rerun()


def afficher_selecteur_mode():
    """Affiche le sélecteur de mode dans la sidebar."""
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📱 Mode d'affichage")

        mode = obtenir_mode_tablette()

        options = {
            ModeTablette.NORMAL: "🖥️ Normal",
            ModeTablette.TABLETTE: "📱 Tablette",
            ModeTablette.CUISINE: "👨‍🍳 Cuisine",
        }

        selectionne = st.selectbox(
            "Choisir le mode",
            options=list(options.keys()),
            format_func=lambda x: options[x],
            index=list(options.keys()).index(mode),
            key="selecteur_mode",
            label_visibility="collapsed",
        )

        if selectionne != mode:
            definir_mode_tablette(selectionne)
            st.rerun()

        if mode == ModeTablette.CUISINE:
            st.info(
                "🍳 Mode cuisine activé:\\n- Interface simplifiée\\n- Gros boutons tactiles\\n- Navigation par étapes"
            )
