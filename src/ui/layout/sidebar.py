"""
Sidebar avec navigation par modules.
"""

import streamlit as st

from src.core.caching import Cache
from src.core.lazy_loader import ChargeurModuleDiffere, afficher_stats_chargement_differe
from src.core.state import GestionnaireEtat, obtenir_etat

# ═══════════════════════════════════════════════════════════
# MENU DES MODULES - Configuration centralisée
# ═══════════════════════════════════════════════════════════

MODULES_MENU = {
    "🏠 Accueil": "accueil",
    # Calendrier unifié - VUE CENTRALE
    "📅 Calendrier Familial": "planning.calendrier",
    "📋 Templates": "planning.templates_ui",
    "📊 Timeline": "planning.timeline_ui",
    # Cuisine - Workflow: Plan → Batch → Courses
    "🍳 Cuisine": {
        "🍽️ Planifier Repas": "cuisine.planificateur_repas",
        "🍳 Batch Cooking": "cuisine.batch_cooking_detaille",
        "🛒 Courses": "cuisine.courses",
        "───────────": None,  # Séparateur
        "📋 Recettes": "cuisine.recettes",
        "🥫 Inventaire": "cuisine.inventaire",
    },
    # Famille - HUB
    "👨‍👩‍👧‍👦 Famille": {
        "🏠 Hub Famille": "famille.hub",
        "👶 Jules": "famille.jules",
        "📅 Planning Jules": "famille.jules_planning",
        "💪 Mon Suivi": "famille.suivi_perso",
        "🎉 Weekend": "famille.weekend",
        "🛍️ Achats": "famille.achats_famille",
    },
    # Maison
    "🏠 Maison": {
        "🏠 Hub": "maison.hub",
        "� Jardin": "maison.jardin",
        "🏡 Entretien": "maison.entretien",
        "💡 Charges": "maison.energie",
        "💰 Dépenses": "maison.depenses",
    },
    # Jeux
    "🎲 Jeux": {
        "⚽ Paris Sportifs": "jeux.paris",
        "🎰 Loto": "jeux.loto",
    },
    # Outils & Config
    "🔧 Outils": {
        "📱 Code-barres": "barcode",
        "🧾 Scan Factures": "scan_factures",
        "🔍 Produits": "recherche_produits",
        "📊 Rapports": "rapports",
        "🔔 Notifications": "notifications_push",
    },
    "⚙️ Paramètres": "parametres",
}


def afficher_sidebar():
    """Affiche la sidebar avec navigation."""
    etat = obtenir_etat()

    with st.sidebar:
        st.title("Navigation")

        # Fil d'Ariane
        fil_ariane = GestionnaireEtat.obtenir_fil_ariane_navigation()
        if len(fil_ariane) > 1:
            st.caption(" → ".join(fil_ariane[-3:]))
            if st.button("⬅️ Retour"):
                GestionnaireEtat.revenir()
                st.rerun()
            st.markdown("---")

        # Rendu du menu
        _rendre_menu(MODULES_MENU, etat)

        st.markdown("---")

        # Stats Lazy Loading
        afficher_stats_chargement_differe()

        st.markdown("---")

        # Debug
        etat.mode_debug = st.checkbox("🐛 Debug", value=etat.mode_debug)

        if etat.mode_debug:
            with st.expander("État App"):
                st.json(GestionnaireEtat.obtenir_resume_etat())

                if st.button("🔄 Reset"):
                    GestionnaireEtat.reinitialiser()
                    Cache.vider()
                    ChargeurModuleDiffere.clear_cache()
                    st.success("Reset OK")
                    st.rerun()


def _rendre_menu(menu: dict, etat) -> None:
    """Rend le menu de navigation récursivement."""
    for label, value in menu.items():
        if isinstance(value, dict):
            # Module avec sous-menus
            est_actif = any(etat.module_actuel.startswith(sub) for sub in value.values() if sub)

            with st.expander(label, expanded=est_actif):
                for sub_label, sub_value in value.items():
                    # Skip séparateurs
                    if sub_value is None:
                        st.divider()
                        continue

                    est_sous_menu_actif = etat.module_actuel == sub_value

                    if st.button(
                        sub_label,
                        key=f"btn_{sub_value}",
                        use_container_width=True,
                        type="primary" if est_sous_menu_actif else "secondary",
                        disabled=est_sous_menu_actif,
                    ):
                        GestionnaireEtat.naviguer_vers(sub_value)
                        st.rerun()
        else:
            # Module simple
            est_actif = etat.module_actuel == value

            if st.button(
                label,
                key=f"btn_{value}",
                use_container_width=True,
                type="primary" if est_actif else "secondary",
                disabled=est_actif,
            ):
                GestionnaireEtat.naviguer_vers(value)
                st.rerun()
