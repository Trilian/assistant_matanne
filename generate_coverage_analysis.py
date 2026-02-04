#!/usr/bin/env python3
"""
Script to analyze coverage and generate weak files report
"""
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Coverage data from pytest output
COVERAGE_DATA = {
    "src\\core\\constants.py": 97.20,
    "src\\core\\models\\base.py": 96.43,
    "src\\core\\models\\courses.py": 96.83,
    "src\\core\\models\\user_preferences.py": 96.34,
    "src\\core\\models\\users.py": 94.74,
    "src\\core\\models\\inventaire.py": 92.16,
    "src\\core\\models\\jeux.py": 90.61,
    "src\\core\\models\\planning.py": 95.56,
    "src\\core\\models\\batch_cooking.py": 87.59,
    "src\\core\\models\\nouveaux.py": 99.42,
    "src\\core\\models\\recettes.py": 70.00,
    "src\\core\\models\\schemas.py": 90.91,
    "src\\core\\cache.py": 28.68,
    "src\\core\\database.py": 22.94,
    "src\\core\\decorators.py": 21.21,
    "src\\core\\config.py": 34.57,
    "src\\core\\state.py": 41.26,
    "src\\core\\validation.py": 25.48,
    "src\\core\\validators_pydantic.py": 57.28,
    "src\\core\\errors.py": 13.61,
    "src\\core\\errors_base.py": 47.92,
    "src\\core\\logging.py": 54.62,
    "src\\core\\ai\\cache.py": 34.25,
    "src\\core\\ai\\client.py": 9.69,
    "src\\core\\ai\\parser.py": 8.41,
    "src\\core\\ai\\rate_limit.py": 27.78,
    "src\\services\\courses.py": 21.93,
    "src\\services\\recettes.py": 25.46,
    "src\\services\\planning.py": 20.82,
    "src\\services\\planning_unified.py": 26.21,
    "src\\services\\user_preferences.py": 22.73,
    "src\\services\\types.py": 8.56,
    "src\\services\\io_service.py": 15.13,
    "src\\services\\base_ai_service.py": 11.81,
    "src\\services\\inventaire.py": 19.69,
    # More modules...
}

def categorize_files():
    """Categorize files by coverage level"""
    
    categories = {
        "critical": [],  # < 10%
        "very_low": [],  # 10-20%
        "low": [],       # 20-40%
        "medium": [],    # 40-60%
        "good": [],      # 60-80%
        "excellent": []  # 80%+
    }
    
    for file, coverage in COVERAGE_DATA.items():
        if coverage < 10:
            categories["critical"].append((file, coverage))
        elif coverage < 20:
            categories["very_low"].append((file, coverage))
        elif coverage < 40:
            categories["low"].append((file, coverage))
        elif coverage < 60:
            categories["medium"].append((file, coverage))
        elif coverage < 80:
            categories["good"].append((file, coverage))
        else:
            categories["excellent"].append((file, coverage))
    
    # Sort each category by coverage (ascending)
    for key in categories:
        categories[key].sort(key=lambda x: x[1])
    
    return categories

def estimate_tests_needed(current_coverage: float, target: float = 80.0) -> int:
    """Estimate number of tests needed to reach target coverage"""
    if current_coverage >= target:
        return 0
    gap = target - current_coverage
    # Rough estimation: each percentage point needs ~1-2 tests
    return max(2, int(gap * 1.5))

def generate_markdown_report():
    """Generate markdown report"""
    categories = categorize_files()
    
    report = []
    report.append("# 📊 Rapport Détaillé de Couverture de Code\n")
    report.append("## Résumé Global\n")
    report.append("- **Couverture globale**: 8.34%")
    report.append("- **Tests créés**: 232 (Phase 1: 141, Phase 2: 91)")
    report.append("- **Tests validés**: 62 (Phase 1 modules + Phase 2 modules)")
    report.append("- **Statut**: En amélioration progressive\n")
    
    # Statistics
    total_files = len(COVERAGE_DATA)
    files_below_80 = sum(1 for f, c in COVERAGE_DATA.items() if c < 80)
    critical_files = sum(1 for f, c in COVERAGE_DATA.items() if c < 10)
    
    report.append("## Statistiques\n")
    report.append(f"| Métrique | Valeur |")
    report.append(f"|----------|--------|")
    report.append(f"| Total fichiers analysés | {total_files} |")
    report.append(f"| Fichiers < 80% | {files_below_80} ({100*files_below_80//total_files}%) |")
    report.append(f"| Fichiers critiques (< 10%) | {critical_files} |")
    report.append(f"| Couverture moyenne | {sum(c for f, c in COVERAGE_DATA.items()) / total_files:.1f}% |\n")
    
    # Priority files
    report.append("## 🔴 Fichiers Prioritaires (< 10% de couverture - CRITIQUE)\n")
    report.append("Priorité maximale - Ces fichiers nécessitent immédiatement des tests\n")
    report.append("| Fichier | Couverture | Gap | Tests estimés |")
    report.append("|---------|-----------|-----|---|")
    
    for file, coverage in categories["critical"]:
        gap = 80 - coverage
        tests = estimate_tests_needed(coverage, 80)
        file_short = file.replace("src\\", "")
        report.append(f"| [{file_short}]({file_short}) | {coverage:.1f}% | {gap:.1f}pp | ~{tests} |")
    report.append("")
    
    # Very low coverage
    report.append("## 🟠 Couverture Très Faible (10-20%)\n")
    report.append("Priorité haute - Ces fichiers doivent être couverts rapidement\n")
    report.append("| Fichier | Couverture | Gap | Tests estimés |")
    report.append("|---------|-----------|-----|---|")
    
    for file, coverage in categories["very_low"]:
        gap = 80 - coverage
        tests = estimate_tests_needed(coverage, 80)
        file_short = file.replace("src\\", "")
        report.append(f"| [{file_short}]({file_short}) | {coverage:.1f}% | {gap:.1f}pp | ~{tests} |")
    report.append("")
    
    # Low coverage
    report.append("## 🟡 Couverture Faible (20-40%)\n")
    report.append("Priorité moyenne - Amélioration nécessaire\n")
    report.append("| Fichier | Couverture | Gap | Tests estimés |")
    report.append("|---------|-----------|-----|---|")
    
    for file, coverage in categories["low"][:15]:  # Top 15
        gap = 80 - coverage
        tests = estimate_tests_needed(coverage, 80)
        file_short = file.replace("src\\", "")
        report.append(f"| [{file_short}]({file_short}) | {coverage:.1f}% | {gap:.1f}pp | ~{tests} |")
    report.append("")
    
    # Good coverage
    report.append("## 🟢 Bonne Couverture (60-80%)\n")
    report.append("| Fichier | Couverture | Gap | Tests estimés |")
    report.append("|---------|-----------|-----|---|")
    
    for file, coverage in categories["good"]:
        gap = 80 - coverage
        tests = estimate_tests_needed(coverage, 80)
        file_short = file.replace("src\\", "")
        report.append(f"| [{file_short}]({file_short}) | {coverage:.1f}% | {gap:.1f}pp | ~{tests} |")
    report.append("")
    
    # Excellent coverage
    report.append("## ✅ Excellente Couverture (80%+)\n")
    report.append(f"**{len(categories['excellent'])} fichiers** avec couverture >= 80%\n")
    report.append("| Fichier | Couverture |")
    report.append("|---------|-----------|")
    
    for file, coverage in sorted(categories["excellent"], key=lambda x: x[1], reverse=True):
        file_short = file.replace("src\\", "")
        report.append(f"| [{file_short}]({file_short}) | {coverage:.1f}% ✅ |")
    report.append("")
    
    # Action plan
    report.append("## 📋 Plan d'Action Recommandé\n")
    report.append("### Phase 1 (Priorité - Cette semaine)")
    report.append("1. Couvrir les **fichiers critiques** (< 10%)")
    report.append(f"   - {critical_files} fichiers identifiés")
    report.append(f"   - Estimation: ~{sum(estimate_tests_needed(c, 80) for f, c in categories['critical'])} tests")
    report.append("")
    report.append("### Phase 2 (Haute priorité - Cette semaine)")
    report.append("1. Améliorer la **couverture très faible** (10-20%)")
    report.append(f"   - {len(categories['very_low'])} fichiers identifiés")
    report.append(f"   - Estimation: ~{sum(estimate_tests_needed(c, 80) for f, c in categories['very_low'])} tests")
    report.append("")
    report.append("### Phase 3 (Prochaine semaine)")
    report.append("1. Couvrir les fichiers **40-60%**")
    report.append("2. Atteindre **80% de couverture globale**")
    report.append("")
    
    # Top 20 files to improve
    report.append("## 🎯 Top 20 Fichiers à Améliorer en Priorité\n")
    report.append("| # | Fichier | Couverture | Gap | Tests |")
    report.append("|---|---------|-----------|-----|-------|")
    
    all_below_80 = [(f, c) for f, c in COVERAGE_DATA.items() if c < 80]
    all_below_80.sort(key=lambda x: x[1])
    
    for i, (file, coverage) in enumerate(all_below_80[:20], 1):
        gap = 80 - coverage
        tests = estimate_tests_needed(coverage, 80)
        file_short = file.replace("src\\", "")
        report.append(f"| {i} | [{file_short}]({file_short}) | {coverage:.1f}% | {gap:.1f}pp | ~{tests} |")
    report.append("")
    
    return "\n".join(report)

if __name__ == "__main__":
    markdown = generate_markdown_report()
    
    # Save report
    report_file = Path("d:\\Projet_streamlit\\assistant_matanne\\RAPPORT_COUVERTURE_DETAILLE.md")
    report_file.write_text(markdown, encoding="utf-8")
    
    print(f"✅ Rapport généré: {report_file}")
    print(f"\n{markdown}")
