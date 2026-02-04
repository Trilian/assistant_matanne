#!/usr/bin/env python3
"""Analyser coverage.json et générer un rapport détaillé"""
import json
from pathlib import Path
from datetime import datetime

def analyze():
    if not Path("coverage.json").exists():
        print("coverage.json non trouvé")
        return
    
    with open("coverage.json", encoding="utf-8") as f:
        data = json.load(f)
    
    modules = {}
    total_lines, total_covered = 0, 0
    
    for file_path, file_data in data.get("files", {}).items():
        if "src/" not in file_path:
            continue
        
        module = file_path.split("src/")[1].split("/")[0]
        if module not in modules:
            modules[module] = {"lines": 0, "covered": 0, "files": []}
        
        summary = file_data.get("summary", {})
        lines = summary.get("num_statements", 0)
        covered = summary.get("num_executed", 0)
        
        modules[module]["lines"] += lines
        modules[module]["covered"] += covered
        total_lines += lines
        total_covered += covered
        
        if lines > 0:
            pct = (covered / lines * 100)
            modules[module]["files"].append({
                "file": file_path.split("src/")[1],
                "lines": lines,
                "covered": covered,
                "percent": pct
            })
    
    # Calculer pourcentages
    for module in modules:
        if modules[module]["lines"] > 0:
            modules[module]["percent"] = (
                modules[module]["covered"] / modules[module]["lines"] * 100
            )
    
    total_percent = (total_covered / total_lines * 100) if total_lines > 0 else 0
    
    # Rapport
    print("=" * 70)
    print("📊 RAPPORT DE COUVERTURE DÉTAILLÉ - ASSISTANT MATANNE")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Global
    print("RÉSUMÉ GLOBAL")
    print("-" * 70)
    print(f"Couverture totale:    {total_percent:.1f}%")
    print(f"Lignes couvertes:     {total_covered}/{total_lines}")
    status = "✅ 80%+" if total_percent >= 80 else "⚠️  60-80%" if total_percent >= 60 else "❌ <60%"
    print(f"Statut:               {status}\n")
    
    # Par module
    print("COUVERTURE PAR MODULE (6 domaines majeurs)")
    print("-" * 70)
    print(f"{'Module':<15} | {'Couverture':>12} | {'Lignes':>15} | {'Status':<6}")
    print("-" * 70)
    
    for m_name, m_data in sorted(modules.items(), key=lambda x: x[1].get("percent", 0), reverse=True):
        pct = m_data.get("percent", 0)
        lines_info = f"{m_data['covered']}/{m_data['lines']}"
        status = "✅" if pct >= 80 else "⚠️" if pct >= 60 else "❌"
        print(f"{m_name:<15} | {pct:>10.1f}% | {lines_info:>15} | {status:<6}")
    
    print("\n" + "=" * 70)
    print("ANALYSE - MODULES CRITIQUES (<60%)")
    print("=" * 70)
    
    critical = [(n, d) for n, d in modules.items() if d.get("percent", 0) < 60]
    if critical:
        for name, data in sorted(critical, key=lambda x: x[1].get("percent", 0)):
            pct = data.get("percent", 0)
            gap = 80 - pct
            print(f"\n❌ {name}: {pct:.1f}% (gap: +{gap:.1f}%)")
            print(f"   Lignes: {data['covered']}/{data['lines']}")
    else:
        print("✅ Pas de modules critiques (<60%)")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    analyze()
