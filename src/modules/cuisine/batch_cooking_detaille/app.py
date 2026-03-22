"""Point d'entrée principal du module Batch Cooking Détaillé."""

import logging
from datetime import date, time, timedelta

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.core.session_keys import SK
from src.core.state import rerun
from src.modules._framework import avec_gestion_erreurs_ui, error_boundary
from src.modules.cuisine.batch_cooking_temps import estimer_heure_fin, formater_duree
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
from .execution_live import afficher_execution_live
from .generation import generer_batch_ia

logger = logging.getLogger(__name__)


def _get_user_robots() -> list[str]:
    """Récupère les robots de l'utilisateur depuis les préférences."""
    from src.modules.cuisine.planificateur_repas.preferences import charger_preferences

    prefs = charger_preferences()
    return prefs.robots if prefs.robots else ["four", "plaques"]


def _generer_texte_batch(batch_data: dict, is_multi: bool) -> str:
    """Génère un texte imprimable des instructions de batch cooking."""
    lines: list[str] = ["🍳 INSTRUCTIONS BATCH COOKING", "=" * 50, ""]

    sessions_to_process = []
    if is_multi:
        for key in ("session_1", "session_2"):
            s = batch_data.get(key, {})
            if s:
                sessions_to_process.append((key, s))
    else:
        sessions_to_process.append(("session", batch_data))

    for session_label, session_data in sessions_to_process:
        info = session_data.get("session", {})
        if info.get("duree_estimee_minutes"):
            lines.append(f"⏱️ Durée estimée: {info['duree_estimee_minutes']} min")
        for c in info.get("conseils_organisation", []):
            lines.append(f"  💡 {c}")
        lines.append("")

        for recette in session_data.get("recettes", []):
            lines.append(f"━━━ {recette.get('nom', '?')} ━━━")
            lines.append(f"  Pour: {', '.join(recette.get('pour_jours', []))}")
            lines.append(f"  Portions: {recette.get('portions', '?')}")
            lines.append("")

            lines.append("  INGRÉDIENTS:")
            for ing in recette.get("ingredients", []):
                q = ing.get("quantite", "")
                d = f" ({ing.get('decoupe', '')})" if ing.get("decoupe") else ""
                lines.append(f"    • {ing.get('nom', '?')} {q}{d}")
            lines.append("")

            lines.append("  ÉTAPES BATCH:")
            for i, etape in enumerate(recette.get("etapes_batch", []), 1):
                robot = f" [{etape.get('robot', '')}]" if etape.get("robot") else ""
                dur = f" ({etape.get('duree_minutes', '?')} min)" if etape.get("duree_minutes") else ""
                lines.append(f"    {i}. {etape.get('titre', '?')}{robot}{dur}")
                if etape.get("detail"):
                    lines.append(f"       → {etape['detail']}")
                if etape.get("tache_jules"):
                    lines.append(f"       👶 Jules: {etape['tache_jules']}")
            lines.append("")

            lines.append("  FINITIONS JOUR J:")
            for fin in recette.get("instructions_finition", []):
                lines.append(f"    → {fin}")
            stockage = recette.get("stockage", "")
            conservation = recette.get("duree_conservation_jours", "")
            if stockage:
                lines.append(f"  📦 Stockage: {stockage} ({conservation}j)")
            lines.append("")

    return "\n".join(lines)


# Session keys scopées
_keys = KeyNamespace("batch_cooking")


@profiler_rerun("batch_cooking")
def app():
    """Point d'entrée du module Batch Cooking Détaillé."""

    st.title("🍳 Batch Cooking")
    st.caption("Préparez vos repas de la semaine en une session efficace")

    # Initialiser la session
    if SK.BATCH_TYPE not in st.session_state:
        st.session_state[SK.BATCH_TYPE] = "dimanche"

    if SK.BATCH_DATA not in st.session_state:
        st.session_state[SK.BATCH_DATA] = {}

    # Récupérer le planning (depuis le planificateur de repas)
    planning_data = st.session_state.get(SK.PLANNING_DATA, {})

    # Tabs avec deep linking URL
    TAB_LABELS = [
        "📋 Préparer",
        "👩‍🍳 Session Batch",
        "\U0001f9d1\u200d🍳 Exécution Live",
        "🍽️ Finitions Jour J",
        "🧊 Congélation",
    ]
    tab_index = tabs_with_url(TAB_LABELS, param="tab")
    tab_preparer, tab_session, tab_execution, tab_finitions, tab_congelation = st.tabs(TAB_LABELS)

    # ═══════════════════════════════════════════════════════
    # TAB: PRÉPARER
    # ═══════════════════════════════════════════════════════

    with tab_preparer:
        with error_boundary(titre="Erreur préparation batch"):
            # Sélection du type de session
            afficher_selecteur_session()

            st.divider()

            # Infos session
            type_info = TYPES_SESSION.get(st.session_state[SK.BATCH_TYPE], {})

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

            st.session_state[SK.BATCH_DATE] = date_batch
            st.session_state[SK.BATCH_HEURE] = heure_batch

            st.divider()

            # Configuration multi-sessions
            st.markdown("##### ⚙️ Sessions de batch cooking")
            col_sess1, col_sess2 = st.columns(2)
            with col_sess1:
                nb_sessions = st.radio(
                    "Nombre de sessions",
                    [1, 2],
                    index=st.session_state.get(SK.BATCH_NB_SESSIONS, 1) - 1,
                    horizontal=True,
                    key="batch_nb_sessions_radio",
                )
                st.session_state[SK.BATCH_NB_SESSIONS] = nb_sessions

            jours = ["dimanche", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"]
            if nb_sessions == 2:
                with col_sess2:
                    c1, c2 = st.columns(2)
                    with c1:
                        j1 = st.selectbox(
                            "Session 1",
                            jours,
                            index=jours.index(
                                st.session_state.get(SK.BATCH_JOUR_SESSION_1, "dimanche")
                            ),
                            key="batch_jour_s1",
                        )
                        st.session_state[SK.BATCH_JOUR_SESSION_1] = j1
                    with c2:
                        j2 = st.selectbox(
                            "Session 2",
                            jours,
                            index=jours.index(
                                st.session_state.get(SK.BATCH_JOUR_SESSION_2, "mercredi")
                            ),
                            key="batch_jour_s2",
                        )
                        st.session_state[SK.BATCH_JOUR_SESSION_2] = j2

            st.divider()

            # Preview du planning avec sélection
            st.markdown("##### 📋 Recettes du planning")

            if planning_data:
                afficher_planning_semaine_preview(planning_data)
            else:
                st.warning("⚠️ Aucun planning de repas trouvé.")
                if st.button("📅 Aller au planificateur de repas"):
                    from src.core.state import naviguer

                    naviguer("cuisine_repas")

            st.divider()

            # Générer le batch (filtrer selon sélection)
            if planning_data:
                selection = st.session_state.get(SK.BATCH_SELECTION, {})
                assignment = st.session_state.get(SK.BATCH_SESSION_ASSIGNMENT, {})
                nb_sessions = st.session_state.get(SK.BATCH_NB_SESSIONS, 1)

                def _filtrer_planning(
                    sel: dict, planning: dict, session_num: int | None = None
                ) -> dict:
                    """Filtre le planning_data selon la sélection et la session."""
                    filtered = {}
                    for jour, repas in planning.items():
                        jour_filtered = {}
                        for tr in ["midi", "soir"]:
                            key = f"{jour}_{tr}"
                            is_selected = sel.get(key, True)
                            if is_selected:
                                if session_num is not None:
                                    if assignment.get(key, 1) != session_num:
                                        continue
                                meal = repas.get(tr)
                                if meal and isinstance(meal, dict):
                                    jour_filtered[tr] = meal
                        if jour_filtered:
                            filtered[jour] = jour_filtered
                    return filtered

                if nb_sessions == 1:
                    if st.button(
                        "🚀 Générer les instructions de batch",
                        type="primary",
                        use_container_width=True,
                    ):
                        avec_jules = type_info.get("avec_jules", False)
                        filtered_data = _filtrer_planning(selection, planning_data)

                        with st.spinner("🤖 L'IA génère vos instructions détaillées..."):
                            result = generer_batch_ia(
                                filtered_data, st.session_state[SK.BATCH_TYPE], avec_jules,
                                robots_user=_get_user_robots(),
                            )

                            if result:
                                st.session_state[SK.BATCH_DATA] = result
                                st.success("✅ Instructions générées!")
                                rerun()
                            else:
                                st.error(
                                    "❌ Impossible de générer les instructions. "
                                    "Réessaie ou réduis à 2-3 recettes."
                                )
                else:
                    col_gen1, col_gen2 = st.columns(2)
                    j1 = st.session_state.get(SK.BATCH_JOUR_SESSION_1, "dimanche")
                    j2 = st.session_state.get(SK.BATCH_JOUR_SESSION_2, "mercredi")
                    with col_gen1:
                        if st.button(
                            f"🚀 Générer Session 1 ({j1})",
                            type="primary",
                            use_container_width=True,
                        ):
                            avec_jules = type_info.get("avec_jules", False)
                            filtered_s1 = _filtrer_planning(selection, planning_data, session_num=1)

                            with st.spinner(f"🤖 Génération session 1 ({j1})..."):
                                result = generer_batch_ia(
                                    filtered_s1, st.session_state[SK.BATCH_TYPE], avec_jules,
                                    robots_user=_get_user_robots(),
                                )
                                if result:
                                    batch_data_all = st.session_state.get(SK.BATCH_DATA, {})
                                    if (
                                        not isinstance(batch_data_all, dict)
                                        or "session_1" not in batch_data_all
                                    ):
                                        batch_data_all = {}
                                    batch_data_all["session_1"] = result
                                    st.session_state[SK.BATCH_DATA] = batch_data_all
                                    st.success("✅ Session 1 générée!")
                                    rerun()
                                else:
                                    st.error(
                                        "❌ Impossible de générer la session 1. "
                                        "Réessaie ou réduis le nombre de recettes."
                                    )

                    with col_gen2:
                        if st.button(
                            f"🚀 Générer Session 2 ({j2})",
                            type="primary",
                            use_container_width=True,
                        ):
                            avec_jules = type_info.get("avec_jules", False)
                            filtered_s2 = _filtrer_planning(selection, planning_data, session_num=2)

                            with st.spinner(f"🤖 Génération session 2 ({j2})..."):
                                result = generer_batch_ia(
                                    filtered_s2, st.session_state[SK.BATCH_TYPE], avec_jules,
                                    robots_user=_get_user_robots(),
                                )
                                if result:
                                    batch_data_all = st.session_state.get(SK.BATCH_DATA, {})
                                    if (
                                        not isinstance(batch_data_all, dict)
                                        or "session_1" not in batch_data_all
                                    ):
                                        batch_data_all = {}
                                    batch_data_all["session_2"] = result
                                    st.session_state[SK.BATCH_DATA] = batch_data_all
                                    st.success("✅ Session 2 générée!")
                                    rerun()
                                else:
                                    st.error(
                                        "❌ Impossible de générer la session 2. "
                                        "Réessaie ou réduis le nombre de recettes."
                                    )

    # ═══════════════════════════════════════════════════════
    # TAB: SESSION BATCH
    # ═══════════════════════════════════════════════════════

    with tab_session:
        with error_boundary(titre="Erreur session batch"):
            batch_data = st.session_state.get(SK.BATCH_DATA, {})

            if not batch_data:
                st.info("👆 Allez dans 'Préparer' et générez les instructions d'abord")
            else:
                # Détecter format multi-sessions
                is_multi = "session_1" in batch_data or "session_2" in batch_data

                if is_multi:
                    sessions_to_show = []
                    if batch_data.get("session_1"):
                        j1 = st.session_state.get(SK.BATCH_JOUR_SESSION_1, "dimanche")
                        sessions_to_show.append((f"Session 1 ({j1})", batch_data["session_1"]))
                    if batch_data.get("session_2"):
                        j2 = st.session_state.get(SK.BATCH_JOUR_SESSION_2, "mercredi")
                        sessions_to_show.append((f"Session 2 ({j2})", batch_data["session_2"]))
                else:
                    sessions_to_show = [("Session", batch_data)]

                for session_label, session_data in sessions_to_show:
                    if len(sessions_to_show) > 1:
                        st.subheader(f"🍳 {session_label}")

                    session_info = session_data.get("session", {})
                    recettes = session_data.get("recettes", [])

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
                    moments_jules = session_data.get("moments_jules", [])
                    afficher_moments_jules(moments_jules)

                    st.divider()

                    # Recettes détaillées
                    safe_label = session_label.replace(" ", "_").replace("(", "").replace(")", "")
                    for recette in recettes:
                        with st.expander(f"🍳 {recette.get('nom', 'Recette')}", expanded=False):
                            # Ingrédients
                            st.markdown("**Ingrédients:**")
                            for ing in recette.get("ingredients", []):
                                afficher_ingredient_detaille(
                                    ing, f"ing_{safe_label}_{recette.get('nom', '')}"
                                )

                            st.divider()

                            # Étapes
                            st.markdown("**Étapes batch:**")
                            for i, etape in enumerate(recette.get("etapes_batch", []), 1):
                                afficher_etape_batch(
                                    etape, i, f"etape_{safe_label}_{recette.get('nom', '')}"
                                )

                            # Stockage
                            st.info(
                                f"📦 Stockage: {recette.get('stockage', 'frigo').upper()} - {recette.get('duree_conservation_jours', 3)} jours max"
                            )

                    st.divider()

                    # Liste de courses
                    liste_courses = session_data.get("liste_courses", {})
                    if liste_courses:
                        afficher_liste_courses_batch(liste_courses)

                    st.divider()

                # Actions (après la boucle de sessions)
                col_act1, col_act2, col_act3 = st.columns(3)

                with col_act1:
                    if st.button("🖨️ Imprimer les instructions", use_container_width=True):
                        try:
                            texte = _generer_texte_batch(batch_data, is_multi)
                            if texte:
                                st.download_button(
                                    label="📥 Télécharger les instructions",
                                    data=texte.encode("utf-8"),
                                    file_name="batch_cooking_instructions.txt",
                                    mime="text/plain",
                                    use_container_width=True,
                                )
                            else:
                                st.warning("⚠️ Aucune instruction à exporter")
                        except Exception as e:
                            logger.error(f"Erreur export batch: {e}")
                            st.error("❌ Erreur lors de l'export")

                with col_act2:
                    if st.button("🛒 Envoyer aux courses", use_container_width=True):
                        # Collecter les listes de courses de toutes les sessions
                        if is_multi:
                            liste = {}
                            for s_data in [
                                batch_data.get("session_1", {}),
                                batch_data.get("session_2", {}),
                            ]:
                                if s_data:
                                    liste.update(s_data.get("liste_courses", {}))
                        else:
                            liste = batch_data.get("liste_courses", {})
                        if liste:
                            st.session_state[SK.COURSES_DEPUIS_BATCH] = liste
                            st.success("✅ Liste envoyée ! Allez dans Courses pour la retrouver.")
                        else:
                            st.warning("⚠️ Aucune liste de courses à envoyer")

                with col_act3:
                    if st.button("💾 Sauvegarder session", use_container_width=True):
                        st.success("✅ Session sauvegardée!")

    # ═══════════════════════════════════════════════════════
    # TAB: EXÉCUTION LIVE (avec st.status)
    # ═══════════════════════════════════════════════════════

    with tab_execution:
        with error_boundary(titre="Erreur exécution live"):
            afficher_execution_live()

    # ═══════════════════════════════════════════════════════
    # TAB: FINITIONS JOUR J
    # ═══════════════════════════════════════════════════════

    with tab_finitions:
        with error_boundary(titre="Erreur finitions jour J"):
            batch_data = st.session_state.get(SK.BATCH_DATA, {})
            recettes = batch_data.get("recettes", [])

            if not recettes:
                st.info("👆 Générez d'abord les instructions de batch")
            else:
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

    # ═══════════════════════════════════════════════════════
    # TAB: CONGÉLATION
    # ═══════════════════════════════════════════════════════

    with tab_congelation:
        with error_boundary(titre="Erreur congélation"):
            from .congelation_ui import afficher_congelation

            afficher_congelation()
