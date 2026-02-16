import os
import sys

sys.path.insert(0, os.path.abspath("."))
#!/usr/bin/env python3
"""
Script de gestion - Remplace le Makefile pour Streamlit Cloud
Usage: python manage.py <command>
"""
import subprocess
import sys
from pathlib import Path


def run_cmd(cmd: str, shell: bool = False):
    """ExÃ©cute une commande"""
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
    print("[RUN] DÃ©marrage de l'application...")
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
    """VÃ©rifie le code avec ruff"""
    print("[SEARCH] VÃ©rification du code...")
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
    print("📦 Génération requirements.txt...")
    if run_cmd("poetry export -f requirements.txt --output requirements.txt --without-hashes"):
        print("✅ requirements.txt généré")


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
                print(f"  SupprimÃ©: {path}")
            elif path.is_file():
                path.unlink()
                print(f"  SupprimÃ©: {path}")

    print("[OK] Nettoyage terminÃ©")


def reset_supabase():
    """Reset complet de la base Supabase"""
    print("[FIRE] Lancement du reset Supabase...")
    run_cmd("python scripts/db/reset_supabase.py")


def deploy_schema():
    """Déploie le schéma SQL vers Supabase"""
    print("[DB] Déploiement du schéma...")
    run_cmd("python scripts/db/deploy_supabase.py --deploy")


def check_db():
    """Vérifie la connexion Supabase"""
    print("[DB] Vérification connexion...")
    run_cmd("python scripts/db/deploy_supabase.py --check")


def seed_recipes():
    """Importe les recettes depuis le fichier JSON"""
    print("[SEED] Import des recettes...")
    run_cmd("python scripts/db/import_recettes.py")


def seed_demo():
    """Charge les données de démo"""
    print("[SEED] Chargement données démo...")
    run_cmd("python scripts/db/seed_data.py")


def test_quick():
    """Tests rapides sans couverture"""
    print("[TEST] Tests rapides...")
    run_cmd("python scripts/test/test_manager.py quick")


def test_core():
    """Tests du core uniquement"""
    print("[TEST] Tests core...")
    run_cmd("python scripts/test/test_manager.py core")


def audit_tests():
    """Audit de couverture des tests"""
    print("[AUDIT] Audit couverture...")
    run_cmd("python scripts/test/audit_tests.py")


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
  deploy-schema        Déploie le schéma SQL vers Supabase
  check-db             Vérifie la connexion Supabase
  seed-recipes         Importe les recettes standard
  seed-demo            Charge les données de démo

Tests avancés:
  test-quick           Tests rapides sans couverture
  test-core            Tests du core uniquement
  audit-tests          Audit de couverture des tests

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
    "deploy-schema": deploy_schema,
    "check-db": check_db,
    "seed-recipes": seed_recipes,
    "seed-demo": seed_demo,
    "test-quick": test_quick,
    "test-core": test_core,
    "audit-tests": audit_tests,
    "requirements": generate_requirements,
    "clean": clean,
    "help": help_cmd,
}


def main():
    """Point d'entrÃ©e"""
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
