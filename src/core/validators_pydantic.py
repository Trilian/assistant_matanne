"""
Validators Pydantic - Schémas Pydantic pour validation des entrées.

Ce module centralise tous les modèles Pydantic pour validation
des inputs utilisateur et des données métier.

Chaque modèle :
- Valide les types
- Applique les contraintes métier
- Nettoie les données
- Fournit des messages d'erreur clairs
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


# ═══════════════════════════════════════════════════════════
# RECETTES
# ═══════════════════════════════════════════════════════════


class IngredientInput(BaseModel):
    """
    Input pour ajouter/modifier un ingrédient.
    """

    nom: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Nom de l'ingrédient",
    )
    quantite: Optional[float] = Field(
        None, ge=0.01, le=10000, description="Quantité (optionnel)"
    )
    unite: Optional[str] = Field(
        None, max_length=50, description="Unité de mesure"
    )

    @field_validator("nom")
    @classmethod
    def nettoyer_nom(cls, v: str) -> str:
        """Nettoie et normalise le nom"""
        return v.strip().capitalize()


class EtapeInput(BaseModel):
    """
    Input pour ajouter/modifier une étape de recette.
    """

    numero: int = Field(..., ge=1, description="Numéro de l'étape")
    description: str = Field(
        ...,
        min_length=5,
        max_length=1000,
        description="Description de l'étape",
    )
    temps_minutes: Optional[int] = Field(
        None, ge=1, le=1440, description="Durée en minutes"
    )

    @field_validator("description")
    @classmethod
    def nettoyer_description(cls, v: str) -> str:
        """Nettoie la description"""
        return v.strip()


class RecetteInput(BaseModel):
    """
    Input pour créer/modifier une recette.

    Validation complète des recettes.
    """

    nom: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Nom de la recette",
    )
    description: Optional[str] = Field(
        None, max_length=500, description="Description"
    )
    temps_preparation: int = Field(
        ..., ge=1, le=1440, description="Temps de préparation (min)"
    )
    temps_cuisson: int = Field(
        ..., ge=0, le=1440, description="Temps de cuisson (min)"
    )
    portions: int = Field(
        default=4, ge=1, le=50, description="Nombre de portions"
    )
    ingredients: list[IngredientInput] = Field(
        ..., min_length=1, max_length=50, description="Liste des ingrédients"
    )
    etapes: list[EtapeInput] = Field(
        ..., min_length=1, max_length=50, description="Étapes de préparation"
    )
    saison: Optional[str] = Field(
        None, description="Saison (printemps, été, automne, hiver)"
    )
    cout_estimee: Optional[float] = Field(
        None, ge=0, description="Coût estimé en euros"
    )

    @field_validator("nom")
    @classmethod
    def valider_nom(cls, v: str) -> str:
        """Nettoie et valide le nom"""
        cleaned = v.strip().capitalize()
        if len(cleaned) < 2:
            raise ValueError("Le nom doit contenir au moins 2 caractères")
        return cleaned

    @field_validator("saison")
    @classmethod
    def valider_saison(cls, v: Optional[str]) -> Optional[str]:
        """Valide la saison"""
        if v:
            saisons_valides = {"printemps", "été", "automne", "hiver"}
            if v.lower() not in saisons_valides:
                raise ValueError(
                    f"Saison invalide. Doit être parmi: {', '.join(saisons_valides)}"
                )
            return v.lower()
        return None

    @model_validator(mode="after")
    def valider_temps_total(self) -> "RecetteInput":
        """Valide que le temps total n'est pas trop long"""
        temps_total = self.temps_preparation + self.temps_cuisson
        if temps_total > 1440:  # 24 heures
            raise ValueError("Temps total ne peut pas dépasser 24 heures")
        return self


# ═══════════════════════════════════════════════════════════
# INVENTAIRE
# ═══════════════════════════════════════════════════════════


class IngredientStockInput(BaseModel):
    """
    Input pour ajouter/modifier un article en inventaire.
    """

    nom: str = Field(..., min_length=1, max_length=200)
    quantite: float = Field(..., ge=0.01)
    unite: str = Field(..., min_length=1, max_length=50)
    date_expiration: Optional[date] = Field(None, description="Date d'expiration")
    localisation: Optional[str] = Field(None, max_length=200)
    prix_unitaire: Optional[float] = Field(None, ge=0)

    @field_validator("nom")
    @classmethod
    def nettoyer_nom(cls, v: str) -> str:
        return v.strip().capitalize()

    @field_validator("localisation")
    @classmethod
    def nettoyer_localisation(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return v.strip().capitalize()
        return None


# ═══════════════════════════════════════════════════════════
# PLANNING
# ═══════════════════════════════════════════════════════════


class RepasInput(BaseModel):
    """
    Input pour ajouter/modifier un repas au planning.
    """

    date_repas: date = Field(..., alias="date", description="Date du repas")
    type_repas: str = Field(
        ...,
        description="Type (petit_déjeuner, déjeuner, dîner, goûter)",
    )
    recette_id: Optional[int] = Field(None, description="ID recette (optionnel)")
    description: Optional[str] = Field(None, max_length=500)
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
            raise ValueError(
                f"Type invalide. Doit être parmi: {', '.join(types_valides)}"
            )
        return v.lower()


# ═══════════════════════════════════════════════════════════
# FAMILLE
# ═══════════════════════════════════════════════════════════


class RoutineInput(BaseModel):
    """
    Input pour créer/modifier une routine.
    """

    nom: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    pour_qui: str = Field(..., description="Enfant associé")
    frequence: str = Field(
        ..., description="Fréquence (quotidien, hebdo, mensuel)"
    )
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
    heure: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    description: Optional[str] = Field(None, max_length=500)

    @field_validator("nom")
    @classmethod
    def nettoyer_nom(cls, v: str) -> str:
        return v.strip().capitalize()


# ═══════════════════════════════════════════════════════════
# JOURNAL / BIEN-ÊTRE
# ═══════════════════════════════════════════════════════════


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
            raise ValueError(
                f"Domaine invalide. Doit être parmi: {', '.join(domaines_valides)}"
            )
        return v.lower()

    @field_validator("titre")
    @classmethod
    def nettoyer_titre(cls, v: str) -> str:
        return v.strip().capitalize()


# ═══════════════════════════════════════════════════════════
# MAISON - PROJETS
# ═══════════════════════════════════════════════════════════


class ProjetInput(BaseModel):
    """
    Input pour créer/modifier un projet.
    """

    nom: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    categorie: str = Field(..., description="Catégorie du projet")
    priorite: str = Field(default="moyenne", description="Priorité")
    date_debut: Optional[date] = Field(None)
    date_fin_estimee: Optional[date] = Field(None, alias="date_fin")

    model_config = {"populate_by_name": True}

    @field_validator("nom")
    @classmethod
    def nettoyer_nom(cls, v: str) -> str:
        return v.strip().capitalize()

    @field_validator("priorite")
    @classmethod
    def valider_priorite(cls, v: str) -> str:
        """Valide la priorité"""
        priorites_valides = {"basse", "moyenne", "haute"}
        if v.lower() not in priorites_valides:
            raise ValueError(
                f"Priorité invalide. Doit être parmi: {', '.join(priorites_valides)}"
            )
        return v.lower()

    @model_validator(mode="after")
    def valider_dates(self) -> "ProjetInput":
        """Valide que la date de fin est après la date de début"""
        if (
            self.date_debut
            and self.date_fin_estimee
            and self.date_fin_estimee < self.date_debut
        ):
            raise ValueError("La date de fin doit être après la date de début")
        return self
