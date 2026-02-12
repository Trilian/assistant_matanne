"""
Types et schémas Pydantic pour le package batch_cooking.

Module unifié avec tous les modèles de données pour les services de batch cooking.
"""

from pydantic import BaseModel, Field


class EtapeBatchIA(BaseModel):
    """Étape générée par l'IA pour une session batch cooking."""
    ordre: int = Field(..., ge=1)
    titre: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=5)
    duree_minutes: int = Field(..., ge=1, le=180)
    robots: list[str] = Field(default_factory=list)
    groupe_parallele: int = Field(default=0, ge=0)
    est_supervision: bool = Field(default=False)
    alerte_bruit: bool = Field(default=False)
    temperature: int | None = Field(default=None, ge=0, le=300)
    recette_nom: str | None = Field(default=None)


class SessionBatchIA(BaseModel):
    """Session batch cooking générée par l'IA."""
    recettes: list[str] = Field(..., min_length=1)
    duree_totale_estimee: int = Field(..., ge=5, le=480)
    etapes: list[EtapeBatchIA] = Field(..., min_length=1)
    conseils_jules: list[str] = Field(default_factory=list)
    ordre_optimal: str = Field(default="")


class PreparationIA(BaseModel):
    """Préparation générée par l'IA."""
    nom: str = Field(..., min_length=3, max_length=200)
    portions: int = Field(..., ge=1, le=20)
    conservation_jours: int = Field(..., ge=1, le=90)
    localisation: str = Field(default="frigo")
    container_suggere: str = Field(default="")


__all__ = [
    "EtapeBatchIA",
    "SessionBatchIA",
    "PreparationIA",
]
