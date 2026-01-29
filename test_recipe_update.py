#!/usr/bin/env python3
"""Test: Vérifier que les mises à jour de recettes fonctionnent maintenant"""

import sys
sys.path.insert(0, 'd:\\Projet_streamlit\\assistant_matanne')

from datetime import datetime
from src.core.database import get_db_context
from src.core.models.recettes import Recette

def test_recipe_update():
    """Test de mise à jour d'une recette avec URL d'image"""
    try:
        print("Test: Mise à jour recette avec URL d'image...")
        
        with get_db_context() as db:
            # Récupérer une recette existante ou créer une de test
            recette = db.query(Recette).first()
            
            if recette:
                print(f"✓ Recette trouvée: {recette.nom} (ID: {recette.id})")
                
                # Mettre à jour l'URL d'image
                old_url = recette.url_image
                recette.url_image = "https://example.com/test-image.jpg"
                
                db.commit()
                db.refresh(recette)
                
                print(f"✓ Mise à jour réussie!")
                print(f"  URL ancienne: {old_url}")
                print(f"  URL nouvelle: {recette.url_image}")
                print(f"  Modifiée le: {recette.modifie_le}")
                
                return True
            else:
                print("⚠ Aucune recette trouvée dans la BD pour tester")
                return False
                
    except Exception as e:
        print(f"✗ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_recipe_update()
    sys.exit(0 if success else 1)
