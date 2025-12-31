"""
Module Inventaire - Version Optimisée Ultra-Simple
"""
from src.ui.base_module import create_module_ui
from .configs import get_inventaire_config

def app():
    """Point d'entrée module inventaire"""
    ui = create_module_ui(get_inventaire_config())
    ui.render()