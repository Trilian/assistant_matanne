"""
Script de backup/restauration de la base de données.

Usage:
  python scripts/db/backup_database.py backup [--tables TABLE1,TABLE2] [--no-compress] [--upload]
  python scripts/db/backup_database.py restore <chemin_fichier> [--tables TABLE1,TABLE2] [--clear]
  python scripts/db/backup_database.py list
  python scripts/db/backup_database.py cleanup [--keep N]

Nécessite DATABASE_URL dans .env.local ou en variable d'environnement.
"""

import argparse
import sys
from pathlib import Path

# Ajouter la racine du projet au path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))


def backup(args: argparse.Namespace) -> None:
    """Crée un backup de la base de données."""
    from src.services.core.backup import ServiceBackup
    from src.services.core.backup.types import BackupConfig

    config = BackupConfig(
        backup_dir=args.output_dir,
        compress=not args.no_compress,
        max_backups=args.keep,
    )
    service = ServiceBackup(config)

    tables = args.tables.split(",") if args.tables else None
    result = service.create_backup(tables=tables, compress=not args.no_compress)

    if result and result.success:
        print(f"✅ {result.message}")
        print(f"   Fichier: {result.file_path}")
        if result.metadata:
            print(f"   Tables: {result.metadata.tables_count}")
            print(f"   Enregistrements: {result.metadata.total_records}")
            print(f"   Taille: {result.metadata.file_size_bytes / 1024:.1f} KB")
            print(f"   Durée: {result.duration_seconds:.2f}s")

        if args.upload:
            ok = service.upload_to_supabase(result.file_path)
            if ok:
                print("☁️  Uploadé vers Supabase Storage")
            else:
                print("⚠️  Échec upload Supabase (vérifier la configuration)")
    else:
        print("❌ Échec du backup")
        if result:
            print(f"   {result.message}")
        sys.exit(1)


def restore(args: argparse.Namespace) -> None:
    """Restaure depuis un fichier de backup."""
    from src.services.core.backup import ServiceBackup

    if not Path(args.file).exists():
        print(f"❌ Fichier introuvable: {args.file}")
        sys.exit(1)

    service = ServiceBackup()
    tables = args.tables.split(",") if args.tables else None

    result = service.restore_backup(
        file_path=args.file,
        tables=tables,
        clear_existing=args.clear,
    )

    if result and result.success:
        print(f"✅ {result.message}")
        print(f"   Tables restaurées: {', '.join(result.tables_restored)}")
        print(f"   Enregistrements: {result.records_restored}")
    else:
        print("❌ Échec de la restauration")
        if result:
            print(f"   {result.message}")
            if result.errors:
                for err in result.errors:
                    print(f"   - {err}")
        sys.exit(1)


def list_backups(args: argparse.Namespace) -> None:
    """Liste les backups disponibles."""
    backup_dir = Path(args.output_dir)
    if not backup_dir.exists():
        print(f"Aucun backup dans {backup_dir}")
        return

    backups = sorted(backup_dir.glob("backup_*"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not backups:
        print("Aucun backup trouvé.")
        return

    print(f"📁 {len(backups)} backup(s) dans {backup_dir}/\n")
    for b in backups:
        size_kb = b.stat().st_size / 1024
        from datetime import datetime

        mtime = datetime.fromtimestamp(b.stat().st_mtime)
        print(f"  {b.name:<50} {size_kb:>8.1f} KB  {mtime:%Y-%m-%d %H:%M}")


def cleanup(args: argparse.Namespace) -> None:
    """Supprime les anciens backups au-delà de --keep."""
    backup_dir = Path(args.output_dir)
    backups = sorted(backup_dir.glob("backup_*"), key=lambda p: p.stat().st_mtime, reverse=True)

    to_delete = backups[args.keep :]
    if not to_delete:
        print(f"Rien à supprimer ({len(backups)} backup(s), seuil: {args.keep})")
        return

    for b in to_delete:
        b.unlink()
        print(f"🗑️  Supprimé: {b.name}")
    print(f"✅ {len(to_delete)} ancien(s) backup(s) supprimé(s)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Backup/Restauration base de données")
    parser.add_argument(
        "--output-dir", default="sauvegardes", help="Répertoire des backups (défaut: sauvegardes)"
    )
    parser.add_argument("--keep", type=int, default=10, help="Nombre max de backups à conserver")

    sub = parser.add_subparsers(dest="command", required=True)

    # backup
    p_backup = sub.add_parser("backup", help="Créer un backup")
    p_backup.add_argument("--tables", help="Tables à exporter (séparées par des virgules)")
    p_backup.add_argument("--no-compress", action="store_true", help="Ne pas compresser")
    p_backup.add_argument("--upload", action="store_true", help="Uploader vers Supabase Storage")

    # restore
    p_restore = sub.add_parser("restore", help="Restaurer depuis un backup")
    p_restore.add_argument("file", help="Chemin du fichier de backup")
    p_restore.add_argument("--tables", help="Tables à restaurer (séparées par des virgules)")
    p_restore.add_argument(
        "--clear", action="store_true", help="Supprimer les données existantes avant restauration"
    )

    # list
    sub.add_parser("list", help="Lister les backups disponibles")

    # cleanup
    sub.add_parser("cleanup", help="Supprimer les anciens backups")

    args = parser.parse_args()

    commands = {
        "backup": backup,
        "restore": restore,
        "list": list_backups,
        "cleanup": cleanup,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
