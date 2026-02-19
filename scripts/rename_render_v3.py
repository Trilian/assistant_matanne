"""
Script de renommage v3 - Optimisé: un seul pass par fichier.
Traite tests/ uniquement (src/ déjà fait par v1 et v2).
"""

import re
from pathlib import Path

ROOT = Path(r"d:\Projet_streamlit\assistant_matanne")


def build_mapping() -> dict[str, str]:
    """Construit le mapping render_xxx -> afficher_xxx depuis src/modules/."""
    modules_dir = ROOT / "src" / "modules"

    renames = {}
    for py_file in modules_dir.rglob("*.py"):
        content = py_file.read_text(encoding="utf-8")
        # Public afficher_*
        for m in re.findall(r"def (afficher_\w+)\s*\(", content):
            old = m.replace("afficher_", "render_", 1)
            renames[old] = m
        # Private _afficher_*
        for m in re.findall(r"def (_afficher_\w+)\s*\(", content):
            old = m.replace("_afficher_", "_render_", 1)
            renames[old] = m

    # Alias exports from ui/views
    renames.update(
        {
            "render_login_form": "afficher_login_form",
            "render_user_menu": "afficher_user_menu",
            "render_profile_settings": "afficher_profile_settings",
            "render_activity_timeline": "afficher_activity_timeline",
            "render_user_activity": "afficher_user_activity",
            "render_activity_stats": "afficher_activity_stats",
        }
    )

    return renames


def process_file(filepath: Path, pattern: re.Pattern, renames: dict) -> int:
    """Process a single file: find all render_xxx matches, replace with afficher_xxx."""
    content = filepath.read_text(encoding="utf-8")

    count = 0

    def replacer(match):
        nonlocal count
        word = match.group(0)
        if word in renames:
            count += 1
            return renames[word]
        return word

    new_content = pattern.sub(replacer, content)

    if count > 0:
        filepath.write_text(new_content, encoding="utf-8")

    return count


def main():
    renames = build_mapping()
    print(f"{len(renames)} mappings construits")

    # Build a single regex that matches any render_xxx word boundary
    # Sort by length (longest first) to avoid partial matches
    sorted_names = sorted(renames.keys(), key=len, reverse=True)
    escaped = [re.escape(name) for name in sorted_names]
    pattern = re.compile(r"\b(" + "|".join(escaped) + r")\b")

    tests_dir = ROOT / "tests"
    total = 0
    files_modified = 0

    for py_file in tests_dir.rglob("*.py"):
        count = process_file(py_file, pattern, renames)
        if count > 0:
            total += count
            files_modified += 1
            print(f"  {py_file.relative_to(ROOT)}: {count}")

    print(f"\nTotal: {total} remplacements dans {files_modified} fichiers")

    # Verify
    remaining = 0
    for py_file in tests_dir.rglob("*.py"):
        content = py_file.read_text(encoding="utf-8")
        for old_name in renames:
            if re.search(r"\b" + re.escape(old_name) + r"\b", content):
                remaining += 1
                break
    print(f"Fichiers tests avec render_* restants: {remaining}")


if __name__ == "__main__":
    main()
