"""
Module Planning Semaine - UI Refactorisée
Version simplifiée : 400 lignes max, logique externalisée
"""
import streamlit as st
import asyncio
from datetime import date, timedelta
from typing import Dict, List, Optional

from src.services.planning.planning_service import planning_service
from src.services.planning.planning_generation_service import create_planning_generation_service
from src.services.planning.repas_service import repas_service
from src.core.state_manager import StateManager, get_state
from src.core.database import get_db_context
from src.core.models import Recette, ConfigPlanningUtilisateur
from src.ui.components import (
    render_stat_row, render_empty_state, render_toast
)


# ===================================
# CONSTANTES
# ===================================

JOURS_SEMAINE = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]


# ===================================
# COMPOSANTS UI
# ===================================

def render_config_sidebar() -> ConfigPlanningUtilisateur:
    """Configuration dans la sidebar"""
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")

        config = planning_service.get_or_create_config()

        with st.expander("👥 Foyer", expanded=False):
            nb_adultes = st.number_input("Adultes", 1, 10, config.nb_adultes, key="cfg_adultes")
            nb_enfants = st.number_input("Enfants", 0, 10, config.nb_enfants, key="cfg_enfants")
            a_bebe = st.checkbox("Avec bébé", config.a_bebe, key="cfg_bebe")

        with st.expander("🍽️ Repas", expanded=True):
            repas_actifs = {}
            for key, label in {
                "petit_déjeuner": "Petit-déjeuner",
                "déjeuner": "Déjeuner",
                "dîner": "Dîner",
                "goûter": "Goûter"
            }.items():
                repas_actifs[key] = st.checkbox(
                    label,
                    config.repas_actifs.get(key, key in ["déjeuner", "dîner"]),
                    key=f"cfg_{key}"
                )

        with st.expander("🍳 Batch Cooking", expanded=False):
            batch_actif = st.checkbox("Activer", config.batch_cooking_actif, key="cfg_batch")

            jours_batch = []
            if batch_actif:
                st.caption("Jours de session :")
                for i, nom in enumerate(["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]):
                    if st.checkbox(nom, i in config.jours_batch, key=f"batch_{i}"):
                        jours_batch.append(i)

        if st.button("💾 Enregistrer", type="primary", use_container_width=True):
            planning_service.update_config({
                "nb_adultes": nb_adultes,
                "nb_enfants": nb_enfants,
                "a_bebe": a_bebe,
                "repas_actifs": repas_actifs,
                "batch_cooking_actif": batch_actif,
                "jours_batch": jours_batch
            })
            render_toast("✅ Configuration sauvegardée", "success")
            st.rerun()

        return config


def render_repas_card(repas: Dict, jour_idx: int, key: str):
    """Affiche une carte repas"""
    if not repas or not repas.get("recette"):
        # Slot vide
        if st.button("➕ Ajouter", key=f"add_{key}", use_container_width=True):
            StateManager.get().editing_repas_slot = (jour_idx, repas.get("type") if repas else "déjeuner")
            st.rerun()
        return

    recette = repas["recette"]

    with st.container():
        # Image + Nom
        col1, col2 = st.columns([1, 3])

        with col1:
            if recette.get("url_image"):
                st.image(recette["url_image"], use_container_width=True)

        with col2:
            st.markdown(f"**{recette['nom']}**")

            badges = []
            if repas.get("est_adapte_bebe"):
                badges.append("👶")
            if repas.get("est_batch"):
                badges.append("🍳")
            if badges:
                st.caption(" ".join(badges))

            st.caption(f"⏱️ {recette['temps_total']}min • {repas['portions']}p")

        # Actions rapides
        col_a1, col_a2, col_a3 = st.columns(3)

        with col_a1:
            if st.button("✏️", key=f"edit_{key}", help="Modifier"):
                StateManager.get().editing_repas_id = repas["id"]
                st.rerun()

        with col_a2:
            if st.button("🔄", key=f"move_{key}", help="Déplacer"):
                StateManager.get().moving_repas_id = repas["id"]
                st.rerun()

        with col_a3:
            if st.button("🗑️", key=f"del_{key}", help="Supprimer"):
                repas_service.supprimer_repas(repas["id"])
                render_toast("🗑️ Repas supprimé", "success")
                st.rerun()


def render_modal_edit_repas(repas_id: int):
    """Modal d'édition de repas"""
    repas = repas_service.get_repas_avec_details(repas_id)

    if not repas:
        st.error("Repas introuvable")
        return

    with st.form(f"edit_repas_{repas_id}"):
        st.markdown(f"### ✏️ Modifier {repas['type_repas']}")

        # Sélection recette
        with get_db_context() as db:
            recettes = db.query(Recette).order_by(Recette.nom).all()

        recette_names = [r.nom for r in recettes]
        current_idx = next(
            (i for i, r in enumerate(recettes) if r.id == repas["recette"]["id"]),
            0
        ) if repas.get("recette") else 0

        nouvelle_recette = st.selectbox("Recette", recette_names, index=current_idx)

        col1, col2 = st.columns(2)
        with col1:
            portions = st.number_input("Portions", 1, 12, repas["portions"])
        with col2:
            adapte_bebe = st.checkbox("Adapter bébé", repas["est_adapte_bebe"])

        notes = st.text_area("Notes", repas.get("notes", ""))

        col_btn1, col_btn2 = st.columns(2)

        with col_btn1:
            if st.form_submit_button("💾 Enregistrer", type="primary", use_container_width=True):
                nouvelle_recette_id = next(r.id for r in recettes if r.nom == nouvelle_recette)

                repas_service.modifier_repas(
                    repas_id,
                    recette_id=nouvelle_recette_id,
                    portions=portions,
                    est_adapte_bebe=adapte_bebe,
                    notes=notes
                )

                del StateManager.get().editing_repas_id
                render_toast("✅ Repas modifié", "success")
                st.rerun()

        with col_btn2:
            if st.form_submit_button("❌ Annuler", use_container_width=True):
                del StateManager.get().editing_repas_id
                st.rerun()


def render_modal_add_repas(jour_idx: int, type_repas: str, planning_id: int, date_jour: date):
    """Modal d'ajout de repas"""
    with st.form(f"add_repas_{jour_idx}_{type_repas}"):
        st.markdown(f"### ➕ Ajouter {type_repas}")

        with get_db_context() as db:
            recettes = db.query(Recette).order_by(Recette.nom).all()

        recette_select = st.selectbox("Recette", [r.nom for r in recettes])

        col1, col2 = st.columns(2)
        with col1:
            portions = st.number_input("Portions", 1, 12, 4)
        with col2:
            adapte_bebe = st.checkbox("Adapter bébé")

        col_btn1, col_btn2 = st.columns(2)

        with col_btn1:
            if st.form_submit_button("➕ Ajouter", type="primary", use_container_width=True):
                recette_id = next(r.id for r in recettes if r.nom == recette_select)

                repas_service.ajouter_repas(
                    planning_id=planning_id,
                    jour_semaine=jour_idx,
                    date_repas=date_jour,
                    type_repas=type_repas,
                    recette_id=recette_id,
                    portions=portions,
                    est_adapte_bebe=adapte_bebe
                )

                del StateManager.get().editing_repas_slot
                render_toast("✅ Repas ajouté", "success")
                st.rerun()

        with col_btn2:
            if st.form_submit_button("❌ Annuler", use_container_width=True):
                del StateManager.get().editing_repas_slot
                st.rerun()


# ===================================
# TABS
# ===================================

def tab_planning():
    """Tab 1: Planning actuel"""
    state = get_state()

    # Navigation semaine
    if "semaine_actuelle" not in st.session_state:
        st.session_state.semaine_actuelle = planning_service.get_semaine_debut()

    col1, col2, col3, col4 = st.columns([1, 2, 1, 1])

    with col1:
        if st.button("⬅️ Préc", use_container_width=True):
            st.session_state.semaine_actuelle -= timedelta(days=7)
            st.rerun()

    with col2:
        semaine = st.session_state.semaine_actuelle
        semaine_fin = semaine + timedelta(days=6)
        st.markdown(f"### {semaine.strftime('%d/%m')} — {semaine_fin.strftime('%d/%m/%Y')}")

    with col3:
        if st.button("Suiv ➡️", use_container_width=True):
            st.session_state.semaine_actuelle += timedelta(days=7)
            st.rerun()

    with col4:
        if st.button("📅 Aujourd'hui", use_container_width=True):
            st.session_state.semaine_actuelle = planning_service.get_semaine_debut()
            st.rerun()

    st.markdown("---")

    # Charger planning
    semaine_actuelle = st.session_state.semaine_actuelle
    planning = planning_service.get_planning_semaine(semaine_actuelle)

    if not planning:
        render_empty_state(
            message="Aucun planning pour cette semaine",
            icon="📅",
            action_label="✨ Générer avec l'IA",
            action_callback=lambda: st.session_state.update({"active_tab": 1})
        )
        return

    # Structure planning
    structure = planning_service.get_planning_structure(planning.id)

    # Stats
    total_repas = sum(len(j["repas"]) for j in structure["jours"])
    repas_bebe = sum(1 for j in structure["jours"] for r in j["repas"] if r["est_adapte_bebe"])

    stats_data = [
        {"label": "Repas planifiés", "value": total_repas},
        {"label": "Recettes uniques", "value": len(set(r["recette"]["nom"] for j in structure["jours"] for r in j["repas"] if r.get("recette")))},
        {"label": "Repas bébé", "value": repas_bebe}
    ]
    render_stat_row(stats_data, cols=3)

    st.markdown("---")

    # Actions globales
    col_act1, col_act2, col_act3 = st.columns(3)

    with col_act1:
        if planning.genere_par_ia:
            st.info("🤖 Planning IA")

    with col_act2:
        if st.button("🔄 Régénérer", use_container_width=True):
            st.session_state.regenerer_planning = True
            st.rerun()

    with col_act3:
        if st.button("🗑️ Supprimer", use_container_width=True):
            planning_service.delete_planning(planning.id)
            render_toast("🗑️ Planning supprimé", "success")
            st.rerun()

    st.markdown("---")

    # Vue tableau par jour
    config = planning_service.get_or_create_config()
    types_repas_actifs = [k for k, v in config.repas_actifs.items() if v]

    for jour_data in structure["jours"]:
        is_today = jour_data["date"] == date.today()

        with st.expander(
                f"{'🔵 ' if is_today else ''}{jour_data['nom_jour']} {jour_data['date'].strftime('%d/%m')}",
                expanded=is_today
        ):
            if not jour_data["repas"]:
                st.caption("Aucun repas planifié")
            else:
                for type_repas in types_repas_actifs:
                    repas = next((r for r in jour_data["repas"] if r["type"] == type_repas), None)

                    st.markdown(f"**{type_repas.replace('_', ' ').title()}**")
                    render_repas_card(
                        repas or {"type": type_repas},
                        jour_data["jour_idx"],
                        f"{jour_data['jour_idx']}_{type_repas}"
                    )

    # Modals
    if hasattr(state, 'editing_repas_id') and state.editing_repas_id:
        st.markdown("---")
        render_modal_edit_repas(state.editing_repas_id)

    if hasattr(state, 'editing_repas_slot') and state.editing_repas_slot:
        jour_idx, type_repas = state.editing_repas_slot
        date_jour = semaine_actuelle + timedelta(days=jour_idx)
        st.markdown("---")
        render_modal_add_repas(jour_idx, type_repas, planning.id, date_jour)


def tab_generation_ia():
    """Tab 2: Génération IA"""
    st.subheader("🤖 Génération Automatique")

    agent = get_state().agent_ia
    if not agent:
        st.error("❌ Agent IA non disponible")
        return

    config = planning_service.get_or_create_config()
    ai_service = create_planning_generation_service(agent)

    # Vérifier si régénération demandée
    if st.session_state.get("regenerer_planning"):
        semaine = st.session_state.semaine_actuelle

        with st.spinner("🤖 L'IA génère ton planning..."):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                result = loop.run_until_complete(
                    ai_service.generer_planning_complet(
                        semaine,
                        config
                    )
                )

                # Supprimer ancien planning
                planning_existant = planning_service.get_planning_semaine(semaine)
                if planning_existant:
                    planning_service.delete_planning(planning_existant.id)

                # Créer nouveau
                planning_id = planning_service.create_planning(semaine, f"Planning IA {semaine.strftime('%d/%m')}")

                # Ajouter repas
                with get_db_context() as db:
                    for jour in result.planning:
                        date_jour = semaine + timedelta(days=jour.jour)

                        for repas_data in jour.repas:
                            # Trouver recette
                            recette = db.query(Recette).filter(
                                Recette.nom.ilike(f"%{repas_data.recette_nom}%")
                            ).first()

                            if recette:
                                repas_service.ajouter_repas(
                                    planning_id=planning_id,
                                    jour_semaine=jour.jour,
                                    date_repas=date_jour,
                                    type_repas=repas_data.type,
                                    recette_id=recette.id,
                                    portions=repas_data.portions,
                                    est_adapte_bebe=repas_data.adapte_bebe,
                                    est_batch=repas_data.est_batch,
                                    notes=f"IA: {repas_data.raison}" if repas_data.raison else None,
                                    db=db
                                )

                # Marquer comme IA
                with get_db_context() as db:
                    planning = db.query(PlanningHebdomadaire).get(planning_id)
                    if planning:
                        planning.genere_par_ia = True
                        db.commit()

                del st.session_state.regenerer_planning
                render_toast("✅ Planning généré !", "success")
                st.balloons()
                st.rerun()

            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")
                del st.session_state.regenerer_planning

    else:
        st.info("💡 Génère automatiquement un planning équilibré pour la semaine")

        if st.button("✨ Générer Planning", type="primary", use_container_width=True):
            st.session_state.regenerer_planning = True
            st.rerun()


def tab_stats():
    """Tab 3: Statistiques"""
    st.subheader("📊 Statistiques")

    semaine = st.session_state.get("semaine_actuelle", planning_service.get_semaine_debut())
    planning = planning_service.get_planning_semaine(semaine)

    if not planning:
        st.info("Aucun planning pour calculer les stats")
        return

    structure = planning_service.get_planning_structure(planning.id)

    # Calculs
    total_repas = sum(len(j["repas"]) for j in structure["jours"])
    temps_total = sum(
        r["recette"]["temps_total"]
        for j in structure["jours"]
        for r in j["repas"]
        if r.get("recette")
    )

    stats_data = [
        {"label": "Total repas", "value": total_repas},
        {"label": "Temps cuisine", "value": f"{temps_total}min", "delta": f"{temps_total // 60}h"},
    ]
    render_stat_row(stats_data, cols=2)

    st.markdown("---")

    # Répartition par jour
    st.markdown("### 📅 Répartition")

    for jour in structure["jours"]:
        nb = len(jour["repas"])
        st.write(f"**{jour['nom_jour']}** : {nb} repas")


# ===================================
# MODULE PRINCIPAL
# ===================================

def app():
    """Point d'entrée du module Planning"""
    st.title("🗓️ Planning Hebdomadaire")
    st.caption("Génération IA, organisation intuitive")

    # Config sidebar
    render_config_sidebar()

    # Tabs
    tab1, tab2, tab3 = st.tabs([
        "📅 Planning",
        "🤖 Génération IA",
        "📊 Statistiques"
    ])

    with tab1:
        tab_planning()

    with tab2:
        tab_generation_ia()

    with tab3:
        tab_stats()