"""
Layout - Header, Footer, CSS
Extraits de app.py pour meilleure maintenabilité
"""

from .footer import afficher_footer
from .header import afficher_header
from .initialisation import initialiser_app
from .styles import injecter_css

__all__ = [
    "afficher_header",
    "afficher_footer",
    "injecter_css",
    "initialiser_app",
]
