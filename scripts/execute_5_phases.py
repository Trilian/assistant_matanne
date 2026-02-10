#!/usr/bin/env python3
"""
Script d'exécution automatique des 5 phases de réorganisation.

Phase 1: Nettoyer les tests redondants (*_deep.py, *_extended.py, *_coverage*.py)
Phase 2: Diviser les fichiers > 500 lignes
Phase 3: Créer les tests 1:1 manquants
Phase 4: Renommer les fichiers en français
Phase 5: Augmenter la couverture à 80%
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# Chemins
PROJET_ROOT = Path(__file__).parent.parent
TESTS_DIR = PROJET_ROOT / "tests"
SRC_DIR = PROJET_ROOT / "src"
BACKUPS_DIR = PROJET_ROOT / "backups"
TESTS_CONSOLIDATE_DIR = BACKUPS_DIR / "tests_to_consolidate"


def phase1_nettoyer_tests_redondants():
    """Phase 1: Déplacer les tests redondants vers backups/tests_to_consolidate/"""
    print("\n" + "=" * 60)
    print("PHASE 1: Nettoyage des tests redondants")
    print("=" * 60)
    
    # Créer le dossier de backup s'il n'existe pas
    TESTS_CONSOLIDATE_DIR.mkdir(parents=True, exist_ok=True)
    
    patterns = ["*_deep.py", "*_extended.py", "*_coverage*.py"]
    moved_files = []
    
    for pattern in patterns:
        for test_file in TESTS_DIR.rglob(pattern):
            # Ne pas toucher aux fichiers dans tests/core/ (déjà traités)
            if "tests/core" in str(test_file) or "tests\\core" in str(test_file):
                continue
            
            # Créer le sous-dossier de destination
            rel_path = test_file.relative_to(TESTS_DIR)
            dest_dir = TESTS_CONSOLIDATE_DIR / rel_path.parent
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            dest_file = dest_dir / test_file.name
            
            # Éviter les conflits de noms
            if dest_file.exists():
                base = dest_file.stem
                ext = dest_file.suffix
                counter = 1
                while dest_file.exists():
                    dest_file = dest_dir / f"{base}_{counter}{ext}"
                    counter += 1
            
            shutil.move(str(test_file), str(dest_file))
            moved_files.append((str(test_file), str(dest_file)))
            print(f"  ✓ Déplacé: {rel_path}")
    
    print(f"\n  Total: {len(moved_files)} fichiers déplacés")
    return moved_files


def phase2_identifier_fichiers_volumineux():
    """Phase 2: Identifier les fichiers > 500 lignes à diviser"""
    print("\n" + "=" * 60)
    print("PHASE 2: Identification des fichiers volumineux (> 500 lignes)")
    print("=" * 60)
    
    large_files = []
    
    for py_file in SRC_DIR.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        try:
            lines = len(py_file.read_text(encoding="utf-8").splitlines())
            if lines > 500:
                large_files.append((py_file, lines))
        except Exception as e:
            print(f"  ⚠ Erreur lecture {py_file}: {e}")
    
    # Trier par nombre de lignes décroissant
    large_files.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n  {len(large_files)} fichiers > 500 lignes trouvés:")
    for path, lines in large_files[:15]:
        rel = path.relative_to(SRC_DIR)
        print(f"    - {rel}: {lines} lignes")
    
    return large_files


def phase3_identifier_tests_manquants():
    """Phase 3: Identifier les fichiers source sans test correspondant"""
    print("\n" + "=" * 60)
    print("PHASE 3: Identification des tests 1:1 manquants")
    print("=" * 60)
    
    missing_tests = []
    
    for py_file in SRC_DIR.rglob("*.py"):
        if "__pycache__" in str(py_file) or py_file.name.startswith("_"):
            continue
        if py_file.name == "__init__.py":
            continue
        
        # Calculer le chemin du test attendu
        rel_path = py_file.relative_to(SRC_DIR)
        test_name = f"test_{py_file.stem}.py"
        
        # Chercher le test dans tests/ avec la même structure
        expected_test_paths = [
            TESTS_DIR / rel_path.parent / test_name,
            TESTS_DIR / rel_path.parent / py_file.stem / test_name,
        ]
        
        test_exists = any(p.exists() for p in expected_test_paths)
        
        if not test_exists:
            # Vérifier aussi avec grep si un test mentionne ce module
            missing_tests.append(py_file)
    
    print(f"\n  {len(missing_tests)} fichiers source sans test 1:1:")
    for path in missing_tests[:20]:
        rel = path.relative_to(SRC_DIR)
        print(f"    - {rel}")
    if len(missing_tests) > 20:
        print(f"    ... et {len(missing_tests) - 20} autres")
    
    return missing_tests


def phase4_identifier_fichiers_anglais():
    """Phase 4: Identifier les fichiers avec noms anglais à renommer"""
    print("\n" + "=" * 60)
    print("PHASE 4: Identification des fichiers anglais à renommer")
    print("=" * 60)
    
    # Mapping de renommage suggéré
    rename_suggestions = {
        "config.py": "configuration.py",
        "database.py": "base_donnees.py",
        "cache.py": "cache.py",  # Garder (terme universel)
        "helpers.py": "utilitaires.py",
        "validators.py": "validateurs.py",
        "formatters.py": "formateurs.py",
        "service.py": "service.py",  # Garder (terme accepté)
        "auth.py": "authentification.py",
        "backup.py": "sauvegarde.py",
        "weather.py": "meteo.py",
        "predictions.py": "predictions.py",  # Garder (terme similaire)
        "budget.py": "budget.py",  # Garder
        "barcode.py": "code_barres.py",
        "notifications.py": "notifications.py",  # Garder
        "performance.py": "performances.py",
        "media.py": "medias.py",
        "image.py": "image.py",  # Garder
        "lazy_loader.py": "chargeur_paresseux.py",
        "rate_limiting.py": "limitation_debit.py",
    }
    
    files_to_rename = []
    
    for py_file in SRC_DIR.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        
        if py_file.name in rename_suggestions:
            new_name = rename_suggestions[py_file.name]
            if new_name != py_file.name:
                files_to_rename.append((py_file, new_name))
    
    print(f"\n  {len(files_to_rename)} fichiers à renommer:")
    for path, new_name in files_to_rename:
        rel = path.relative_to(SRC_DIR)
        print(f"    - {rel} → {new_name}")
    
    return files_to_rename


def phase5_analyser_couverture():
    """Phase 5: Analyser les fichiers avec faible couverture"""
    print("\n" + "=" * 60)
    print("PHASE 5: Analyse de la couverture (fichiers prioritaires)")
    print("=" * 60)
    
    # Les fichiers critiques identifiés comme prioritaires
    priority_files = [
        ("src/core/decorators.py", "21%", "80%"),
        ("src/core/cache.py", "28%", "80%"),
        ("src/core/cache_multi.py", "35%", "80%"),
        ("src/services/recettes.py", "25%", "80%"),
        ("src/services/inventaire.py", "30%", "80%"),
        ("src/core/lazy_loader.py", "40%", "80%"),
        ("src/core/multi_tenant.py", "45%", "80%"),
    ]
    
    print("\n  Fichiers prioritaires pour atteindre 80% de couverture:")
    for path, current, target in priority_files:
        print(f"    - {path}: {current} → {target}")
    
    return priority_files


def main():
    """Exécute les 5 phases de réorganisation."""
    print("\n" + "=" * 60)
    print("EXÉCUTION DES 5 PHASES DE RÉORGANISATION")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Phase 1: Nettoyer les tests redondants
    moved_files = phase1_nettoyer_tests_redondants()
    
    # Phase 2: Identifier les fichiers volumineux
    large_files = phase2_identifier_fichiers_volumineux()
    
    # Phase 3: Identifier les tests manquants
    missing_tests = phase3_identifier_tests_manquants()
    
    # Phase 4: Identifier les fichiers à renommer
    files_to_rename = phase4_identifier_fichiers_anglais()
    
    # Phase 5: Analyser la couverture
    priority_files = phase5_analyser_couverture()
    
    # Résumé
    print("\n" + "=" * 60)
    print("RÉSUMÉ DE L'EXÉCUTION")
    print("=" * 60)
    print(f"  Phase 1: {len(moved_files)} tests redondants déplacés")
    print(f"  Phase 2: {len(large_files)} fichiers > 500 lignes identifiés")
    print(f"  Phase 3: {len(missing_tests)} tests 1:1 manquants identifiés")
    print(f"  Phase 4: {len(files_to_rename)} fichiers à renommer identifiés")
    print(f"  Phase 5: {len(priority_files)} fichiers prioritaires pour couverture")
    
    return {
        "phase1": moved_files,
        "phase2": large_files,
        "phase3": missing_tests,
        "phase4": files_to_rename,
        "phase5": priority_files,
    }


if __name__ == "__main__":
    main()
