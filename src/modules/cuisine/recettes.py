"""
Module Recettes - Gestion complète des recettes
"""

import logging
import streamlit as st
from src.services.recettes import get_recette_service
from src.core.errors_base import ErreurValidation
from src.modules.cuisine.recettes_import import render_importer

logger = logging.getLogger(__name__)


def app():
    """Point d'entrée module recettes"""
    st.title("🍽️ Mes Recettes")
    st.caption("Gestion complète de votre base de recettes")

    # Gérer l'état de la vue détails
    if "detail_recette_id" not in st.session_state:
        st.session_state.detail_recette_id = None

    # Si une recette est sélectionnée, afficher son détail
    if st.session_state.detail_recette_id is not None:
        service = get_recette_service()
        if service is not None:
            recette = service.get_by_id_full(st.session_state.detail_recette_id)
            if recette:
                # Bouton retour en haut avec icône visible
                col_retour, col_titre = st.columns([1, 10])
                with col_retour:
                    if st.button("⬅️", help="Retour à la liste", use_container_width=True):
                        st.session_state.detail_recette_id = None
                        st.rerun()
                with col_titre:
                    st.write(f"**{recette.nom}**")
                st.divider()
                render_detail_recette(recette)
                return
        st.error("❌ Recette non trouvée")
        st.session_state.detail_recette_id = None

    # Sous-tabs
    tab_liste, tab_ajout, tab_import, tab_ia = st.tabs(["📋 Liste", "➕ Ajouter Manuel", "📥 Importer", "✨ Générer IA"])

    with tab_liste:
        render_liste()

    with tab_ajout:
        render_ajouter_manuel()
    
    with tab_import:
        render_importer()
    
    with tab_ia:
        render_generer_ia()


def render_liste():
    """Affiche la liste des recettes avec pagination"""
    service = get_recette_service()
    
    if service is None:
        st.error("❌ Service recettes indisponible")
        return
    
    # Initialiser pagination
    if "recettes_page" not in st.session_state:
        st.session_state.recettes_page = 0
    
    PAGE_SIZE = 9  # 3 colonnes x 3 lignes
    
    # Filtres
    col1, col2, col3 = st.columns(3)
    with col1:
        type_repas = st.selectbox(
            "Type de repas",
            ["Tous", "petit_déjeuner", "déjeuner", "dîner", "goûter"],
            key="filter_type_repas"
        )
    with col2:
        difficulte = st.selectbox(
            "Difficulté",
            ["Tous", "facile", "moyen", "difficile"],
            key="filter_difficulte"
        )
    with col3:
        temps_max = st.number_input(
            "Temps max (min)",
            min_value=0,
            max_value=300,
            value=60,
            key="filter_temps"
        )
    
    # Filtres supplémentaires avancés
    with st.expander("⚙️ Filtres avancés", expanded=False):
        col_bio, col_local = st.columns(2)
        with col_bio:
            min_score_bio = st.slider("🌱 Score bio min (%)", 0, 100, 0, key="filter_score_bio")
        with col_local:
            min_score_local = st.slider("📍 Score local min (%)", 0, 100, 0, key="filter_score_local")
        
        # Filtres robots
        st.markdown("**🤖 Compatible avec:**")
        col_robots = st.columns(4)
        robots_selected = {}
        with col_robots[0]:
            robots_selected['cookeo'] = st.checkbox("Cookeo", key="robot_cookeo")
        with col_robots[1]:
            robots_selected['monsieur_cuisine'] = st.checkbox("Monsieur Cuisine", key="robot_mc")
        with col_robots[2]:
            robots_selected['airfryer'] = st.checkbox("Airfryer", key="robot_airfryer")
        with col_robots[3]:
            robots_selected['multicooker'] = st.checkbox("Multicooker", key="robot_multicooker")
        
        # Filtres tags
        st.markdown("**🏷️ Caractéristiques:**")
        col_tags = st.columns(3)
        with col_tags[0]:
            est_rapide = st.checkbox("⚡ Rapide", key="tag_rapide")
        with col_tags[1]:
            est_equilibre = st.checkbox("💪 Équilibré", key="tag_equilibre")
        with col_tags[2]:
            congelable = st.checkbox("❄️ Congélable", key="tag_congelable")
    
    # Chercher les recettes
    type_repas_filter = None if type_repas == "Tous" else type_repas
    difficulte_filter = None if difficulte == "Tous" else difficulte
    
    recettes = service.search_advanced(
        type_repas=type_repas_filter,
        difficulte=difficulte_filter,
        temps_max=temps_max,
        limit=200,
    )
    
    # Appliquer les filtres avancés
    if min_score_bio > 0:
        recettes = [r for r in recettes if (r.score_bio or 0) >= min_score_bio]
    if min_score_local > 0:
        recettes = [r for r in recettes if (r.score_local or 0) >= min_score_local]
    
    # Filtres robots
    if any(robots_selected.values()):
        def has_robot(recette):
            if robots_selected.get('cookeo') and not recette.compatible_cookeo:
                return False
            if robots_selected.get('monsieur_cuisine') and not recette.compatible_monsieur_cuisine:
                return False
            if robots_selected.get('airfryer') and not recette.compatible_airfryer:
                return False
            if robots_selected.get('multicooker') and not recette.compatible_multicooker:
                return False
            return True
        recettes = [r for r in recettes if has_robot(r)]
    
    # Filtres tags
    if est_rapide:
        recettes = [r for r in recettes if r.est_rapide]
    if est_equilibre:
        recettes = [r for r in recettes if r.est_equilibre]
    if congelable:
        recettes = [r for r in recettes if r.congelable]
    
    if not recettes:
        st.info("Aucune recette ne correspond à vos critères. Créez-en une!")
        return
    
    # Pagination
    total_pages = (len(recettes) + PAGE_SIZE - 1) // PAGE_SIZE
    st.session_state.recettes_page = min(st.session_state.recettes_page, total_pages - 1)
    
    start_idx = st.session_state.recettes_page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    page_recettes = recettes[start_idx:end_idx]
    
    st.success(f"✅ {len(recettes)} recette(s) trouvée(s) | Page {st.session_state.recettes_page + 1}/{total_pages}")
    
    # Afficher en grid avec badges
    cols = st.columns(3, gap="small")
    for idx, recette in enumerate(page_recettes):
        with cols[idx % 3]:
            # Container avec hauteur fixe pour alignement parfait
            with st.container(border=True):
                st.markdown(f'''
                <div style="display: flex; flex-direction: column; height: 550px; justify-content: space-between;">
                ''', unsafe_allow_html=True)
                
                # Image si disponible (hauteur fixe)
                if recette.url_image:
                    try:
                        st.image(recette.url_image, use_column_width=True, width=250)
                    except Exception:
                        st.markdown('<div style="height: 180px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; border-radius: 8px;">🖼️</div>', unsafe_allow_html=True)
                else:
                    import random
                    food_emojis = ["🍽️", "🍳", "🥘", "🍲", "🥗", "🍜"]
                    emoji = random.choice(food_emojis)
                    st.markdown(f'<div style="height: 180px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; border-radius: 8px; font-size: 80px; opacity: 0.3;">{emoji}</div>', unsafe_allow_html=True)
                
                # Contenu (Difficulté + Nom + Description)
                difficulty_emoji = {"facile": "🟢", "moyen": "🟡", "difficile": "🔴"}.get(recette.difficulte, "⚪")
                st.markdown(f"<h4 style='margin: 8px 0; line-height: 1.2;'>{difficulty_emoji} {recette.nom}</h4>", unsafe_allow_html=True)
                
                if recette.description:
                    desc = recette.description[:65]
                    if len(recette.description) > 65:
                        desc += "..."
                    st.markdown(f"<p style='margin: 4px 0; font-size: 12px; opacity: 0.7;'>{desc}</p>", unsafe_allow_html=True)
                
                # Tags badges avec tooltips
                badge_definitions = {
                    "🌱": "Bio - Produit biologique",
                    "📍": "Local - Produit local",
                    "⚡": "Rapide - Recette rapide",
                    "💪": "Équilibré - Recette équilibrée",
                    "❄️": "Congélable - Peut être congelé"
                }
                
                tags = []
                if recette.est_bio:
                    tags.append("🌱")
                if recette.est_local:
                    tags.append("📍")
                if recette.est_rapide:
                    tags.append("⚡")
                if recette.est_equilibre:
                    tags.append("💪")
                if recette.congelable:
                    tags.append("❄️")
                
                if tags:
                    tags_html = " ".join([f'<span title="{badge_definitions.get(tag, tag)}" style="cursor: help;">{tag}</span>' for tag in tags])
                    st.markdown(f"<p style='margin: 4px 0;'>{tags_html}</p>", unsafe_allow_html=True)
                
                # Robots avec tooltips
                if recette.robots_compatibles:
                    robots_icons = {
                        'Cookeo': ('🤖', 'Compatible Cookeo'),
                        'Monsieur Cuisine': ('👨‍🍳', 'Compatible Monsieur Cuisine'),
                        'Airfryer': ('🌪️', 'Compatible Airfryer'),
                        'Multicooker': ('⏲️', 'Compatible Multicooker')
                    }
                    robot_html_list = []
                    for robot in recette.robots_compatibles:
                        icon, tooltip = robots_icons.get(robot, ('🤖', 'Robot compatible'))
                        robot_html_list.append(f'<span title="{tooltip}" style="cursor: help;">{icon}</span>')
                    robot_text = " ".join(robot_html_list)
                    st.markdown(f"<p style='margin: 4px 0; font-size: 12px;'>{robot_text}</p>", unsafe_allow_html=True)
                
                # Infos principales (3 colonnes)
                st.markdown("<div style='margin: 8px 0; border-top: 1px solid #ddd; border-bottom: 1px solid #ddd; padding: 8px 0;'>", unsafe_allow_html=True)
                info_cols = st.columns(3, gap="small")
                with info_cols[0]:
                    st.markdown(f"<div style='text-align: center;'><div style='font-size: 14px;'>⏱️</div><div style='font-size: 13px; font-weight: bold;'>{recette.temps_preparation}m</div></div>", unsafe_allow_html=True)
                with info_cols[1]:
                    st.markdown(f"<div style='text-align: center;'><div style='font-size: 14px;'>👥</div><div style='font-size: 13px; font-weight: bold;'>{recette.portions}</div></div>", unsafe_allow_html=True)
                with info_cols[2]:
                    cal = recette.calories if recette.calories else "—"
                    st.markdown(f"<div style='text-align: center;'><div style='font-size: 14px;'>🔥</div><div style='font-size: 13px; font-weight: bold;'>{cal}</div></div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Bouton voir détails (fixé en bas)
                if st.button(
                    "👁️ Voir détails",
                    use_container_width=True,
                    key=f"detail_{recette.id}"
                ):
                    st.session_state.detail_recette_id = recette.id
                    st.rerun()
                
                st.markdown("</div>", unsafe_allow_html=True)
    
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
            if st.button("Suivant ➡️"):
                st.session_state.recettes_page += 1
                st.rerun()


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
            st.image(recette.url_image, use_column_width=True, caption=recette.nom)
        except Exception:
            st.caption("🖼️ Image indisponible")
    else:
        # Placeholder visuel
        import random
        food_emojis = ["🍽️", "🍳", "🥘", "🍲", "🥗", "🍜", "🍱", "🥙", "🍛", "🥟", "🍚", "🥘"]
        emoji = random.choice(food_emojis)
        col = st.columns(1)[0]
        with col:
            st.markdown(f"<div style='text-align: center; font-size: 80px; opacity: 0.3;'>{emoji}</div>", unsafe_allow_html=True)
    
    # Bouton pour générer une image
    if st.button("✨ Générer une image avec l'IA", use_container_width=True):
        render_generer_image(recette)
    
    # Badges et caractéristiques
    badges = []
    if recette.est_bio:
        badges.append("🌱 Bio")
    if recette.est_local:
        badges.append("📍 Local")
    if recette.est_rapide:
        badges.append("⚡ Rapide")
    if recette.est_equilibre:
        badges.append("💪 Équilibré")
    if recette.congelable:
        badges.append("❄️ Congélable")
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
                st.metric("📍 Score Local", f"{recette.score_local}%", delta=None)
    
    # Robots compatibles
    if recette.robots_compatibles:
        robots_icons = {
            'Cookeo': ('🤖', 'Cookeo'),
            'Monsieur Cuisine': ('👨‍🍳', 'Monsieur Cuisine'),
            'Airfryer': ('🌪️', 'Airfryer'),
            'Multicooker': ('⏲️', 'Multicooker')
        }
        st.markdown("**🤖 Compatible avec:**")
        robot_cols = st.columns(len(recette.robots_compatibles))
        for idx, robot in enumerate(recette.robots_compatibles):
            icon, label = robots_icons.get(robot, ('🤖', robot.replace('_', ' ').title()))
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
            st.metric("🔥 Calories", "—")
    
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
        st.markdown("### 📝 Description")
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
            ingredient_cols[1].write(f"{ri.quantite}")
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
                    portions = st.number_input("Portions cuisinées", min_value=1, max_value=20, value=recette.portions)
                    note = st.slider("Note (0-5 étoiles)", 0, 5, 0)
                    avis = st.text_area("Avis personnel (optionnel)")
                    
                    if st.form_submit_button("Enregistrer"):
                        if service.enregistrer_cuisson(recette.id, portions, note if note > 0 else None, avis if avis else None):
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
        tab_list = ["📋 Versions existantes", "✨ Générer avec IA"]
        
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
                        icon = "⏲️"
                    else:
                        icon = "📋"
                    
                    with st.expander(f"{icon} Version {version.type_version}"):
                        if version.instructions_modifiees:
                            st.markdown("**Instructions adaptées:**")
                            st.write(version.instructions_modifiees)
                        
                        if version.notes_bebe:
                            st.info(version.notes_bebe)
                        
                        if version.type_version == "batch cooking" and version.etapes_paralleles_batch:
                            st.markdown("**Étapes parallèles:**")
                            for etape in version.etapes_paralleles_batch:
                                st.caption(f"• {etape}")
                        
                        if version.temps_optimise_batch:
                            st.caption(f"⏱️ Temps optimisé: {version.temps_optimise_batch} minutes")
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
                            "Ajoute les ingrédients sensibles à la fin"
                        ]
                    },
                    "Monsieur Cuisine": {
                        "icon": "👨‍🍳",
                        "desc": "Robot cuiseur multifonction",
                        "temps": "Généralement similaire ou réduit",
                        "conseils": [
                            "Utilise les programmes automatiques si disponibles",
                            "Réduis les portions pour éviter le débordement",
                            "Contrôle régulièrement la cuisson"
                        ]
                    },
                    "Airfryer": {
                        "icon": "🌪️",
                        "desc": "Friteuse à air chaud",
                        "temps": "Généralement réduit de 20-30%",
                        "conseils": [
                            "Coupe les aliments en tailles uniformes",
                            "Secoue le panier à mi-cuisson",
                            "N'empile pas trop les aliments"
                        ]
                    },
                    "Multicooker": {
                        "icon": "⏲️",
                        "desc": "Cuiseur multifonctions programmable",
                        "temps": "Généralement similaire",
                        "conseils": [
                            "Choisissez le programme approprié à la recette",
                            "Suivez les instructions du fabricant",
                            "Testez pour ajuster les temps"
                        ]
                    }
                }
                
                for robot in robots_compatibles:
                    info = robot_info.get(robot, {})
                    with st.expander(f"{info.get('icon', '🤖')} {robot}", expanded=False):
                        st.write(f"**Description:** {info.get('desc', '')}")
                        st.write(f"**Temps de cuisson:** {info.get('temps', '')}")
                        
                        if info.get('conseils'):
                            st.markdown("**Conseils d'adaptation:**")
                            for conseil in info.get('conseils', []):
                                st.caption(f"• {conseil}")
        
        # Onglet génération
        generation_tab_idx = 2 if robots_compatibles else 1
        with tab_versions[generation_tab_idx]:
            st.markdown("### ✨ Générer des versions adaptées")
            
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
                                st.error("❌ Erreur lors de la génération")
                        except Exception as e:
                            st.error(f"❌ Erreur: {str(e)}")
            
            with col2:
                if st.button("⏲️ Générer version batch cooking", use_container_width=True):
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
                    "Multicooker": ("⏲️", "multicooker"),
                }
                
                # Créer colonnes pour les boutons disponibles
                available_robots = [r for r in robots_compatibles]
                if available_robots:
                    cols = st.columns(len(available_robots))
                    for idx, robot_name in enumerate(available_robots):
                        icon, robot_key = robot_buttons.get(robot_name, ("🤖", robot_name.lower()))
                        with cols[idx]:
                            if st.button(
                                f"{icon} {robot_name}", 
                                use_container_width=True,
                                key=f"gen_robot_{robot_key}"
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


def render_ajouter_manuel():
    """Formulaire pour ajouter une recette manuellement"""
    st.subheader("➕ Ajouter une recette manuellement")
    
    with st.form("form_recette_manuel", border=True):
        # Info basique
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Nom de la recette *", max_chars=200)
        with col2:
            type_repas = st.selectbox(
                "Type de repas *",
                ["petit_déjeuner", "déjeuner", "dîner", "goûter", "apéritif", "dessert"]
            )
        
        description = st.text_area("Description", height=100)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            temps_prep = st.number_input("Temps préparation (min)", min_value=0, max_value=300, value=15)
        with col2:
            temps_cuisson = st.number_input("Temps cuisson (min)", min_value=0, max_value=300, value=20)
        with col3:
            portions = st.number_input("Portions", min_value=1, max_value=20, value=4)
        
        col1, col2 = st.columns(2)
        with col1:
            difficulte = st.selectbox("Difficulté", ["facile", "moyen", "difficile"])
        with col2:
            saison = st.selectbox(
                "Saison",
                ["toute_année", "printemps", "été", "automne", "hiver"]
            )
        
        # Ingrédients
        st.markdown("### Ingrédients")
        ingredients = []
        num_ingredients = st.number_input("Nombre d'ingrédients", min_value=1, max_value=20, value=3)
        
        for i in range(num_ingredients):
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                ing_nom = st.text_input(f"Ingrédient {i+1}", key=f"ing_nom_{i}")
            with col2:
                ing_qty = st.number_input(f"Qté", value=1.0, key=f"ing_qty_{i}", step=0.25)
            with col3:
                ing_unit = st.text_input(f"Unité", value="g", key=f"ing_unit_{i}", max_chars=20)
            
            if ing_nom:
                ingredients.append({
                    "nom": ing_nom,
                    "quantite": ing_qty,
                    "unite": ing_unit
                })
        
        # Étapes
        st.markdown("### Étapes de préparation")
        etapes = []
        num_etapes = st.number_input("Nombre d'étapes", min_value=1, max_value=15, value=3)
        
        for i in range(num_etapes):
            etape_desc = st.text_area(f"Étape {i+1}", height=80, key=f"etape_{i}")
            if etape_desc:
                etapes.append({
                    "description": etape_desc,
                    "duree": None
                })
        
        submitted = st.form_submit_button("✅ Créer la recette", use_container_width=True)
        
        if submitted:
            if not nom or not type_repas:
                st.error("❌ Nom et type de repas sont obligatoires")
            elif not ingredients:
                st.error("❌ Ajoutez au moins un ingrédient")
            elif not etapes:
                st.error("❌ Ajoutez au moins une étape")
            else:
                # Créer la recette
                service = get_recette_service()
                if service is None:
                    st.error("❌ Service indisponible")
                else:
                    try:
                        data = {
                            "nom": nom,
                            "description": description,
                            "type_repas": type_repas,
                            "temps_preparation": temps_prep,
                            "temps_cuisson": temps_cuisson,
                            "portions": portions,
                            "difficulte": difficulte,
                            "saison": saison,
                            "ingredients": ingredients,
                            "etapes": etapes,
                        }
                        
                        recette = service.create_complete(data)
                        
                        st.success(f"✅ Recette '{recette.nom}' créée avec succès!")
                        st.balloons()
                        
                    except ErreurValidation as e:
                        st.error(f"❌ Erreur validation: {e}")
                    except Exception as e:
                        st.error(f"❌ Erreur: {str(e)}")
                        logger.error(f"Erreur création recette: {e}")


def render_generer_ia():
    """Interface pour générer des recettes avec l'IA"""
    st.subheader("✨ Générer des recettes avec l'IA")
    
    service = get_recette_service()
    if service is None:
        st.error("❌ Service IA indisponible")
        return
    
    with st.form("form_recette_ia", border=True):
        st.info("💡 Laissez l'IA générer des recettes personnalisées basées sur vos préférences")
        
        col1, col2 = st.columns(2)
        with col1:
            type_repas = st.selectbox(
                "Type de repas *",
                ["petit_déjeuner", "déjeuner", "dîner", "goûter", "apéritif", "dessert"]
            )
        with col2:
            saison = st.selectbox(
                "Saison *",
                ["printemps", "été", "automne", "hiver", "toute_année"]
            )
        
        col1, col2 = st.columns(2)
        with col1:
            difficulte = st.selectbox(
                "Niveau de difficulté",
                ["facile", "moyen", "difficile"]
            )
        with col2:
            nb_recettes = st.number_input(
                "Nombre de suggestions",
                min_value=1,
                max_value=5,
                value=3
            )
        
        ingredients_str = st.text_area(
            "Ingrédients disponibles (optionnel)",
            placeholder="Séparez les ingrédients par des virgules\nEx: tomate, oignon, ail, riz",
            height=80
        )
        
        submitted = st.form_submit_button("🤖 Générer avec l'IA", use_container_width=True)
        
        if submitted:
            if not type_repas or not saison:
                st.error("❌ Type de repas et saison sont obligatoires")
            else:
                ingredients_dispo = None
                if ingredients_str:
                    ingredients_dispo = [i.strip() for i in ingredients_str.split(",") if i.strip()]
                
                with st.spinner("🤖 L'IA génère vos recettes..."):
                    try:
                        recettes_suggestions = service.generer_recettes_ia(
                            type_repas=type_repas,
                            saison=saison,
                            difficulte=difficulte,
                            ingredients_dispo=ingredients_dispo,
                            nb_recettes=nb_recettes,
                        )
                        
                        if not recettes_suggestions:
                            st.warning("⚠️ Aucune recette générée. Réessayez.")
                            return
                        
                        st.success(f"✅ {len(recettes_suggestions)} recette(s) générée(s)!")
                        
                        # Afficher les suggestions
                        for idx, suggestion in enumerate(recettes_suggestions, 1):
                            with st.expander(f"🍳 Recette {idx}: {suggestion.nom}", expanded=(idx == 1)):
                                st.markdown(f"**{suggestion.description}**")
                                
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("Préparation", f"{suggestion.temps_preparation} min")
                                with col2:
                                    st.metric("Cuisson", f"{suggestion.temps_cuisson} min")
                                with col3:
                                    st.metric("Portions", suggestion.portions)
                                with col4:
                                    st.metric("Difficulté", suggestion.difficulte)
                                
                                if suggestion.ingredients:
                                    st.markdown("#### Ingrédients")
                                    for ing in suggestion.ingredients:
                                        if isinstance(ing, dict):
                                            st.write(f"- {ing.get('nom', 'N/A')}: {ing.get('quantite', '')} {ing.get('unite', '')}")
                                        else:
                                            st.write(f"- {ing}")
                                
                                if suggestion.etapes:
                                    st.markdown("#### Étapes")
                                    for i, etape in enumerate(suggestion.etapes, 1):
                                        if isinstance(etape, dict):
                                            st.write(f"{i}. {etape.get('description', etape)}")
                                        else:
                                            st.write(f"{i}. {etape}")
                                
                                # Bouton pour ajouter à la base
                                if st.button(f"➕ Ajouter à mes recettes", key=f"add_suggestion_{idx}"):
                                    try:
                                        # Préparer les données pour la création
                                        data = {
                                            "nom": suggestion.nom,
                                            "description": suggestion.description,
                                            "type_repas": type_repas,
                                            "temps_preparation": suggestion.temps_preparation,
                                            "temps_cuisson": suggestion.temps_cuisson,
                                            "portions": suggestion.portions,
                                            "difficulte": suggestion.difficulte,
                                            "saison": suggestion.saison or saison,
                                            "ingredients": suggestion.ingredients or [],
                                            "etapes": suggestion.etapes or [],
                                        }
                                        
                                        recette = service.create_complete(data)
                                        st.success(f"✅ '{recette.nom}' ajoutée à vos recettes!")
                                        
                                    except Exception as e:
                                        st.error(f"❌ Erreur: {str(e)}")
                                        logger.error(f"Erreur ajout suggestion: {e}")
                    
                    except Exception as e:
                        st.error(f"❌ Erreur génération: {str(e)}")
                        logger.error(f"Erreur IA recettes: {e}")


def render_generer_image(recette):
    """Affiche l'interface pour générer une image pour la recette"""
    st.subheader("✨ Générer une image avec l'IA")
    
    # Description du prompt
    prompt = f"{recette.nom}"
    if recette.description:
        prompt += f": {recette.description}"
    
    st.caption(f"📝 {prompt}")
    
    # Bouton génération
    if st.button("🎨 Générer l'image", use_container_width=True, key=f"gen_img_{recette.id}"):
        with st.spinner("⏳ Génération de l'image en cours..."):
            try:
                from src.utils.image_generator import generer_image_recette
                
                url_image = generer_image_recette(recette.nom, recette.description or "")
                
                if url_image:
                    # Stocker dans session state pour persister après le spinner
                    st.session_state[f"generated_image_{recette.id}"] = url_image
                    st.success("✅ Image générée!")
                else:
                    st.error("❌ Impossible de générer l'image")
                    
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")
    
    # Afficher l'image si elle existe en session state
    if f"generated_image_{recette.id}" in st.session_state:
        url_image = st.session_state[f"generated_image_{recette.id}"]
        st.image(url_image, caption=recette.nom, use_column_width=True)
        
        # Proposer de sauvegarder
        if st.button("💾 Sauvegarder cette image", use_container_width=True, key=f"save_img_{recette.id}"):
            service = get_recette_service()
            if service:
                try:
                    recette.url_image = url_image
                    service.update(recette)
                    st.success("✅ Image sauvegardée dans la recette!")
                    st.session_state[f"generated_image_{recette.id}"] = None
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur sauvegarde: {str(e)}")
