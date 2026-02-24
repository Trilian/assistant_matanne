#!/usr/bin/env python3
"""Verifie et corrige les fichiers avec BOM UTF-8.

Ce script detecte les fichiers Python contenant un BOM UTF-8 (Byte Order Mark)
et peut les convertir en UTF-8 sans BOM.

Usage:
    python scripts/convert_to_utf8.py           # Corrige tous les fichiers
    python scripts/convert_to_utf8.py --check   # Verifie sans modifier (exit 1 si problemes)
"""

import glob
import sys
from pathlib import Path

# BOM UTF-8 : 3 bytes au debut du fichier
UTF8_BOM = b"\xef\xbb\xbf"


def check_file_for_bom(filepath: str) -> bool:
    """Verifie si un fichier contient un BOM UTF-8.

    Returns:
        True si le fichier contient un BOM, False sinon.
    """
    try:
        with open(filepath, "rb") as f:
            return f.read(3) == UTF8_BOM
    except OSError:
        return False


def remove_bom(filepath: str) -> bool:
    """Supprime le BOM UTF-8 d'un fichier.

    Returns:
        True si le BOM a ete supprime, False sinon.
    """
    try:
        with open(filepath, "rb") as f:
            content = f.read()

        if content.startswith(UTF8_BOM):
            with open(filepath, "wb") as f:
                f.write(content[3:])  # Ecrire sans les 3 premiers bytes (BOM)
            return True
        return False
    except OSError as e:
        print(f"Erreur lors du traitement de {filepath}: {e}")
        return False


def find_python_files(root_dir: str = ".") -> list[str]:
    """Trouve tous les fichiers Python dans le repertoire.

    Args:
        root_dir: Repertoire racine de recherche.

    Returns:
        Liste des chemins de fichiers Python.
    """
    patterns = [
        f"{root_dir}/src/**/*.py",
        f"{root_dir}/tests/**/*.py",
        f"{root_dir}/scripts/**/*.py",
        f"{root_dir}/*.py",
    ]

    files = []
    for pattern in patterns:
        files.extend(glob.glob(pattern, recursive=True))

    # Exclure les dossiers de cache et virtualenv
    excluded = {"__pycache__", ".venv", "venv", ".git", "node_modules", "sauvegardes"}
    return [f for f in files if not any(excl in f.replace("\\", "/") for excl in excluded)]


def main() -> int:
    """Point d'entree principal.

    Returns:
        0 si OK, 1 si problemes detectes en mode check.
    """
    check_only = "--check" in sys.argv

    # Determiner le repertoire racine
    script_path = Path(__file__).resolve()
    root_dir = script_path.parent.parent  # Remonter de scripts/ vers la racine

    files = find_python_files(str(root_dir))

    files_with_bom = []
    for filepath in files:
        if check_file_for_bom(filepath):
            files_with_bom.append(filepath)

    if not files_with_bom:
        if not check_only:
            print("Aucun fichier avec BOM UTF-8 detecte.")
        return 0

    if check_only:
        print(f"Fichiers avec BOM UTF-8 detectes ({len(files_with_bom)}):")
        for f in files_with_bom:
            print(f"  - {f}")
        print("\nExecutez 'python scripts/convert_to_utf8.py' pour corriger.")
        return 1

    # Mode correction
    fixed_count = 0
    for filepath in files_with_bom:
        if remove_bom(filepath):
            print(f"BOM supprime: {filepath}")
            fixed_count += 1

    print(f"\n{fixed_count} fichier(s) corrige(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
