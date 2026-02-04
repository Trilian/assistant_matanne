#!/usr/bin/env python3
"""Analyse précise de la couverture en lisant le rapport HTML."""

import re
from pathlib import Path
from collections import defaultdict

workspace = Path(__file__).parent

def extract_coverage_from_html():
    """Extrait les données de couverture du rapport HTML."""
    
    htmlcov_dir = workspace / "htmlcov"
    index_file = htmlcov_dir / "index.html"
    
    print("\n" + "="*70)
    print("📊 ANALYSE DE COUVERTURE - Fichiers < 80%")
    print("="*70 + "\n")
    
    if not index_file.exists():
        print(f"⚠️  Fichier {index_file} non trouvé")
        return
    
    print("📂 Analysant index.html...\n")
    
    try:
        content = index_file.read_text(encoding='utf-8')
        
        # Chercher les lignes avec pourcentage de couverture
        # Pattern: <a href="...">filename</a> ... percentage%
        pattern = r'<a href="[^"]+">([^<]+)</a>.*?(\d+)%'
        
        matches = re.findall(pattern, content)
        
        if matches:
            files_data = defaultdict(list)
            
            for filename, coverage_str in matches:
                coverage = int(coverage_str)
                
                # Filtrer les vrais fichiers source
                if "src/" in filename or coverage < 100:
                    files_data['all'].append((filename, coverage))
                    
                    if coverage < 80:
                        # Extraire le module
                        if "src/" in filename:
                            parts = filename.split("/")
                            module = parts[1] if len(parts) > 1 else "other"
                        else:
                            module = "other"
                        
                        files_data[module].append((filename, coverage))
            
            # Afficher résumé
            low_count = len(files_data.get('all', []))
            print(f"🔴 Fichiers TOTAUX: {len(files_data.get('all', []))}")
            print(f"🔴 Fichiers < 80%: {len([c for _, c in files_data.get('all', []) if c < 80])}\n")
            
            # Détail par module < 80%
            modules_low = {k: v for k, v in files_data.items() if k != 'all' and v}
            
            if modules_low:
                print("Détail des fichiers < 80%:\n")
                
                for module in sorted(modules_low.keys()):
                    files = sorted([(f, c) for f, c in modules_low[module] if c < 80], key=lambda x: x[1])
                    
                    if files:
                        print(f"  📁 {module}/ ({len(files)} fichiers)")
                        
                        for filename, coverage in files[:10]:  # Afficher top 10
                            gap = 80 - coverage
                            bar = "█" * int(coverage/10) + "░" * (8 - int(coverage/10))
                            print(f"     • {filename:<45} {coverage:>3}% [{bar}] (+{gap}%)")
                        
                        if len(files) > 10:
                            print(f"     ... et {len(files)-10} autres fichiers")
                        print()
        else:
            print("⚠️  Impossible d'extraire les données de couverture du HTML")
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print("="*70 + "\n")

def simple_analysis():
    """Analyse simple en regardant les fichiers source."""
    
    print("\n" + "="*70)
    print("📊 ANALYSE SIMPLE - Fichiers Source < 80% (estimation)")
    print("="*70 + "\n")
    
    src_dir = workspace / "src"
    
    # Modules identifiés comme < 80%
    low_coverage_modules = {
        "src/utils": "~60%",
        "src/domains": "~45%",
        "src/services": "~70%",
    }
    
    print("🔴 Modules avec couverture estimée < 80%:\n")
    
    for module, coverage in low_coverage_modules.items():
        module_path = workspace / module
        py_files = list(module_path.glob("**/*.py"))
        
        coverage_val = int(coverage.strip("~%"))
        gap = 80 - coverage_val
        bar = "█" * int(coverage_val/10) + "░" * (8 - int(coverage_val/10))
        
        print(f"  📁 {module:<20} {coverage:>6} [{bar}] (gap: +{gap}%)")
        print(f"     → {len(py_files)} fichiers Python")
        print(f"     → ~{len(py_files)*3}-{len(py_files)*5} tests manquants")
        print()
    
    print("="*70)
    print("📈 RÉSUMÉ ESTIMATION")
    print("="*70 + "\n")
    
    total_files = 0
    total_tests_needed = 0
    
    for module, coverage in low_coverage_modules.items():
        module_path = workspace / module
        py_files = list(module_path.glob("**/*.py"))
        total_files += len(py_files)
        total_tests_needed += len(py_files) * 4
    
    print(f"  Fichiers à couvrir: ~{total_files}")
    print(f"  Tests à créer: ~{total_tests_needed}")
    print(f"  Gap total: +{(80-70)*3} à +{(80-45)*4}% couverture")
    
    print("\n" + "="*70)
    print("💡 ACTIONS RECOMMANDÉES")
    print("="*70 + "\n")
    
    print("""
  1️⃣  PRIORISER les modules:
      • src/domains/ (45% → 35% gap, ~83 fichiers)
      • src/utils/ (60% → 20% gap, ~21 fichiers)
      • src/services/ (70% → 10% gap, ~33 fichiers)
  
  2️⃣  CRÉER les 6 fichiers extended:
      • tests/domains/test_cuisine_extended.py
      • tests/domains/test_famille_extended.py
      • tests/domains/test_planning_extended.py
      • tests/utils/test_formatters_extended.py
      • tests/utils/test_validators_extended.py
      • tests/utils/test_helpers_extended.py
  
  3️⃣  AJOUTER ~100-150 tests dans ces fichiers
  
  4️⃣  RE-EXÉCUTER pour valider:
      $ pytest tests/ --cov=src --cov-report=html
  
  5️⃣  OBJECTIF FINAL:
      ✅ Couverture globale ≥ 80%
      ✅ Pass rate ≥ 95%
""")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    # Essayer l'analyse HTML d'abord
    extract_coverage_from_html()
    
    # Puis l'estimation simple
    simple_analysis()
