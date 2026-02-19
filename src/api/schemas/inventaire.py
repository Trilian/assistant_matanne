"""
Schémas Pydantic pour l'inventaire.
"""

from datetime import datetime

from pydantic import BaseModel

from .base import IdentifiedResponse, NomValidatorMixin, QuantiteStricteValidatorMixin


class InventaireItemBase(BaseModel, NomValidatorMixin, QuantiteStricteValidatorMixin):
    """Schéma de base pour un article d'inventaire."""

    nom: str
    quantite: float = 1.0
    unite: str | None = None
    categorie: str | None = None
    date_peremption: datetime | None = None


class InventaireItemCreate(InventaireItemBase):
    """Schéma pour créer un article."""

    code_barres: str | None = None
    emplacement: str | None = None


class InventaireItemResponse(InventaireItemBase):
    """Schéma de réponse pour un article."""

    id: int
    code_barres: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
