"""
Script v4 - Approche simple: remplacer TOUT render_ -> afficher_ dans tests/
avec exclusion des patterns qui ne doivent pas changer.
"""

import re
from pathlib import Path

ROOT = Path(r"d:\Projet_streamlit\assistant_matanne")

# Patterns à ne PAS remplacer
EXCLUDE = {
    "render_template",
    "render_mermaid",
    "renderMermaid",
}


def process_file(filepath: Path) -> int:
    """Replace all render_ with afficher_ except exclusions."""
    content = filepath.read_text(encoding="utf-8")

    # Simple: replace render_ -> afficher_ partout, sauf dans EXCLUDE
    def replacer(match):
        full = match.group(0)
        if full in EXCLUDE:
            return full
        return full.replace("render_", "afficher_", 1)

    # Match render_xxx (word boundary)
    new_content, count = re.subn(r"\brender_\w+", replacer, content)

    # Also handle _render_ (private methods)
    def private_replacer(match):
        full = match.group(0)
        return full.replace("_render_", "_afficher_", 1)

    new_content, count2 = re.subn(r"\b_render_\w+", private_replacer, new_content)

    total = count + count2

    # Also handle RENDER_ in constants (like RENDER_ADD_ACTIVITY)
    def const_replacer(match):
        full = match.group(0)
        return full.replace("RENDER_", "AFFICHER_", 1)

    new_content, count3 = re.subn(r"\bRENDER_\w+", const_replacer, new_content)
    total += count3

    if total > 0:
        filepath.write_text(new_content, encoding="utf-8")

    return total


def main():
    tests_dir = ROOT / "tests"
    total = 0
    files_modified = 0

    for py_file in tests_dir.rglob("*.py"):
        count = process_file(py_file)
        if count > 0:
            total += count
            files_modified += 1
            print(f"  {py_file.relative_to(ROOT)}: {count}")

    print(f"\nTotal: {total} remplacements dans {files_modified} fichiers")

    # Also process src/ui/views/ for remaining aliases
    views_dir = ROOT / "src" / "ui" / "views"
    for py_file in views_dir.rglob("*.py"):
        count = process_file(py_file)
        if count > 0:
            total += count
            print(f"  {py_file.relative_to(ROOT)}: {count}")

    # Verify
    remaining = 0
    for py_file in tests_dir.rglob("*.py"):
        content = py_file.read_text(encoding="utf-8")
        matches = re.findall(r"\brender_\w+", content)
        clean = [m for m in matches if m not in EXCLUDE]
        if clean:
            remaining += len(clean)
    print(f"\nrender_* restants dans tests/: {remaining}")


if __name__ == "__main__":
    main()
