"""
Sprint 12 — A3: Rename factory functions from get_*_service → obtenir_*_service.

Strategy:
- Rename the function definition in each service file
- Add a backward-compat alias: get_X_service = obtenir_X_service

This avoids having to update all routes (180+ import sites).
"""

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SERVICES_DIR = ROOT / "src" / "services"

# Mapping: old_name -> new_name
RENAME_MAP: dict[str, str] = {}


def camel_to_snake_french(name: str) -> str:
    """Convert get_xxx_service → obtenir_xxx_service."""
    return name.replace("get_", "obtenir_", 1)


def collect_factory_functions(services_dir: Path) -> dict[Path, list[str]]:
    """Find all get_*_service factory functions in service files."""
    results: dict[Path, list[str]] = {}
    pattern = re.compile(r"^def (get_\w+_service)\s*\(", re.MULTILINE)

    for py_file in services_dir.rglob("*.py"):
        text = py_file.read_text(encoding="utf-8")
        found = pattern.findall(text)
        if found:
            results[py_file] = found
    return results


def rename_in_file(filepath: Path, names: list[str]) -> bool:
    """
    Rename factory functions in a file:
    1. def get_X_service(...) → def obtenir_X_service(...)
    2. Add alias: get_X_service = obtenir_X_service  # aliases Sprint 12 A3
    """
    text = filepath.read_text(encoding="utf-8")
    original = text

    for old_name in names:
        new_name = camel_to_snake_french(old_name)
        RENAME_MAP[old_name] = new_name

        # 1. Rename def line  
        text = re.sub(
            rf"^def {re.escape(old_name)}\b",
            f"def {new_name}",
            text,
            flags=re.MULTILINE,
        )

    # 2. Append aliases at end of file (before last newline)
    alias_lines = []
    for old_name in names:
        new_name = RENAME_MAP[old_name]
        # Only add alias if not already present
        if f"{old_name} = {new_name}" not in text:
            alias_lines.append(f"{old_name} = {new_name}  # alias rétrocompatibilité Sprint 12 A3")

    if alias_lines:
        if not text.endswith("\n"):
            text += "\n"
        text += "\n\n# ─── Aliases rétrocompatibilité (Sprint 12 A3) ───────────────────────────────\n"
        text += "\n".join(alias_lines) + "\n"

    if text != original:
        filepath.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    print("Sprint 12 A3 — Renaming factory functions ...")
    factory_map = collect_factory_functions(SERVICES_DIR)

    total_files = 0
    total_functions = 0
    for filepath, names in sorted(factory_map.items()):
        changed = rename_in_file(filepath, names)
        if changed:
            total_files += 1
            total_functions += len(names)
            rel = filepath.relative_to(ROOT)
            for n in names:
                print(f"  {rel}: {n} → {camel_to_snake_french(n)}")

    print(f"\nDone: {total_functions} functions renamed in {total_files} files.")

    # Verify all files still parse
    print("\nVerifying syntax ...")
    errors = 0
    for filepath in factory_map:
        try:
            ast.parse(filepath.read_text(encoding="utf-8"))
        except SyntaxError as e:
            print(f"  SYNTAX ERROR in {filepath}: {e}")
            errors += 1
    if errors == 0:
        print("  All files parse OK.")
    else:
        print(f"  {errors} files have syntax errors!")
        sys.exit(1)


if __name__ == "__main__":
    main()
