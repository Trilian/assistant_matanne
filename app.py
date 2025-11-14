import streamlit as st
import importlib
from core.helpers import log_event
from core.config import get_app_info
from core.schema_manager import create_all_tables  # remplacé ensure_tables
from core.database import get_connection

def app():
    # --- Initialisation de la base ---
    create_all_tables()
    app_info = get_app_info()
    st.set_page_config(
        page_title=f"{app_info['name']}",
        page_icon="🌿",
        layout="wide"
    )

    # === Application du thème ===
    theme = app_info.get("theme", "light")
    if theme == "dark":
        st.markdown(
            """
            <style>
            body, .main, .stApp { background-color: #1e1e1e; color: #fafafa; }
            </style>
            """,
            unsafe_allow_html=True
        )

    # === HEADER PRINCIPAL ===
    st.markdown(
        f"""
        <div style='display:flex; align-items:center; justify-content:space-between;' >
            <div style='font-size:2rem; color:#3b6b48; font-weight:700;'>
                🌿 {app_info['name']}
            </div>
            <div style='color:gray; font-size:0.9rem;'>
                v{app_info['version']}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<hr style='margin-top:-5px;'>", unsafe_allow_html=True)

    # === SIDEBAR ===
    st.sidebar.header("Navigation")

    # --- Vérifie le nombre de notifications non lues ---
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM user_notifications WHERE read = 0")
        notif_count = cur.fetchone()[0]
        conn.close()
    except Exception:
        notif_count = 0

    # --- Label "Paramètres" stylisé ---
    if notif_count > 0:
        notif_label = f"""
        ⚙️ Paramètres 
        <span style="
            background-color:#e63946;
            color:white;
            border-radius:50%;
            font-size:0.8rem;
            font-weight:bold;
            padding:0.15em 0.4em;
            margin-left:0.4em;">
            {notif_count}
        </span>
        """
    else:
        notif_label = "⚙️ Paramètres"

    # --- Dictionnaire des modules ---
    modules = {
        "🏠 Accueil": "modules.accueil",
        "🍲 Recettes": "modules.recettes",
        "📦 Inventaire": "modules.inventaire",
        "👶 Jules": "modules.suivi_enfant",
        "🌱 Jardin": "modules.jardin",
        "💆 Bien-être": "modules.bien_etre",
        "🗓️ Calendrier": "modules.calendrier",
        "🏡 Projets Maison": "modules.projets_maison",
        "🥘 Repas Batch": "modules.repas_batch",
        "💡 Suggestions": "modules.suggestions",
        "⏰ Routines": "modules.routines",
        "🌤️ Météo": "modules.weather_ui",
        "⚙️ Paramètres": "modules.parametres",
        "🧪 Mode Test": "modules.test_mode",

    }

    labels = list(modules.keys())

    # --- Radio navigation avec clé unique ---
    choix = st.sidebar.radio(
        "Choisir un module :",
        labels,
        key="sidebar_module_radio"
    )

    # --- Bouton rechargement avec clé unique ---
    if st.sidebar.button("🔄 Recharger les données", key="reload_data_btn"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.toast("Données rechargées ✅")
        log_event("Rechargement global effectué.")
        st.rerun()

    # --- Chargement du module sélectionné ---
    try:
        module_path = modules[choix]
        module = importlib.import_module(module_path)
        module.app()
        log_event(f"Module {choix} chargé avec succès.")
    except Exception as e:
        st.error(f"Erreur lors du chargement du module {choix} : {e}")
        log_event(f"Erreur module {choix} : {e}", level="error")

if __name__ == "__main__":
    app()