"""
Composants UI - PLANNING
Composants spécialisés pour le planning hebdomadaire
"""
import streamlit as st
from typing import Dict, List, Optional, Callable
from datetime import date, timedelta


JOURS_SEMAINE = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

TYPES_REPAS_ICONS = {
    "petit_déjeuner": "🌅",
    "déjeuner": "☀️",
    "goûter": "🍪",
    "dîner": "🌙",
    "bébé": "👶",
    "batch_cooking": "🍳"
}


def meal_card(
        meal: Dict,
        on_edit: Optional[Callable[[int], None]] = None,
        on_delete: Optional[Callable[[int], None]] = None,
        on_mark_done: Optional[Callable[[int], None]] = None,
        compact: bool = False,
        key: str = "meal"
):
    """
    Carte repas

    Args:
        meal: {
            "id": int,
            "type": str,
            "recette": {"id": int, "nom": str, "temps_total": int, "url_image": str},
            "portions": int,
            "est_adapte_bebe": bool,
            "est_batch": bool,
            "notes": str,
            "statut": str
        }
        on_edit/delete/mark_done: Callbacks
        compact: Mode compact
        key: Clé unique
    """
    if not meal.get("recette"):
        st.info("🍽️ Aucun repas planifié")
        return

    recette = meal["recette"]
    type_repas = meal.get("type", "dîner")
    icon = TYPES_REPAS_ICONS.get(type_repas, "🍽️")

    # Statut couleur
    statut_color = "#d4edda" if meal.get("statut") == "terminé" else "#fff3cd"

    with st.container():
        st.markdown(
            f'<div style="border-left: 4px solid {statut_color}; padding: 0.75rem; '
            f'background: #ffffff; border-radius: 8px; margin-bottom: 0.5rem;"></div>',
            unsafe_allow_html=True
        )

        if compact:
            # Mode compact
            st.markdown(f"**{icon} {recette['nom']}**")
            st.caption(f"{meal['portions']}p • {recette.get('temps_total', 0)}min")

            if meal.get("est_adapte_bebe"):
                st.caption("👶 Adapté bébé")
        else:
            # Mode détaillé
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"### {icon} {recette['nom']}")

                meta = [f"{meal['portions']} portions"]
                if recette.get('temps_total'):
                    meta.append(f"⏱️ {recette['temps_total']}min")
                if meal.get("est_adapte_bebe"):
                    meta.append("👶 Bébé")
                if meal.get("est_batch"):
                    meta.append("🍳 Batch")

                st.caption(" • ".join(meta))

                if meal.get("notes"):
                    with st.expander("📝 Notes"):
                        st.write(meal["notes"])

            with col2:
                if meal.get("statut") == "terminé":
                    st.success("✅ Fait")
                else:
                    if on_mark_done and st.button("✅", key=f"{key}_done", help="Marquer fait"):
                        on_mark_done(meal["id"])

            # Actions
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                if on_edit and st.button("✏️ Modifier", key=f"{key}_edit", use_container_width=True):
                    on_edit(meal["id"])
            with col_a2:
                if on_delete and st.button("🗑️ Suppr.", key=f"{key}_del", use_container_width=True):
                    on_delete(meal["id"])


def week_calendar(
        planning_data: Dict,
        on_day_click: Optional[Callable[[int], None]] = None,
        on_meal_click: Optional[Callable[[int], None]] = None,
        key: str = "calendar"
):
    """
    Calendrier hebdomadaire

    Args:
        planning_data: {
            "semaine_debut": date,
            "jours": [{"jour_idx": int, "nom_jour": str, "date": date, "repas": [...]}]
        }
        on_day_click: Callback(jour_idx)
        on_meal_click: Callback(meal_id)
        key: Clé unique
    """
    semaine_debut = planning_data.get("semaine_debut")

    # Header
    st.markdown(f"### 📅 Semaine du {semaine_debut.strftime('%d/%m/%Y')}")

    # Grille 7 colonnes
    cols = st.columns(7)

    for jour_data in planning_data.get("jours", []):
        jour_idx = jour_data["jour_idx"]
        is_today = jour_data["date"] == date.today()

        with cols[jour_idx]:
            # Header jour
            if is_today:
                st.markdown(f"**🔵 {jour_data['nom_jour'][:3]}**")
            else:
                st.markdown(f"**{jour_data['nom_jour'][:3]}**")

            st.caption(jour_data["date"].strftime("%d/%m"))

            # Repas du jour
            repas = jour_data.get("repas", [])

            if repas:
                for idx, meal in enumerate(repas[:3]):  # Max 3 en compact
                    icon = TYPES_REPAS_ICONS.get(meal.get("type"), "🍽️")
                    recette_nom = meal.get("recette", {}).get("nom", "—")

                    if on_meal_click and st.button(
                            f"{icon} {recette_nom[:15]}...",
                            key=f"{key}_{jour_idx}_{idx}",
                            use_container_width=True
                    ):
                        on_meal_click(meal["id"])

                if len(repas) > 3:
                    st.caption(f"+{len(repas) - 3}")
            else:
                st.caption("Vide")

            # Action jour
            if on_day_click and st.button("➕", key=f"{key}_add_{jour_idx}", use_container_width=True):
                on_day_click(jour_idx)


def meal_timeline(
        repas_jour: List[Dict],
        on_click: Optional[Callable[[int], None]] = None,
        key: str = "timeline"
):
    """
    Timeline repas d'un jour

    Args:
        repas_jour: Liste repas du jour
        on_click: Callback(meal_id)
        key: Clé unique
    """
    if not repas_jour:
        st.info("Aucun repas planifié")
        return

    # Trier par ordre
    sorted_meals = sorted(repas_jour, key=lambda x: x.get("ordre", 0))

    for idx, meal in enumerate(sorted_meals):
        type_repas = meal.get("type", "dîner")
        icon = TYPES_REPAS_ICONS.get(type_repas, "🍽️")

        col1, col2 = st.columns([1, 10])

        with col1:
            # Icône + ligne
            color = "#4CAF50" if meal.get("statut") == "terminé" else "#FF9800"
            st.markdown(
                f'<div style="text-align: center; font-size: 1.5rem; color: {color};">{icon}</div>',
                unsafe_allow_html=True
            )

        with col2:
            if meal.get("recette"):
                recette = meal["recette"]
                st.markdown(f"**{type_repas.replace('_', ' ').title()}** - {recette['nom']}")
                st.caption(f"{meal['portions']}p • {recette.get('temps_total', 0)}min")

                if on_click and st.button("👁️ Voir", key=f"{key}_{idx}", use_container_width=True):
                    on_click(meal["id"])
            else:
                st.caption(f"*{type_repas.replace('_', ' ').title()}* - Non planifié")

        # Ligne de connexion (sauf dernier)
        if idx < len(sorted_meals) - 1:
            st.markdown(
                f'<div style="margin-left: 1.5rem; border-left: 2px solid #e0e0e0; height: 1rem;"></div>',
                unsafe_allow_html=True
            )


def planning_stats(stats: Dict, key: str = "plan_stats"):
    """
    Stats planning

    Args:
        stats: {
            "total_repas": int,
            "repas_bebe": int,
            "repas_batch": int,
            "repas_termines": int
        }
        key: Clé unique
    """
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Repas", stats.get("total_repas", 0))

    with col2:
        st.metric("👶 Bébé", stats.get("repas_bebe", 0))

    with col3:
        st.metric("🍳 Batch", stats.get("repas_batch", 0))

    with col4:
        st.metric("✅ Faits", stats.get("repas_termines", 0))


def week_selector(
        current_week: date,
        on_change: Callable[[date], None],
        key: str = "week_sel"
):
    """
    Sélecteur de semaine

    Args:
        current_week: Semaine actuelle (lundi)
        on_change: Callback(new_week)
        key: Clé unique
    """
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("⬅️ Préc.", key=f"{key}_prev", use_container_width=True):
            new_week = current_week - timedelta(days=7)
            on_change(new_week)

    with col2:
        # Affichage semaine
        end_week = current_week + timedelta(days=6)
        st.markdown(
            f"<div style='text-align:center; padding:0.5rem;'>"
            f"<strong>{current_week.strftime('%d/%m')} - {end_week.strftime('%d/%m/%Y')}</strong>"
            f"</div>",
            unsafe_allow_html=True
        )

    with col3:
        if st.button("Suiv. ➡️", key=f"{key}_next", use_container_width=True):
            new_week = current_week + timedelta(days=7)
            on_change(new_week)


def meal_form(
        recettes: List[Dict],
        types_repas: List[str],
        on_submit: Callable[[Dict], None],
        key: str = "meal_form"
):
    """
    Formulaire ajout/édition repas

    Args:
        recettes: Liste recettes disponibles
        types_repas: Types de repas actifs
        on_submit: Callback(data)
        key: Clé unique
    """
    with st.form(f"{key}_form"):
        col1, col2 = st.columns(2)

        with col1:
            recette_id = st.selectbox(
                "Recette *",
                options=[r["id"] for r in recettes],
                format_func=lambda x: next(r["nom"] for r in recettes if r["id"] == x),
                key=f"{key}_rec"
            )

            type_repas = st.selectbox(
                "Type *",
                options=types_repas,
                format_func=lambda x: f"{TYPES_REPAS_ICONS.get(x, '🍽️')} {x.replace('_', ' ').title()}",
                key=f"{key}_type"
            )

        with col2:
            portions = st.number_input("Portions", 1, 20, 4, key=f"{key}_port")
            adapte_bebe = st.checkbox("👶 Adapter bébé", key=f"{key}_bebe")

        notes = st.text_area("Notes (optionnel)", key=f"{key}_notes")

        submitted = st.form_submit_button("✅ Valider", use_container_width=True)

        if submitted:
            data = {
                "recette_id": recette_id,
                "type_repas": type_repas,
                "portions": portions,
                "est_adapte_bebe": adapte_bebe,
                "notes": notes
            }
            on_submit(data)