"""
Composants UI - Planning
Cartes et widgets spécifiques planning
"""
import streamlit as st
from typing import Dict, Optional, Callable
from datetime import date


TYPES_REPAS_ICONS = {
    "petit_déjeuner": "🌅",
    "déjeuner": "☀️",
    "goûter": "🍪",
    "dîner": "🌙",
    "bébé": "👶",
}


def meal_card(
        meal: Dict,
        on_edit: Optional[Callable[[int], None]] = None,
        on_delete: Optional[Callable[[int], None]] = None,
        key: str = "meal"
):
    """
    Carte repas

    Args:
        meal: Dict repas
        on_edit: Callback (repas_id)
        on_delete: Callback (repas_id)
        key: Clé unique
    """
    if not meal.get("recette"):
        st.info("🍽️ Aucun repas planifié")
        return

    recette = meal["recette"]
    type_repas = meal.get("type", "dîner")
    icon = TYPES_REPAS_ICONS.get(type_repas, "🍽️")

    with st.container():
        st.markdown(f"### {icon} {recette['nom']}")
        st.caption(f"{meal['portions']}p • {recette.get('temps_total', 0)}min")

        if meal.get("est_adapte_bebe"):
            st.caption("👶 Adapté bébé")

        if on_edit or on_delete:
            col1, col2 = st.columns(2)
            if on_edit:
                with col1:
                    if st.button("✏️ Modifier", key=f"{key}_edit", use_container_width=True):
                        on_edit(meal["id"])
            if on_delete:
                with col2:
                    if st.button("🗑️ Suppr.", key=f"{key}_del", use_container_width=True):
                        on_delete(meal["id"])


def week_calendar(
        planning_data: Dict,
        on_day_click: Optional[Callable[[int], None]] = None,
        key: str = "calendar"
):
    """
    Calendrier hebdomadaire

    Args:
        planning_data: Structure planning complète
        on_day_click: Callback (jour_idx)
        key: Clé unique
    """
    semaine_debut = planning_data.get("semaine_debut")
    st.markdown(f"### 📅 Semaine du {semaine_debut.strftime('%d/%m/%Y')}")

    cols = st.columns(7)

    for jour_data in planning_data.get("jours", []):
        jour_idx = jour_data["jour_idx"]
        is_today = jour_data["date"] == date.today()

        with cols[jour_idx]:
            if is_today:
                st.markdown(f"**🔵 {jour_data['nom_jour'][:3]}**")
            else:
                st.markdown(f"**{jour_data['nom_jour'][:3]}**")

            st.caption(jour_data["date"].strftime("%d/%m"))

            repas = jour_data.get("repas", [])
            if repas:
                for idx, meal in enumerate(repas[:2]):
                    icon = TYPES_REPAS_ICONS.get(meal.get("type"), "🍽️")
                    recette_nom = meal.get("recette", {}).get("nom", "—")
                    st.caption(f"{icon} {recette_nom[:12]}...")
                if len(repas) > 2:
                    st.caption(f"+{len(repas) - 2}")
            else:
                st.caption("Vide")

            if on_day_click and st.button("➕", key=f"{key}_add_{jour_idx}", use_container_width=True):
                on_day_click(jour_idx)


def planning_summary(planning_data: Dict):
    """
    Résumé planning

    Args:
        planning_data: Structure planning
    """
    total_repas = sum(len(j["repas"]) for j in planning_data.get("jours", []))

    repas_bebe = sum(
        1 for j in planning_data.get("jours", [])
        for r in j["repas"]
        if r.get("est_adapte_bebe")
    )

    temps_total = sum(
        r.get("recette", {}).get("temps_total", 0)
        for j in planning_data.get("jours", [])
        for r in j["repas"]
        if r.get("recette")
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Repas Planifiés", total_repas)

    with col2:
        st.metric("👶 Adaptés Bébé", repas_bebe)

    with col3:
        st.metric("⏱️ Temps Total", f"{temps_total}min")


def meal_type_selector(on_select: Callable, key: str = "meal_type"):
    """
    Sélecteur type de repas avec icônes

    Args:
        on_select: Callback (type_repas)
        key: Clé unique
    """
    types = list(TYPES_REPAS_ICONS.keys())

    cols = st.columns(len(types))

    for idx, type_repas in enumerate(types):
        with cols[idx]:
            icon = TYPES_REPAS_ICONS[type_repas]
            label = f"{icon} {type_repas.replace('_', ' ').title()}"

            if st.button(label, key=f"{key}_{type_repas}", use_container_width=True):
                on_select(type_repas)


def day_header(jour_data: Dict, is_today: bool = False):
    """
    Header pour un jour

    Args:
        jour_data: Données du jour
        is_today: Est-ce aujourd'hui ?
    """
    jour_nom = jour_data["nom_jour"]
    date_jour = jour_data["date"]
    nb_repas = len(jour_data.get("repas", []))

    prefix = "🔵 " if is_today else ""

    st.markdown(
        f"### {prefix}{jour_nom} {date_jour.strftime('%d/%m')} "
        f"({nb_repas} repas)"
    )