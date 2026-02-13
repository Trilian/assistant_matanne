"""
Sidebar avec navigation par modules.
"""

import streamlit as st

from src.core.cache import Cache
from src.core.lazy_loader import ChargeurModuleDiffere, afficher_stats_chargement_differe
from src.core.state import GestionnaireEtat, obtenir_etat

# ═══════════════════════════════════════════════════════════
# MENU DES MODULES - Configuration centralisée
# ═══════════════════════════════════════════════════════════

MODULES_MENU = {
    "ðŸ  Accueil": "accueil",
    # Calendrier unifié - VUE CENTRALE
    "ðŸ“… Calendrier Familial": "planning.calendrier_unifie",
    # Cuisine - Workflow: Plan â†’ Batch â†’ Courses
    "ðŸ³ Cuisine": {
        "ðŸ½ï¸ Planifier Repas": "cuisine.planificateur_repas",
        "ðŸ³ Batch Cooking": "cuisine.batch_cooking_detaille",
        "ðŸ›’ Courses": "cuisine.courses",
        "â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€": None,  # Séparateur
        "ðŸ“š Recettes": "cuisine.recettes",
        "ðŸ¥« Inventaire": "cuisine.inventaire",
    },
    # Famille - HUB
    "ðŸ‘¨â€ðŸ‘©â€ðŸ‘§â€ðŸ‘¦ Famille": {
        "ðŸ  Hub Famille": "famille.hub",
        "ðŸ‘¶ Jules": "famille.jules",
        "ðŸ“… Planning Jules": "famille.jules_planning",
        "ðŸ’ª Mon Suivi": "famille.suivi_perso",
        "ðŸŽ‰ Weekend": "famille.weekend",
        "ðŸ›ï¸ Achats": "famille.achats_famille",
    },
    # Maison
    "ðŸ  Maison": {
        "ðŸ  Hub Maison": "maison",
        "ðŸŒ³ Zones Jardin": "maison.jardin_zones",
        "ðŸ”‹ Énergie": "maison.energie",
        "ðŸ“¸ Scan Factures": "maison.scan_factures",
        "ðŸ§¹ Entretien": "maison.entretien",
        "ðŸ›‹ï¸ Meubles": "maison.meubles",
        "ðŸ’° Dépenses": "maison.depenses",
        "ðŸŒ± Éco-Tips": "maison.eco",
    },
    # Jeux
    "ðŸŽ² Jeux": {
        "âš½ Paris Sportifs": "jeux.paris",
        "ðŸŽ° Loto": "jeux.loto",
    },
    # Outils & Config
    "ðŸ”§ Outils": {
        "ðŸ“± Code-barres": "barcode",
        "ðŸ“Š Rapports": "rapports",
        "ðŸ”” Notifications": "notifications_push",
    },
    "âš™ï¸ Paramètres": "parametres",
}


def afficher_sidebar():
    """Affiche la sidebar avec navigation."""
    etat = obtenir_etat()

    with st.sidebar:
        st.title("Navigation")

        # Fil d'Ariane
        fil_ariane = GestionnaireEtat.obtenir_fil_ariane_navigation()
        if len(fil_ariane) > 1:
            st.caption(" â†’ ".join(fil_ariane[-3:]))
            if st.button("â¬…ï¸ Retour"):
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
        etat.mode_debug = st.checkbox("ðŸ› Debug", value=etat.mode_debug)

        if etat.mode_debug:
            with st.expander("État App"):
                st.json(GestionnaireEtat.obtenir_resume_etat())

                if st.button("ðŸ”„ Reset"):
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
