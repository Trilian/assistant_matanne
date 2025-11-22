import streamlit as st
import importlib
from core.helpers import log_event
from core.config import get_app_info
from core.schema_manager import create_all_tables
from core.database import get_connection

def load_module(module_path):
    """Charge un module via importlib et appelle sa fonction app()"""
    try:
        module = importlib.import_module(module_path)
        if hasattr(module, "app"):
            module.app()
            log_event(f"Module {module_path} chargé avec succès.")
        else:
            st.warning(f"Le module {module_path} n'a pas de fonction app()")
    except Exception as e:
        st.error(f"Erreur lors du chargement du module {module_path} : {e}")
        log_event(f"Erreur module {module_path} : {e}", level="error")

def app():
    # --- Initialisation de la base ---
    create_all_tables()
    app_info = get_app_info()
    st.set_page_config(
        page_title=f"{app_info['name']}",
        page_icon="🌿",
        layout="wide"
    )

    # === Thème ===
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

    # === HEADER ===
    st.markdown(
        f"""
        <div style='display:flex; align-items:center; justify-content:space-between;' >
            <div style='font-size:2rem; color:#3b6b48; font-weight:700;'>{app_info['name']}</div>
            <div style='color:gray; font-size:0.9rem;'>v{app_info['version']}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<hr style='margin-top:-5px;'>", unsafe_allow_html=True)

    # === SIDEBAR ===
    st.sidebar.header("Navigation")

    # Notifications
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM user_notifications WHERE read = 0")
        notif_count = cur.fetchone()[0]
        conn.close()
    except Exception:
        notif_count = 0

    notif_label = f"⚙️ Paramètres <span style='background-color:#e63946;color:white;border-radius:50%;font-size:0.8rem;font-weight:bold;padding:0.15em 0.4em;margin-left:0.4em;'>{notif_count}</span>" if notif_count else "⚙️ Paramètres"

    # Modules et sous-modules
    modules = {
        "👨‍👩‍👧 Famille": {
            "Suivi Jules": "modules.famille.suivi_enfant",
            "Bien-être": "modules.famille.bien_etre",
        },
        "🏡 Maison & Organisation": {
            "Maison": "modules.maison.maison",
            "Projets": "modules.maison.projets_maison",
            "Routines": "modules.maison.routines",
            "Jardin": "modules.maison.jardin",
        },
        "🍲 Cuisine": {
            "Repas / Batch Cooking": "modules.cuisine.repas_batch",
            "Recettes": "modules.cuisine.recettes",
            "Courses": "modules.cuisine.courses",
            "Inventaire": "modules.cuisine.inventaire",
        },
        "🛠️ Outils": {
            "Suggestions": "modules.outils.suggestions",
            "Calendrier": "modules.outils.calendrier",
            "Météo": "modules.outils.weather_ui",
            "Mode Test": "modules.outils.test_mode",
            "Paramètres": "modules.parametres"
        },
    }

    # --- Initialisation de la sélection dans session_state ---
    if "choix_module" not in st.session_state:
        st.session_state.choix_module = "modules.accueil"  # Accueil par défaut

    # --- Bouton Accueil en haut du sidebar ---
    accueil_active = st.session_state.choix_module == "modules.accueil"
    if st.sidebar.button(f"🏠 Accueil {'✅' if accueil_active else ''}", key="btn_accueil"):
        st.session_state.choix_module = "modules.accueil"

    # --- Sidebar avec expanders et indicateur pour module actif ---
    for cat_label, cat_value in modules.items():
        with st.sidebar.expander(cat_label, expanded=True):
            if isinstance(cat_value, dict):
                for sub_label, sub_module in cat_value.items():
                    active = st.session_state.choix_module == sub_module
                    clicked = st.button(f"{sub_label} {'✅' if active else ''}", key=f"{cat_label}_{sub_label}")
                    if clicked:
                        st.session_state.choix_module = sub_module
            else:
                if sub_module != "modules.accueil":
                    active = st.session_state.choix_module == sub_module
                    clicked = st.button(f"{cat_label} {'✅' if active else ''}", key=f"{cat_label}")
                    if clicked:
                        st.session_state.choix_module = cat_value

    # --- Chargement du module sélectionné ---
    if st.session_state.choix_module:
        load_module(st.session_state.choix_module)

    # --- Bouton rechargement ---
    if st.sidebar.button("🔄 Recharger les données", key="reload_data_btn"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.toast("Données rechargées ✅")
        log_event("Rechargement global effectué.")
        st.experimental_rerun()


if __name__ == "__main__":
    app()