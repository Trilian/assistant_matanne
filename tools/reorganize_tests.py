#!/usr/bin/env python3
"""
Script pour réorganiser les tests et créer une structure 1:1 avec les fichiers sources.

Ce script:
1. Analyse la structure des tests actuels
2. Identifie les fichiers sources sans tests
3. Propose une réorganisation pour avoir un mapping 1:1
4. Génère des fichiers de tests stub pour les fichiers manquants
"""

import json
import re
import shutil
from pathlib import Path
from typing import Dict, List, Set, Tuple


SRC_DIR = Path("src")
TESTS_DIR = Path("tests")


def get_all_source_files() -> List[Path]:
    """Récupère tous les fichiers source Python."""
    return [
        f for f in SRC_DIR.rglob("*.py")
        if f.name != "__init__.py" and not f.name.startswith("_")
    ]


def get_all_test_files() -> List[Path]:
    """Récupère tous les fichiers de test Python."""
    return [
        f for f in TESTS_DIR.rglob("*.py")
        if f.name.startswith("test_") or f.name.endswith("_test.py")
    ]


def find_test_for_source(src_file: Path) -> List[Path]:
    """Trouve les fichiers de test correspondant à un fichier source."""
    rel_path = src_file.relative_to(SRC_DIR)
    module_name = rel_path.stem
    
    # Patterns de nommage possibles
    patterns = [
        f"test_{module_name}.py",
        f"{module_name}_test.py",
        f"test_{module_name}_*.py",
    ]
    
    test_files = []
    
    # Chercher dans la structure miroir
    test_dir = TESTS_DIR / rel_path.parent
    if test_dir.exists():
        for pattern in patterns:
            test_files.extend(test_dir.glob(pattern))
    
    # Chercher aussi dans d'autres emplacements
    for subdir in TESTS_DIR.rglob("*"):
        if subdir.is_dir():
            for pattern in patterns:
                test_files.extend(subdir.glob(pattern))
    
    return list(set(test_files))


def count_test_functions(test_file: Path) -> int:
    """Compte le nombre de fonctions de test dans un fichier."""
    try:
        content = test_file.read_text(encoding="utf-8")
        return len(re.findall(r'^\s*def test_', content, re.MULTILINE))
    except Exception:
        return 0


def analyze_test_coverage() -> Dict:
    """Analyse la couverture des tests."""
    source_files = get_all_source_files()
    test_files = get_all_test_files()
    
    results = {
        "total_source_files": len(source_files),
        "total_test_files": len(test_files),
        "files_with_tests": 0,
        "files_without_tests": 0,
        "total_test_functions": 0,
        "mapping": [],
        "files_without_tests_list": [],
        "duplicate_test_files": []
    }
    
    for src_file in source_files:
        rel_path = src_file.relative_to(SRC_DIR)
        tests = find_test_for_source(src_file)
        
        test_count = sum(count_test_functions(t) for t in tests)
        results["total_test_functions"] += test_count
        
        mapping_entry = {
            "source": str(rel_path),
            "test_files": [str(t.relative_to(TESTS_DIR)) for t in tests],
            "test_count": test_count,
            "has_tests": len(tests) > 0
        }
        
        results["mapping"].append(mapping_entry)
        
        if len(tests) > 0:
            results["files_with_tests"] += 1
            if len(tests) > 1:
                results["duplicate_test_files"].append(mapping_entry)
        else:
            results["files_without_tests"] += 1
            results["files_without_tests_list"].append(str(rel_path))
    
    return results


def generate_reorganization_plan(analysis: Dict) -> Dict:
    """Génère un plan de réorganisation."""
    plan = {
        "create_missing_tests": [],
        "consolidate_tests": [],
        "move_tests": []
    }
    
    for mapping in analysis["mapping"]:
        src_path = Path("src") / mapping["source"]
        rel_src = Path(mapping["source"])
        
        # Fichiers sans tests: créer un test stub
        if not mapping["has_tests"]:
            expected_test_path = TESTS_DIR / rel_src.parent / f"test_{rel_src.stem}.py"
            plan["create_missing_tests"].append({
                "source": mapping["source"],
                "test_file": str(expected_test_path.relative_to(TESTS_DIR))
            })
        
        # Fichiers avec plusieurs fichiers de test: consolider
        elif len(mapping["test_files"]) > 1:
            primary_test = mapping["test_files"][0]
            plan["consolidate_tests"].append({
                "source": mapping["source"],
                "primary_test": primary_test,
                "duplicate_tests": mapping["test_files"][1:]
            })
    
    return plan


def create_test_stub(src_file: str, test_file: str) -> str:
    """Crée un fichier de test stub."""
    module_path = Path(src_file).with_suffix("").as_posix().replace("/", ".")
    module_name = Path(src_file).stem
    
    stub = f'''"""
Tests pour {src_file}

Ce fichier a été généré automatiquement.
TODO: Ajouter des tests pour atteindre 80% de couverture.
"""

import pytest
from src.{module_path} import *


class Test{module_name.title().replace("_", "")}:
    """Tests pour le module {module_name}."""
    
    def test_module_loads(self):
        """Vérifie que le module se charge correctement."""
        # TODO: Ajouter des tests réels
        assert True
    
    # TODO: Ajouter plus de tests ici
    # Objectif: 80% de couverture du code
'''
    
    return stub


def main():
    """Point d'entrée principal."""
    print("=" * 80)
    print("🔄 ANALYSE ET RÉORGANISATION DES TESTS")
    print("=" * 80)
    print()
    
    # Analyse
    print("📊 Analyse de la structure actuelle...")
    analysis = analyze_test_coverage()
    
    print(f"\n✅ Analyse terminée:")
    print(f"   - Fichiers source: {analysis['total_source_files']}")
    print(f"   - Fichiers de test: {analysis['total_test_files']}")
    print(f"   - Fichiers avec tests: {analysis['files_with_tests']}")
    print(f"   - Fichiers sans tests: {analysis['files_without_tests']}")
    print(f"   - Fonctions de test totales: {analysis['total_test_functions']}")
    
    if analysis['duplicate_test_files']:
        print(f"\n⚠️ {len(analysis['duplicate_test_files'])} fichiers ont plusieurs fichiers de test")
    
    # Générer le plan
    print("\n📋 Génération du plan de réorganisation...")
    plan = generate_reorganization_plan(analysis)
    
    print(f"\n✅ Plan généré:")
    print(f"   - Tests à créer: {len(plan['create_missing_tests'])}")
    print(f"   - Tests à consolider: {len(plan['consolidate_tests'])}")
    
    # Sauvegarder l'analyse
    analysis_file = Path("test_analysis.json")
    with open(analysis_file, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Analyse sauvegardée: {analysis_file}")
    
    # Sauvegarder le plan
    plan_file = Path("test_reorganization_plan.json")
    with open(plan_file, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
    print(f"✅ Plan sauvegardé: {plan_file}")
    
    # Générer un rapport markdown
    report_lines = [
        "# Plan de Réorganisation des Tests",
        "",
        "## Résumé",
        "",
        f"- **Fichiers source**: {analysis['total_source_files']}",
        f"- **Fichiers de test**: {analysis['total_test_files']}",
        f"- **Fichiers avec tests**: {analysis['files_with_tests']}",
        f"- **Fichiers sans tests**: {analysis['files_without_tests']}",
        f"- **Fonctions de test totales**: {analysis['total_test_functions']}",
        "",
        "## Actions Recommandées",
        "",
        f"### 1. Créer {len(plan['create_missing_tests'])} fichiers de test manquants",
        ""
    ]
    
    if plan['create_missing_tests']:
        report_lines.append("Fichiers sans tests:")
        report_lines.append("")
        for item in plan['create_missing_tests'][:20]:  # Limiter l'affichage
            report_lines.append(f"- `{item['source']}` → `{item['test_file']}`")
        if len(plan['create_missing_tests']) > 20:
            report_lines.append(f"- ... et {len(plan['create_missing_tests']) - 20} autres")
        report_lines.append("")
    
    if plan['consolidate_tests']:
        report_lines.extend([
            f"### 2. Consolider {len(plan['consolidate_tests'])} fichiers avec tests dupliqués",
            ""
        ])
        for item in plan['consolidate_tests'][:10]:
            report_lines.append(f"- `{item['source']}`:")
            report_lines.append(f"  - Garder: `{item['primary_test']}`")
            report_lines.append(f"  - Fusionner: {', '.join([f'`{t}`' for t in item['duplicate_tests']])}")
        if len(plan['consolidate_tests']) > 10:
            report_lines.append(f"- ... et {len(plan['consolidate_tests']) - 10} autres")
        report_lines.append("")
    
    report = "\n".join(report_lines)
    report_file = Path("test_reorganization_report.md")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"✅ Rapport généré: {report_file}")
    
    print(f"\n{'='*80}")
    print("✅ Analyse et planification terminées!")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
