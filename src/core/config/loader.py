"""
Loader - Chargement des fichiers de configuration.

Fonctions pour charger les fichiers .env et .env.local (via python-dotenv).
"""

import os
from pathlib import Path

from dotenv import load_dotenv


def _reload_env_files():
    """Recharge les fichiers .env.

    Utilise python-dotenv pour un parsing robuste (multilignes, échappements,
    exports, interpolation, etc.) au lieu d'un parser naïf ligne par ligne.
    """
    try:
        _config_dir = Path(__file__).parent.parent.parent.parent

        env_path = _config_dir / ".env"
        env_local_path = _config_dir / ".env.local"

        if env_path.exists():
            load_dotenv(env_path, override=True)
        if env_local_path.exists():
            load_dotenv(env_local_path, override=True)
    except Exception:
        pass


def _read_env_secret(section: str) -> str | None:
    """Lit une variable d'environnement (remplacement de st.secrets).

    Args:
        section: Nom de la variable d'environnement (case-insensitive).

    Returns:
        Valeur ou None si non trouvée.
    """
    return os.environ.get(section) or os.environ.get(section.upper())
