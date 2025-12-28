"""
Module Planning Semaine - VERSION 3.0 REFACTORISÉE
Intègre tous les refactoring core/ui/utils
"""
import streamlit as st
import asyncio
from datetime import date, timedelta
from typing import Dict, List, Optional

# ═══════════════════════════════════════════════════════════════
# IMPORTS REFACTORISÉS
# ═══════════════════════════════════════════════════════════════

# Core
from src.core.state import StateManager, get_state
from src.core.cache import Cache
from src.core.errors import handle_errors
from src.core.database import get_db_context
from src.core.models import Recette, PlanningHebdomadaire

# UI - Namespace unifié
from src.ui import (
    # Base
    empty_state,
    # Forms
    date_selector,
    # Data
    metrics_row,
    # Feedback
    toast, Modal,
    # Layouts
    timeline
)

# Services
from src.services.planning import (
    planning_service,
    create_planning_generation_service,
    repas_service
)

# Utils
from src.utils import format_date, get_week_bounds


# Constantes
JOURS_SEMAINE = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

TYPES_REPAS = {
    "petit_déjeuner": {"icone": "🌅", "ordre": 1},
    "déjeuner": {"icone": "☀️", "ordre": 2},
    "goûter": {"icone": "🍪", "ordre": 3},
    "dîner": {"icone": "🌙", "ordre": 4},
}


# ═══════════════════════════════════════════════════════════════
# SIDEBAR CONFIGURATION
# ═══════════════════════════════════════════════════════════════

def render_config_sidebar() -> Dict:
    """Configuration dans sidebar"""
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")

        config = planning_service.get_or_create_config()

        # Foyer
        with st.expander("👥 Foyer", expanded=True):
            nb_adultes = st.number_input("Adultes", 1, 10, config.nb_adultes)
            nb_enfants = st.number_input("Enfants", 0, 10, config.nb_enfants)
            a_bebe = st.toggle("👶 Bébé", value=config.a_bebe)

        # Repas
        with st.expander("🍽️ Repas"):
            repas_actifs = {}
            for type_repas, info in TYPES_REPAS.items():
                default = config.repas_actifs.get(
                    type_repas,
                    type_repas in ["déjeuner", "dîner"]
                )
                repas_actifs[type_repas] = st.checkbox(
                    f"{info['icone']} {type_repas.replace('_', ' ').title()}",
                    value=default,
                    key=f"cfg_{type_repas}"
                )

        # Batch
        with st.expander("🍳 Batch"):
            batch_actif = st.toggle("Actif", value=config.batch_cooking_actif)
            jours_batch = []

            if batch_actif:
                st.caption("Jours de préparation:")
                for i, jour in enumerate(JOURS_SEMAINE):
                    if st.checkbox(
                            jour[:3],
                            value=i in config.jours_batch,
                            key=f"batch_{i}"
                    ):
                        jours_batch.append(i)

        st.markdown("---")

        if st.button("💾 Enregistrer", type="primary", use_container_width=True):
            planning_service.update_config({
                "nb_adultes": nb_adultes,
                "nb_enfants": nb_enfants,
                "a_bebe": a_bebe,
                "repas_actifs": repas_actifs,
                "batch_cooking_actif": batch_actif,
                "jours_batch": jours_batch if batch_actif else [],
            })
            toast("✅ Sauvegardé", "success")
            Cache.invalidate("planning")
            st.rerun()

        return config


# ═══════════════════════════════════════════════════════════════
# TAB 1 : PLANNING ACTUEL
# ═══════════════════════════════════════════════════════════════

@handle_errors(show_in_ui=True)
def tab_planning():
    """Tab Planning - REFACTORISÉ"""
    st.subheader("📋 Mon Planning")

    # ✅ Sélecteur semaine
    if "semaine_actuelle" not in st.session_state:
        st.session_state.semaine_actuelle = planning_service.get_semaine_debut()

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("⬅️ Semaine préc.", use_container_width=True):
            st.session_state.semaine_actuelle -= timedelta(days=7)
            st.rerun()

    with col2:
        semaine = date_selector(
            label="Semaine du",
            default=st.session_state.semaine_actuelle,
            key="week_selector"
        )

        if semaine != st.session_state.semaine_actuelle:
            st.session_state.semaine_actuelle = planning_service.get_semaine_debut(semaine)
            st.rerun()

    with col3:
        if st.button("Semaine suiv. ➡️", use_container_width=True):
            st.session_state.semaine_actuelle += timedelta(days=7)
            st.rerun()

    st.markdown("---")

    # Charger planning
    @Cache.cached(ttl=60)
    def load_planning(semaine_debut):
        return planning_service.get_planning_semaine(semaine_debut)

    planning = load_planning(st.session_state.semaine_actuelle)

    if not planning:
        empty_state(
            message="Aucun planning pour cette semaine",
            icon="📅",
            subtext="Génère un planning avec l'IA"
        )

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("✨ Générer IA", type="primary", use_container_width=True):
                st.session_state.active_tab = 1
                st.rerun()

        with col_b:
            if st.button("➕ Planning vide", use_container_width=True):
                _create_empty_planning(st.session_state.semaine_actuelle)

        return

    # Structure planning
    structure = planning_service.get_planning_structure(planning.id)
    config = planning_service.get_or_create_config()

    # ✅ Stats
    stats = {
        "total_repas": sum(len(j["repas"]) for j in structure["jours"]),
        "repas_bebe": sum(
            1 for j in structure["jours"]
            for r in j["repas"]
            if r.get("est_adapte_bebe")
        ),
        "repas_batch": sum(
            1 for j in structure["jours"]
            for r in j["repas"]
            if r.get("est_batch")
        )
    }

    metrics_row([
        {"label": "Repas", "value": stats["total_repas"]},
        {"label": "Bébé", "value": stats["repas_bebe"]},
        {"label": "Batch", "value": stats["repas_batch"]}
    ], cols=3)

    st.markdown("---")

    # ✅ Timeline par jour
    types_repas_actifs = [k for k, v in config.repas_actifs.items() if v]

    for jour_data in structure["jours"]:
        is_today = jour_data["date"] == date.today()

        with st.expander(
                f"{'🔵 ' if is_today else ''}{jour_data['nom_jour']} {format_date(jour_data['date'], 'short')}",
                expanded=is_today
        ):
            # Préparer events pour timeline
            events = []

            for type_repas in types_repas_actifs:
                repas = next((r for r in jour_data["repas"] if r["type"] == type_repas), None)

                if repas and repas.get("recette"):
                    status = "completed" if repas.get("statut") == "terminé" else "current"

                    events.append({
                        "title": f"{TYPES_REPAS[type_repas]['icone']} {repas['recette']['nom']}",
                        "description": f"{repas['portions']}p",
                        "icon": TYPES_REPAS[type_repas]['icone'],
                        "status": status
                    })

            # ✅ Timeline
            if events:
                timeline(events, key=f"timeline_{jour_data['jour_idx']}")
            else:
                st.info("Aucun repas planifié")

            # Actions
            col_a, col_b = st.columns(2)

            with col_a:
                if st.button(
                        "➕ Ajouter repas",
                        key=f"add_{jour_data['jour_idx']}",
                        use_container_width=True
                ):
                    st.session_state.adding_repas = {
                        "planning_id": planning.id,
                        "jour_idx": jour_data["jour_idx"],
                        "date": jour_data["date"]
                    }
                    st.rerun()

            with col_b:
                if st.button(
                        "🗑️ Supprimer planning",
                        key=f"del_plan_{jour_data['jour_idx']}",
                        use_container_width=True
                ):
                    _delete_planning(planning.id)

    # Modal ajout repas
    if hasattr(st.session_state, "adding_repas"):
        _render_modal_add_repas()


# ═══════════════════════════════════════════════════════════════
# TAB 2 : GÉNÉRATION IA
# ═══════════════════════════════════════════════════════════════

@handle_errors(show_in_ui=True)
def tab_generation_ia():
    """Tab Génération IA - REFACTORISÉ"""
    st.subheader("🤖 Génération Automatique")

    agent = get_state().agent_ia
    if not agent:
        st.error("❌ Agent IA indisponible")
        return

    config = planning_service.get_or_create_config()

    # Vérifier recettes
    with get_db_context() as db:
        nb_recettes = db.query(Recette).count()

    if nb_recettes < 5:
        st.warning(f"⚠️ {nb_recettes} recette(s) - Il en faut au moins 5")
        return

    st.info(f"💡 {nb_recettes} recettes disponibles")

    # Résumé config
    with st.expander("📋 Configuration"):
        st.write(f"👥 {config.nb_adultes} adultes, {config.nb_enfants} enfants")
        if config.a_bebe:
            st.write("👶 Mode bébé")
        if config.batch_cooking_actif:
            st.write(f"🍳 Batch jours: {', '.join([JOURS_SEMAINE[j] for j in config.jours_batch])}")

    st.markdown("---")

    # Génération
    semaine = st.session_state.get(
        "semaine_actuelle",
        planning_service.get_semaine_debut()
    )

    if st.button("✨ Générer Planning", type="primary", use_container_width=True):
        with st.spinner("🤖 Génération..."):
            try:
                ai_service = create_planning_generation_service(agent)

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                result = loop.run_until_complete(
                    ai_service.generer_planning_complet(semaine, config, None)
                )

                # Supprimer ancien
                existing = planning_service.get_planning_semaine(semaine)
                if existing:
                    planning_service.delete_planning(existing.id)

                # Créer nouveau
                planning_id = planning_service.create_planning(
                    semaine,
                    f"Planning IA {format_date(semaine, 'short')}"
                )

                # Ajouter repas
                with get_db_context() as db:
                    for jour_planning in result.planning:
                        date_jour = semaine + timedelta(days=jour_planning.jour)

                        for repas_data in jour_planning.repas:
                            recette = db.query(Recette).filter(
                                Recette.nom.ilike(f"%{repas_data.recette_nom}%")
                            ).first()

                            if recette:
                                repas_service.ajouter_repas(
                                    planning_id=planning_id,
                                    jour_semaine=jour_planning.jour,
                                    date_repas=date_jour,
                                    type_repas=repas_data.type,
                                    recette_id=recette.id,
                                    portions=repas_data.portions,
                                    est_adapte_bebe=repas_data.adapte_bebe,
                                    est_batch=repas_data.est_batch,
                                    db=db
                                )

                    # Marquer IA
                    planning = db.query(PlanningHebdomadaire).get(planning_id)
                    if planning:
                        planning.genere_par_ia = True
                        db.commit()

                toast("✅ Planning généré !", "success")
                Cache.invalidate("planning")
                st.balloons()
                st.rerun()

            except Exception as e:
                st.error(f"❌ {str(e)}")


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _create_empty_planning(semaine: date):
    """Crée planning vide"""
    try:
        planning_service.create_planning(semaine, f"Planning {format_date(semaine, 'short')}")
        toast("✅ Planning créé", "success")
        Cache.invalidate("planning")
        st.rerun()
    except Exception as e:
        st.error(f"❌ {str(e)}")


def _delete_planning(planning_id: int):
    """Supprime planning avec confirmation"""
    modal = Modal(f"del_planning_{planning_id}")

    if modal.is_showing():
        st.warning("⚠️ Supprimer ce planning ?")

        if modal.confirm():
            try:
                planning_service.delete_planning(planning_id)
                toast("🗑️ Planning supprimé", "success")
                Cache.invalidate("planning")
                modal.close()
            except Exception as e:
                st.error(f"❌ {str(e)}")

        modal.cancel()


def _render_modal_add_repas():
    """Modal ajout repas"""
    if not hasattr(st.session_state, "adding_repas"):
        return

    slot = st.session_state.adding_repas

    st.markdown("---")
    st.markdown("### ➕ Ajouter un repas")

    # Sélection recette
    with get_db_context() as db:
        recettes = db.query(Recette).order_by(Recette.nom).all()

    if not recettes:
        st.error("Aucune recette")
        if st.button("Annuler"):
            del st.session_state.adding_repas
            st.rerun()
        return

    recette_id = st.selectbox(
        "Recette",
        options=[r.id for r in recettes],
        format_func=lambda x: next(r.nom for r in recettes if r.id == x)
    )

    recette = next(r for r in recettes if r.id == recette_id)

    col1, col2 = st.columns(2)

    with col1:
        type_repas = st.selectbox("Type", list(TYPES_REPAS.keys()))
        portions = st.number_input("Portions", 1, 20, recette.portions)

    with col2:
        adapte_bebe = st.checkbox("👶 Adapter bébé")

    col_a, col_b = st.columns(2)

    with col_a:
        if st.button("✅ Ajouter", type="primary", use_container_width=True):
            try:
                repas_service.ajouter_repas(
                    planning_id=slot["planning_id"],
                    jour_semaine=slot["jour_idx"],
                    date_repas=slot["date"],
                    type_repas=type_repas,
                    recette_id=recette_id,
                    portions=portions,
                    est_adapte_bebe=adapte_bebe
                )

                del st.session_state.adding_repas
                toast(f"✅ {recette.nom} ajouté", "success")
                Cache.invalidate("planning")
                st.rerun()

            except Exception as e:
                st.error(f"❌ {str(e)}")

    with col_b:
        if st.button("❌ Annuler", use_container_width=True):
            del st.session_state.adding_repas
            st.rerun()


# ═══════════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════════

def app():
    """Point d'entrée - VERSION REFACTORISÉE"""
    st.title("🗓️ Planning Hebdomadaire")
    st.caption("IA • Batch cooking • Mode bébé")

    # Config sidebar
    render_config_sidebar()

    # Tabs
    tab1, tab2 = st.tabs(["📅 Mon Planning", "🤖 Générer IA"])

    with tab1:
        tab_planning()

    with tab2:
        tab_generation_ia()