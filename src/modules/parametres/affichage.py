"""
Paramètres - Configuration Affichage
Mode tablette et personnalisation de l'interface
"""

import streamlit as st


def render_display_config():
    """Configuration de l'affichage et mode tablette."""

    st.markdown("### 🖥️ Configuration Affichage")
    st.caption("Personnalise l'interface selon ton appareil")

    try:
        from src.ui.tablet_mode import (
            TabletMode,
            get_tablet_mode,
            set_tablet_mode,
        )

        mode_options = {
            "💻 Normal": TabletMode.NORMAL,
            "📱 Tablette": TabletMode.TABLET,
            "🍳 Cuisine": TabletMode.KITCHEN,
        }

        mode_descriptions = {
            TabletMode.NORMAL: "Interface standard pour ordinateur",
            TabletMode.TABLET: "Boutons plus grands, interface tactile",
            TabletMode.KITCHEN: "Mode cuisine avec navigation par étapes",
        }

        # Initialiser si nécessaire
        if "display_mode_selection" not in st.session_state:
            current = get_tablet_mode()
            st.session_state.display_mode_selection = next(
                (label for label, mode in mode_options.items() if mode == current),
                "💻 Normal",
            )

        def on_mode_change():
            """Callback quand le mode change."""
            label = st.session_state.display_mode_key
            mode = mode_options[label]
            set_tablet_mode(mode)
            st.session_state.display_mode_selection = label

        st.markdown("#### Mode d'affichage")

        selected_label = st.radio(
            "Choisir le mode",
            options=list(mode_options.keys()),
            index=list(mode_options.keys()).index(st.session_state.display_mode_selection),
            horizontal=True,
            label_visibility="collapsed",
            key="display_mode_key",
            on_change=on_mode_change,
        )

        selected_mode = mode_options[selected_label]
        st.caption(mode_descriptions[selected_mode])

        st.markdown("---")

        st.markdown("#### Prévisualisation")

        if selected_mode == TabletMode.NORMAL:
            st.info("💻 Mode normal actif - Interface optimisée pour ordinateur")
        elif selected_mode == TabletMode.TABLET:
            st.warning("📱 Mode tablette actif - Boutons et textes agrandis")
        else:
            st.success("🍳 Mode cuisine actif - Interface simplifiée pour cuisiner")

    except ImportError:
        st.error("Module tablet_mode non disponible")
