#!/usr/bin/env python3
"""
Exécuter Phase 16 et mesurer couverture globale
"""

import subprocess
import json
import sys

test_files = [
    "tests/services/test_services_basic.py",
    "tests/services/test_services_integration.py",
    "tests/models/test_models_basic.py",
    "tests/core/test_decorators_basic.py",
    "tests/utils/test_utils_basic.py",
    "tests/integration/test_domains_integration.py",
    "tests/integration/test_business_logic.py",
    "tests/integration/test_phase_16_expanded.py"
]

print("=" * 70)
print("PHASE 16: EXECUTION & COUVERTURE GLOBALE")
print("=" * 70)

# Exécuter tests
cmd = [
    "pytest",
    *test_files,
    "--cov=src",
    "--cov-report=json",
    "--cov-report=term-missing",
    "-v",
    "--tb=short",
    "-q"
]

print(f"\n📊 Exécution de {len(test_files)} fichiers de test...\n")
result = subprocess.run(cmd, capture_output=True, text=True)

print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

# Extraire couverture
try:
    with open("coverage.json", "r") as f:
        coverage_data = json.load(f)
    
    total_coverage = coverage_data.get("totals", {}).get("percent_covered", 0)
    
    print("\n" + "=" * 70)
    print(f"📈 COUVERTURE GLOBALE: {total_coverage:.2f}%")
    print("=" * 70)
    
    # Module breakdown
    files = coverage_data.get("files", {})
    modules = {}
    for file_path, file_data in files.items():
        if "/src/" in file_path:
            # Extract module name
            parts = file_path.split("/src/")[1].split("/")
            module = parts[0] if parts else "unknown"
            
            if module not in modules:
                modules[module] = {"covered": 0, "total": 0}
            
            coverage_stats = file_data.get("summary", {})
            modules[module]["covered"] += coverage_stats.get("covered_lines", 0)
            modules[module]["total"] += coverage_stats.get("num_statements", 0)
    
    print("\nBREAKDOWN PAR MODULE:")
    for module in sorted(modules.keys()):
        stats = modules[module]
        if stats["total"] > 0:
            pct = (stats["covered"] / stats["total"]) * 100
            print(f"  {module:15s}: {pct:6.2f}%")
    
except Exception as e:
    print(f"⚠️  Erreur extraction couverture: {e}")
    sys.exit(1)

sys.exit(result.returncode)
