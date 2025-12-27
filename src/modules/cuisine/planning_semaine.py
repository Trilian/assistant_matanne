# src/modules/cuisine/planning_semaine.py
"""
Module Planning Semaine - VERSION OPTIMISÉE
Utilise planning_components + DynamicList

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
from src.core.models import Recette, PlanningHebdomadaire
from src.core.exceptions import handle_errors

# ✅ NOUVEAUX COMPOSANTS
from src.ui.planning_components import (
    render_week_calendar,
    render_meal_timeline,
    render_recipe_selector,
    render_planning_stats,
    render_empty_planning,
    render_planning_preview
)
from src.ui.components import render_toast

# Constantes
JOURS_SEMAINE = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

TYPES_REPAS = {
    "petit_déjeuner": {"icone": "🌅", "label": "Petit-déjeuner", "ordre": 1},
    "déjeuner": {"icone": "☀️", "label": "Déjeuner", "ordre": 2},
    "goûter": {"icone": "🍪", "label": "Goûter", "ordre": 3},
    "dîner": {"icone": "🌙", "label": "Dîner", "ordre": 4},
}


# ═══════════════════════════════════════════════════════════════
# CONFIGURATION SIDEBAR (inchangé mais commenté pour gain place)
# ═══════════════════════════════════════════════════════════════

def render_config_sidebar() -> Dict:
    """Configuration intelligente dans la sidebar"""
    with st.sidebar:
        st.markdown("### ⚙️ Configuration Planning")

        config = planning_service.get_or_create_config()

        # Foyer
        with st.expander("👥 Composition du foyer", expanded=True):
            nb_adultes = st.number_input("Adultes", 1, 10, config.nb_adultes, key="cfg_adultes")
            nb_enfants = st.number_input("Enfants", 0, 10, config.nb_enfants, key="cfg_enfants")

            st.markdown("---")
            st.markdown("**👶 Bébé dans le foyer ?**")
            a_bebe = st.toggle(
                "Oui, adapter les recettes pour bébé",
                value=config.a_bebe,
                key="cfg_bebe"
            )

            if a_bebe:
                st.info("💡 L'IA privilégiera les recettes compatibles bébé")

        # Repas
        with st.expander("🍽️ Repas à planifier", expanded=True):
            repas_actifs = {}
            for type_repas, info in TYPES_REPAS.items():
                default = config.repas_actifs.get(type_repas, type_repas in ["déjeuner", "dîner"])
                repas_actifs[type_repas] = st.checkbox(
                    f"{info['icone']} {info['label']}",
                    value=default,
                    key=f"cfg_{type_repas}"
                )

        # Batch
        with st.expander("🍳 Batch Cooking", expanded=False):
            batch_actif = st.toggle("Activer", value=config.batch_cooking_actif, key="cfg_batch")

            jours_batch = []
            if batch_actif:
                st.markdown("**📅 Jours de préparation :**")
                col_j1, col_j2 = st.columns(2)

                with col_j1:
                    for i in range(4):
                        if st.checkbox(
                                JOURS_SEMAINE[i][:3],
                                value=i in config.jours_batch,
                                key=f"batch_{i}"
                        ):
                            jours_batch.append(i)

                with col_j2:
                    for i in range(4, 7):
                        if st.checkbox(
                                JOURS_SEMAINE[i][:3],
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
            render_toast("✅ Configuration sauvegardée", "success")
            st.rerun()

        return config


# ═══════════════════════════════════════════════════════════════
# TAB 1 : PLANNING ACTUEL (REFACTORISÉ avec composants)
# ═══════════════════════════════════════════════════════════════

def tab_planning():
    """Affichage du planning - VERSION OPTIMISÉE"""
    st.subheader("📋 Mon Planning")

    # ✅ Initialiser semaine
    if "semaine_actuelle" not in st.session_state:
        st.session_state.semaine_actuelle = planning_service.get_semaine_debut()

    # ✅ Calendrier avec composant
    def on_week_change(new_week: date):
        st.session_state.semaine_actuelle = new_week
        st.rerun()

    semaine = render_week_calendar(
        st.session_state.semaine_actuelle,
        on_week_change=on_week_change,
        show_today=True
    )

    st.markdown("---")

    # Charger planning
    planning = planning_service.get_planning_semaine(semaine)

    if not planning:
        # ✅ État vide avec composant
        render_empty_planning(
            message="Aucun planning pour cette semaine",
            actions=[
                {
                    "label": "✨ Générer avec l'IA",
                    "callback": lambda: st.session_state.update({"switch_to_tab": 1}),
                    "type": "primary"
                },
                {
                    "label": "➕ Créer un planning vide",
                    "callback": lambda: _create_empty_planning(semaine),
                    "type": "secondary"
                }
            ]
        )
        return

    # ✅ Stats avec composant
    structure = planning_service.get_planning_structure(planning.id)
    config = planning_service.get_or_create_config()

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

    render_planning_stats(
        stats,
        highlight_metrics=["total_repas", "repas_bebe", "repas_batch"]
    )

    st.markdown("---")

    # Batch cooking button
    if config.batch_cooking_actif and stats["repas_batch"] > 0:
        if st.button(
                f"🍳 Préparer {stats['repas_batch']} repas en Batch",
                type="primary",
                use_container_width=True
        ):
            st.session_state.show_batch_modal = True
            st.rerun()

    st.markdown("---")

    # ✅ Affichage par jour (simplifié)
    types_repas_actifs = [k for k, v in config.repas_actifs.items() if v]

    for jour_data in structure["jours"]:
        is_today = jour_data["date"] == date.today()

        with st.expander(
                f"{'🔵 ' if is_today else ''}{jour_data['nom_jour']} {jour_data['date'].strftime('%d/%m')}",
                expanded=is_today
        ):
            # Préparer données pour timeline
            meals_timeline = []

            for type_repas in types_repas_actifs:
                repas = next((r for r in jour_data["repas"] if r["type"] == type_repas), None)

                if repas and repas.get("recette"):
                    badges = []
                    if repas.get("est_adapte_bebe"):
                        badges.append("👶 Bébé")
                    if repas.get("est_batch"):
                        badges.append("🍳 Batch")

                    meals_timeline.append({
                        "id": repas["id"],
                        "type": type_repas,
                        "recette": {
                            "nom": repas["recette"]["nom"],
                            "url_image": repas["recette"].get("url_image")
                        },
                        "portions": repas["portions"],
                        "badges": badges
                    })

            # ✅ Timeline avec composant
            if meals_timeline:
                render_meal_timeline(
                    meals_timeline,
                    types_repas_actifs,
                    on_meal_click=lambda m: _view_meal_details(m["id"])
                )
            else:
                st.info("Aucun repas planifié")

            # Bouton ajout
            if st.button(
                    "➕ Ajouter un repas",
                    key=f"add_meal_{jour_data['jour_idx']}",
                    use_container_width=True
            ):
                st.session_state.adding_repas_slot = {
                    "planning_id": planning.id,
                    "jour_idx": jour_data["jour_idx"],
                    "date_jour": jour_data["date"],
                }
                st.rerun()

    # Modal ajout repas
    if "adding_repas_slot" in st.session_state:
        _render_modal_add_repas()

    # Modal Batch
    if st.session_state.get("show_batch_modal"):
        _render_batch_modal(planning.id, structure)


# ═══════════════════════════════════════════════════════════════
# TAB 2 : GÉNÉRATION IA (SIMPLIFIÉ)
# ═══════════════════════════════════════════════════════════════

@handle_errors(show_in_ui=True)
def tab_generation_ia():
    """Génération IA - VERSION SIMPLIFIÉE"""
    st.subheader("🤖 Génération Automatique")

    agent = get_state().agent_ia
    if not agent:
        st.error("❌ Agent IA non disponible")
        return

    config = planning_service.get_or_create_config()

    # Vérifier recettes
    with get_db_context() as db:
        nb_recettes = db.query(Recette).count()

    if nb_recettes < 5:
        st.warning(f"⚠️ {nb_recettes} recette(s) seulement. Il en faut au moins 5.")
        return

    st.info(f"💡 {nb_recettes} recettes disponibles pour la génération")

    # Résumé config
    with st.expander("📋 Configuration", expanded=False):
        st.write(f"👥 {config.nb_adultes} adultes, {config.nb_enfants} enfants")
        if config.a_bebe:
            st.write("👶 Mode bébé activé")

    st.markdown("---")

    # Génération
    semaine = st.session_state.get("semaine_actuelle", planning_service.get_semaine_debut())

    if st.button("✨ Générer", type="primary", use_container_width=True):
        with st.spinner("🤖 L'IA génère..."):
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
                    f"Planning IA {semaine.strftime('%d/%m')}"
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

                render_toast("✅ Planning généré !", "success")
                st.balloons()
                st.rerun()

            except Exception as e:
                st.error(f"❌ Erreur : {str(e)}")


# ═══════════════════════════════════════════════════════════════
# HELPERS PRIVÉS
# ═══════════════════════════════════════════════════════════════

def _create_empty_planning(semaine: date):
    """Crée un planning vide"""
    planning_id = planning_service.create_planning(
        semaine,
        f"Planning manuel {semaine.strftime('%d/%m')}"
    )
    render_toast("✅ Planning créé !", "success")
    st.rerun()


def _view_meal_details(meal_id: int):
    """Affiche détails repas"""
    st.session_state.viewing_meal_details = meal_id
    st.rerun()


def _render_modal_add_repas():
    """Modal ajout repas - VERSION SIMPLIFIÉE"""
    if "adding_repas_slot" not in st.session_state:
        return

    slot = st.session_state.adding_repas_slot

    st.markdown("---")
    st.markdown(f"### ➕ Ajouter un repas")

    # ✅ Sélecteur de recettes avec composant
    with get_db_context() as db:
        recettes = db.query(Recette).order_by(Recette.nom).all()

    if not recettes:
        st.error("❌ Aucune recette disponible")
        if st.button("Annuler"):
            del st.session_state.adding_repas_slot
            st.rerun()
        return

    recettes_data = [
        {
            "id": r.id,
            "nom": r.nom,
            "temps_total": r.temps_preparation + r.temps_cuisson,
            "portions": r.portions,
            "tags": [
                "⚡ Rapide" if r.est_rapide else None,
                "👶 Bébé" if r.compatible_bebe else None
            ]
        }
        for r in recettes
    ]

    selected = render_recipe_selector(
        [r for r in recettes_data if r is not None],
        key="modal_selector"
    )

    if selected:
        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            portions = st.number_input("Portions", 1, 20, selected["portions"])

        with col2:
            adapte_bebe = st.checkbox("👶 Adapter bébé", value=False)

        col_btn1, col_btn2 = st.columns(2)

        with col_btn1:
            if st.button("✅ Ajouter", type="primary", use_container_width=True):
                repas_service.ajouter_repas(
                    planning_id=slot["planning_id"],
                    jour_semaine=slot["jour_idx"],
                    date_repas=slot["date_jour"],
                    type_repas="dîner",  # Par défaut
                    recette_id=selected["id"],
                    portions=portions,
                    est_adapte_bebe=adapte_bebe
                )

                del st.session_state.adding_repas_slot
                render_toast(f"✅ {selected['nom']} ajouté !", "success")
                st.rerun()

        with col_btn2:
            if st.button("❌ Annuler", use_container_width=True):
                del st.session_state.adding_repas_slot
                st.rerun()


def _render_batch_modal(planning_id: int, structure: Dict):
    """Modal batch cooking - SIMPLIFIÉ"""
    st.markdown("---")
    st.markdown("## 🍳 Session Batch Cooking")

    repas_batch = []
    for jour in structure["jours"]:
        for repas in jour["repas"]:
            if repas.get("est_batch"):
                repas_batch.append({
                    **repas,
                    "jour_nom": jour["nom_jour"],
                    "date": jour["date"]
                })

    if not repas_batch:
        st.info("Aucun repas batch")
        if st.button("Fermer"):
            del st.session_state.show_batch_modal
            st.rerun()
        return

    st.info(f"💡 {len(repas_batch)} repas à préparer")

    # Grouper par recette
    from collections import defaultdict
    recettes_grouped = defaultdict(list)

    for repas in repas_batch:
        recettes_grouped[repas["recette"]["id"]].append({
            "jour": repas["jour_nom"],
            "portions": repas["portions"]
        })

    for recette_id, occurrences in recettes_grouped.items():
        recette = repas_batch[0]["recette"]  # Simplification
        total_portions = sum(o["portions"] for o in occurrences)

        with st.expander(f"**{recette['nom']}** ({total_portions}p total)", expanded=True):
            for occ in occurrences:
                st.write(f"• {occ['jour']}: {occ['portions']}p")

    if st.button("✅ Terminer", type="primary", use_container_width=True):
        del st.session_state.show_batch_modal
        render_toast("🎉 Session terminée !", "success")
        st.balloons()
        st.rerun()


# ═══════════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════════

def app():
    """Point d'entrée - SIMPLIFIÉ"""
    st.title("🗓️ Planning Hebdomadaire")
    st.caption("Génération IA, ajout manuel, batch cooking, mode bébé")

    # Config sidebar
    render_config_sidebar()

    # Tabs
    tab1, tab2 = st.tabs(["📅 Mon Planning", "🤖 Générer avec l'IA"])

    with tab1:
        tab_planning()

    with tab2:
        tab_generation_ia()