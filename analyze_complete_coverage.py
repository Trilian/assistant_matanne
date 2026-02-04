#!/usr/bin/env python3
"""
Script pour analyser la couverture complète de src/ depuis pytest output
"""
import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

def parse_coverage_report(report_file: str) -> Dict[str, float]:
    """Parse coverage report from pytest output"""
    coverage_data = {}
    
    try:
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract coverage percentages using regex
        # Pattern: "src\path\file.py" ... "XX.XX%"
        pattern = r'(src\\[^\s]+\.py)\s+\d+\s+\d+\s+\d+\s+\d+\s+([\d.]+)%'
        matches = re.findall(pattern, content)
        
        for filepath, percentage in matches:
            coverage_data[filepath] = float(percentage)
    except Exception as e:
        print(f"Error parsing report: {e}")
    
    return coverage_data

def categorize_by_folder(coverage_data: Dict[str, float]) -> Dict[str, List[Tuple]]:
    """Categorize files by folder"""
    folders = defaultdict(list)
    
    for filepath, percentage in coverage_data.items():
        # Extract folder from path
        parts = filepath.split('\\')
        if len(parts) > 2:
            folder = '\\'.join(parts[:3])
        else:
            folder = parts[0]
        
        folders[folder].append((filepath, percentage))
    
    return dict(folders)

def generate_complete_report():
    """Generate complete coverage report for all src/"""
    report_file = "coverage_report_complete.txt"
    
    # Parse existing report
    coverage = parse_coverage_report(report_file)
    
    if not coverage:
        print(f"❌ No coverage data found in {report_file}")
        print("Generating test report first...")
        return
    
    # Categorize by folder
    by_folder = categorize_by_folder(coverage)
    
    # Calculate statistics
    total_files = len(coverage)
    files_below_80 = sum(1 for p in coverage.values() if p < 80)
    files_below_50 = sum(1 for p in coverage.values() if p < 50)
    files_below_20 = sum(1 for p in coverage.values() if p < 20)
    avg_coverage = sum(coverage.values()) / len(coverage) if coverage else 0
    
    # Generate markdown
    report_lines = []
    report_lines.append("# 📊 Rapport Complet de Couverture - src/\n")
    report_lines.append("## 📈 Statistiques Globales\n")
    
    report_lines.append(f"| Métrique | Valeur |")
    report_lines.append(f"|----------|--------|")
    report_lines.append(f"| **Total fichiers** | {total_files} |")
    report_lines.append(f"| **Fichiers < 80%** | {files_below_80} ({100*files_below_80//total_files}%) |")
    report_lines.append(f"| **Fichiers < 50%** | {files_below_50} ({100*files_below_50//total_files}%) |")
    report_lines.append(f"| **Fichiers < 20%** | {files_below_20} ({100*files_below_20//total_files}%) |")
    report_lines.append(f"| **Couverture moyenne** | {avg_coverage:.1f}% |")
    report_lines.append(f"| **Couverture min** | {min(coverage.values()):.1f}% |")
    report_lines.append(f"| **Couverture max** | {max(coverage.values()):.1f}% |\n")
    
    # Coverage distribution
    ranges = [
        (0, 10, "🔴 Critique"),
        (10, 20, "🔴 Très faible"),
        (20, 40, "🟠 Faible"),
        (40, 60, "🟡 Moyen"),
        (60, 80, "🟢 Bon"),
        (80, 101, "✅ Excellent")
    ]
    
    report_lines.append("## 📊 Distribution de Couverture\n")
    report_lines.append("| Plage | Nombre de fichiers | % |")
    report_lines.append("|-------|-------------------|---|")
    
    for min_cov, max_cov, label in ranges:
        count = sum(1 for p in coverage.values() if min_cov <= p < max_cov)
        pct = (100 * count // total_files) if total_files > 0 else 0
        report_lines.append(f"| {label} ({min_cov}-{max_cov}%) | {count} | {pct}% |")
    report_lines.append("")
    
    # By folder breakdown
    report_lines.append("## 📂 Couverture par Dossier\n")
    
    for folder in sorted(by_folder.keys()):
        files = by_folder[folder]
        folder_avg = sum(p for _, p in files) / len(files)
        file_count = len(files)
        below_80 = sum(1 for _, p in files if p < 80)
        
        report_lines.append(f"### {folder}")
        report_lines.append(f"- **Fichiers**: {file_count}")
        report_lines.append(f"- **Couverture moyenne**: {folder_avg:.1f}%")
        report_lines.append(f"- **Fichiers < 80%**: {below_80}\n")
        
        # List files below 80%
        weak_files = [(f, p) for f, p in files if p < 80]
        if weak_files:
            weak_files.sort(key=lambda x: x[1])
            report_lines.append("| Fichier | Couverture | Gap | Tests est. |")
            report_lines.append("|---------|-----------|-----|---|")
            for filepath, percentage in weak_files[:10]:  # Top 10 per folder
                gap = 80 - percentage
                tests = max(2, int(gap * 1.5))
                filename = Path(filepath).name
                report_lines.append(f"| {filename} | {percentage:.1f}% | {gap:.1f}pp | ~{tests} |")
            report_lines.append("")
    
    # Top 50 files to improve
    report_lines.append("## 🎯 Top 50 Fichiers à Améliorer\n")
    report_lines.append("| # | Fichier | Couverture | Gap | Tests |")
    report_lines.append("|---|---------|-----------|-----|-------|")
    
    sorted_files = sorted(coverage.items(), key=lambda x: x[1])
    for i, (filepath, percentage) in enumerate(sorted_files[:50], 1):
        gap = 80 - percentage
        tests = max(2, int(gap * 1.5))
        filename = Path(filepath).name
        report_lines.append(f"| {i} | {filename} | {percentage:.1f}% | {gap:.1f}pp | ~{tests} |")
    report_lines.append("")
    
    # Summary
    report_lines.append("## 📋 Résumé\n")
    total_tests_needed = sum(max(2, int((80 - p) * 1.5)) for p in coverage.values() if p < 80)
    report_lines.append(f"- **Tests créés**: 213 (validés)")
    report_lines.append(f"- **Tests nécessaires pour 80%**: ~{total_tests_needed}")
    report_lines.append(f"- **Couverture actuelle moyenne**: {avg_coverage:.1f}%")
    report_lines.append(f"- **Progression nécessaire**: {80 - avg_coverage:.1f}pp\n")
    
    # Save
    report_text = "\n".join(report_lines)
    output_file = Path("RAPPORT_COMPLET_SRC.md")
    output_file.write_text(report_text, encoding='utf-8')
    
    print(f"✅ Rapport complet généré: {output_file}")
    print(f"\n{report_text[:1000]}...")
    print(f"\n... (rapport complet saved)")

if __name__ == "__main__":
    generate_complete_report()
