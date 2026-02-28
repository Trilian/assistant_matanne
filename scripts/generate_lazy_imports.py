#!/usr/bin/env python
"""
Auto-génère les dicts _LAZY_IMPORTS pour les packages PEP 562.

Scanne les sous-modules d'un package et construit automatiquement
le mapping {symbole: (module_relatif, attribut)} à partir de __all__.

Usage:
    python scripts/generate_lazy_imports.py              # Vérifie la cohérence
    python scripts/generate_lazy_imports.py --update     # Met à jour les __init__.py
    python scripts/generate_lazy_imports.py --check      # CI: échoue si désynchronisé
"""

from __future__ import annotations

import argparse
import ast
import importlib
import importlib.util
import re
import sys
import textwrap
from pathlib import Path

# Racine du projet
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

# Packages cibles avec leurs __init__.py et exclusions
PACKAGES: list[dict] = [
    {
        "init": SRC / "ui" / "__init__.py",
        "package": "src.ui",
        "submodules": [
            ".tokens",
            ".tokens_semantic",
            ".a11y",
            ".animations",
            ".theme",
            ".registry",
            ".engine",
            ".components",
            ".feedback",
            ".integrations",
            ".tablet",
            ".views",
            ".testing",
            ".fragments",
            ".grid",
            ".state",
            ".keys",
        ],
        "eager_names": set(),  # Noms déjà importés eagerly
    },
    {
        "init": SRC / "core" / "models" / "__init__.py",
        "package": "src.core.models",
        "submodules": [
            ".batch_cooking",
            ".calendrier",
            ".courses",
            ".famille",
            ".finances",
            ".habitat",
            ".inventaire",
            ".jardin",
            ".jeux",
            ".maison",
            ".notifications",
            ".persistent_state",
            ".planning",
            ".recettes",
            ".sante",
            ".systeme",
            ".temps_entretien",
            ".user_preferences",
            ".users",
        ],
        "eager_names": {
            "Base",
            "metadata",
            "utc_now",
            "PrioriteEnum",
            "SaisonEnum",
            "TypeRepasEnum",
            "TypeVersionRecetteEnum",
            "CreeLeMixin",
            "TimestampMixin",
            "charger_tous_modeles",
        },
    },
    {
        "init": SRC / "core" / "__init__.py",
        "package": "src.core",
        "submodules": [
            ".ai",
            ".caching",
            ".config",
            ".db",
            ".resilience",
            ".observability",
            ".bootstrap",
            ".config.validator",
            ".decorators",
            ".exceptions",
            ".lazy_loader",
            ".logging",
            ".monitoring",
            ".state",
            ".storage",
            ".validation",
        ],
        "eager_names": set(),
    },
]


def _resolve_module_path(package: str, relative: str) -> Path:
    """Résout le chemin fichier d'un import relatif."""
    parts = package.split(".")
    base = SRC.parent
    for p in parts:
        base = base / p

    rel_parts = relative.lstrip(".").split(".")
    candidate = base
    for p in rel_parts:
        candidate = candidate / p

    # Essayer package/__init__.py d'abord, puis module.py
    if (candidate / "__init__.py").exists():
        return candidate / "__init__.py"
    elif candidate.with_suffix(".py").exists():
        return candidate.with_suffix(".py")
    return candidate.with_suffix(".py")


def _extract_all_from_file(filepath: Path) -> list[str]:
    """Extrait __all__ d'un fichier Python via AST (sans l'importer)."""
    if not filepath.exists():
        return []

    try:
        tree = ast.parse(filepath.read_text(encoding="utf-8"))
    except SyntaxError:
        return []

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    if isinstance(node.value, ast.List):
                        return [
                            elt.value
                            for elt in node.value.elts
                            if isinstance(elt, ast.Constant | ast.Str)
                        ]
    return []


def _extract_public_names(filepath: Path) -> list[str]:
    """Extrait les noms publics d'un fichier (classes, fonctions, variables)."""
    if not filepath.exists():
        return []

    try:
        tree = ast.parse(filepath.read_text(encoding="utf-8"))
    except SyntaxError:
        return []

    names = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            if not node.name.startswith("_"):
                names.append(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and not target.id.startswith("_"):
                    names.append(target.id)
    return names


def _get_reexported_names(init_path: Path) -> dict[str, str]:
    """Pour un __init__.py de package, extrait les noms réexportés depuis sous-modules."""
    if not init_path.exists():
        return {}

    try:
        tree = ast.parse(init_path.read_text(encoding="utf-8"))
    except SyntaxError:
        return {}

    exports: dict[str, str] = {}
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                real_name = alias.asname or alias.name
                if not real_name.startswith("_") and alias.name != "*":
                    exports[real_name] = alias.name
    return exports


def scan_package(pkg_config: dict) -> dict[str, tuple[str, str]]:
    """Scanne un package et construit le _LAZY_IMPORTS attendu."""
    package = pkg_config["package"]
    eager = pkg_config.get("eager_names", set())
    result: dict[str, tuple[str, str]] = {}

    for submod in pkg_config["submodules"]:
        mod_path = _resolve_module_path(package, submod)

        # Si c'est un package (__init__.py), extraire les réexports
        if mod_path.name == "__init__.py":
            reexports = _get_reexported_names(mod_path)
            all_names = _extract_all_from_file(mod_path)
            if all_names:
                for name in all_names:
                    if name not in eager and not name.startswith("_"):
                        attr = reexports.get(name, name)
                        result[name] = (submod, attr)
            else:
                # Pas de __all__, utiliser les réexports
                for name, attr in reexports.items():
                    if name not in eager and not name.startswith("_"):
                        result[name] = (submod, attr)
        else:
            # Module simple, utiliser __all__ ou noms publics
            all_names = _extract_all_from_file(mod_path)
            if not all_names:
                all_names = _extract_public_names(mod_path)

            for name in all_names:
                if name not in eager and not name.startswith("_"):
                    result[name] = (submod, name)

    return result


def _read_existing_lazy_imports(init_path: Path) -> dict[str, tuple[str, str]]:
    """Lit le _LAZY_IMPORTS existant d'un __init__.py via AST."""
    content = init_path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return {}

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "_LAZY_IMPORTS":
                    if isinstance(node.value, ast.Dict):
                        result = {}
                        for key, val in zip(node.value.keys, node.value.values, strict=False):
                            if isinstance(key, ast.Constant) and isinstance(val, ast.Tuple):  # noqa: UP038
                                elts = val.elts
                                if len(elts) == 2:
                                    mod = elts[0].value if isinstance(elts[0], ast.Constant) else ""
                                    attr = (
                                        elts[1].value if isinstance(elts[1], ast.Constant) else ""
                                    )
                                    result[key.value] = (mod, attr)
                        return result
    return {}


def compare(
    existing: dict[str, tuple[str, str]],
    generated: dict[str, tuple[str, str]],
) -> tuple[set[str], set[str], set[str]]:
    """Compare existant vs généré. Retourne (manquants, obsolètes, différents)."""
    existing_keys = set(existing.keys())
    generated_keys = set(generated.keys())

    manquants = generated_keys - existing_keys
    obsoletes = existing_keys - generated_keys
    differents = {k for k in existing_keys & generated_keys if existing[k] != generated[k]}

    return manquants, obsoletes, differents


def format_lazy_imports_dict(
    imports: dict[str, tuple[str, str]],
) -> str:
    """Formate le dict _LAZY_IMPORTS en code Python lisible."""
    # Grouper par module
    by_module: dict[str, list[tuple[str, str]]] = {}
    for name, (mod, attr) in sorted(imports.items()):
        by_module.setdefault(mod, []).append((name, attr))

    lines = ["_LAZY_IMPORTS: dict[str, tuple[str, str]] = {"]
    for mod in sorted(by_module.keys()):
        # Commentaire de section
        mod_label = mod.lstrip(".").replace(".", "/").replace("_", " ").title()
        lines.append(f"    # ── {mod_label} {'─' * max(1, 45 - len(mod_label))}")
        for name, attr in sorted(by_module[mod]):
            if name == attr:
                lines.append(f'    "{name}": ("{mod}", "{attr}"),')
            else:
                lines.append(f'    "{name}": ("{mod}", "{attr}"),')
    lines.append("}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Vérifie/génère les _LAZY_IMPORTS PEP 562.")
    parser.add_argument("--check", action="store_true", help="Mode CI: échoue si désynchronisé")
    parser.add_argument("--update", action="store_true", help="Met à jour les __init__.py")
    parser.add_argument("--verbose", "-v", action="store_true", help="Affichage détaillé")
    args = parser.parse_args()

    total_issues = 0

    for pkg_config in PACKAGES:
        init_path = pkg_config["init"]
        pkg_name = pkg_config["package"]

        if not init_path.exists():
            print(f"⚠️  {pkg_name}: {init_path} non trouvé")
            continue

        existing = _read_existing_lazy_imports(init_path)
        generated = scan_package(pkg_config)
        manquants, obsoletes, differents = compare(existing, generated)

        if not manquants and not obsoletes and not differents:
            print(f"✅ {pkg_name}: {len(existing)} entrées synchronisées")
            continue

        issues = len(manquants) + len(obsoletes) + len(differents)
        total_issues += issues
        print(f"⚠️  {pkg_name}: {issues} différence(s)")

        if manquants:
            print(f"   ➕ Manquants ({len(manquants)}):")
            for name in sorted(manquants):
                mod, attr = generated[name]
                print(f"      {name} → ({mod}, {attr})")

        if obsoletes:
            print(f"   ➖ Obsolètes ({len(obsoletes)}):")
            for name in sorted(obsoletes):
                print(f"      {name}")

        if differents:
            print(f"   🔄 Différents ({len(differents)}):")
            for name in sorted(differents):
                print(f"      {name}: {existing[name]} → {generated[name]}")

        if args.update:
            print(f"   📝 Mise à jour {init_path}...")
            content = init_path.read_text(encoding="utf-8")
            new_dict = format_lazy_imports_dict(
                {**generated, **{k: existing[k] for k in obsoletes}}
            )
            # Note: La mise à jour automatique du fichier nécessite un
            # remplacement regex du bloc _LAZY_IMPORTS existant.
            # Pour l'instant on affiche le dict généré.
            print(textwrap.indent(new_dict, "   "))

    if args.check and total_issues > 0:
        print(f"\n❌ {total_issues} différence(s) trouvée(s). Exécutez:")
        print("   python scripts/generate_lazy_imports.py --update")
        return 1

    if total_issues == 0:
        print("\n✅ Tous les packages PEP 562 sont synchronisés.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
