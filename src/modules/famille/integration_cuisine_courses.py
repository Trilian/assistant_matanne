"""
Intégration Cuisine/Courses/Famille

Connexions entre modules:
- Suggestions de recettes basées sur objectifs santé
- Pré-remplissage shopping depuis activités planifiées
- Calories tracking depuis recettes vers santé
- Budgets partagés entre famille et courses
"""

import streamlit as st
from datetime import date, timedelta
from typing import List, Dict
import pandas as pd

from src.core.database import get_db
from src.core.models import HealthObjective, FamilyActivity, ShoppingItem, HealthEntry

# Logique métier pure (si existe)
try:
    from src.modules.famille.integration_logic import (
        mapper_objectifs_recettes,
        calculer_calories_objectifs
    )
except ImportError:
    pass  # Pas de logic file pour intégration

from src.modules.famille.helpers import (
    get_objectives_actifs,
    get_activites_semaine,
    get_stats_santé_semaine
)


# ════════════════════════════════════════════════════════════════════════════
# INTEGRATION CUISINE
# ════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=1800)
def get_recipe_suggestions(objectifs: List[Dict]) -> Dict:
    """
    Suggère des recettes basées sur les objectifs santé
    
    Args:
        objectifs: Liste d'HealthObjective
    
    Returns:
        Dict avec recettes suggérées et leurs propriétés nutritionnelles
    """
    
    # Mapper objectifs à types de recettes
    recette_map = {
        "endurance": {
            "label": "Recettes pour l'endurance",
            "recettes": [
                {
                    "nom": "Pâtes complètes sauce tomate",
                    "calories": 450,
                    "proteines": 15,
                    "glucides": 65,
                    "lipides": 8,
                    "temps": 20,
                    "difficulte": "facile"
                },
                {
                    "nom": "Poulet grillé avec riz",
                    "calories": 520,
                    "proteines": 35,
                    "glucides": 55,
                    "lipides": 10,
                    "temps": 25,
                    "difficulte": "facile"
                },
                {
                    "nom": "Oeufs brouillés avec toast complet",
                    "calories": 350,
                    "proteines": 20,
                    "glucides": 35,
                    "lipides": 12,
                    "temps": 10,
                    "difficulte": "très facile"
                }
            ]
        },
        "poids": {
            "label": "Recettes légères",
            "recettes": [
                {
                    "nom": "Salade composée poulet",
                    "calories": 280,
                    "proteines": 30,
                    "glucides": 15,
                    "lipides": 8,
                    "temps": 15,
                    "difficulte": "très facile"
                },
                {
                    "nom": "Soupe légumes lentilles",
                    "calories": 200,
                    "proteines": 15,
                    "glucides": 25,
                    "lipides": 3,
                    "temps": 30,
                    "difficulte": "facile"
                },
                {
                    "nom": "Omelette blanche avec légumes",
                    "calories": 220,
                    "proteines": 18,
                    "glucides": 8,
                    "lipides": 10,
                    "temps": 12,
                    "difficulte": "facile"
                }
            ]
        },
        "muscle": {
            "label": "Recettes riches en protéines",
            "recettes": [
                {
                    "nom": "Escalope de poulet panée",
                    "calories": 380,
                    "proteines": 45,
                    "glucides": 20,
                    "lipides": 12,
                    "temps": 20,
                    "difficulte": "facile"
                },
                {
                    "nom": "Steak haché avec pâtes",
                    "calories": 580,
                    "proteines": 50,
                    "glucides": 50,
                    "lipides": 18,
                    "temps": 25,
                    "difficulte": "facile"
                },
                {
                    "nom": "Filet poisson sauce citron",
                    "calories": 320,
                    "proteines": 40,
                    "glucides": 10,
                    "lipides": 12,
                    "temps": 20,
                    "difficulte": "facile"
                }
            ]
        },
        "nutrition": {
            "label": "Recettes équilibrées",
            "recettes": [
                {
                    "nom": "Menu équilibré (riz, légumes, poisson)",
                    "calories": 420,
                    "proteines": 35,
                    "glucides": 40,
                    "lipides": 12,
                    "temps": 30,
                    "difficulte": "facile"
                },
                {
                    "nom": "Couscous légumes pois chiche",
                    "calories": 380,
                    "proteines": 20,
                    "glucides": 50,
                    "lipides": 8,
                    "temps": 25,
                    "difficulte": "facile"
                }
            ]
        }
    }
    
    suggestions = {}
    for objectif in objectifs:
        cat = objectif['categorie'].lower()
        if cat in recette_map:
            suggestions[cat] = recette_map[cat]
    
    return suggestions


@st.cache_data(ttl=1800)
def get_shopping_from_recipes(recettes_selectionnees: List[str]) -> List[Dict]:
    """
    Génère une liste de courses à partir des recettes sélectionnées
    
    Args:
        recettes_selectionnees: Liste des noms de recettes
    
    Returns:
        Liste des ingrédients à acheter
    """
    
    # Mapping recette -> ingrédients
    ingredients_map = {
        "Pâtes complètes sauce tomate": [
            ("Pâtes complètes", 500, "g", "épicerie"),
            ("Sauce tomate", 500, "ml", "épicerie"),
            ("Oignon", 2, "pièces", "fruits_légumes"),
            ("Ail", 2, "gousses", "fruits_légumes"),
            ("Huile olive", 3, "cl", "épicerie")
        ],
        "Poulet grillé avec riz": [
            ("Poulet fermier", 600, "g", "viandes"),
            ("Riz blanc", 250, "g", "épicerie"),
            ("Citron", 1, "pièce", "fruits_légumes"),
            ("Huile olive", 2, "cl", "épicerie")
        ],
        "Salade composée poulet": [
            ("Poulet rôti", 400, "g", "viandes"),
            ("Laitue", 1, "pièce", "fruits_légumes"),
            ("Tomate", 3, "pièces", "fruits_légumes"),
            ("Concombre", 1, "pièce", "fruits_légumes"),
            ("Vinaigrette", 5, "cl", "épicerie")
        ],
        "Omelette blanche avec légumes": [
            ("Oeufs", 3, "pièces", "épicerie"),
            ("Poivron", 1, "pièce", "fruits_légumes"),
            ("Champignons", 200, "g", "fruits_légumes"),
            ("Beurre", 10, "g", "lait_produits")
        ],
        "Escalope de poulet panée": [
            ("Escalope de poulet", 600, "g", "viandes"),
            ("Oeuf", 2, "pièces", "épicerie"),
            ("Chapelure", 100, "g", "épicerie"),
            ("Citron", 1, "pièce", "fruits_légumes")
        ]
    }
    
    shopping_list = []
    for recette in recettes_selectionnees:
        if recette in ingredients_map:
            for ingredient, qty, unit, cat in ingredients_map[recette]:
                shopping_list.append({
                    "ingredient": ingredient,
                    "quantite": qty,
                    "unite": unit,
                    "categorie": cat,
                    "recette": recette
                })
    
    return shopping_list


# ════════════════════════════════════════════════════════════════════════════
# INTEGRATION COURSES
# ════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=1800)
def get_shopping_from_activities(activites: List) -> List[Dict]:
    """
    Pré-remplit le shopping depuis les activités planifiées
    
    Exemples:
    - Pique-nique → fruits, sandwichs, boissons
    - Parc → snacks, eau
    - Piscine → fruits secs, eau
    """
    
    activity_shopping_map = {
        "picnic": [
            ("Fruits (pommes, raisins)", "fruits_légumes"),
            ("Pain sandwich", "épicerie"),
            ("Fromage", "lait_produits"),
            ("Jambon", "viandes"),
            ("Jus de fruits", "boissons"),
            ("Eau minérale", "boissons"),
            ("Gâteaux secs", "épicerie")
        ],
        "parc": [
            ("Fruits secs", "épicerie"),
            ("Barre granola", "épicerie"),
            ("Eau plate", "boissons"),
            ("Mouchoirs", "hygiène")
        ],
        "piscine": [
            ("Fruits secs", "épicerie"),
            ("Eau mineral", "boissons"),
            ("Banane", "fruits_légumes")
        ],
        "restaurant": [
            ("Mouchoirs", "hygiène"),
            ("Jouets poche", "jouets")
        ],
        "sport": [
            ("Eau plate", "boissons"),
            ("Banane", "fruits_légumes"),
            ("Fruits secs", "épicerie")
        ]
    }
    
    shopping = []
    for activity in activites:
        activity_type = activity.get('type', activity.type_activite) if hasattr(activity, 'type_activite') else activity.get('type')
        if activity_type and activity_type in activity_shopping_map:
            items = activity_shopping_map[activity_type]
            for item_name, category in items:
                activity_titre = activity.get('titre', activity.titre) if hasattr(activity, 'titre') else activity.get('titre')
                activity_date = activity.get('date', activity.date_prevue) if hasattr(activity, 'date_prevue') else activity.get('date')
                shopping.append({
                    "item": item_name,
                    "categorie": category,
                    "activite": activity_titre,
                    "date_activite": activity_date
                })
    
    return shopping


def add_shopping_items_from_integration(items_list: List[Dict], liste_type="Nous"):
    """Ajoute des items au shopping depuis l'intégration"""
    try:
        with get_db() as db:
            for item_data in items_list:
                existing = db.query(ShoppingItem).filter(
                    ShoppingItem.titre == item_data.get("item") or item_data.get("ingredient"),
                    ShoppingItem.date_ajout == date.today(),
                    ShoppingItem.actif == True
                ).first()
                
                if not existing:
                    shopping_item = ShoppingItem(
                        titre=item_data.get("item") or item_data.get("ingredient"),
                        categorie=item_data.get("categorie"),
                        quantite=item_data.get("quantite", 1),
                        liste=liste_type,
                    date_ajout=date.today(),
                    actif=True
                )
                db.add(shopping_item)
        
        db.commit()
        return True
    except Exception as e:
        st.error(f"❌ Erreur ajout items: {e}")
        return False


# ════════════════════════════════════════════════════════════════════════════
# INTEGRATION SANTÉ/NUTRITION
# ════════════════════════════════════════════════════════════════════════════

def get_nutrition_from_recipe(recipe: Dict) -> Dict:
    """Extrait les infos nutritionnelles d'une recette"""
    return {
        "calories": recipe.get("calories", 0),
        "proteines": recipe.get("proteines", 0),
        "glucides": recipe.get("glucides", 0),
        "lipides": recipe.get("lipides", 0)
    }


def log_meal_to_health_tracker(recipe_name: str, calories: int, timestamp=None):
    """Enregistre un repas dans le tracker santé"""
    try:
        with get_db() as db:
            entry = HealthEntry(
                type_activite="repas",
                duree_minutes=0,
                calories_brulees=-calories,  # Négatif = apport calorique
                note_type="nutrition",
                description=recipe_name
            )
            
            db.add(entry)
            db.commit()
            return True
    except Exception as e:
        st.error(f"❌ Erreur enregistrement santé: {e}")
        return False


# ════════════════════════════════════════════════════════════════════════════
# STREAMLIT: TAB INTÉGRATION
# ════════════════════════════════════════════════════════════════════════════

def app():
    """Affiche l'onglet intégration Cuisine/Courses/Santé"""
    
    st.subheader("🔗 Intégrations Cuisine & Courses")
    
    # Section 1: Recettes suggérées
    st.markdown("## 🍳 Recettes suggérées par vos objectifs")
    
    try:
        objectifs = get_objectives_actifs()
        
        if objectifs:
            suggestions = get_recipe_suggestions(objectifs)
            
            if suggestions:
                # Réciter les objectifs actifs
                st.write("**Vos objectifs actuels:**")
                for obj in objectifs:
                    progress = (obj.valeur_actuelle or 0) / (obj.valeur_cible or 1) * 100
                    st.progress(min(progress / 100, 1.0), text=f"{obj.titre} ({progress:.0f}%)")
                
                st.divider()
                
                for category, recette_info in suggestions.items():
                    with st.expander(f"📚 {recette_info['label']}", expanded=False):
                        
                        recettes = recette_info['recettes']
                        
                        for recette in recettes:
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"**{recette['nom']}** ⏱️ {recette['temps']}min")
                                
                                # Nutrition info
                                cols = st.columns(4)
                                with cols[0]:
                                    st.caption(f"🔥 {recette['calories']} cal")
                                with cols[1]:
                                    st.caption(f"🥩 {recette['proteines']}g protéines")
                                with cols[2]:
                                    st.caption(f"🌾 {recette['glucides']}g glucides")
                                with cols[3]:
                                    st.caption(f"🧈 {recette['lipides']}g lipides")
                            
                            with col2:
                                if st.button(f"Ajouter au shopping", key=f"recipe_{recette['nom']}"):
                                    # Ajouter ingrédients au shopping
                                    ingredients = get_shopping_from_recipes([recette['nom']])
                                    if add_shopping_items_from_integration(ingredients):
                                        st.success(f"✅ {recette['nom']} ajouté au shopping!")
            
            else:
                st.info("ℹ️ Aucun objectif pour suggérer des recettes")
        
        else:
            st.info("ℹ️ Aucun objectif santé actif")
    
    except Exception as e:
        st.error(f"❌ Erreur suggestions: {e}")
    
    st.divider()
    
    # Section 2: Shopping depuis activités
    st.markdown("## 🛒 Pré-remplir le shopping depuis activités")
    
    try:
        activites = get_activites_semaine()
        
        if activites:
            st.write("**Activités cette semaine:**")
            for activity in activites:
                titre = activity.get('titre', activity.titre) if hasattr(activity, 'titre') else activity.get('titre', 'Sans titre')
                date_act = activity.get('date', activity.date_prevue) if hasattr(activity, 'date_prevue') else activity.get('date', '?')
                st.write(f"📅 {titre} - {date_act}")
            
            if st.button("📋 Pré-remplir shopping depuis ces activités"):
                shopping_from_act = get_shopping_from_activities(activites)
                if shopping_from_act:
                    if add_shopping_items_from_integration(shopping_from_act):
                        st.success("✅ Shopping mis à jour avec articles pour les activités!")
                else:
                    st.info("ℹ️ Aucune suggestion de shopping pour ces activités")
        
        else:
            st.info("ℹ️ Aucune activité prévue cette semaine")
    
    except Exception as e:
        st.error(f"❌ Erreur activités: {e}")
    
    st.divider()
    
    # Section 3: Résumé nutritionnel semaine
    st.markdown("## 📊 Résumé nutritionnel semaine")
    
    try:
        stats = get_stats_santé_semaine()
        
        if stats:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_calories = sum(entry.calories_brulees or 0 for entry in stats if entry.calories_brulees)
                st.metric("🔥 Calories brûlées", f"{total_calories:.0f}")
            
            with col2:
                avg_energie = sum(entry.note_energie or 0 for entry in stats) / max(len(stats), 1)
                st.metric("⚡ Énergie moyenne", f"{avg_energie:.1f}/10")
            
            with col3:
                avg_moral = sum(entry.note_moral or 0 for entry in stats) / max(len(stats), 1)
                st.metric("😊 Moral moyen", f"{avg_moral:.1f}/10")
        
        else:
            st.info("ℹ️ Aucune donnée santé cette semaine")
    
    except Exception as e:
        st.error(f"❌ Erreur stats: {e}")


if __name__ == "__main__":
    show_integration_tab()
