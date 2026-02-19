"""
Script to rename render_* references in tests/ directory.
Uses the afficher_* functions already defined in src/modules/ to build the mapping.
"""

import os
import re
from pathlib import Path

ROOT = Path(r"d:\Projet_streamlit\assistant_matanne")
SRC_MODULES = ROOT / "src" / "modules"
TESTS_DIR = ROOT / "tests"

EXCLUDE_PATTERNS = {"render_template", "render_mermaid", "renderMermaid", "render_google"}


def find_afficher_functions(directory):
    """Find all afficher_* function definitions to derive the rename mapping."""
    functions = set()
    for py_file in directory.rglob("*.py"):
        content = py_file.read_text(encoding="utf-8")
        matches = re.findall(r"def (afficher_\w+)\s*\(", content)
        functions.update(matches)
    return functions


def build_rename_map(afficher_funcs):
    """Build old -> new mapping from afficher_* functions."""
    mapping = {}
    for name in afficher_funcs:
        old_name = name.replace("afficher_", "render_", 1)
        if old_name not in EXCLUDE_PATTERNS:
            mapping[old_name] = name
    return mapping


def rename_in_file(filepath, old_name, new_name):
    content = Path(filepath).read_text(encoding="utf-8")
    pattern = re.compile(r"\b" + re.escape(old_name) + r"\b")
    new_content, count = pattern.subn(new_name, content)
    if count > 0:
        Path(filepath).write_text(new_content, encoding="utf-8")
    return count


def main():
    print("=" * 60)
    print("RENOMMAGE render_* -> afficher_* dans tests/")
    print("=" * 60)

    # Build mapping from existing afficher_* definitions
    afficher_funcs = find_afficher_functions(SRC_MODULES)
    rename_map = build_rename_map(afficher_funcs)

    print(f"  {len(rename_map)} fonctions dans le mapping")

    # Collect test files
    test_files = list(TESTS_DIR.rglob("*.py"))
    print(f"  {len(test_files)} fichiers de tests a traiter")

    # Apply renames
    total = 0
    files_modified = set()

    for old_name, new_name in sorted(rename_map.items()):
        for py_file in test_files:
            filepath = str(py_file)
            count = rename_in_file(filepath, old_name, new_name)
            if count > 0:
                total += count
                files_modified.add(filepath)
                rel = os.path.relpath(filepath, ROOT)
                print(f"  [OK] {rel}: {old_name} -> {new_name} ({count}x)")

    print(f"\n{'=' * 60}")
    print(f"[DONE] {total} remplacements dans {len(files_modified)} fichiers")
    print(f"{'=' * 60}")

    # Check remaining
    remaining_count = 0
    for py_file in test_files:
        content = py_file.read_text(encoding="utf-8")
        for old_name in rename_map:
            if re.search(r"\b" + re.escape(old_name) + r"\b", content):
                remaining_count += 1
                rel = os.path.relpath(str(py_file), ROOT)
                print(f"  [WARN] Still has {old_name} in {rel}")

    if remaining_count == 0:
        print("[OK] All render_* references updated in tests!")
    else:
        print(f"[WARN] {remaining_count} remaining references")


if __name__ == "__main__":
    main()
