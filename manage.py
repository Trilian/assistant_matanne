import os
import sys

sys.path.insert(0, os.path.abspath("."))
#!/usr/bin/env python3
"""
Script de gestion - Assistant MaTanne
Usage: python manage.py <command>
"""
import subprocess
import sys
from pathlib import Path

for flux in (sys.stdout, sys.stderr):
    if hasattr(flux, "reconfigure"):
        flux.reconfigure(encoding="utf-8", errors="replace")


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
    """Lance le serveur FastAPI"""
    print("[RUN] D\u00e9marrage du serveur FastAPI...")
    run_cmd("uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000")


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
    import importlib.util

    if importlib.util.find_spec("ruff") is None:
        print("[INSTALL] Ruff absent, installation en cours...")
        if not run_cmd(f'"{sys.executable}" -m pip install ruff', shell=True):
            return False

    return run_cmd(f'"{sys.executable}" -m ruff check src tests', shell=True)


def migrate():
    """Applique les migrations SQL depuis sql/migrations/"""
    print("[DB] Application des migrations SQL...")
    try:
        from src.core.db import GestionnaireMigrations

        GestionnaireMigrations.executer_migrations()
        version = GestionnaireMigrations.obtenir_version_courante()
        print(f"[OK] Migrations appliqu\u00e9es. Schema v{version}")
    except Exception as e:
        print(f"[ERROR] Erreur: {e}")
        sys.exit(1)


def create_migration():
    """Crée un nouveau fichier de migration SQL dans sql/migrations/"""
    import re
    from datetime import datetime

    message = input("Message de migration: ").strip()
    if not message:
        print("[ERROR] Message requis")
        sys.exit(1)

    migrations_dir = Path("sql/migrations")
    migrations_dir.mkdir(parents=True, exist_ok=True)

    # Trouver le prochain numéro
    existing = sorted(migrations_dir.glob("*.sql"))
    if existing:
        last_num = int(existing[-1].name.split("_")[0])
        next_num = last_num + 1
    else:
        next_num = 1

    # Slug du message
    slug = re.sub(r"[^a-z0-9]+", "_", message.lower()).strip("_")
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"{next_num:03d}_{slug}.sql"
    filepath = migrations_dir / filename

    template = f"""-- ============================================================================
-- Migration {next_num:03d}: {message}
-- Date: {date_str}
-- Description: [Décrire les changements ici]
-- ============================================================================
BEGIN;

-- [Votre SQL ici]

COMMIT;
"""

    filepath.write_text(template, encoding="utf-8")
    print(f"[EDIT] Migration créée: {filepath}")
    print("  -> Éditez le fichier puis lancez: python manage.py migrate")


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


def backup_db():
    """Crée un backup de la base de données"""
    print("[DB] Création backup...")
    run_cmd("python scripts/db/backup_database.py backup")


def restore_db():
    """Restaure la base depuis un backup"""
    if len(sys.argv) < 3:
        print("[ERROR] Usage: python manage.py restore <chemin_backup>")
        sys.exit(1)
    fichier = sys.argv[2]
    print(f"[DB] Restauration depuis {fichier}...")
    run_cmd(f"python scripts/db/backup_database.py restore {fichier}")


def list_backups():
    """Liste les backups disponibles"""
    run_cmd("python scripts/db/backup_database.py list")


def check_db():
    """Vérifie la connexion Supabase"""
    print("[DB] Vérification connexion...")
    run_cmd("python scripts/db/deploy_supabase.py --check")


def schema_diff():
    """Compare le schéma SQL, l'ORM et la base active."""
    print("[DB] Analyse du diff de schéma...")
    try:
        from src.core.db.schema_diff import formater_schema_diff_console, generer_schema_diff

        diff = generer_schema_diff()
        print(formater_schema_diff_console(diff))
        if diff.get("status") == "error":
            sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Erreur schema diff: {e}")
        sys.exit(1)


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


def test_visual():
    """Lance les tests visuels Playwright (nécessite: pip install playwright pytest-playwright && playwright install chromium)"""
    print("[VISUAL] Tests visuels Playwright...")
    run_cmd("pytest tests/visual/ -m visual -v")


def test_visual_update():
    """Met à jour les snapshots de référence Playwright"""
    import os

    print("[VISUAL] Mise à jour des snapshots...")
    os.environ["UPDATE_SNAPSHOTS"] = "1"
    run_cmd("pytest tests/visual/ -m visual -v")
    os.environ.pop("UPDATE_SNAPSHOTS", None)
    print("[OK] Snapshots mis à jour")


def playwright_install():
    """Installe Playwright et les navigateurs nécessaires"""
    print("[INSTALL] Installation Playwright...")
    run_cmd("pip install playwright pytest-playwright")
    run_cmd("playwright install chromium")
    print("[OK] Playwright installé")


def test_core():
    """Tests du core uniquement"""
    print("[TEST] Tests core...")
    run_cmd("python scripts/test/test_manager.py core")


def audit_tests():
    """Audit rapide des tests (mapping source/test, patterns inefficaces)"""
    print("[AUDIT] Audit tests...")
    run_cmd("python scripts/test/audit_tests_fast.py")


def mutation():
    """Lance un mutation testing focalisé sur un module critique (dashboard/planning/cuisine)."""
    profil = sys.argv[2] if len(sys.argv) >= 3 else "dashboard"
    print(f"[DNA] Mutation testing ciblé ({profil})...")
    if sys.platform.startswith("win"):
        print("[WARN] mutmut nécessite WSL sous Windows pour une exécution locale.")
        print(f"       Utiliser: wsl python3 scripts/test/run_mutation_ci.py --profile {profil}")
        print("       Ou lancer le workflow GitHub Actions 'Mutation Testing'.")
        sys.exit(1)
    return run_cmd(
        f'"{sys.executable}" scripts/test/run_mutation_ci.py --profile {profil}',
        shell=True,
    )


def mutation_ci():
    """Alias explicite pour la commande CI de mutation testing."""
    profil = sys.argv[2] if len(sys.argv) >= 3 else "dashboard"
    print(f"[DNA] Mutation testing — mode CI ({profil})...")
    if sys.platform.startswith("win"):
        print("[WARN] mutmut nécessite WSL sous Windows pour une exécution locale.")
        print(f"       Utiliser: wsl python3 scripts/test/run_mutation_ci.py --profile {profil}")
        print("       Ou lancer le workflow GitHub Actions 'Mutation Testing'.")
        sys.exit(1)
    return run_cmd(
        f'"{sys.executable}" scripts/test/run_mutation_ci.py --profile {profil}',
        shell=True,
    )


def staging():
    """Gère l'environnement staging Docker Compose"""
    if len(sys.argv) < 3:
        print("Usage: python manage.py staging <start|stop|reset|logs|status>")
        sys.exit(1)

    action = sys.argv[2]
    compose_file = "docker-compose.staging.yml"
    base_cmd = f"docker compose -f {compose_file}"

    if action == "start":
        print("[STAGING] Démarrage de l'environnement staging...")
        run_cmd(f"{base_cmd} up -d --build", shell=True)
        print("[OK] Staging démarré:")
        print("  Backend:  http://localhost:8001")
        print("  Frontend: http://localhost:3001")
        print("  DB:       localhost:5433")
    elif action == "stop":
        print("[STAGING] Arrêt de l'environnement staging...")
        run_cmd(f"{base_cmd} down", shell=True)
    elif action == "reset":
        print("[STAGING] Reset complet (volumes inclus)...")
        run_cmd(f"{base_cmd} down -v", shell=True)
        run_cmd(f"{base_cmd} up -d --build", shell=True)
        print("[OK] Staging reset et redémarré")
    elif action == "logs":
        run_cmd(f"{base_cmd} logs -f", shell=True)
    elif action == "status":
        run_cmd(f"{base_cmd} ps", shell=True)
    else:
        print(f"[ERROR] Action inconnue: {action}")
        print("Actions: start, stop, reset, logs, status")
        sys.exit(1)


def help_cmd():
    """Affiche l'aide"""
    print(
        """
Assistant MaTanne v2 - Commandes disponibles

Développement:
  run                  Lance le serveur FastAPI (uvicorn)
  test                 Lance les tests
  coverage             Tests avec couverture
  format               Formate le code (black)
  lint                 Vérifie le code (ruff)
  clean                Nettoie les fichiers temporaires

Base de données:
  migrate              Applique les migrations SQL (sql/migrations/)
  create-migration     Crée un fichier de migration SQL
  reset-supabase       [FIRE] Reset COMPLET Supabase (DANGER)
  deploy-schema        Déploie le schéma SQL vers Supabase
  check-db             Vérifie la connexion Supabase
  schema-diff          Compare SQL, ORM et base active
  seed-recipes         Importe les recettes standard
  seed-demo            Charge les données de démo
  backup               Crée un backup de la base de données
  restore <fichier>    Restaure depuis un backup
  list-backups         Liste les backups disponibles

Tests avancés:
  test-quick           Tests rapides sans couverture
  test-core            Tests du core uniquement
  audit-tests          Audit de couverture des tests
  mutation [profil]    Mutation testing focalisé (dashboard/planning/cuisine)
  mutation-ci [profil] Mutation testing avec seuils CI

Staging:
  staging start        Démarre l'environnement staging Docker
  staging stop         Arrête le staging
  staging reset        Reset complet (volumes + rebuild)
  staging logs         Affiche les logs en continu
  staging status       Statut des containers

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
    "schema-diff": schema_diff,
    "seed-recipes": seed_recipes,
    "seed-demo": seed_demo,
    "backup": backup_db,
    "restore": restore_db,
    "list-backups": list_backups,
    "test-quick": test_quick,
    "test-core": test_core,
    "audit-tests": audit_tests,
    "mutation": mutation,
    "mutation-ci": mutation_ci,
    "requirements": generate_requirements,
    "staging": staging,
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
