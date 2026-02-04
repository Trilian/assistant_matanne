#!/usr/bin/env python3
"""
Script d'exécution du plan de couverture 80%
Exécute les phases séquentiellement et génère des rapports
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Mapping des phases avec leurs tests et sources
PHASES = {
    "phase1_core": {
        "name": "Phase 1: Core Foundation",
        "test_dirs": ["tests/core/"],
        "src_dirs": ["src/core/"],
        "target": 80,
        "priority": "CRITIQUE"
    },
    "phase2_api": {
        "name": "Phase 2: API Module",
        "test_dirs": ["tests/api/"],
        "src_dirs": ["src/api/"],
        "target": 80,
        "priority": "HAUTE"
    },
    "phase3_services": {
        "name": "Phase 3: Services",
        "test_dirs": ["tests/services/"],
        "src_dirs": ["src/services/"],
        "target": 80,
        "priority": "HAUTE"
    },
    "phase4_domains": {
        "name": "Phase 4: Domains",
        "test_dirs": ["tests/domains/"],
        "src_dirs": ["src/domains/"],
        "target": 80,
        "priority": "MOYENNE"
    },
    "phase5_ui_utils": {
        "name": "Phase 5: UI & Utils",
        "test_dirs": ["tests/ui/", "tests/utils/"],
        "src_dirs": ["src/ui/", "src/utils/"],
        "target": 80,
        "priority": "MOYENNE"
    },
    "phase6_transversal": {
        "name": "Phase 6: Transversal & Validation",
        "test_dirs": ["tests/integration/", "tests/e2e/", "tests/edge_cases/"],
        "src_dirs": ["src/"],
        "target": 80,
        "priority": "FINALE"
    }
}


def run_coverage_for_phase(phase_id: str) -> dict:
    """Exécute la couverture pour une phase donnée"""
    phase = PHASES[phase_id]
    
    test_dirs = " ".join(phase["test_dirs"])
    src_dirs = ",".join(phase["src_dirs"])
    
    cmd = f"python -m pytest {test_dirs} --cov={src_dirs} --cov-report=term-missing --cov-report=json -q --tb=no"
    
    print(f"\n{'='*60}")
    print(f"🚀 {phase['name']}")
    print(f"   Tests: {test_dirs}")
    print(f"   Source: {src_dirs}")
    print(f"   Cible: {phase['target']}%")
    print(f"{'='*60}\n")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    # Parser le résultat
    output = result.stdout + result.stderr
    
    # Chercher la couverture totale
    import re
    match = re.search(r'TOTAL\s+\d+\s+\d+\s+(\d+)%', output)
    coverage_pct = int(match.group(1)) if match else 0
    
    status = "✅ PASS" if coverage_pct >= phase["target"] else "❌ FAIL"
    
    print(f"\n📊 Résultat {phase['name']}: {coverage_pct}% {status}")
    
    return {
        "phase": phase_id,
        "name": phase["name"],
        "coverage": coverage_pct,
        "target": phase["target"],
        "passed": coverage_pct >= phase["target"]
    }


def run_global_coverage() -> dict:
    """Exécute la couverture globale"""
    cmd = "python -m pytest tests/ --cov=src --cov-report=term --cov-report=html --cov-report=json -q --tb=no"
    
    print(f"\n{'='*60}")
    print("🌍 COUVERTURE GLOBALE")
    print(f"{'='*60}\n")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    output = result.stdout + result.stderr
    
    import re
    match = re.search(r'TOTAL\s+\d+\s+\d+\s+(\d+)%', output)
    coverage_pct = int(match.group(1)) if match else 0
    
    return {"global_coverage": coverage_pct}


def generate_report(results: list, global_cov: dict):
    """Génère un rapport de progression"""
    report = f"""
# 📊 RAPPORT DE COUVERTURE
**Généré le**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Couverture Globale: {global_cov['global_coverage']}%

## Résultats par Phase

| Phase | Couverture | Cible | Status |
|-------|-----------|-------|--------|
"""
    
    for r in results:
        status = "✅" if r["passed"] else "❌"
        report += f"| {r['name']} | {r['coverage']}% | {r['target']}% | {status} |\n"
    
    report += f"""

## Prochaines Étapes

"""
    
    for r in results:
        if not r["passed"]:
            gap = r["target"] - r["coverage"]
            report += f"- ⚠️ **{r['name']}**: +{gap}% requis\n"
    
    # Sauvegarder le rapport
    with open("RAPPORT_PROGRESSION_COUVERTURE.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print(report)


def main():
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Exécution du plan de couverture 80%")
    parser.add_argument("--phase", choices=list(PHASES.keys()) + ["all", "global"], 
                        default="global", help="Phase à exécuter")
    parser.add_argument("--report", action="store_true", help="Générer un rapport complet")
    
    args = parser.parse_args()
    
    if args.phase == "global":
        result = run_global_coverage()
        print(f"\n🎯 Couverture globale: {result['global_coverage']}%")
        
    elif args.phase == "all":
        results = []
        for phase_id in PHASES:
            result = run_coverage_for_phase(phase_id)
            results.append(result)
        
        global_cov = run_global_coverage()
        
        if args.report:
            generate_report(results, global_cov)
    else:
        result = run_coverage_for_phase(args.phase)
        print(f"\n📊 {result['name']}: {result['coverage']}% (cible: {result['target']}%)")


if __name__ == "__main__":
    main()
