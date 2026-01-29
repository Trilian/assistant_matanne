#!/usr/bin/env python
"""
Script pour mesurer et afficher la couverture de tests
Utilisation: python measure_coverage.py [target]
"""

import subprocess
import sys
import json
import os
from pathlib import Path

def run_tests_with_coverage():
    """Exécute les tests et mesure la couverture"""
    print("🧪 Exécution des tests avec mesure de couverture...")
    print("⏳ Cela peut prendre 3-5 minutes...\n")
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "--cov=src",
        "--cov-report=json",
        "--cov-report=html",
        "-q",
        "--tb=line"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        return result
    except subprocess.TimeoutExpired:
        print("❌ Tests dépassé le timeout (600s)")
        return None

def read_coverage_data():
    """Lit les données de couverture depuis coverage.json"""
    if not os.path.exists("coverage.json"):
        print("❌ coverage.json not found")
        return None
    
    try:
        with open("coverage.json", "r", encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error reading coverage.json: {e}")
        return None

def display_coverage_report(data, target_pct=40):
    """Affiche un rapport détaillé de couverture"""
    if not data:
        print("❌ Aucune donnée de couverture")
        return None
    
    totals = data.get('totals', {})
    total_pct = totals.get('percent_covered', 0)
    covered = totals.get('covered_lines', 0)
    total_lines = totals.get('num_statements', 0)
    
    print("\n" + "="*70)
    print("📊 RAPPORT DE COUVERTURE")
    print("="*70)
    
    # Main metrics
    print(f"\nCouverture globale:        {total_pct:.2f}%")
    print(f"Lignes couvertes:          {covered}/{total_lines}")
    print(f"Cible:                     {target_pct}%")
    
    # Progress bar
    filled = int((total_pct / target_pct) * 40)
    bar = "█" * filled + "░" * (40 - filled)
    print(f"Progression:               [{bar}] {(total_pct/target_pct)*100:.1f}%")
    
    # Gap analysis
    gap = target_pct - total_pct
    if total_pct >= target_pct:
        print(f"\n✅ CIBLE ATTEINTE! (+{total_pct - target_pct:.2f}%)")
    else:
        print(f"\n⏳ Gap restant:             {gap:.2f}%")
        print(f"   Estimation:             {gap * 2:.0f}-{gap * 3:.0f} lignes à couvrir")
    
    # Files with lowest coverage
    print("\n" + "-"*70)
    print("📋 Fichiers avec couverture < 50% (priorité)")
    print("-"*70)
    
    files_coverage = []
    for filepath, file_data in data.get('files', {}).items():
        covered_lines = file_data['summary'].get('covered_lines', 0)
        total = file_data['summary'].get('num_statements', 0)
        
        if total > 10:  # Ignorer les fichiers < 10 lignes
            pct = (covered_lines / total) * 100
            if pct < 50:
                files_coverage.append((filepath, pct, total))
    
    # Sort by coverage
    files_coverage.sort(key=lambda x: x[1])
    
    count = 0
    for filepath, pct, total in files_coverage[:15]:
        if count >= 15:
            break
        
        status = "🔴" if pct < 10 else "🟡" if pct < 30 else "🟠"
        shortpath = filepath.replace("src\\", "").replace("src/", "")
        print(f"{status} {pct:5.1f}% | {total:3} lines | {shortpath}")
        count += 1
    
    if len(files_coverage) > 15:
        print(f"\n... et {len(files_coverage) - 15} autres fichiers")
    
    print("\n" + "="*70)
    return total_pct

def get_quick_wins(data):
    """Identifie les fichiers pour les gains rapides"""
    print("\n🎯 FICHIERS AVEC MEILLEUR POTENTIEL (pour gains rapides)")
    print("="*70)
    
    # Fichiers avec 0% couverture mais petit taille = gains rapides
    candidates = []
    for filepath, file_data in data.get('files', {}).items():
        covered = file_data['summary'].get('covered_lines', 0)
        total = file_data['summary'].get('num_statements', 0)
        
        if covered == 0 and 50 < total < 300:
            candidates.append((filepath, total))
    
    candidates.sort(key=lambda x: x[1])
    
    for i, (filepath, size) in enumerate(candidates[:5], 1):
        shortpath = filepath.replace("src\\", "").replace("src/", "")
        estimated_lines = min(size // 3, 50)  # ~30% pour nouveaux tests
        print(f"{i}. {shortpath}")
        print(f"   Size: {size} lines | Est. gain: {estimated_lines} lines")
        print()

if __name__ == "__main__":
    target = float(sys.argv[1]) if len(sys.argv) > 1 else 40
    
    # Run tests
    result = run_tests_with_coverage()
    
    if result and result.returncode >= 0:
        # Read coverage
        data = read_coverage_data()
        
        # Display report
        coverage = display_coverage_report(data, target)
        
        # Show quick wins
        if data:
            get_quick_wins(data)
        
        # Open HTML report
        html_file = Path("htmlcov/index.html")
        if html_file.exists():
            print(f"\n📈 Report HTML généré: {html_file}")
            print(f"   Ouvrir: {html_file.absolute()}")
    else:
        print("❌ Tests failed")
        sys.exit(1)
