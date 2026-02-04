#!/usr/bin/env python3
"""Génère un rapport d'analyse détaillé par module."""

import subprocess
from collections import defaultdict
import re

# Commande pour collecter les tests skipped ET failed
result = subprocess.run(
    ["python", "-m", "pytest", "tests/", "-v", "--co", "-q"],
    capture_output=True,
    text=True
)

output = result.stdout

# Analyse simple
print("ANALYSE RAPIDE DES TESTS\n")
print("="*80)

# Compteurs
api_tests = output.count("test_api_endpoints")
service_tests = output.count("test_services")
core_tests = output.count("test_core")
domain_tests = output.count("domains")

print(f"📁 API Tests:              ~{api_tests} tests")
print(f"📁 Service Tests:          ~{service_tests} tests")
print(f"📁 Core Tests:             ~{core_tests} tests")
print(f"📁 Domain Tests:           ~{domain_tests} tests")

print("\n" + "="*80)
print("MODULES MAJEURS IDENTIFIÉS\n")

modules_to_check = [
    ("tests/api/", "API Endpoints"),
    ("tests/services/", "Services"),
    ("tests/core/", "Core Systems"),
    ("tests/domains/", "Domain Logic"),
]

# Try to find problematic patterns
problematic_patterns = {
    "test_maison_extended": "Maison (Extended)",
    "test_planning_extended": "Planning (Extended)",
    "test_tier1_critical": "Tier1 Critical",
    "test_courses_service": "Courses Service",
    "test_cache_multi": "Cache (Multi)",
    "test_inventaire_extended": "Inventaire (Extended)",
}

print("Modules potentiellement problématiques (patterns):\n")
for pattern, name in problematic_patterns.items():
    count = output.count(pattern)
    if count > 0:
        print(f"  - {name:<30} {count:>3} tests")

print("\n" + "="*80)
print("PROCHAINE ÉTAPE\n")

print("""
Pour analyser précisément les failures vs skipped:

1. Lancer: 
   pytest tests/services/test_maison_extended.py -v --tb=short
   pytest tests/services/test_planning_extended.py -v --tb=short
   pytest tests/services/test_tier1_critical.py -v --tb=short

2. Identifier les patterns de failures

3. Prioriser corrections par:
   - Impact (nombre de tests)
   - Difficulté (une simple signature = facile)
   - Risque (tests critiques vs edge cases)
""")
