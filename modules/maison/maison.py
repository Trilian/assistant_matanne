# assistant_matanne/modules/maison.py

import streamlit as st
import importlib
from core.helpers import log_event
from core.schema_manager import create_all_tables

def app():
    st.markdown(
        """
        <style>
        .module-btn {
            padding: 18px;
            background: #f3f6f4;
            border-radius: 14px;
            border: 1px solid #d7e3dc;
            transition: 0.2s ease;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 1.2rem;
            font-weight: 600;
            color: #2d4d36;
        }
        .module-btn:hover {
            background: #e9f2ec;
            transform: translateY(-2px);
            border-color: #b5ccb8;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.header("🏡 Maison & Organisation")
    st.caption("Votre centre de gestion familiale : cuisine, stocks, routines et projets au même endroit.")

    create_all_tables()

    SUBMODULES = {
        "🍲 Recettes": "modules.recettes",
        "📦 Inventaire": "modules.inventaire",
        "🛒 Liste de courses": "modules.courses",
        "🥘 Batch Cooking": "modules.repas_batch",
        "🏡 Projets maison": "modules.projets_maison",
        "⏰ Routines": "modules.routines",
        "💡 Suggestions intelligentes": "modules.suggestions",
    }

    # État interne pour savoir quel sous-module est actif
    if "module_selection" not in st.session_state:
        st.session_state["module_selection"] = None

    # === Interface en grille moderne ===
    st.markdown("### Choisir une section")

    cols = st.columns(3)

    i = 0
    for label in SUBMODULES.keys():
        col = cols[i % 3]
        with col:
            if st.button(
                    f"{label}",
                    key=f"btn_{label}",
                    help=f"Ouvrir : {label}",
                    use_container_width=True,
                    type="secondary"
            ):
                st.session_state["module_selection"] = label
        i += 1

    st.markdown("---")

    # === Chargement du module choisi ===
    selected = st.session_state.get("module_selection")

    if selected:
        st.subheader(f"📂 {selected}")
        try:
            module = importlib.import_module(SUBMODULES[selected])
            module.app()
            log_event(f"[Maison] Module chargé : {selected}")
        except Exception as e:
            st.error(f"Erreur lors du chargement du module '{selected}' : {e}")
            log_event(f"[Maison] Erreur : {e}", level="error")
    else:
        st.info("Sélectionne un module ci-dessus pour commencer.")