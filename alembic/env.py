"""Configuration de l'environnement Alembic — Assistant Matanne.

Charge automatiquement l'URL de connexion depuis ``src.core.config``
et importe tous les modèles SQLAlchemy pour les migrations autogénérées.

Usage rapide :
    alembic revision --autogenerate -m "ajout_table_xyz"
    alembic upgrade head
    alembic downgrade -1
    alembic current
    alembic history --verbose

Pour la baseline initiale (première fois sur une DB existante) :
    alembic stamp head
"""

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# Racine du projet dans le chemin Python
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import obtenir_parametres  # noqa: E402
from src.core.models import Base, charger_tous_modeles  # noqa: E402

# Charger tous les modèles SQLAlchemy pour que l'autogénération les détecte
charger_tous_modeles()

# ── Alembic Config ────────────────────────────────────────────────────────────
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Métadonnées de la Base — utilisées pour --autogenerate
target_metadata = Base.metadata


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_url() -> str:
    """Charge l'URL de connexion depuis la configuration centralisée."""
    return obtenir_parametres().DATABASE_URL


# ── Modes de migration ────────────────────────────────────────────────────────

def run_migrations_offline() -> None:
    """Mode offline : génère le SQL sans connexion réelle à la DB.

    Utile pour produire un script SQL à appliquer manuellement sur Supabase.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Mode online : exécute les migrations directement contre la DB.

    Requiert que DATABASE_URL pointe vers une connexion active (Supabase
    connection pooler en mode session recommandé).
    """
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # NullPool adapté aux scripts de migration
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            # Schéma Supabase public par défaut
            include_schemas=False,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
