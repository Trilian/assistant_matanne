#!/usr/bin/env python3
"""
Script pour corriger les fichiers Python avec des caractères BOM (Byte Order Mark).

Le caractère BOM (U+FEFF) au début d'un fichier UTF-8 cause des erreurs de parsing.
Ce script identifie et corrige ces fichiers.
"""

import sys
from pathlib import Path
from typing import List


SRC_DIR = Path("src")


def has_bom(file_path: Path) -> bool:
    """Vérifie si un fichier contient un BOM UTF-8."""
    try:
        with open(file_path, "rb") as f:
            first_bytes = f.read(3)
            # UTF-8 BOM is EF BB BF
            return first_bytes == b'\xef\xbb\xbf'
    except Exception as e:
        print(f"⚠️ Erreur lors de la vérification de {file_path}: {e}")
        return False


def remove_bom(file_path: Path, dry_run: bool = True) -> bool:
    """Supprime le BOM d'un fichier."""
    try:
        # Lire le fichier en mode binaire
        with open(file_path, "rb") as f:
            content = f.read()
        
        # Vérifier et supprimer le BOM
        if content.startswith(b'\xef\xbb\xbf'):
            content = content[3:]  # Supprimer les 3 premiers octets
            
            if dry_run:
                print(f"  [DRY-RUN] Supprimerait le BOM de: {file_path.relative_to(SRC_DIR)}")
                return True
            else:
                # Créer une sauvegarde
                backup_path = file_path.with_suffix(".py.bak")
                with open(backup_path, "wb") as f:
                    with open(file_path, "rb") as original:
                        f.write(original.read())
                
                # Écrire le fichier sans BOM
                with open(file_path, "wb") as f:
                    f.write(content)
                
                print(f"  ✅ BOM supprimé de: {file_path.relative_to(SRC_DIR)}")
                print(f"     Sauvegarde: {backup_path.name}")
                return True
        
        return False
        
    except Exception as e:
        print(f"  ❌ Erreur lors de la suppression du BOM de {file_path}: {e}")
        return False


def find_files_with_bom() -> List[Path]:
    """Trouve tous les fichiers Python avec BOM."""
    files_with_bom = []
    
    for py_file in SRC_DIR.rglob("*.py"):
        if has_bom(py_file):
            files_with_bom.append(py_file)
    
    return files_with_bom


def main():
    """Point d'entrée principal."""
    dry_run = True
    
    # Vérifier les arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--execute":
            dry_run = False
            print("⚠️ MODE EXÉCUTION ACTIVÉ - Les modifications seront appliquées!")
        elif sys.argv[1] == "--help":
            print("Usage: python tools/fix_utf8_bom.py [--execute]")
            print()
            print("Options:")
            print("  (aucun)    Mode dry-run (par défaut)")
            print("  --execute  Applique réellement les modifications")
            print("  --help     Affiche cette aide")
            return
    
    print("=" * 80)
    print("🔧 CORRECTION DES PROBLÈMES UTF-8 BOM")
    print("=" * 80)
    print()
    
    if dry_run:
        print("ℹ️ MODE DRY-RUN - Aucune modification ne sera appliquée")
        print("   Utilisez --execute pour appliquer les modifications")
    else:
        print("⚠️ MODE EXÉCUTION - Les modifications seront appliquées")
    
    print()
    
    # Trouver les fichiers avec BOM
    print("🔍 Recherche des fichiers avec BOM UTF-8...")
    files_with_bom = find_files_with_bom()
    
    if not files_with_bom:
        print("✅ Aucun fichier avec BOM trouvé!")
        return
    
    print(f"\n⚠️ Trouvé {len(files_with_bom)} fichier(s) avec BOM:\n")
    
    for file_path in files_with_bom:
        print(f"  - {file_path.relative_to(SRC_DIR)}")
    
    print()
    
    # Demander confirmation en mode exécution
    if not dry_run:
        print("⚠️ ATTENTION: Cette opération va modifier les fichiers!")
        response = input("Continuer? (oui/non): ").lower()
        if response not in ["oui", "o", "yes", "y"]:
            print("❌ Opération annulée")
            return
        print()
    
    # Corriger les fichiers
    print("🔧 Correction des fichiers...\n")
    
    fixed = 0
    failed = 0
    
    for file_path in files_with_bom:
        if remove_bom(file_path, dry_run):
            fixed += 1
        else:
            failed += 1
    
    print(f"\n{'='*80}")
    print("✅ Résumé:")
    print(f"   - Fichiers corrigés: {fixed}")
    print(f"   - Échecs: {failed}")
    
    if dry_run:
        print("\nℹ️ Utilisez --execute pour appliquer les modifications")
    else:
        print("\n✅ Corrections appliquées!")
        print("   Les fichiers originaux ont été sauvegardés en .bak")
    
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
