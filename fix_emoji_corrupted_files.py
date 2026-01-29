#!/usr/bin/env python3
"""Script pour fixer tous les emojis corrompus dans les fichiers Python"""

import os
from pathlib import Path

def fix_emoji_in_file(filepath: str) -> int:
    """Corrige les emojis corrompus dans un fichier"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Remplacements simples - les chaînes UTF-8 corrompues
        replacements = [
            ('\xf0\x9f\xa4\x96', '\U0001f916'),  # Robot
            ('\xf0\x9f\x93\x88', '\U0001f4c8'),  # Graphique hausse
            ('\xf0\x9f\x93\xa6', '\U0001f4e6'),  # Boîte
            ('\xf0\x9f\x93\x85', '\U0001f4c5'),  # Calendrier
            ('\xf0\x9f\x93\x94', '\U0001f4d4'),  # Carnet
            ('\xf0\x9f\x93\x8a', '\U0001f4ca'),  # Graphique Stock
            ('\xf0\x9f\x93\x9a', '\U0001f4da'),  # Livres
            ('\xf0\x9f\x93\x8b', '\U0001f4cb'),  # Planning
            ('\xf0\x9f\x93\x9c', '\U0001f4dc'),  # Historique
            ('\xf0\x9f\x93\xb8', '\U0001f4f8'),  # Photos
            ('\xf0\x9f\x91\xb6', '\U0001f476'),  # Bébé
        ]
        
        count = 0
        for corrupted, fixed in replacements:
            new_content = content.replace(corrupted, fixed)
            if new_content != content:
                count += content.count(corrupted)
                content = new_content
        
        # Si des changements, sauvegarder
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return count
        
        return 0
    
    except Exception as e:
        print(f"Erreur pour {filepath}: {e}")
        return -1

def main():
    """Parcourt tous les fichiers Python et corrige les emojis"""
    print("\n" + "="*70)
    print("CORRECTION DES EMOJIS CORROMPUS - FICHIERS PYTHON")
    print("="*70)
    
    root_dir = Path("src")
    py_files = list(root_dir.rglob("*.py"))
    
    print(f"\nScanning {len(py_files)} fichiers Python...")
    
    total_fixed = 0
    files_modified = 0
    
    for py_file in sorted(py_files):
        count = fix_emoji_in_file(str(py_file))
        
        if count > 0:
            files_modified += 1
            total_fixed += count
            rel_path = py_file.relative_to(Path.cwd())
            print(f"[OK] {rel_path}: {count} emojis corriges")
        elif count < 0:
            rel_path = py_file.relative_to(Path.cwd())
            print(f"[ERR] {rel_path}: erreur")
    
    print("\n" + "="*70)
    print(f"Fichiers modifies: {files_modified}")
    print(f"Emojis corriges: {total_fixed}")
    print("="*70 + "\n")
    
    if total_fixed > 0:
        print("SUCCESS! Les emojis ont ete corriges.")
        print("Relancer Streamlit pour voir les changements.")
    else:
        print("Aucun emoji corrompu trouve - tout est bon!")

if __name__ == "__main__":
    main()
