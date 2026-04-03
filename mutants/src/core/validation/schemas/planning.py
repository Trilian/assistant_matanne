"""Schémas de validation pour le planning."""

from datetime import date

from pydantic import BaseModel, Field, field_validator


class RepasInput(BaseModel):
    """
    Input pour ajouter/modifier un repas au planning.
    """

    date_repas: date = Field(..., alias="date", description="Date du repas")
    type_repas: str = Field(
        ...,
        description="Type (petit_déjeuner, déjeuner, dîner, goûter)",
    )
    recette_id: int | None = Field(None, description="ID recette (optionnel)")
    description: str | None = Field(None, max_length=500)
    portions: int = Field(default=4, ge=1, le=50)

    model_config = {"populate_by_name": True}

    @field_validator("type_repas")
    @classmethod
    def valider_type(cls, v: str) -> str:
        """Valide le type de repas"""
        types_valides = {
            "petit_déjeuner",
            "déjeuner",
            "dîner",
            "goûter",
        }
        if v.lower() not in types_valides:
            raise ValueError(f"Type invalide. Doit être parmi: {', '.join(types_valides)}")
        return v.lower()
