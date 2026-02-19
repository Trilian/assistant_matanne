"""
Configuration - Module de configuration centralisée.

Ce module fournit:
- Chargement des paramètres (Pydantic BaseSettings)
- Chargement des fichiers .env et secrets Streamlit
- Fonction factory obtenir_parametres()
"""

from .loader import charger_secrets_streamlit
from .settings import Parametres, obtenir_parametres, reinitialiser_parametres

__all__ = [
    "Parametres",
    "obtenir_parametres",
    "reinitialiser_parametres",
    "charger_secrets_streamlit",
]
