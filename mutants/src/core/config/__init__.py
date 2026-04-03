"""
Configuration - Module de configuration centralisée.

Ce module fournit:
- Chargement des paramètres (Pydantic BaseSettings)
- Chargement des fichiers .env
- Fonction factory obtenir_parametres()
"""

from .settings import Parametres, obtenir_parametres, reinitialiser_parametres

__all__ = [
    "Parametres",
    "obtenir_parametres",
    "reinitialiser_parametres",
]
