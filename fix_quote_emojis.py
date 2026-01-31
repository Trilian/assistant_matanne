#!/usr/bin/env python3
"""Fix dictionary emoji quote issues and remaining mojibakes"""

import re
from pathlib import Path

# More aggressive mojibake fixes
AGGRESSIVE_FIXES = {
    # Emojis with missing quotes in dictionaries
    r'"emoji":\s*"([^"]*)"([,\s])*"color"': r'"emoji": "\1", "color"',
    r'"emoji":\s*"([^"]*),\s*"label"': r'"emoji": "\1", "label"',
    r'"emoji":\s*"([^"]*),\s*"color"': r'"emoji": "\1", "color"',
    
    # Remaining mojibakes
    'â„¹ï¸': 'ℹ️',
    'âš ï¸': '⚠️',
    'âŒ': '❌',
    'â­•': '◯',
    'Ã©': 'é',
    'â€"': '–',
    'â€™': "'",
    'â€œ': '"',
    'â€\x9d': '"',
}

def fix_file(filepath):
    """Fix dictionary quote issues and mojibakes"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Apply regex fixes
        for pattern, replacement in AGGRESSIVE_FIXES.items():
            if pattern.startswith(r'"emoji"'):
                content = re.sub(pattern, replacement, content)
            else:
                content = content.replace(pattern, replacement)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error in {filepath}: {e}")
        return False

# Files with known issues
PROBLEM_FILES = [
    'src/domains/cuisine/logic/inventaire_logic.py',
    'src/domains/famille/logic/accueil_logic.py',
    'src/domains/famille/ui/accueil.py',
    'src/domains/famille/ui/activites.py',
    'src/domains/famille/ui/bien_etre.py',
]

fixed_count = 0
for filepath in PROBLEM_FILES:
    path = Path(filepath)
    if path.exists():
        if fix_file(path):
            fixed_count += 1
            print(f"Fixed: {filepath}")
    else:
        print(f"Not found: {filepath}")

print(f"\nTotal files fixed: {fixed_count}")
