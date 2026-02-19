"""
Optimized script to rename render_* references in tests/ directory.
Processes each file once with all replacements.
"""

import os
import re
from pathlib import Path

ROOT = Path(r"d:\Projet_streamlit\assistant_matanne")
SRC_MODULES = ROOT / "src" / "modules"
TESTS_DIR = ROOT / "tests"

EXCLUDE_PATTERNS = {"render_template", "render_mermaid", "renderMermaid", "render_google"}


def find_afficher_functions(directory):
    functions = set()
    for py_file in directory.rglob("*.py"):
        content = py_file.read_text(encoding="utf-8")
        matches = re.findall(r"def (afficher_\w+)\s*\(", content)
        functions.update(matches)
    return functions


def build_rename_map(afficher_funcs):
    mapping = {}
    for name in afficher_funcs:
        old_name = name.replace("afficher_", "render_", 1)
        if old_name not in EXCLUDE_PATTERNS:
            mapping[old_name] = name
    return mapping


def main():
    print("=" * 60)
    print("RENOMMAGE render_* -> afficher_* dans tests/")
    print("=" * 60)

    afficher_funcs = find_afficher_functions(SRC_MODULES)
    rename_map = build_rename_map(afficher_funcs)
    print(f"  {len(rename_map)} fonctions dans le mapping")

    # Build a single compiled regex with all render_ names
    # Sort by length descending to match longest first
    sorted_names = sorted(rename_map.keys(), key=len, reverse=True)
    pattern = re.compile(r"\b(" + "|".join(re.escape(n) for n in sorted_names) + r")\b")

    test_files = list(TESTS_DIR.rglob("*.py"))
    print(f"  {len(test_files)} fichiers de tests")

    total = 0
    files_modified = 0

    for py_file in test_files:
        content = py_file.read_text(encoding="utf-8")

        def replacer(match):
            return rename_map[match.group(0)]

        new_content, count = pattern.subn(replacer, content)

        if count > 0:
            py_file.write_text(new_content, encoding="utf-8")
            total += count
            files_modified += 1
            rel = os.path.relpath(str(py_file), ROOT)
            print(f"  [OK] {rel} ({count}x)")

    print(f"\n{'=' * 60}")
    print(f"[DONE] {total} remplacements dans {files_modified} fichiers")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
