#!/usr/bin/env python3
"""
Script pour corriger les emojis cassés dans toute la codebase.
Remplace les séquences UTF-8 corrompues par les emojis valides.
"""

import os
import re
from pathlib import Path

# Mappings des emojis corrompus vers les emojis valides
EMOJI_FIXES = {
    # Plus cassé: âž• -> ➕
    'âž•': '➕',
    
    # Time/horloge cassé: â±ï¸ -> ⏱️
    'â±ï¸': '⏱️',
    'â±': '⏱',
    
    # Warning cassé: âš -> ⚠️
    'âš ï¸': '⚠️',
    'âš ': '⚠',
    'âš¡': '⚡',
    
    # Checkmark cassé: â˜'ï¸ -> ✓
    'â˜'ï¸': '✓',
    
    # Plante cassé: 💡± -> 🪴 (mais garder le lightbulb)
    '💡±': '💡🪴',
    
    # Placeholders génériques
    '[CHART]': '📊',
}

# Extensions à vérifier
EXTENSIONS = {'.py'}

def fix_emojis_in_file(filepath):
    """Corrige les emojis dans un fichier."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Appliquer toutes les corrections
        for corrupt, correct in EMOJI_FIXES.items():
            content = content.replace(corrupt, correct)
        
        # Écrire back si des changements ont été faits
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Erreur en traitant {filepath}: {e}")
        return False

def main():
    """Parcourt tous les fichiers Python et corrige les emojis."""
    src_dir = Path("src")
    fixed_count = 0
    
    if not src_dir.exists():
        print("Répertoire 'src' non trouvé.")
        return
    
    for filepath in src_dir.rglob("*"):
        if filepath.is_file() and filepath.suffix in EXTENSIONS:
            if fix_emojis_in_file(str(filepath)):
                print(f"✅ Corrigé: {filepath}")
                fixed_count += 1
    
    print(f"\n✅ {fixed_count} fichiers corrigés.")
    print(f"\nCorrections appliquées:")
    for corrupt, correct in EMOJI_FIXES.items():
        print(f"  '{corrupt}' → '{correct}'")

if __name__ == "__main__":
    main()
