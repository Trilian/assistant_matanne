"""Schémas de validation pour la famille."""

from datetime import date

from pydantic import BaseModel, Field, field_validator


class RoutineInput(BaseModel):
    """
    Input pour créer/modifier une routine.
    """

    nom: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=500)
    pour_qui: str = Field(..., description="Enfant associé")
    frequence: str = Field(..., description="Fréquence (quotidien, hebdo, mensuel)")
    is_active: bool = Field(default=True)

    @field_validator("nom")
    @classmethod
    def nettoyer_nom(cls, v: str) -> str:
        return v.strip().capitalize()

    @field_validator("frequence")
    @classmethod
    def valider_frequence(cls, v: str) -> str:
        """Valide la fréquence"""
        frequences_valides = {"quotidien", "hebdomadaire", "mensuel"}
        if v.lower() not in frequences_valides:
            raise ValueError(
                f"Fréquence invalide. Doit être parmi: {', '.join(frequences_valides)}"
            )
        return v.lower()


class TacheRoutineInput(BaseModel):
    """
    Input pour ajouter une tâche à une routine.
    """

    nom: str = Field(..., min_length=1, max_length=200)
    heure: str | None = Field(None, pattern=r"^\d{2}:\d{2}$")
    description: str | None = Field(None, max_length=500)

    @field_validator("nom")
    @classmethod
    def nettoyer_nom(cls, v: str) -> str:
        return v.strip().capitalize()


class EntreeJournalInput(BaseModel):
    """
    Input pour ajouter une entrée au journal.
    """

    domaine: str = Field(..., description="Domaine (santé, humeur, développement)")
    titre: str = Field(..., min_length=1, max_length=200)
    contenu: str = Field(..., min_length=1, max_length=2000)
    date_entree: date = Field(default_factory=date.today, alias="date")
    tags: list[str] = Field(default_factory=list, max_length=10)

    model_config = {"populate_by_name": True}

    @field_validator("domaine")
    @classmethod
    def valider_domaine(cls, v: str) -> str:
        """Valide le domaine"""
        domaines_valides = {"santé", "humeur", "développement", "comportement"}
        if v.lower() not in domaines_valides:
            raise ValueError(f"Domaine invalide. Doit être parmi: {', '.join(domaines_valides)}")
        return v.lower()

    @field_validator("titre")
    @classmethod
    def nettoyer_titre(cls, v: str) -> str:
        return v.strip().capitalize()
