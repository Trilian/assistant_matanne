"""Point d'entrée principal du module Batch Cooking Détaillé."""

import logging
from datetime import date, time, timedelta

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.core.session_keys import SK
from src.modules._framework import avec_gestion_erreurs_ui, error_boundary
from src.modules.cuisine.batch_cooking_utils import estimer_heure_fin, formater_duree
from src.ui import etat_vide
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

from .components import (
    afficher_etape_batch,
    afficher_finition_jour_j,
    afficher_ingredient_detaille,
    afficher_liste_courses_batch,
    afficher_moments_jules,
    afficher_planning_semaine_preview,
    afficher_selecteur_session,
    afficher_timeline_session,
)
from .constants import TYPES_SESSION
from .generation import generer_batch_ia

logger = logging.getLogger(__name__)

# Session keys scopées
_keys = KeyNamespace("batch_cooking")


@profiler_rerun("batch_cooking")
def app():
    """Point d'entrée du module Batch Cooking Détaillé."""

    st.title("🍳 Batch Cooking")
    st.caption("Préparez vos repas de la semaine en une session efficace")

    # Initialiser la session
    if SK.BATCH_TYPE not in st.session_state:
        st.session_state.batch_type = "dimanche"

    if SK.BATCH_DATA not in st.session_state:
        st.session_state.batch_data = {}

    # Récupérer le planning (depuis le planificateur de repas)
    planning_data = st.session_state.get(SK.PLANNING_DATA, {})

    # Tabs avec deep linking URL
    TAB_LABELS = ["📋 Préparer", "👩‍🍳 Session Batch", "🍽️ Finitions Jour J"]
    tab_index = tabs_with_url(TAB_LABELS, param="tab")
    tab_preparer, tab_session, tab_finitions = st.tabs(TAB_LABELS)

    # ═══════════════════════════════════════════════════════
    # TAB: PRÉPARER
    # ═══════════════════════════════════════════════════════

    with tab_preparer:
        with error_boundary(titre="Erreur préparation batch"):
            # Sélection du type de session
            afficher_selecteur_session()

            st.divider()

            # Infos session
            type_info = TYPES_SESSION.get(st.session_state.batch_type, {})

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"**{type_info.get('label', 'Session')}**")
                st.caption(type_info.get("description", ""))

            with col2:
                st.markdown(f"**⏱️ Durée**: {type_info.get('duree_type', '2h')}")

            with col3:
                avec_jules = type_info.get("avec_jules", False)
                if avec_jules:
                    st.success("👶 Avec Jules")
                else:
                    st.info("👤 Solo")

            st.divider()

            # Sélection date & heure
            col_date, col_heure = st.columns(2)

            with col_date:
                date_batch = st.date_input(
                    "📅 Date de la session",
                    value=date.today() + timedelta(days=1),
                    format="DD/MM/YYYY",
                )

            with col_heure:
                heure_batch = st.time_input(
                    "⏰ Heure de début",
                    value=type_info.get("heure_defaut", time(10, 0)),
                )

            st.session_state.batch_date = date_batch
            st.session_state.batch_heure = heure_batch

            st.divider()

            # Preview du planning
            st.markdown("##### 📋 Recettes du planning")

            if planning_data:
                afficher_planning_semaine_preview(planning_data)
            else:
                st.warning("⚠️ Aucun planning de repas trouvé.")
                if st.button("📅 Aller au planificateur de repas"):
                    from src.core.state import naviguer, rerun

                    naviguer("cuisine.planificateur_repas")

            st.divider()

            # Générer le batch
            if planning_data:
                if st.button(
                    "🚀 Générer les instructions de batch", type="primary", use_container_width=True
                ):
                    avec_jules = type_info.get("avec_jules", False)

                    with st.spinner("🤖 L'IA génère vos instructions détaillées..."):
                        result = generer_batch_ia(
                            planning_data, st.session_state.batch_type, avec_jules
                        )

                        if result:
                            st.session_state.batch_data = result
                            st.success("✅ Instructions générées!")
                            rerun()
                        else:
                            st.error("❌ Impossible de générer les instructions")

    # ═══════════════════════════════════════════════════════
    # TAB: SESSION BATCH
    # ═══════════════════════════════════════════════════════

    with tab_session:
        with error_boundary(titre="Erreur session batch"):
            batch_data = st.session_state.get(SK.BATCH_DATA, {})

            if not batch_data:
                st.info("👆 Allez dans 'Préparer' et générez les instructions d'abord")
                return

            session_info = batch_data.get("session", {})
            recettes = batch_data.get("recettes", [])

            # Header session
            duree = session_info.get("duree_estimee_minutes", 120)
            heure_debut = st.session_state.get(SK.BATCH_HEURE, time(10, 0))
            heure_fin = estimer_heure_fin(heure_debut, duree)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("⏱️ Durée estimée", formater_duree(duree))

            with col2:
                st.metric("🕐 Début", heure_debut.strftime("%H:%M"))

            with col3:
                st.metric("🕐 Fin estimée", heure_fin.strftime("%H:%M"))

            # Conseils
            conseils = session_info.get("conseils_organisation", [])
            if conseils:
                with st.expander("💡 Conseils d'organisation", expanded=False):
                    for c in conseils:
                        st.markdown(f"• {c}")

            st.divider()

            # Timeline
            all_etapes = []
            for recette in recettes:
                for etape in recette.get("etapes_batch", []):
                    etape["recette"] = recette.get("nom", "")
                    all_etapes.append(etape)

            if all_etapes:
                afficher_timeline_session(all_etapes, heure_debut)

            st.divider()

            # Moments Jules
            moments_jules = batch_data.get("moments_jules", [])
            afficher_moments_jules(moments_jules)

            st.divider()

            # Recettes détaillées
            for recette in recettes:
                with st.expander(f"🍳 {recette.get('nom', 'Recette')}", expanded=False):
                    # Ingrédients
                    st.markdown("**Ingrédients:**")
                    for ing in recette.get("ingredients", []):
                        afficher_ingredient_detaille(ing, f"ing_{recette.get('nom', '')}")

                    st.divider()

                    # Étapes
                    st.markdown("**Étapes batch:**")
                    for i, etape in enumerate(recette.get("etapes_batch", []), 1):
                        afficher_etape_batch(etape, i, f"etape_{recette.get('nom', '')}")

                    # Stockage
                    st.info(
                        f"📦 Stockage: {recette.get('stockage', 'frigo').upper()} - {recette.get('duree_conservation_jours', 3)} jours max"
                    )

            st.divider()

            # Liste de courses
            liste_courses = batch_data.get("liste_courses", {})
            if liste_courses:
                afficher_liste_courses_batch(liste_courses)

            st.divider()

            # Actions
            col_act1, col_act2, col_act3 = st.columns(3)

            with col_act1:
                if st.button("🖨️ Imprimer les instructions", use_container_width=True):
                    try:
                        from src.modules.cuisine.planificateur_repas import (
                            generer_pdf_planning_session,
                        )

                        pdf_buf = generer_pdf_planning_session(
                            planning_data=batch_data,
                            date_debut=st.session_state.get("batch_date"),
                            conseils="",
                            suggestions_bio=[],
                        )
                        if pdf_buf:
                            st.download_button(
                                label="📥 Télécharger PDF",
                                data=pdf_buf,
                                file_name="batch_cooking.pdf",
                                mime="application/pdf",
                                use_container_width=True,
                            )
                        else:
                            st.warning("⚠️ Génération PDF impossible")
                    except Exception as e:
                        logger.error(f"Erreur export PDF batch: {e}")
                        st.error("❌ Erreur lors de l'export PDF")

            with col_act2:
                if st.button("🛒 Envoyer aux courses", use_container_width=True):
                    liste = batch_data.get("liste_courses", {})
                    if liste:
                        # Stocker la liste de courses dans session_state pour le module courses
                        st.session_state[SK.COURSES_DEPUIS_BATCH] = liste
                        st.success("✅ Liste envoyée ! Allez dans Courses pour la retrouver.")
                    else:
                        st.warning("⚠️ Aucune liste de courses à envoyer")

            with col_act3:
                if st.button("💾 Sauvegarder session", use_container_width=True):
                    st.success("✅ Session sauvegardée!")

    # ═══════════════════════════════════════════════════════
    # TAB: FINITIONS JOUR J
    # ═══════════════════════════════════════════════════════

    with tab_finitions:
        with error_boundary(titre="Erreur finitions jour J"):
            batch_data = st.session_state.get(SK.BATCH_DATA, {})
            recettes = batch_data.get("recettes", [])

            if not recettes:
                st.info("👆 Générez d'abord les instructions de batch")
                return

            st.markdown("##### 🗓️ Instructions de finition par jour")
            st.caption("Ce qu'il reste à faire le jour J")

            # Grouper par jour
            finitions_par_jour = {}
            for recette in recettes:
                for jour in recette.get("pour_jours", []):
                    if jour not in finitions_par_jour:
                        finitions_par_jour[jour] = []
                    finitions_par_jour[jour].append(recette)

            if finitions_par_jour:
                for jour in sorted(finitions_par_jour.keys()):
                    with st.expander(f"📅 {jour}", expanded=False):
                        for recette in finitions_par_jour[jour]:
                            afficher_finition_jour_j(recette)
            else:
                # Afficher toutes les recettes
                for recette in recettes:
                    with st.expander(f"🍽️ {recette.get('nom', 'Recette')}", expanded=False):
                        afficher_finition_jour_j(recette)
