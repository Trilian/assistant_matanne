"""
Module Recettes - Gestion complète des recettes
"""

import logging
import streamlit as st
from src.services.recettes import get_recette_service
from src.core.errors_base import ErreurValidation

logger = logging.getLogger(__name__)


def app():
    """Point d'entrée module recettes"""
    st.title("🍽️ Mes Recettes")
    st.caption("Gestion complète de votre base de recettes")

    # Sous-tabs
    tab_liste, tab_ajout, tab_ia = st.tabs(["📋 Liste", "➕ Ajouter Manuel", "✨ Générer IA"])

    with tab_liste:
        render_liste()

    with tab_ajout:
        render_ajouter_manuel()

    with tab_ia:
        render_generer_ia()


def render_liste():
    """Affiche la liste des recettes"""
    service = get_recette_service()
    
    if service is None:
        st.error("❌ Service recettes indisponible")
        return
    
    # Filtres
    col1, col2, col3 = st.columns(3)
    with col1:
        type_repas = st.selectbox(
            "Type de repas",
            ["Tous", "petit_déjeuner", "déjeuner", "dîner", "goûter"],
        )
    with col2:
        difficulte = st.selectbox(
            "Difficulté",
            ["Tous", "facile", "moyen", "difficile"],
        )
    with col3:
        temps_max = st.number_input(
            "Temps max (min)",
            min_value=0,
            max_value=300,
            value=60,
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
        limit=20,
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
    
    st.success(f"✅ {len(recettes)} recette(s) trouvée(s)")
    
    # Afficher en grid avec badges
    cols = st.columns(3)
    for idx, recette in enumerate(recettes):
        with cols[idx % 3]:
            with st.container(border=True):
                # En-tête avec nom et badge difficulté
                title_col, difficulty_col = st.columns([3, 1])
                with title_col:
                    st.subheader(recette.nom)
                with difficulty_col:
                    if recette.difficulte == "facile":
                        st.markdown("🟢")
                    elif recette.difficulte == "moyen":
                        st.markdown("🟡")
                    elif recette.difficulte == "difficile":
                        st.markdown("🔴")
                
                st.markdown(f"*{recette.description[:100]}...*" if recette.description else "")
                
                # Badges bio/local/rapide/équilibré
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
                    st.caption(" • ".join(badges))
                
                # Scores bio/local si présents
                if (recette.score_bio or 0) > 0 or (recette.score_local or 0) > 0:
                    score_cols = st.columns(2)
                    with score_cols[0]:
                        if (recette.score_bio or 0) > 0:
                            st.metric("🌱 Bio", f"{recette.score_bio}%")
                    with score_cols[1]:
                        if (recette.score_local or 0) > 0:
                            st.metric("📍 Local", f"{recette.score_local}%")
                
                # Robots compatibles
                if recette.robots_compatibles:
                    robots_icons = {
                        'cookeo': '🤖',
                        'monsieur_cuisine': '👨‍🍳',
                        'airfryer': '🌪️',
                        'multicooker': '⏲️'
                    }
                    robot_badges = []
                    for robot in recette.robots_compatibles:
                        icon = robots_icons.get(robot, '🤖')
                        robot_badges.append(icon)
                    st.caption("Compatible: " + " ".join(robot_badges))
                
                # Infos principales
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.caption(f"⏱️ {recette.temps_preparation}min")
                with col_b:
                    st.caption(f"👥 {recette.portions}")
                with col_c:
                    if recette.calories:
                        st.caption(f"🔥 {recette.calories}kcal")
                
                # Nutrition si disponible
                if any([recette.calories, recette.proteines, recette.lipides, recette.glucides]):
                    with st.expander("📊 Nutrition"):
                        nutrition_cols = st.columns(4)
                        if recette.calories:
                            nutrition_cols[0].metric("Cal", f"{recette.calories}")
                        if recette.proteines:
                            nutrition_cols[1].metric("Prot", f"{recette.proteines}g")
                        if recette.lipides:
                            nutrition_cols[2].metric("Lip", f"{recette.lipides}g")
                        if recette.glucides:
                            nutrition_cols[3].metric("Gluc", f"{recette.glucides}g")
                
                if st.button("Voir détails", key=f"recette_{recette.id}"):
                    render_detail_recette(recette)


def render_detail_recette(recette):
    """Affiche les détails d'une recette avec badges et scores"""
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
            'cookeo': ('🤖', 'Cookeo'),
            'monsieur_cuisine': ('👨‍🍳', 'Monsieur Cuisine'),
            'airfryer': ('🌪️', 'Airfryer'),
            'multicooker': ('⏲️', 'Multicooker')
        }
        st.markdown("**🤖 Compatible avec:**")
        robot_cols = st.columns(len(recette.robots_compatibles))
        for idx, robot in enumerate(recette.robots_compatibles):
            icon, label = robots_icons.get(robot, ('🤖', robot.replace('_', ' ').title()))
            robot_cols[idx].metric(icon, label)
    
    # Infos principales
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("⏱️ Préparation", f"{recette.temps_preparation} min")
    with col2:
        st.metric("🍳 Cuisson", f"{recette.temps_cuisson} min")
    with col3:
        st.metric("👥 Portions", recette.portions)
    with col4:
        if recette.calories:
            st.metric("🔥 Calories", f"{recette.calories} kcal")
    
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
    
    if recette.description:
        st.markdown("### 📝 Description")
        st.write(recette.description)
    
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
    
    if recette.etapes:
        st.markdown("### 👨‍🍳 Étapes de préparation")
        for etape in sorted(recette.etapes, key=lambda e: e.ordre or 0):
            st.markdown(f"**Étape {etape.ordre}:** {etape.description}")


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
