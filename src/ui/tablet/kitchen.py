"""
Mode cuisine - Interface step-by-step pour recettes.

Fournit une interface tactile simplifiée pour:
- Suivre les étapes d'une recette
- Timer intégré
- Navigation par gestes/boutons
"""

from typing import Any

import streamlit as st

from .config import TabletMode, get_tablet_mode, set_tablet_mode


def render_kitchen_recipe_view(
    recette: dict[str, Any],
    key: str = "kitchen_recipe",
):
    """
    Affiche une recette en mode cuisine (step-by-step).

    Args:
        recette: Dict avec nom, ingredients, instructions
        key: Clé unique
    """
    # État
    if f"{key}_step" not in st.session_state:
        st.session_state[f"{key}_step"] = 0

    current_step = st.session_state[f"{key}_step"]
    instructions = recette.get("instructions", [])
    total_steps = len(instructions)

    # Timer (si défini)
    if f"{key}_timer" in st.session_state and st.session_state[f"{key}_timer"] > 0:
        st.markdown(
            f"""
            <div class="kitchen-timer active">
                ⏱️ {st.session_state[f"{key}_timer"]} min
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Titre de la recette
    st.markdown(f"## 👨‍🍳 {recette.get('nom', 'Recette')}")

    # Navigation par onglets
    tab1, tab2 = st.tabs(["📝 Étapes", "🥕 Ingrédients"])

    with tab1:
        if current_step == 0:
            # Écran d'accueil
            st.markdown("### 🚀 Prêt à cuisiner ?")
            st.markdown(f"**{total_steps} étapes** à suivre")

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
                "▶️ Commencer", key=f"{key}_start", type="primary", use_container_width=True
            ):
                st.session_state[f"{key}_step"] = 1
                st.rerun()

        elif current_step > total_steps:
            # Fin de la recette
            st.markdown("### 🎉 Bravo !")
            st.markdown("Votre plat est prêt. Bon appétit !")
            st.balloons()

            if st.button("🔄 Recommencer", key=f"{key}_restart", use_container_width=True):
                st.session_state[f"{key}_step"] = 0
                st.rerun()

        else:
            # Étape courante
            instruction = instructions[current_step - 1]

            st.markdown(
                f"""
                <div class="kitchen-step-card kitchen-step-transition">
                    <span class="kitchen-step-number">{current_step}</span>
                    <span style="font-size: 1.4rem;">{instruction}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Barre de progression
            progress = current_step / total_steps
            st.progress(progress, text=f"Étape {current_step}/{total_steps}")

            # Timer rapide
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("⏱️ 1 min", key=f"{key}_timer_1"):
                    st.session_state[f"{key}_timer"] = 1
            with col2:
                if st.button("⏱️ 5 min", key=f"{key}_timer_5"):
                    st.session_state[f"{key}_timer"] = 5
            with col3:
                if st.button("⏱️ 10 min", key=f"{key}_timer_10"):
                    st.session_state[f"{key}_timer"] = 10

    with tab2:
        # Liste des ingrédients
        ingredients = recette.get("ingredients", [])

        st.markdown("### 🥕 Ingrédients")

        for i, ing in enumerate(ingredients):
            if isinstance(ing, dict):
                quantite = ing.get("quantite", "")
                unite = ing.get("unite", "")
                nom = ing.get("nom", ing.get("ingredient", ""))
                label = f"{quantite} {unite} {nom}".strip()
            else:
                label = str(ing)

            st.checkbox(label, key=f"{key}_ing_{i}")

    # Navigation fixe en bas
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if current_step > 1:
            if st.button("◀️ Précédent", key=f"{key}_prev", use_container_width=True):
                st.session_state[f"{key}_step"] = current_step - 1
                st.rerun()

    with col2:
        if st.button("❌ Quitter", key=f"{key}_quit", use_container_width=True):
            st.session_state[f"{key}_step"] = 0

    with col3:
        if current_step >= 1 and current_step <= total_steps:
            btn_label = "✅ Terminé" if current_step == total_steps else "Suivant ▶️"
            if st.button(btn_label, key=f"{key}_next", type="primary", use_container_width=True):
                st.session_state[f"{key}_step"] = current_step + 1
                st.rerun()


def render_mode_selector():
    """Affiche le sélecteur de mode dans la sidebar."""
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📱 Mode d'affichage")

        mode = get_tablet_mode()

        options = {
            TabletMode.NORMAL: "🖥️ Normal",
            TabletMode.TABLET: "📱 Tablette",
            TabletMode.KITCHEN: "👨‍🍳 Cuisine",
        }

        selected = st.selectbox(
            "Choisir le mode",
            options=list(options.keys()),
            format_func=lambda x: options[x],
            index=list(options.keys()).index(mode),
            key="mode_selector",
            label_visibility="collapsed",
        )

        if selected != mode:
            set_tablet_mode(selected)
            st.rerun()

        if mode == TabletMode.KITCHEN:
            st.info(
                "🍳 Mode cuisine activé:\n- Interface simplifiée\n- Gros boutons tactiles\n- Navigation par étapes"
            )
