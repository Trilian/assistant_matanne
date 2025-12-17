"""
Module Planning Semaine - Version Complète et Fonctionnelle
Génération IA, Ajout Manuel, Batch Cooking, Mode Bébé
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
from src.core.models import Recette, ConfigPlanningUtilisateur, PlanningHebdomadaire
from src.ui.components import render_stat_row, render_empty_state, render_toast
from src.utils.formatters import format_temps


# ===================================
# CONSTANTES
# ===================================

JOURS_SEMAINE = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

TYPES_REPAS = {
    "petit_déjeuner": {"icone": "🌅", "label": "Petit-déjeuner", "ordre": 1},
    "déjeuner": {"icone": "☀️", "label": "Déjeuner", "ordre": 2},
    "goûter": {"icone": "🍪", "label": "Goûter", "ordre": 3},
    "dîner": {"icone": "🌙", "label": "Dîner", "ordre": 4},
}


# ===================================
# CONFIGURATION SIDEBAR
# ===================================

def render_config_sidebar() -> ConfigPlanningUtilisateur:
    """Configuration intelligente dans la sidebar"""

    with st.sidebar:
        st.markdown("### ⚙️ Configuration Planning")

        config = planning_service.get_or_create_config()

        # ===================================
        # FOYER
        # ===================================
        with st.expander("👥 Composition du foyer", expanded=True):
            nb_adultes = st.number_input(
                "Adultes",
                1, 10,
                config.nb_adultes,
                key="cfg_adultes",
                help="Nombre d'adultes dans le foyer"
            )

            nb_enfants = st.number_input(
                "Enfants (hors bébé)",
                0, 10,
                config.nb_enfants,
                key="cfg_enfants",
                help="Nombre d'enfants (3 ans et +)"
            )

            # ✅ MODE BÉBÉ - Intuitif et friendly
            st.markdown("---")
            st.markdown("**👶 Bébé dans le foyer ?**")

            a_bebe = st.toggle(
                "Oui, adapter les recettes pour bébé",
                value=config.a_bebe,
                key="cfg_bebe",
                help="Active les adaptations pour bébé (6-18 mois)"
            )

            if a_bebe:
                st.info("💡 L'IA privilégiera les recettes compatibles bébé et suggérera des adaptations")

        # ===================================
        # REPAS À PLANIFIER
        # ===================================
        with st.expander("🍽️ Repas à planifier", expanded=True):
            repas_actifs = {}

            for type_repas, info in TYPES_REPAS.items():
                default_value = config.repas_actifs.get(
                    type_repas,
                    type_repas in ["déjeuner", "dîner"]
                )

                repas_actifs[type_repas] = st.checkbox(
                    f"{info['icone']} {info['label']}",
                    value=default_value,
                    key=f"cfg_{type_repas}"
                )

        # ===================================
        # BATCH COOKING
        # ===================================
        with st.expander("🍳 Batch Cooking", expanded=False):
            st.markdown("""
            Le **batch cooking** consiste à préparer plusieurs repas en une seule session.
            
            **Avantages :**
            - ⏱️ Gain de temps en semaine
            - 💰 Économies d'énergie
            - 🧘 Moins de stress quotidien
            """)

            batch_actif = st.toggle(
                "Activer le batch cooking",
                value=config.batch_cooking_actif,
                key="cfg_batch"
            )

            jours_batch = []
            if batch_actif:
                st.markdown("**📅 Jours de préparation :**")

                col_j1, col_j2 = st.columns(2)

                with col_j1:
                    for i, nom in enumerate(["Lun", "Mar", "Mer", "Jeu"]):
                        if st.checkbox(
                                nom,
                                value=i in config.jours_batch,
                                key=f"batch_{i}"
                        ):
                            jours_batch.append(i)

                with col_j2:
                    for i, nom in enumerate(["Ven", "Sam", "Dim"], start=4):
                        if st.checkbox(
                                nom,
                                value=i in config.jours_batch,
                                key=f"batch_{i}"
                        ):
                            jours_batch.append(i)

                if not jours_batch:
                    st.warning("⚠️ Sélectionne au moins un jour de préparation")

        # ===================================
        # SAUVEGARDER
        # ===================================
        st.markdown("---")

        if st.button("💾 Enregistrer la configuration", type="primary", use_container_width=True):
            planning_service.update_config({
                "nb_adultes": nb_adultes,
                "nb_enfants": nb_enfants,
                "a_bebe": a_bebe,
                "repas_actifs": repas_actifs,
                "batch_cooking_actif": batch_actif,
                "jours_batch": jours_batch if batch_actif else []
            })
            render_toast("✅ Configuration sauvegardée", "success")
            st.rerun()

        return config


# ===================================
# COMPOSANTS REPAS
# ===================================

def render_repas_card(repas: Optional[Dict], jour_idx: int, type_repas: str, planning_id: int, date_jour: date, key: str):
    """Carte repas avec actions"""

    if not repas or not repas.get("recette"):
        # ✅ SLOT VIDE - Bouton d'ajout
        if st.button(
                f"➕ Ajouter {TYPES_REPAS[type_repas]['label']}",
                key=f"add_{key}",
                use_container_width=True,
                type="secondary"
        ):
            # Stocker les infos pour le modal
            st.session_state.adding_repas_slot = {
                "planning_id": planning_id,
                "jour_idx": jour_idx,
                "date_jour": date_jour,
                "type_repas": type_repas
            }
            st.rerun()

        return

    # ✅ REPAS EXISTANT
    recette = repas["recette"]

    with st.container():
        # Header avec image miniature
        col1, col2 = st.columns([1, 4])

        with col1:
            if recette.get("url_image"):
                st.image(recette["url_image"], use_container_width=True)
            else:
                st.markdown(f"<div style='font-size: 3rem; text-align: center;'>{TYPES_REPAS[type_repas]['icone']}</div>", unsafe_allow_html=True)

        with col2:
            st.markdown(f"**{recette['nom']}**")

            badges = []
            if repas.get("est_adapte_bebe"):
                badges.append("👶 Adapté bébé")
            if repas.get("est_batch"):
                badges.append("🍳 Batch")

            if badges:
                st.caption(" • ".join(badges))

            st.caption(f"⏱️ {format_temps(recette['temps_total'])} • {repas['portions']} pers.")

        # Actions
        col_a1, col_a2, col_a3, col_a4 = st.columns(4)

        with col_a1:
            if st.button("👁️", key=f"view_{key}", help="Voir détails"):
                st.session_state.viewing_repas_details = repas["id"]
                st.rerun()

        with col_a2:
            if st.button("✏️", key=f"edit_{key}", help="Modifier"):
                st.session_state.editing_repas_id = repas["id"]
                st.rerun()

        with col_a3:
            if st.button("🔄", key=f"move_{key}", help="Déplacer"):
                st.session_state.moving_repas_id = repas["id"]
                st.rerun()

        with col_a4:
            if st.button("🗑️", key=f"del_{key}", help="Supprimer"):
                repas_service.supprimer_repas(repas["id"])
                render_toast("🗑️ Repas supprimé", "success")
                st.rerun()


def render_modal_add_repas():
    """Modal d'ajout de repas manuel"""

    if "adding_repas_slot" not in st.session_state:
        return

    slot = st.session_state.adding_repas_slot

    st.markdown("---")
    st.markdown(f"### ➕ Ajouter un repas - {JOURS_SEMAINE[slot['jour_idx']]} {TYPES_REPAS[slot['type_repas']]['label']}")

    with st.form("add_repas_form"):
        # Sélection recette
        with get_db_context() as db:
            recettes = db.query(Recette).order_by(Recette.nom).all()

        if not recettes:
            st.error("❌ Aucune recette disponible. Crée d'abord des recettes !")
            if st.form_submit_button("Annuler"):
                del st.session_state.adding_repas_slot
                st.rerun()
            return

        recette_names = [r.nom for r in recettes]
        recette_select = st.selectbox(
            "🍽️ Recette",
            recette_names,
            key="select_recette"
        )

        # Afficher infos recette sélectionnée
        recette_choisie = next(r for r in recettes if r.nom == recette_select)

        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.caption(f"⏱️ {format_temps(recette_choisie.temps_preparation + recette_choisie.temps_cuisson)}")
            st.caption(f"👥 {recette_choisie.portions} portions par défaut")
        with col_info2:
            if recette_choisie.compatible_bebe:
                st.caption("👶 Compatible bébé")
            if recette_choisie.compatible_batch:
                st.caption("🍳 Compatible batch")

        st.markdown("---")

        # Options
        col_opt1, col_opt2 = st.columns(2)

        with col_opt1:
            portions = st.number_input(
                "Portions",
                1, 20,
                recette_choisie.portions,
                key="portions_add"
            )

        with col_opt2:
            adapte_bebe = st.checkbox(
                "👶 Adapter pour bébé",
                value=recette_choisie.compatible_bebe,
                disabled=not recette_choisie.compatible_bebe,
                key="bebe_add"
            )

        notes = st.text_input(
            "Notes (optionnel)",
            placeholder="Ex: Doubler la recette, Congeler une portion...",
            key="notes_add"
        )

        # Boutons
        col_btn1, col_btn2 = st.columns(2)

        with col_btn1:
            submitted = st.form_submit_button("✅ Ajouter", type="primary", use_container_width=True)

        with col_btn2:
            cancelled = st.form_submit_button("❌ Annuler", use_container_width=True)

        if submitted:
            # Ajouter le repas
            repas_service.ajouter_repas(
                planning_id=slot["planning_id"],
                jour_semaine=slot["jour_idx"],
                date_repas=slot["date_jour"],
                type_repas=slot["type_repas"],
                recette_id=recette_choisie.id,
                portions=portions,
                est_adapte_bebe=adapte_bebe,
                notes=notes
            )

            del st.session_state.adding_repas_slot
            render_toast(f"✅ {recette_choisie.nom} ajouté !", "success")
            st.rerun()

        if cancelled:
            del st.session_state.adding_repas_slot
            st.rerun()


# ===================================
# TAB 1 : PLANNING ACTUEL
# ===================================

def tab_planning():
    """Affichage du planning avec ajout manuel"""

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
            action_callback=lambda: st.session_state.update({"switch_to_tab": 1})
        )

        # Créer un planning vide pour permettre l'ajout manuel
        if st.button("➕ Créer un planning vide", type="secondary", use_container_width=True):
            planning_id = planning_service.create_planning(
                semaine_actuelle,
                f"Planning manuel {semaine_actuelle.strftime('%d/%m')}"
            )
            render_toast("✅ Planning créé ! Tu peux maintenant ajouter des repas.", "success")
            st.rerun()

        return

    # Structure planning
    structure = planning_service.get_planning_structure(planning.id)
    config = planning_service.get_or_create_config()

    # Stats
    total_repas = sum(len(j["repas"]) for j in structure["jours"])
    repas_bebe = sum(1 for j in structure["jours"] for r in j["repas"] if r.get("est_adapte_bebe"))
    repas_batch = sum(1 for j in structure["jours"] for r in j["repas"] if r.get("est_batch"))

    stats_data = [
        {"label": "Repas planifiés", "value": total_repas},
        {"label": "Adapté bébé", "value": repas_bebe} if config.a_bebe else None,
        {"label": "Batch cooking", "value": repas_batch} if config.batch_cooking_actif else None,
    ]

    stats_data = [s for s in stats_data if s is not None]
    render_stat_row(stats_data, cols=len(stats_data))

    st.markdown("---")

    # ✅ BOUTON BATCH COOKING
    if config.batch_cooking_actif and repas_batch > 0:
        if st.button(
                f"🍳 Préparer {repas_batch} repas en Batch Cooking",
                type="primary",
                use_container_width=True
        ):
            st.session_state.show_batch_modal = True
            st.rerun()

    st.markdown("---")

    # Affichage par jour
    types_repas_actifs = [k for k, v in config.repas_actifs.items() if v]

    for jour_data in structure["jours"]:
        is_today = jour_data["date"] == date.today()

        with st.expander(
                f"{'🔵 ' if is_today else ''}{jour_data['nom_jour']} {jour_data['date'].strftime('%d/%m')}",
                expanded=is_today
        ):
            if not any(r["type"] in types_repas_actifs for r in jour_data["repas"]):
                st.caption("Aucun repas planifié")

            for type_repas in types_repas_actifs:
                repas = next((r for r in jour_data["repas"] if r["type"] == type_repas), None)

                st.markdown(f"**{TYPES_REPAS[type_repas]['icone']} {TYPES_REPAS[type_repas]['label']}**")

                render_repas_card(
                    repas,
                    jour_data["jour_idx"],
                    type_repas,
                    planning.id,
                    jour_data["date"],
                    f"{jour_data['jour_idx']}_{type_repas}"
                )

                st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    # Modal ajout repas
    render_modal_add_repas()

    # ✅ Modal Batch Cooking
    if st.session_state.get("show_batch_modal"):
        render_batch_cooking_modal(planning.id, structure)


# ===================================
# MODAL BATCH COOKING
# ===================================

def render_batch_cooking_modal(planning_id: int, structure: Dict):
    """Modal de préparation batch cooking"""

    st.markdown("---")
    st.markdown("## 🍳 Session Batch Cooking")

    # Récupérer tous les repas batch
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
        st.info("Aucun repas batch dans ce planning")
        if st.button("Fermer"):
            del st.session_state.show_batch_modal
            st.rerun()
        return

    st.info(f"💡 **{len(repas_batch)} repas** à préparer en batch cooking")

    # Grouper par recette
    recettes_grouped = {}
    for repas in repas_batch:
        recette_id = repas["recette"]["id"]
        if recette_id not in recettes_grouped:
            recettes_grouped[recette_id] = {
                "recette": repas["recette"],
                "occurrences": []
            }
        recettes_grouped[recette_id]["occurrences"].append({
            "jour": repas["jour_nom"],
            "portions": repas["portions"]
        })

    # Afficher par recette
    st.markdown("### 📋 Liste de préparation")

    for recette_id, data in recettes_grouped.items():
        recette = data["recette"]
        occurrences = data["occurrences"]

        total_portions = sum(o["portions"] for o in occurrences)

        with st.expander(f"**{recette['nom']}** ({total_portions} portions total)", expanded=True):
            st.write(f"⏱️ Temps: {format_temps(recette['temps_total'])}")

            st.markdown("**Occasions :**")
            for occ in occurrences:
                st.write(f"• {occ['jour']} : {occ['portions']} portions")

            st.markdown("---")

            col_b1, col_b2 = st.columns(2)

            with col_b1:
                if st.button(f"👁️ Voir la recette", key=f"view_batch_{recette_id}"):
                    StateManager.set_viewing_recipe(recette_id)
                    del st.session_state.show_batch_modal
                    StateManager.navigate_to("cuisine.recettes")
                    st.rerun()

            with col_b2:
                if st.button(f"✅ Marquer préparé", key=f"done_batch_{recette_id}"):
                    st.success(f"✅ {recette['nom']} préparé !")

    st.markdown("---")

    # Conseils
    st.markdown("### 💡 Conseils Batch Cooking")

    conseils = [
        "🕐 Prépare tout le même jour pour optimiser le temps",
        "📦 Utilise des contenants hermétiques adaptés",
        "❄️ Les plats se conservent 3-5 jours au frigo",
        "🏷️ Étiquette chaque plat avec nom et date",
        "🔥 Réchauffe à feu doux pour préserver les saveurs"
    ]

    for conseil in conseils:
        st.info(conseil)

    if st.button("✅ Terminer la session", type="primary", use_container_width=True):
        del st.session_state.show_batch_modal
        render_toast("🎉 Session batch cooking terminée !", "success")
        st.balloons()
        st.rerun()


# ===================================
# TAB 2 : GÉNÉRATION IA (CORRIGÉE)
# ===================================

def tab_generation_ia():
    """Génération automatique avec IA - VERSION CORRIGÉE"""

    st.subheader("🤖 Génération Automatique")

    agent = get_state().agent_ia
    if not agent:
        st.error("❌ Agent IA non disponible")
        return

    config = planning_service.get_or_create_config()

    # Vérifier qu'il y a des recettes
    with get_db_context() as db:
        nb_recettes = db.query(Recette).count()

    if nb_recettes < 5:
        st.warning(f"⚠️ Seulement {nb_recettes} recette(s) disponible(s). Il en faut au moins 5 pour générer un planning.")
        if st.button("➕ Ajouter des recettes"):
            StateManager.navigate_to("cuisine.recettes")
            st.rerun()
        return

    st.info(f"💡 L'IA va générer un planning équilibré avec {nb_recettes} recettes disponibles")

    # Résumé config
    with st.expander("📋 Configuration actuelle", expanded=False):
        st.write(f"👥 **Foyer :** {config.nb_adultes} adultes, {config.nb_enfants} enfants")
        if config.a_bebe:
            st.write("👶 **Mode bébé activé**")

        repas_actifs = [k for k, v in config.repas_actifs.items() if v]
        st.write(f"🍽️ **Repas :** {', '.join(repas_actifs)}")

        if config.batch_cooking_actif:
            jours = [JOURS_SEMAINE[j] for j in config.jours_batch]
            st.write(f"🍳 **Batch cooking :** {', '.join(jours)}")

    st.markdown("---")

    # Bouton génération
    semaine_actuelle = st.session_state.get("semaine_actuelle", planning_service.get_semaine_debut())

    if st.button("✨ Générer le planning de la semaine", type="primary", use_container_width=True):

        with st.spinner("🤖 L'IA génère ton planning..."):
            try:
                ai_service = create_planning_generation_service(agent)

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                # ✅ CORRECTION: Appel corrigé
                result = loop.run_until_complete(
                    ai_service.generer_planning_complet(
                        semaine_actuelle,
                        config,
                        contraintes=None
                    )
                )

                # Supprimer ancien planning si existe
                planning_existant = planning_service.get_planning_semaine(semaine_actuelle)
                if planning_existant:
                    planning_service.delete_planning(planning_existant.id)

                # Créer nouveau planning
                planning_id = planning_service.create_planning(
                    semaine_actuelle,
                    f"Planning IA {semaine_actuelle.strftime('%d/%m')}"
                )

                # Ajouter les repas
                with get_db_context() as db:
                    for jour_planning in result.planning:
                        date_jour = semaine_actuelle + timedelta(days=jour_planning.jour)

                        for repas_data in jour_planning.repas:
                            # Trouver la recette
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
                                    notes=f"IA: {repas_data.raison}" if repas_data.raison else None,
                                    db=db
                                )

                    # Marquer comme généré par IA
                    planning = db.query(PlanningHebdomadaire).get(planning_id)
                    if planning:
                        planning.genere_par_ia = True
                        db.commit()

                render_toast("✅ Planning généré avec succès !", "success")
                st.balloons()
                st.rerun()

            except Exception as e:
                st.error(f"❌ Erreur lors de la génération : {str(e)}")

                # Debug info
                with st.expander("🔍 Détails de l'erreur (pour debug)", expanded=False):
                    import traceback
                    st.code(traceback.format_exc())


# ===================================
# MAIN APP
# ===================================

def app():
    """Module Planning Semaine - Point d'entrée"""

    st.title("🗓️ Planning Hebdomadaire")
    st.caption("Génération IA, ajout manuel, batch cooking, mode bébé")

    # Config sidebar
    render_config_sidebar()

    # Gérer le switch de tab
    if "switch_to_tab" in st.session_state:
        default_tab = st.session_state.switch_to_tab
        del st.session_state.switch_to_tab
    else:
        default_tab = 0

    # Tabs
    tab1, tab2 = st.tabs([
        "📅 Mon Planning",
        "🤖 Générer avec l'IA"
    ])

    with tab1:
        tab_planning()

    with tab2:
        tab_generation_ia()