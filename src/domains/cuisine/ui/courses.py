"""
Module Courses - Gestion complète de la liste de courses
✨ Fonctionnalités complètes:
- Gestion CRUD complète de la liste
- Intégration inventaire (stock bas → courses)
- Suggestions IA par recettes
- Historique & modèles récurrents
- Partage & synchronisation multi-appareils
- Synchronisation temps réel entre utilisateurs
"""

import logging
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from src.services.courses import get_courses_service
from src.services.inventaire import get_inventaire_service
from src.services.recettes import get_recette_service
from src.services.realtime_sync import get_realtime_sync_service
from src.services.courses_intelligentes import get_courses_intelligentes_service
from src.core.errors_base import ErreurValidation
from src.core.database import obtenir_contexte_db

# Import du module logique métier séparé
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

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTES (réexportées depuis courses_logic)
# ─────────────────────────────────────────────────────────────────────────────
# Note: PRIORITY_EMOJIS et RAYONS_DEFAULT sont importés depuis courses_logic


def app():
    """Point d'entrée module courses"""
    st.title("🛍 Courses")
    st.caption("Gestion de votre liste de courses")

    # Initialiser session state
    if "courses_refresh" not in st.session_state:
        st.session_state.courses_refresh = 0
    if "new_article_mode" not in st.session_state:
        st.session_state.new_article_mode = False
    if "courses_active_tab" not in st.session_state:
        st.session_state.courses_active_tab = 0
    
    # Initialiser la synchronisation temps réel
    _init_realtime_sync()

    # Tabs principales
    tab_liste, tab_planning, tab_suggestions, tab_historique, tab_modeles, tab_outils = st.tabs([
        "📋 Liste Active",
        "🍽️ Depuis Planning",
        "✨ Suggestions IA",
        "📚 Historique",
        "📄 Modèles",
        "📧 Outils"
    ])

    with tab_liste:
        st.session_state.courses_active_tab = 0
        render_liste_active()

    with tab_planning:
        st.session_state.courses_active_tab = 1
        render_courses_depuis_planning()

    with tab_suggestions:
        st.session_state.courses_active_tab = 2
        render_suggestions_ia()

    with tab_historique:
        st.session_state.courses_active_tab = 3
        render_historique()

    with tab_modeles:
        st.session_state.courses_active_tab = 4
        render_modeles()

    with tab_outils:
        st.session_state.courses_active_tab = 5
        render_outils()


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1: LISTE ACTIVE
# ─────────────────────────────────────────────────────────────────────────────

def render_liste_active():
    """Gestion interactive de la liste active"""
    service = get_courses_service()
    inventaire_service = get_inventaire_service()
    
    if service is None:
        st.error("❌ Service courses indisponible")
        return
    
    try:
        # Récupérer la liste
        liste = service.get_liste_courses(achetes=False)
        
        # Statistiques
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📥 À acheter", len(liste))
        with col2:
            haute = len([a for a in liste if a.get("priorite") == "haute"])
            st.metric("🔴 Haute priorité", haute)
        with col3:
            if inventaire_service:
                alertes = inventaire_service.get_alertes()
                stock_bas = len(alertes.get("stock_bas", []))
                st.metric("⚠️ Stock bas", stock_bas)
        with col4:
            st.metric("💰 Total articles", len(service.get_liste_courses(achetes=True)))
        
        st.divider()
        
        if not liste:
            st.info("✅ Liste vide! Ajoutez des articles ou générez des suggestions IA.")
            if st.button("✨ Générer suggestions IA"):
                st.session_state.new_article_mode = False
                st.rerun()
            return
        
        # Filtres
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_priorite = st.selectbox(
                "Filtrer par priorité",
                ["Toutes", "🔴 Haute", "🟡 Moyenne", "🟢 Basse"],
                key="filter_priorite"
            )
        with col2:
            filter_rayon = st.selectbox(
                "Filtrer par rayon",
                ["Tous les rayons"] + sorted(set(a.get("rayon_magasin", "Autre") for a in liste)),
                key="filter_rayon"
            )
        with col3:
            search_term = st.text_input("🔍 Chercher...", key="search_courses")
        
        # Appliquer filtres
        liste_filtree = liste.copy()
        
        if filter_priorite != "Toutes":
            priority_map = {"🔴 Haute": "haute", "🟡 Moyenne": "moyenne", "🟢 Basse": "basse"}
            liste_filtree = [a for a in liste_filtree if a.get("priorite") == priority_map[filter_priorite]]
        
        if filter_rayon != "Tous les rayons":
            liste_filtree = [a for a in liste_filtree if a.get("rayon_magasin") == filter_rayon]
        
        if search_term:
            liste_filtree = [a for a in liste_filtree if search_term.lower() in a.get("ingredient_nom", "").lower()]
        
        st.success(f"📊 {len(liste_filtree)}/{len(liste)} article(s)")
        
        # Afficher par rayon
        st.subheader("📦 Articles par rayon")
        
        rayons = {}
        for article in liste_filtree:
            rayon = article.get("rayon_magasin", "Autre")
            if rayon not in rayons:
                rayons[rayon] = []
            rayons[rayon].append(article)
        
        for rayon in sorted(rayons.keys()):
            with st.expander(f"🪑 {rayon} ({len(rayons[rayon])} articles)", expanded=True):
                render_rayon_articles(service, rayon, rayons[rayon])
        
        st.divider()
        
        # Actions rapides
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("➕ Ajouter article", use_container_width=True):
                st.session_state.new_article_mode = True
                st.rerun()
        with col2:
            if st.button("📄 Imprimer liste", use_container_width=True):
                render_print_view(liste_filtree)
        with col3:
            if st.button("🗑️ Vider (achetés)", use_container_width=True):
                if service.get_liste_courses(achetes=True):
                    st.warning("⚠️ Suppression des articles achetés...")
                    st.session_state.courses_refresh += 1
                    st.rerun()
        
        # Formulaire ajout article
        if st.session_state.new_article_mode:
            st.divider()
            render_ajouter_article()
            
    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")
        logger.error(f"Erreur render_liste_active: {e}")


def render_rayon_articles(service, rayon: str, articles: list):
    """Affiche et gère les articles d'un rayon"""
    for article in articles:
        col1, col2, col3, col4 = st.columns([4, 1, 1, 1], gap="small")
        
        with col1:
            priorite_emoji = PRIORITY_EMOJIS.get(article.get("priorite", "moyenne"), "⚫")
            label = f"{priorite_emoji} {article.get('ingredient_nom')} ({article.get('quantite_necessaire')} {article.get('unite')})"
            
            if article.get("notes"):
                label += f" | 📝 {article.get('notes')}"
            
            if article.get("suggere_par_ia"):
                label += " ✨"
            
            st.write(label)
        
        with col2:
            if st.button("✅", key=f"article_mark_{article['id']}", help="Marquer acheté", use_container_width=True):
                try:
                    service.update(article['id'], {"achete": True, "achete_le": datetime.now()})
                    st.success(f"✅ {article.get('ingredient_nom')} marqué acheté!")
                    st.session_state.courses_refresh += 1
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")
        
        with col3:
            if st.button("✏️", key=f"article_edit_{article['id']}", help="Modifier", use_container_width=True):
                st.session_state.edit_article_id = article['id']
                st.rerun()
        
        with col4:
            if st.button("🗑️", key=f"article_del_{article['id']}", help="Supprimer", use_container_width=True):
                try:
                    service.delete(article['id'])
                    st.success(f"✅ {article.get('ingredient_nom')} supprimé!")
                    st.session_state.courses_refresh += 1
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")
        
        # Formulaire édition inline si sélectionné
        if st.session_state.get('edit_article_id') == article['id']:
            st.divider()
            with st.form(f"article_edit_form_{article['id']}"):
                col1, col2 = st.columns(2)
                with col1:
                    new_quantite = st.number_input(
                        "Quantité",
                        value=article.get('quantite_necessaire', 1.0),
                        min_value=0.1,
                        step=0.1,
                        key=f"article_qty_{article['id']}"
                    )
                with col2:
                    new_priorite = st.selectbox(
                        "Priorité",
                        list(PRIORITY_EMOJIS.keys()),
                        index=list(PRIORITY_EMOJIS.keys()).index(article.get('priorite', 'moyenne')),
                        key=f"article_prio_{article['id']}"
                    )
                
                new_rayon = st.selectbox(
                    "Rayon",
                    RAYONS_DEFAULT,
                    index=RAYONS_DEFAULT.index(article.get('rayon_magasin', 'Autre')) if article.get('rayon_magasin') in RAYONS_DEFAULT else -1,
                    key=f"article_ray_{article['id']}"
                )
                
                new_notes = st.text_area(
                    "Notes",
                    value=article.get('notes', ''),
                    max_chars=200,
                    key=f"article_notes_{article['id']}"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 Sauvegarder", key=f"article_save_{article['id']}"):
                        try:
                            service.update(article['id'], {
                                "quantite_necessaire": new_quantite,
                                "priorite": new_priorite,
                                "rayon_magasin": new_rayon,
                                "notes": new_notes or None
                            })
                            st.success("✅ Article mis à jour!")
                            st.session_state.edit_article_id = None
                            st.session_state.courses_refresh += 1
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erreur: {str(e)}")
                
                with col2:
                    if st.form_submit_button("❌ Annuler", key=f"article_cancel_{article['id']}"):
                        st.session_state.edit_article_id = None
                        st.rerun()


def render_ajouter_article():
    """Formulaire ajout article"""
    st.subheader("➕ Ajouter un article")
    
    service = get_courses_service()
    if service is None:
        st.error("❌ Service indisponible")
        return
    
    with st.form("form_new_article"):
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Nom de l'article", placeholder="ex: Tomates", max_chars=100)
        with col2:
            unite = st.selectbox("Unité", ["kg", "l", "pièce", "g", "ml", "paquet"])
        
        quantite = st.number_input("Quantité", min_value=0.1, value=1.0, step=0.1)
        
        col1, col2 = st.columns(2)
        with col1:
            priorite = st.selectbox("Priorité", ["basse", "moyenne", "haute"])
        with col2:
            rayon = st.selectbox("Rayon", RAYONS_DEFAULT)
        
        notes = st.text_area("Notes (optionnel)", max_chars=200)
        
        submitted = st.form_submit_button("✅ Ajouter", use_container_width=True)
        if submitted:
            if not nom:
                st.error("⚠️ Entrez un nom d'article")
                return
            
            try:
                # Créer/trouver l'ingrédient
                from src.core.models import Ingredient
                from src.core.database import obtenir_contexte_db
                
                with obtenir_contexte_db() as db:
                    ingredient = db.query(Ingredient).filter(Ingredient.nom == nom).first()
                    
                    if not ingredient:
                        ingredient = Ingredient(nom=nom, unite=unite)
                        db.add(ingredient)
                        db.flush()
                        db.refresh(ingredient)
                    
                    ingredient_id = ingredient.id
                
                # Ajouter article courses avec le service
                data = {
                    "ingredient_id": ingredient_id,
                    "quantite_necessaire": quantite,
                    "priorite": priorite,
                    "rayon_magasin": rayon,
                    "notes": notes or None
                }
                
                service.create(data)
                
                st.success(f"✅ {nom} ajouté à la liste!")
                st.session_state.new_article_mode = False
                st.session_state.courses_refresh += 1
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")
                logger.error(f"Erreur ajout article: {e}")


def render_print_view(liste):
    """Vue d'impression optimisée"""
    st.subheader("🖨️ Liste à imprimer")
    
    # Grouper par rayon
    rayons = {}
    for article in liste:
        rayon = article.get("rayon_magasin", "Autre")
        if rayon not in rayons:
            rayons[rayon] = []
        rayons[rayon].append(article)
    
    print_text = "📋 LISTE DE COURSES\n"
    print_text += f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
    print_text += "=" * 40 + "\n\n"
    
    for rayon in sorted(rayons.keys()):
        print_text += f"🪑 {rayon}\n"
        for article in rayons[rayon]:
            checkbox = "☑"
            qty = f"{article.get('quantite_necessaire')} {article.get('unite')}"
            print_text += f"  {checkbox} {article.get('ingredient_nom')} ({qty})\n"
        print_text += "\n"
    
    st.text_area("Copier/Coller la liste:", value=print_text, height=400, disabled=True)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2: COURSES DEPUIS PLANNING
# ─────────────────────────────────────────────────────────────────────────────

def render_courses_depuis_planning():
    """Génère la liste de courses depuis le planning repas actif."""
    st.subheader("🍽️ Courses depuis le Planning")
    
    st.info("""
    **Génération automatique** de la liste de courses basée sur votre planning de repas.
    
    Le système analyse les recettes planifiées, extrait les ingrédients,
    compare avec votre inventaire et génère une liste optimisée.
    """)
    
    service = get_courses_intelligentes_service()
    
    # Vérifier planning actif
    planning = service.obtenir_planning_actif()
    
    if not planning:
        st.warning("⚠️ Aucun planning actif trouvé.")
        st.caption("Créez d'abord un planning de repas dans 'Cuisine → Planning Semaine'")
        
        if st.button("📅 Aller au planning", use_container_width=True):
            # Naviguer vers planning
            import streamlit as st
            st.session_state.current_page = "cuisine.planning_semaine"
            st.rerun()
        return
    
    # Afficher info planning
    col1, col2 = st.columns([2, 1])
    with col1:
        st.success(f"✅ Planning actif: **{planning.nom}**")
        nb_repas = len(planning.repas) if planning.repas else 0
        st.caption(f"📆 Du {planning.semaine_debut} au {planning.semaine_fin} • {nb_repas} repas planifiés")
    
    with col2:
        # Bouton générer
        if st.button("🔄 Générer la liste", type="primary", use_container_width=True):
            with st.spinner("Analyse du planning en cours..."):
                resultat = service.generer_liste_courses()
                st.session_state["courses_planning_resultat"] = resultat
                st.rerun()
    
    st.divider()
    
    # Afficher résultat si disponible
    resultat = st.session_state.get("courses_planning_resultat")
    
    if resultat:
        # Alertes
        for alerte in resultat.alertes:
            if "✅" in alerte:
                st.success(alerte)
            elif "⚠️" in alerte:
                st.warning(alerte)
            else:
                st.info(alerte)
        
        if resultat.articles:
            # Métriques
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🛒 Articles à acheter", resultat.total_articles)
            with col2:
                st.metric("🍳 Recettes couvertes", len(resultat.recettes_couvertes))
            with col3:
                # Répartition par rayon
                rayons = set(a.rayon for a in resultat.articles)
                st.metric("📦 Rayons", len(rayons))
            
            # Recettes couvertes
            if resultat.recettes_couvertes:
                st.markdown("**Recettes concernées:**")
                st.caption(", ".join(resultat.recettes_couvertes[:5]))
            
            st.divider()
            
            # Afficher articles par rayon
            st.subheader("📋 Articles à acheter")
            
            # Grouper par rayon
            articles_par_rayon = {}
            for article in resultat.articles:
                if article.rayon not in articles_par_rayon:
                    articles_par_rayon[article.rayon] = []
                articles_par_rayon[article.rayon].append(article)
            
            # Sélection articles à ajouter
            articles_selectionnes = []
            
            for rayon in sorted(articles_par_rayon.keys()):
                articles = articles_par_rayon[rayon]
                priorite_emoji = {1: "🔴", 2: "🟡", 3: "🟢"}.get(articles[0].priorite, "⚪")
                
                with st.expander(f"{priorite_emoji} {rayon} ({len(articles)} articles)", expanded=True):
                    for i, article in enumerate(articles):
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            # Checkbox pour sélection
                            selected = st.checkbox(
                                f"**{article.nom}**",
                                value=True,
                                key=f"art_sel_{rayon}_{i}"
                            )
                            if selected:
                                articles_selectionnes.append(article)
                            
                            # Sources
                            sources = ", ".join(article.recettes_source[:2])
                            st.caption(f"📖 {sources}")
                        
                        with col2:
                            st.markdown(f"**{article.a_acheter:.0f}** {article.unite}")
                        
                        with col3:
                            if article.en_stock > 0:
                                st.caption(f"(en stock: {article.en_stock:.0f})")
            
            # Action finale
            st.divider()
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(
                    f"✅ Ajouter {len(articles_selectionnes)} articles à la liste",
                    type="primary",
                    use_container_width=True,
                    disabled=len(articles_selectionnes) == 0
                ):
                    with st.spinner("Ajout en cours..."):
                        ids = service.ajouter_a_liste_courses(articles_selectionnes)
                        if ids:
                            st.success(f"✅ {len(ids)} articles ajoutés à votre liste de courses!")
                            # Reset
                            del st.session_state["courses_planning_resultat"]
                            st.session_state.courses_refresh += 1
                            st.rerun()
            
            with col2:
                if st.button("🔄 Régénérer", use_container_width=True):
                    del st.session_state["courses_planning_resultat"]
                    st.rerun()
    else:
        # Instructions
        st.markdown("""
        ### Comment ça marche?
        
        1. **Analyse** - Le système parcourt toutes les recettes de votre planning
        2. **Extraction** - Les ingrédients sont extraits et regroupés
        3. **Comparaison** - Vérification avec votre inventaire actuel
        4. **Optimisation** - Seuls les articles manquants sont listés
        5. **Organisation** - Tri par rayon pour faciliter vos courses
        
        Cliquez sur **"Générer la liste"** pour commencer.
        """)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3: SUGGESTIONS IA
# ─────────────────────────────────────────────────────────────────────────────

def render_suggestions_ia():
    """Suggestions IA depuis inventaire & recettes"""
    service = get_courses_service()
    inventaire_service = get_inventaire_service()
    recettes_service = get_recette_service()
    
    st.subheader("✨ Suggestions intelligentes")
    
    tab_inventaire, tab_recettes = st.tabs(["📦 Depuis inventaire", "🍽️ Par recettes"])
    
    with tab_inventaire:
        st.write("**Générer suggestions depuis stock bas**")
        
        if st.button("🤖 Analyser inventaire & générer suggestions"):
            with st.spinner("⏳ Analyse en cours..."):
                try:
                    suggestions = service.generer_suggestions_ia_depuis_inventaire()
                    
                    if suggestions:
                        st.success(f"✅ {len(suggestions)} suggestions générées!")
                        
                        # Afficher suggestions
                        df = pd.DataFrame([{
                            "Article": s.nom,
                            "Quantité": f"{s.quantite} {s.unite}",
                            "Priorité": s.priorite,
                            "Rayon": s.rayon
                        } for s in suggestions])
                        
                        st.dataframe(df, use_container_width=True)
                        
                        if st.button("✅ Ajouter toutes les suggestions"):
                            try:
                                from src.core.models import Ingredient
                                
                                db = next(obtenir_contexte_db())
                                count = 0
                                
                                for suggestion in suggestions:
                                    # Trouver ou créer ingrédient
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
                                    
                                    # Ajouter à la liste
                                    data = {
                                        "ingredient_id": ingredient.id,
                                        "quantite_necessaire": suggestion.quantite,
                                        "priorite": suggestion.priorite,
                                        "rayon_magasin": suggestion.rayon,
                                        "suggere_par_ia": True
                                    }
                                    service.create(data)
                                    count += 1
                                
                                st.success(f"✅ {count} articles ajoutés!")
                                st.session_state.courses_refresh += 1
                                # Pas de rerun pour rester sur cet onglet
                                time.sleep(0.5)
                            except Exception as e:
                                st.error(f"❌ Erreur sauvegarde: {str(e)}")
                    else:
                        st.info("Aucune suggestion (inventaire OK)")
                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")
    
    with tab_recettes:
        st.write("**Ajouter ingrédients manquants pour recettes**")
        
        if recettes_service is None:
            st.warning("⚠️ Service recettes indisponible")
        else:
            # Lister recettes
            try:
                recettes = recettes_service.get_all()
                
                if not recettes:
                    st.info("Aucune recette disponible")
                else:
                    recette_names = {r.id: r.nom for r in recettes}
                    selected_recette_id = st.selectbox(
                        "Sélectionner une recette",
                        options=list(recette_names.keys()),
                        format_func=lambda x: recette_names[x],
                        key="select_recette_courses"
                    )
                    
                    if selected_recette_id:
                        recette = recettes_service.get_by_id_full(selected_recette_id)
                        
                        if recette:
                            # Afficher ingrédients de la recette
                            nb_ingredients = len(recette.ingredients) if recette.ingredients else 0
                            st.caption(f"📝 {nb_ingredients} ingrédients")
                            
                            if st.button("🔍 Ajouter ingrédients manquants", key="btn_add_missing_ingredients"):
                                try:
                                    from src.core.models import Ingredient
                                    from src.core.database import obtenir_contexte_db
                                    
                                    # Récupérer ingrédients de la recette
                                    ingredients_recette = recette.ingredients if recette.ingredients else []
                                    
                                    if not ingredients_recette:
                                        st.warning("Aucun ingrédient dans cette recette")
                                    else:
                                        count_added = 0
                                        
                                        with obtenir_contexte_db() as db:
                                            for ing_obj in ingredients_recette:
                                                # Récupérer ingrédient
                                                ing_nom = ing_obj.ingredient.nom if hasattr(ing_obj, 'ingredient') else ing_obj.nom
                                                ing_quantite = ing_obj.quantite if hasattr(ing_obj, 'quantite') else 1
                                                ing_unite = ing_obj.ingredient.unite if hasattr(ing_obj, 'ingredient') and hasattr(ing_obj.ingredient, 'unite') else 'pièce'
                                                
                                                if not ing_nom:
                                                    continue
                                                
                                                ingredient = db.query(Ingredient).filter(
                                                    Ingredient.nom == ing_nom
                                                ).first()
                                                
                                                if not ingredient:
                                                    ingredient = Ingredient(
                                                        nom=ing_nom,
                                                        unite=ing_unite
                                                    )
                                                    db.add(ingredient)
                                                    db.flush()
                                                    db.refresh(ingredient)
                                                
                                                # Ajouter à la liste courses
                                                data = {
                                                    "ingredient_id": ingredient.id,
                                                    "quantite_necessaire": ing_quantite,
                                                    "priorite": "moyenne",
                                                    "rayon_magasin": "Autre",
                                                    "notes": f"Pour {recette.nom}"
                                                }
                                                service.create(data)
                                                count_added += 1
                                        
                                        st.success(f"✅ {count_added} ingrédient(s) ajouté(s) à la liste!")
                                        st.session_state.courses_refresh += 1
                                        # Pas de rerun pour rester sur cet onglet
                                        time.sleep(0.5)
                                except Exception as e:
                                    st.error(f"❌ Erreur: {str(e)}")
                                    logger.error(f"Erreur ajout ingrédients recette: {e}")
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")
                logger.error(f"Erreur render tab recettes: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3: HISTORIQUE
# ─────────────────────────────────────────────────────────────────────────────

def render_historique():
    """Historique des listes de courses"""
    service = get_courses_service()
    
    st.subheader("📚 Historique des courses")
    
    col1, col2 = st.columns(2)
    with col1:
        date_debut = st.date_input("Du", value=datetime.now() - timedelta(days=30))
    with col2:
        date_fin = st.date_input("Au", value=datetime.now())
    
    try:
        # Récupérer les articles achetés dans la période
        from src.core.models import ArticleCourses
        from sqlalchemy.orm import joinedload
        
        with obtenir_contexte_db() as db:
            articles_achetes = db.query(ArticleCourses).options(
                joinedload(ArticleCourses.ingredient)
            ).filter(
                ArticleCourses.achete == True,
                ArticleCourses.achete_le >= datetime.combine(date_debut, datetime.min.time()),
                ArticleCourses.achete_le <= datetime.combine(date_fin, datetime.max.time())
            ).all()
        
        if not articles_achetes:
            st.info("Aucun achat pendant cette période")
            return
        
        # Statistiques
        total_articles = len(articles_achetes)
        rayons_utilises = set(a.rayon_magasin for a in articles_achetes if a.rayon_magasin)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Articles achetés", total_articles)
        with col2:
            st.metric("🪑 Rayons différents", len(rayons_utilises))
        with col3:
            priorite_haute = len([a for a in articles_achetes if a.priorite == "haute"])
            st.metric("🔴 Haute priorité", priorite_haute)
        
        st.divider()
        
        # Tableau détaillé
        st.subheader("📋 Détail des achats")
        
        df = pd.DataFrame([{
            "Article": a.ingredient.nom if a.ingredient else "N/A",
            "Quantité": f"{a.quantite_necessaire} {a.ingredient.unite if a.ingredient else ''}",
            "Priorité": PRIORITY_EMOJIS.get(a.priorite, "⚫") + " " + a.priorite,
            "Rayon": a.rayon_magasin or "N/A",
            "Acheté le": a.achete_le.strftime("%d/%m/%Y %H:%M") if a.achete_le else "N/A",
            "IA": "✨" if a.suggere_par_ia else ""
        } for a in articles_achetes])
        
        st.dataframe(df, use_container_width=True)
        
        # Export CSV - directement, sans button wrapper
        if df is not None and not df.empty:
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Télécharger en CSV",
                data=csv,
                file_name=f"historique_courses_{date_debut}_{date_fin}.csv",
                mime="text/csv"
            )
        
    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")
        logger.error(f"Erreur historique: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4: MODÈLES RÉCURRENTS
# ─────────────────────────────────────────────────────────────────────────────

def render_modeles():
    """Gestion des modèles de listes récurrentes (Phase 2: Persistance BD)"""
    st.subheader("📄 Modèles de listes - Phase 2")
    
    service = get_courses_service()
    
    try:
        # Récupérer modèles depuis BD (Phase 2)
        modeles = service.get_modeles(utilisateur_id=None)  # TODO: user_id depuis auth
        
        tab_mes_modeles, tab_nouveau = st.tabs(["📋 Mes modèles", "➕ Nouveau"])
        
        # ─────────────────────────────────────────────────────────────────────────────
        # ONGLET: MES MODÈLES (affichage et actions)
        # ─────────────────────────────────────────────────────────────────────────────
        
        with tab_mes_modeles:
            st.write("**Modèles sauvegardés en BD**")
            
            if not modeles:
                st.info("✨ Aucun modèle sauvegardé. Créez-en un dans l'onglet 'Nouveau'!")
            else:
                for modele in modeles:
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            st.write(f"**📋 {modele['nom']}**")
                            if modele.get('description'):
                                st.caption(f"📝 {modele['description']}")
                            st.caption(f"📦 {len(modele.get('articles', []))} articles | 📅 {modele.get('cree_le', '')[:10]}")
                        
                        with col2:
                            if st.button("📥 Charger", key=f"modele_load_{modele['id']}", use_container_width=True, help="Charger ce modèle dans la liste"):
                                try:
                                    # Appliquer le modèle (crée articles courses)
                                    article_ids = service.appliquer_modele(modele['id'])
                                    if not article_ids:
                                        st.warning(f"⚠️ Modèle chargé mais aucun article trouvé")
                                    else:
                                        st.success(f"✅ Modèle chargé ({len(article_ids)} articles)!")
                                        st.session_state.courses_refresh += 1
                                        st.rerun()
                                except Exception as e:
                                    import traceback
                                    st.error(f"❌ Erreur: {str(e)}")
                                    with st.expander("📋 Détails d'erreur"):
                                        st.code(traceback.format_exc())
                        
                        with col3:
                            if st.button("🗑️ Supprimer", key=f"modele_del_{modele['id']}", use_container_width=True, help="Supprimer ce modèle"):
                                try:
                                    service.delete_modele(modele['id'])
                                    st.success("✅ Modèle supprimé!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Erreur: {str(e)}")
                        
                        # Afficher les articles du modèle
                        with st.expander(f"👁️ Voir {len(modele.get('articles', []))} articles"):
                            for article in modele.get('articles', []):
                                priorite_emoji = "🔴" if article['priorite'] == 'haute' else ("🟡" if article['priorite'] == 'moyenne' else "🟢")
                                st.write(f"{priorite_emoji} **{article['nom']}** - {article['quantite']} {article['unite']} ({article['rayon']})")
                                if article.get('notes'):
                                    st.caption(f"📌 {article['notes']}")
        
        # ─────────────────────────────────────────────────────────────────────────────
        # ONGLET: CRÉER NOUVEAU MODÈLE
        # ─────────────────────────────────────────────────────────────────────────────
        
        with tab_nouveau:
            st.write("**Sauvegarder la liste actuelle comme modèle réutilisable**")
            
            # Récupérer liste actuelle
            liste_actuelle = service.get_liste_courses(achetes=False)
            
            if not liste_actuelle:
                st.warning("⚠️ La liste est vide. Ajoutez des articles d'abord!")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    nom_modele = st.text_input(
                        "Nom du modèle",
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
                
                # Aperçu des articles à sauvegarder
                st.subheader(f"📦 Articles ({len(liste_actuelle)})")
                for i, article in enumerate(liste_actuelle):
                    priorite_emoji = "🔴" if article['priorite'] == 'haute' else ("🟡" if article['priorite'] == 'moyenne' else "🟢")
                    st.write(f"{i+1}. {priorite_emoji} **{article['ingredient_nom']}** - {article['quantite_necessaire']} {article['unite']} ({article['rayon_magasin']})")
                
                st.divider()
                
                if st.button("💾 Sauvegarder comme modèle", use_container_width=True, type="primary"):
                    if not nom_modele or nom_modele.strip() == "":
                        st.error("⚠️ Entrez un nom pour le modèle")
                    else:
                        try:
                            # Préparer les données articles
                            articles_data = [{
                                "ingredient_id": a.get("ingredient_id"),
                                "nom": a.get("ingredient_nom"),
                                "quantite": float(a.get("quantite_necessaire", 1.0)),
                                "unite": a.get("unite", "pièce"),
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
                            
                            st.success(f"✅ Modèle '{nom_modele}' créé et sauvegardé en BD!")
                            st.balloons()
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erreur lors de la sauvegarde: {str(e)}")
                            logger.error(f"Erreur create_modele: {e}")
    
    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")
        logger.error(f"Erreur render_modeles: {e}")



# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5: OUTILS
# ─────────────────────────────────────────────────────────────────────────────

def render_outils():
    """Outils utilitaires - Phase 2: Code-barres, partage, UX améliorée"""
    st.subheader("📧 Outils")
    
    # PHASE 2 FEATURES
    tab_barcode, tab_share, tab_export, tab_stats = st.tabs([
        "📱 Code-barres (PHASE 2)",
        "👥 Partage (PHASE 2)", 
        "💾 Export/Import", 
        "📊 Stats"
    ])
    
    # ─────────────────────────────────────────────────────────────────────────────
    # PHASE 2: CODE-BARRES SCANNING
    # ─────────────────────────────────────────────────────────────────────────────
    
    with tab_barcode:
        st.write("**📱 Scanner code-barres pour saisie rapide**")
        st.info("⏳ Phase 2 - En développement")
        
        # Simuler la structure Phase 2
        col1, col2 = st.columns(2)
        with col1:
            st.write("""
            **Fonctionnalités planifiées:**
            - 📱 Scan code-barres avec webcam
            - 🔍 Reconnaissance automatique article
            - ⚡ Saisie 10x plus rapide
            - 📊 Base de codes-barres articles
            """)
        with col2:
            st.write("""
            **Intégration:**
            - Ajout rapide en magasin
            - Sync prix automatique
            - Recommandations marque
            - Export liste code-barres
            """)
        
        st.divider()
        st.markdown("**Estimation:** 2-3 jours (composant scanning + base données)")
    
    # ─────────────────────────────────────────────────────────────────────────────
    # PHASE 2: PARTAGE MULTI-UTILISATEURS
    # ─────────────────────────────────────────────────────────────────────────────
    
    with tab_share:
        st.write("**👥 Partager liste avec famille/colocataires**")
        st.info("⏳ Phase 2 - En développement")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("""
            **Fonctionnalités planifiées:**
            - 👥 Partage par email/lien
            - 📄 Sync temps réel
            - ✅ Permissions (lecture/écriture)
            - 📱 Notifications mises à jour
            """)
        with col2:
            st.write("""
            **Avantages:**
            - Colocataires voient qui achète
            - Une seule liste partagée
            - Pas de doublons articles
            - Historique collaboratif
            """)
        
        st.divider()
        
        # Structure Phase 2
        st.subheader("Configuration partage (à venir)")
        shared_with = st.multiselect(
            "Partager avec:",
            ["Alice", "Bob", "Charlie"],
            disabled=True,
            help="Disponible en Phase 2"
        )
        
        st.markdown("**Estimation:** 3-4 jours (BD + permissions + notifications)")
    
    # ─────────────────────────────────────────────────────────────────────────────
    # EXPORT/IMPORT (EXISTANT)
    # ─────────────────────────────────────────────────────────────────────────────
    
    with tab_export:
        st.write("**Exporter/Importer listes**")
        
        col1, col2 = st.columns(2)
        with col1:
            service = get_courses_service()
            liste = service.get_liste_courses(achetes=False)
            
            if liste:
                df = pd.DataFrame([{
                    "Article": a.get('ingredient_nom'),
                    "Quantité": a.get('quantite_necessaire'),
                    "Unité": a.get('unite'),
                    "Priorité": a.get('priorite'),
                    "Rayon": a.get('rayon_magasin'),
                    "Notes": a.get('notes', '')
                } for a in liste])
                
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Télécharger liste (CSV)",
                    data=csv,
                    file_name=f"liste_courses_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            uploaded = st.file_uploader("📤 Importer liste (CSV)", type=["csv"], key="import_csv")
            if uploaded:
                try:
                    import io
                    df_import = pd.read_csv(io.BytesIO(uploaded.getvalue()))
                    st.write(f"✅ Fichier contient {len(df_import)} articles")
                    
                    if st.button("✅ Confirmer import"):
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
                                    unite=row.get('Unité', 'pièce')
                                )
                                db.add(ingredient)
                                db.commit()
                            
                            service.create({
                                "ingredient_id": ingredient.id,
                                "quantite_necessaire": float(row['Quantité']),
                                "priorite": row.get('Priorité', 'moyenne'),
                                "rayon_magasin": row.get('Rayon', 'Autre'),
                                "notes": row.get('Notes')
                            })
                            count += 1
                        
                        st.success(f"✅ {count} articles importés!")
                        st.session_state.courses_refresh += 1
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur import: {str(e)}")
    
    # ─────────────────────────────────────────────────────────────────────────────
    # STATISTIQUES GLOBALES (EXISTANT + PHASE 2)
    # ─────────────────────────────────────────────────────────────────────────────
    
    with tab_stats:
        st.write("**📊 Statistiques globales**")
        
        try:
            service = get_courses_service()
            
            # Stats existantes
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                liste = service.get_liste_courses(achetes=False)
                st.metric("📋 Articles actifs", len(liste))
            with col2:
                liste_achetee = service.get_liste_courses(achetes=True)
                st.metric("✅ Articles achetés", len(liste_achetee))
            with col3:
                rayons = set(a.get('rayon_magasin') for a in liste if a.get('rayon_magasin'))
                st.metric("🪑 Rayons utilisés", len(rayons))
            with col4:
                st.metric("⏲️ Dernière mise à jour", datetime.now().strftime("%H:%M"))
            
            st.divider()
            
            # Stats par priorité
            col1, col2, col3 = st.columns(3)
            with col1:
                haute = len([a for a in liste if a.get('priorite') == 'haute'])
                st.metric("🔴 Haute", haute)
            with col2:
                moyenne = len([a for a in liste if a.get('priorite') == 'moyenne'])
                st.metric("🟡 Moyenne", moyenne)
            with col3:
                basse = len([a for a in liste if a.get('priorite') == 'basse'])
                st.metric("🟢 Basse", basse)
            
            st.divider()
            
            # Phase 2: Budgeting
            st.subheader("💰 Budget tracking (PHASE 2)")
            
        except Exception as e:
            st.error(f"❌ Erreur chargement stats: {str(e)}")


# ─────────────────────────────────────────────────────────────────────────────
# SYNCHRONISATION TEMPS RÉEL
# ─────────────────────────────────────────────────────────────────────────────


def _init_realtime_sync():
    """Initialise la synchronisation temps réel."""
    if "realtime_initialized" not in st.session_state:
        st.session_state.realtime_initialized = False
    
    try:
        sync_service = get_realtime_sync_service()
        
        if sync_service.is_configured and not st.session_state.realtime_initialized:
            # Récupérer l'utilisateur courant
            user_id = st.session_state.get("user_id", "anonymous")
            user_name = st.session_state.get("user_name", "Utilisateur")
            
            # Rejoindre le canal de synchronisation (liste par défaut = 1)
            liste_id = st.session_state.get("liste_active_id", 1)
            
            if sync_service.join_list(liste_id, user_id, user_name):
                st.session_state.realtime_initialized = True
                logger.info(f"Sync temps réel initialisée pour liste {liste_id}")
        
    except Exception as e:
        logger.warning(f"Sync temps réel non disponible: {e}")


def render_realtime_status():
    """Affiche le statut de synchronisation temps réel."""
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
            st.markdown("### 📄 Synchronisation")
            
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
        logger.debug(f"Statut realtime non affiché: {e}")


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
        logger.debug(f"Broadcast non envoyé: {e}")
