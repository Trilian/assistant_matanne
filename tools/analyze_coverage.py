#!/usr/bin/env python3
"""
Script d'analyse de couverture de tests pour assistant_matanne.

Ce script:
1. Analyse tous les dossiers et fichiers dans src/
2. Calcule la couverture pour chaque dossier et fichier
3. Identifie les tests correspondants dans tests/
4. Génère un rapport détaillé avec recommandations
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import re

# Configuration
SRC_DIR = Path("src")
TESTS_DIR = Path("tests")
COVERAGE_THRESHOLD = 80.0
LARGE_FILE_THRESHOLD = 1000


def run_coverage_analysis() -> Dict:
    """Execute pytest avec coverage et retourne les résultats."""
    print("🔍 Exécution de l'analyse de couverture...")
    
    try:
        # Run coverage with JSON output
        result = subprocess.run(
            ["pytest", "--cov=src", "--cov-report=json", "--cov-report=term", "-q"],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        print("Coverage output:")
        print(result.stdout)
        if result.stderr:
            print("Errors/Warnings:")
            print(result.stderr)
        
        # Load JSON coverage data
        if Path(".coverage.json").exists():
            with open(".coverage.json", "r") as f:
                return json.load(f)
        elif Path("coverage.json").exists():
            with open("coverage.json", "r") as f:
                return json.load(f)
        else:
            print("⚠️ Fichier JSON de couverture non trouvé, analyse partielle disponible")
            return {}
            
    except subprocess.TimeoutExpired:
        print("⚠️ Timeout lors de l'exécution des tests")
        return {}
    except Exception as e:
        print(f"⚠️ Erreur lors de l'analyse de couverture: {e}")
        return {}


def get_file_line_count(file_path: Path) -> int:
    """Compte le nombre de lignes dans un fichier."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return len(f.readlines())
    except Exception:
        return 0


def find_test_file_for_source(src_file: Path) -> List[Path]:
    """Trouve le(s) fichier(s) de test correspondant à un fichier source."""
    # Convertir le chemin source en chemin de test potentiel
    relative_path = src_file.relative_to(SRC_DIR)
    
    # Plusieurs patterns de nommage possibles
    patterns = [
        f"test_{relative_path.stem}.py",  # test_module.py
        f"{relative_path.stem}_test.py",  # module_test.py
        f"test_{relative_path.stem}_*.py",  # test_module_*.py
    ]
    
    test_files = []
    
    # Chercher dans la structure miroir
    test_dir = TESTS_DIR / relative_path.parent
    if test_dir.exists():
        for pattern in patterns:
            test_files.extend(test_dir.glob(pattern))
    
    # Chercher aussi dans les autres emplacements courants
    for test_subdir in [TESTS_DIR, TESTS_DIR / "unit", TESTS_DIR / "integration"]:
        if test_subdir.exists():
            for pattern in patterns:
                test_files.extend(test_subdir.glob(pattern))
    
    return list(set(test_files))  # Dédupliquer


def count_test_functions(test_file: Path) -> int:
    """Compte le nombre de fonctions de test dans un fichier."""
    try:
        with open(test_file, "r", encoding="utf-8") as f:
            content = f.read()
            # Compter les définitions de test
            return len(re.findall(r'^\s*def test_', content, re.MULTILINE))
    except Exception:
        return 0


def analyze_file(src_file: Path, coverage_data: Dict) -> Dict:
    """Analyse un fichier source individuel."""
    line_count = get_file_line_count(src_file)
    test_files = find_test_file_for_source(src_file)
    
    # Extraire la couverture depuis les données
    coverage_percent = 0.0
    file_key = str(src_file)
    
    if coverage_data and "files" in coverage_data:
        for key, data in coverage_data["files"].items():
            if src_file.name in key or str(src_file) in key:
                summary = data.get("summary", {})
                coverage_percent = summary.get("percent_covered", 0.0)
                break
    
    total_test_functions = sum(count_test_functions(tf) for tf in test_files)
    
    return {
        "path": str(src_file),
        "line_count": line_count,
        "coverage": coverage_percent,
        "test_files": [str(tf) for tf in test_files],
        "test_count": total_test_functions,
        "needs_splitting": line_count > LARGE_FILE_THRESHOLD,
        "below_threshold": coverage_percent < COVERAGE_THRESHOLD,
        "has_tests": len(test_files) > 0
    }


def analyze_directory(directory: Path, coverage_data: Dict) -> Dict:
    """Analyse récursive d'un répertoire."""
    results = {
        "path": str(directory.relative_to(SRC_DIR)),
        "files": [],
        "subdirs": [],
        "total_files": 0,
        "avg_coverage": 0.0,
        "files_below_threshold": 0,
        "large_files": 0
    }
    
    # Analyser les fichiers Python dans ce répertoire
    for py_file in directory.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
        
        file_analysis = analyze_file(py_file, coverage_data)
        results["files"].append(file_analysis)
        results["total_files"] += 1
        
        if file_analysis["below_threshold"]:
            results["files_below_threshold"] += 1
        if file_analysis["needs_splitting"]:
            results["large_files"] += 1
    
    # Analyser les sous-répertoires
    for subdir in directory.iterdir():
        if subdir.is_dir() and not subdir.name.startswith(".") and not subdir.name == "__pycache__":
            subdir_analysis = analyze_directory(subdir, coverage_data)
            results["subdirs"].append(subdir_analysis)
    
    # Calculer la couverture moyenne
    all_coverages = [f["coverage"] for f in results["files"] if f["coverage"] > 0]
    results["avg_coverage"] = sum(all_coverages) / len(all_coverages) if all_coverages else 0.0
    
    return results


def generate_report(analysis: Dict) -> str:
    """Génère un rapport en markdown."""
    lines = [
        "# Rapport d'Analyse de Couverture de Tests",
        "",
        f"**Seuil de couverture**: {COVERAGE_THRESHOLD}%",
        f"**Seuil de taille de fichier**: {LARGE_FILE_THRESHOLD} lignes",
        "",
        "## Résumé Global",
        ""
    ]
    
    def add_dir_summary(dir_data: Dict, level: int = 2):
        """Ajoute récursivement le résumé d'un répertoire."""
        indent = "  " * (level - 2)
        lines.append(f"{'#' * level} {indent}{dir_data['path'] or 'Root'}")
        lines.append("")
        lines.append(f"- **Fichiers totaux**: {dir_data['total_files']}")
        lines.append(f"- **Couverture moyenne**: {dir_data['avg_coverage']:.2f}%")
        lines.append(f"- **Fichiers sous le seuil**: {dir_data['files_below_threshold']}")
        lines.append(f"- **Fichiers volumineux (>{LARGE_FILE_THRESHOLD} lignes)**: {dir_data['large_files']}")
        lines.append("")
        
        # Lister les fichiers problématiques
        problem_files = [f for f in dir_data["files"] if f["below_threshold"] or f["needs_splitting"]]
        if problem_files:
            lines.append("### ⚠️ Fichiers nécessitant une attention:")
            lines.append("")
            for file_data in problem_files:
                rel_path = Path(file_data["path"]).relative_to(SRC_DIR)
                issues = []
                if file_data["needs_splitting"]:
                    issues.append(f"📏 {file_data['line_count']} lignes")
                if file_data["below_threshold"]:
                    issues.append(f"📊 {file_data['coverage']:.1f}% couverture")
                if not file_data["has_tests"]:
                    issues.append("❌ Pas de tests")
                
                lines.append(f"- `{rel_path}` - {', '.join(issues)}")
                if file_data["test_files"]:
                    lines.append(f"  - Tests: {', '.join([Path(t).name for t in file_data['test_files']])}")
            lines.append("")
        
        # Traiter les sous-répertoires
        for subdir in dir_data["subdirs"]:
            add_dir_summary(subdir, level + 1)
    
    add_dir_summary(analysis)
    
    # Recommandations
    lines.extend([
        "## 📋 Recommandations",
        "",
        "### Fichiers à diviser (>1000 lignes):",
        ""
    ])
    
    def collect_large_files(dir_data: Dict, result: List):
        for file_data in dir_data["files"]:
            if file_data["needs_splitting"]:
                result.append(file_data)
        for subdir in dir_data["subdirs"]:
            collect_large_files(subdir, result)
    
    large_files = []
    collect_large_files(analysis, large_files)
    large_files.sort(key=lambda x: x["line_count"], reverse=True)
    
    for i, file_data in enumerate(large_files[:10], 1):
        rel_path = Path(file_data["path"]).relative_to(SRC_DIR)
        lines.append(f"{i}. `{rel_path}` ({file_data['line_count']} lignes)")
    
    lines.extend([
        "",
        "### Fichiers sans tests ou avec faible couverture (<80%):",
        ""
    ])
    
    def collect_low_coverage_files(dir_data: Dict, result: List):
        for file_data in dir_data["files"]:
            if file_data["below_threshold"] or not file_data["has_tests"]:
                result.append(file_data)
        for subdir in dir_data["subdirs"]:
            collect_low_coverage_files(subdir, result)
    
    low_coverage = []
    collect_low_coverage_files(analysis, low_coverage)
    low_coverage.sort(key=lambda x: x["coverage"])
    
    for i, file_data in enumerate(low_coverage[:20], 1):
        rel_path = Path(file_data["path"]).relative_to(SRC_DIR)
        status = "❌ Aucun test" if not file_data["has_tests"] else f"📊 {file_data['coverage']:.1f}%"
        lines.append(f"{i}. `{rel_path}` - {status}")
    
    return "\n".join(lines)


def main():
    """Point d'entrée principal."""
    print("=" * 80)
    print("🧪 ANALYSE DE COUVERTURE DE TESTS - Assistant MaTanne")
    print("=" * 80)
    print()
    
    # Vérifier que nous sommes dans le bon répertoire
    if not SRC_DIR.exists() or not TESTS_DIR.exists():
        print("❌ Erreur: Les répertoires src/ et tests/ doivent exister")
        sys.exit(1)
    
    # Exécuter l'analyse de couverture
    coverage_data = run_coverage_analysis()
    
    # Analyser la structure
    print("\n📊 Analyse de la structure des fichiers...")
    analysis = analyze_directory(SRC_DIR, coverage_data)
    
    # Générer le rapport
    print("\n📝 Génération du rapport...")
    report = generate_report(analysis)
    
    # Sauvegarder le rapport
    report_path = Path("coverage_analysis_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"\n✅ Rapport généré: {report_path}")
    
    # Sauvegarder aussi les données JSON pour traitement ultérieur
    json_path = Path("coverage_analysis_data.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2)
    
    print(f"✅ Données JSON sauvegardées: {json_path}")
    
    # Afficher le rapport dans le terminal
    print("\n" + "=" * 80)
    print(report)
    print("=" * 80)


if __name__ == "__main__":
    main()
