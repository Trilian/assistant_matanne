#!/usr/bin/env python3
"""Exécution finale - Génère le rapport HTML de couverture."""

import subprocess
import json
import time
from pathlib import Path
from datetime import datetime

workspace = Path(__file__).parent

def main():
    print("\n" + "="*70)
    print(" "*15 + "🎯 EXÉCUTION FINALE - COUVERTURE")
    print("="*70)
    print(f"Démarrage: {datetime.now().strftime('%H:%M:%S')}\n")
    
    # Créer commande
    cmd = [
        "python", "-m", "pytest",
        "tests/",
        "--cov=src",
        "--cov-report=html",
        "--cov-report=term-missing",
        "-v",
        "--tb=short"
    ]
    
    print("📊 Commande exécutée:")
    print(f"  $ {' '.join(cmd)}\n")
    
    print("⏳ Exécution en cours...")
    print("   (Ceci peut prendre 5-10 minutes)\n")
    
    try:
        # Lancer pytest en arrière-plan
        process = subprocess.Popen(
            cmd,
            cwd=workspace,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Afficher output en temps réel
        lines_output = []
        line_count = 0
        
        for line in process.stdout:
            line_count += 1
            lines_output.append(line.rstrip())
            
            # Afficher chaque 50ème ligne pour voir la progression
            if line_count % 50 == 0:
                print(f"   • {line_count} lignes traitées...")
            
            # Afficher les lignes importantes
            if any(x in line for x in ["PASSED", "FAILED", "ERROR", "coverage", "passed"]):
                print(f"   {line.rstrip()}")
        
        # Attendre la fin
        return_code = process.wait()
        
        print(f"\n✅ Exécution terminée (code: {return_code})")
        
        # Chercher résultat dans les dernières lignes
        print("\n📈 RÉSULTATS:\n")
        for line in lines_output[-20:]:
            if line.strip():
                print(f"  {line}")
        
        # Vérifier si HTML généré
        html_report = workspace / "htmlcov" / "index.html"
        if html_report.exists():
            print(f"\n✅ Rapport HTML généré: htmlcov/index.html")
        
        # Chercher le résumé de couverture
        coverage_file = workspace / ".coverage"
        if coverage_file.exists():
            print(f"✅ Données de couverture sauvegardées")
        
        return True
        
    except KeyboardInterrupt:
        print("\n❌ Exécution annulée par l'utilisateur")
        return False
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    start = time.time()
    success = main()
    elapsed = time.time() - start
    
    print("\n" + "="*70)
    if success:
        print("✅ EXÉCUTION FINALE COMPLÉTÉE")
        print(f"⏱️  Durée: {elapsed/60:.1f} minutes")
        print("\n📂 Prochaines étapes:")
        print("  1. Ouvrir le rapport HTML:")
        print("     $ start htmlcov/index.html")
        print("  2. Vérifier la couverture par module")
        print("  3. Identifier les fichiers < 80%")
        print("  4. Créer les tests extended nécessaires")
    else:
        print("❌ EXÉCUTION ÉCHOUÉE")
    print("="*70 + "\n")
