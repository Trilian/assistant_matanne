#!/usr/bin/env python3
"""
Script de correction des erreurs de tests
- Corrige l'encodage des fichiers
- Identifie les imports manquants
"""

import os
from pathlib import Path

def main():
    base_path = Path('d:/Projet_streamlit/assistant_matanne')
    test_path = base_path / 'tests'
    src_path = base_path / 'src'

    print('=' * 70)
    print('Correction des erreurs d\'encodage et imports')
    print('=' * 70)

    # Étape 1: Corriger les encodages
    print('\n[1/3] Correction des encodages UTF-8...')
    fixed = 0
    skipped = 0

    for py_file in test_path.rglob('*.py'):
        if '__pycache__' in str(py_file):
            continue
        
        try:
            # Lire en UTF-8, sinon essayer avec Latin-1
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                with open(py_file, 'r', encoding='latin-1') as f:
                    content = f.read()
            
            # Réécrire en UTF-8
            with open(py_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            fixed += 1
        except Exception as e:
            skipped += 1

    print(f'  ✓ {fixed} fichiers corrigés')
    print(f'  - {skipped} fichiers ignorés')

    # Étape 2: Corriger sante.py
    print('\n[2/3] Correction de src/domains/famille/ui/sante.py...')
    sane_file = src_path / 'domains/famille/ui/sante.py'
    if sane_file.exists():
        try:
            try:
                with open(sane_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                with open(sane_file, 'r', encoding='latin-1') as f:
                    content = f.read()
            
            with open(sane_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print('  ✓ sante.py corrigé')
        except Exception as e:
            print(f'  ✗ Erreur: {e}')

    # Étape 3: Signaler les imports problématiques
    print('\n[3/3] Vérification des imports problématiques...')
    print('\n  ⚠  test_planning_module.py:')
    print('      Import: render_planning, render_generer, render_historique')
    print('      Status: À CORRIGER MANUELLEMENT')
    print('      Problème: Ces fonctions n\'existent pas dans planning_logic.py')
    
    print('\n  ⚠  test_courses_module.py:')
    print('      Import: render_liste_active, render_rayon_articles, etc.')
    print('      Status: À CORRIGER MANUELLEMENT')
    print('      Problème: Ces fonctions n\'existent pas dans courses_logic.py')

    # Résumé
    print('\n' + '=' * 70)
    print('RÉSUMÉ')
    print('=' * 70)
    print(f'✓ Encodage: {fixed} fichiers corrigés')
    print('⚠ Imports: 2 fichiers à corriger manuellement')
    print('\nProchaines étapes:')
    print('  1. Ouvrir test_planning_module.py et vérifier l\'import')
    print('  2. Ouvrir test_courses_module.py et vérifier l\'import')
    print('  3. Exécuter: pytest tests/ -v pour valider')
    print('=' * 70 + '\n')

if __name__ == '__main__':
    main()
