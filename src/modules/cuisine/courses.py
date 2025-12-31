"""
Module Courses - Version Optimisée Ultra-Simple
"""
from src.ui.base_module import create_module_ui
from .configs import get_courses_config

def app():
    """Point d'entrée module courses"""
    ui = create_module_ui(get_courses_config())
    ui.render()