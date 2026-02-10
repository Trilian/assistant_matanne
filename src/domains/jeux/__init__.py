"""Domaine Jeux - Paris sportifs et Loto avec prédictions IA."""

# UI
from .ui import paris, loto

# Logic
from .logic import paris as paris_logic_module, loto_logic
# Backward compatibility alias
paris_logic = paris_logic_module

__all__ = [
    # UI
    "paris", "loto",
    # Logic
    "paris_logic", "paris_logic_module", "loto_logic",
]
