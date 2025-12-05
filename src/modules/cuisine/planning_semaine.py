"""
Module Planning Semaine - Interface Streamlit
Génération IA, modification manuelle, vue tableau
"""
import streamlit as st
import asyncio
from datetime import date, timedelta
from typing import Dict, List
from src.services.planning_service import planning_service
from src.core.database import get_db_context
from src.core.models import Recette, ConfigPlanningUtilisateur
from src.core.ai_agent import AgentIA

# ===================================
# HELPERS UI
# ===================================

def render_config_sidebar() -> ConfigPlanningUtilisateur:
    """Affiche la config dans la sidebar"""
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")

        config = planning_service.get_or_create_config()

        with st.expander("👥 Composition foyer", expanded=False):
            nb_adultes = st.number_input("Adultes", 1, 10, config.nb_adultes, key="cfg_adultes")
            nb_enfants = st.number_input("Enfants", 0, 10, config.nb_enfants, key="cfg_enfants")
            a_bebe = st.checkbox("Avec bébé", config.a_bebe, key="cfg_bebe")

        with st.expander("🍽️ Repas à planifier", expanded=True):
            repas_types = {
                "petit_déjeuner": "Petit-déjeuner",
                "déjeuner": "Déjeuner",
                "dîner": "Dîner",
                "goûter": "Goûter"
            }

            repas_actifs = {}
            for key, label in repas_types.items():
                repas_actifs[key] = st.checkbox(
                    label,
                    config.repas_actifs.get(key, key in ["déjeuner", "dîner"]),
                    key=f"cfg_repas_{key}"
                )

            if a_bebe:
                repas_actifs["bébé"] = st.checkbox(
                    "Repas bébé séparés",
                    config.repas_actifs.get("bébé", False),
                    key="cfg_repas_bebe"
                )

        with st.expander("🍳 Batch Cooking", expanded=False):
            batch_actif = st.checkbox(
                "Activer batch cooking",
                config.batch_cooking_actif,
                key="cfg_batch"
            )

            jours_batch = []
            if batch_actif:
                st.caption("Jours de session batch :")
                col1, col2 = st.columns(2)
                jours_noms = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
                for i, nom in enumerate(jours_noms):
                    col = col1 if i < 4 else col2
                    if col.checkbox(nom, i in config.jours_batch, key=f"batch_jour_{i}"):
                        jours_batch.append(i)

        if st.button("💾 Enregistrer config", type="primary", use_container_width=True):
            planning_service.update_config({
                "nb_adultes": nb_adultes,
                "nb_enfants": nb_enfants,
                "a_bebe": a_bebe,
                "repas_actifs": repas_actifs,
                "batch_cooking_actif": batch_actif,
                "jours_batch": jours_batch
            })
            st.success("✅ Configuration sauvegardée")
            st.rerun()

        return config


def render_vue_tableau(structure: Dict):
    """Affiche le planning en vue tableau"""
    st.markdown("### 📅 Planning de la semaine")

    # Types de repas actifs
    config = planning_service.get_or_create_config()
    types_repas_actifs = [k for k, v in config.repas_actifs.items() if v]

    # En-têtes (jours)
    cols_jours = st.columns(7)
    for i, col in enumerate(cols_jours):
        jour_data = structure["jours"][i]
        col.markdown(f"**{jour_data['nom_jour']}**")
        col.caption(jour_data['date'].strftime("%d/%m"))

    st.markdown("---")

    # Lignes (types de repas)
    for type_repas in types_repas_actifs:
        st.markdown(f"**{type_repas.replace('_', ' ').title()}**")

        cols_repas = st.columns(7)

        for jour_idx, col in enumerate(cols_repas):
            jour_data = structure["jours"][jour_idx]

            # Trouver le repas correspondant
            repas = next((r for r in jour_data["repas"] if r["type"] == type_repas), None)

            with col:
                if repas and repas["recette"]:
                    # Afficher carte repas
                    with st.container():
                        if repas["recette"]["url_image"]:
                            st.image(repas["recette"]["url_image"], use_container_width=True)

                        st.markdown(f"<small>{repas['recette']['nom']}</small>", unsafe_allow_html=True)

                        badges = []
                        if repas["est_adapte_bebe"]:
                            badges.append("👶")
                        if repas["est_batch"]:
                            badges.append("🍳")
                        if badges:
                            st.caption(" ".join(badges))

                        st.caption(f"⏱️ {repas['recette']['temps_total']}min • {repas['portions']}p")

                        # Actions
                        col_a1, col_a2 = st.columns(2)
                        with col_a1:
                            if st.button("✏️", key=f"edit_{repas['id']}", help="Modifier"):
                                st.session_state[f"editing_{repas['id']}"] = True
                                st.rerun()
                        with col_a2:
                            if st.button("🗑️", key=f"del_{repas['id']}", help="Supprimer"):
                                planning_service.delete_repas(repas['id'])
                                st.success("Repas supprimé")
                                st.rerun()

                        # Modal modification
                        if st.session_state.get(f"editing_{repas['id']}", False):
                            with st.expander("Modifier", expanded=True):
                                render_edit_repas(repas, jour_data)
                else:
                    # Case vide - bouton ajouter
                    if st.button("➕", key=f"add_{jour_idx}_{type_repas}", use_container_width=True):
                        st.session_state[f"adding_{jour_idx}_{type_repas}"] = True
                        st.rerun()

                    # Modal ajout
                    if st.session_state.get(f"adding_{jour_idx}_{type_repas}", False):
                        with st.expander("Ajouter repas", expanded=True):
                            render_add_repas_form(structure["planning_id"], jour_idx, jour_data["date"], type_repas)

        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)


def render_edit_repas(repas: Dict, jour_data: Dict):
    """Formulaire d'édition d'un repas"""
    with st.form(f"edit_form_{repas['id']}"):
        # Changer recette
        with get_db_context() as db:
            recettes = db.query(Recette).order_by(Recette.nom).all()

        recette_names = [r.nom for r in recettes]
        current_idx = next((i for i, r in enumerate(recettes) if r.id == repas["recette"]["id"]), 0)

        nouvelle_recette = st.selectbox(
            "Recette",
            recette_names,
            index=current_idx,
            key=f"edit_recette_{repas['id']}"
        )

        portions = st.number_input("Portions", 1, 12, repas["portions"], key=f"edit_portions_{repas['id']}")

        adapte_bebe = st.checkbox("Adapter pour bébé", repas["est_adapte_bebe"], key=f"edit_bebe_{repas['id']}")

        notes = st.text_area("Notes", repas.get("notes", ""), key=f"edit_notes_{repas['id']}")

        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Enregistrer", type="primary"):
                nouvelle_recette_id = next(r.id for r in recettes if r.nom == nouvelle_recette)

                planning_service.update_repas(
                    repas["id"],
                    recette_id=nouvelle_recette_id,
                    portions=portions,
                    est_adapte_bebe=adapte_bebe,
                    notes=notes
                )

                del st.session_state[f"editing_{repas['id']}"]
                st.success("✅ Repas modifié")
                st.rerun()

        with col2:
            if st.form_submit_button("❌ Annuler"):
                del st.session_state[f"editing_{repas['id']}"]
                st.rerun()


def render_add_repas_form(planning_id: int, jour_idx: int, date_jour: date, type_repas: str):
    """Formulaire d'ajout de repas"""
    with st.form(f"add_form_{jour_idx}_{type_repas}"):
        with get_db_context() as db:
            recettes = db.query(Recette).order_by(Recette.nom).all()

        recette_select = st.selectbox(
            "Recette",
            [r.nom for r in recettes],
            key=f"add_recette_{jour_idx}_{type_repas}"
        )

        portions = st.number_input("Portions", 1, 12, 4, key=f"add_portions_{jour_idx}_{type_repas}")

        adapte_bebe = st.checkbox("Adapter pour bébé", key=f"add_bebe_{jour_idx}_{type_repas}")

        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("➕ Ajouter", type="primary"):
                recette_id = next(r.id for r in recettes if r.nom == recette_select)

                planning_service.add_repas(
                    planning_id=planning_id,
                    jour_semaine=jour_idx,
                    date_repas=date_jour,
                    type_repas=type_repas,
                    recette_id=recette_id,
                    portions=portions,
                    est_adapte_bebe=adapte_bebe
                )

                del st.session_state[f"adding_{jour_idx}_{type_repas}"]
                st.success("✅ Repas ajouté")
                st.rerun()

        with col2:
            if st.form_submit_button("❌ Annuler"):
                del st.session_state[f"adding_{jour_idx}_{type_repas}"]
                st.rerun()


# ===================================
# MODULE PRINCIPAL
# ===================================

def app():
    """Module Planning Semaine - Point d'entrée"""
    st.title("🗓️ Planning Hebdomadaire Intelligent")
    st.caption("Génération IA, modification drag & drop, batch cooking")

    # Config sidebar
    config = render_config_sidebar()

    # Récupérer l'agent IA
    agent: AgentIA = st.session_state.get("agent_ia")

    # ===================================
    # NAVIGATION SEMAINE
    # ===================================

    if "semaine_actuelle" not in st.session_state:
        st.session_state.semaine_actuelle = planning_service.get_semaine_debut()

    col_nav1, col_nav2, col_nav3, col_nav4 = st.columns([1, 2, 1, 1])

    with col_nav1:
        if st.button("⬅️ Semaine préc.", use_container_width=True):
            st.session_state.semaine_actuelle -= timedelta(days=7)
            st.rerun()

    with col_nav2:
        semaine = st.session_state.semaine_actuelle
        semaine_fin = semaine + timedelta(days=6)
        st.markdown(f"### {semaine.strftime('%d/%m')} — {semaine_fin.strftime('%d/%m/%Y')}")

    with col_nav3:
        if st.button("Semaine suiv. ➡️", use_container_width=True):
            st.session_state.semaine_actuelle += timedelta(days=7)
            st.rerun()

    with col_nav4:
        if st.button("📅 Aujourd'hui", use_container_width=True):
            st.session_state.semaine_actuelle = planning_service.get_semaine_debut()
            st.rerun()

    st.markdown("---")

    # ===================================
    # CHARGER OU CRÉER PLANNING
    # ===================================

    semaine_actuelle = st.session_state.semaine_actuelle
    planning = planning_service.get_planning_semaine(semaine_actuelle)

    if not planning:
        # Aucun planning pour cette semaine
        st.info("📝 Aucun planning pour cette semaine")

        col_create1, col_create2 = st.columns(2)

        with col_create1:
            if st.button("➕ Créer planning vide", type="secondary", use_container_width=True):
                planning_id = planning_service.create_planning(semaine_actuelle)
                st.success("✅ Planning créé")
                st.rerun()

        with col_create2:
            if agent and st.button("✨ Générer avec l'IA", type="primary", use_container_width=True):
                with st.spinner("🤖 L'IA génère ton planning..."):
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)

                        planning_id = loop.run_until_complete(
                            planning_service.generer_planning_ia(
                                semaine_actuelle,
                                config,
                                agent
                            )
                        )

                        st.success("✅ Planning généré par l'IA !")
                        st.balloons()
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Erreur génération IA : {e}")

    else:
        # Planning existant
        structure = planning_service.get_planning_structure(planning.id)

        # Actions globales
        col_actions1, col_actions2, col_actions3 = st.columns([2, 1, 1])

        with col_actions1:
            if planning.genere_par_ia:
                st.info("🤖 Planning généré par l'IA")

        with col_actions2:
            if st.button("🔄 Régénérer IA", use_container_width=True):
                if agent:
                    with st.spinner("🤖 Régénération..."):
                        # Supprimer ancien
                        planning_service.delete_planning(planning.id)

                        # Générer nouveau
                        try:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)

                            planning_id = loop.run_until_complete(
                                planning_service.generer_planning_ia(
                                    semaine_actuelle,
                                    config,
                                    agent
                                )
                            )

                            st.success("✅ Planning régénéré !")
                            st.rerun()

                        except Exception as e:
                            st.error(f"❌ Erreur : {e}")

        with col_actions3:
            if st.button("🗑️ Supprimer", use_container_width=True):
                planning_service.delete_planning(planning.id)
                st.success("Planning supprimé")
                st.rerun()

        st.markdown("---")

        # ===================================
        # AFFICHAGE PLANNING
        # ===================================

        tab1, tab2, tab3 = st.tabs(["📅 Vue Tableau", "📋 Vue Liste", "📊 Statistiques"])

        with tab1:
            render_vue_tableau(structure)

        with tab2:
            st.markdown("### 📋 Vue Liste")

            for jour_data in structure["jours"]:
                with st.expander(f"{jour_data['nom_jour']} {jour_data['date'].strftime('%d/%m')}", expanded=False):
                    if not jour_data["repas"]:
                        st.caption("Aucun repas planifié")
                    else:
                        for repas in jour_data["repas"]:
                            if repas["recette"]:
                                col1, col2 = st.columns([3, 1])

                                with col1:
                                    badges = []
                                    if repas["est_adapte_bebe"]:
                                        badges.append("👶")
                                    if repas["est_batch"]:
                                        badges.append("🍳")

                                    st.markdown(f"**{repas['type']}** : {repas['recette']['nom']} {' '.join(badges)}")
                                    st.caption(f"{repas['portions']} portions • {repas['recette']['temps_total']}min")

                                with col2:
                                    if st.button("✏️", key=f"list_edit_{repas['id']}"):
                                        st.session_state[f"editing_{repas['id']}"] = True
                                        st.rerun()

        with tab3:
            st.markdown("### 📊 Statistiques du planning")

            # Calculs
            total_repas = sum(len(j["repas"]) for j in structure["jours"])
            repas_bebe = sum(1 for j in structure["jours"] for r in j["repas"] if r["est_adapte_bebe"])
            sessions_batch = sum(1 for j in structure["jours"] for r in j["repas"] if r["est_batch"])

            temps_total = 0
            recettes_utilisees = set()
            for jour in structure["jours"]:
                for repas in jour["repas"]:
                    if repas["recette"]:
                        temps_total += repas["recette"]["temps_total"]
                        recettes_utilisees.add(repas["recette"]["nom"])

            col_s1, col_s2, col_s3, col_s4 = st.columns(4)

            with col_s1:
                st.metric("Total repas", total_repas)

            with col_s2:
                st.metric("Recettes uniques", len(recettes_utilisees))

            with col_s3:
                st.metric("Temps cuisine", f"{temps_total}min", delta=f"{temps_total // 60}h")

            with col_s4:
                st.metric("Repas bébé", repas_bebe)

            if sessions_batch > 0:
                st.success(f"🍳 {sessions_batch} session(s) de batch cooking planifiée(s)")

            # Répartition par jour
            st.markdown("#### Répartition par jour")

            for jour_data in structure["jours"]:
                nb_repas_jour = len(jour_data["repas"])
                st.write(f"**{jour_data['nom_jour']}** : {nb_repas_jour} repas")