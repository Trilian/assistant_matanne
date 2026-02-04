#!/usr/bin/env python3
"""
Analyse de couverture - Version simplifiée
"""
import os
import sys
from pathlib import Path
from collections import defaultdict

# Ajouter le workspace au chemin Python
workspace = Path("d:\\Projet_streamlit\\assistant_matanne")
sys.path.insert(0, str(workspace))

def get_python_files(directory: Path) -> list:
    """Récupère tous les fichiers Python d'un répertoire."""
    files = []
    for root, dirs, filenames in os.walk(directory):
        # Ignorer __pycache__
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.pytest_cache']]
        for filename in filenames:
            if filename.endswith('.py') and not filename.startswith('__'):
                rel_path = os.path.relpath(os.path.join(root, filename), directory)
                files.append(rel_path)
    return sorted(files)

def analyze():
    """Analyse la structure des tests."""
    src_dir = workspace / "src"
    tests_dir = workspace / "tests"
    
    print("\n" + "="*100)
    print("ANALYSE DE LA STRUCTURE DES TESTS")
    print("="*100)
    
    # Fichiers src/
    src_files = get_python_files(src_dir)
    print(f"\n✓ Fichiers src/: {len(src_files)}")
    
    # Fichiers tests/
    test_files = get_python_files(tests_dir)
    print(f"✓ Fichiers tests/: {len(test_files)}")
    
    # Analyse par dossier
    src_by_folder = defaultdict(list)
    test_by_folder = defaultdict(list)
    
    for f in src_files:
        parts = f.split('\\')
        folder = parts[0] if len(parts) > 1 else 'root'
        src_by_folder[folder].append(f)
    
    for f in test_files:
        parts = f.split('\\')
        folder = parts[0] if len(parts) > 1 else 'root'
        test_by_folder[folder].append(f)
    
    print("\n1. STRUCTURE PAR DOSSIER")
    print("-" * 100)
    
    all_folders = set(src_by_folder.keys()) | set(test_by_folder.keys())
    
    print(f"{'Dossier':<20} {'Fichiers src/':<15} {'Tests/':<15} {'Couverture':<15} {'Statut':<20}")
    print("-" * 100)
    
    for folder in sorted(all_folders):
        src_count = len(src_by_folder.get(folder, []))
        test_count = len(test_by_folder.get(folder, []))
        
        if src_count > 0:
            coverage = (test_count / src_count) * 100
            status = "✓ Complet" if coverage >= 80 else f"⚠️  Incomplet ({coverage:.0f}%)"
        else:
            status = "Tests supplémentaires"
            coverage = 0
        
        print(f"{folder:<20} {src_count:<15} {test_count:<15} {coverage:<14.1f}% {status:<20}")
    
    # Fichiers manquants
    print("\n2. FICHIERS SANS TESTS CORRESPONDANTS")
    print("-" * 100)
    
    missing = []
    for folder, files in src_by_folder.items():
        for file in files:
            if file.endswith('__init__.py'):
                continue
            
            filename = os.path.basename(file).replace('.py', '')
            test_name = f'test_{filename}.py'
            
            # Vérifier si un test existe
            test_found = False
            for test_file in test_by_folder.get(folder, []):
                if test_file.endswith(test_name):
                    test_found = True
                    break
            
            if not test_found:
                missing.append(f"{folder}/{file}")
    
    if missing:
        print(f"⚠️  Total: {len(missing)} fichiers manquants\n")
        for m in sorted(missing)[:20]:
            print(f"  - {m}")
        if len(missing) > 20:
            print(f"  ... et {len(missing) - 20} autres")
    else:
        print("✓ Tous les fichiers ont des tests correspondants")
    
    # Dossiers sans tests
    print("\n3. DOSSIERS SRC SANS CORRESPONDANT TESTS")
    print("-" * 100)
    
    missing_folders = set(src_by_folder.keys()) - set(test_by_folder.keys())
    if missing_folders:
        print(f"⚠️  Dossiers sans tests:\n")
        for folder in sorted(missing_folders):
            count = len(src_by_folder[folder])
            print(f"  - {folder}/ ({count} fichiers)")
    else:
        print("✓ Tous les dossiers src ont des tests correspondants")
    
    # Résumé
    print("\n4. RÉSUMÉ")
    print("-" * 100)
    print(f"Fichiers src/ couvert: {len(src_files)} fichiers")
    print(f"Fichiers tests/ existants: {len(test_files)} fichiers")
    print(f"Couverture globale des fichiers: {(len(test_files)/(len(src_files)+1))*100:.1f}%")
    print(f"Fichiers manquant des tests: {len(missing)}")
    
    # Recommandations
    print("\n5. RECOMMANDATIONS PRIORITAIRES")
    print("-" * 100)
    
    priorities = []
    
    if missing_folders:
        for folder in sorted(missing_folders):
            priorities.append(f"  1. Créer le dossier tests/{folder}/ pour couvrir {len(src_by_folder[folder])} fichiers")
    
    if missing:
        for folder in sorted(set(f.split('/')[0] for f in missing)):
            count = len([m for m in missing if m.startswith(folder)])
            priorities.append(f"  {len(priorities)+1}. Créer {count} tests dans tests/{folder}/ pour les fichiers src/{folder}/")
    
    for p in priorities[:10]:
        print(p)
    
    print("\n" + "="*100)

if __name__ == "__main__":
    analyze()
