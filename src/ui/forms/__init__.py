"""
Système de formulaires déclaratifs pour Streamlit.

Modules:
- builder: FormBuilder avec validation Pydantic intégrée
"""

from src.ui.forms.builder import (
    ChampConfig,
    FormBuilder,
    FormResult,
    TypeChamp,
    creer_formulaire,
)

__all__ = [
    # Classes
    "FormBuilder",
    "FormResult",
    "ChampConfig",
    # Enums
    "TypeChamp",
    # Factory
    "creer_formulaire",
]
