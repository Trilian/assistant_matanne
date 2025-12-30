"""
Module Planning Semaine
"""
import streamlit as st
import asyncio
from datetime import date, timedelta
from typing import Dict, List

# Core
from src.core.state import StateManager, get_state
from src.core.cache import Cache
from src.core.errors import handle_errors
from src.core.database import get_db_context
from src.core.models import Recette, PlanningHebdomadaire

# UI Composants Domaine
from src.ui.domain import (
    meal_card,
    week_calendar,
    meal_timeline,
    planning_stats,
    week_selector,
    meal_form
)

# UI Composants Génériques
from src.ui import empty_state, toast, Modal

# Services
from src.services.planning import (
    planning_service,
    create_planning_generation_service,
    repas_service
)

# Utils
from src.utils import format_date


JOURS_SEMAINE = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]


# ═══════════════════════════════════════════════════════════════
# SIDEBAR CONFIG
# ═══════════════════════════════════════════════════════════════

def render_config_sidebar():
    """Configuration dans sidebar"""
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")

        config = planning_service.get_or_create_config()

        # Foyer
        with st.expander("👥 Foyer", expanded=True):
            nb_adultes = st.number_input("Adultes", 1, 10, config.nb_adultes)
            nb_enfants = st.number_input("Enfants", 0, 10, config.nb_enfants)
            a_bebe = st.toggle("👶 Bébé", value=config.a_bebe)

        # Repas actifs
        with st.expander("🍽️ Repas"):
            repas_actifs = {}
            for type_r in ["petit_déjeuner", "déjeuner", "goûter", "dîner"]:
                repas_actifs[type_r] = st.checkbox(
                    type_r.replace("_", " ").title(),
                    value=config.repas_actifs.get(type_r, type_r in ["déjeuner", "dîner"]),
                    key=f"cfg_{type_r}"
                )

        # Batch
        with st.expander("🍳 Batch"):
            batch_actif = st.toggle("Actif", value=config.batch_cooking_actif)
            jours_batch = []

            if batch_actif:
                st.caption("Jours:")
                for i, jour in enumerate(JOURS_SEMAINE):
                    if st.checkbox(jour[:3], value=i in config.jours_batch, key=f"batch_{i}"):
                        jours_batch.append(i)

        st.markdown("---")

        if st.button("💾 Enregistrer", type="primary", use_container_width=True):
            planning_service.update_config({
                "nb_adultes": nb_adultes,
                "nb_enfants": nb_enfants,
                "a_bebe": a_bebe,
                "repas_actifs": repas_actifs,
                "batch_cooking_actif": batch_actif,
                "jours_batch": jours_batch if batch_actif else []
            })
            toast("✅ Sauvegardé", "success")
            Cache.invalidate("planning")
            st.rerun()


# ═══════════════════════════════════════════════════════════════
# TAB 1 : PLANNING
# ═══════════════════════════════════════════════════════════════

@handle_errors(show_in_ui=True)
def tab_planning():
    """Tab Mon Planning"""
    st.subheader("📋 Mon Planning")

    # Sélecteur semaine
    if "semaine_actuelle" not in st.session_state:
        st.session_state.semaine_actuelle = planning_service.get_semaine_debut()

    week_selector(
        st.session_state.semaine_actuelle,
        on_change=lambda w: _change_week(w),
        key="week_sel"
    )

    st.markdown("---")

    # Charger planning
    planning = planning_service.get_planning_semaine(st.session_state.semaine_actuelle)

    if not planning:
        empty_state(
            "Aucun planning",
            "📅",
            "Génère un planning avec l'IA"
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✨ Générer IA", type="primary", use_container_width=True):
                st.session_state.active_tab = 1
                st.rerun()
        with col2:
            if st.button("➕ Planning vide", use_container_width=True):
                _create_empty_planning()
        return

    # Structure planning
    structure = planning_service.get_planning_structure(planning.id)

    # Stats
    stats = {
        "total_repas": sum(len(j["repas"]) for j in structure["jours"]),
        "repas_bebe": sum(1 for j in structure["jours"] for r in j["repas"] if r.get("est_adapte_bebe")),
        "repas_batch": sum(1 for j in structure["jours"] for r in j["repas"] if r.get("est_batch")),
        "repas_termines": sum(1 for j in structure["jours"] for r in j["repas"] if r.get("statut") == "terminé")
    }
    planning_stats(stats)

    st.markdown("---")

    # Calendrier hebdomadaire
    week_calendar(
        structure,
        on_day_click=lambda jour_idx: _add_meal_to_day(planning.id, jour_idx),
        on_meal_click=lambda meal_id: st.info(f"Repas {meal_id}"),
        key="calendar"
    )

    st.markdown("---")

    # Timeline par jour
    config = planning_service.get_or_create_config()

    for jour_data in structure["jours"]:
        is_today = jour_data["date"] == date.today()

        with st.expander(
                f"{'🔵 ' if is_today else ''}{jour_data['nom_jour']} {format_date(jour_data['date'], 'short')}",
                expanded=is_today
        ):
            meal_timeline(
                jour_data["repas"],
                on_click=lambda mid: st.info(f"Repas {mid}"),
                key=f"timeline_{jour_data['jour_idx']}"
            )

            # Actions jour
            col1, col2 = st.columns(2)
            with col1:
                if st.button("➕ Ajouter repas", key=f"add_{jour_data['jour_idx']}", use_container_width=True):
                    _add_meal_to_day(planning.id, jour_data["jour_idx"])
            with col2:
                if st.button("🗑️ Vider jour", key=f"clear_{jour_data['jour_idx']}", use_container_width=True):
                    _clear_day(jour_data["jour_idx"])

    # Modal ajout repas
    if hasattr(st.session_state, "adding_meal"):
        _render_add_meal_modal()


# ═══════════════════════════════════════════════════════════════
# TAB 2 : GÉNÉRATION IA
# ═══════════════════════════════════════════════════════════════

@handle_errors(show_in_ui=True)
def tab_generation_ia():
    """Tab Génération IA"""
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

    # Config
    with st.expander("📋 Configuration"):
        st.write(f"👥 {config.nb_adultes}A, {config.nb_enfants}E")
        if config.a_bebe:
            st.write("👶 Mode bébé")
        if config.batch_cooking_actif:
            jours_str = ", ".join([JOURS_SEMAINE[j] for j in config.jours_batch])
            st.write(f"🍳 Batch: {jours_str}")

    st.markdown("---")

    # Génération
    semaine = st.session_state.get("semaine_actuelle", planning_service.get_semaine_debut())

    if st.button("✨ Générer Planning", type="primary", use_container_width=True):
        _generate_planning_ia(semaine, config, agent)


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _change_week(new_week: date):
    """Change semaine"""
    st.session_state.semaine_actuelle = new_week


def _create_empty_planning():
    """Crée planning vide"""
    semaine = st.session_state.semaine_actuelle
    planning_service.create_planning(semaine, f"Planning {format_date(semaine, 'short')}")
    toast("✅ Planning créé", "success")
    Cache.invalidate("planning")
    st.rerun()


def _add_meal_to_day(planning_id: int, jour_idx: int):
    """Prépare ajout repas"""
    semaine = st.session_state.semaine_actuelle
    date_jour = semaine + timedelta(days=jour_idx)

    st.session_state.adding_meal = {
        "planning_id": planning_id,
        "jour_idx": jour_idx,
        "date": date_jour
    }
    st.rerun()


def _clear_day(jour_idx: int):
    """Vide jour"""
    modal = Modal(f"clear_{jour_idx}")

    if modal.is_showing():
        st.warning("Supprimer tous les repas de ce jour ?")

        if modal.confirm():
            # TODO: Implémenter suppression
            toast("🗑️ Jour vidé", "success")
            modal.close()

        modal.cancel()
    else:
        modal.show()


def _render_add_meal_modal():
    """Modal ajout repas"""
    if not hasattr(st.session_state, "adding_meal"):
        return

    slot = st.session_state.adding_meal

    st.markdown("---")
    st.markdown("### ➕ Ajouter un repas")

    # Recettes disponibles
    with get_db_context() as db:
        recettes = db.query(Recette).order_by(Recette.nom).all()

    if not recettes:
        st.error("Aucune recette")
        if st.button("Annuler"):
            del st.session_state.adding_meal
            st.rerun()
        return

    # Types repas actifs
    config = planning_service.get_or_create_config()
    types_actifs = [k for k, v in config.repas_actifs.items() if v]

    # Formulaire
    meal_form(
        [{"id": r.id, "nom": r.nom} for r in recettes],
        types_actifs,
        on_submit=lambda data: _submit_meal(slot, data),
        key="meal_form"
    )

    # Annuler
    if st.button("❌ Annuler", use_container_width=True):
        del st.session_state.adding_meal
        st.rerun()


def _submit_meal(slot: Dict, data: Dict):
    """Soumet repas"""
    try:
        repas_service.ajouter_repas(
            planning_id=slot["planning_id"],
            jour_semaine=slot["jour_idx"],
            date_repas=slot["date"],
            type_repas=data["type_repas"],
            recette_id=data["recette_id"],
            portions=data["portions"],
            est_adapte_bebe=data["est_adapte_bebe"],
            notes=data.get("notes")
        )

        del st.session_state.adding_meal
        toast("✅ Repas ajouté", "success")
        Cache.invalidate("planning")
        st.rerun()

    except Exception as e:
        st.error(f"❌ {str(e)}")


def _generate_planning_ia(semaine: date, config, agent):
    """Génère planning IA"""
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
                planning_service.delete(existing.id)

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
# MAIN
# ═══════════════════════════════════════════════════════════════

def app():
    """Point d'entrée"""
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