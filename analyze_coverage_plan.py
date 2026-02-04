#!/usr/bin/env python3
"""Analyse la couverture actuelle et génère un plan vers 80%"""

import re
from pathlib import Path
from collections import defaultdict

def extract_coverage_from_html():
    """Extrait la couverture de chaque fichier depuis le rapport HTML"""
    html_file = Path("htmlcov/index.html")
    if not html_file.exists():
        return {}
    
    html = html_file.read_text(encoding='utf-8')
    
    # Pattern pour extraire: fichier, lignes couvertes, lignes totales, pourcentage
    pattern = r'<a href="[^"]+">([^<]+)</a></td>\s*<td[^>]*>&nbsp;</td>\s*<td[^>]*data-ratio="(\d+)\s+(\d+)">(\d+\.\d+)%'
    matches = re.findall(pattern, html)
    
    coverage = {}
    for m in matches:
        # Nettoyer le nom de fichier
        filename = m[0].replace('&#8201;', '').replace('\\', '/').strip()
        covered = int(m[1])
        total = int(m[2])
        pct = float(m[3])
        coverage[filename] = {"covered": covered, "total": total, "pct": pct}
    
    return coverage

def categorize_by_module(coverage_data):
    """Catégorise la couverture par module"""
    modules = defaultdict(lambda: {"files": [], "covered": 0, "total": 0})
    
    for filename, data in coverage_data.items():
        parts = filename.split('/')
        if len(parts) >= 2:
            module = parts[1]  # src/MODULE/...
        else:
            module = "root"
        
        modules[module]["files"].append((filename, data))
        modules[module]["covered"] += data["covered"]
        modules[module]["total"] += data["total"]
    
    return modules

def calculate_gap_to_80(modules):
    """Calcule l'écart pour atteindre 80% par module"""
    results = []
    for module, data in sorted(modules.items(), key=lambda x: x[1]["total"], reverse=True):
        if data["total"] == 0:
            continue
        
        current_pct = (data["covered"] / data["total"] * 100) if data["total"] > 0 else 0
        target_80 = int(data["total"] * 0.80)
        gap = max(0, target_80 - data["covered"])
        
        results.append({
            "module": module,
            "files": len(data["files"]),
            "total_lines": data["total"],
            "covered_lines": data["covered"],
            "current_pct": current_pct,
            "target_80": target_80,
            "gap_lines": gap,
            "priority": "CRITIQUE" if current_pct < 20 else "HAUTE" if current_pct < 50 else "MOYENNE" if current_pct < 70 else "BASSE"
        })
    
    return results

def find_low_coverage_files(coverage_data, threshold=30):
    """Trouve les fichiers avec couverture < seuil%"""
    low_files = []
    for filename, data in coverage_data.items():
        if data["pct"] < threshold and data["total"] > 20:  # Ignore les petits fichiers
            low_files.append({
                "file": filename,
                "pct": data["pct"],
                "total": data["total"],
                "gap_to_80": int(data["total"] * 0.80) - data["covered"]
            })
    
    return sorted(low_files, key=lambda x: x["gap_to_80"], reverse=True)

def main():
    print("\n" + "="*80)
    print("📊 ANALYSE COUVERTURE POUR PLAN 80%".center(80))
    print("="*80)
    
    coverage = extract_coverage_from_html()
    
    if not coverage:
        print("\n❌ Pas de données de couverture disponibles")
        print("Exécutez d'abord: pytest --cov=src --cov-report=html")
        return
    
    # Stats globales
    total_covered = sum(d["covered"] for d in coverage.values())
    total_lines = sum(d["total"] for d in coverage.values())
    global_pct = (total_covered / total_lines * 100) if total_lines > 0 else 0
    
    print(f"\n📈 COUVERTURE GLOBALE ACTUELLE")
    print(f"   {global_pct:.1f}% ({total_covered:,} / {total_lines:,} lignes)")
    print(f"   Gap pour 80%: {int(total_lines * 0.80) - total_covered:,} lignes supplémentaires")
    
    # Par module
    modules = categorize_by_module(coverage)
    results = calculate_gap_to_80(modules)
    
    print("\n" + "-"*80)
    print("📦 COUVERTURE PAR MODULE")
    print("-"*80)
    print(f"{'Module':<20} {'Fichiers':<10} {'Lignes':<10} {'Couvert':<10} {'%':<8} {'Gap 80%':<10} {'Priorité'}")
    print("-"*80)
    
    for r in results:
        print(f"{r['module']:<20} {r['files']:<10} {r['total_lines']:<10} {r['covered_lines']:<10} {r['current_pct']:>5.1f}%  {r['gap_lines']:<10} {r['priority']}")
    
    # Fichiers critiques
    low_files = find_low_coverage_files(coverage, threshold=20)
    
    print("\n" + "-"*80)
    print("🚨 TOP 20 FICHIERS CRITIQUES (< 20% couverture, > 20 lignes)")
    print("-"*80)
    
    for i, f in enumerate(low_files[:20], 1):
        print(f"  {i:2}. {f['file']:<55} {f['pct']:>5.1f}%  (gap: {f['gap_to_80']:>4} lignes)")
    
    # Fichiers moyens
    mid_files = [f for f in coverage.items() if 20 <= f[1]["pct"] < 50 and f[1]["total"] > 50]
    
    print(f"\n📋 FICHIERS À AMÉLIORER (20-50%, > 50 lignes): {len(mid_files)} fichiers")
    
    # Plan d'action
    print("\n" + "="*80)
    print("🎯 PLAN D'ACTION VERS 80%")
    print("="*80)
    
    print("""
PHASE 1: CRITIQUE - Modules < 20% (Priorité: TRÈS HAUTE)
=========================================================
""")
    
    for r in results:
        if r["priority"] == "CRITIQUE":
            print(f"  • {r['module']}: {r['current_pct']:.1f}% → 80% (besoin: +{r['gap_lines']} lignes)")
    
    print("""
PHASE 2: HAUTE - Modules 20-50% 
================================
""")
    
    for r in results:
        if r["priority"] == "HAUTE":
            print(f"  • {r['module']}: {r['current_pct']:.1f}% → 80% (besoin: +{r['gap_lines']} lignes)")
    
    print("""
PHASE 3: MOYENNE - Modules 50-70%
==================================
""")
    
    for r in results:
        if r["priority"] == "MOYENNE":
            print(f"  • {r['module']}: {r['current_pct']:.1f}% → 80% (besoin: +{r['gap_lines']} lignes)")
    
    print("""
PHASE 4: FINALISATION - Modules > 70%
======================================
""")
    
    for r in results:
        if r["priority"] == "BASSE":
            print(f"  • {r['module']}: {r['current_pct']:.1f}% → 80% (besoin: +{r['gap_lines']} lignes)")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
