#!/usr/bin/env python3
"""Régénère INIT_COMPLET.sql depuis les fichiers sql/schema/*.sql.

Ce script est le pendant de split_init_sql.py. Il concatène tous les
fichiers du répertoire sql/schema/ dans le bon ordre pour reconstruire
sql/INIT_COMPLET.sql.

Usage:
    python scripts/db/regenerate_init.py [--check] [--output PATH]

Options:
    --check       Vérifie que INIT_COMPLET.sql est à jour sans réécrire
    --output      Chemin de sortie (défaut: sql/INIT_COMPLET.sql)

Le fichier résultant est fonctionnellement équivalent à l'original :
il peut être exécuté directement dans Supabase SQL Editor ou psql.

Workflow:
    1. Modifier un fichier dans sql/schema/
    2. Exécuter: python scripts/db/regenerate_init.py
    3. Vérifier: python scripts/db/regenerate_init.py --check
    4. Appliquer en base: psql $DATABASE_URL -f sql/INIT_COMPLET.sql
"""

import argparse
import hashlib
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SCHEMA_DIR = ROOT / "sql" / "schema"
DEFAULT_OUTPUT = ROOT / "sql" / "INIT_COMPLET.sql"

# Ordre de concaténation des fichiers (numérotation préfixe comme ordre naturel)
# Les fichiers sont triés alphabétiquement par nom, ce qui respecte l'ordre numérique.
# Pour garantir la bonne gestion des dépendances FK, l'ordre des domaines est:
#   systeme → cuisine → famille → maison (06a-06e) → habitat → jeux → notifications → finances → utilitaires

EXPECTED_FILES = [
    "01_extensions.sql",       # BEGIN; extensions
    "02_functions.sql",        # Fonctions trigger + helpers
    "03_systeme.sql",          # Tables système (FK source pour beaucoup d'autres)
    "04_cuisine.sql",          # Tables cuisine
    "05_famille.sql",          # Tables famille (dépend de systeme)
    "06a_projets.sql",         # Maison: projets & routines
    "06b_entretien.sql",       # Maison: entretien & organisation
    "06c_jardin.sql",          # Maison: jardin & autonomie
    "06d_equipements.sql",     # Maison: équipements & travaux
    "06e_energie.sql",         # Maison: énergie & charges
    "07_habitat.sql",          # Tables habitat (dépend de maison)
    "08_jeux.sql",             # Tables jeux
    "09_notifications.sql",    # Tables notifications (dépend de systeme)
    "10_finances.sql",         # Tables finances (dépend de systeme)
    "11_utilitaires.sql",      # Tables utilitaires
    "12_triggers.sql",         # Triggers modifie_le (après toutes les tables)
    "13_views.sql",            # Vues (après toutes les tables)
    "14_indexes.sql",          # Index supplémentaires
    "15_rls_policies.sql",     # Row Level Security
    "16_seed_data.sql",        # Données de référence
    "99_footer.sql",           # COMMIT + vérification finale
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="Vérifier sans réécrire")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Fichier de sortie")
    parser.add_argument("--schema-dir", default=str(SCHEMA_DIR), help="Répertoire source")
    return parser.parse_args()


def sha256_of_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_header(schema_dir: Path, files: list[Path]) -> str:
    """Génère l'en-tête du fichier INIT_COMPLET.sql régénéré."""
    total_lines = sum(f.read_text(encoding="utf-8").count("\n") for f in files)
    return f"""\
-- ============================================================================
-- ASSISTANT MATANNE — SCRIPT D'INITIALISATION COMPLET
-- ============================================================================
-- Version    : 3.1 (régénéré automatiquement)
-- Généré le  : {datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')}
-- Source     : sql/schema/*.sql ({len(files)} fichiers, ~{total_lines} lignes)
-- Cible      : Supabase PostgreSQL
-- ============================================================================
--
-- ⚠️  NE PAS MODIFIER CE FICHIER DIRECTEMENT.
--     Modifier les fichiers dans sql/schema/ puis relancer:
--       python scripts/db/regenerate_init.py
--
-- Workflow SQL-first:
--   - Nouvelles tables → ajouter dans sql/schema/0X_domaine.sql
--   - Modifications  → créer sql/migrations/VNNN__description.sql
--   - Réinitialisation complète → exécuter ce fichier (DROP CASCADE)
--
-- Usage:
--   psql $DATABASE_URL -f sql/INIT_COMPLET.sql
--   (ou Supabase SQL Editor)
--
-- ============================================================================
"""


def main() -> int:
    args = parse_args()
    schema_dir = Path(args.schema_dir)
    output_path = Path(args.output)

    if not schema_dir.exists():
        print(f"❌ Répertoire source introuvable: {schema_dir}", file=sys.stderr)
        print("   Exécutez d'abord: python scripts/db/split_init_sql.py", file=sys.stderr)
        return 1

    # Chercher les fichiers dans l'ordre attendu
    found_files: list[Path] = []
    missing: list[str] = []

    for filename in EXPECTED_FILES:
        f = schema_dir / filename
        if f.exists():
            found_files.append(f)
        else:
            missing.append(filename)
            print(f"  ⚠️  Fichier manquant: {filename}", file=sys.stderr)

    # Chercher aussi les fichiers supplémentaires (non listés dans EXPECTED_FILES)
    extra_files = [
        f for f in sorted(schema_dir.glob("*.sql"))
        if f.name not in EXPECTED_FILES
    ]
    if extra_files:
        print(f"  ℹ️  Fichiers supplémentaires trouvés: {[f.name for f in extra_files]}")
        # Les insérer avant 99_footer.sql
        insert_before_footer = output_path if not found_files else None
        for ef in extra_files:
            if ef not in found_files and "99_footer.sql" in EXPECTED_FILES:
                idx = found_files.index(schema_dir / "99_footer.sql") if (schema_dir / "99_footer.sql") in found_files else len(found_files)
                found_files.insert(idx, ef)

    if not found_files:
        print("❌ Aucun fichier SQL trouvé dans sql/schema/", file=sys.stderr)
        return 1

    # Construire le contenu
    header = build_header(schema_dir, found_files)
    parts = [header]

    for f in found_files:
        content = f.read_text(encoding="utf-8")
        # On omet le BEGIN; des fichiers individuels sauf 01_extensions.sql
        # (le BEGIN est déjà dans 01_extensions.sql)
        parts.append(f"\n-- Source: {f.name}\n")
        parts.append(content)

    final_content = "".join(parts)

    # Mode --check : comparer avec l'existant
    if args.check:
        if not output_path.exists():
            print(f"⚠️  {output_path} n'existe pas encore (à régénérer).")
            return 0

        existing = output_path.read_text(encoding="utf-8")
        # Comparer sans l'en-tête (qui change à chaque génération)
        existing_body = "\n".join(existing.splitlines()[10:])  # skip header
        new_body = "\n".join(final_content.splitlines()[10:])
        if existing_body == new_body:
            print("✅ INIT_COMPLET.sql est à jour.")
            return 0
        else:
            print("⚠️  INIT_COMPLET.sql n'est PAS à jour.")
            print("   Exécutez: python scripts/db/regenerate_init.py")
            return 1

    # Écrire
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(final_content, encoding="utf-8")

    total = len(final_content.splitlines())
    print(f"✅ {output_path} régénéré ({total} lignes, {len(found_files)} fichiers)")

    if missing:
        print(f"\n⚠️  {len(missing)} fichier(s) manquant(s) dans sql/schema/:")
        for m in missing:
            print(f"   - {m}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
