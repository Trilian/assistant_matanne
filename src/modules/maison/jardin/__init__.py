"""
Sous-module Jardin - Gestion intelligente du potager.

Structure:
- styles.py: CSS du module
- data.py: Chargement catalogue plantes
- taches.py: Génération automatique des tâches
- autonomie.py: Calculs d'autonomie alimentaire
- ui.py: Composants UI réutilisables
- onglets.py: Onglets de l'interface
"""

from .main import app

__all__ = ["app"]
