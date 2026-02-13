"""
Layout - Header, Sidebar, Footer, CSS
Extraits de app.py pour meilleure maintenabilité
"""

from .footer import afficher_footer
from .header import afficher_header
from .init import initialiser_app
from .sidebar import MODULES_MENU, afficher_sidebar
from .styles import injecter_css

__all__ = [
    "afficher_header",
    "afficher_sidebar",
    "afficher_footer",
    "injecter_css",
    "initialiser_app",
    "MODULES_MENU",
]
