"""
Validators Consolidés - VERSION UNIFIÉE
Centralise tous les validators Pydantic

Structure:
- src/core/validation/
  ├── __init__.py (exports)
  ├── validators.py (ce fichier - Pydantic models)
  └── functions.py (fonctions de validation pures)

"""
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Dict
from datetime import date
import re


# ═══════════════════════════════════════════════════════════
# HELPERS VALIDATION
# ═══════════════════════════════════════════════════════════

def clean_text(v: str) -> str:
    """Nettoie texte (évite injection)"""
    if not v:
        return v
    v = re.sub(r"[<>{}]", "", v)
    return v.strip()


def validate_positive(v: float, field_name: str = "valeur") -> float:
    """Valide nombre positif"""
    if v <= 0:
        raise ValueError(f"{field_name} doit être positif")
    return v


# ═══════════════════════════════════════════════════════════
# RECETTES
# ═══════════════════════════════════════════════════════════

class IngredientInput(BaseModel):
    """Validation ingrédient dans recette"""
    nom: str = Field(..., min_length=2, max_length=200)
    quantite: float = Field(..., gt=0, le=10000)
    unite: str = Field(..., min_length=1, max_length=50)
    optionnel: bool = False

    @field_validator("nom")
    @classmethod
    def clean_nom(cls, v):
        return clean_text(v)

    @field_validator("quantite")
    @classmethod
    def round_quantite(cls, v):
        return round(v, 2)


class EtapeInput(BaseModel):
    """Validation étape recette"""
    ordre: int = Field(..., ge=1, le=50)
    description: str = Field(..., min_length=10, max_length=1000)
    duree: Optional[int] = Field(None, ge=0, le=300)

    @field_validator("description")
    @classmethod
    def clean_description(cls, v):
        return clean_text(v)


class RecetteInput(BaseModel):
    """Validation création/modification recette"""
    nom: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    temps_preparation: int = Field(..., gt=0, le=300)
    temps_cuisson: int = Field(..., ge=0, le=300)
    portions: int = Field(..., gt=0, le=20)
    difficulte: str = Field(..., pattern="^(facile|moyen|difficile)$")
    type_repas: str = Field(..., pattern="^(petit_déjeuner|déjeuner|dîner|goûter)$")
    saison: str = Field(..., pattern="^(printemps|été|automne|hiver|toute_année)$")
    categorie: Optional[str] = Field(None, max_length=100)

    est_rapide: bool = False
    est_equilibre: bool = False
    compatible_bebe: bool = False
    compatible_batch: bool = False
    congelable: bool = False

    url_image: Optional[str] = Field(None, max_length=500)

    ingredients: List[IngredientInput] = Field(..., min_length=1, max_length=50)
    etapes: List[EtapeInput] = Field(..., min_length=1, max_length=30)

    @field_validator("nom", "description")
    @classmethod
    def clean_strings(cls, v):
        return clean_text(v) if v else v

    @field_validator("url_image")
    @classmethod
    def validate_url(cls, v):
        if v and not v.startswith(("http://", "https://")):
            raise ValueError("URL doit commencer par http:// ou https://")
        return v

    @model_validator(mode="after")
    def check_temps_coherent(self):
        """Auto-marquer rapide si < 30min"""
        if self.temps_preparation + self.temps_cuisson < 30:
            self.est_rapide = True
        return self

    @field_validator("etapes")
    @classmethod
    def check_etapes_ordre(cls, v):
        """Vérifie ordre séquentiel"""
        ordres = [e.ordre for e in v]
        if ordres != sorted(ordres):
            raise ValueError("Les étapes doivent être ordonnées")
        if len(ordres) != len(set(ordres)):
            raise ValueError("Ordre d'étapes dupliqué")
        return v


# ═══════════════════════════════════════════════════════════
# INVENTAIRE
# ═══════════════════════════════════════════════════════════

class ArticleInventaireInput(BaseModel):
    """Validation article inventaire"""
    nom: str = Field(..., min_length=2, max_length=200)
    categorie: str = Field(..., min_length=2, max_length=100)
    quantite: float = Field(..., ge=0, le=10000)
    unite: str = Field(..., min_length=1, max_length=50)
    quantite_min: float = Field(..., ge=0, le=1000)
    emplacement: Optional[str] = Field(None, max_length=100)
    date_peremption: Optional[date] = None

    @field_validator("nom", "categorie", "emplacement")
    @classmethod
    def clean_strings(cls, v):
        return clean_text(v) if v else v

    @field_validator("date_peremption")
    @classmethod
    def check_date_future(cls, v):
        if v and v < date.today():
            raise ValueError("Date de péremption ne peut être passée")
        return v


class AjustementStockInput(BaseModel):
    """Validation ajustement stock"""
    article_id: int = Field(..., gt=0)
    delta: float = Field(..., ge=-10000, le=10000)
    raison: Optional[str] = Field(None, max_length=200)

    @field_validator("delta")
    @classmethod
    def check_delta_non_zero(cls, v):
        if v == 0:
            raise ValueError("Delta ne peut être zéro")
        return v


# ═══════════════════════════════════════════════════════════
# COURSES
# ═══════════════════════════════════════════════════════════

class ArticleCoursesInput(BaseModel):
    """Validation article courses"""
    nom: str = Field(..., min_length=2, max_length=200)
    quantite: float = Field(..., gt=0, le=10000)
    unite: str = Field(..., min_length=1, max_length=50)
    priorite: str = Field("moyenne", pattern="^(haute|moyenne|basse)$")
    magasin: Optional[str] = Field(None, max_length=100)
    rayon: Optional[str] = Field(None, max_length=100)

    @field_validator("nom")
    @classmethod
    def clean_nom(cls, v):
        return clean_text(v)


# ═══════════════════════════════════════════════════════════
# PLANNING
# ═══════════════════════════════════════════════════════════

class RepasInput(BaseModel):
    """Validation ajout repas planning"""
    planning_id: int = Field(..., gt=0)
    jour_semaine: int = Field(..., ge=0, le=6)
    date_repas: date
    type_repas: str = Field(
        ...,
        pattern="^(petit_déjeuner|déjeuner|dîner|goûter|bébé|batch_cooking)$"
    )
    recette_id: Optional[int] = Field(None, gt=0)
    portions: int = Field(4, gt=0, le=20)
    est_adapte_bebe: bool = False
    est_batch_cooking: bool = False
    notes: Optional[str] = Field(None, max_length=500)

    @model_validator(mode="after")
    def check_date_coherente(self):
        """Vérifie cohérence date/jour"""
        if self.date_repas.weekday() != self.jour_semaine:
            raise ValueError(
                f"Date ne correspond pas au jour {self.jour_semaine}"
            )
        return self


# ═══════════════════════════════════════════════════════════
# FAMILLE
# ═══════════════════════════════════════════════════════════

class ProfilEnfantInput(BaseModel):
    """Validation profil enfant"""
    prenom: str = Field(..., min_length=2, max_length=100)
    date_naissance: date
    url_photo: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=2000)

    @field_validator("prenom")
    @classmethod
    def clean_prenom(cls, v):
        return clean_text(v)

    @field_validator("date_naissance")
    @classmethod
    def check_date_passee(cls, v):
        if v > date.today():
            raise ValueError("Date de naissance ne peut être future")

        age_jours = (date.today() - v).days
        if age_jours > 18 * 365:
            raise ValueError("Profil enfant limité à 18 ans")

        return v


class EntreeBienEtreInput(BaseModel):
    """Validation entrée bien-être"""
    enfant_id: Optional[int] = Field(None, gt=0)
    date_entree: date = Field(default_factory=date.today)
    humeur: str = Field(..., pattern="^(😊 Bien|😐 Moyen|😞 Mal)$")
    heures_sommeil: Optional[float] = Field(None, ge=0, le=24)
    activite: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = Field(None, max_length=1000)
    nom_utilisateur: Optional[str] = Field(None, max_length=100)

    @field_validator("heures_sommeil")
    @classmethod
    def round_heures(cls, v):
        return round(v, 1) if v else v

    @field_validator("date_entree")
    @classmethod
    def check_date_valide(cls, v):
        delta = (date.today() - v).days
        if delta > 30:
            raise ValueError("Entrée ne peut dater de plus de 30 jours")
        if v > date.today():
            raise ValueError("Date ne peut être future")
        return v


# ═══════════════════════════════════════════════════════════
# PROJETS
# ═══════════════════════════════════════════════════════════

class ProjetInput(BaseModel):
    """Validation projet"""
    nom: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    categorie: Optional[str] = Field(None, max_length=100)
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    priorite: str = Field("moyenne", pattern="^(haute|moyenne|basse)$")
    statut: str = Field("à faire", pattern="^(à faire|en cours|terminé|annulé)$")
    progression: int = Field(0, ge=0, le=100)

    @field_validator("nom", "description")
    @classmethod
    def clean_strings(cls, v):
        return clean_text(v) if v else v

    @model_validator(mode="after")
    def check_dates_coherentes(self):
        """Vérifie cohérence dates"""
        if self.date_debut and self.date_fin:
            if self.date_fin < self.date_debut:
                raise ValueError("Date fin < date début")
        return self

    @model_validator(mode="after")
    def auto_update_statut(self):
        """Auto-détecte statut selon progression"""
        if self.progression == 100 and self.statut not in ["terminé", "annulé"]:
            self.statut = "terminé"
        elif self.progression > 0 and self.statut == "à faire":
            self.statut = "en cours"
        return self


# ═══════════════════════════════════════════════════════════
# HELPERS VALIDATION
# ═══════════════════════════════════════════════════════════

def validate_model(
        model_class: BaseModel,
        data: dict
) -> tuple[bool, str, Optional[BaseModel]]:
    """
    Helper validation générique

    Args:
        model_class: Classe Pydantic
        data: Données à valider

    Returns:
        (success: bool, error_message: str, validated_data: Optional[Model])

    Usage:
        success, error, validated = validate_model(RecetteInput, data)
        if not success:
            st.error(error)
    """
    try:
        validated = model_class(**data)
        return True, "", validated
    except Exception as e:
        error_msg = str(e)

        # Simplifier messages d'erreur
        if "field required" in error_msg.lower():
            error_msg = "Champs obligatoires manquants"
        elif "validation error" in error_msg.lower():
            error_msg = "Données invalides"

        return False, error_msg, None


def validate_and_clean(model_class: BaseModel, data: dict) -> dict:
    """
    Valide et retourne dict nettoyé

    Args:
        model_class: Classe Pydantic
        data: Données

    Returns:
        Dict validé et nettoyé

    Raises:
        ValidationError si invalide

    Usage:
        cleaned = validate_and_clean(RecetteInput, data)
    """
    validated = model_class(**data)
    return validated.model_dump(exclude_unset=True)