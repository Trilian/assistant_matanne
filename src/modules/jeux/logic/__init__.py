"""Logique métier du domaine Jeux - Calculs et prédictions."""

from . import paris, loto_logic
# Backward compatibility
from . import paris as paris_logic

__all__ = ["paris", "paris_logic", "loto_logic"]
