#!/usr/bin/env python3
"""
Mesure de couverture par module - évite pytest hang.
Exécute les tests par domaine isolé avec timeout.
Généré: Diagnostic 4 février 2026
"""

import subprocess
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

@dataclass
class CoverageResult:
    module: str
    total_lines: int
    covered_lines: int
    coverage_pct: float
    tests_passed: int
    tests_failed: int
    status: str

def measure_module_coverage(module_path: str, timeout: int = 60) -> Optional[CoverageResult]:
    """Mesure la couverture pour un module spécifique."""
    print(f"📊 Mesurant couverture: {module_path}...")
    
    try:
        cmd = [
            "pytest",
            f"tests/{module_path}/",
            f"--cov=src.{module_path.replace('/', '.')}",
            "--cov-report=json:coverage_module.json",
            "--cov-report=term-missing",
            "-v",
            "--tb=short",
            f"--timeout={timeout}"
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout + 30
        )
        
        # Parser la couverture depuis JSON
        coverage_file = Path("coverage_module.json")
        if coverage_file.exists():
            with open(coverage_file) as f:
                cov_data = json.load(f)
                total = cov_data['totals']['num_statements']
                covered = cov_data['totals']['covered_lines']
                pct = cov_data['totals']['percent_covered']
                
            # Parser les tests
            output = result.stdout
            passed = output.count(" PASSED")
            failed = output.count(" FAILED")
            
            return CoverageResult(
                module=module_path,
                total_lines=total,
                covered_lines=covered,
                coverage_pct=pct,
                tests_passed=passed,
                tests_failed=failed,
                status="✅ OK" if pct >= 80 else "⚠️ LOW" if pct >= 50 else "🔴 CRITICAL"
            )
        
    except subprocess.TimeoutExpired:
        print(f"❌ TIMEOUT: {module_path}")
        return CoverageResult(module_path, 0, 0, 0, 0, 0, "⏱️ TIMEOUT")
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return CoverageResult(module_path, 0, 0, 0, 0, 0, "❌ ERROR")
    
    return None

def main():
    """Mesure la couverture pour tous les modules."""
    modules = [
        "services",
        "core",
        "modules",
    ]
    
    results = []
    total_coverage = 0
    
    print("=" * 80)
    print("🔍 MESURE DE COUVERTURE PAR MODULE")
    print("=" * 80)
    print()
    
    for module in modules:
        result = measure_module_coverage(module)
        if result:
            results.append(result)
            total_coverage += result.coverage_pct
            print(f"  Module: {result.module}")
            print(f"  Couverture: {result.coverage_pct:.1f}% ({result.covered_lines}/{result.total_lines} lignes)")
            print(f"  Tests: {result.tests_passed} passed, {result.tests_failed} failed")
            print(f"  Status: {result.status}")
            print()
    
    # Résumé
    print("=" * 80)
    print("📋 RÉSUMÉ GLOBAL")
    print("=" * 80)
    
    avg_coverage = total_coverage / len(results) if results else 0
    
    print(f"\n✓ Modules analysés: {len(results)}")
    print(f"✓ Couverture moyenne: {avg_coverage:.1f}%")
    print(f"✓ Objectif: 80%")
    
    if avg_coverage >= 80:
        print(f"\n🎉 OBJECTIF ATTEINT! Couverture ≥ 80%")
    elif avg_coverage >= 50:
        print(f"\n⚠️ À améliorer: {80 - avg_coverage:.1f}% manquants pour 80%")
    else:
        print(f"\n🔴 CRITIQUE: Couverture < 50%")
    
    # Tableau détaillé
    print("\n" + "=" * 80)
    print("📊 TABLEAU DÉTAILLÉ")
    print("=" * 80)
    print(f"{'Module':<20} {'Couverture':<15} {'Lignes':<20} {'Tests':<15} {'Status':<15}")
    print("-" * 85)
    
    for r in results:
        print(f"{r.module:<20} {r.coverage_pct:>5.1f}%{'':<8} {r.covered_lines:>3}/{r.total_lines:<3} {r.tests_passed:>3}✓ {r.tests_failed:>2}✗ {r.status:<15}")
    
    print("=" * 85)

if __name__ == "__main__":
    main()
