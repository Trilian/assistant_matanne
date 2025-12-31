"""
Validation Unifié - Tous les Validators Pydantic
Fusionne core/validation/validators.py
"""
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List
from datetime import date
import re


def clean_text(v: str) -> str:
    """Nettoie texte (évite injection)"""
    if not v:
        return v
    return re.sub(r"[<>{}]", "", v).strip()


# ════════════════════════════════════════════════════════════
# RECETTES
# ════════════════════════════════════════════════════════════

class IngredientInput(BaseModel):
    nom: str = Field(..., min_length=2, max_length=200)
    quantite: float = Field(..., gt=0, le=10000)
    unite: str = Field(..., min_length=1, max_length=50)
    optionnel: bool = False

    @field_validator("nom")
    @classmethod
    def clean_nom(cls, v):
        return clean_text(v)


class EtapeInput(BaseModel):
    ordre: int = Field(..., ge=1, le=50)
    description: str = Field(..., min_length=10, max_length=1000)
    duree: Optional[int] = Field(None, ge=0, le=300)

    @field_validator("description")
    @classmethod
    def clean_description(cls, v):
        return clean_text(v)


class RecetteInput(BaseModel):
    nom: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    temps_preparation: int = Field(..., gt=0, le=300)
    temps_cuisson: int = Field(..., ge=0, le=300)
    portions: int = Field(..., gt=0, le=20)
    difficulte: str = Field(..., pattern="^(facile|moyen|difficile)$")
    type_repas: str = Field(..., pattern="^(petit_déjeuner|déjeuner|dîner|goûter)$")
    saison: str = Field(..., pattern="^(printemps|été|automne|hiver|toute_année)$")
    ingredients: List[IngredientInput] = Field(..., min_length=1)
    etapes: List[EtapeInput] = Field(..., min_length=1)

    @field_validator("nom", "description")
    @classmethod
    def clean_strings(cls, v):
        return clean_text(v) if v else v

    @model_validator(mode="after")
    def validate_etapes_ordre(self):
        ordres = [e.ordre for e in self.etapes]
        if ordres != sorted(ordres):
            raise ValueError("Les étapes doivent être ordonnées")
        return self


# ════════════════════════════════════════════════════════════
# INVENTAIRE
# ════════════════════════════════════════════════════════════

class ArticleInventaireInput(BaseModel):
    nom: str = Field(..., min_length=2, max_length=200)
    categorie: str = Field(..., min_length=2, max_length=100)
    quantite: float = Field(..., ge=0, le=10000)
    unite: str = Field(..., min_length=1, max_length=50)
    seuil: float = Field(..., ge=0, le=1000)
    emplacement: Optional[str] = None
    date_peremption: Optional[date] = None

    @field_validator("nom", "categorie")
    @classmethod
    def clean_strings(cls, v):
        return clean_text(v) if v else v


# ════════════════════════════════════════════════════════════
# COURSES
# ════════════════════════════════════════════════════════════

class ArticleCoursesInput(BaseModel):
    nom: str = Field(..., min_length=2, max_length=200)
    quantite: float = Field(..., gt=0, le=10000)
    unite: str = Field(..., min_length=1, max_length=50)
    priorite: str = Field("moyenne", pattern="^(haute|moyenne|basse)$")
    magasin: Optional[str] = None

    @field_validator("nom")
    @classmethod
    def clean_nom(cls, v):
        return clean_text(v)


# ════════════════════════════════════════════════════════════
# PLANNING
# ════════════════════════════════════════════════════════════

class RepasInput(BaseModel):
    planning_id: int = Field(..., gt=0)
    jour_semaine: int = Field(..., ge=0, le=6)
    date_repas: date
    type_repas: str = Field(..., pattern="^(petit_déjeuner|déjeuner|dîner|goûter|bébé)$")
    recette_id: Optional[int] = Field(None, gt=0)
    portions: int = Field(4, gt=0, le=20)

    @model_validator(mode="after")
    def check_date_coherente(self):
        if self.date_repas.weekday() != self.jour_semaine:
            raise ValueError(f"Date ne correspond pas au jour {self.jour_semaine}")
        return self


# ════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════

def validate_model(model_class: BaseModel, data: dict) -> tuple[bool, str, Optional[BaseModel]]:
    """Helper validation générique"""
    try:
        validated = model_class(**data)
        return True, "", validated
    except Exception as e:
        error_msg = str(e)
        if "field required" in error_msg.lower():
            error_msg = "Champs obligatoires manquants"
        elif "validation error" in error_msg.lower():
            error_msg = "Données invalides"
        return False, error_msg, None