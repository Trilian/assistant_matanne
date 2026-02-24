"""
Module Routines avec Agent IA integre
Gestion des routines quotidiennes avec rappels intelligents

Refactorisé: la logique métier est dans ``src.services.famille.routines.ServiceRoutines``.
Ce module ne contient que l'UI Streamlit.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.core.session_keys import SK
from src.modules._framework import error_boundary
from src.ui import etat_vide
from src.ui.fragments import ui_fragment
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

if TYPE_CHECKING:
    from src.services.famille.routines import ServiceRoutines

# Session keys scopées
_keys = KeyNamespace("routines")


def _get_service() -> ServiceRoutines:
    """Lazy-load du service routines."""
    from src.services.famille.routines import obtenir_service_routines

    return obtenir_service_routines()


# ===================================
# MODULE PRINCIPAL
# ===================================


@profiler_rerun("routines")
def app() -> None:
    """Module Routines avec IA integree."""
    from src.core.async_utils import executer_async

    svc = _get_service()

    st.title("⏰ Routines Quotidiennes")
    st.caption("Gestion intelligente des routines familiales")

    # Recuperer l'agent IA
    agent: Any = st.session_state.get(SK.AGENT_IA)

    # ===================================
    # HEURE ACTUELLE & ALERTES
    # ===================================

    now = datetime.now()
    st.info(f"👶 **{now.strftime('%H:%M')}** — {now.strftime('%A %d %B %Y')}")

    # Tâches en retard
    taches_retard = svc.get_taches_en_retard()

    if taches_retard:
        st.warning(f"⚠️ **{len(taches_retard)} tâche(s) en retard**")

        for tache in taches_retard[:3]:
            col_r1, col_r2 = st.columns([3, 1])

            with col_r1:
                st.write(f"• **{tache['routine']}** : {tache['tache']} (prevu {tache['heure']})")

            with col_r2:
                if st.button("✅ Fait", key=f"late_{tache['id']}", use_container_width=True):
                    svc.marquer_complete(tache["id"])
                    st.success("Termine !")
                    st.rerun()

    st.markdown("---")

    # ===================================
    # TABS PRINCIPAUX
    # ===================================

    TAB_LABELS = ["🎯 Mes Routines", "🤖 Rappels IA", "➕ Créer Routine", "📊 Suivi"]
    tab_index = tabs_with_url(TAB_LABELS, param="tab")
    tab1, tab2, tab3, tab4 = st.tabs(TAB_LABELS)

    with tab1:
        with error_boundary(titre="Erreur routines actives"):
            _afficher_tab_routines(svc)

    with tab2:
        with error_boundary(titre="Erreur rappels IA"):
            _afficher_tab_rappels_ia(svc, agent, executer_async)

    with tab3:
        with error_boundary(titre="Erreur création routine"):
            _afficher_tab_creer(svc)

    with tab4:
        with error_boundary(titre="Erreur suivi routines"):
            _afficher_tab_suivi(svc)


# ===================================
# TABS INDIVIDUELS (< 80 lignes chacun)
# ===================================


@ui_fragment
def _afficher_tab_routines(svc: ServiceRoutines) -> None:
    """TAB 1: Liste des routines actives."""
    st.subheader("Routines actives")

    col_a1, col_a2 = st.columns([2, 1])
    with col_a1:
        if st.button("🔄 Rafraîchir", use_container_width=True):
            st.rerun()
    with col_a2:
        if st.button("🔄 Reinitialiser jour", use_container_width=True):
            nb = svc.reinitialiser_taches_jour()
            st.success(f"Tâches reinitialisees ({nb})")
            st.rerun()

    routines_list = svc.lister_routines(actives_uniquement=True)

    if not routines_list:
        st.info("Aucune routine active. Cree-en une ou utilise l'IA pour generer des suggestions !")
        return

    for routine in routines_list:
        with st.expander(
            f"{routine['ia']} **{routine['nom']}** — {routine['pour']} "
            f"({routine['nb_taches']} tâches)",
            expanded=True,
        ):
            st.caption(routine["description"])
            st.caption(f"📋 Frequence : {routine['frequence']}")

            taches_list = svc.lister_taches(routine["id"])

            if taches_list:
                st.markdown("**Tâches :**")
                for tache in taches_list:
                    _afficher_tache(svc, tache, routine["id"])

                # Ajouter tâche (si mode actif)
                if st.session_state.get(SK.ADDING_TASK_TO) == routine["id"]:
                    _formulaire_ajout_tache(svc, routine["id"])

            # Actions routine
            col_act1, col_act2 = st.columns(2)
            with col_act1:
                if st.button(
                    "⏸️ Desactiver",
                    key=f"disable_{routine['id']}",
                    use_container_width=True,
                ):
                    svc.desactiver_routine(routine["id"])
                    st.success("Routine desactivee")
                    st.rerun()
            with col_act2:
                if st.button(
                    "🗑️ Supprimer",
                    key=f"del_{routine['id']}",
                    type="secondary",
                    use_container_width=True,
                ):
                    svc.supprimer_routine(routine["id"])
                    st.success("Routine supprimee")
                    st.rerun()


def _afficher_tache(svc: ServiceRoutines, tache: dict[str, Any], routine_id: int) -> None:
    """Affiche une tâche avec actions."""
    col_t1, col_t2, col_t3 = st.columns([2, 1, 1])

    with col_t1:
        statut_emoji = "✅" if tache["statut"] == "termine" else "⏳"
        st.write(f"{statut_emoji} **{tache['heure']}** — {tache['nom']}")

    with col_t2:
        if tache["statut"] == "à faire":
            if st.button("✅ Termine", key=f"done_{tache['id']}", use_container_width=True):
                svc.marquer_complete(tache["id"])
                st.success("Tâche terminee !")
                st.rerun()
        else:
            st.caption(
                f"Fait à {tache['completed_at'].strftime('%H:%M')}" if tache["completed_at"] else ""
            )

    with col_t3:
        if st.button("➕ Tâche", key=f"add_{routine_id}", use_container_width=True):
            st.session_state[SK.ADDING_TASK_TO] = routine_id


def _formulaire_ajout_tache(svc: ServiceRoutines, routine_id: int) -> None:
    """Formulaire inline pour ajouter une tâche."""
    with st.form(f"form_add_task_{routine_id}"):
        new_task_name = st.text_input("Nom de la tâche")
        new_task_time = st.time_input("Heure (optionnel)")

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            if st.form_submit_button("✅ Ajouter"):
                if new_task_name:
                    time_str = new_task_time.strftime("%H:%M") if new_task_time else None
                    svc.ajouter_tache(routine_id, new_task_name, time_str)
                    st.success("Tâche ajoutee")
                    del st.session_state[SK.ADDING_TASK_TO]
                    st.rerun()
        with col_f2:
            if st.form_submit_button("❌ Annuler"):
                del st.session_state[SK.ADDING_TASK_TO]
                st.rerun()


@ui_fragment
def _afficher_tab_rappels_ia(
    svc: ServiceRoutines, agent: Any, executer_async: Callable[..., Any]
) -> None:
    """TAB 2: Rappels intelligents via IA."""
    st.subheader("🤖 Rappels intelligents")

    if not agent:
        st.error("Agent IA non disponible")
        return

    st.info("💡 L'IA analyse tes routines et te rappelle les tâches importantes")
    heure_actuelle = datetime.now().strftime("%H:%M")

    if st.button("🤖 Demander rappels IA", type="primary", use_container_width=True):
        with st.spinner("🤖 Analyse des routines..."):
            try:
                routines_data = svc.get_taches_ia_data()
                rappels = executer_async(agent.rappeler_routines(routines_data, heure_actuelle))
                st.session_state[SK.RAPPELS_IA] = rappels
                st.success("✅ Rappels generes")
            except Exception as e:
                st.error(f"Erreur IA : {e}")

    # Afficher rappels
    if SK.RAPPELS_IA in st.session_state:
        rappels = st.session_state[SK.RAPPELS_IA]
        if not rappels:
            st.success("✅ Aucune routine urgente ! Tout est sous contrôle.")
        else:
            st.markdown("---")
            st.markdown("### ⏰ Rappels à l'instant")
            for rappel in rappels:
                priorite = rappel.get("priorite", "moyenne")
                if priorite == "haute":
                    st.error(f"❌ **{rappel['routine']}** : {rappel['message']}")
                elif priorite == "moyenne":
                    st.warning(f"⚠️ **{rappel['routine']}** : {rappel['message']}")
                else:
                    st.info(f"ℹ️ **{rappel['routine']}** : {rappel['message']}")

    # Suggestions de routines
    st.markdown("---")
    st.markdown("### 💡 Routines suggerees par l'IA")

    suggestions_base = [
        {
            "nom": "Routine du matin",
            "taches": ["Reveil", "Petit-dejeuner", "Preparation", "Depart"],
        },
        {
            "nom": "Routine du soir (Jules)",
            "taches": ["Bain", "Dîner", "Brossage dents", "Histoire", "Dodo"],
        },
        {
            "nom": "Routine coucher (adultes)",
            "taches": ["Preparation lendemain", "Rangement", "Lecture", "Coucher"],
        },
        {
            "nom": "Routine weekend",
            "taches": ["Grasse matinee", "Activite famille", "Repas ensemble", "Detente"],
        },
    ]

    for sugg in suggestions_base[:2]:
        with st.expander(f"✨ {sugg['nom']}", expanded=False):
            st.write("**Tâches suggerees :**")
            for tache in sugg["taches"]:
                st.write(f"• {tache}")

            if st.button("➕ Creer cette routine", key=f"create_{sugg['nom']}"):
                nom_routine = str(sugg["nom"])
                routine_id = svc.creer_routine(
                    nom_routine, "Routine suggeree par l'IA", "Famille", "quotidien"
                )
                for tache in sugg["taches"]:
                    svc.ajouter_tache(routine_id, tache)
                st.success(f"✅ Routine '{sugg['nom']}' creee !")
                st.rerun()


@ui_fragment
def _afficher_tab_creer(svc: ServiceRoutines) -> None:
    """TAB 3: Formulaire de création de routine."""
    st.subheader("➕ Creer une nouvelle routine")

    with st.form("form_create_routine"):
        nom = st.text_input("Nom de la routine *", placeholder="Ex: Routine du soir")

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            description = st.text_area("Description", placeholder="Objectif de cette routine...")
        with col_c2:
            personnes = svc.lister_personnes()
            pour_qui = st.selectbox("Pour qui ?", personnes)
            frequence = st.selectbox(
                "Frequence", ["quotidien", "semaine", "weekend", "occasionnel"]
            )

        st.markdown("**Tâches de la routine**")
        nb_taches = st.number_input("Nombre de tâches", 1, 20, 3, key="nb_tasks_create")

        taches: list[dict[str, Any]] = []
        for i in range(int(nb_taches)):
            col_t1, col_t2 = st.columns([2, 1])
            with col_t1:
                tache_nom = st.text_input(
                    f"Tâche {i + 1}", placeholder="Ex: Brossage de dents", key=f"task_name_{i}"
                )
            with col_t2:
                tache_heure = st.time_input(f"Heure {i + 1}", value=None, key=f"task_time_{i}")
            if tache_nom:
                taches.append(
                    {
                        "nom": tache_nom,
                        "heure": tache_heure.strftime("%H:%M") if tache_heure else None,
                    }
                )

        submitted = st.form_submit_button("📅 Creer la routine", type="primary")

        if submitted:
            if not nom:
                st.error("Le nom est obligatoire")
            elif not taches:
                st.error("Ajoute au moins une tâche")
            else:
                routine_id = svc.creer_routine(nom, description, pour_qui, frequence)
                for tache in taches:
                    svc.ajouter_tache(routine_id, tache["nom"], tache["heure"])
                st.success(f"✅ Routine '{nom}' creee avec {len(taches)} tâches !")
                st.balloons()
                st.rerun()


@ui_fragment
def _afficher_tab_suivi(svc: ServiceRoutines) -> None:
    """TAB 4: Suivi & statistiques."""
    st.subheader("📊 Suivi des routines")

    routines_all = svc.lister_routines(actives_uniquement=False)

    if not routines_all:
        etat_vide("Aucune routine à analyser", "📊")
        return

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric("Routines totales", len(routines_all))
    with col_m2:
        actives = sum(1 for r in routines_all if r["active"])
        st.metric("Actives", actives)
    with col_m3:
        ia_count = sum(1 for r in routines_all if r["ia"] == "–")
        st.metric("Suggerees IA", ia_count)
    with col_m4:
        tasks_today = svc.compter_completees_aujourdhui()
        st.metric("Completees aujourd'hui", tasks_today)

    st.markdown("---")
    st.markdown("### 🧹 Details par routine")

    for routine in routines_all:
        taches_list = svc.lister_taches(routine["id"])
        if taches_list:
            terminees = sum(1 for t in taches_list if t["statut"] == "termine")
            total = len(taches_list)
            pct = (terminees / total) * 100 if total > 0 else 0

            col_stat1, col_stat2, col_stat3 = st.columns([2, 1, 1])
            with col_stat1:
                st.write(f"**{routine['nom']}**")
            with col_stat2:
                st.progress(pct / 100)
            with col_stat3:
                st.write(f"{terminees}/{total} ({pct:.0f}%)")

    st.markdown("---")
    st.markdown("### 📋 Historique de la semaine")
    st.info("Fonctionnalite en developpement : graphique d'historique sur 7 jours")
