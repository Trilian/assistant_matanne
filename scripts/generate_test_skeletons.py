#!/usr/bin/env python3
"""
Générateur automatique de squelettes de tests pour src/modules/

Ce script analyse chaque fichier Python dans src/modules/ et génére
un fichier de test correspondant si celui-ci n'existe pas déjà.

Usage:
    python scripts/generate_test_skeletons.py --dry-run  # Prévisualiser
    python scripts/generate_test_skeletons.py            # Générer les tests
"""

import ast
import os
import sys
from typing import Any


def extract_functions_and_classes(filepath: str) -> dict[str, Any]:
    """Extrait les fonctions et classes d'un fichier Python."""
    with open(filepath, encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            return {"functions": [], "classes": [], "error": True}

    result = {"functions": [], "classes": [], "error": False}

    # Collect class methods to exclude them from top-level functions
    class_methods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    class_methods.add(id(item))

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef):
            # Skip class methods
            if id(node) in class_methods:
                continue
            # Fonction publique (pas _private)
            if not node.name.startswith("_"):
                result["functions"].append(
                    {
                        "name": node.name,
                        "args": [arg.arg for arg in node.args.args if arg.arg != "self"],
                        "docstring": ast.get_docstring(node) or "",
                    }
                )

        elif isinstance(node, ast.ClassDef):
            methods = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and not item.name.startswith("_"):
                    methods.append(item.name)

            result["classes"].append(
                {
                    "name": node.name,
                    "methods": methods,
                    "docstring": ast.get_docstring(node) or "",
                }
            )

    return result


def generate_test_content(module_path: str, module_name: str, extracted: dict[str, Any]) -> str:
    """Génère le contenu du fichier de test."""

    # Import path - normaliser les slashes
    module_path = module_path.replace("\\", "/")
    import_path = module_path.replace("/", ".").replace(".py", "")

    lines = [
        '"""',
        f"Tests pour {module_path}",
        "",
        "Tests générés automatiquement - à compléter avec la logique de test.",
        '"""',
        "",
        "import pytest",
        "from unittest.mock import Mock, patch, MagicMock",
        "",
    ]

    # Generate imports for each function/class
    imports = []
    if extracted["functions"]:
        func_names = [f["name"] for f in extracted["functions"][:10]]  # Limit to 10
        imports.extend(func_names)

    if extracted["classes"]:
        class_names = [c["name"] for c in extracted["classes"][:5]]
        imports.extend(class_names)

    if imports:
        if len(imports) <= 3:
            lines.append(f'from {import_path} import {", ".join(imports)}')
        else:
            lines.append(f"from {import_path} import (")
            for imp in imports:
                lines.append(f"    {imp},")
            lines.append(")")
    else:
        lines.append(f"# from {import_path} import ...")

    class_name = f'Test{module_name.title().replace("_", "")}'
    lines.extend(
        ["", "", f"class {class_name}:", f'    """Tests pour le module {module_name}"""', ""]
    )

    # Generate test methods for functions
    for func in extracted["functions"][:10]:
        func_name = func["name"]
        test_name = f"test_{func_name}"

        lines.extend(
            [
                f"    def {test_name}(self):",
                f'        """Test de la fonction {func_name}"""',
                "        # TODO: Implémenter le test",
                "        pass",
                "",
            ]
        )

    # Generate test methods for classes
    for cls in extracted["classes"][:5]:
        class_name_test = cls["name"]

        # Test class creation
        lines.extend(
            [
                f"    def test_{class_name_test.lower()}_creation(self):",
                f'        """Test de création de {class_name_test}"""',
                "        # TODO: Implémenter le test",
                "        pass",
                "",
            ]
        )

        # Test each method
        for method in cls["methods"][:5]:
            lines.extend(
                [
                    f"    def test_{class_name_test.lower()}_{method}(self):",
                    f'        """Test de {class_name_test}.{method}"""',
                    "        # TODO: Implémenter le test",
                    "        pass",
                    "",
                ]
            )

    # If no functions or classes found
    if not extracted["functions"] and not extracted["classes"]:
        lines.extend(
            [
                "    def test_import(self):",
                '        """Test que le module peut être importé"""',
                f"        import {import_path}",
                "        assert True",
                "",
            ]
        )

    return "\n".join(lines)


def get_test_path(source_path: str, tests_root: str = "tests/modules") -> str:
    """Calcule le chemin du fichier de test pour un fichier source."""
    # Exemple: src/modules/cuisine/courses/utils.py -> tests/modules/cuisine/courses/test_utils.py
    # Normaliser les séparateurs
    source_path = source_path.replace("\\", "/")
    rel_path = source_path.replace("src/modules/", "")
    dir_path = os.path.dirname(rel_path)
    file_name = os.path.basename(rel_path)
    test_file_name = f"test_{file_name}"

    return os.path.join(tests_root, dir_path, test_file_name).replace("\\", "/")


def find_source_files(base_dir: str = "src/modules") -> list[str]:
    """Trouve tous les fichiers Python source."""
    files = []
    for root, dirs, filenames in os.walk(base_dir):
        dirs[:] = [d for d in dirs if d not in ["__pycache__", ".git"]]
        for f in filenames:
            if f.endswith(".py") and f != "__init__.py":
                files.append(os.path.join(root, f))
    return sorted(files)


def main():
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("=== DRY RUN MODE ===\n")

    source_files = find_source_files()
    print(f"Fichiers source trouvés: {len(source_files)}")

    created = 0
    skipped = 0
    errors = 0

    for source_path in source_files:
        test_path = get_test_path(source_path)

        # Skip if test already exists
        if os.path.exists(test_path):
            skipped += 1
            continue

        # Extract functions and classes
        extracted = extract_functions_and_classes(source_path)

        if extracted["error"]:
            print(f"  ERROR: Syntax error in {source_path}")
            errors += 1
            continue

        # Generate test content
        module_name = os.path.basename(source_path).replace(".py", "")
        content = generate_test_content(source_path, module_name, extracted)

        if dry_run:
            print(f"  Would create: {test_path}")
            print(
                f"    - {len(extracted['functions'])} functions, {len(extracted['classes'])} classes"
            )
        else:
            # Create directory if needed
            os.makedirs(os.path.dirname(test_path), exist_ok=True)

            # Create __init__.py if missing
            init_path = os.path.join(os.path.dirname(test_path), "__init__.py")
            if not os.path.exists(init_path):
                with open(init_path, "w", encoding="utf-8") as f:
                    f.write("")

            # Write test file
            with open(test_path, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"  Created: {test_path}")

        created += 1

    print(f"\n{'='*50}")
    print("RÉSUMÉ")
    print(f"{'='*50}")
    print(f"  Fichiers source: {len(source_files)}")
    print(f"  Tests existants (ignorés): {skipped}")
    print(f"  Tests créés: {created}")
    print(f"  Erreurs: {errors}")

    if dry_run:
        print("\n[DRY RUN] Aucun fichier créé. Relancer sans --dry-run pour générer.")


if __name__ == "__main__":
    main()
