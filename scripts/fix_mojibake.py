#!/usr/bin/env python3
"""Fix remaining mojibake patterns in source files."""

import os

# Patterns to fix (mojibake -> correct)
FIXES = {
    '\u00e2\u0153\u0085': '\u2705',  # checkmark
    '\u00e2\u0152': '\u274c',        # cross
    '\u00e2\u0161 ': '\u26a0\ufe0f', # warning
    '\u00e2\u0161\u00a1': '\u26a1',  # lightning
    '\u00e2\u00b0': '\u23f0',        # alarm
    '\u00e2\u0086\u2019': '\u2192',  # arrow
    '\u00e2\u201c': '\u2753',        # question
}

files = [
    'src/modules/cuisine/inventaire/alertes.py',
    'src/modules/cuisine/inventaire/utils.py',
    'src/modules/cuisine/planificateur_repas/preferences.py',
    'src/modules/famille/routines.py',
    'src/modules/jeux/integration.py',
    'src/modules/jeux/loto/utils.py',
    'src/modules/maison/entretien.py',
    'src/modules/maison/jardin.py',
    'src/modules/maison/projets.py',
    'src/modules/outils/accueil_utils.py',
    'src/modules/outils/barcode.py',
    'src/modules/outils/parametres.py',
    'src/modules/outils/rapports.py',
    'src/modules/planning/vue_ensemble.py',
    'src/modules/planning/vue_ensemble_utils.py',
    'src/modules/planning/vue_semaine.py',
    'src/modules/planning/components/__init__.py',
    'src/services/budget/utils.py',
    'src/services/budget/__init__.py',
    'src/services/notifications/__init__.py',
    'src/services/rapports/__init__.py',
]

def main():
    fixed = 0
    for fpath in files:
        if not os.path.exists(fpath):
            print(f'Skip (not found): {fpath}')
            continue
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
        orig = content
        for old, new in FIXES.items():
            content = content.replace(old, new)
        if content != orig:
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(content)
            fixed += 1
            print(f'Fixed: {fpath}')
    print(f'Total fixed: {fixed}')

if __name__ == '__main__':
    main()
