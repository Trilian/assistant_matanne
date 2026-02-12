#!/usr/bin/env python3
"""
Script pour charger les 50 recettes standard dans la base de donnÃ©es.
Usage: python seed_recettes.py
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv('.env.local')

from src.core.database import obtenir_fabrique_session, initialiser_database, obtenir_contexte_db
from src.core.models import Recette, RecetteIngredient, Ingredient, EtapeRecette
from sqlalchemy.orm import Session

def load_recettes_from_json(db: Session):
    """Charge les recettes depuis le fichier JSON standard."""
    
    json_path = Path(__file__).parent / "data" / "recettes_standard.json"
    
    if not json_path.exists():
        print(f"âŒ Fichier non trouvÃ©: {json_path}")
        return
    
    print(f"ðŸ“– Chargement des recettes depuis {json_path}...")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    recettes_data = data.get('recettes', [])
    print(f"ðŸ“ {len(recettes_data)} recettes Ã  charger...")
    
    loaded = 0
    skipped = 0
    
    for recette_data in recettes_data:
        try:
            # VÃ©rifier si la recette existe dÃ©jÃ 
            existing = db.query(Recette).filter(
                Recette.nom == recette_data['nom']
            ).first()
            
            if existing:
                skipped += 1
                continue
            
            # CrÃ©er la recette
            recette = Recette(
                nom=recette_data['nom'],
                description=recette_data.get('description', ''),
                temps_preparation=recette_data.get('temps_preparation', 30),
                temps_cuisson=recette_data.get('temps_cuisson', 20),
                portions=recette_data.get('portions', 4),
                difficulte=recette_data.get('difficulte', 'moyen'),
                type_repas=recette_data.get('type_repas', 'dÃ®ner'),
                saison=recette_data.get('saison', 'toute_annee'),
                url_image=recette_data.get('url_image'),
            )
            
            # Ajouter les ingrÃ©dients
            for ing_data in recette_data.get('ingredients', []):
                ingredient = Ingredient(
                    nom=ing_data['nom'],
                    unite=ing_data.get('unite', 'g'),
                )
                recette_ingredient = RecetteIngredient(
                    ingredient=ingredient,
                    quantite=ing_data.get('quantite', 100),
                )
                recette.ingredients.append(recette_ingredient)
            
            # Ajouter les Ã©tapes
            for ordre, etape_text in enumerate(recette_data.get('etapes', []), 1):
                etape = EtapeRecette(
                    ordre=ordre,
                    description=etape_text,
                )
                recette.etapes.append(etape)
            
            db.add(recette)
            loaded += 1
            
        except Exception as e:
            print(f"âš ï¸ Erreur pour {recette_data.get('nom', 'INCONNU')}: {e}")
    
    # Commit
    try:
        db.commit()
        print(f"\nâœ… {loaded} recettes chargÃ©es")
        if skipped:
            print(f"â­ï¸ {skipped} recettes dÃ©jÃ  prÃ©sentes (skip)")
    except Exception as e:
        db.rollback()
        print(f"âŒ Erreur lors de la sauvegarde: {e}")

if __name__ == "__main__":
    print("ðŸŒ¾ Initialisation de la base de donnÃ©es...")
    
    # Initialiser la BD
    initialiser_database()
    
    # Obtenir une session
    SessionLocal = obtenir_fabrique_session()
    db = SessionLocal()
    
    try:
        load_recettes_from_json(db)
        print("\nâœ… Seed complÃ¨te!")
    except Exception as e:
        print(f"âŒ Erreur: {e}")
    finally:
        db.close()
