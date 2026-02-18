"""
Loader - Chargement des fichiers de configuration.

Fonctions pour charger:
- Fichiers .env et .env.local
- Secrets Streamlit
"""

import os
from pathlib import Path


def _reload_env_files():
    """Recharge les fichiers .env (appelé à chaque accès config pour Streamlit)"""
    try:
        # Trouver le répertoire racine du projet (parent du dossier src)
        _config_dir = Path(__file__).parent.parent.parent.parent
        _env_files = [_config_dir / ".env.local", _config_dir / ".env"]

        for env_path in _env_files:
            if env_path.exists():
                # Charger manuellement le fichier .env
                with open(env_path) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            if "=" in line:
                                key, value = line.split("=", 1)
                                key = key.strip()
                                value = value.strip()
                                # Retirer les guillemets
                                if value.startswith('"') and value.endswith('"'):
                                    value = value[1:-1]
                                elif value.startswith("'") and value.endswith("'"):
                                    value = value[1:-1]
                                # Pour Streamlit : forcer le rechargement
                                os.environ[key] = value
    except Exception:
        # Ignorer les erreurs si le chargement échoue
        pass


def _read_st_secret(section: str):
    """Lit de façon sûre une section de `st.secrets` si disponible.

    Retourne `None` si `st.secrets` n'est pas présent ou si la section manque.
    """
    try:
        import streamlit as st

        if hasattr(st, "secrets"):
            return st.secrets.get(section)
    except Exception:
        # Ne pas propager les erreurs d'accès à Streamlit secrets
        return None

    return None


def _is_streamlit_cloud() -> bool:
    """Détecte si l'app s'exécute sur Streamlit Cloud.

    Returns:
        True si sur Streamlit Cloud, False sinon
    """
    # Indicateurs de Streamlit Cloud
    if os.getenv("STREAMLIT_SERVER_HEADLESS") == "true":
        return True
    if os.getenv("STREAMLIT_RUNTIME_ENV") == "cloud":
        return True
    # Présence de secrets indique souvent le cloud - vérification sécurisée
    try:
        import streamlit as st

        if hasattr(st, "secrets"):
            # Éviter d'accéder directement à st.secrets pour ne pas lever d'exception
            return False  # En dev, considérer comme non-cloud
    except Exception:
        pass
    return False


def charger_secrets_streamlit() -> str | None:
    """Récupère la clé API Mistral des secrets Streamlit.

    Plusieurs stratégies pour accéder aux secrets:
    - Streamlit Cloud: `st.secrets`
    - Déploiement local avec secrets.toml: `st.secrets`

    Returns:
        Clé API ou None si non trouvée
    """
    import sys

    # Essayer d'accéder à st.secrets de plusieurs façons
    api_key = None

    # Stratégie 1: Import streamlit et accès direct
    try:
        import streamlit as st

        if hasattr(st, "secrets") and st.secrets:
            # Essayer d'accéder via .get()
            try:
                mistral = st.secrets.get("mistral", {})
                if mistral:
                    api_key = (
                        mistral.get("api_key")
                        if hasattr(mistral, "get")
                        else mistral.get("api_key", None)
                        if isinstance(mistral, dict)
                        else None
                    )
                    if api_key:
                        return api_key
            except Exception:
                pass

            # Essayer accès direct dict
            try:
                if "mistral" in st.secrets:
                    api_key = st.secrets["mistral"]["api_key"]
                    if api_key:
                        return api_key
            except Exception:
                pass

    except Exception:
        pass

    # Stratégie 2: Vérifier si on est en Streamlit et accéder à la config
    try:
        if "streamlit" in sys.modules:
            import streamlit.runtime.secrets as secrets_module

            try:
                # Accès direct au gestionnaire de secrets Streamlit
                if hasattr(secrets_module, "get_secret_file_path"):
                    pass  # Module trouvé mais pas d'accès direct
            except Exception:
                pass
    except Exception:
        pass

    return None


# Alias pour compatibilité
_get_mistral_api_key_from_secrets = charger_secrets_streamlit
