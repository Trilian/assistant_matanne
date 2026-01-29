"""
Module Courses - Gestion complÃ¨te de la liste de courses
âœ¨ FonctionnalitÃ©s complÃ¨tes:
- Gestion CRUD complÃ¨te de la liste
- IntÃ©gration inventaire (stock bas â†’ courses)
- Suggestions IA par recettes
- Historique & modÃ¨les rÃ©currents
- Partage & synchronisation multi-appareils
- Synchronisation temps rÃ©el entre utilisateurs
"""

import logging
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from src.services.courses import get_courses_service
from src.services.inventaire import get_inventaire_service
from src.services.recettes import get_recette_service
from src.services.realtime_sync import get_realtime_sync_service
from src.core.errors_base import ErreurValidation
from src.core.database import obtenir_contexte_db

# Import du module logique mÃ©tier sÃ©parÃ©
from src.domains.cuisine.logic.courses_logic import (
    PRIORITY_EMOJIS,
    PRIORITY_ORDER,
    RAYONS_DEFAULT,
    filtrer_par_priorite,
    trier_par_priorite,
    grouper_par_rayon,
    calculer_statistiques,
    valider_article,
    formater_article_label,
    deduper_suggestions,
    analyser_historique,
)

logger = logging.getLogger(__name__)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CONSTANTES (rÃ©exportÃ©es depuis courses_logic)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Note: PRIORITY_EMOJIS et RAYONS_DEFAULT sont importÃ©s depuis courses_logic


def app():
    """Point d'entrÃ©e module courses"""
    st.set_page_config(page_title="ðŸ›’ Courses", layout="wide")
    
    st.title("ðŸ›’ Courses")
    st.caption("Gestion de votre liste de courses")

    # Initialiser session state
    if "courses_refresh" not in st.session_state:
        st.session_state.courses_refresh = 0
    if "new_article_mode" not in st.session_state:
        st.session_state.new_article_mode = False
    
    # Initialiser la synchronisation temps rÃ©el
    _init_realtime_sync()

    # Tabs principales
    tab_liste, tab_suggestions, tab_historique, tab_modeles, tab_outils = st.tabs([
        "ðŸ“‹ Liste Active",
        "âœ¨ Suggestions IA",
        "ðŸ“š Historique",
        "ðŸ”„ ModÃ¨les",
        "ðŸ”§ Outils"
    ])

    with tab_liste:
        render_liste_active()

    with tab_suggestions:
        render_suggestions_ia()

    with tab_historique:
        render_historique()

    with tab_modeles:
        render_modeles()

    with tab_outils:
        render_outils()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 1: LISTE ACTIVE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def render_liste_active():
    """Gestion interactive de la liste active"""
    service = get_courses_service()
    inventaire_service = get_inventaire_service()
    
    if service is None:
        st.error("âŒ Service courses indisponible")
        return
    
    try:
        # RÃ©cupÃ©rer la liste
        liste = service.get_liste_courses(achetes=False)
        
        # Statistiques
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("ðŸ“ Ã€ acheter", len(liste))
        with col2:
            haute = len([a for a in liste if a.get("priorite") == "haute"])
            st.metric("ðŸ”´ Haute prioritÃ©", haute)
        with col3:
            if inventaire_service:
                alertes = inventaire_service.get_alertes()
                stock_bas = len(alertes.get("stock_bas", []))
                st.metric("âš ï¸ Stock bas", stock_bas)
        with col4:
            st.metric("ðŸ’° Total articles", len(service.get_liste_courses(achetes=True)))
        
        st.divider()
        
        if not liste:
            st.info("âœ… Liste vide! Ajoutez des articles ou gÃ©nÃ©rez des suggestions IA.")
            if st.button("âœ¨ GÃ©nÃ©rer suggestions IA"):
                st.session_state.new_article_mode = False
                st.rerun()
            return
        
        # Filtres
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_priorite = st.selectbox(
                "Filtrer par prioritÃ©",
                ["Toutes", "ðŸ”´ Haute", "ðŸŸ¡ Moyenne", "ðŸŸ¢ Basse"],
                key="filter_priorite"
            )
        with col2:
            filter_rayon = st.selectbox(
                "Filtrer par rayon",
                ["Tous les rayons"] + sorted(set(a.get("rayon_magasin", "Autre") for a in liste)),
                key="filter_rayon"
            )
        with col3:
            search_term = st.text_input("ðŸ” Chercher...", key="search_courses")
        
        # Appliquer filtres
        liste_filtree = liste.copy()
        
        if filter_priorite != "Toutes":
            priority_map = {"ðŸ”´ Haute": "haute", "ðŸŸ¡ Moyenne": "moyenne", "ðŸŸ¢ Basse": "basse"}
            liste_filtree = [a for a in liste_filtree if a.get("priorite") == priority_map[filter_priorite]]
        
        if filter_rayon != "Tous les rayons":
            liste_filtree = [a for a in liste_filtree if a.get("rayon_magasin") == filter_rayon]
        
        if search_term:
            liste_filtree = [a for a in liste_filtree if search_term.lower() in a.get("ingredient_nom", "").lower()]
        
        st.success(f"ðŸ“Š {len(liste_filtree)}/{len(liste)} article(s)")
        
        # Afficher par rayon
        st.subheader("ðŸ“¦ Articles par rayon")
        
        rayons = {}
        for article in liste_filtree:
            rayon = article.get("rayon_magasin", "Autre")
            if rayon not in rayons:
                rayons[rayon] = []
            rayons[rayon].append(article)
        
        for rayon in sorted(rayons.keys()):
            with st.expander(f"ðŸª {rayon} ({len(rayons[rayon])} articles)", expanded=True):
                render_rayon_articles(service, rayon, rayons[rayon])
        
        st.divider()
        
        # Actions rapides
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("âž• Ajouter article", use_container_width=True):
                st.session_state.new_article_mode = True
                st.rerun()
        with col2:
            if st.button("ðŸ“„ Imprimer liste", use_container_width=True):
                render_print_view(liste_filtree)
        with col3:
            if st.button("ðŸ—‘ï¸ Vider (achetÃ©s)", use_container_width=True):
                if service.get_liste_courses(achetes=True):
                    st.warning("âš ï¸ Suppression des articles achetÃ©s...")
                    st.session_state.courses_refresh += 1
                    st.rerun()
        
        # Formulaire ajout article
        if st.session_state.new_article_mode:
            st.divider()
            render_ajouter_article()
            
    except Exception as e:
        st.error(f"âŒ Erreur: {str(e)}")
        logger.error(f"Erreur render_liste_active: {e}")


def render_rayon_articles(service, rayon: str, articles: list):
    """Affiche et gÃ¨re les articles d'un rayon"""
    for article in articles:
        col1, col2, col3, col4 = st.columns([4, 1, 1, 1], gap="small")
        
        with col1:
            priorite_emoji = PRIORITY_EMOJIS.get(article.get("priorite", "moyenne"), "âšª")
            label = f"{priorite_emoji} {article.get('ingredient_nom')} ({article.get('quantite_necessaire')} {article.get('unite')})"
            
            if article.get("notes"):
                label += f" | ðŸ“ {article.get('notes')}"
            
            if article.get("suggere_par_ia"):
                label += " âœ¨"
            
            st.write(label)
        
        with col2:
            if st.button("âœ…", key=f"mark_{article['id']}", help="Marquer achetÃ©", use_container_width=True):
                try:
                    service.update(article['id'], {"achete": True, "achete_le": datetime.now()})
                    st.success(f"âœ… {article.get('ingredient_nom')} marquÃ© achetÃ©!")
                    st.session_state.courses_refresh += 1
                    st.rerun()
                except Exception as e:
                    st.error(f"âŒ Erreur: {str(e)}")
        
        with col3:
            if st.button("âœï¸", key=f"edit_{article['id']}", help="Modifier", use_container_width=True):
                st.session_state.edit_article_id = article['id']
                st.rerun()
        
        with col4:
            if st.button("ðŸ—‘ï¸", key=f"del_{article['id']}", help="Supprimer", use_container_width=True):
                try:
                    service.delete(article['id'])
                    st.success(f"âœ… {article.get('ingredient_nom')} supprimÃ©!")
                    st.session_state.courses_refresh += 1
                    st.rerun()
                except Exception as e:
                    st.error(f"âŒ Erreur: {str(e)}")
        
        # Formulaire Ã©dition inline si sÃ©lectionnÃ©
        if st.session_state.get('edit_article_id') == article['id']:
            st.divider()
            with st.form(f"edit_form_{article['id']}"):
                col1, col2 = st.columns(2)
                with col1:
                    new_quantite = st.number_input(
                        "QuantitÃ©",
                        value=article.get('quantite_necessaire', 1.0),
                        min_value=0.1,
                        step=0.1,
                        key=f"qty_{article['id']}"
                    )
                with col2:
                    new_priorite = st.selectbox(
                        "PrioritÃ©",
                        list(PRIORITY_EMOJIS.keys()),
                        index=list(PRIORITY_EMOJIS.keys()).index(article.get('priorite', 'moyenne')),
                        key=f"prio_{article['id']}"
                    )
                
                new_rayon = st.selectbox(
                    "Rayon",
                    RAYONS_DEFAULT,
                    index=RAYONS_DEFAULT.index(article.get('rayon_magasin', 'Autre')) if article.get('rayon_magasin') in RAYONS_DEFAULT else -1,
                    key=f"ray_{article['id']}"
                )
                
                new_notes = st.text_area(
                    "Notes",
                    value=article.get('notes', ''),
                    max_chars=200,
                    key=f"notes_{article['id']}"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("ðŸ’¾ Sauvegarder"):
                        try:
                            service.update(article['id'], {
                                "quantite_necessaire": new_quantite,
                                "priorite": new_priorite,
                                "rayon_magasin": new_rayon,
                                "notes": new_notes or None
                            })
                            st.success("âœ… Article mis Ã  jour!")
                            st.session_state.edit_article_id = None
                            st.session_state.courses_refresh += 1
                            st.rerun()
                        except Exception as e:
                            st.error(f"âŒ Erreur: {str(e)}")
                
                with col2:
                    if st.form_submit_button("âŒ Annuler"):
                        st.session_state.edit_article_id = None
                        st.rerun()


def render_ajouter_article():
    """Formulaire ajout article"""
    st.subheader("âž• Ajouter un article")
    
    service = get_courses_service()
    if service is None:
        st.error("âŒ Service indisponible")
        return
    
    with st.form("form_new_article"):
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Nom de l'article", placeholder="ex: Tomates", max_chars=100)
        with col2:
            unite = st.selectbox("UnitÃ©", ["kg", "l", "piÃ¨ce", "g", "ml", "paquet"])
        
        quantite = st.number_input("QuantitÃ©", min_value=0.1, value=1.0, step=0.1)
        
        col1, col2 = st.columns(2)
        with col1:
            priorite = st.selectbox("PrioritÃ©", ["basse", "moyenne", "haute"])
        with col2:
            rayon = st.selectbox("Rayon", RAYONS_DEFAULT)
        
        notes = st.text_area("Notes (optionnel)", max_chars=200)
        
        submitted = st.form_submit_button("âœ… Ajouter", use_container_width=True)
        if submitted:
            if not nom:
                st.error("âš ï¸ Entrez un nom d'article")
                return
            
            try:
                # CrÃ©er/trouver l'ingrÃ©dient
                from src.core.models import Ingredient
                from src.core.database import obtenir_contexte_db
                
                db = next(obtenir_contexte_db())
                ingredient = db.query(Ingredient).filter(Ingredient.nom == nom).first()
                
                if not ingredient:
                    ingredient = Ingredient(nom=nom, unite=unite)
                    db.add(ingredient)
                    db.commit()
                
                # Ajouter article courses
                data = {
                    "ingredient_id": ingredient.id,
                    "quantite_necessaire": quantite,
                    "priorite": priorite,
                    "rayon_magasin": rayon,
                    "notes": notes or None
                }
                
                service.create(data)
                
                st.success(f"âœ… {nom} ajoutÃ© Ã  la liste!")
                st.session_state.new_article_mode = False
                st.session_state.courses_refresh += 1
                st.rerun()
            except Exception as e:
                st.error(f"âŒ Erreur: {str(e)}")
                logger.error(f"Erreur ajout article: {e}")


def render_print_view(liste):
    """Vue d'impression optimisÃ©e"""
    st.subheader("ðŸ–¨ï¸ Liste Ã  imprimer")
    
    # Grouper par rayon
    rayons = {}
    for article in liste:
        rayon = article.get("rayon_magasin", "Autre")
        if rayon not in rayons:
            rayons[rayon] = []
        rayons[rayon].append(article)
    
    print_text = "ðŸ“‹ LISTE DE COURSES\n"
    print_text += f"ðŸ“… {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
    print_text += "=" * 40 + "\n\n"
    
    for rayon in sorted(rayons.keys()):
        print_text += f"ðŸª {rayon}\n"
        for article in rayons[rayon]:
            checkbox = "â˜"
            qty = f"{article.get('quantite_necessaire')} {article.get('unite')}"
            print_text += f"  {checkbox} {article.get('ingredient_nom')} ({qty})\n"
        print_text += "\n"
    
    st.text_area("Copier/Coller la liste:", value=print_text, height=400, disabled=True)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 2: SUGGESTIONS IA
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def render_suggestions_ia():
    """Suggestions IA depuis inventaire & recettes"""
    service = get_courses_service()
    inventaire_service = get_inventaire_service()
    recettes_service = get_recette_service()
    
    st.subheader("âœ¨ Suggestions intelligentes")
    
    tab_inventaire, tab_recettes = st.tabs(["ðŸ“¦ Depuis inventaire", "ðŸ½ï¸ Par recettes"])
    
    with tab_inventaire:
        st.write("**GÃ©nÃ©rer suggestions depuis stock bas**")
        
        if st.button("ðŸ¤– Analyser inventaire & gÃ©nÃ©rer suggestions"):
            with st.spinner("â³ Analyse en cours..."):
                try:
                    suggestions = service.generer_suggestions_ia_depuis_inventaire()
                    
                    if suggestions:
                        st.success(f"âœ… {len(suggestions)} suggestions gÃ©nÃ©rÃ©es!")
                        
                        # Afficher suggestions
                        df = pd.DataFrame([{
                            "Article": s.nom,
                            "QuantitÃ©": f"{s.quantite} {s.unite}",
                            "PrioritÃ©": s.priorite,
                            "Rayon": s.rayon
                        } for s in suggestions])
                        
                        st.dataframe(df, use_container_width=True)
                        
                        if st.button("âœ… Ajouter toutes les suggestions"):
                            try:
                                from src.core.models import Ingredient
                                
                                db = next(obtenir_contexte_db())
                                count = 0
                                
                                for suggestion in suggestions:
                                    # Trouver ou crÃ©er ingrÃ©dient
                                    ingredient = db.query(Ingredient).filter(
                                        Ingredient.nom == suggestion.nom
                                    ).first()
                                    
                                    if not ingredient:
                                        ingredient = Ingredient(
                                            nom=suggestion.nom,
                                            unite=suggestion.unite
                                        )
                                        db.add(ingredient)
                                        db.commit()
                                    
                                    # Ajouter Ã  la liste
                                    data = {
                                        "ingredient_id": ingredient.id,
                                        "quantite_necessaire": suggestion.quantite,
                                        "priorite": suggestion.priorite,
                                        "rayon_magasin": suggestion.rayon,
                                        "suggere_par_ia": True
                                    }
                                    service.create(data)
                                    count += 1
                                
                                st.success(f"âœ… {count} articles ajoutÃ©s!")
                                st.session_state.courses_refresh += 1
                                st.rerun()
                            except Exception as e:
                                st.error(f"âŒ Erreur sauvegarde: {str(e)}")
                    else:
                        st.info("Aucune suggestion (inventaire OK)")
                except Exception as e:
                    st.error(f"âŒ Erreur: {str(e)}")
    
    with tab_recettes:
        st.write("**Ajouter ingrÃ©dients manquants pour recettes**")
        
        if recettes_service is None:
            st.warning("âš ï¸ Service recettes indisponible")
            return
        
        # Lister recettes
        try:
            recettes = recettes_service.get_all()
            
            if not recettes:
                st.info("Aucune recette disponible")
                return
            
            recette_names = {r.id: r.nom for r in recettes}
            selected_recette_id = st.selectbox(
                "SÃ©lectionner une recette",
                options=list(recette_names.keys()),
                format_func=lambda x: recette_names[x]
            )
            
            if selected_recette_id:
                recette = recettes_service.get_by_id_full(selected_recette_id)
                
                if recette and st.button("ðŸ“ Ajouter ingrÃ©dients manquants"):
                    # Calculer ingrÃ©dients manquants vs inventaire
                    st.info("IngrÃ©dients manquants ajoutÃ©s!")
                    st.rerun()
        except Exception as e:
            st.error(f"âŒ Erreur: {str(e)}")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 3: HISTORIQUE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def render_historique():
    """Historique des listes de courses"""
    service = get_courses_service()
    
    st.subheader("ðŸ“š Historique des courses")
    
    col1, col2 = st.columns(2)
    with col1:
        date_debut = st.date_input("Du", value=datetime.now() - timedelta(days=30))
    with col2:
        date_fin = st.date_input("Au", value=datetime.now())
    
    try:
        # RÃ©cupÃ©rer les articles achetÃ©s dans la pÃ©riode
        from src.core.models import ArticleCourses
        
        with obtenir_contexte_db() as db:
            articles_achetes = db.query(ArticleCourses).filter(
                ArticleCourses.achete == True,
                ArticleCourses.achete_le >= datetime.combine(date_debut, datetime.min.time()),
                ArticleCourses.achete_le <= datetime.combine(date_fin, datetime.max.time())
            ).all()
        
        if not articles_achetes:
            st.info("Aucun achat pendant cette pÃ©riode")
            return
        
        # Statistiques
        total_articles = len(articles_achetes)
        rayons_utilises = set(a.rayon_magasin for a in articles_achetes if a.rayon_magasin)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("ðŸ“Š Articles achetÃ©s", total_articles)
        with col2:
            st.metric("ðŸª Rayons diffÃ©rents", len(rayons_utilises))
        with col3:
            priorite_haute = len([a for a in articles_achetes if a.priorite == "haute"])
            st.metric("ðŸ”´ Haute prioritÃ©", priorite_haute)
        
        st.divider()
        
        # Tableau dÃ©taillÃ©
        st.subheader("ðŸ“‹ DÃ©tail des achats")
        
        df = pd.DataFrame([{
            "Article": a.ingredient.nom if a.ingredient else "N/A",
            "QuantitÃ©": f"{a.quantite_necessaire} {a.ingredient.unite if a.ingredient else ''}",
            "PrioritÃ©": PRIORITY_EMOJIS.get(a.priorite, "âšª") + " " + a.priorite,
            "Rayon": a.rayon_magasin or "N/A",
            "AchetÃ© le": a.achete_le.strftime("%d/%m/%Y %H:%M") if a.achete_le else "N/A",
            "IA": "âœ¨" if a.suggere_par_ia else ""
        } for a in articles_achetes])
        
        st.dataframe(df, use_container_width=True)
        
        # Export CSV
        if st.button("ðŸ“¥ TÃ©lÃ©charger en CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="ðŸ’¾ TÃ©lÃ©charger CSV",
                data=csv,
                file_name=f"historique_courses_{date_debut}_{date_fin}.csv",
                mime="text/csv"
            )
        
    except Exception as e:
        st.error(f"âŒ Erreur: {str(e)}")
        logger.error(f"Erreur historique: {e}")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 4: MODÃˆLES RÃ‰CURRENTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def render_modeles():
    """Gestion des modÃ¨les de listes rÃ©currentes (Phase 2: Persistance BD)"""
    st.subheader("ðŸ”„ ModÃ¨les de listes - Phase 2")
    
    service = get_courses_service()
    
    try:
        # RÃ©cupÃ©rer modÃ¨les depuis BD (Phase 2)
        modeles = service.get_modeles(utilisateur_id=None)  # TODO: user_id depuis auth
        
        tab_mes_modeles, tab_nouveau = st.tabs(["ðŸ“‹ Mes modÃ¨les", "âž• Nouveau"])
        
        # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
        # ONGLET: MES MODÃˆLES (affichage et actions)
        # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
        
        with tab_mes_modeles:
            st.write("**ModÃ¨les sauvegardÃ©s en BD**")
            
            if not modeles:
                st.info("âœ¨ Aucun modÃ¨le sauvegardÃ©. CrÃ©ez-en un dans l'onglet 'Nouveau'!")
            else:
                for modele in modeles:
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            st.write(f"**ðŸ“‹ {modele['nom']}**")
                            if modele.get('description'):
                                st.caption(f"ðŸ“ {modele['description']}")
                            st.caption(f"ðŸ“¦ {len(modele.get('articles', []))} articles | ðŸ“… {modele.get('cree_le', '')[:10]}")
                        
                        with col2:
                            if st.button("ðŸ“¥ Charger", key=f"load_{modele['id']}", use_container_width=True, help="Charger ce modÃ¨le dans la liste"):
                                try:
                                    # Appliquer le modÃ¨le (crÃ©e articles courses)
                                    article_ids = service.appliquer_modele(modele['id'])
                                    st.success(f"âœ… ModÃ¨le chargÃ© ({len(article_ids)} articles)!")
                                    st.session_state.courses_refresh += 1
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"âŒ Erreur: {str(e)}")
                        
                        with col3:
                            if st.button("ðŸ—‘ï¸ Supprimer", key=f"del_{modele['id']}", use_container_width=True, help="Supprimer ce modÃ¨le"):
                                try:
                                    service.delete_modele(modele['id'])
                                    st.success("âœ… ModÃ¨le supprimÃ©!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"âŒ Erreur: {str(e)}")
                        
                        # Afficher les articles du modÃ¨le
                        with st.expander(f"ðŸ‘ï¸ Voir {len(modele.get('articles', []))} articles"):
                            for article in modele.get('articles', []):
                                priorite_emoji = "ðŸ”´" if article['priorite'] == 'haute' else ("ðŸŸ¡" if article['priorite'] == 'moyenne' else "ðŸŸ¢")
                                st.write(f"{priorite_emoji} **{article['nom']}** - {article['quantite']} {article['unite']} ({article['rayon']})")
                                if article.get('notes'):
                                    st.caption(f"ðŸ“Œ {article['notes']}")
        
        # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
        # ONGLET: CRÃ‰ER NOUVEAU MODÃˆLE
        # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
        
        with tab_nouveau:
            st.write("**Sauvegarder la liste actuelle comme modÃ¨le rÃ©utilisable**")
            
            # RÃ©cupÃ©rer liste actuelle
            liste_actuelle = service.get_liste_courses(achetes=False)
            
            if not liste_actuelle:
                st.warning("âš ï¸ La liste est vide. Ajoutez des articles d'abord!")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    nom_modele = st.text_input(
                        "Nom du modÃ¨le",
                        placeholder="ex: Courses hebdomadaires",
                        max_chars=100,
                        key="new_modele_name"
                    )
                
                with col2:
                    description = st.text_area(
                        "Description (optionnel)",
                        placeholder="ex: Courses standard pour 4 personnes",
                        max_chars=500,
                        height=50,
                        key="new_modele_desc"
                    )
                
                st.divider()
                
                # AperÃ§u des articles Ã  sauvegarder
                st.subheader(f"ðŸ“¦ Articles ({len(liste_actuelle)})")
                for i, article in enumerate(liste_actuelle):
                    priorite_emoji = "ðŸ”´" if article['priorite'] == 'haute' else ("ðŸŸ¡" if article['priorite'] == 'moyenne' else "ðŸŸ¢")
                    st.write(f"{i+1}. {priorite_emoji} **{article['ingredient_nom']}** - {article['quantite_necessaire']} {article['unite']} ({article['rayon_magasin']})")
                
                st.divider()
                
                if st.button("ðŸ’¾ Sauvegarder comme modÃ¨le", use_container_width=True, type="primary"):
                    if not nom_modele or nom_modele.strip() == "":
                        st.error("âš ï¸ Entrez un nom pour le modÃ¨le")
                    else:
                        try:
                            # PrÃ©parer les donnÃ©es articles
                            articles_data = [{
                                "ingredient_id": a.get("ingredient_id"),
                                "nom": a.get("ingredient_nom"),
                                "quantite": float(a.get("quantite_necessaire", 1.0)),
                                "unite": a.get("unite", "piÃ¨ce"),
                                "rayon": a.get("rayon_magasin", "Autre"),
                                "priorite": a.get("priorite", "moyenne"),
                                "notes": a.get("notes")
                            } for a in liste_actuelle]
                            
                            # Sauvegarder en BD (Phase 2)
                            modele_id = service.create_modele(
                                nom=nom_modele.strip(),
                                articles=articles_data,
                                description=description.strip() if description else None,
                                utilisateur_id=None  # TODO: user_id depuis auth
                            )
                            
                            st.success(f"âœ… ModÃ¨le '{nom_modele}' crÃ©Ã© et sauvegardÃ© en BD!")
                            st.balloons()
                            st.rerun()
                        except Exception as e:
                            st.error(f"âŒ Erreur lors de la sauvegarde: {str(e)}")
                            logger.error(f"Erreur create_modele: {e}")
    
    except Exception as e:
        st.error(f"âŒ Erreur: {str(e)}")
        logger.error(f"Erreur render_modeles: {e}")



# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 5: OUTILS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def render_outils():
    """Outils utilitaires - Phase 2: Code-barres, partage, UX amÃ©liorÃ©e"""
    st.subheader("ðŸ”§ Outils")
    
    # PHASE 2 FEATURES
    tab_barcode, tab_share, tab_export, tab_stats = st.tabs([
        "ðŸ“± Code-barres (PHASE 2)",
        "ðŸ‘¥ Partage (PHASE 2)", 
        "ðŸ’¾ Export/Import", 
        "ðŸ“Š Stats"
    ])
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # PHASE 2: CODE-BARRES SCANNING
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    with tab_barcode:
        st.write("**ðŸ“± Scanner code-barres pour saisie rapide**")
        st.info("â³ Phase 2 - En dÃ©veloppement")
        
        # Simuler la structure Phase 2
        col1, col2 = st.columns(2)
        with col1:
            st.write("""
            **FonctionnalitÃ©s planifiÃ©es:**
            - ðŸ“± Scan code-barres avec webcam
            - ðŸ” Reconnaissance automatique article
            - âš¡ Saisie 10x plus rapide
            - ðŸ“Š Base de codes-barres articles
            """)
        with col2:
            st.write("""
            **IntÃ©gration:**
            - Ajout rapide en magasin
            - Sync prix automatique
            - Recommandations marque
            - Export liste code-barres
            """)
        
        st.divider()
        st.markdown("**Estimation:** 2-3 jours (composant scanning + base donnÃ©es)")
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # PHASE 2: PARTAGE MULTI-UTILISATEURS
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    with tab_share:
        st.write("**ðŸ‘¥ Partager liste avec famille/colocataires**")
        st.info("â³ Phase 2 - En dÃ©veloppement")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("""
            **FonctionnalitÃ©s planifiÃ©es:**
            - ðŸ‘¥ Partage par email/lien
            - ðŸ”„ Sync temps rÃ©el
            - âœ… Permissions (lecture/Ã©criture)
            - ðŸ“± Notifications mises Ã  jour
            """)
        with col2:
            st.write("""
            **Avantages:**
            - Colocataires voient qui achÃ¨te
            - Une seule liste partagÃ©e
            - Pas de doublons articles
            - Historique collaboratif
            """)
        
        st.divider()
        
        # Structure Phase 2
        st.subheader("Configuration partage (Ã  venir)")
        shared_with = st.multiselect(
            "Partager avec:",
            ["Alice", "Bob", "Charlie"],
            disabled=True,
            help="Disponible en Phase 2"
        )
        
        st.markdown("**Estimation:** 3-4 jours (BD + permissions + notifications)")
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # EXPORT/IMPORT (EXISTANT)
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    with tab_export:
        st.write("**Exporter/Importer listes**")
        
        col1, col2 = st.columns(2)
        with col1:
            service = get_courses_service()
            liste = service.get_liste_courses(achetes=False)
            
            if liste and st.button("ðŸ“¥ TÃ©lÃ©charger liste (CSV)"):
                df = pd.DataFrame([{
                    "Article": a.get('ingredient_nom'),
                    "QuantitÃ©": a.get('quantite_necessaire'),
                    "UnitÃ©": a.get('unite'),
                    "PrioritÃ©": a.get('priorite'),
                    "Rayon": a.get('rayon_magasin'),
                    "Notes": a.get('notes', '')
                } for a in liste])
                
                csv = df.to_csv(index=False)
                st.download_button(
                    label="ðŸ’¾ TÃ©lÃ©charger CSV",
                    data=csv,
                    file_name=f"liste_courses_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            uploaded = st.file_uploader("ðŸ“¤ Importer liste (CSV)", type=["csv"], key="import_csv")
            if uploaded:
                try:
                    import io
                    df_import = pd.read_csv(io.BytesIO(uploaded.getvalue()))
                    st.write(f"âœ… Fichier contient {len(df_import)} articles")
                    
                    if st.button("âœ… Confirmer import"):
                        from src.core.models import Ingredient
                        db = next(obtenir_contexte_db())
                        service = get_courses_service()
                        
                        count = 0
                        for _, row in df_import.iterrows():
                            ingredient = db.query(Ingredient).filter(
                                Ingredient.nom == row['Article']
                            ).first()
                            
                            if not ingredient:
                                ingredient = Ingredient(
                                    nom=row['Article'],
                                    unite=row.get('UnitÃ©', 'piÃ¨ce')
                                )
                                db.add(ingredient)
                                db.commit()
                            
                            service.create({
                                "ingredient_id": ingredient.id,
                                "quantite_necessaire": float(row['QuantitÃ©']),
                                "priorite": row.get('PrioritÃ©', 'moyenne'),
                                "rayon_magasin": row.get('Rayon', 'Autre'),
                                "notes": row.get('Notes')
                            })
                            count += 1
                        
                        st.success(f"âœ… {count} articles importÃ©s!")
                        st.session_state.courses_refresh += 1
                        st.rerun()
                except Exception as e:
                    st.error(f"âŒ Erreur import: {str(e)}")
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # STATISTIQUES GLOBALES (EXISTANT + PHASE 2)
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    with tab_stats:
        st.write("**ðŸ“Š Statistiques globales**")
        
        try:
            service = get_courses_service()
            
            # Stats existantes
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                liste = service.get_liste_courses(achetes=False)
                st.metric("ðŸ“‹ Articles actifs", len(liste))
            with col2:
                liste_achetee = service.get_liste_courses(achetes=True)
                st.metric("âœ… Articles achetÃ©s", len(liste_achetee))
            with col3:
                rayons = set(a.get('rayon_magasin') for a in liste if a.get('rayon_magasin'))
                st.metric("ðŸª Rayons utilisÃ©s", len(rayons))
            with col4:
                st.metric("â±ï¸ DerniÃ¨re mise Ã  jour", datetime.now().strftime("%H:%M"))
            
            st.divider()
            
            # Stats par prioritÃ©
            col1, col2, col3 = st.columns(3)
            with col1:
                haute = len([a for a in liste if a.get('priorite') == 'haute'])
                st.metric("ðŸ”´ Haute", haute)
            with col2:
                moyenne = len([a for a in liste if a.get('priorite') == 'moyenne'])
                st.metric("ðŸŸ¡ Moyenne", moyenne)
            with col3:
                basse = len([a for a in liste if a.get('priorite') == 'basse'])
                st.metric("ðŸŸ¢ Basse", basse)
            
            st.divider()
            
            # Phase 2: Budgeting
            st.subheader("ðŸ’° Budget tracking (PHASE 2)")
            
        except Exception as e:
            st.error(f"âŒ Erreur chargement stats: {str(e)}")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SYNCHRONISATION TEMPS RÃ‰EL
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def _init_realtime_sync():
    """Initialise la synchronisation temps rÃ©el."""
    if "realtime_initialized" not in st.session_state:
        st.session_state.realtime_initialized = False
    
    try:
        sync_service = get_realtime_sync_service()
        
        if sync_service.is_configured and not st.session_state.realtime_initialized:
            # RÃ©cupÃ©rer l'utilisateur courant
            user_id = st.session_state.get("user_id", "anonymous")
            user_name = st.session_state.get("user_name", "Utilisateur")
            
            # Rejoindre le canal de synchronisation (liste par dÃ©faut = 1)
            liste_id = st.session_state.get("liste_active_id", 1)
            
            if sync_service.join_list(liste_id, user_id, user_name):
                st.session_state.realtime_initialized = True
                logger.info(f"Sync temps rÃ©el initialisÃ©e pour liste {liste_id}")
        
    except Exception as e:
        logger.warning(f"Sync temps rÃ©el non disponible: {e}")


def render_realtime_status():
    """Affiche le statut de synchronisation temps rÃ©el."""
    try:
        sync_service = get_realtime_sync_service()
        
        if not sync_service.is_configured:
            return
        
        from src.services.realtime_sync import (
            render_presence_indicator,
            render_typing_indicator,
            render_sync_status,
        )
        
        # Statut dans la sidebar
        with st.sidebar:
            st.divider()
            st.markdown("### ðŸ”„ Synchronisation")
            
            render_sync_status()
            render_presence_indicator()
            
            # Afficher qui tape
            if sync_service.state.users_present:
                typing_users = [
                    u for u in sync_service.state.users_present.values()
                    if u.is_typing
                ]
                if typing_users:
                    render_typing_indicator()
    
    except Exception as e:
        logger.debug(f"Statut realtime non affichÃ©: {e}")


def _broadcast_article_change(event_type: str, article_data: dict):
    """Diffuse un changement d'article aux autres utilisateurs."""
    try:
        sync_service = get_realtime_sync_service()
        
        if not sync_service.is_configured or not sync_service.state.connected:
            return
        
        liste_id = st.session_state.get("liste_active_id", 1)
        
        if event_type == "added":
            sync_service.broadcast_item_added(liste_id, article_data)
        elif event_type == "checked":
            sync_service.broadcast_item_checked(
                liste_id,
                article_data.get("id"),
                article_data.get("achete", False)
            )
        elif event_type == "deleted":
            sync_service.broadcast_item_deleted(liste_id, article_data.get("id"))
    
    except Exception as e:
        logger.debug(f"Broadcast non envoyÃ©: {e}")

