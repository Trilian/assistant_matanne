#!/usr/bin/env python3
"""
Script de nettoyage des emojis corrompus en base de donnees
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.core.database import obtenir_contexte_db
from src.core.models import Ingredient, Recette, ArticleCourses

# Mapping des caracteres corrompus
CORRECTIONS = []
CORRECTIONS.append(('ðŸ"´', u'\U0001f534'))  # Cercle rouge
CORRECTIONS.append(('ðŸŸ¢', u'\U0001f7e2'))  # Cercle vert
CORRECTIONS.append(('ðŸŸ¡', u'\U0001f7e1'))  # Cercle jaune
CORRECTIONS.append(('ðŸ'ª', u'\U0001f4aa'))  # Bras
CORRECTIONS.append(('ðŸƒ', u'\U0001f3c3'))   # Coureur
CORRECTIONS.append(('ðŸŽ¯', u'\U0001f3af'))  # Cible
CORRECTIONS.append(('ðŸ"¥', u'\U0001f525'))  # Feu
CORRECTIONS.append(('ðŸ˜Š', u'\U0001f60a'))  # Smiley


def nettoyer(texte):
    """Remplace les emojis corrompus"""
    if not texte:
        return texte
    for old, new in CORRECTIONS.items():
        texte = texte.replace(old, new)
    return texte


def main():
    print("Nettoyage emojis...")
    
    try:
        # Ingredients
        with obtenir_contexte_db() as db:
            for ing in db.query(Ingredient).all():
                ing.nom = nettoyer(ing.nom)
                if ing.categorie:
                    ing.categorie = nettoyer(ing.categorie)
            db.commit()
        print("✓ Ingredients nettoyes")
        
        # Recettes
        with obtenir_contexte_db() as db:
            for rec in db.query(Recette).all():
                rec.nom = nettoyer(rec.nom)
                if rec.description:
                    rec.description = nettoyer(rec.description)
            db.commit()
        print("✓ Recettes nettoyees")
        
        # Courses
        with obtenir_contexte_db() as db:
            for art in db.query(ArticleCourses).all():
                if art.notes:
                    art.notes = nettoyer(art.notes)
                if art.rayon_magasin:
                    art.rayon_magasin = nettoyer(art.rayon_magasin)
            db.commit()
        print("✓ Courses nettoyees")
        
        print("FINI!")
    except Exception as e:
        print(f"ERREUR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
