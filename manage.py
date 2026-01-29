#!/usr/bin/env python3
"""
Script de gestion - Remplace le Makefile pour Streamlit Cloud
Usage: python manage.py <command>
"""
import sys
import subprocess
from pathlib import Path


def run_cmd(cmd: str, shell: bool = False):
    """Exécute une commande"""
    try:
        if shell:
            subprocess.run(cmd, shell=True, check=True)
        else:
            subprocess.run(cmd.split(), check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Erreur: {e}")
        return False


def run():
    """Lance l'application Streamlit"""
    print("[RUN] Démarrage de l'application...")
    run_cmd("streamlit run src/app.py")


def test():
    """Lance les tests"""
    print("[TEST] Lancement des tests...")
    run_cmd("pytest")


def test_coverage():
    """Lance les tests avec couverture"""
    print("[CHART] Tests avec couverture...")
    run_cmd("pytest --cov=src --cov-report=html --cov-report=term")


def format_code():
    """Formate le code avec black"""
    print("[STAR] Formatage du code...")
    run_cmd("black src tests")


def lint():
    """Vérifie le code avec ruff"""
    print("[SEARCH] Vérification du code...")
    run_cmd("ruff check src tests")


def migrate():
    """Applique les migrations Alembic"""
    print("[DB] Application des migrations...")
    run_cmd("alembic upgrade head")


def create_migration():
    """Crée une nouvelle migration"""
    message = input("Message de migration: ")
    print(f"[EDIT] Création migration: {message}")
    run_cmd(f"alembic revision --autogenerate -m '{message}'", shell=True)


def generate_requirements():
    """Génère requirements.txt depuis pyproject.toml"""
    print("[PKG] Génération requirements.txt...")
    if run_cmd("poetry export -f requirements.txt --output requirements.txt --without-hashes"):
        print("[OK] requirements.txt généré")


def clean():
    """Nettoie les fichiers temporaires"""
    print("[CLEAN] Nettoyage...")
    import shutil

    patterns = [
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "htmlcov",
        ".coverage",
    ]

    for pattern in patterns:
        for path in Path(".").rglob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"  Supprimé: {path}")
            elif path.is_file():
                path.unlink()
                print(f"  Supprimé: {path}")

    print("[OK] Nettoyage terminé")


def reset_supabase():
    """Reset complet de la base Supabase"""
    print("[FIRE] Lancement du reset Supabase...")
    run_cmd("python scripts/reset_supabase.py")


def help_cmd():
    """Affiche l'aide"""
    print(
        """
🤖 Assistant MaTanne v2 - Commandes disponibles

Développement:
  run                  Lance l'application Streamlit
  test                 Lance les tests
  coverage             Tests avec couverture
  format               Formate le code (black)
  lint                 Vérifie le code (ruff)
  clean                Nettoie les fichiers temporaires

Base de données:
  migrate              Applique les migrations
  create-migration     Crée une nouvelle migration
  reset-supabase       [FIRE] Reset COMPLET Supabase (DANGER)

Déploiement:
  requirements         Génère requirements.txt

Usage:
  python manage.py <command>
    """
    )


COMMANDS = {
    "run": run,
    "test": test,
    "coverage": test_coverage,
    "format": format_code,
    "lint": lint,
    "migrate": migrate,
    "create-migration": create_migration,
    "reset-supabase": reset_supabase,
    "requirements": generate_requirements,
    "clean": clean,
    "help": help_cmd,
}


def main():
    """Point d'entrée"""
    if len(sys.argv) < 2:
        help_cmd()
        sys.exit(0)

    command = sys.argv[1]

    if command not in COMMANDS:
        print(f"[ERROR] Commande inconnue: {command}")
        help_cmd()
        sys.exit(1)

    COMMANDS[command]()


if __name__ == "__main__":
    main()
