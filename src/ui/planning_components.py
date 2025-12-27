"""
Composants UI Planning - Réutilisables
Calendrier, Timeline, Sélecteur de recettes
"""
import streamlit as st
from datetime import date, timedelta
from typing import List, Dict, Optional, Callable, Any
import pandas as pd


# ═══════════════════════════════════════════════════════════════
# CALENDRIER SEMAINE
# ═══════════════════════════════════════════════════════════════

def render_week_calendar(
        current_week: date,
        on_week_change: Optional[Callable[[date], None]] = None,
        show_today: bool = True,
        key: str = "calendar"
) -> date:
    """
    Calendrier semaine avec navigation

    Args:
        current_week: Lundi de la semaine actuelle
        on_week_change: Callback(nouvelle_date)
        show_today: Bouton "Aujourd'hui"
        key: Clé unique

    Returns:
        Date du lundi sélectionné
    """
    col1, col2, col3, col4 = st.columns([1, 3, 1, 1])

    with col1:
        if st.button("⬅️ Préc", key=f"{key}_prev", use_container_width=True):
            new_week = current_week - timedelta(days=7)
            if on_week_change:
                on_week_change(new_week)
            return new_week

    with col2:
        week_end = current_week + timedelta(days=6)
        st.markdown(
            f"### 📅 {current_week.strftime('%d/%m')} — {week_end.strftime('%d/%m/%Y')}"
        )

    with col3:
        if st.button("Suiv ➡️", key=f"{key}_next", use_container_width=True):
            new_week = current_week + timedelta(days=7)
            if on_week_change:
                on_week_change(new_week)
            return new_week

    with col4:
        if show_today:
            if st.button("📅 Aujourd'hui", key=f"{key}_today", use_container_width=True):
                # Calculer le lundi de la semaine actuelle
                today = date.today()
                monday = today - timedelta(days=today.weekday())
                if on_week_change:
                    on_week_change(monday)
                return monday

    return current_week


def render_week_grid(
        days_data: List[Dict],
        on_day_click: Optional[Callable[[int, date], None]] = None,
        key: str = "grid"
):
    """
    Grille 7 jours avec données

    Args:
        days_data: Liste de 7 dicts {
            "jour_idx": 0-6,
            "date": date,
            "nom_jour": "Lundi",
            "content": Any,  # Contenu custom
            "highlight": bool
        }
        on_day_click: Callback(jour_idx, date)
        key: Clé unique
    """
    cols = st.columns(7)

    for idx, day in enumerate(days_data):
        with cols[idx]:
            is_today = day["date"] == date.today()
            is_highlight = day.get("highlight", False)

            # Card pour chaque jour
            bg_color = "#e3f2fd" if is_today else "#f5f5f5" if is_highlight else "#ffffff"

            st.markdown(
                f"""
                <div style="background: {bg_color}; 
                            padding: 0.5rem; 
                            border-radius: 8px; 
                            border: 2px solid {'#2196F3' if is_today else '#e0e0e0'};
                            text-align: center;">
                    <div style="font-weight: bold;">{day['nom_jour'][:3]}</div>
                    <div style="font-size: 0.875rem;">{day['date'].strftime('%d/%m')}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Contenu custom
            if day.get("content"):
                st.write(day["content"])

            # Action
            if on_day_click:
                if st.button(
                        "➕",
                        key=f"{key}_day_{idx}",
                        use_container_width=True
                ):
                    on_day_click(day["jour_idx"], day["date"])


# ═══════════════════════════════════════════════════════════════
# TIMELINE REPAS
# ═══════════════════════════════════════════════════════════════

def render_meal_timeline(
        meals: List[Dict],
        types_repas: List[str],
        on_meal_click: Optional[Callable[[Dict], None]] = None,
        key: str = "timeline"
):
    """
    Timeline des repas d'une journée

    Args:
        meals: Liste de repas {
            "id": int,
            "type": str,
            "recette": {"nom": str, "url_image": str},
            "portions": int,
            "badges": List[str]
        }
        types_repas: ["petit_déjeuner", "déjeuner", "dîner"]
        on_meal_click: Callback(meal)
        key: Clé unique
    """
    ICONS = {
        "petit_déjeuner": "🌅",
        "déjeuner": "☀️",
        "goûter": "🍪",
        "dîner": "🌙"
    }

    for type_repas in types_repas:
        meal = next((m for m in meals if m["type"] == type_repas), None)

        icon = ICONS.get(type_repas, "🍽️")
        st.markdown(f"**{icon} {type_repas.replace('_', ' ').title()}**")

        if meal and meal.get("recette"):
            recette = meal["recette"]

            col1, col2 = st.columns([1, 3])

            with col1:
                if recette.get("url_image"):
                    st.image(recette["url_image"], use_container_width=True)

            with col2:
                st.markdown(f"**{recette['nom']}**")

                if meal.get("badges"):
                    st.caption(" • ".join(meal["badges"]))

                if meal.get("portions"):
                    st.caption(f"🍽️ {meal['portions']} portions")

                if on_meal_click:
                    if st.button(
                            "👁️ Détails",
                            key=f"{key}_{type_repas}_{meal['id']}",
                            use_container_width=True
                    ):
                        on_meal_click(meal)
        else:
            st.info("Aucun repas planifié")

        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# SÉLECTEUR DE RECETTES
# ═══════════════════════════════════════════════════════════════

def render_recipe_selector(
        recipes: List[Dict],
        selected_id: Optional[int] = None,
        on_select: Optional[Callable[[Dict], None]] = None,
        filters: Optional[Dict] = None,
        key: str = "selector"
) -> Optional[Dict]:
    """
    Sélecteur de recettes avec recherche/filtres

    Args:
        recipes: Liste de recettes {
            "id": int,
            "nom": str,
            "temps_total": int,
            "portions": int,
            "tags": List[str]
        }
        selected_id: ID recette sélectionnée
        on_select: Callback(recette)
        filters: Filtres actifs
        key: Clé unique

    Returns:
        Recette sélectionnée ou None
    """
    # Recherche
    search = st.text_input(
        "🔍 Rechercher",
        placeholder="Nom de la recette...",
        key=f"{key}_search"
    )

    # Filtrer
    filtered = recipes

    if search:
        filtered = [
            r for r in filtered
            if search.lower() in r["nom"].lower()
        ]

    if filters:
        if filters.get("rapide"):
            filtered = [r for r in filtered if r.get("est_rapide")]
        if filters.get("bebe"):
            filtered = [r for r in filtered if r.get("compatible_bebe")]

    # Afficher
    if not filtered:
        st.info("Aucune recette trouvée")
        return None

    st.caption(f"{len(filtered)} recette(s)")

    selected_recipe = None

    for recipe in filtered[:20]:  # Limiter à 20
        is_selected = recipe["id"] == selected_id

        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            label = f"✅ {recipe['nom']}" if is_selected else recipe['nom']
            st.markdown(f"**{label}**")

            tags = recipe.get("tags", [])
            if tags:
                st.caption(" • ".join(tags[:3]))

        with col2:
            st.caption(f"⏱️ {recipe['temps_total']}min")
            st.caption(f"🍽️ {recipe['portions']}p")

        with col3:
            if st.button(
                    "Choisir" if not is_selected else "✓",
                    key=f"{key}_select_{recipe['id']}",
                    disabled=is_selected,
                    use_container_width=True
            ):
                selected_recipe = recipe
                if on_select:
                    on_select(recipe)

    return selected_recipe


# ═══════════════════════════════════════════════════════════════
# INDICATEURS PLANNING
# ═══════════════════════════════════════════════════════════════

def render_planning_stats(
        stats: Dict[str, Any],
        highlight_metrics: Optional[List[str]] = None,
        key: str = "stats"
):
    """
    Indicateurs du planning

    Args:
        stats: {
            "total_repas": 21,
            "repas_bebe": 7,
            "temps_moyen": 35,
            "budget_estime": 120.0
        }
        highlight_metrics: Métriques à mettre en avant
        key: Clé unique
    """
    metrics_config = {
        "total_repas": {"label": "Repas planifiés", "icon": "🍽️"},
        "repas_bebe": {"label": "Adapté bébé", "icon": "👶"},
        "repas_batch": {"label": "Batch cooking", "icon": "🍳"},
        "temps_moyen": {"label": "Temps moyen", "icon": "⏱️", "suffix": "min"},
        "budget_estime": {"label": "Budget estimé", "icon": "💶", "suffix": "€"},
    }

    # Filtrer métriques à afficher
    if highlight_metrics:
        display_stats = {k: v for k, v in stats.items() if k in highlight_metrics}
    else:
        display_stats = stats

    cols = st.columns(len(display_stats))

    for idx, (key_name, value) in enumerate(display_stats.items()):
        config = metrics_config.get(key_name, {"label": key_name, "icon": "📊"})

        with cols[idx]:
            suffix = config.get("suffix", "")
            st.metric(
                f"{config['icon']} {config['label']}",
                f"{value}{suffix}"
            )


# ═══════════════════════════════════════════════════════════════
# PLANNING VIDE
# ═══════════════════════════════════════════════════════════════

def render_empty_planning(
        message: str = "Aucun planning pour cette semaine",
        actions: Optional[List[Dict]] = None,
        key: str = "empty"
):
    """
    État vide du planning avec actions

    Args:
        message: Message à afficher
        actions: [{"label": str, "callback": Callable, "type": str}]
        key: Clé unique
    """
    st.markdown(
        f"""
        <div style="text-align: center; padding: 3rem; color: #6c757d;">
            <div style="font-size: 4rem;">📅</div>
            <div style="font-size: 1.5rem; margin-top: 1rem;">{message}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if actions:
        cols = st.columns(len(actions))

        for idx, action in enumerate(actions):
            with cols[idx]:
                button_type = action.get("type", "secondary")

                if st.button(
                        action["label"],
                        key=f"{key}_action_{idx}",
                        type=button_type,
                        use_container_width=True
                ):
                    action["callback"]()


# ═══════════════════════════════════════════════════════════════
# PRÉVISUALISATION PLANNING
# ═══════════════════════════════════════════════════════════════

def render_planning_preview(
        planning_data: Dict,
        editable: bool = False,
        on_edit: Optional[Callable[[str, Any], None]] = None,
        key: str = "preview"
):
    """
    Prévisualisation d'un planning avant validation

    Args:
        planning_data: {
            "nom": str,
            "semaine_debut": date,
            "nb_repas": int,
            "recettes": List[Dict]
        }
        editable: Permet édition inline
        on_edit: Callback(field, new_value)
        key: Clé unique
    """
    st.markdown("### 👁️ Prévisualisation")

    col1, col2 = st.columns(2)

    with col1:
        if editable and on_edit:
            nom = st.text_input(
                "Nom du planning",
                value=planning_data.get("nom", ""),
                key=f"{key}_nom"
            )
            if nom != planning_data.get("nom"):
                on_edit("nom", nom)
        else:
            st.markdown(f"**Nom:** {planning_data.get('nom', '—')}")

        st.markdown(f"**Semaine:** {planning_data['semaine_debut'].strftime('%d/%m/%Y')}")

    with col2:
        st.metric("Repas planifiés", planning_data.get("nb_repas", 0))
        st.metric("Recettes uniques", len(set(
            r["nom"] for r in planning_data.get("recettes", [])
        )))

    st.markdown("---")

    # Liste des recettes
    if planning_data.get("recettes"):
        st.markdown("**📋 Recettes utilisées**")

        recettes_grouped = {}
        for recette in planning_data["recettes"]:
            nom = recette["nom"]
            if nom not in recettes_grouped:
                recettes_grouped[nom] = 0
            recettes_grouped[nom] += 1

        for nom, count in recettes_grouped.items():
            st.write(f"• {nom} ({count}x)")