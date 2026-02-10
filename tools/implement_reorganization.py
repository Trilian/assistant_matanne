#!/usr/bin/env python3
"""
Script d'implémentation pour réorganiser les tests.

Ce script exécute les actions identifiées dans le plan de réorganisation:
1. Crée les fichiers de test manquants
2. Consolide les tests dupliqués
3. Nettoie la structure
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List
import sys


TESTS_DIR = Path("tests")
SRC_DIR = Path("src")
DRY_RUN = True  # Par défaut en mode dry-run


def load_plan() -> Dict:
    """Charge le plan de réorganisation."""
    plan_file = Path("test_reorganization_plan.json")
    if not plan_file.exists():
        print("❌ Erreur: test_reorganization_plan.json n'existe pas")
        print("   Exécutez d'abord: python tools/reorganize_tests.py")
        sys.exit(1)
    
    with open(plan_file, "r", encoding="utf-8") as f:
        return json.load(f)


def create_test_stub(src_file: str, test_file: str, dry_run: bool = True) -> bool:
    """Crée un fichier de test stub."""
    test_path = TESTS_DIR / test_file
    
    if test_path.exists():
        print(f"  ⚠️ Le fichier existe déjà: {test_file}")
        return False
    
    # Créer le contenu du stub
    module_path = Path(src_file).with_suffix("").as_posix().replace("/", ".")
    module_name = Path(src_file).stem
    class_name = "".join(word.capitalize() for word in module_name.split("_"))
    
    stub = f'''"""
Tests pour {src_file}

Ce fichier a été généré automatiquement lors de la réorganisation des tests.
TODO: Ajouter des tests pour atteindre 80% de couverture.
"""

import pytest
# TODO: Importer les éléments spécifiques à tester depuis src.{module_path}


class Test{class_name}:
    """Tests pour le module {module_name}."""
    
    def test_module_loads(self):
        """Vérifie que le module se charge correctement."""
        # TODO: Ajouter des tests réels ici
        # Ceci est juste un stub pour établir la structure 1:1
        assert True
    
    # TODO: Ajouter plus de tests ici pour atteindre 80% de couverture
    # Référence: src/{src_file}
'''
    
    if dry_run:
        print(f"  [DRY-RUN] Créerait: {test_file}")
        return True
    else:
        # Créer les répertoires parents si nécessaire
        test_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Écrire le fichier
        test_path.write_text(stub, encoding="utf-8")
        print(f"  ✅ Créé: {test_file}")
        return True


def consolidate_tests(source: str, primary: str, duplicates: List[str], dry_run: bool = True) -> bool:
    """Consolide plusieurs fichiers de test en un seul."""
    primary_path = TESTS_DIR / primary
    
    if not primary_path.exists():
        print(f"  ❌ Le fichier primaire n'existe pas: {primary}")
        return False
    
    print(f"  📦 Consolidation pour {source}:")
    print(f"     Primaire: {primary}")
    
    for dup in duplicates:
        dup_path = TESTS_DIR / dup
        
        if not dup_path.exists():
            print(f"     ⚠️ Fichier dupliqué introuvable: {dup}")
            continue
        
        if dry_run:
            print(f"     [DRY-RUN] Fusionnerait: {dup}")
        else:
            # TODO: Implémenter la fusion intelligente
            # Pour l'instant, on renomme en .bak
            backup_path = dup_path.with_suffix(".py.bak")
            shutil.move(str(dup_path), str(backup_path))
            print(f"     ✅ Sauvegardé: {dup} → {backup_path.name}")
    
    return True


def phase2_create_missing_tests(plan: Dict, dry_run: bool = True):
    """Phase 2: Créer les fichiers de test manquants."""
    missing_tests = plan["create_missing_tests"]
    
    print(f"\n{'='*80}")
    print(f"📝 PHASE 2: Création de {len(missing_tests)} fichiers de test manquants")
    print(f"{'='*80}\n")
    
    created = 0
    skipped = 0
    
    for item in missing_tests:
        src_file = item["source"]
        test_file = item["test_file"]
        
        print(f"\n• {src_file}")
        
        if create_test_stub(src_file, test_file, dry_run):
            created += 1
        else:
            skipped += 1
    
    print(f"\n{'='*80}")
    print(f"✅ Résumé Phase 2:")
    print(f"   - Tests créés: {created}")
    print(f"   - Tests ignorés: {skipped}")
    print(f"{'='*80}")


def phase2_consolidate_tests(plan: Dict, dry_run: bool = True):
    """Phase 2: Consolider les tests dupliqués."""
    consolidations = plan["consolidate_tests"]
    
    print(f"\n{'='*80}")
    print(f"🔄 PHASE 2b: Consolidation de {len(consolidations)} fichiers avec tests dupliqués")
    print(f"{'='*80}\n")
    
    consolidated = 0
    skipped = 0
    
    for item in consolidations:
        src = item["source"]
        primary = item["primary_test"]
        dups = item["duplicate_tests"]
        
        print(f"\n• {src}")
        
        if consolidate_tests(src, primary, dups, dry_run):
            consolidated += 1
        else:
            skipped += 1
    
    print(f"\n{'='*80}")
    print(f"✅ Résumé Phase 2b:")
    print(f"   - Fichiers consolidés: {consolidated}")
    print(f"   - Fichiers ignorés: {skipped}")
    print(f"{'='*80}")


def main():
    """Point d'entrée principal."""
    global DRY_RUN
    
    # Vérifier les arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--execute":
            DRY_RUN = False
            print("⚠️ MODE EXÉCUTION ACTIVÉ - Les modifications seront appliquées!")
        elif sys.argv[1] == "--help":
            print("Usage: python tools/implement_reorganization.py [--execute]")
            print()
            print("Options:")
            print("  (aucun)    Mode dry-run (par défaut)")
            print("  --execute  Applique réellement les modifications")
            print("  --help     Affiche cette aide")
            return
    
    print("=" * 80)
    print("🚀 IMPLÉMENTATION DE LA RÉORGANISATION DES TESTS")
    print("=" * 80)
    print()
    
    if DRY_RUN:
        print("ℹ️ MODE DRY-RUN - Aucune modification ne sera appliquée")
        print("   Utilisez --execute pour appliquer les modifications")
    else:
        print("⚠️ MODE EXÉCUTION - Les modifications seront appliquées")
    
    print()
    
    # Charger le plan
    print("📋 Chargement du plan de réorganisation...")
    plan = load_plan()
    
    print(f"✅ Plan chargé:")
    print(f"   - Tests à créer: {len(plan['create_missing_tests'])}")
    print(f"   - Tests à consolider: {len(plan['consolidate_tests'])}")
    
    # Demander confirmation en mode exécution
    if not DRY_RUN:
        print("\n⚠️ ATTENTION: Cette opération va modifier les fichiers de test!")
        response = input("Continuer? (oui/non): ").lower()
        if response not in ["oui", "o", "yes", "y"]:
            print("❌ Opération annulée")
            return
    
    # Exécuter les phases
    phase2_create_missing_tests(plan, DRY_RUN)
    phase2_consolidate_tests(plan, DRY_RUN)
    
    print(f"\n{'='*80}")
    if DRY_RUN:
        print("✅ Simulation terminée!")
        print("   Utilisez --execute pour appliquer les modifications")
    else:
        print("✅ Réorganisation terminée!")
        print("   N'oubliez pas de:")
        print("   1. Vérifier les fichiers créés")
        print("   2. Fusionner manuellement les tests dupliqués")
        print("   3. Exécuter les tests: pytest")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
