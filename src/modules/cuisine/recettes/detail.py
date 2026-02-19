"""
Détail d'une recette - Affichage complet avec historique et versions.
"""

import random
import time

import streamlit as st

from src.services.cuisine.recettes import get_recette_service

from .generation_image import render_generer_image
from .utils import formater_quantite


def render_detail_recette(recette):
    """Affiche les détails d'une recette avec badges, historique et versions"""
    service = get_recette_service()

    # En-tête
    col1, col2 = st.columns([3, 1])
    with col1:
        st.header(recette.nom)
    with col2:
        if recette.difficulte == "facile":
            st.markdown("# 🟢")
        elif recette.difficulte == "moyen":
            st.markdown("# 🟡")
        elif recette.difficulte == "difficile":
            st.markdown("# 🔴")

    # Image si disponible
    if recette.url_image:
        try:
            st.image(recette.url_image, caption=recette.nom, width=400)
        except Exception:
            st.caption("🖼️ Image indisponible")
    else:
        # Placeholder visuel
        food_emojis = [
            "🍽️",
            "🍳",
            "🥘",
            "🍲",
            "🥗",
            "🍜",
            "🍱",
            "🥙",
            "🍕",
            "🥟",
            "🍝",
            "🥜",
        ]
        emoji = random.choice(food_emojis)
        col = st.columns(1)[0]
        with col:
            st.markdown(
                f"<div style='text-align: center; font-size: 80px; opacity: 0.3;'>{emoji}</div>",
                unsafe_allow_html=True,
            )

    # Section génération d'image (fusionnée en une seule)
    render_generer_image(recette)

    # Badges et caractéristiques
    badges = []
    if recette.est_bio:
        badges.append("🌱 Bio")
    if recette.est_local:
        badges.append("🚜 Local")
    if recette.est_rapide:
        badges.append("⚡ Rapide")
    if recette.est_equilibre:
        badges.append("💪 Équilibré")
    if recette.congelable:
        badges.append("â„ï¸ Congélable")
    if badges:
        st.markdown(" • ".join(badges))

    # Scores bio et local
    if (recette.score_bio or 0) > 0 or (recette.score_local or 0) > 0:
        score_col1, score_col2 = st.columns(2)
        with score_col1:
            if (recette.score_bio or 0) > 0:
                st.metric("🌱 Score Bio", f"{recette.score_bio}%", delta=None)
        with score_col2:
            if (recette.score_local or 0) > 0:
                st.metric("🚜 Score Local", f"{recette.score_local}%", delta=None)

    # Robots compatibles
    if recette.robots_compatibles:
        robots_icons = {
            "Cookeo": ("🤖", "Cookeo"),
            "Monsieur Cuisine": ("👨‍🍳", "Monsieur Cuisine"),
            "Airfryer": ("🌪️", "Airfryer"),
            "Multicooker": ("🍳", "Multicooker"),
        }
        st.markdown("**🤖 Compatible avec:**")
        robot_cols = st.columns(len(recette.robots_compatibles))
        for idx, robot in enumerate(recette.robots_compatibles):
            icon, label = robots_icons.get(robot, ("🤖", robot.replace("_", " ").title()))
            robot_cols[idx].metric(icon, label)

    # Infos principales
    metric_cols = st.columns(4)
    with metric_cols[0]:
        st.metric("⏱️ Préparation", f"{recette.temps_preparation} min")
    with metric_cols[1]:
        st.metric("🍳 Cuisson", f"{recette.temps_cuisson} min")
    with metric_cols[2]:
        st.metric("👥 Portions", recette.portions)
    with metric_cols[3]:
        if recette.calories:
            st.metric("🔥 Calories", f"{recette.calories} kcal")
        else:
            st.metric("🔥 Calories", "─")

    # Nutrition complète
    if any([recette.calories, recette.proteines, recette.lipides, recette.glucides]):
        with st.expander("📊 Nutrition détaillée", expanded=False):
            nutrition_cols = st.columns(4)
            if recette.calories:
                nutrition_cols[0].metric("Calories", f"{recette.calories} kcal")
            if recette.proteines:
                nutrition_cols[1].metric("Protéines", f"{recette.proteines}g")
            if recette.lipides:
                nutrition_cols[2].metric("Lipides", f"{recette.lipides}g")
            if recette.glucides:
                nutrition_cols[3].metric("Glucides", f"{recette.glucides}g")

    # Description
    if recette.description:
        st.markdown("### 📝 Description")
        st.write(recette.description)

    # Ingrédients
    if recette.ingredients:
        st.markdown("### 🛒 Ingrédients")
        ingredient_cols = st.columns([2, 1, 1])
        ingredient_cols[0].markdown("**Ingrédient**")
        ingredient_cols[1].markdown("**Quantité**")
        ingredient_cols[2].markdown("**Unité**")
        st.divider()
        for ri in recette.ingredients:
            ingredient_cols = st.columns([2, 1, 1])
            ingredient_cols[0].write(f"{ri.ingredient.nom}")
            quantite_display = formater_quantite(ri.quantite)
            ingredient_cols[1].write(f"{quantite_display}")
            ingredient_cols[2].write(f"{ri.unite}")

    # Étapes de préparation
    if recette.etapes:
        st.markdown("### 👨‍🍳 Étapes de préparation")
        for etape in sorted(recette.etapes, key=lambda e: e.ordre or 0):
            st.markdown(f"**Étape {etape.ordre}:** {etape.description}")

    # Historique d'utilisation
    st.divider()
    st.markdown("### 📊 Historique d'utilisation")

    if service:
        stats = service.get_stats_recette(recette.id)

        stat_cols = st.columns(5)
        stat_cols[0].metric("🍽️ Cuissons", stats.get("nb_cuissons", 0))
        if stats.get("derniere_cuisson"):
            stat_cols[1].metric("📅 Dernière", stats.get("jours_depuis_derniere", "?"), "jours")
        if stats.get("note_moyenne"):
            stat_cols[2].metric("⭐ Note moyenne", f"{stats.get('note_moyenne', 0):.1f}/5")
        stat_cols[3].metric("👥 Total portions", stats.get("total_portions", 0))

        # Bouton pour enregistrer une cuisson
        col_a, col_b, col_c = st.columns([2, 1, 2])
        with col_b:
            if st.button("✅ Cuisinée aujourd'hui!", use_container_width=True):
                with st.form("form_enregistrer_cuisson"):
                    portions = st.number_input(
                        "Portions cuisinées", min_value=1, max_value=20, value=recette.portions
                    )
                    note = st.slider("Note (0-5 étoiles)", 0, 5, 0)
                    avis = st.text_area("Avis personnel (optionnel)")

                    if st.form_submit_button("Enregistrer"):
                        if service.enregistrer_cuisson(
                            recette.id, portions, note if note > 0 else None, avis if avis else None
                        ):
                            st.success("✅ Cuisson enregistrée!")
                            st.rerun()
                        else:
                            st.error("❌ Erreur lors de l'enregistrement")

        # Historique des 5 dernières cuissons
        historique = service.get_historique(recette.id, nb_dernieres=5)
        if historique:
            with st.expander("📜 5 dernières utilisations", expanded=True):
                for h in historique:
                    col_date, col_portions, col_note = st.columns([1, 1, 1])
                    with col_date:
                        st.caption(f"📅 {h.date_cuisson.strftime('%d/%m/%Y')}")
                    with col_portions:
                        st.caption(f"👥 {h.portions_cuisinees} portions")
                    with col_note:
                        if h.note:
                            st.caption(f"⭐ {h.note}/5")
                    if h.avis:
                        st.caption(f"💭 {h.avis}")
                    st.divider()

    # Versions (bébé, batch cooking, robots)
    st.divider()
    st.markdown("### 🎯 Versions adaptées")

    if service:
        versions = service.get_versions(recette.id)

        # Créer tabs pour les différents types
        tab_list = ["📋 Versions existantes", "⏰ Générer avec IA"]

        # Ajouter tab robots si compatibles
        robots_compatibles = []
        if recette.compatible_cookeo:
            robots_compatibles.append("Cookeo")
        if recette.compatible_monsieur_cuisine:
            robots_compatibles.append("Monsieur Cuisine")
        if recette.compatible_airfryer:
            robots_compatibles.append("Airfryer")
        if recette.compatible_multicooker:
            robots_compatibles.append("Multicooker")

        if robots_compatibles:
            tab_list.insert(1, "🤖 Robots compatibles")

        tab_versions = st.tabs(tab_list)

        with tab_versions[0]:
            if versions:
                for version in versions:
                    if version.type_version == "bébé":
                        icon = "👶"
                    elif version.type_version == "batch cooking":
                        icon = "🍳"
                    else:
                        icon = "📋"

                    with st.expander(f"{icon} Version {version.type_version}"):
                        if version.instructions_modifiees:
                            st.markdown("**Instructions adaptées:**")
                            st.write(version.instructions_modifiees)

                        if version.notes_bebe:
                            st.info(version.notes_bebe)

                        if (
                            version.type_version == "batch cooking"
                            and version.etapes_paralleles_batch
                        ):
                            st.markdown("**Étapes parallèles:**")
                            for etape in version.etapes_paralleles_batch:
                                st.caption(f"• {etape}")

                        if version.temps_optimise_batch:
                            st.caption(
                                f"â±ï¸ Temps optimisé: {version.temps_optimise_batch} minutes"
                            )
            else:
                st.info("Aucune version adaptée générée.")

        # Afficher onglet robots si compatible
        if robots_compatibles:
            with tab_versions[1]:
                st.markdown("### 🤖 Robots de cuisine compatibles")

                robot_info = {
                    "Cookeo": {
                        "icon": "🍲",
                        "desc": "Fait-tout multicuiseur sous pression",
                        "temps": "Généralement réduit de 30-40%",
                        "conseils": [
                            "Utilise le mode haute pression pour cuisson plus rapide",
                            "Réduis légèrement les liquides",
                            "Ajoute les ingrédients sensibles à la fin",
                        ],
                    },
                    "Monsieur Cuisine": {
                        "icon": "👨‍🍳",
                        "desc": "Robot cuiseur multifonction",
                        "temps": "Généralement similaire ou réduit",
                        "conseils": [
                            "Utilise les programmes automatiques si disponibles",
                            "Réduis les portions pour éviter le débordement",
                            "Contrôle régulièrement la cuisson",
                        ],
                    },
                    "Airfryer": {
                        "icon": "🌪️",
                        "desc": "Friteuse à air chaud",
                        "temps": "Généralement réduit de 20-30%",
                        "conseils": [
                            "Coupe les aliments en tailles uniformes",
                            "Secoue le panier à mi-cuisson",
                            "N'empile pas trop les aliments",
                        ],
                    },
                    "Multicooker": {
                        "icon": "🍳",
                        "desc": "Cuiseur multifonctions programmable",
                        "temps": "Généralement similaire",
                        "conseils": [
                            "Choisissez le programme approprié à la recette",
                            "Suivez les instructions du fabricant",
                            "Testez pour ajuster les temps",
                        ],
                    },
                }

                for robot in robots_compatibles:
                    info = robot_info.get(robot, {})
                    with st.expander(f"{info.get('icon', '🤖')} {robot}", expanded=False):
                        st.write(f"**Description:** {info.get('desc', '')}")
                        st.write(f"**Temps de cuisson:** {info.get('temps', '')}")

                        if info.get("conseils"):
                            st.markdown("**Conseils d'adaptation:**")
                            for conseil in info.get("conseils", []):
                                st.caption(f"• {conseil}")

        # Onglet génération
        generation_tab_idx = 2 if robots_compatibles else 1
        with tab_versions[generation_tab_idx]:
            st.markdown("### ⏰ Générer des versions adaptées")

            # Versions standards
            col1, col2 = st.columns(2)
            with col1:
                if st.button("👶 Générer version bébé", use_container_width=True):
                    with st.spinner("🤖 L'IA adapte la recette..."):
                        try:
                            version = service.generer_version_bebe(recette.id)
                            if version:
                                st.success("✅ Version bébé créée!")
                                st.rerun()
                            else:
                                st.error("❌ Erreur lors de la génération (version=None)")
                        except Exception as e:
                            st.error(f"❌ Erreur: {str(e)}")

            with col2:
                if st.button("🍳 Générer version batch cooking", use_container_width=True):
                    with st.spinner("🤖 L'IA optimise la recette pour le batch cooking..."):
                        try:
                            version = service.generer_version_batch_cooking(recette.id)
                            if version:
                                st.success("✅ Version batch cooking créée!")
                                st.rerun()
                            else:
                                st.error("❌ Erreur lors de la génération")
                        except Exception as e:
                            st.error(f"❌ Erreur: {str(e)}")

            # Versions robots si compatibles
            if robots_compatibles:
                st.markdown("---")
                st.markdown("### 🤖 Générer pour robots de cuisine")

                robot_buttons = {
                    "Cookeo": ("🍲", "cookeo"),
                    "Monsieur Cuisine": ("👨‍🍳", "monsieur_cuisine"),
                    "Airfryer": ("🌪️", "airfryer"),
                    "Multicooker": ("🍳", "multicooker"),
                }

                # Créer colonnes pour les boutons disponibles
                available_robots = list(robots_compatibles)
                if available_robots:
                    cols = st.columns(len(available_robots))
                    for idx, robot_name in enumerate(available_robots):
                        icon, robot_key = robot_buttons.get(robot_name, ("🤖", robot_name.lower()))
                        with cols[idx]:
                            if st.button(
                                f"{icon} {robot_name}",
                                use_container_width=True,
                                key=f"gen_robot_{robot_key}",
                            ):
                                with st.spinner(f"🤖 L'IA adapte pour {robot_name}..."):
                                    try:
                                        version = service.generer_version_robot(
                                            recette.id, robot_key
                                        )
                                        if version:
                                            st.success(f"✅ Version {robot_name} créée!")
                                            st.rerun()
                                        else:
                                            st.error("❌ Erreur lors de la génération")
                                    except Exception as e:
                                        st.error(f"❌ Erreur: {str(e)}")

    # Actions sur la recette
    st.divider()
    st.markdown("### ⚙️ Actions")

    action_cols = st.columns(3)

    with action_cols[0]:
        if st.button("✏️ Modifier", use_container_width=True, key="btn_modifier_recette"):
            st.session_state.edit_mode_recette = recette.id
            st.rerun()

    with action_cols[1]:
        if st.button("📋 Dupliquer", width="stretch", key="btn_dupliquer_recette"):
            if service:
                try:
                    with st.spinner("Duplication en cours..."):
                        from datetime import datetime

                        recette_dict = {
                            "nom": f"{recette.nom} (copie)",
                            "description": recette.description,
                            "type_repas": recette.type_repas,
                            "categorie": recette.categorie,
                            "temps_preparation": recette.temps_preparation,
                            "temps_cuisson": recette.temps_cuisson,
                            "portions": recette.portions,
                            "difficulte": recette.difficulte,
                            "saison": recette.saison,
                            "calories": recette.calories,
                            "proteines": recette.proteines,
                            "lipides": recette.lipides,
                            "glucides": recette.glucides,
                            "updated_at": datetime.utcnow(),
                        }
                        service.create(recette_dict)
                        st.success("✅ Recette dupliquée!")
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")

    with action_cols[2]:
        with st.popover("🗑️ Supprimer", use_container_width=True):
            st.warning(f"⚠️ Êtes-vous sûr de vouloir supprimer:\n\n**{recette.nom}** ?")
            col_oui, col_non = st.columns(2)
            with col_oui:
                if st.button(
                    "✅ Oui, supprimer", use_container_width=True, key="btn_confirmer_suppression"
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
            with col_non:
                if st.button("❌ Annuler", use_container_width=True, key="btn_annuler_suppression"):
                    st.rerun()


__all__ = ["render_detail_recette"]
