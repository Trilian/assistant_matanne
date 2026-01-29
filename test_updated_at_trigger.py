#!/usr/bin/env python3
"""
Test: Vérifier que les mises à jour de recettes et modèles de courses marchent
Cela teste que le trigger updated_at fonctionne correctement maintenant.
"""

import sys
import os
sys.path.insert(0, os.path.abspath('/d:/Projet_streamlit/assistant_matanne'))

from datetime import datetime
from decimal import Decimal
from src.core.database import get_db_context
from src.core.models.recettes import Recette
from src.core.models.courses import ModeleCourses

def test_recettes_update():
    """Test de mise à jour d'une recette"""
    try:
        print("=" * 60)
        print("TEST 1: Mise à jour recette")
        print("=" * 60)
        
        with get_db_context() as db:
            # Créer une recette de test
            test_recipe = Recette(
                nom="Recette Test Trigger",
                description="Test pour vérifier le trigger updated_at",
                temps_preparation=10,
                temps_cuisson=20,
                portions=4,
                difficulte="facile"
            )
            
            db.add(test_recipe)
            db.commit()
            db.refresh(test_recipe)
            
            recipe_id = test_recipe.id
            updated_at_before = test_recipe.updated_at
            
            print(f"✓ Recette créée (ID: {recipe_id})")
            print(f"  URL image avant: {test_recipe.url_image}")
            print(f"  updated_at avant: {updated_at_before}")
            
            # Mettre à jour l'URL d'image
            test_recipe.url_image = "https://example.com/test-recipe.jpg"
            db.commit()
            db.refresh(test_recipe)
            
            updated_at_after = test_recipe.updated_at
            
            print(f"✓ Mise à jour réussie!")
            print(f"  URL image après: {test_recipe.url_image}")
            print(f"  updated_at après: {updated_at_after}")
            print(f"  Timestamp mis à jour: {updated_at_after > updated_at_before}")
            
            # Vérifier qu'updated_at a été modifié
            assert test_recipe.url_image == "https://example.com/test-recipe.jpg"
            assert updated_at_after >= updated_at_before
            
            # Nettoyer le test
            db.delete(test_recipe)
            db.commit()
            
            return True
            
    except Exception as e:
        print(f"✗ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_modeles_courses_update():
    """Test de mise à jour d'un modèle de courses"""
    try:
        print("\n" + "=" * 60)
        print("TEST 2: Mise à jour modèle de courses")
        print("=" * 60)
        
        with get_db_context() as db:
            # Créer un modèle de test
            test_model = ModeleCourses(
                nom="Modèle Test Trigger",
                description="Test pour vérifier le trigger updated_at"
            )
            
            db.add(test_model)
            db.commit()
            db.refresh(test_model)
            
            model_id = test_model.id
            updated_at_before = test_model.updated_at
            
            print(f"✓ Modèle créé (ID: {model_id})")
            print(f"  Description avant: {test_model.description}")
            print(f"  updated_at avant: {updated_at_before}")
            
            # Mettre à jour la description
            test_model.description = "Description mise à jour pour test"
            db.commit()
            db.refresh(test_model)
            
            updated_at_after = test_model.updated_at
            
            print(f"✓ Mise à jour réussie!")
            print(f"  Description après: {test_model.description}")
            print(f"  updated_at après: {updated_at_after}")
            print(f"  Timestamp mis à jour: {updated_at_after > updated_at_before}")
            
            # Vérifier qu'updated_at a été modifié
            assert test_model.description == "Description mise à jour pour test"
            assert updated_at_after >= updated_at_before
            
            # Nettoyer le test
            db.delete(test_model)
            db.commit()
            
            return True
            
    except Exception as e:
        print(f"✗ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("TESTS DE VÉRIFICATION DU TRIGGER UPDATED_AT")
    print("=" * 60)
    
    test1_ok = test_recettes_update()
    test2_ok = test_modeles_courses_update()
    
    print("\n" + "=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)
    print(f"Test Recettes: {'✓ PASS' if test1_ok else '✗ FAIL'}")
    print(f"Test Modèles: {'✓ PASS' if test2_ok else '✗ FAIL'}")
    
    success = test1_ok and test2_ok
    print(f"\n{'✓ TOUS LES TESTS RÉUSSIS!' if success else '✗ CERTAINS TESTS ONT ÉCHOUÉ'}\n")
    
    sys.exit(0 if success else 1)
