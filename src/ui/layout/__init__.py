"""
Layout - Header, Sidebar, Footer, CSS
Extraits de app.py pour meilleure maintenabilité
"""

from .header import afficher_header
from .sidebar import afficher_sidebar, MODULES_MENU
from .footer import afficher_footer
from .styles import injecter_css
from .init import initialiser_app

__all__ = [
    "afficher_header",
    "afficher_sidebar",
    "afficher_footer",
    "injecter_css",
    "initialiser_app",
    "MODULES_MENU",
]
