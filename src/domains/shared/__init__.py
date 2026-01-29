"""Domaine Shared - Modules partagÃ©s (accueil, paramÃ¨tres, rapports)."""

# UI
from .ui import accueil, parametres, rapports, barcode

# Logic
from .logic import parametres_logic, rapports_logic, barcode_logic

__all__ = [
    # UI
    "accueil", "parametres", "rapports", "barcode",
    # Logic
    "parametres_logic", "rapports_logic", "barcode_logic",
]

