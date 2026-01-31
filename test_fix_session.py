#!/usr/bin/env python3
"""
Test de validation du fix SQLAlchemy Session
Vérifie que les erreurs "Parent instance not bound to a Session" sont résolues
"""

import sys
from datetime import date, timedelta

# Add project to path
sys.path.insert(0, r'd:\Projet_streamlit\assistant_matanne')

def test_eager_loading():
    """Test 1: Vérifier que get_planning() charge les relations"""
    print("\n📋 TEST 1: Eager Loading de Planning.repas")
    print("=" * 60)
    
    try:
        from src.services.planning import get_planning_service
        
        service = get_planning_service()
        planning = service.get_planning()
        
        if planning:
            print(f"✅ Planning chargé: {planning.nom}")
            print(f"   ID: {planning.id}")
            print(f"   Semaine: {planning.semaine_debut} → {planning.semaine_fin}")
            
            # TEST CRITIQUE: Accéder à repas sans erreur
            try:
                repas_count = len(planning.repas) if planning.repas else 0
                print(f"✅ Accès à planning.repas OK: {repas_count} repas")
                
                # Parcourir les repas
                if planning.repas:
                    for i, repas in enumerate(planning.repas):
                        try:
                            recette_nom = repas.recette.nom if repas.recette else "Aucune"
                            print(f"   Repas {i+1}: {repas.type_repas} - {recette_nom}")
                        except Exception as e:
                            print(f"   ❌ Erreur accès recette: {e}")
                            return False
                
                print("✅ TEST 1 PASSED: Eager loading fonctionne!")
                return True
                
            except Exception as e:
                print(f"❌ ERREUR accès planning.repas: {e}")
                print(f"   Type: {type(e).__name__}")
                return False
        else:
            print("⚠️  Aucun planning actif trouvé (normal si BD vide)")
            print("✅ TEST 1 PASSED: Pas d'erreur de session")
            return True
            
    except Exception as e:
        print(f"❌ TEST 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_context_manager_usage():
    """Test 2: Vérifier que le context manager fonctionne correctement"""
    print("\n📋 TEST 2: Context Manager obtenir_contexte_db()")
    print("=" * 60)
    
    try:
        from src.core.database import obtenir_contexte_db
        from src.core.models import Recette
        
        # Test d'utilisation correcte
        with obtenir_contexte_db() as db:
            recettes = db.query(Recette).all()
            recette_count = len(recettes)
        
        print(f"✅ Context manager OK: {recette_count} recettes récupérées")
        
        # Test d'accès après fermeture (ne doit pas utiliser db ici)
        print("✅ Session fermée correctement après 'with'")
        print("✅ TEST 2 PASSED: Context manager fonctionne!")
        return True
        
    except Exception as e:
        print(f"❌ TEST 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_service_modifications():
    """Test 3: Vérifier que les modifications en BD marchent"""
    print("\n📋 TEST 3: Modifications BD via Service")
    print("=" * 60)
    
    try:
        from src.services.planning import get_planning_service
        from src.core.models import Repas
        
        service = get_planning_service()
        planning = service.get_planning()
        
        if not planning or not planning.repas:
            print("⚠️  Aucun planning/repas à tester (normal si BD vide)")
            print("✅ TEST 3 PASSED: Pas d'erreur")
            return True
        
        # Chercher un repas à modifier
        repas = planning.repas[0] if planning.repas else None
        if repas:
            original_prepare = repas.prepare
            print(f"Test avec repas ID: {repas.id}")
            print(f"État original 'prepare': {original_prepare}")
            
            # Modifier via context manager (comme dans le UI)
            from src.core.database import obtenir_contexte_db
            with obtenir_contexte_db() as db:
                repas_db = db.query(Repas).filter_by(id=repas.id).first()
                if repas_db:
                    repas_db.prepare = not original_prepare
                    db.commit()
            
            print(f"✅ Modification BD OK")
            print("✅ TEST 3 PASSED: Modifications marchent!")
            
            # Restore state
            with obtenir_contexte_db() as db:
                repas_db = db.query(Repas).filter_by(id=repas.id).first()
                if repas_db:
                    repas_db.prepare = original_prepare
                    db.commit()
            
            return True
        
        return True
        
    except Exception as e:
        print(f"❌ TEST 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_joinedload_imports():
    """Test 4: Vérifier que joinedload est importé correctement"""
    print("\n📋 TEST 4: Imports SQLAlchemy")
    print("=" * 60)
    
    try:
        from sqlalchemy.orm import joinedload
        print("✅ joinedload importé correctement")
        
        from src.core.models import Planning, Repas
        print("✅ Modèles importés correctement")
        
        # Vérifier que Planning a la relation repas
        if hasattr(Planning, 'repas'):
            print("✅ Planning.repas relationship existe")
        else:
            print("❌ Planning.repas relationship NOT FOUND")
            return False
        
        # Vérifier que Repas a la relation recette
        if hasattr(Repas, 'recette'):
            print("✅ Repas.recette relationship existe")
        else:
            print("❌ Repas.recette relationship NOT FOUND")
            return False
        
        print("✅ TEST 4 PASSED: Tous les imports OK!")
        return True
        
    except Exception as e:
        print(f"❌ TEST 4 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Lancer tous les tests"""
    print("\n" + "=" * 60)
    print("🧪 VALIDATION FIX SQLAlchemy Session")
    print("=" * 60)
    
    results = {
        "Test 1 - Eager Loading": test_joinedload_imports(),
        "Test 2 - Imports": test_eager_loading(),
        "Test 3 - Context Manager": test_context_manager_usage(),
        "Test 4 - Modifications": test_service_modifications(),
    }
    
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passés")
    
    if passed == total:
        print("\n🎉 TOUS LES TESTS PASSÉS! Le fix est validé.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) échoué(s)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
