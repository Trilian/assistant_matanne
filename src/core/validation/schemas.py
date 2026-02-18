"""
Schemas - Modèles Pydantic pour validation métier.

Contient:
- Schémas de validation pour recettes, inventaire, courses
- Schémas pour planning, famille, projets
- Schémas dict-based pour formulaires simples
"""

import re
from datetime import date

from pydantic import BaseModel, Field, field_validator, model_validator

# Import des constantes avec gestion d'erreur
try:
    from ..constants import (
        MAX_ETAPES,
        MAX_INGREDIENTS,
        MAX_LENGTH_LONG,
        MAX_LENGTH_MEDIUM,
        MAX_LENGTH_SHORT,
        MAX_LENGTH_TEXT,
        MAX_PORTIONS,
        MAX_QUANTITE,
        MAX_TEMPS_CUISSON,
        MAX_TEMPS_PREPARATION,
        MIN_ETAPES,
        MIN_INGREDIENTS,
    )
except ImportError:
    # Valeurs par défaut si constants.py n'est pas disponible
    MAX_LENGTH_SHORT = 100
    MAX_LENGTH_MEDIUM = 200
    MAX_LENGTH_LONG = 1000
    MAX_LENGTH_TEXT = 2000
    MAX_PORTIONS = 20
    MAX_TEMPS_PREPARATION = 300
    MAX_TEMPS_CUISSON = 300
    MAX_QUANTITE = 10000
    MIN_INGREDIENTS = 1
    MAX_INGREDIENTS = 50
    MIN_ETAPES = 1
    MAX_ETAPES = 50


def nettoyer_texte(v: str) -> str:
    """
    Helper de nettoyage pour validators Pydantic.

    Args:
        v: Texte à nettoyer

    Returns:
        Texte nettoyé
    """
    if not v:
        return v
    return re.sub(r"[<>{}]", "", v).strip()


# ═══════════════════════════════════════════════════════════
# RECETTES
# ═══════════════════════════════════════════════════════════


class IngredientInput(BaseModel):
    """
    Validation d'un ingrédient.

    Attributes:
        nom: Nom de l'ingrédient
        quantite: Quantité nécessaire (optionnel)
        unite: Unité de mesure (optionnel)
        optionnel: Est-ce optionnel
    """

    nom: str = Field(..., min_length=1, max_length=MAX_LENGTH_MEDIUM)
    quantite: float | None = Field(None, ge=0.01, le=MAX_QUANTITE)
    unite: str | None = Field(None, max_length=50)
    optionnel: bool = False

    @field_validator("nom")
    @classmethod
    def nettoyer_nom(cls, v: str) -> str:
        """Nettoie et normalise le nom"""
        return v.strip().capitalize()


class EtapeInput(BaseModel):
    """
    Validation d'une étape de recette.

    Attributes:
        numero: Numéro de l'étape (alias: ordre)
        ordre: Ordre de l'étape (alias de numero)
        description: Description de l'étape
        duree: Durée en minutes (optionnelle)
    """

    numero: int | None = Field(None, ge=1, le=MAX_ETAPES, description="Numéro de l'étape")
    ordre: int | None = Field(
        None, ge=1, le=MAX_ETAPES, description="Ordre de l'étape (alias de numero)"
    )
    description: str = Field(..., min_length=1, max_length=MAX_LENGTH_LONG)
    duree: int | None = Field(None, ge=0, le=MAX_TEMPS_CUISSON)

    model_config = {"populate_by_name": True}

    @field_validator("description")
    @classmethod
    def nettoyer_description(cls, v):
        return nettoyer_texte(v) if v else v

    @model_validator(mode="after")
    def valider_numero_ou_ordre(self) -> "EtapeInput":
        """Assure qu'au moins un de numero ou ordre est fourni"""
        if self.numero is None and self.ordre is None:
            raise ValueError("Soit 'numero' soit 'ordre' doit être fourni")
        # Utiliser ordre si numero n'est pas fourni
        if self.numero is None and self.ordre is not None:
            self.numero = self.ordre
        return self


class RecetteInput(BaseModel):
    """
    Validation complète d'une recette.

    Attributes:
        nom: Nom de la recette
        description: Description (optionnelle)
        temps_preparation: Temps de préparation en minutes
        temps_cuisson: Temps de cuisson en minutes
        portions: Nombre de portions
        difficulte: Niveau de difficulté
        type_repas: Type de repas
        saison: Saison recommandée
        ingredients: Liste des ingrédients
        etapes: Liste des étapes
    """

    nom: str = Field(..., min_length=1, max_length=MAX_LENGTH_MEDIUM)
    description: str | None = Field(None, max_length=MAX_LENGTH_TEXT)
    temps_preparation: int = Field(..., ge=1, le=MAX_TEMPS_PREPARATION)
    temps_cuisson: int = Field(..., ge=0, le=MAX_TEMPS_CUISSON)
    portions: int = Field(default=4, ge=1, le=MAX_PORTIONS)
    difficulte: str = Field(default="moyen", description="Niveau de difficulté")
    type_repas: str = Field(..., description="Type de repas")
    saison: str | None = Field(None, description="Saison (printemps, été, automne, hiver)")
    url_image: str | None = Field(None, max_length=500, description="URL ou chemin de l'image")
    ingredients: list[IngredientInput] = Field(
        ..., min_length=MIN_INGREDIENTS, max_length=MAX_INGREDIENTS
    )
    etapes: list[EtapeInput] = Field(..., min_length=MIN_ETAPES, max_length=MAX_ETAPES)

    @field_validator("nom")
    @classmethod
    def valider_nom(cls, v: str) -> str:
        """Nettoie et valide le nom"""
        cleaned = v.strip()
        if cleaned:
            cleaned = cleaned[0].upper() + cleaned[1:] if len(cleaned) > 1 else cleaned.upper()
        if len(cleaned) < 2:
            raise ValueError("Le nom doit contenir au moins 2 caractères")
        return cleaned

    @field_validator("difficulte")
    @classmethod
    def valider_difficulte(cls, v: str) -> str:
        """Valide la difficulté"""
        difficultes_valides = {"facile", "moyen", "difficile"}
        if v.lower() not in difficultes_valides:
            raise ValueError(
                f"Difficulté invalide. Doit être parmi: {', '.join(difficultes_valides)}"
            )
        return v.lower()

    @field_validator("type_repas")
    @classmethod
    def valider_type_repas(cls, v: str) -> str:
        """Valide le type de repas"""
        types_valides = {"petit_déjeuner", "déjeuner", "dîner", "goûter", "apéritif", "dessert"}
        if v.lower() not in types_valides:
            raise ValueError(f"Type de repas invalide. Doit être parmi: {', '.join(types_valides)}")
        return v.lower()

    @field_validator("saison")
    @classmethod
    def valider_saison(cls, v: str | None) -> str | None:
        """Valide la saison"""
        if v:
            saisons_valides = {"printemps", "été", "automne", "hiver", "toute_année"}
            if v.lower() not in saisons_valides:
                raise ValueError(f"Saison invalide. Doit être parmi: {', '.join(saisons_valides)}")
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


class ArticleInventaireInput(BaseModel):
    """
    Validation d'un article inventaire.

    Attributes:
        nom: Nom de l'article
        categorie: Catégorie
        quantite: Quantité en stock
        unite: Unité de mesure
        quantite_min: Seuil minimal
        emplacement: Lieu de stockage (optionnel)
        date_peremption: Date de péremption (optionnelle)
    """

    nom: str = Field(..., min_length=2, max_length=MAX_LENGTH_MEDIUM)
    categorie: str = Field(..., min_length=2, max_length=MAX_LENGTH_SHORT)
    quantite: float = Field(..., ge=0, le=MAX_QUANTITE)
    unite: str = Field(..., min_length=1, max_length=50)
    quantite_min: float = Field(..., ge=0, le=1000)
    emplacement: str | None = None
    date_peremption: date | None = None

    @field_validator("nom", "categorie")
    @classmethod
    def nettoyer_chaines(cls, v):
        return nettoyer_texte(v) if v else v


class IngredientStockInput(BaseModel):
    """
    Input pour ajouter/modifier un article en inventaire.
    """

    nom: str = Field(..., min_length=1, max_length=200)
    quantite: float = Field(..., ge=0.01)
    unite: str = Field(..., min_length=1, max_length=50)
    date_expiration: date | None = Field(None, description="Date d'expiration")
    localisation: str | None = Field(None, max_length=200)
    prix_unitaire: float | None = Field(None, ge=0)

    @field_validator("nom")
    @classmethod
    def nettoyer_nom(cls, v: str) -> str:
        return v.strip().capitalize()

    @field_validator("localisation")
    @classmethod
    def nettoyer_localisation(cls, v: str | None) -> str | None:
        if v:
            return v.strip().capitalize()
        return None


# ═══════════════════════════════════════════════════════════
# COURSES
# ═══════════════════════════════════════════════════════════


class ArticleCoursesInput(BaseModel):
    """
    Validation d'un article courses.

    Attributes:
        nom: Nom de l'article
        quantite: Quantité à acheter
        unite: Unité de mesure
        priorite: Priorité d'achat
        magasin: Magasin cible (optionnel)
    """

    nom: str = Field(..., min_length=2, max_length=MAX_LENGTH_MEDIUM)
    quantite: float = Field(..., gt=0, le=MAX_QUANTITE)
    unite: str = Field(..., min_length=1, max_length=50)
    priorite: str = Field("moyenne", pattern="^(haute|moyenne|basse)$")
    magasin: str | None = None

    @field_validator("nom")
    @classmethod
    def nettoyer_nom(cls, v):
        return nettoyer_texte(v)


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


# ═══════════════════════════════════════════════════════════
# FAMILLE
# ═══════════════════════════════════════════════════════════


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


# ═══════════════════════════════════════════════════════════
# MAISON - PROJETS
# ═══════════════════════════════════════════════════════════


class ProjetInput(BaseModel):
    """
    Input pour créer/modifier un projet.
    """

    nom: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    categorie: str = Field(..., description="Catégorie du projet")
    priorite: str = Field(default="moyenne", description="Priorité")
    date_debut: date | None = Field(None)
    date_fin_estimee: date | None = Field(None, alias="date_fin")

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
            raise ValueError(f"Priorité invalide. Doit être parmi: {', '.join(priorites_valides)}")
        return v.lower()

    @model_validator(mode="after")
    def valider_dates(self) -> "ProjetInput":
        """Valide que la date de fin est après la date de début"""
        if self.date_debut and self.date_fin_estimee and self.date_fin_estimee < self.date_debut:
            raise ValueError("La date de fin doit être après la date de début")
        return self


# ═══════════════════════════════════════════════════════════
# SCHÉMAS DICT-BASED (pour formulaires simples)
# ═══════════════════════════════════════════════════════════

SCHEMA_RECETTE = {
    "nom": {"type": "string", "max_length": MAX_LENGTH_MEDIUM, "required": True, "label": "Nom"},
    "description": {"type": "string", "max_length": MAX_LENGTH_TEXT, "label": "Description"},
    "temps_preparation": {
        "type": "number",
        "min": 0,
        "max": MAX_TEMPS_PREPARATION,
        "required": True,
        "label": "Temps préparation",
    },
    "temps_cuisson": {
        "type": "number",
        "min": 0,
        "max": MAX_TEMPS_CUISSON,
        "required": True,
        "label": "Temps cuisson",
    },
    "portions": {
        "type": "number",
        "min": 1,
        "max": MAX_PORTIONS,
        "required": True,
        "label": "Portions",
    },
}

SCHEMA_INVENTAIRE = {
    "nom": {"type": "string", "max_length": MAX_LENGTH_MEDIUM, "required": True, "label": "Nom"},
    "categorie": {
        "type": "string",
        "max_length": MAX_LENGTH_SHORT,
        "required": True,
        "label": "Catégorie",
    },
    "quantite": {
        "type": "number",
        "min": 0,
        "max": MAX_QUANTITE,
        "required": True,
        "label": "Quantité",
    },
    "unite": {"type": "string", "max_length": 50, "required": True, "label": "Unité"},
    "quantite_min": {"type": "number", "min": 0, "max": 1000, "label": "Seuil"},
    "emplacement": {"type": "string", "max_length": MAX_LENGTH_SHORT, "label": "Emplacement"},
    "date_peremption": {"type": "date", "label": "Date péremption"},
}

SCHEMA_COURSES = {
    "nom": {
        "type": "string",
        "max_length": MAX_LENGTH_MEDIUM,
        "required": True,
        "label": "Article",
    },
    "quantite": {
        "type": "number",
        "min": 0.1,
        "max": MAX_QUANTITE,
        "required": True,
        "label": "Quantité",
    },
    "unite": {"type": "string", "max_length": 50, "required": True, "label": "Unité"},
    "priorite": {"type": "string", "max_length": 20, "label": "Priorité"},
    "magasin": {"type": "string", "max_length": MAX_LENGTH_SHORT, "label": "Magasin"},
}
