"""Domaine Jeux - Paris sportifs et Loto avec prédictions IA."""

# UI
from .ui import paris, loto

# Logic
from .logic import paris_logic, loto_logic

__all__ = [
    # UI
    "paris", "loto",
    # Logic
    "paris_logic", "loto_logic",
]
