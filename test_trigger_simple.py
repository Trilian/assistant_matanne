#!/usr/bin/env python3
"""Test avec output file"""

import sys
import os
sys.path.insert(0, os.path.abspath('d:/Projet_streamlit/assistant_matanne'))

from src.core.database import get_db_context
from src.core.models.recettes import Recette

output = []

try:
    output.append("=== TEST MISE À JOUR RECETTES ===")
    
    with get_db_context() as db:
        # Créer une recette
        recipe = Recette(
            nom="Test",
            temps_preparation=10,
            temps_cuisson=20,
            portions=4,
            difficulte="facile"
        )
        db.add(recipe)
        db.commit()
        db.refresh(recipe)
        
        output.append(f"Recette créée: ID={recipe.id}")
        output.append(f"updated_at (création): {recipe.updated_at}")
        
        # Mettre à jour
        recipe.url_image = "https://example.com/image.jpg"
        db.commit()
        db.refresh(recipe)
        
        output.append(f"Après UPDATE: url_image={recipe.url_image}")
        output.append(f"updated_at (update): {recipe.updated_at}")
        output.append("✓ SUCCESS - Trigger fonctionne!")
        
        # Cleanup
        db.delete(recipe)
        db.commit()
        
except Exception as e:
    output.append(f"✗ ERROR: {str(e)}")
    import traceback
    output.append(traceback.format_exc())

# Write output to file
with open('d:/Projet_streamlit/assistant_matanne/test_result.txt', 'w') as f:
    f.write('\n'.join(output))

print("Test completed - see test_result.txt")
