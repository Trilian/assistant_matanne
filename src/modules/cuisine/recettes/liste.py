"""
Liste des recettes - Affichage et pagination.
"""

import html
import random
import time

import streamlit as st

from src.services.cuisine.recettes import obtenir_service_recettes
from src.ui import etat_vide
from src.ui.fragments import ui_fragment
from src.ui.keys import KeyNamespace

_keys = KeyNamespace("recettes_liste")


@ui_fragment
def afficher_liste():
    """Affiche la liste des recettes avec pagination"""
    service = obtenir_service_recettes()

    if service is None:
        st.error("❌ Service recettes indisponible")
        return

    # Initialiser pagination
    if "recettes_page" not in st.session_state:
        st.session_state.recettes_page = 0

    if "recettes_page_size" not in st.session_state:
        st.session_state.recettes_page_size = 9

    # Contrôles de pagination en haut
    col_size1, col_size2, col_size3 = st.columns([2, 1.5, 2])
    with col_size1:
        st.caption("👁️ Options d'affichage")
    with col_size2:
        page_size = st.selectbox(
            "Recettes/page",
            [6, 9, 12, 15],
            index=[6, 9, 12, 15].index(st.session_state.recettes_page_size),
            key=_keys("page_size"),
            label_visibility="collapsed",
        )
        st.session_state.recettes_page_size = page_size
    with col_size3:
        st.write("")  # Espacement

    PAGE_SIZE = st.session_state.recettes_page_size

    # Filtres
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

    # Chercher les recettes
    type_repas_filter = None if type_repas == "Tous" else type_repas
    difficulte_filter = None if difficulte == "Tous" else difficulte

    recettes = service.search_advanced(
        type_repas=type_repas_filter,
        difficulte=difficulte_filter,
        temps_max=temps_max,
        limit=200,
    )

    # Appliquer filtres en mémoire (remplace Specification pattern)
    if nom_filter and nom_filter.strip():
        search_term = nom_filter.strip().lower()
        recettes = [r for r in recettes if search_term in r.nom.lower()]

    # Filtres avancés: scores
    if min_score_bio > 0:
        recettes = [r for r in recettes if getattr(r, "score_bio", 0) or 0 >= min_score_bio]
    if min_score_local > 0:
        recettes = [r for r in recettes if getattr(r, "score_local", 0) or 0 >= min_score_local]

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

    # Pagination
    total_pages = (len(recettes) + PAGE_SIZE - 1) // PAGE_SIZE
    st.session_state.recettes_page = min(st.session_state.recettes_page, total_pages - 1)

    start_idx = st.session_state.recettes_page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    page_recettes = recettes[start_idx:end_idx]

    st.success(
        f"✅ {len(recettes)} recette(s) trouvée(s) | Page {st.session_state.recettes_page + 1}/{total_pages}"
    )

    # Afficher en grid avec badges
    cols = st.columns(3, gap="small")
    for idx, recette in enumerate(page_recettes):
        with cols[idx % 3]:
            # Container avec flexbox minimal
            with st.container(border=True):
                # Image avec hauteur RÉDUITE (100px) et conteneur strictement dimensionné
                if recette.url_image:
                    try:
                        st.markdown(
                            f'<div style="height: 100px; width: 100%; overflow: hidden; border-radius: 6px; margin-bottom: 6px; background: linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%); display: flex; align-items: center; justify-content: center;"><img src="{recette.url_image}" loading="lazy" decoding="async" alt="{recette.nom}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 6px;" /></div>',
                            unsafe_allow_html=True,
                        )
                    except Exception:
                        st.markdown(
                            '<div style="height: 100px; width: 100%; border-radius: 6px; margin-bottom: 6px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; font-size: 40px; opacity: 0.3;">🖼️</div>',
                            unsafe_allow_html=True,
                        )
                else:
                    food_emojis = ["🍽️", "🍳", "🥘", "🍲", "🥗", "🍜"]
                    emoji = random.choice(food_emojis)
                    st.markdown(
                        f'<div style="height: 100px; width: 100%; border-radius: 6px; margin-bottom: 6px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; font-size: 40px; opacity: 0.3;">{emoji}</div>',
                        unsafe_allow_html=True,
                    )

                # Titre et infos compactes - HAUTEUR FIXE
                difficulty_emoji = {"facile": "🟢", "moyen": "🟡", "difficile": "🔴"}.get(
                    recette.difficulte, "âš«"
                )

                # Échapper le nom pour éviter les problèmes d'encodage
                nom_echappé = html.escape(recette.nom, quote=True)
                st.markdown(
                    f"<h4 style='margin: 6px 0; line-height: 1.3; font-size: 15px; min-height: 3.9em; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; word-break: break-word;'>{difficulty_emoji} {nom_echappé}</h4>",
                    unsafe_allow_html=True,
                )

                # Description sur hauteur fixe pour éviter décalage
                if recette.description:
                    # Limiter à ~250 caractères pour laisser la CSS faire le clamp sur 3 lignes
                    desc = recette.description
                    # Tronquer à limite mais sans couper mid-word
                    if len(desc) > 250:
                        truncated = desc[:250]
                        last_space = truncated.rfind(" ")
                        if last_space > 150:
                            desc = truncated[:last_space] + "..."
                        else:
                            desc = truncated + "..."
                    st.markdown(
                        f"<p style='margin: 4px 0; font-size: 11px; opacity: 0.7; min-height: 3.3em; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical;'>{desc}</p>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        "<p style='margin: 4px 0; font-size: 11px; opacity: 0; min-height: 3.3em;'>&nbsp;</p>",
                        unsafe_allow_html=True,
                    )

                # Badges et robots sur la même ligne
                badge_definitions = {
                    "🌱": "Bio",
                    "🚜": "Local",
                    "⚡": "Rapide",
                    "💪": "Équilibré",
                    "❄️": "Congélable",
                }

                all_badges = []

                if recette.est_bio:
                    all_badges.append(
                        f'<span title="{badge_definitions["🌱"]}" style="cursor: help;">🌱</span>'
                    )
                if recette.est_local:
                    all_badges.append(
                        f'<span title="{badge_definitions["🚜"]}" style="cursor: help;">🚜</span>'
                    )
                if recette.est_rapide:
                    all_badges.append(
                        f'<span title="{badge_definitions["⚡"]}" style="cursor: help;">⚡</span>'
                    )
                if recette.est_equilibre:
                    all_badges.append(
                        f'<span title="{badge_definitions["💪"]}" style="cursor: help;">💪</span>'
                    )
                if recette.congelable:
                    all_badges.append(
                        f'<span title="{badge_definitions["❄️"]}" style="cursor: help;">❄️</span>'
                    )

                if recette.robots_compatibles:
                    robots_icons = {
                        "Cookeo": ("🤖", "Cookeo"),
                        "Monsieur Cuisine": ("👨‍🍳", "MC"),
                        "Airfryer": ("🌪️", "Airfryer"),
                        "Multicooker": ("🍳", "MC"),
                    }
                    for robot in recette.robots_compatibles:
                        icon, tooltip = robots_icons.get(robot, ("🤖", robot))
                        all_badges.append(
                            f'<span title="{tooltip}" style="cursor: help;">{icon}</span>'
                        )

                if all_badges:
                    all_badges_html = " ".join(all_badges)
                    st.markdown(
                        f"<p style='margin: 2px 0; font-size: 13px;'>{all_badges_html}</p>",
                        unsafe_allow_html=True,
                    )

                st.divider()

                # Infos principales (3 colonnes compactes)
                info_cols = st.columns(3, gap="small")
                with info_cols[0]:
                    st.markdown(
                        f"<div style='text-align: center; font-size: 13px;'><div>â±ï¸</div><div style='font-weight: bold;'>{recette.temps_preparation}m</div></div>",
                        unsafe_allow_html=True,
                    )
                with info_cols[1]:
                    st.markdown(
                        f"<div style='text-align: center; font-size: 13px;'><div>👥</div><div style='font-weight: bold;'>{recette.portions}</div></div>",
                        unsafe_allow_html=True,
                    )
                with info_cols[2]:
                    cal = recette.calories if recette.calories else "─"
                    st.markdown(
                        f"<div style='text-align: center; font-size: 13px;'><div>🔥</div><div style='font-weight: bold;'>{cal}</div></div>",
                        unsafe_allow_html=True,
                    )

                # Bouton voir détails
                if st.button(
                    "👁️ Voir détails", use_container_width=True, key=_keys("detail", recette.id)
                ):
                    st.session_state.detail_recette_id = recette.id
                    st.rerun()

                # Bouton supprimer avec popover confirmation
                with st.popover("🗑️ Supprimer", width="stretch"):
                    st.warning(f"⚠️ Êtes-vous sûr de vouloir supprimer:\n\n**{recette.nom}** ?")
                    col_del_oui, col_del_non = st.columns(2)
                    with col_del_oui:
                        if st.button(
                            "✅ Oui, supprimer", width="stretch", key=_keys("del_oui", recette.id)
                        ):
                            if service:
                                try:
                                    with st.spinner("Suppression en cours..."):
                                        if service.delete(recette.id):
                                            st.success("✅ Recette supprimée!")
                                            st.session_state.detail_recette_id = None
                                            time.sleep(1)
                                            st.rerun()
                                        else:
                                            st.error("❌ Impossible de supprimer la recette")
                                except Exception as e:
                                    st.error(f"❌ Erreur lors de la suppression: {str(e)}")
                    with col_del_non:
                        if st.button(
                            "❌ Annuler", width="stretch", key=_keys("del_non", recette.id)
                        ):
                            st.rerun()

    # Pagination controls
    st.divider()
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.session_state.recettes_page > 0:
            if st.button("⬅️ Précédent"):
                st.session_state.recettes_page -= 1
                st.rerun()

    with col3:
        st.write(f"Page {st.session_state.recettes_page + 1}/{total_pages}")

    with col5:
        if st.session_state.recettes_page < total_pages - 1:
            if st.button("Suivant ➡️"):
                st.session_state.recettes_page += 1
                st.rerun()


__all__ = ["afficher_liste"]
