#!/usr/bin/env python3
"""Analyser la couverture JSON et générer rapports détaillés."""

import json
import os
from pathlib import Path
from collections import defaultdict

def analyze_coverage():
    """Analyser le fichier .coverage.json."""
    
    cov_json_path = Path(".coverage.json")
    
    if not cov_json_path.exists():
        print("⏳ Attente du fichier .coverage.json...")
        return None
    
    print("\n" + "=" * 80)
    print("📊 ANALYSE DÉTAILLÉE DE COUVERTURE")
    print("=" * 80)
    
    try:
        with open(cov_json_path) as f:
            data = json.load(f)
        
        # Totaux
        totals = data.get("totals", {})
        global_coverage = totals.get("percent_covered", 0)
        
        print(f"\n🎯 COUVERTURE GLOBALE: {global_coverage:.1f}%")
        print(f"   Lignes couvertes: {totals.get('covered_lines', 0)}")
        print(f"   Lignes totales: {totals.get('num_statements', 0)}")
        
        # Analyser par fichier
        files = data.get("files", {})
        
        # Grouper par couverture
        excellent = []  # >= 90%
        good = []       # 80-89%
        medium = []     # 70-79%
        low = []        # 60-69%
        critical = []   # < 60%
        
        for filepath, file_data in files.items():
            if "src/" in filepath:
                summary = file_data.get("summary", {})
                coverage = summary.get("percent_covered", 0)
                
                short_path = filepath.replace("\\", "/").replace("src/", "")
                
                if coverage >= 90:
                    excellent.append((coverage, short_path))
                elif coverage >= 80:
                    good.append((coverage, short_path))
                elif coverage >= 70:
                    medium.append((coverage, short_path))
                elif coverage >= 60:
                    low.append((coverage, short_path))
                else:
                    critical.append((coverage, short_path))
        
        # Afficher résultats
        print("\n" + "=" * 80)
        print("📈 RÉPARTITION DES FICHIERS")
        print("=" * 80)
        
        print(f"\n🟢 EXCELLENT (≥90%): {len(excellent)} fichiers")
        for cov, path in sorted(excellent, reverse=True)[:5]:
            print(f"   {cov:5.1f}%  {path}")
        
        print(f"\n🟡 BON (80-89%): {len(good)} fichiers")
        for cov, path in sorted(good, reverse=True)[:10]:
            print(f"   {cov:5.1f}%  {path}")
        
        print(f"\n🟠 MOYEN (70-79%): {len(medium)} fichiers")
        for cov, path in sorted(medium, reverse=True)[:10]:
            print(f"   {cov:5.1f}%  {path}")
        
        print(f"\n🔴 FAIBLE (60-69%): {len(low)} fichiers")
        for cov, path in sorted(low, reverse=True):
            print(f"   {cov:5.1f}%  {path}")
        
        print(f"\n🔴🔴 CRITIQUE (<60%): {len(critical)} fichiers")
        for cov, path in sorted(critical):
            print(f"   {cov:5.1f}%  {path}")
        
        # Résumé
        print("\n" + "=" * 80)
        print("📊 RÉSUMÉ")
        print("=" * 80)
        print(f"Excellent (≥90%):  {len(excellent):3} fichiers")
        print(f"Bon (80-89%):      {len(good):3} fichiers")
        print(f"Moyen (70-79%):    {len(medium):3} fichiers")
        print(f"Faible (60-69%):   {len(low):3} fichiers")
        print(f"Critique (<60%):   {len(critical):3} fichiers")
        print(f"─────────────────────────────────")
        print(f"TOTAL:             {len(excellent) + len(good) + len(medium) + len(low) + len(critical):3} fichiers")
        
        # Cibles d'amélioration
        print("\n" + "=" * 80)
        print("🎯 FICHIERS À AMÉLIORER (priorité: < 80%)")
        print("=" * 80)
        
        to_improve = critical + low + medium
        to_improve.sort(key=lambda x: x[0])  # Trier du plus faible au plus fort
        
        for cov, path in to_improve[:20]:
            gap = 80 - cov
            priority = "🔴" if cov < 60 else "🔴" if cov < 70 else "🟠"
            print(f"{priority} {cov:5.1f}%  (+{gap:4.1f}% pour 80%)  {path}")
        
        return {
            'global': global_coverage,
            'excellent': excellent,
            'good': good,
            'medium': medium,
            'low': low,
            'critical': critical,
        }
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

if __name__ == "__main__":
    result = analyze_coverage()
