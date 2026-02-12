"""
DÃetail d'une recette - Affichage complet avec historique et versions.
"""

import random
import time
import streamlit as st

from src.services.recettes import get_recette_service
from .utilitaires import formater_quantite
from .generation_image import render_generer_image


def render_detail_recette(recette):
    """Affiche les dÃetails d'une recette avec badges, historique et versions"""
    service = get_recette_service()
    
    # En-tête
    col1, col2 = st.columns([3, 1])
    with col1:
        st.header(recette.nom)
    with col2:
        if recette.difficulte == "facile":
            st.markdown("# ðŸŸ¢")
        elif recette.difficulte == "moyen":
            st.markdown("# ðŸŸ¡")
        elif recette.difficulte == "difficile":
            st.markdown("# ðŸ”´")
    
    # Image si disponible
    if recette.url_image:
        try:
            st.image(recette.url_image, caption=recette.nom, width=400)
        except Exception:
            st.caption("ðŸ–¼ï¸ Image indisponible")
    else:
        # Placeholder visuel
        food_emojis = ["ðŸ½ï¸", "ðŸ³", "ðŸ¥˜", "ðŸ²", "ðŸ¥—", "ðŸœ", "ðŸ±", "ðŸ¥™", "ðŸ•", "ðŸ¥Ÿ", "ðŸ", "ðŸ¥œ"]
        emoji = random.choice(food_emojis)
        col = st.columns(1)[0]
        with col:
            st.markdown(f"<div style='text-align: center; font-size: 80px; opacity: 0.3;'>{emoji}</div>", unsafe_allow_html=True)
    
    # Section gÃenÃeration d'image (fusionnÃee en une seule)
    render_generer_image(recette)
    
    # Badges et caractÃeristiques
    badges = []
    if recette.est_bio:
        badges.append("ðŸŒ± Bio")
    if recette.est_local:
        badges.append("ðŸšœ Local")
    if recette.est_rapide:
        badges.append("âš¡ Rapide")
    if recette.est_equilibre:
        badges.append("ðŸ’ª ÉquilibrÃe")
    if recette.congelable:
        badges.append("â„ï¸ CongÃelable")
    if badges:
        st.markdown(" â€¢ ".join(badges))
    
    # Scores bio et local
    if (recette.score_bio or 0) > 0 or (recette.score_local or 0) > 0:
        score_col1, score_col2 = st.columns(2)
        with score_col1:
            if (recette.score_bio or 0) > 0:
                st.metric("ðŸŒ± Score Bio", f"{recette.score_bio}%", delta=None)
        with score_col2:
            if (recette.score_local or 0) > 0:
                st.metric("ðŸšœ Score Local", f"{recette.score_local}%", delta=None)
    
    # Robots compatibles
    if recette.robots_compatibles:
        robots_icons = {
            'Cookeo': ('ðŸ¤–', 'Cookeo'),
            'Monsieur Cuisine': ('ðŸ‘¨â€ðŸ³', 'Monsieur Cuisine'),
            'Airfryer': ('ðŸŒªï¸', 'Airfryer'),
            'Multicooker': ('ðŸ³', 'Multicooker')
        }
        st.markdown("**ðŸ¤– Compatible avec:**")
        robot_cols = st.columns(len(recette.robots_compatibles))
        for idx, robot in enumerate(recette.robots_compatibles):
            icon, label = robots_icons.get(robot, ('ðŸ¤–', robot.replace('_', ' ').title()))
            robot_cols[idx].metric(icon, label)
    
    # Infos principales
    metric_cols = st.columns(4)
    with metric_cols[0]:
        st.metric("â±ï¸ PrÃeparation", f"{recette.temps_preparation} min")
    with metric_cols[1]:
        st.metric("ðŸ³ Cuisson", f"{recette.temps_cuisson} min")
    with metric_cols[2]:
        st.metric("ðŸ‘¥ Portions", recette.portions)
    with metric_cols[3]:
        if recette.calories:
            st.metric("ðŸ”¥ Calories", f"{recette.calories} kcal")
        else:
            st.metric("ðŸ”¥ Calories", "â€“")
    
    # Nutrition complète
    if any([recette.calories, recette.proteines, recette.lipides, recette.glucides]):
        with st.expander("ðŸ“Š Nutrition dÃetaillÃee", expanded=False):
            nutrition_cols = st.columns(4)
            if recette.calories:
                nutrition_cols[0].metric("Calories", f"{recette.calories} kcal")
            if recette.proteines:
                nutrition_cols[1].metric("ProtÃeines", f"{recette.proteines}g")
            if recette.lipides:
                nutrition_cols[2].metric("Lipides", f"{recette.lipides}g")
            if recette.glucides:
                nutrition_cols[3].metric("Glucides", f"{recette.glucides}g")
    
    # Description
    if recette.description:
        st.markdown("### ðŸ“ Description")
        st.write(recette.description)
    
    # IngrÃedients
    if recette.ingredients:
        st.markdown("### ðŸ› IngrÃedients")
        ingredient_cols = st.columns([2, 1, 1])
        ingredient_cols[0].markdown("**IngrÃedient**")
        ingredient_cols[1].markdown("**QuantitÃe**")
        ingredient_cols[2].markdown("**UnitÃe**")
        st.divider()
        for ri in recette.ingredients:
            ingredient_cols = st.columns([2, 1, 1])
            ingredient_cols[0].write(f"{ri.ingredient.nom}")
            quantite_display = formater_quantite(ri.quantite)
            ingredient_cols[1].write(f"{quantite_display}")
            ingredient_cols[2].write(f"{ri.unite}")
    
    # Étapes de prÃeparation
    if recette.etapes:
        st.markdown("### ðŸ‘¨â€ðŸ³ Étapes de prÃeparation")
        for etape in sorted(recette.etapes, key=lambda e: e.ordre or 0):
            st.markdown(f"**Étape {etape.ordre}:** {etape.description}")
    
    # Historique d'utilisation
    st.divider()
    st.markdown("### ðŸ“Š Historique d'utilisation")
    
    if service:
        stats = service.get_stats_recette(recette.id)
        
        stat_cols = st.columns(5)
        stat_cols[0].metric("ðŸ½ï¸ Cuissons", stats.get("nb_cuissons", 0))
        if stats.get("derniere_cuisson"):
            stat_cols[1].metric("ðŸ“… Dernière", stats.get("jours_depuis_derniere", "?"), "jours")
        if stats.get("note_moyenne"):
            stat_cols[2].metric("â­ Note moyenne", f"{stats.get('note_moyenne', 0):.1f}/5")
        stat_cols[3].metric("ðŸ‘¥ Total portions", stats.get("total_portions", 0))
        
        # Bouton pour enregistrer une cuisson
        col_a, col_b, col_c = st.columns([2, 1, 2])
        with col_b:
            if st.button("âœ… CuisinÃee aujourd'hui!", use_container_width=True):
                with st.form("form_enregistrer_cuisson"):
                    portions = st.number_input("Portions cuisinÃees", min_value=1, max_value=20, value=recette.portions)
                    note = st.slider("Note (0-5 Ãetoiles)", 0, 5, 0)
                    avis = st.text_area("Avis personnel (optionnel)")
                    
                    if st.form_submit_button("Enregistrer"):
                        if service.enregistrer_cuisson(recette.id, portions, note if note > 0 else None, avis if avis else None):
                            st.success("âœ… Cuisson enregistrÃee!")
                            st.rerun()
                        else:
                            st.error("âŒ Erreur lors de l'enregistrement")
        
        # Historique des 5 dernières cuissons
        historique = service.get_historique(recette.id, nb_dernieres=5)
        if historique:
            with st.expander("ðŸ“œ 5 dernières utilisations", expanded=True):
                for h in historique:
                    col_date, col_portions, col_note = st.columns([1, 1, 1])
                    with col_date:
                        st.caption(f"ðŸ“… {h.date_cuisson.strftime('%d/%m/%Y')}")
                    with col_portions:
                        st.caption(f"ðŸ‘¥ {h.portions_cuisinees} portions")
                    with col_note:
                        if h.note:
                            st.caption(f"â­ {h.note}/5")
                    if h.avis:
                        st.caption(f"ðŸ’­ {h.avis}")
                    st.divider()
    
    # Versions (bÃebÃe, batch cooking, robots)
    st.divider()
    st.markdown("### ðŸŽ¯ Versions adaptÃees")
    
    if service:
        versions = service.get_versions(recette.id)
        
        # CrÃeer tabs pour les diffÃerents types
        tab_list = ["ðŸ“‹ Versions existantes", "âœ¨ GÃenÃerer avec IA"]
        
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
            tab_list.insert(1, "ðŸ¤– Robots compatibles")
        
        tab_versions = st.tabs(tab_list)
        
        with tab_versions[0]:
            if versions:
                for version in versions:
                    if version.type_version == "bÃebÃe":
                        icon = "ðŸ‘¶"
                    elif version.type_version == "batch cooking":
                        icon = "ðŸ³"
                    else:
                        icon = "ðŸ“‹"
                    
                    with st.expander(f"{icon} Version {version.type_version}"):
                        if version.instructions_modifiees:
                            st.markdown("**Instructions adaptÃees:**")
                            st.write(version.instructions_modifiees)
                        
                        if version.notes_bebe:
                            st.info(version.notes_bebe)
                        
                        if version.type_version == "batch cooking" and version.etapes_paralleles_batch:
                            st.markdown("**Étapes parallèles:**")
                            for etape in version.etapes_paralleles_batch:
                                st.caption(f"â€¢ {etape}")
                        
                        if version.temps_optimise_batch:
                            st.caption(f"â±ï¸ Temps optimisÃe: {version.temps_optimise_batch} minutes")
            else:
                st.info("Aucune version adaptÃee gÃenÃerÃee.")
        
        # Afficher onglet robots si compatible
        if robots_compatibles:
            with tab_versions[1]:
                st.markdown("### ðŸ¤– Robots de cuisine compatibles")
                
                robot_info = {
                    "Cookeo": {
                        "icon": "ðŸ²",
                        "desc": "Fait-tout multicuiseur sous pression",
                        "temps": "GÃenÃeralement rÃeduit de 30-40%",
                        "conseils": [
                            "Utilise le mode haute pression pour cuisson plus rapide",
                            "RÃeduis lÃegèrement les liquides",
                            "Ajoute les ingrÃedients sensibles Ã  la fin"
                        ]
                    },
                    "Monsieur Cuisine": {
                        "icon": "ðŸ‘¨â€ðŸ³",
                        "desc": "Robot cuiseur multifonction",
                        "temps": "GÃenÃeralement similaire ou rÃeduit",
                        "conseils": [
                            "Utilise les programmes automatiques si disponibles",
                            "RÃeduis les portions pour Ãeviter le dÃebordement",
                            "Contrôle rÃegulièrement la cuisson"
                        ]
                    },
                    "Airfryer": {
                        "icon": "ðŸŒªï¸",
                        "desc": "Friteuse Ã  air chaud",
                        "temps": "GÃenÃeralement rÃeduit de 20-30%",
                        "conseils": [
                            "Coupe les aliments en tailles uniformes",
                            "Secoue le panier Ã  mi-cuisson",
                            "N'empile pas trop les aliments"
                        ]
                    },
                    "Multicooker": {
                        "icon": "ðŸ³",
                        "desc": "Cuiseur multifonctions programmable",
                        "temps": "GÃenÃeralement similaire",
                        "conseils": [
                            "Choisissez le programme appropriÃe Ã  la recette",
                            "Suivez les instructions du fabricant",
                            "Testez pour ajuster les temps"
                        ]
                    }
                }
                
                for robot in robots_compatibles:
                    info = robot_info.get(robot, {})
                    with st.expander(f"{info.get('icon', 'ðŸ¤–')} {robot}", expanded=False):
                        st.write(f"**Description:** {info.get('desc', '')}")
                        st.write(f"**Temps de cuisson:** {info.get('temps', '')}")
                        
                        if info.get('conseils'):
                            st.markdown("**Conseils d'adaptation:**")
                            for conseil in info.get('conseils', []):
                                st.caption(f"â€¢ {conseil}")
        
        # Onglet gÃenÃeration
        generation_tab_idx = 2 if robots_compatibles else 1
        with tab_versions[generation_tab_idx]:
            st.markdown("### âœ¨ GÃenÃerer des versions adaptÃees")
            
            # Versions standards
            col1, col2 = st.columns(2)
            with col1:
                if st.button("ðŸ‘¶ GÃenÃerer version bÃebÃe", use_container_width=True):
                    with st.spinner("ðŸ¤– L'IA adapte la recette..."):
                        try:
                            version = service.generer_version_bebe(recette.id)
                            if version:
                                st.success("âœ… Version bÃebÃe crÃeÃee!")
                                st.rerun()
                            else:
                                st.error("âŒ Erreur lors de la gÃenÃeration (version=None)")
                        except Exception as e:
                            st.error(f"âŒ Erreur: {str(e)}")
            
            with col2:
                if st.button("ðŸ³ GÃenÃerer version batch cooking", use_container_width=True):
                    with st.spinner("ðŸ¤– L'IA optimise la recette pour le batch cooking..."):
                        try:
                            version = service.generer_version_batch_cooking(recette.id)
                            if version:
                                st.success("âœ… Version batch cooking crÃeÃee!")
                                st.rerun()
                            else:
                                st.error("âŒ Erreur lors de la gÃenÃeration")
                        except Exception as e:
                            st.error(f"âŒ Erreur: {str(e)}")
            
            # Versions robots si compatibles
            if robots_compatibles:
                st.markdown("---")
                st.markdown("### ðŸ¤– GÃenÃerer pour robots de cuisine")
                
                robot_buttons = {
                    "Cookeo": ("ðŸ²", "cookeo"),
                    "Monsieur Cuisine": ("ðŸ‘¨â€ðŸ³", "monsieur_cuisine"),
                    "Airfryer": ("ðŸŒªï¸", "airfryer"),
                    "Multicooker": ("ðŸ³", "multicooker"),
                }
                
                # CrÃeer colonnes pour les boutons disponibles
                available_robots = [r for r in robots_compatibles]
                if available_robots:
                    cols = st.columns(len(available_robots))
                    for idx, robot_name in enumerate(available_robots):
                        icon, robot_key = robot_buttons.get(robot_name, ("ðŸ¤–", robot_name.lower()))
                        with cols[idx]:
                            if st.button(
                                f"{icon} {robot_name}", 
                                use_container_width=True,
                                key=f"gen_robot_{robot_key}"
                            ):
                                with st.spinner(f"ðŸ¤– L'IA adapte pour {robot_name}..."):
                                    try:
                                        version = service.generer_version_robot(
                                            recette.id, robot_key
                                        )
                                        if version:
                                            st.success(f"âœ… Version {robot_name} crÃeÃee!")
                                            st.rerun()
                                        else:
                                            st.error("âŒ Erreur lors de la gÃenÃeration")
                                    except Exception as e:
                                        st.error(f"âŒ Erreur: {str(e)}")
    
    # Actions sur la recette
    st.divider()
    st.markdown("### âš™ï¸ Actions")
    
    action_cols = st.columns(3)
    
    with action_cols[0]:
        if st.button("âœï¸ Modifier", use_container_width=True, key="btn_modifier_recette"):
            st.session_state.edit_mode_recette = recette.id
            st.rerun()
    
    with action_cols[1]:
        if st.button("ðŸ“‹ Dupliquer", width='stretch', key="btn_dupliquer_recette"):
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
                        nouvelle_recette = service.create(recette_dict)
                        st.success("âœ… Recette dupliquÃee!")
                        st.rerun()
                except Exception as e:
                    st.error(f"âŒ Erreur: {str(e)}")
    
    with action_cols[2]:
        with st.popover("ðŸ—‘ï¸ Supprimer", use_container_width=True):
            st.warning(f"âš ï¸ ÃŠtes-vous sûr de vouloir supprimer:\n\n**{recette.nom}** ?")
            col_oui, col_non = st.columns(2)
            with col_oui:
                if st.button("âœ… Oui, supprimer", use_container_width=True, key="btn_confirmer_suppression"):
                    if service:
                        try:
                            with st.spinner("Suppression en cours..."):
                                if service.delete(recette.id):
                                    st.success("âœ… Recette supprimÃee!")
                                    st.session_state.detail_recette_id = None
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error("âŒ Impossible de supprimer la recette")
                        except Exception as e:
                            st.error(f"âŒ Erreur lors de la suppression: {str(e)}")
            with col_non:
                if st.button("âŒ Annuler", use_container_width=True, key="btn_annuler_suppression"):
                    st.rerun()


__all__ = ["render_detail_recette"]
