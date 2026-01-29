#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de correction des erreurs d'encodage UTF-8 dans les fichiers Python.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Mappages des caractères mal encodés (UTF-8 interprété en latin-1)
# Utilisation de codes Unicode pour éviter les problèmes d'encodage du script lui-même
ENCODING_FIXES = {
    # Caractères accentués majuscules et minuscules
    '\u00c3\u0080': '\u00c0',  # Ã€ -> À
    '\u00c3\u0089': '\u00c9',  # Ã‰ -> É
    '\u00c3\u0088': '\u00c8',  # Ã' -> È
    '\u00c3\u008a': '\u00ca',  # ÃŠ -> Ê
    '\u00c3\u00ab': '\u00eb',  # ë -> ë
    '\u00c3\u00ae': '\u00ee',  # î -> î
    '\u00c3\u00af': '\u00ef',  # ï -> ï
    '\u00c3\u00b4': '\u00f4',  # ô -> ô
    '\u00c3\u00b9': '\u00f9',  # ù -> ù
    '\u00c3\u00bb': '\u00fb',  # û -> û
    '\u00c3\u00bc': '\u00fc',  # ü -> ü
    '\u00c3\u00a7': '\u00e7',  # ç -> ç
    
    # Minuscules
    '\u00c3\u00a1': '\u00e1',  # á -> á
    '\u00c3\u00a0': '\u00e0',  # Ã  -> à
    '\u00c3\u00a9': '\u00e9',  # é -> é
    '\u00c3\u00a8': '\u00e8',  # è -> è
    '\u00c3\u00aa': '\u00ea',  # ê -> ê
    '\u00c3\u00ad': '\u00ed',  # í -> í
    '\u00c3\u00b3': '\u00f3',  # ó -> ó
    '\u00c3\u00b1': '\u00f1',  # ñ -> ñ
    
    # Caractères spéciaux
    '\u00c2\u00ae': '\u00ae',  # ® -> ®
    '\u00e2\u0080\u0083': ' ',  # â€ƒ -> espace
    '\u00e2\u0080\u0093': '\u2013',  # â€" -> en-dash
    '\u00e2\u0080\u0094': '\u2014',  # â€" -> em-dash
    '\u00e2\u0080\u009c': '\u201c',  # â€œ -> "
    '\u00e2\u0080\u009d': '\u201d',  # â€\u009d -> "
    '\u00e2\u0080\u0098': '\u2018',  # â€˜ -> '
    '\u00e2\u0080\u0099': '\u2019',  # â€™ -> '
    '\u00e2\u0080\u00a6': '\u2026',  # â€¦ -> …
    '\u00e2\u0080\u00a2': '\u2022',  # â€¢ -> •
    
    # Traits et caractères de dessin
    '\u00e2\u0095\u0090': '\u2500',  # â•– -> ─
    '\u00e2\u0095\u0091': '\u2501',  # â•' -> ━
}


def try_read_file(filepath: Path) -> Tuple[str, str]:
    """
    Essaie de lire un fichier avec différents encodages.
    Retourne (contenu, encodage_utilisé)
    """
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                content = f.read()
            return content, encoding
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    return None, None


def detect_encoding_issues(content: str) -> bool:
    """Détecte s'il y a des caractères mal encodés."""
    # Chercher les patterns typiques d'erreurs d'encodage
    for key in ENCODING_FIXES.keys():
        if key in content:
            return True
    return False


def fix_encoding_issues(content: str) -> str:
    """Corrige les erreurs d'encodage dans le contenu."""
    fixed_content = content
    
    for wrong, correct in ENCODING_FIXES.items():
        fixed_content = fixed_content.replace(wrong, correct)
    
    # Nettoyage supplémentaire: supprimer les caractères UTF-8 invalides orphelins
    fixed_content = re.sub(r'[\x80-\x9f]', '', fixed_content)
    
    return fixed_content


def process_files(root_dir: Path) -> Dict[str, List[str]]:
    """
    Traite tous les fichiers .py du répertoire racine.
    Retourne un dictionnaire de statistiques.
    """
    stats = {
        'processed': [],
        'fixed': [],
        'errors': [],
        'skipped': [],
    }
    
    py_files = list(root_dir.rglob('*.py'))
    print(f"Trouve {len(py_files)} fichiers .py\n")
    
    for filepath in py_files:
        # Ignorer les répertoires spécifiques
        path_str = str(filepath)
        if any(part in path_str for part in ['.venv', '__pycache__', '.git', 'htmlcov']):
            stats['skipped'].append(path_str)
            continue
        
        try:
            # Lire le fichier
            content, encoding = try_read_file(filepath)
            
            if content is None:
                stats['errors'].append(f"{filepath}: Impossible de lire")
                continue
            
            stats['processed'].append(path_str)
            
            # Détecter les problèmes
            if detect_encoding_issues(content):
                print(f"[CORRECTION] {filepath.name}")
                print(f"  Encodage detecte: {encoding}")
                
                # Corriger
                fixed_content = fix_encoding_issues(content)
                
                # Sauvegarder
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                
                stats['fixed'].append(path_str)
                print(f"  OK - Corrige et sauvegarde en UTF-8\n")
        
        except Exception as e:
            stats['errors'].append(f"{filepath}: {str(e)}")
            print(f"[ERREUR] {filepath}: {e}\n")
    
    return stats


def print_report(stats: Dict[str, List[str]]):
    """Imprime un rapport des opérations effectuées."""
    print("\n" + "="*70)
    print("RAPPORT DE CORRECTION D'ENCODAGE")
    print("="*70 + "\n")
    
    print(f"Fichiers traites: {len(stats['processed'])}")
    print(f"Fichiers corriges: {len(stats['fixed'])}")
    print(f"Fichiers ignores: {len(stats['skipped'])}")
    print(f"Erreurs: {len(stats['errors'])}\n")
    
    if stats['fixed']:
        print("FICHIERS CORRIGES:")
        for file in stats['fixed'][:20]:
            print(f"  [OK] {file}")
        if len(stats['fixed']) > 20:
            print(f"  ... et {len(stats['fixed']) - 20} autres fichiers")
    
    if stats['errors']:
        print("\nERREURS RENCONTREES:")
        for error in stats['errors'][:10]:
            print(f"  [ERREUR] {error}")
        if len(stats['errors']) > 10:
            print(f"  ... et {len(stats['errors']) - 10} autres erreurs")
    
    print("\n" + "="*70)


def verify_critical_files(root_dir: Path):
    """Vérifie que les fichiers critiques sont maintenant lisibles."""
    print("\nVERIFICATION DES FICHIERS CRITIQUES:")
    print("-" * 70)
    
    critical_files = [
        'tests/core/test_ai_parser.py',
        'src/domains/famille/ui/sante.py',
    ]
    
    for rel_path in critical_files:
        filepath = root_dir / rel_path
        
        if not filepath.exists():
            print(f"[ATTENTION] Fichier non trouve: {rel_path}")
            continue
        
        try:
            content, encoding = try_read_file(filepath)
            
            if content is None:
                print(f"[ERREUR] {rel_path}: Impossible a lire")
                continue
            
            has_issues = detect_encoding_issues(content)
            
            if has_issues:
                print(f"[ATTENTION] {rel_path}: Encore des problemes d'encodage")
            else:
                print(f"[OK] {rel_path}: Lisible et sans erreurs d'encodage")
                
                # Afficher un aperçu
                lines = content.split('\n')[:3]
                print(f"  Apercu:")
                for line in lines:
                    if line.strip():
                        preview = line[:70]
                        print(f"    {preview}")
        
        except Exception as e:
            print(f"[ERREUR] {rel_path}: {e}")
    
    print()


if __name__ == '__main__':
    root_dir = Path('d:/Projet_streamlit/assistant_matanne').resolve()
    
    if not root_dir.exists():
        print(f"Erreur: Le repertoire {root_dir} n'existe pas")
        exit(1)
    
    print("Demarrage de la correction d'encodage UTF-8...")
    print(f"Repertoire cible: {root_dir}\n")
    
    # Traiter les fichiers
    stats = process_files(root_dir)
    
    # Afficher le rapport
    print_report(stats)
    
    # Vérifier les fichiers critiques
    verify_critical_files(root_dir)
    
    print("Correction terminee!")
