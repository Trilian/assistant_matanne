"""
Script de renommage v2 - Finalise la migration render_* → afficher_*

Phase 1: Renomme les fonctions _render_* privées dans src/modules/
Phase 2: Met à jour les alias/exports dans src/ui/views/
Phase 3: Met à jour toutes les références render_* dans tests/

Sécurité:
- Utilise des word-boundaries pour les remplacements
- Exclut les noms qui ne doivent pas être renommés
- Rapport détaillé à la fin
"""

import os
import re
from pathlib import Path

ROOT = Path(r"d:\Projet_streamlit\assistant_matanne")

# Noms à NE PAS renommer
EXCLUDE_PATTERNS = {
    "render_template",
    "render_mermaid",
    "renderMermaid",
    "render_google_calendar_config",
    "render_sync_status",
    "render_quick_sync_button",
}


def rename_in_content(content: str, old_name: str, new_name: str) -> tuple[str, int]:
    """Remplace old_name par new_name avec word-boundary."""
    pattern = re.compile(r"\b" + re.escape(old_name) + r"\b")
    new_content, count = pattern.subn(new_name, content)
    return new_content, count


def phase1_private_render():
    """Renomme les fonctions _render_* privées dans src/modules/."""
    print("\n" + "=" * 60)
    print("PHASE 1: Renommer _render_* privés dans src/modules/")
    print("=" * 60)

    modules_dir = ROOT / "src" / "modules"

    # Trouver les définitions _render_*
    private_fns = {}  # old -> new
    for py_file in modules_dir.rglob("*.py"):
        content = py_file.read_text(encoding="utf-8")
        matches = re.findall(r"def (_render_\w+)\s*\(", content)
        for name in matches:
            if name not in EXCLUDE_PATTERNS:
                new_name = name.replace("_render_", "_afficher_", 1)
                private_fns[name] = new_name

    if not private_fns:
        print("  Aucune fonction _render_* privée trouvée.")
        return 0

    print(f"  {len(private_fns)} fonctions privées à renommer:")
    for old, new in sorted(private_fns.items()):
        print(f"    {old} -> {new}")

    # Renommer dans tous les fichiers src/modules/
    total = 0
    for py_file in modules_dir.rglob("*.py"):
        content = py_file.read_text(encoding="utf-8")
        modified = False
        for old_name, new_name in private_fns.items():
            content, count = rename_in_content(content, old_name, new_name)
            if count > 0:
                total += count
                modified = True
        if modified:
            py_file.write_text(content, encoding="utf-8")
            print(f"  [OK] {py_file.relative_to(ROOT)}")

    print(f"  Total Phase 1: {total} remplacements")
    return total


def phase2_aliases():
    """Met à jour les alias/exports render_* dans src/ui/views/."""
    print("\n" + "=" * 60)
    print("PHASE 2: Mettre à jour alias/exports dans src/ui/views/")
    print("=" * 60)

    views_dir = ROOT / "src" / "ui" / "views"
    total = 0

    # Fichiers spécifiques avec des alias render_*
    target_files = [
        views_dir / "__init__.py",
        views_dir / "authentification.py",
        views_dir / "realtime.py",
    ]

    # Aussi le services/core/utilisateur/historique.py qui a render_ exports
    historique = ROOT / "src" / "services" / "core" / "utilisateur" / "historique.py"
    if historique.exists():
        target_files.append(historique)

    # Mappings spécifiques pour les alias dans ui/views
    alias_renames = {
        "render_login_form": "afficher_login_form",
        "render_user_menu": "afficher_user_menu",
        "render_profile_settings": "afficher_profile_settings",
        "render_activity_timeline": "afficher_activity_timeline",
        "render_user_activity": "afficher_user_activity",
        "render_activity_stats": "afficher_activity_stats",
        "render_presence_indicator": "afficher_presence_indicator",
        "render_typing_indicator": "afficher_typing_indicator",
        "render_sync_status": "afficher_sync_status",
        "render_realtime_status": "afficher_realtime_status",
        "render_budget_dashboard": "afficher_budget_dashboard",
        "render_calendar_sync_ui": "afficher_calendar_sync_ui",
    }

    for filepath in target_files:
        if not filepath.exists():
            continue
        content = filepath.read_text(encoding="utf-8")
        modified = False
        for old_name, new_name in alias_renames.items():
            content, count = rename_in_content(content, old_name, new_name)
            if count > 0:
                total += count
                modified = True
        if modified:
            filepath.write_text(content, encoding="utf-8")
            print(f"  [OK] {filepath.relative_to(ROOT)}")

    print(f"  Total Phase 2: {total} remplacements")
    return total


def phase3_tests():
    """Met à jour toutes les références render_* dans tests/."""
    print("\n" + "=" * 60)
    print("PHASE 3: Mettre à jour tests/")
    print("=" * 60)

    tests_dir = ROOT / "tests"

    # Construire le mapping complet depuis src/modules/ (afficher_ fonctions existantes)
    # On cherche toutes les fonctions afficher_* pour reconstruire le mapping inverse
    modules_dir = ROOT / "src" / "modules"

    all_afficher = set()
    for py_file in modules_dir.rglob("*.py"):
        content = py_file.read_text(encoding="utf-8")
        matches = re.findall(r"def (afficher_\w+)\s*\(", content)
        all_afficher.update(matches)
        # Aussi les privées _afficher_*
        matches_priv = re.findall(r"def (_afficher_\w+)\s*\(", content)
        all_afficher.update(matches_priv)

    # Reconstruire old -> new
    renames = {}
    for name in all_afficher:
        if name.startswith("_afficher_"):
            old = name.replace("_afficher_", "_render_", 1)
        else:
            old = name.replace("afficher_", "render_", 1)
        renames[old] = name

    # Ajouter les alias de Phase 2
    renames.update(
        {
            "render_login_form": "afficher_login_form",
            "render_user_menu": "afficher_user_menu",
            "render_profile_settings": "afficher_profile_settings",
            "render_activity_timeline": "afficher_activity_timeline",
            "render_user_activity": "afficher_user_activity",
            "render_activity_stats": "afficher_activity_stats",
            "render_presence_indicator": "afficher_presence_indicator",
            "render_typing_indicator": "afficher_typing_indicator",
            "render_realtime_status": "afficher_realtime_status",
            "render_budget_dashboard": "afficher_budget_dashboard",
        }
    )

    print(f"  {len(renames)} mappings render_ -> afficher_ disponibles")

    # Traiter chaque fichier test
    total = 0
    files_modified = 0

    test_files = list(tests_dir.rglob("*.py"))
    print(f"  {len(test_files)} fichiers de test à scanner")

    for py_file in test_files:
        content = py_file.read_text(encoding="utf-8")
        original = content
        file_count = 0

        for old_name, new_name in renames.items():
            content, count = rename_in_content(content, old_name, new_name)
            file_count += count

        if file_count > 0:
            py_file.write_text(content, encoding="utf-8")
            total += file_count
            files_modified += 1
            print(f"  [OK] {py_file.relative_to(ROOT)}: {file_count} remplacements")

    print(f"  Total Phase 3: {total} remplacements dans {files_modified} fichiers")
    return total


def verify():
    """Vérifie les résultats."""
    print("\n" + "=" * 60)
    print("VERIFICATION FINALE")
    print("=" * 60)

    for dir_name, dir_path in [("src", ROOT / "src"), ("tests", ROOT / "tests")]:
        count = 0
        for py_file in dir_path.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            # Trouver render_ qui ne sont pas dans EXCLUDE
            matches = re.findall(r"\brender_\w+", content)
            valid = [
                m
                for m in matches
                if m not in EXCLUDE_PATTERNS and not m.startswith("render_template")
            ]
            if valid:
                count += len(valid)
                rel = py_file.relative_to(ROOT)
                # Show up to 3 examples
                examples = list(set(valid))[:3]
                print(f"  [{dir_name}] {rel}: {examples}")
        print(f"  {dir_name}/: {count} references render_* restantes")


if __name__ == "__main__":
    print("SCRIPT RENOMMAGE RENDER_* v2")
    print("=" * 60)

    t1 = phase1_private_render()
    t2 = phase2_aliases()
    t3 = phase3_tests()

    print(f"\n{'=' * 60}")
    print(f"TOTAL: {t1 + t2 + t3} remplacements")
    print(f"{'=' * 60}")

    verify()
