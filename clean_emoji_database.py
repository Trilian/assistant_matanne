#!/usr/bin/env python3
"""Script de nettoyage des emojis corrompus dans la base de données"""

import re
import logging
from src.core.database import obtenir_contexte_db
from src.core.models import ArticleCourses, Ingredient, ModeleCourses, ArticleModele

logger = logging.getLogger(__name__)

# Map des emojis corrompus vers les bons emojis
EMOJI_FIXES = {
    'ðŸ"´': '🍞',     # Pain
    'ðŸ¥•': '🥕',     # Carotte
    'ðŸ…': '🍅',       # Tomate
    'ðŸ§': '🧀',      # Fromage
    'ðŸ„': '🍄',      # Champignon
    'ðŸ¥¦': '🥦',     # Brocoli
    'ðŸ¥': '🥔',      # Pomme de terre
    'ðŸ§': '🧅',      # Oignon
    'ðŸ': '🍎',       # Pomme
    'ðŸŠ': '🍊',      # Orange
    'ðŸ‹': '🍋',      # Citron
    'ðŸ': '🍌',      # Banane
    'ðŸ"': '🍓',      # Fraise
    'ðŸ«': '🍫',      # Chocolat
    'ðŸ½': '🍽',      # Assiette
    'ðŸ¥„': '🥄',     # Cuillère
    'ðŸ¥¢': '🥢',     # Baguettes
    'ðŸ°': '🍰',      # Gâteau
    'ðŸª': '🍪',      # Biscuit
    'ðŸ¥›': '🥛',     # Verre de lait
    'ðŸ§ˆ': '🧈',     # Beurre
    'ðŸ§': '🧂',      # Sel
    'â': 'à',
    'ê': 'ê',
    'ô': 'ô',
    'â€"': '–',
    'â€"': '—',
}

def clean_string(text: str) -> str:
    """Nettoie les emojis et caractères corrompus"""
    if not text:
        return text
    
    for corrupted, fixed in EMOJI_FIXES.items():
        text = text.replace(corrupted, fixed)
    
    return text

def clean_database():
    """Nettoie tous les emojis corrompus dans la BD"""
    print("\n" + "="*60)
    print("🧹 NETTOYAGE DES EMOJIS CORROMPUS")
    print("="*60)
    
    try:
        with obtenir_contexte_db() as db:
            count = 0
            
            # Nettoyer ArticleCourses
            print("\n📦 Nettoyage ArticleCourses...")
            articles = db.query(ArticleCourses).all()
            for article in articles:
                cleaned_notes = clean_string(article.notes) if article.notes else None
                if cleaned_notes != article.notes:
                    article.notes = cleaned_notes
                    count += 1
            
            # Nettoyer Ingredient
            print("\n🥕 Nettoyage Ingredient...")
            ingredients = db.query(Ingredient).all()
            for ing in ingredients:
                cleaned_nom = clean_string(ing.nom) if ing.nom else None
                if cleaned_nom != ing.nom:
                    ing.nom = cleaned_nom
                    count += 1
            
            # Nettoyer ModeleCourses
            print("\n📋 Nettoyage ModeleCourses...")
            modeles = db.query(ModeleCourses).all()
            for modele in modeles:
                cleaned_nom = clean_string(modele.nom) if modele.nom else None
                cleaned_desc = clean_string(modele.description) if modele.description else None
                if cleaned_nom != modele.nom:
                    modele.nom = cleaned_nom
                    count += 1
                if cleaned_desc != modele.description:
                    modele.description = cleaned_desc
                    count += 1
            
            # Nettoyer ArticleModele
            print("\n📝 Nettoyage ArticleModele...")
            articles_modele = db.query(ArticleModele).all()
            for am in articles_modele:
                cleaned_nom = clean_string(am.nom_article) if am.nom_article else None
                cleaned_notes = clean_string(am.notes) if am.notes else None
                if cleaned_nom != am.nom_article:
                    am.nom_article = cleaned_nom
                    count += 1
                if cleaned_notes != am.notes:
                    am.notes = cleaned_notes
                    count += 1
            
            # Valider et sauvegarder
            db.commit()
            print(f"\n✅ NETTOYAGE TERMINÉ: {count} champs nettoyés!")
            print("="*60)
            
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    clean_database()
