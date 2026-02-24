"""
Module Planificateur de Repas Intelligent - UI Streamlit

Interface style Jow:
- Générateur IA de menus équilibrés
- Apprentissage des goûts (👍/👎) persistant en DB
- Versions Jules intégrées
- Suggestions alternatives
- Validation équilibre nutritionnel
"""

from datetime import date, timedelta

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.core.session_keys import SK
from src.modules._framework import avec_gestion_erreurs_ui, error_boundary
from src.ui import etat_vide
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

from .components import (
    afficher_apprentissage_ia,
    afficher_carte_recette_suggestion,
    afficher_configuration_preferences,
    afficher_jour_planning,
    afficher_resume_equilibre,
)
from .generation import generer_semaine_ia

# Import des fonctions pour exposer l'API publique
from .pdf import generer_pdf_planning_session

# Session keys scopées
_keys = KeyNamespace("planificateur_repas")
from .preferences import (
    ajouter_feedback,
    charger_feedbacks,
    charger_preferences,
    sauvegarder_preferences,
)


def _sauvegarder_planning_db(planning_data: dict, date_debut: date) -> bool:
    """Sauvegarde le planning généré en base de données."""
    try:
        from src.services.cuisine.planning import obtenir_service_planning

        service = obtenir_service_planning()

        # Construire la sélection de recettes
        recettes_selection = {}
        for i, (jour, repas) in enumerate(planning_data.items()):
            for type_repas in ["midi", "soir"]:
                recette_info = repas.get(type_repas)
                if recette_info and isinstance(recette_info, dict) and recette_info.get("id"):
                    recettes_selection[f"jour_{i}"] = recette_info["id"]
                    break  # Un repas par jour suffit pour le mapping

        if recettes_selection:
            planning = service.creer_planning_avec_choix(
                semaine_debut=date_debut,
                recettes_selection=recettes_selection,
            )
            return planning is not None
    except Exception as e:
        import logging

        logging.getLogger(__name__).error(f"Erreur sauvegarde planning: {e}")
    return False


def _charger_historique_plannings() -> list[dict]:
    """Charge l'historique des plannings via ServicePlanning."""
    try:
        from src.services.cuisine.planning import obtenir_service_planning

        service = obtenir_service_planning()
        return service.get_historique_plannings(limit=20)
    except Exception as e:
        import logging

        logging.getLogger(__name__).debug(f"Erreur chargement historique: {e}")
    return []


@profiler_rerun("planificateur_repas")
def app():
    """Point d'entrée du module Planificateur de Repas."""

    st.title("🍽️ Planifier mes repas")
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

    # Tabs avec deep linking URL
    TAB_LABELS = ["📅 Planifier", "⚙️ Préférences", "📋 Historique"]
    tab_index = tabs_with_url(TAB_LABELS, param="tab")
    tab_planifier, tab_preferences, tab_historique = st.tabs(TAB_LABELS)

    # ═══════════════════════════════════════════════════════
    # TAB: PLANIFIER
    # ═══════════════════════════════════════════════════════

    with tab_planifier:
        # Sélection période
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            date_debut = st.date_input(
                "📅 Début de la semaine",
                value=st.session_state.planning_date_debut,
                format="DD/MM/YYYY",
            )
            st.session_state.planning_date_debut = date_debut

        with col2:
            date_fin = date_debut + timedelta(days=9)  # Mer → Ven suivant = 10 jours
            st.markdown(f"**→** Vendredi {date_fin.strftime('%d/%m/%Y')}")

        with col3:
            st.write("")  # Spacer

        st.divider()

        # Apprentissage IA
        with st.expander("🧠 Ce que l'IA a appris", expanded=False):
            afficher_apprentissage_ia()

        st.divider()

        # Bouton génération
        col_gen1, col_gen2, col_gen3 = st.columns([2, 2, 1])

        with col_gen1:
            if st.button("🎲 Générer une semaine", type="primary", use_container_width=True):
                with st.spinner("🤖 L'IA réfléchit à vos menus..."):
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

                        st.success("✅ Semaine générée!")
                        st.rerun()
                    else:
                        st.error("❌ Impossible de générer la semaine")

        with col_gen2:
            if st.button("📦 Utiliser mon stock", use_container_width=True):
                try:
                    from src.services.inventaire import obtenir_service_inventaire

                    service_inv = obtenir_service_inventaire()
                    stock = service_inv.lister_produits() if service_inv else []
                    if stock:
                        noms_stock = [p.nom for p in stock[:20]]
                        st.session_state[SK.PLANNING_STOCK_CONTEXT] = noms_stock
                        st.success(f"✅ {len(noms_stock)} produits chargés depuis votre stock")
                        st.caption("Cliquez sur 'Générer une semaine' pour les intégrer")
                    else:
                        st.info("📦 Stock vide. Ajoutez des produits dans l'inventaire.")
                except Exception as e:
                    import logging

                    logging.getLogger(__name__).error(f"Erreur chargement stock: {e}")
                    st.warning("⚠️ Impossible de charger le stock")

        with col_gen3:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state.planning_data = {}
                st.rerun()

        st.divider()

        # Afficher le planning
        if st.session_state.planning_data:
            # Résumé équilibre
            afficher_resume_equilibre(st.session_state.planning_data)

            st.divider()

            # Afficher par jour
            for i, (jour, repas) in enumerate(st.session_state.planning_data.items()):
                jour_date = date_debut + timedelta(days=i)
                afficher_jour_planning(jour, jour_date, repas, f"jour_{i}")

            st.divider()

            # Conseils batch
            if st.session_state.get(SK.PLANNING_CONSEILS):
                st.markdown("##### 🍳 Conseils Batch Cooking")
                st.info(st.session_state.planning_conseils)

            # Suggestions bio
            if st.session_state.get(SK.PLANNING_SUGGESTIONS_BIO):
                st.markdown("##### 🌿 Suggestions bio/local")
                for sug in st.session_state.planning_suggestions_bio:
                    st.caption(f"• {sug}")

            st.divider()

            # Actions finales
            col_val1, col_val2, col_val3 = st.columns(3)

            with col_val1:
                if st.button("💚 Valider ce planning", type="primary", use_container_width=True):
                    saved = _sauvegarder_planning_db(st.session_state.planning_data, date_debut)
                    if saved:
                        st.success("✅ Planning validé et sauvegardé !")
                    else:
                        st.success("✅ Planning validé!")
                        st.caption("⚠️ Sauvegarde BD partielle (certaines recettes non liées)")

            with col_val2:
                if st.button("🛒 Générer courses", use_container_width=True):
                    try:
                        # Extraire les noms de recettes du planning
                        recettes_noms = []
                        for jour, repas in st.session_state.planning_data.items():
                            for type_repas in ["midi", "soir", "gouter"]:
                                r = repas.get(type_repas)
                                if r and isinstance(r, dict) and r.get("nom"):
                                    recettes_noms.append(r["nom"])

                        if recettes_noms:
                            # Stocker dans session_state pour le module courses
                            st.session_state[SK.COURSES_DEPUIS_PLANNING] = recettes_noms
                            st.success(
                                f"✅ Liste de courses générée ({len(recettes_noms)} recettes)"
                            )
                            st.caption("🛒 Allez dans le module Courses pour gérer la liste")
                        else:
                            st.warning("⚠️ Aucune recette trouvée dans le planning")
                    except Exception as e:
                        import logging

                        logging.getLogger(__name__).error(f"Erreur génération courses: {e}")
                        st.error("❌ Erreur lors de la génération")

            with col_val3:
                # Export PDF du planning
                if st.session_state.planning_data:
                    pdf_buffer = generer_pdf_planning_session(
                        planning_data=st.session_state.planning_data,
                        date_debut=date_debut,
                        conseils=st.session_state.get(SK.PLANNING_CONSEILS, ""),
                        suggestions_bio=st.session_state.get(SK.PLANNING_SUGGESTIONS_BIO, []),
                    )
                    if pdf_buffer:
                        st.download_button(
                            label="🖨️ Télécharger PDF",
                            data=pdf_buffer,
                            file_name=f"planning_{date_debut.strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                        )
                    else:
                        st.button("🖨️ Imprimer", disabled=True, use_container_width=True)

        else:
            st.info("👆 Cliquez sur 'Générer une semaine' pour commencer")

    # ═══════════════════════════════════════════════════════
    # TAB: PRÉFÉRENCES
    # ═══════════════════════════════════════════════════════

    with tab_preferences:
        with error_boundary(titre="Erreur préférences"):
            afficher_configuration_preferences()

    # ═══════════════════════════════════════════════════════
    # TAB: HISTORIQUE
    # ═══════════════════════════════════════════════════════

    with tab_historique:
        st.subheader("📋 Historique des plannings")

        historique_plannings = _charger_historique_plannings()

        if historique_plannings:
            for plan in historique_plannings:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"**📅 {plan['nom']}**")
                        st.caption(
                            f"Du {plan['debut'].strftime('%d/%m/%Y')} au {plan['fin'].strftime('%d/%m/%Y')}"
                        )
                    with col2:
                        st.metric("🍽️ Repas", plan["nb_repas"])
                    with col3:
                        badge = "🤖 IA" if plan["genere_par_ia"] else "✍️ Manuel"
                        st.write(badge)
        else:
            etat_vide("Aucun planning sauvegardé", "💭", "Générez votre premier planning de repas")

        st.divider()

        st.markdown("##### 🧠 Vos feedbacks")
        feedbacks = charger_feedbacks()

        if feedbacks:
            for fb in feedbacks[-10:]:
                emoji = (
                    "👍" if fb.feedback == "like" else "👎" if fb.feedback == "dislike" else "😐"
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
    "afficher_configuration_preferences",
    "afficher_apprentissage_ia",
    "afficher_carte_recette_suggestion",
    "afficher_jour_planning",
    "afficher_resume_equilibre",
    # Generation
    "generer_semaine_ia",
]
