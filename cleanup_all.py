#!/usr/bin/env python3
"""
Script tout-en-un: Nettoyage complet + Vérification.
À exécuter avant les tests suivants.
"""

import os
import shutil
from pathlib import Path
import subprocess
import json

def cleanup_integration_dir():
    """Nettoyer integration/ et renommer les fichiers."""
    integration_dir = Path("tests/integration")
    
    print("=" * 70)
    print("1. NETTOYAGE TESTS/INTEGRATION/")
    print("=" * 70)
    print()
    
    # Fichiers à supprimer
    to_delete = [
        "test_phase16.py",
        "test_phase16_fixed.py", 
        "test_phase16_v2.py",
        "test_15e_extended_coverage.py",
    ]
    
    # Fichiers à renommer
    to_rename = {
        "test_phase16_extended.py": "test_integration_crud_models.py",
        "test_business_logic.py": "test_integration_business_logic.py",
        "test_domains_integration.py": "test_integration_domains_workflows.py",
    }
    
    # Supprimer
    for file in to_delete:
        filepath = integration_dir / file
        if filepath.exists():
            print(f"   ❌ Suppression: {file}")
            filepath.unlink()
    
    print()
    
    # Renommer
    for old_name, new_name in to_rename.items():
        old_path = integration_dir / old_name
        new_path = integration_dir / new_name
        
        if old_path.exists():
            print(f"   ✅ Renommage: {old_name}")
            print(f"              → {new_name}")
            old_path.rename(new_path)
    
    print()
    print("   Résultat final:")
    for f in sorted(integration_dir.glob("test_*.py")):
        size = f.stat().st_size
        test_count = f.read_text().count("def test_")
        print(f"      ✓ {f.name:<40} ({test_count:>2} tests)")
    
    print()

def verify_collection():
    """Vérifier que les tests se collectent sans erreur."""
    print("=" * 70)
    print("2. VÉRIFICATION COLLECTION DES TESTS")
    print("=" * 70)
    print()
    
    try:
        result = subprocess.run(
            ['python', '-m', 'pytest', 'tests/', '--co', '-q'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Vérifier qu'il n'y a pas d'erreurs
        if 'error' in result.stdout.lower() or 'error' in result.stderr.lower():
            print("   ❌ ERREURS DÉTECTÉES:")
            print(result.stdout)
            print(result.stderr)
            return False
        else:
            # Parser le dernier ligne pour le nombre de tests
            lines = result.stdout.strip().split('\n')
            print(f"   ✅ Collection réussie!")
            for line in lines[-3:]:
                if line.strip():
                    print(f"      {line}")
            return True
    except subprocess.TimeoutExpired:
        print("   ⚠️  Collection timeout - tests trop nombreux?")
        return False
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def main():
    print()
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "SCRIPT DE NETTOYAGE COMPLET" + " " * 25 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    try:
        # 1. Nettoyage
        cleanup_integration_dir()
        
        # 2. Vérification
        success = verify_collection()
        
        print()
        print("=" * 70)
        if success:
            print("✅ TOUS LES NETTOYAGES COMPLÉTÉS AVEC SUCCÈS!")
            print()
            print("Prochaines étapes:")
            print("  1. Exécuter: pytest tests/ --cov=src --cov-report=json")
            print("  2. Analyser: python analyze_coverage_by_module.py")
            print("  3. Créer Phase 17+ tests")
        else:
            print("⚠️  VÉRIFICATION ÉCHOUÉE - Vérifiez les erreurs ci-dessus")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ ERREUR FATALE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
