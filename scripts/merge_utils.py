#!/usr/bin/env python3
"""
Script pour fusionner utilitaires.py dans utils.py et mettre à jour les imports.

Usage:
    python scripts/merge_utils.py --dry-run  # Prévisualiser les changements
    python scripts/merge_utils.py            # Exécuter la fusion
"""

import os
import re
import sys

# Dossiers avec les deux fichiers à fusionner
DIRS_TO_MERGE = [
    "src/modules/cuisine/inventaire",
    "src/modules/cuisine/recettes",
    "src/modules/famille/achats_famille",
    "src/modules/famille/jules",
    "src/modules/famille/suivi_perso",
    "src/modules/famille/weekend",
    "src/modules/jeux/loto",
    "src/modules/jeux/paris",
]

# Dossiers avec seulement utilitaires.py -> renommer en utils.py
DIRS_TO_RENAME = [
    "src/modules/famille",
    "src/modules/jeux",
    "src/modules/maison",
]


def read_file(path: str) -> str:
    """Lire un fichier avec encodage UTF-8."""
    with open(path, encoding="utf-8") as f:
        return f.read()


def write_file(path: str, content: str) -> None:
    """Écrire un fichier avec encodage UTF-8."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def extract_imports_and_code(content: str) -> tuple[list[str], str]:
    """Sépare les imports du reste du code."""
    lines = content.split("\n")
    import_lines = []
    code_start = 0
    in_docstring = False
    docstring_char = None

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Gérer les docstrings multi-lignes
        if not in_docstring:
            if stripped.startswith('"""') or stripped.startswith("'''"):
                docstring_char = stripped[:3]
                if stripped.count(docstring_char) == 1:
                    in_docstring = True
                continue
        else:
            if docstring_char in stripped:
                in_docstring = False
            continue

        # Ignorer les lignes vides et commentaires au début
        if not stripped or stripped.startswith("#"):
            continue

        # Identifier les imports
        if stripped.startswith(("import ", "from ")):
            import_lines.append(line)
        else:
            code_start = i
            break

    # Trouver le vrai début du code (après imports et lignes vides)
    code_lines = lines[code_start:]
    # Supprimer les lignes vides au début
    while code_lines and not code_lines[0].strip():
        code_lines.pop(0)

    return import_lines, "\n".join(code_lines)


def merge_files(utils_path: str, utilitaires_path: str, dry_run: bool = False) -> bool:
    """Fusionne utilitaires.py dans utils.py."""
    if not os.path.exists(utils_path) or not os.path.exists(utilitaires_path):
        return False

    utils_content = read_file(utils_path)
    util_content = read_file(utilitaires_path)

    # Si utilitaires.py est vide ou juste des imports, ignorer
    if len(util_content.strip()) < 50:
        print(f"  Skipping {utilitaires_path} (too small)")
        return False

    # Extraire les imports et le code de utilitaires.py
    util_imports, util_code = extract_imports_and_code(util_content)

    # Construire le nouveau contenu
    # Ajouter une section séparatrice et le code de utilitaires
    separator = f"\n\n# {'=' * 60}\n# Fonctions importées depuis utilitaires.py\n# {'=' * 60}\n\n"

    merged_content = utils_content.rstrip() + separator + util_code

    if dry_run:
        print(f"  Would merge {utilitaires_path} into {utils_path}")
        print(f"    - Adding {len(util_code.split(chr(10)))} lines to utils.py")
    else:
        write_file(utils_path, merged_content)
        os.remove(utilitaires_path)
        print(f"  Merged {utilitaires_path} into {utils_path}")

    return True


def rename_utilitaires_to_utils(dir_path: str, dry_run: bool = False) -> bool:
    """Renomme utilitaires.py en utils.py si utils.py n'existe pas."""
    utilitaires_path = os.path.join(dir_path, "utilitaires.py")
    utils_path = os.path.join(dir_path, "utils.py")

    if not os.path.exists(utilitaires_path):
        return False

    if os.path.exists(utils_path):
        print(f"  Warning: Both files exist in {dir_path}, use merge instead")
        return False

    if dry_run:
        print(f"  Would rename {utilitaires_path} to {utils_path}")
    else:
        os.rename(utilitaires_path, utils_path)
        print(f"  Renamed {utilitaires_path} to {utils_path}")

    return True


def update_imports_in_file(file_path: str, dry_run: bool = False) -> int:
    """Met à jour les imports de utilitaires vers utils."""
    content = read_file(file_path)
    original = content

    # Patterns à remplacer
    patterns = [
        # from .utilitaires import X -> from .utils import X
        (r"from \.utilitaires import", "from .utils import"),
        # from src.modules.X.utilitaires import -> from src.modules.X.utils import
        (r"from (src\.modules\.[a-z_/]+)\.utilitaires import", r"from \1.utils import"),
        # import .utilitaires -> import .utils
        (r"import \.utilitaires\b", "import .utils"),
    ]

    changes = 0
    for pattern, replacement in patterns:
        new_content, n = re.subn(pattern, replacement, content)
        if n > 0:
            changes += n
            content = new_content

    if changes > 0:
        if dry_run:
            print(f"  Would update {changes} import(s) in {file_path}")
        else:
            write_file(file_path, content)
            print(f"  Updated {changes} import(s) in {file_path}")

    return changes


def find_python_files(base_dir: str) -> list[str]:
    """Trouve tous les fichiers Python dans un répertoire."""
    files = []
    for root, dirs, filenames in os.walk(base_dir):
        # Ignorer les dossiers spéciaux
        dirs[:] = [d for d in dirs if d not in ["__pycache__", ".git", "venv", ".venv"]]
        for f in filenames:
            if f.endswith(".py"):
                files.append(os.path.join(root, f))
    return files


def main():
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("=== DRY RUN MODE ===\n")

    # Étape 1: Fusionner les fichiers dans les dossiers avec les deux
    print("Étape 1: Fusion des fichiers utils.py et utilitaires.py")
    print("-" * 50)
    merged_count = 0
    for dir_path in DIRS_TO_MERGE:
        utils_path = os.path.join(dir_path, "utils.py")
        utilitaires_path = os.path.join(dir_path, "utilitaires.py")
        if merge_files(utils_path, utilitaires_path, dry_run):
            merged_count += 1
    print(f"\n  Total: {merged_count} fichier(s) fusionné(s)\n")

    # Étape 2: Renommer utilitaires.py en utils.py dans les autres dossiers
    print("Étape 2: Renommage de utilitaires.py en utils.py")
    print("-" * 50)
    renamed_count = 0
    for dir_path in DIRS_TO_RENAME:
        if rename_utilitaires_to_utils(dir_path, dry_run):
            renamed_count += 1
    print(f"\n  Total: {renamed_count} fichier(s) renommé(s)\n")

    # Étape 3: Mettre à jour tous les imports
    print("Étape 3: Mise à jour des imports")
    print("-" * 50)
    all_files = find_python_files("src")
    all_files += find_python_files("tests")

    import_changes = 0
    for file_path in all_files:
        import_changes += update_imports_in_file(file_path, dry_run)
    print(f"\n  Total: {import_changes} import(s) mis à jour\n")

    # Résumé
    print("=" * 50)
    print("RÉSUMÉ")
    print("=" * 50)
    print(f"  Fichiers fusionnés: {merged_count}")
    print(f"  Fichiers renommés: {renamed_count}")
    print(f"  Imports mis à jour: {import_changes}")

    if dry_run:
        print("\n[DRY RUN] Aucune modification effectuée. Relancez sans --dry-run pour appliquer.")
    else:
        print("\n✓ Toutes les modifications ont été appliquées.")


if __name__ == "__main__":
    main()
