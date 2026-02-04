#!/usr/bin/env python3
"""Extrait les métriques de couverture complètes du rapport HTML"""

import json
import re
from pathlib import Path

def extract_coverage_from_html():
    """Extrait couverture du fichier HTML"""
    html_file = Path("htmlcov/index.html")
    
    if not html_file.exists():
        print("❌ htmlcov/index.html n'existe pas")
        return None
    
    content = html_file.read_text(encoding='utf-8')
    
    # Chercher le total: data-ratio="3563 31434">11.33%
    match = re.search(r'data-ratio="(\d+)\s+(\d+)">(\d+\.\d+)%', content)
    
    if match:
        covered = int(match.group(1))
        total = int(match.group(2))
        pct = float(match.group(3))
        
        print("\n" + "="*60)
        print("📊 COUVERTURE GLOBALE (DE TOUS LES 3908 TESTS)".center(60))
        print("="*60)
        print(f"\n  Couverture: {pct}%")
        print(f"  Lignes couvertes: {covered:,} / {total:,}")
        print(f"  Lignes non couvertes: {total - covered:,}")
        print(f"\n" + "="*60)
        
        return {"coverage": pct, "covered": covered, "total": total}
    
    return None

def extract_test_results():
    """Extrait résultats des tests du fichier log"""
    log_file = Path("coverage_full_measure.txt")
    
    if not log_file.exists():
        print("❌ coverage_full_measure.txt n'existe pas")
        return None
    
    content = log_file.read_text(encoding='utf-8', errors='ignore')
    last_lines = content.split('\n')[-50:]
    last_text = '\n'.join(last_lines)
    
    # Chercher pattern: X passed, Y failed, Z skipped in Zs
    match = re.search(r'(\d+) passed(?:.*?(\d+) failed)?(?:.*?(\d+) skipped)?', last_text)
    
    if match:
        passed = int(match.group(1))
        failed = int(match.group(2)) if match.group(2) else 0
        skipped = int(match.group(3)) if match.group(3) else 0
        total = passed + failed + skipped
        
        print("\n" + "="*60)
        print("🧪 RÉSULTATS DES TESTS (3908 TOTAL)".center(60))
        print("="*60)
        print(f"\n  ✅ PASSED:  {passed:5} ({passed/total*100:5.1f}%)")
        print(f"  ❌ FAILED:  {failed:5} ({failed/total*100:5.1f}%)" if failed > 0 else "")
        print(f"  ⏭️  SKIPPED: {skipped:5} ({skipped/total*100:5.1f}%)" if skipped > 0 else "")
        print(f"  📊 TOTAL:   {total:5}")
        print(f"\n" + "="*60)
        
        return {"passed": passed, "failed": failed, "skipped": skipped, "total": total}
    else:
        print(f"⏳ Tests encore en cours... cherche résultats...")
        if "collected 3908" in content:
            print("   ✓ 3908 tests collectés confirmés")
        return None

def main():
    print("\n🔍 Extraction des métriques de couverture...\n")
    
    coverage = extract_coverage_from_html()
    tests = extract_test_results()
    
    if coverage and tests:
        print("\n💡 RÉSUMÉ:")
        print(f"   - Tests: {tests['passed']} / {tests['total']} exécutés")
        print(f"   - Couverture: {coverage['coverage']}% des {coverage['total']:,} lignes")
        print(f"   - Ratio tests/couverture: {coverage['covered'] / tests['total']:.2f} lignes/test")
    elif coverage:
        print("\n✓ Couverture extraite, tests encore en cours")
    else:
        print("\n⏳ En attente des résultats...")

if __name__ == "__main__":
    main()
