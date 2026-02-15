"""
Migration Script: Feature-First Structure
==========================================
Moves from ui/logic separation to feature-first flat structure.

Before: module/ui/feature/ + module/logic/feature_logic.py
After:  module/feature/   + module/feature/utils.py

Usage: python scripts/migrate_feature_first.py
"""

import os
import re
import shutil
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
MODULES_PATH = PROJECT_ROOT / "src" / "modules"

# Track all changes for import updates
MOVED_FILES: dict[str, str] = {}  # old_path -> new_path


def git_mv(src: str, dst: str) -> bool:
    """Move file using git mv for history preservation."""
    try:
        # Ensure destination directory exists
        dst_dir = os.path.dirname(dst)
        if dst_dir and not os.path.exists(dst_dir):
            os.makedirs(dst_dir)

        result = subprocess.run(
            ["git", "mv", src, dst], capture_output=True, text=True, cwd=PROJECT_ROOT
        )
        if result.returncode == 0:
            print(f"   {src}  {dst}")
            return True
        else:
            # Try regular move if git mv fails
            shutil.move(src, dst)
            print(f"   {src}  {dst} (non-git)")
            return True
    except Exception as e:
        print(f"   {src}: {e}")
        return False


def migrate_module(module_name: str):
    """Migrate a single module to feature-first structure."""
    module_path = MODULES_PATH / module_name
    ui_path = module_path / "ui"
    logic_path = module_path / "logic"

    if not module_path.exists():
        print(f" Module {module_name} not found")
        return

    print(f"\n{'=' * 60}")
    print(f" MIGRATING {module_name.upper()}")
    print(f"{'=' * 60}")

    # Step 1: Move UI subfolders up (they become the main features)
    if ui_path.exists():
        print("\n Moving UI files up...")

        # Move subfolders first
        for item in ui_path.iterdir():
            if item.is_dir() and item.name != "__pycache__":
                # This is a feature subfolder - move it up
                new_path = module_path / item.name
                if not new_path.exists():
                    git_mv(str(item), str(new_path))
                    MOVED_FILES[f"src/modules/{module_name}/ui/{item.name}"] = (
                        f"src/modules/{module_name}/{item.name}"
                    )
                else:
                    print(f"   {new_path} already exists, merging...")
                    for file in item.glob("*.py"):
                        git_mv(str(file), str(new_path / file.name))

        # Move direct files (except __init__.py)
        for file in ui_path.glob("*.py"):
            if file.name != "__init__.py":
                git_mv(str(file), str(module_path / file.name))
                MOVED_FILES[f"src/modules/{module_name}/ui/{file.name}"] = (
                    f"src/modules/{module_name}/{file.name}"
                )

        # Remove empty ui folder
        try:
            # Remove __init__.py and __pycache__
            ui_init = ui_path / "__init__.py"
            if ui_init.exists():
                os.remove(ui_init)
            pycache = ui_path / "__pycache__"
            if pycache.exists():
                shutil.rmtree(pycache)
            if ui_path.exists() and not any(ui_path.iterdir()):
                ui_path.rmdir()
                print("   Removed empty ui/")
        except Exception as e:
            print(f"   Could not remove ui/: {e}")

    # Step 2: Move logic files to their corresponding feature folders
    if logic_path.exists():
        print("\n Moving logic files to features...")

        for file in logic_path.glob("*.py"):
            if file.name == "__init__.py":
                continue

            # Parse logic filename: feature_logic.py -> feature/utils.py
            if file.name.endswith("_logic.py"):
                feature_name = file.name.replace("_logic.py", "")
                feature_dir = module_path / feature_name

                # Check if feature folder exists
                if feature_dir.exists() and feature_dir.is_dir():
                    dest = feature_dir / "utils.py"
                    if not dest.exists():
                        git_mv(str(file), str(dest))
                        MOVED_FILES[f"src/modules/{module_name}/logic/{file.name}"] = (
                            f"src/modules/{module_name}/{feature_name}/utils.py"
                        )
                    else:
                        print(f"   {dest} exists, merging content needed")
                else:
                    # No matching folder - move to root as utils
                    dest = module_path / f"{feature_name}_utils.py"
                    git_mv(str(file), str(dest))
                    MOVED_FILES[f"src/modules/{module_name}/logic/{file.name}"] = (
                        f"src/modules/{module_name}/{feature_name}_utils.py"
                    )

            elif file.name == "schemas.py":
                # Special case: schemas stays at module root
                git_mv(str(file), str(module_path / "schemas.py"))
                MOVED_FILES[f"src/modules/{module_name}/logic/schemas.py"] = (
                    f"src/modules/{module_name}/schemas.py"
                )

            else:
                # Other logic files move to module root
                git_mv(str(file), str(module_path / file.name))
                MOVED_FILES[f"src/modules/{module_name}/logic/{file.name}"] = (
                    f"src/modules/{module_name}/{file.name}"
                )

        # Handle logic subfolders (like jeux/logic/paris/)
        for item in logic_path.iterdir():
            if item.is_dir() and item.name != "__pycache__":
                feature_dir = module_path / item.name
                if feature_dir.exists():
                    # Merge into existing feature folder
                    for file in item.glob("*.py"):
                        dest = feature_dir / file.name
                        if not dest.exists():
                            git_mv(str(file), str(dest))
                else:
                    # Move entire folder
                    git_mv(str(item), str(feature_dir))

        # Remove empty logic folder
        try:
            logic_init = logic_path / "__init__.py"
            if logic_init.exists():
                os.remove(logic_init)
            pycache = logic_path / "__pycache__"
            if pycache.exists():
                shutil.rmtree(pycache)
            if logic_path.exists() and not any(logic_path.iterdir()):
                logic_path.rmdir()
                print("   Removed empty logic/")
        except Exception as e:
            print(f"   Could not remove logic/: {e}")


def update_imports_in_file(filepath: Path):
    """Update imports in a single file."""
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return False

    original = content

    # Pattern replacements for imports
    replacements = [
        # Remove .ui. from imports
        (r"from (src\.modules\.\w+)\.ui\.(\w+)", r"from \1.\2"),
        (r"from (src\.modules\.\w+)\.ui import", r"from \1 import"),
        # Remove .logic. from imports
        (r"from (src\.modules\.\w+)\.logic\.(\w+)_logic import", r"from \1.\2.utils import"),
        (r"from (src\.modules\.\w+)\.logic import (\w+)_logic", r"from \1.\2 import utils"),
        (r"from (src\.modules\.\w+)\.logic\.(\w+) import", r"from \1.\2 import"),
        (r"from (src\.modules\.\w+)\.logic import", r"from \1 import"),
        # Relative imports within modules
        (r"from \.\.ui\.(\w+) import", r"from ..\1 import"),
        (r"from \.\.logic\.(\w+)_logic import", r"from ..\1.utils import"),
        (r"from \.\.logic import", r"from .. import"),
        (r"from \.ui\.", r"from ."),
        (r"from \.logic\.", r"from ."),
    ]

    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)

    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def update_all_imports():
    """Update imports across the entire codebase."""
    print(f"\n{'=' * 60}")
    print(" UPDATING IMPORTS")
    print(f"{'=' * 60}\n")

    updated = 0
    for root, dirs, files in os.walk(PROJECT_ROOT / "src"):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in files:
            if f.endswith(".py"):
                filepath = Path(root) / f
                if update_imports_in_file(filepath):
                    print(f"   {filepath.relative_to(PROJECT_ROOT)}")
                    updated += 1

    # Also update tests
    for root, dirs, files in os.walk(PROJECT_ROOT / "tests"):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in files:
            if f.endswith(".py"):
                filepath = Path(root) / f
                if update_imports_in_file(filepath):
                    print(f"   {filepath.relative_to(PROJECT_ROOT)}")
                    updated += 1

    print(f"\n Updated {updated} files")


def update_module_init(module_name: str):
    """Update the module's __init__.py for new structure."""
    module_path = MODULES_PATH / module_name
    init_path = module_path / "__init__.py"

    if not init_path.exists():
        return

    # Find all feature folders (directories with __init__.py)
    features = []
    for item in module_path.iterdir():
        if item.is_dir() and (item / "__init__.py").exists():
            if item.name not in ["__pycache__", "ui", "logic"]:
                features.append(item.name)

    # Find all .py files at module root (except __init__.py)
    root_files = []
    for f in module_path.glob("*.py"):
        if f.name != "__init__.py":
            root_files.append(f.stem)

    # Generate new __init__.py content
    content = f'''"""Module {module_name.capitalize()} - Structure Feature-First."""

# Lazy loading pour performance
_SUBMODULES = {{
'''

    for feature in sorted(features):
        content += f'    "{feature}": ".{feature}",\n'

    for rf in sorted(root_files):
        content += f'    "{rf}": ".{rf}",\n'

    content += '''}

__all__ = list(_SUBMODULES.keys())


def __getattr__(name: str):
    """Chargement diffr des sous-modules."""
    if name in _SUBMODULES:
        import importlib
        return importlib.import_module(_SUBMODULES[name], __name__)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
'''

    with open(init_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"   Updated {module_name}/__init__.py")


def rename_common_to_utils():
    """Rename _common.py files to utils.py where appropriate."""
    print(f"\n{'=' * 60}")
    print(" RENAMING _common.py  utils.py")
    print(f"{'=' * 60}\n")

    for common_file in MODULES_PATH.glob("**/_common.py"):
        utils_file = common_file.parent / "utils.py"
        if not utils_file.exists():
            git_mv(str(common_file), str(utils_file))
        else:
            print(f"   {utils_file} exists, keeping _common.py")


def main():
    print("\n" + "== " * 20)
    print("MIGRATION FEATURE-FIRST")
    print("== " * 20)

    # Migrate each module
    modules = ["cuisine", "famille", "maison", "jeux", "planning", "outils"]

    for module in modules:
        migrate_module(module)

    # Rename _common.py files
    rename_common_to_utils()

    # Update all imports
    update_all_imports()

    # Update module __init__.py files
    print(f"\n{'=' * 60}")
    print(" UPDATING MODULE __init__.py")
    print(f"{'=' * 60}\n")
    for module in modules:
        update_module_init(module)

    print("\n" + "=" * 60)
    print(" MIGRATION COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print('1. Run: python -c "from src.modules import cuisine, famille" to verify')
    print("2. Run: pytest tests/ -x -q to check tests")
    print("3. Review git diff for any issues")


if __name__ == "__main__":
    main()
