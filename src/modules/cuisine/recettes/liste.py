"""
Liste des recettes - Affichage style Marmiton avec catégories et pagination.
"""

import html
import random
import time
from pathlib import Path

import streamlit as st

from src.core.session_keys import SK
from src.core.state import rerun
from src.services.cuisine.recettes import obtenir_service_recettes
from src.ui import etat_vide
from src.ui.fragments import ui_fragment
from src.ui.keys import KeyNamespace

_keys = KeyNamespace("recettes_liste")

# Couleurs par catégorie pour les badges
_CAT_COLORS = {
    "Plat": "#4CAF50",
    "Entrée": "#2196F3",
    "Dessert": "#FF9800",
    "Accompagnement": "#9C27B0",
    "Apéritif": "#F44336",
    "Petit-déjeuner": "#795548",
    "Goûter": "#E91E63",
}

# Catégories pour les onglets
_CATEGORIE_TABS = ["Tous", "Entrées", "Plats", "Desserts", "Accompagnements", "Autres"]
_CAT_TAB_MAP = {
    "Entrées": "Entrée",
    "Plats": "Plat",
    "Desserts": "Dessert",
    "Accompagnements": "Accompagnement",
}
_MAIN_CATS = {"Entrée", "Plat", "Dessert", "Accompagnement"}


def _afficher_image(recette):
    """Affiche l'image d'une recette (locale ou URL)."""
    if recette.url_image:
        # Chemin local
        if not recette.url_image.startswith("http") and Path(recette.url_image).exists():
            st.image(recette.url_image, use_container_width=True)
        else:
            try:
                nom_safe = html.escape(recette.nom, quote=True)
                st.markdown(
                    f'<div style="height: 160px; width: 100%; overflow: hidden; '
                    f'border-radius: 8px 8px 0 0; margin-bottom: 6px;">'
                    f'<img src="{recette.url_image}" loading="lazy" decoding="async" '
                    f'alt="{nom_safe}" style="width: 100%; height: 100%; object-fit: cover;" />'
                    f"</div>",
                    unsafe_allow_html=True,
                )
            except Exception:
                _afficher_placeholder()
    else:
        _afficher_placeholder()


def _afficher_placeholder():
    """Affiche un placeholder image."""
    food_emojis = ["🍽️", "🍳", "🥘", "🍲", "🥗", "🍜", "🥧", "🍰", "🥩", "🐟"]
    emoji = random.choice(food_emojis)
    st.markdown(
        f'<div style="height: 160px; width: 100%; border-radius: 8px 8px 0 0; '
        f"margin-bottom: 6px; "
        f"background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); "
        f"display: flex; align-items: center; justify-content: center; "
        f'font-size: 50px; opacity: 0.8;">{emoji}</div>',
        unsafe_allow_html=True,
    )


@ui_fragment
def afficher_liste():
    """Affiche la liste des recettes avec catégories style Marmiton et pagination."""
    service = obtenir_service_recettes()

    if service is None:
        st.error("❌ Service recettes indisponible")
        return

    # Initialiser pagination
    if _keys("page") not in st.session_state:
        st.session_state[_keys("page")] = 0

    # ── Onglets catégories ──
    selected_cat = st.radio(
        "Catégorie",
        _CATEGORIE_TABS,
        horizontal=True,
        key=_keys("cat_tab"),
        label_visibility="collapsed",
    )

    # ── Contrôles affichage ──
    col_size1, col_size2, col_size3 = st.columns([2, 1.5, 2])
    with col_size1:
        st.caption("👁️ Options d'affichage")
    with col_size2:
        page_size = st.selectbox(
            "Recettes/page",
            [6, 9, 12, 15],
            index=1,
            key=_keys("page_size_val"),
            label_visibility="collapsed",
        )
    with col_size3:
        st.write("")

    PAGE_SIZE = page_size

    # ── Filtres ──
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        nom_filter = st.text_input(
            "Chercher par nom",
            placeholder="ex: pâte, gâteau...",
            key=_keys("filter_nom"),
            label_visibility="collapsed",
        )
    with col2:
        type_repas = st.selectbox(
            "Type de repas",
            ["Tous", "petit_déjeuner", "déjeuner", "dîner", "goûter"],
            key=_keys("filter_type_repas"),
            label_visibility="collapsed",
        )
    with col3:
        difficulte = st.selectbox(
            "Difficulté",
            ["Tous", "facile", "moyen", "difficile"],
            key=_keys("filter_difficulte"),
            label_visibility="collapsed",
        )
    with col4:
        temps_max = st.number_input(
            "Temps max (min)",
            min_value=0,
            max_value=300,
            value=60,
            key=_keys("filter_temps"),
            label_visibility="collapsed",
        )

    # Filtres supplémentaires avancés
    with st.expander("⚙️ Filtres avancés", expanded=False):
        col_bio, col_local = st.columns(2)
        with col_bio:
            min_score_bio = st.slider(
                "🌱 Score bio min (%)", 0, 100, 0, key=_keys("filter_score_bio")
            )
        with col_local:
            min_score_local = st.slider(
                "🚜 Score local min (%)", 0, 100, 0, key=_keys("filter_score_local")
            )

        # Filtres robots
        st.markdown("**🤖 Compatible avec:**")
        col_robots = st.columns(4)
        robots_selected = {}
        with col_robots[0]:
            robots_selected["cookeo"] = st.checkbox("Cookeo", key=_keys("robot_cookeo"))
        with col_robots[1]:
            robots_selected["monsieur_cuisine"] = st.checkbox(
                "Monsieur Cuisine", key=_keys("robot_mc")
            )
        with col_robots[2]:
            robots_selected["airfryer"] = st.checkbox("Airfryer", key=_keys("robot_airfryer"))
        with col_robots[3]:
            robots_selected["multicooker"] = st.checkbox(
                "Multicooker", key=_keys("robot_multicooker")
            )

        # Filtres tags
        st.markdown("**🏷️ Caractéristiques:**")
        col_tags = st.columns(3)
        with col_tags[0]:
            est_rapide = st.checkbox("⚡ Rapide", key=_keys("tag_rapide"))
        with col_tags[1]:
            est_equilibre = st.checkbox("💪 Équilibré", key=_keys("tag_equilibre"))
        with col_tags[2]:
            congelable = st.checkbox("❄️ Congélable", key=_keys("tag_congelable"))

    # ── Recherche ──
    type_repas_filter = None if type_repas == "Tous" else type_repas
    difficulte_filter = None if difficulte == "Tous" else difficulte

    recettes = service.search_advanced(
        type_repas=type_repas_filter,
        difficulte=difficulte_filter,
        temps_max=temps_max,
        limit=200,
    )

    # Filtre par nom
    if nom_filter and nom_filter.strip():
        search_term = nom_filter.strip().lower()
        recettes = [r for r in recettes if search_term in r.nom.lower()]

    # Filtre par catégorie (onglet)
    if selected_cat != "Tous":
        if selected_cat == "Autres":
            recettes = [r for r in recettes if getattr(r, "categorie", "Plat") not in _MAIN_CATS]
        else:
            target_cat = _CAT_TAB_MAP.get(selected_cat, selected_cat)
            recettes = [r for r in recettes if getattr(r, "categorie", "Plat") == target_cat]

    # Filtres avancés: scores
    if min_score_bio > 0:
        recettes = [r for r in recettes if (getattr(r, "score_bio", 0) or 0) >= min_score_bio]
    if min_score_local > 0:
        recettes = [r for r in recettes if (getattr(r, "score_local", 0) or 0) >= min_score_local]

    # Filtres robots
    robot_mapping = {
        "cookeo": "Cookeo",
        "monsieur_cuisine": "Monsieur Cuisine",
        "airfryer": "Airfryer",
        "multicooker": "Multicooker",
    }
    for key, robot_name in robot_mapping.items():
        if robots_selected.get(key):
            recettes = [
                r for r in recettes if robot_name in (getattr(r, "robots_compatibles", None) or [])
            ]

    # Filtres tags
    if est_rapide:
        recettes = [r for r in recettes if getattr(r, "est_rapide", False)]
    if est_equilibre:
        recettes = [r for r in recettes if getattr(r, "est_equilibre", False)]
    if congelable:
        recettes = [r for r in recettes if getattr(r, "congelable", False)]

    if not recettes:
        etat_vide(
            "Aucune recette ne correspond à vos critères",
            "🍳",
            "Modifiez les filtres ou créez une recette",
        )
        return

    # ── Pagination ──
    total_pages = (len(recettes) + PAGE_SIZE - 1) // PAGE_SIZE
    st.session_state[_keys("page")] = min(st.session_state[_keys("page")], total_pages - 1)

    start_idx = st.session_state[_keys("page")] * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    page_recettes = recettes[start_idx:end_idx]

    st.caption(
        f"{len(recettes)} recette(s) · Page {st.session_state[_keys('page')] + 1}/{total_pages}"
    )

    # ── Grille de cartes style Marmiton ──
    cols = st.columns(3, gap="small")
    for idx, recette in enumerate(page_recettes):
        with cols[idx % 3]:
            with st.container(border=True):
                # Image plus grande
                _afficher_image(recette)

                # Badge catégorie
                cat = getattr(recette, "categorie", "Plat")
                cat_color = _CAT_COLORS.get(cat, "#757575")
                st.markdown(
                    f'<span style="background: {cat_color}; color: white; padding: 2px 10px; '
                    f'border-radius: 12px; font-size: 11px; font-weight: 500;">{cat}</span>',
                    unsafe_allow_html=True,
                )

                # Titre
                difficulty_emoji = {"facile": "🟢", "moyen": "🟡", "difficile": "🔴"}.get(
                    recette.difficulte, "⚫"
                )
                nom_safe = html.escape(recette.nom, quote=True)
                st.markdown(
                    f"<h4 style='margin: 6px 0 4px 0; line-height: 1.3; font-size: 15px; "
                    f"min-height: 2.6em; overflow: hidden; display: -webkit-box; "
                    f"-webkit-line-clamp: 2; -webkit-box-orient: vertical; "
                    f"word-break: break-word;'>{difficulty_emoji} {nom_safe}</h4>",
                    unsafe_allow_html=True,
                )

                # Ligne compacte: temps + difficulté + portions
                temps = recette.temps_preparation or 0
                st.markdown(
                    f"<div style='font-size: 12px; opacity: 0.7; margin-bottom: 4px;'>"
                    f"⏱️ {temps}min · {recette.difficulte} · 👥 {recette.portions} pers."
                    f"</div>",
                    unsafe_allow_html=True,
                )

                # Badges (bio, local, rapide, etc.)
                badges = []
                if recette.est_bio:
                    badges.append("🌱")
                if recette.est_local:
                    badges.append("🚜")
                if recette.est_rapide:
                    badges.append("⚡")
                if recette.est_equilibre:
                    badges.append("💪")
                if recette.congelable:
                    badges.append("❄️")
                if recette.robots_compatibles:
                    robots_icons = {
                        "Cookeo": "🤖",
                        "Monsieur Cuisine": "👨‍🍳",
                        "Airfryer": "🌪️",
                        "Multicooker": "🍳",
                    }
                    for robot in recette.robots_compatibles:
                        badges.append(robots_icons.get(robot, "🤖"))

                if badges:
                    st.markdown(
                        f"<p style='margin: 2px 0 6px 0; font-size: 14px;'>"
                        f"{' '.join(badges)}</p>",
                        unsafe_allow_html=True,
                    )

                # Bouton voir détails
                if st.button(
                    "Voir la recette",
                    use_container_width=True,
                    key=_keys("detail", recette.id),
                    type="primary",
                ):
                    st.session_state[_keys("detail_id")] = recette.id
                    st.session_state[SK.DETAIL_RECETTE_ID] = recette.id
                    rerun()

                # Bouton supprimer avec popover confirmation
                with st.popover("🗑️", use_container_width=True):
                    st.warning(f"Supprimer **{recette.nom}** ?")
                    col_del_oui, col_del_non = st.columns(2)
                    with col_del_oui:
                        if st.button(
                            "Oui", use_container_width=True, key=_keys("del_oui", recette.id)
                        ):
                            if service:
                                try:
                                    if service.delete(recette.id):
                                        st.success("Recette supprimée")
                                        st.session_state[SK.DETAIL_RECETTE_ID] = None
                                        time.sleep(1)
                                        rerun()
                                    else:
                                        st.error("Impossible de supprimer")
                                except Exception as e:
                                    st.error(f"Erreur: {e}")
                    with col_del_non:
                        if st.button(
                            "Non", use_container_width=True, key=_keys("del_non", recette.id)
                        ):
                            rerun()

    # ── Pagination controls ──
    st.divider()
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.session_state[_keys("page")] > 0:
            if st.button("⬅️ Précédent", key=_keys("prev")):
                st.session_state[_keys("page")] -= 1
                rerun()

    with col3:
        st.write(f"Page {st.session_state[_keys('page')] + 1}/{total_pages}")

    with col5:
        if st.session_state[_keys("page")] < total_pages - 1:
            if st.button("Suivant ➡️", key=_keys("next")):
                st.session_state[_keys("page")] += 1
                rerun()


__all__ = ["afficher_liste"]
