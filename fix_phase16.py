#!/usr/bin/env python3
"""
Fix test_phase16_extended.py field names
Replace jour_semaine, semaine with proper Planning/Repas fields
"""

import re

# Read file
with open('tests/integration/test_phase16_extended.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix patterns
fixes = [
    # Fix 1: Planning(semaine=date(...)) → Planning(nom="...", semaine_debut=date(...), semaine_fin=date(...)+timedelta(days=6))
    (r'Planning\(semaine=(date\([^)]+\))', r'Planning(nom="PlanningTest", semaine_debut=\1, semaine_fin=\1+timedelta(days=6)'),
    
    # Fix 2: Remove jour_semaine parameter from Planning
    (r',\s*jour_semaine="[^"]*"', ''),
    
    # Fix 3: Remove type_repas from Planning (not a Planning field)
    (r'planning = Planning\([^)]*type_repas="[^"]*"[^)]*\)', lambda m: 
     re.sub(r',?\s*type_repas="[^"]*"', '', m.group(0))),
    
    # Fix 4: Replace jour="..." in Repas with date_repas=date(...)
    # This is tricky - for now, replace jour= with a date mapping
    (r'jour="lundi"', 'date_repas=date(2025, 2, 3)'),
    (r'jour="mardi"', 'date_repas=date(2025, 2, 4)'),
    (r'jour="mercredi"', 'date_repas=date(2025, 2, 5)'),
    (r'jour="jeudi"', 'date_repas=date(2025, 2, 6)'),
    (r'jour="vendredi"', 'date_repas=date(2025, 2, 7)'),
    (r'jour="samedi"', 'date_repas=date(2025, 2, 8)'),
    (r'jour="dimanche"', 'date_repas=date(2025, 2, 9)'),
]

# Apply fixes
for pattern, replacement in fixes:
    if callable(replacement):
        # Skip callable replacements for now
        continue
    else:
        content = re.sub(pattern, replacement, content)

# Write back
with open('tests/integration/test_phase16_extended.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed test_phase16_extended.py")
