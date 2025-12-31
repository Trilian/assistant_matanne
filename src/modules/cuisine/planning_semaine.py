"""
Module Planning
"""
import streamlit as st
from datetime import timedelta
from src.services.planning import planning_service, repas_service
from src.ui import empty_state, meal_card, badge
from src.core.cache import Cache

@Cache.cached(ttl=60, key="planning_semaine")
def load_planning(semaine_debut):
    """Charge planning avec cache"""
    return planning_service.get_planning_semaine(semaine_debut)

def app():
    """Point d'entrée module planning"""
    st.title("🗓️ Planning Hebdomadaire")

    # ═══════════════════════════════════════════════════════════
    # NAVIGATION SEMAINE
    # ═══════════════════════════════════════════════════════════

    if "semaine_actuelle" not in st.session_state:
        st.session_state.semaine_actuelle = planning_service.get_semaine_debut()

    semaine = st.session_state.semaine_actuelle

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("⬅️ Semaine précédente", use_container_width=True):
            st.session_state.semaine_actuelle = semaine - timedelta(days=7)
            Cache.invalidate("planning_semaine")
            st.rerun()

    with col2:
        st.markdown(
            f"<div style='text-align:center; padding:0.5rem;'>"
            f"<strong>Semaine du {semaine.strftime('%d/%m/%Y')}</strong>"
            f"</div>",
            unsafe_allow_html=True
        )

    with col3:
        if st.button("Semaine suivante ➡️", use_container_width=True):
            st.session_state.semaine_actuelle = semaine + timedelta(days=7)
            Cache.invalidate("planning_semaine")
            st.rerun()

    st.markdown("---")

    # ═══════════════════════════════════════════════════════════
    # CHARGER PLANNING
    # ═══════════════════════════════════════════════════════════

    planning = load_planning(semaine)

    if not planning:
        empty_state(
            "Aucun planning pour cette semaine",
            "📅",
            "Crée un planning pour commencer"
        )

        if st.button("➕ Créer planning", type="primary", use_container_width=True):
            planning_service.create({
                "semaine_debut": semaine,
                "nom": f"Semaine {semaine.strftime('%d/%m')}"
            })
            Cache.invalidate("planning_semaine")
            st.rerun()

        return

    # ═══════════════════════════════════════════════════════════
    # AFFICHER STRUCTURE
    # ═══════════════════════════════════════════════════════════

    structure = planning_service.get_planning_structure(planning.id)

    # Stats rapides
    total_repas = sum(len(j["repas"]) for j in structure["jours"])
    st.caption(f"📊 {total_repas} repas planifiés cette semaine")

    # Affichage par jour
    for jour_data in structure["jours"]:
        jour_nom = jour_data["nom_jour"]
        date_jour = jour_data["date"]
        repas = jour_data["repas"]

        # Badge date
        is_today = date_jour == planning_service.get_semaine_debut()

        with st.expander(
                f"{'🔵 ' if is_today else ''}{jour_nom} {date_jour.strftime('%d/%m')} ({len(repas)} repas)",
                expanded=is_today
        ):
            if repas:
                for idx, repas_data in enumerate(repas):
                    meal_card(
                        repas_data,
                        on_edit=lambda rid=repas_data["id"]: _edit_repas(rid),
                        on_delete=lambda rid=repas_data["id"]: _delete_repas(rid),
                        on_mark_done=lambda rid=repas_data["id"]: _mark_done(rid),
                        key=f"meal_{repas_data['id']}"
                    )

                    if idx < len(repas) - 1:
                        st.markdown("---")
            else:
                st.info("🍽️ Aucun repas planifié")

            # Action rapide
            if st.button(
                    "➕ Ajouter un repas",
                    key=f"add_{jour_data['jour_idx']}",
                    use_container_width=True
            ):
                _add_repas_jour(planning.id, jour_data["jour_idx"], date_jour)

def _edit_repas(repas_id: int):
    """Édite repas"""
    st.session_state.editing_repas_id = repas_id
    st.rerun()

def _delete_repas(repas_id: int):
    """Supprime repas"""
    repas_service.delete(repas_id)
    from src.ui import toast
    toast("🗑️ Repas supprimé", "success")
    Cache.invalidate("planning_semaine")
    st.rerun()

def _mark_done(repas_id: int):
    """Marque repas comme fait"""
    repas_service.update(repas_id, {"statut": "terminé"})
    from src.ui import toast
    toast("✅ Repas marqué fait", "success")
    Cache.invalidate("planning_semaine")
    st.rerun()

def _add_repas_jour(planning_id: int, jour_idx: int, date_jour):
    """Ajoute repas pour un jour"""
    st.session_state.adding_repas_planning_id = planning_id
    st.session_state.adding_repas_jour = jour_idx
    st.session_state.adding_repas_date = date_jour
    st.rerun()