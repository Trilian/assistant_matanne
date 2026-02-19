"""
Script de renommage automatique render_* → afficher_* dans src/modules/.

Stratégie:
- Scanne tous les fichiers .py sous src/modules/ et src/ui/
- Pour chaque fichier, remplace 'render_' par 'afficher_' dans:
  1. Définitions de fonctions: `def render_xxx(`
  2. Appels de fonctions: `render_xxx(`
  3. Références dans imports: `from .xxx import render_xxx`
  4. Chaînes dans __all__: `"render_xxx"`
  5. Docstrings et commentaires (best effort)

Exclusions:
- Ne touche PAS src/ui/ (design system - déjà en français)
- Ne touche PAS src/api/ (API layer)
- Ne touche PAS les tests/ (les tests seront mis à jour séparément)
"""

import os
import re
from pathlib import Path

ROOT = Path(r"d:\Projet_streamlit\assistant_matanne")
SRC_MODULES = ROOT / "src" / "modules"
TESTS_DIR = ROOT / "tests"

# Noms de fonctions à NE PAS renommer (proviennent d'autres couches)
EXCLUDE_NAMES = {
    "render_template",
    "render_mermaid",
    "renderMermaid",
    "render_google_calendar_config",  # déjà renommé
    "render_sync_status",  # déjà renommé
    "render_quick_sync_button",  # déjà renommé
}


def find_render_functions(directory: Path) -> dict[str, list[str]]:
    """Trouve toutes les fonctions render_* définies dans chaque fichier."""
    functions_by_file = {}

    for py_file in directory.rglob("*.py"):
        content = py_file.read_text(encoding="utf-8")
        # Trouver les définitions de fonctions render_*
        matches = re.findall(r"def (render_\w+)\s*\(", content)
        matches = [m for m in matches if m not in EXCLUDE_NAMES]
        if matches:
            functions_by_file[str(py_file)] = list(set(matches))

    return functions_by_file


def make_afficher_name(render_name: str) -> str:
    """Convertit render_xxx en afficher_xxx."""
    return render_name.replace("render_", "afficher_", 1)


def rename_in_file(filepath: str, old_name: str, new_name: str) -> int:
    """Remplace toutes les occurrences de old_name par new_name dans un fichier.
    Retourne le nombre de remplacements effectués."""
    content = Path(filepath).read_text(encoding="utf-8")

    # Utiliser un pattern word-boundary pour éviter les faux positifs
    # Match: render_xxx suivi de ( ou , ou ) ou espace ou fin de ligne ou "
    pattern = re.compile(r"\b" + re.escape(old_name) + r"\b")

    new_content, count = pattern.subn(new_name, content)

    if count > 0:
        Path(filepath).write_text(new_content, encoding="utf-8")

    return count


def main():
    print("=" * 60)
    print("RENOMMAGE render_* -> afficher_* dans src/modules/ + tests/")
    print("=" * 60)

    # 1. Trouver toutes les fonctions render_* définies
    functions_by_file = find_render_functions(SRC_MODULES)

    all_renames = {}  # old_name -> new_name
    for filepath, func_names in functions_by_file.items():
        for name in func_names:
            new_name = make_afficher_name(name)
            all_renames[name] = new_name

    print(f"\n  {len(all_renames)} fonctions a renommer:")
    for old, new in sorted(all_renames.items()):
        print(f"  {old} -> {new}")

    # 2. Collecter tous les fichiers Python à traiter (modules + tests)
    all_py_files = list(SRC_MODULES.rglob("*.py")) + list(TESTS_DIR.rglob("*.py"))
    print(f"\n[SCAN] {len(all_py_files)} fichiers a scanner dans src/modules/ + tests/")

    # 3. Effectuer les remplacements
    total_replacements = 0
    files_modified = set()

    for old_name, new_name in sorted(all_renames.items()):
        for py_file in all_py_files:
            filepath = str(py_file)
            count = rename_in_file(filepath, old_name, new_name)
            if count > 0:
                total_replacements += count
                files_modified.add(filepath)
                rel = os.path.relpath(filepath, ROOT)
                print(f"  [OK] {rel}: {old_name} -> {new_name} ({count}x)")

    print(f"\n{'=' * 60}")
    print(f"[DONE] {total_replacements} remplacements dans {len(files_modified)} fichiers")
    print(f"{'=' * 60}")

    # 4. Vérifier qu'il ne reste plus de render_
    remaining = 0
    for py_file in all_py_files:
        content = py_file.read_text(encoding="utf-8")
        matches = re.findall(r"def render_\w+\s*\(", content)
        matches = [m for m in matches if not any(ex in m for ex in EXCLUDE_NAMES)]
        if matches:
            remaining += len(matches)
            rel = os.path.relpath(str(py_file), ROOT)
            print(f"  [WARN] RESTANT dans {rel}: {matches}")

    if remaining == 0:
        print("\n[OK] Aucune fonction render_* restante!")
    else:
        print(f"\n[WARN] {remaining} fonctions render_* encore presentes!")


if __name__ == "__main__":
    main()
