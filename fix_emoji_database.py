#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de nettoyage des emojis corrompus en base de donnees.
Corrige les emojis UTF-8 mal encodes dans tous les modeles.
"""

import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent))

from src.core.database import obtenir_contexte_db
from src.core.models import (
    Ingredient, Recette, ArticleCourses
)

# Mapping des emojis corrompus vers leurs versions correctes
# Les cles sont les sequences de bytes mal interpretees
EMOJI_FIXES = {
    # Emojis corrompus (UTF-8 mal decode en Latin-1)
    'ðŸ"´': '🔴',      # Rouge
    'ðŸŸ¢': '🟢',      # Vert
    'ðŸŸ¡': '🟡',      # Jaune  
    'ðŸ'ª': '💪',      # Bras
    'ðŸƒ': '🏃',       # Course
    'ðŸŽ¯': '🎯',      # Cible
    'ðŸŽ': '🍎',       # Pomme
    'ðŸ"¥': '🔥',      # Feu
    'ðŸ˜Š': '😊',      # Smiley
    'âšª': '⚫',        # Cercle noir
    'âž•': '➕',        # Plus
}



def corriger_texte(texte: str) -> str:
    """Remplace tous les emojis corrompus dans un texte."""
    if not texte:
        return texte
    
    resultat = texte
    for old, new in EMOJI_FIXES.items():
        if old in resultat:
            print(f"   Remplacement: {old} -> {new}")
            resultat = resultat.replace(old, new)
    return resultat


def corriger_ingredients():
    """Corriger les emojis dans les ingredients."""
    print("\n1. Traitement des ingredients...")
    with obtenir_contexte_db() as db:
        ingredients = db.query(Ingredient).all()
        count = 0
        
        for ing in ingredients:
            nom_original = ing.nom
            ing.nom = corriger_texte(ing.nom)
            ing.categorie = corriger_texte(ing.categorie) if ing.categorie else None
            
            if ing.nom != nom_original:
                count += 1
                print(f"   OK '{nom_original}' -> '{ing.nom}'")
        
        if count > 0:
            db.commit()
            print(f"   TOTAL: {count} ingredient(s) mis a jour")
        else:
            print("   OK Aucun ingredient a corriger")


def corriger_recettes():
    """Corriger les emojis dans les recettes."""
    print("\n2. Traitement des recettes...")
    with obtenir_contexte_db() as db:
        recettes = db.query(Recette).all()
        count = 0
        
        for recette in recettes:
            nom_original = recette.nom
            recette.nom = corriger_texte(recette.nom)
            recette.description = corriger_texte(recette.description) if recette.description else None
            
            if recette.nom != nom_original:
                count += 1
                print(f"   OK '{nom_original}' -> '{recette.nom}'")
        
        if count > 0:
            db.commit()
            print(f"   TOTAL: {count} recette(s) mise(s) a jour")
        else:
            print("   OK Aucune recette a corriger")


def corriger_courses():
    """Corriger les emojis dans les courses."""
    print("\n3. Traitement des courses...")
    with obtenir_contexte_db() as db:
        articles = db.query(ArticleCourses).all()
        count = 0
        
        for article in articles:
            notes_original = article.notes
            article.notes = corriger_texte(article.notes) if article.notes else None
            article.rayon_magasin = corriger_texte(article.rayon_magasin) if article.rayon_magasin else None
            
            if article.notes != notes_original:
                count += 1
        
        if count > 0:
            db.commit()
            print(f"   TOTAL: {count} article(s) de course mis a jour")
        else:
            print("   OK Aucun article a corriger")


if __name__ == "__main__":
    print("=" * 70)
    print("NETTOYAGE des emojis corrompus en base de donnees")
    print("=" * 70)
    
    try:
        corriger_ingredients()
        corriger_recettes()
        corriger_courses()
        
        print("\n" + "=" * 70)
        print("SUCCES: Nettoyage termine!")
        print("=" * 70)
    except Exception as e:
        print(f"\nERREUR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

