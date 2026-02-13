"""
Module Planificateur de Repas Intelligent - UI Streamlit

Interface style Jow:
- Générateur IA de menus équilibrés
- Apprentissage des goûts (ðŸ‘/ðŸ‘Ž) persistant en DB
- Versions Jules intégrées
- Suggestions alternatives
- Validation équilibre nutritionnel
"""

from ._common import date, st, timedelta
from .components import (
    render_apprentissage_ia,
    render_carte_recette_suggestion,
    render_configuration_preferences,
    render_jour_planning,
    render_resume_equilibre,
)
from .generation import generer_semaine_ia

# Import des fonctions pour exposer l'API publique
from .pdf import generer_pdf_planning_session
from .preferences import (
    ajouter_feedback,
    charger_feedbacks,
    charger_preferences,
    sauvegarder_preferences,
)


def app():
    """Point d'entrée du module Planificateur de Repas."""

    st.title("ðŸ½ï¸ Planifier mes repas")
    st.caption("Générateur intelligent de menus équilibrés avec adaptation pour Jules")

    # Initialiser la session
    if "planning_data" not in st.session_state:
        st.session_state.planning_data = {}

    if "planning_date_debut" not in st.session_state:
        # Par défaut: mercredi prochain
        today = date.today()
        days_until_wednesday = (2 - today.weekday()) % 7
        if days_until_wednesday == 0:
            days_until_wednesday = 7
        st.session_state.planning_date_debut = today + timedelta(days=days_until_wednesday)

    # Tabs
    tab_planifier, tab_preferences, tab_historique = st.tabs(
        ["ðŸ“… Planifier", "âš™ï¸ Préférences", "ðŸ“š Historique"]
    )

    # ═══════════════════════════════════════════════════════
    # TAB: PLANIFIER
    # ═══════════════════════════════════════════════════════

    with tab_planifier:
        # Sélection période
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            date_debut = st.date_input(
                "ðŸ“… Début de la semaine",
                value=st.session_state.planning_date_debut,
                format="DD/MM/YYYY",
            )
            st.session_state.planning_date_debut = date_debut

        with col2:
            date_fin = date_debut + timedelta(days=9)  # Mer â†’ Ven suivant = 10 jours
            st.markdown(f"**â†’** Vendredi {date_fin.strftime('%d/%m/%Y')}")

        with col3:
            st.write("")  # Spacer

        st.divider()

        # Apprentissage IA
        with st.expander("ðŸ§  Ce que l'IA a appris", expanded=False):
            render_apprentissage_ia()

        st.divider()

        # Bouton génération
        col_gen1, col_gen2, col_gen3 = st.columns([2, 2, 1])

        with col_gen1:
            if st.button("ðŸŽ² Générer une semaine", type="primary", use_container_width=True):
                with st.spinner("ðŸ¤– L'IA réfléchit à vos menus..."):
                    result = generer_semaine_ia(date_debut)

                    if result and result.get("semaine"):
                        # Convertir en format interne
                        planning = {}
                        for jour_data in result["semaine"]:
                            jour = jour_data.get("jour", "")
                            planning[jour] = {
                                "midi": jour_data.get("midi"),
                                "soir": jour_data.get("soir"),
                                "gouter": jour_data.get("gouter"),
                            }

                        st.session_state.planning_data = planning
                        st.session_state.planning_conseils = result.get("conseils_batch", "")
                        st.session_state.planning_suggestions_bio = result.get(
                            "suggestions_bio", []
                        )

                        st.success("âœ… Semaine générée!")
                        st.rerun()
                    else:
                        st.error("âŒ Impossible de générer la semaine")

        with col_gen2:
            if st.button("ðŸ“¦ Utiliser mon stock", use_container_width=True):
                st.info("ðŸš§ Fonctionnalité en développement")

        with col_gen3:
            if st.button("ðŸ”„ Reset", use_container_width=True):
                st.session_state.planning_data = {}
                st.rerun()

        st.divider()

        # Afficher le planning
        if st.session_state.planning_data:
            # Résumé équilibre
            render_resume_equilibre(st.session_state.planning_data)

            st.divider()

            # Afficher par jour
            for i, (jour, repas) in enumerate(st.session_state.planning_data.items()):
                jour_date = date_debut + timedelta(days=i)
                render_jour_planning(jour, jour_date, repas, f"jour_{i}")

            st.divider()

            # Conseils batch
            if st.session_state.get("planning_conseils"):
                st.markdown("##### ðŸ³ Conseils Batch Cooking")
                st.info(st.session_state.planning_conseils)

            # Suggestions bio
            if st.session_state.get("planning_suggestions_bio"):
                st.markdown("##### ðŸŒ¿ Suggestions bio/local")
                for sug in st.session_state.planning_suggestions_bio:
                    st.caption(f"• {sug}")

            st.divider()

            # Actions finales
            col_val1, col_val2, col_val3 = st.columns(3)

            with col_val1:
                if st.button("ðŸ’š Valider ce planning", type="primary", use_container_width=True):
                    st.success("âœ… Planning validé! Redirection vers les courses...")
                    # TODO: Créer le planning en DB et générer la liste de courses

            with col_val2:
                if st.button("ðŸ›’ Générer courses", use_container_width=True):
                    st.info("ðŸš§ Génération de la liste de courses...")

            with col_val3:
                # Export PDF du planning
                if st.session_state.planning_data:
                    pdf_buffer = generer_pdf_planning_session(
                        planning_data=st.session_state.planning_data,
                        date_debut=date_debut,
                        conseils=st.session_state.get("planning_conseils", ""),
                        suggestions_bio=st.session_state.get("planning_suggestions_bio", []),
                    )
                    if pdf_buffer:
                        st.download_button(
                            label="ðŸ–¨ï¸ Télécharger PDF",
                            data=pdf_buffer,
                            file_name=f"planning_{date_debut.strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                        )
                    else:
                        st.button("ðŸ–¨ï¸ Imprimer", disabled=True, use_container_width=True)

        else:
            st.info("ðŸ‘† Cliquez sur 'Générer une semaine' pour commencer")

    # ═══════════════════════════════════════════════════════
    # TAB: PRÉFÉRENCES
    # ═══════════════════════════════════════════════════════

    with tab_preferences:
        render_configuration_preferences()

    # ═══════════════════════════════════════════════════════
    # TAB: HISTORIQUE
    # ═══════════════════════════════════════════════════════

    with tab_historique:
        st.subheader("ðŸ“š Historique des plannings")

        # TODO: Charger l'historique depuis la DB
        st.info("ðŸš§ Historique des plannings passés à venir")

        st.markdown("##### ðŸ§  Vos feedbacks")
        feedbacks = charger_feedbacks()

        if feedbacks:
            for fb in feedbacks[-10:]:
                emoji = (
                    "ðŸ‘"
                    if fb.feedback == "like"
                    else "ðŸ‘Ž"
                    if fb.feedback == "dislike"
                    else "ðŸ˜"
                )
                st.caption(f"{emoji} {fb.recette_nom} ({fb.date_feedback.strftime('%d/%m')})")
        else:
            st.caption("Pas encore de feedbacks")


__all__ = [
    # Entry point
    "app",
    # PDF
    "generer_pdf_planning_session",
    # Preferences
    "charger_preferences",
    "sauvegarder_preferences",
    "charger_feedbacks",
    "ajouter_feedback",
    # Components
    "render_configuration_preferences",
    "render_apprentissage_ia",
    "render_carte_recette_suggestion",
    "render_jour_planning",
    "render_resume_equilibre",
    # Generation
    "generer_semaine_ia",
]
