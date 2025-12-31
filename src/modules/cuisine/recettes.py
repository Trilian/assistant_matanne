"""
Module Recettes - Version Optimisée Ultra-Simple
"""
from src.ui.base_module import create_module_ui
from .configs import get_recettes_config

def app():
    """Point d'entrée module recettes"""
    ui = create_module_ui(get_recettes_config())
    ui.render()