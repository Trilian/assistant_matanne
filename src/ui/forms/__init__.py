"""
Système de formulaires déclaratifs pour Streamlit.

Modules:
- types: TypeChamp, ChampConfig, FormResult
- fields: FormFieldsMixin (12 méthodes fluides)
- rendering: FormRenderingMixin (rendu + validation)
- builder: FormBuilder composé des mixins
"""

from src.ui.forms.builder import FormBuilder, creer_formulaire
from src.ui.forms.types import ChampConfig, FormResult, TypeChamp

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
