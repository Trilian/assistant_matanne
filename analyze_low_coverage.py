#!/usr/bin/env python3
"""Analyse le rapport de couverture pour identifier les fichiers < 80%."""

import json
import re
from pathlib import Path
from collections import defaultdict

workspace = Path(__file__).parent

def analyze_coverage():
    """Analyse la couverture à partir du rapport HTML."""
    
    htmlcov_dir = workspace / "htmlcov"
    
    print("\n" + "="*70)
    print("📊 ANALYSE DE COUVERTURE - Fichiers < 80%")
    print("="*70 + "\n")
    
    # Chercher le fichier status.json
    status_file = htmlcov_dir / "status.json"
    
    if status_file.exists():
        print("📂 Analysant status.json...\n")
        
        try:
            with open(status_file) as f:
                status = json.load(f)
            
            # Extraire les données de couverture
            files_coverage = status.get("files", {})
            
            # Filtrer les fichiers < 80%
            low_coverage = {}
            modules_coverage = defaultdict(list)
            
            for filepath, data in files_coverage.items():
                if isinstance(data, dict):
                    coverage = data.get("coverage", 0)
                else:
                    coverage = data
                
                if coverage < 80:
                    low_coverage[filepath] = coverage
                    
                    # Grouper par module
                    parts = filepath.split("/")
                    if len(parts) > 0:
                        module = parts[0] if parts[0] != "src" else (parts[1] if len(parts) > 1 else "unknown")
                        modules_coverage[module].append((filepath, coverage))
            
            print(f"🔴 Fichiers avec couverture < 80%: {len(low_coverage)}\n")
            
            if low_coverage:
                print("Détail par module:\n")
                
                # Trier par module
                for module in sorted(modules_coverage.keys()):
                    files = sorted(modules_coverage[module], key=lambda x: x[1])
                    print(f"  📁 {module}/ ({len(files)} fichiers)")
                    
                    for filepath, coverage in files:
                        # Simplifier le chemin
                        simple_path = filepath.replace("src/", "").replace(".py", "")
                        gap = 80 - coverage
                        bar = "█" * int(coverage/10) + "░" * (8 - int(coverage/10))
                        print(f"     • {simple_path:<40} {coverage:>6.1f}% [{bar}] (gap: +{gap:.1f}%)")
                    print()
            
            # Stats globales
            print("="*70)
            print("📈 STATISTIQUES")
            print("="*70 + "\n")
            
            all_coverage = [c for c in files_coverage.values() if isinstance(c, (int, float))]
            if all_coverage:
                avg_coverage = sum(all_coverage) / len(all_coverage)
                min_coverage = min(all_coverage)
                max_coverage = max(all_coverage)
                
                print(f"  Couverture moyenne:  {avg_coverage:.1f}%")
                print(f"  Couverture min:      {min_coverage:.1f}%")
                print(f"  Couverture max:      {max_coverage:.1f}%")
                print(f"  Fichiers < 80%:      {len(low_coverage)}")
                print(f"  Fichiers ≥ 80%:      {len(files_coverage) - len(low_coverage)}")
            
            # Recommandations
            print("\n" + "="*70)
            print("💡 RECOMMANDATIONS")
            print("="*70 + "\n")
            
            if len(low_coverage) > 0:
                print(f"  🎯 Créer tests pour {len(low_coverage)} fichiers < 80%")
                print(f"  📊 Cela devrait ajouter ~{len(low_coverage) * 5}-{len(low_coverage) * 10} tests")
                print(f"  ✨ Impact estimé: +{len(low_coverage) * 2}-{len(low_coverage) * 5}% couverture globale")
            else:
                print(f"  ✅ Tous les fichiers ont ≥ 80% de couverture!")
        
        except json.JSONDecodeError as e:
            print(f"❌ Erreur lecture JSON: {e}")
        except Exception as e:
            print(f"❌ Erreur analyse: {e}")
    
    else:
        print(f"⚠️  Fichier status.json non trouvé")
        print(f"   Chemin attendu: {status_file}")
        print("\n   Peut-être faut-il exécuter d'abord:")
        print("   $ pytest tests/ --cov=src --cov-report=html")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    analyze_coverage()
