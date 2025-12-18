"""
Alembic Environment - Compatible Streamlit Cloud + Supabase
"""
import os
import sys
from pathlib import Path
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import des modèles
from src.core.models import Base

# Configuration Alembic
config = context.config

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Métadonnées des modèles
target_metadata = Base.metadata


def get_url():
    """
    Récupère l'URL de connexion depuis les secrets Streamlit
    ou depuis les variables d'environnement
    """
    try:
        # Essayer d'abord avec Streamlit secrets (production)
        import streamlit as st

        db = st.secrets["db"]
        return (
            f"postgresql://{db['user']}:{db['password']}"
            f"@{db['host']}:{db['port']}/{db['name']}"
            f"?sslmode=require"
        )
    except:
        # Fallback sur .env (développement local)
        from dotenv import load_dotenv

        load_dotenv()

        user = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD")
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        database = os.getenv("POSTGRES_DB", "postgres")

        if not password:
            raise ValueError(
                "❌ Configuration DB manquante.\n"
                "Configure soit :\n"
                "1. Les secrets Streamlit (.streamlit/secrets.toml)\n"
                "2. Les variables d'environnement (.env)"
            )

        return f"postgresql://{user}:{password}" f"@{host}:{port}/{database}" f"?sslmode=require"


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
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
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
