"""
Configuration - Module de configuration centralisée.

Ce module fournit:
- Chargement des paramètres (Pydantic BaseSettings)
- Chargement des fichiers .env et secrets Streamlit
- Fonction factory obtenir_parametres()
"""

from .loader import (
    _get_mistral_api_key_from_secrets,
    _is_streamlit_cloud,
    _read_st_secret,
    _reload_env_files,
    charger_secrets_streamlit,
)
from .settings import Parametres, obtenir_parametres

__all__ = [
    "Parametres",
    "obtenir_parametres",
    "_reload_env_files",
    "_read_st_secret",
    "_is_streamlit_cloud",
    "_get_mistral_api_key_from_secrets",
    "charger_secrets_streamlit",
]
