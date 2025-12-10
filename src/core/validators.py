"""
Validators Pydantic pour toutes les entrées utilisateur
Assure la sécurité et la cohérence des données
"""
from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, List, Dict
from datetime import date, datetime
import re


# ===================================
# VALIDATORS GÉNÉRIQUES
# ===================================

def clean_text(v: str) -> str:
    """Nettoie un texte (évite injection)"""
    if not v:
        return v

    # Supprimer caractères dangereux
    v = re.sub(r'[<>{}]', '', v)

    # Trim
    return v.strip()


def validate_positive(v: float) -> float:
    """Valide qu'un nombre est positif"""
    if v <= 0:
        raise ValueError("Doit être positif")
    return v


# ===================================
# RECETTES
# ===================================

class IngredientInput(BaseModel):
    """Validation ingrédient dans recette"""
    nom: str = Field(..., min_length=2, max_length=200)
    quantite: float = Field(..., gt=0, le=10000)
    unite: str = Field(..., min_length=1, max_length=50)
    optionnel: bool = False

    @validator('nom')
    def clean_nom(cls, v):
        return clean_text(v)

    @validator('quantite')
    def round_quantite(cls, v):
        return round(v, 2)


class EtapeInput(BaseModel):
    """Validation étape de recette"""
    ordre: int = Field(..., ge=1, le=50)
    description: str = Field(..., min_length=10, max_length=1000)
    duree: Optional[int] = Field(None, ge=0, le=300)

    @validator('description')
    def clean_description(cls, v):
        return clean_text(v)


class RecetteInput(BaseModel):
    """Validation création/modification recette"""
    nom: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    temps_preparation: int = Field(..., gt=0, le=300)
    temps_cuisson: int = Field(..., ge=0, le=300)
    portions: int = Field(..., gt=0, le=20)
    difficulte: str = Field(..., regex="^(facile|moyen|difficile)$")
    type_repas: str = Field(
        ...,
        regex="^(petit_déjeuner|déjeuner|dîner|goûter)$"
    )
    saison: str = Field(
        ...,
        regex="^(printemps|été|automne|hiver|toute_année)$"
    )
    categorie: Optional[str] = Field(None, max_length=100)

    est_rapide: bool = False
    est_equilibre: bool = False
    compatible_bebe: bool = False
    compatible_batch: bool = False
    congelable: bool = False

    url_image: Optional[str] = Field(None, max_length=500)

    ingredients: List[IngredientInput] = Field(..., min_items=1, max_items=50)
    etapes: List[EtapeInput] = Field(..., min_items=1, max_items=30)

    @validator('nom', 'description')
    def clean_strings(cls, v):
        return clean_text(v) if v else v

    @validator('url_image')
    def validate_url(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError("URL doit commencer par http:// ou https://")
        return v

    @root_validator
    def check_temps_coherent(cls, values):
        """Vérifie cohérence des temps"""
        prep = values.get('temps_preparation', 0)
        cuisson = values.get('temps_cuisson', 0)

        # Auto-marquer rapide si < 30min
        if prep + cuisson < 30:
            values['est_rapide'] = True

        return values

    @validator('etapes')
    def check_etapes_ordre(cls, v):
        """Vérifie que les étapes sont bien ordonnées"""
        ordres = [e.ordre for e in v]
        if ordres != sorted(ordres):
            raise ValueError("Les étapes doivent être ordonnées séquentiellement")

        # Vérifier pas de doublons
        if len(ordres) != len(set(ordres)):
            raise ValueError("Ordre d'étapes dupliqué")

        return v


# ===================================
# INVENTAIRE
# ===================================

class ArticleInventaireInput(BaseModel):
    """Validation article inventaire"""
    nom: str = Field(..., min_length=2, max_length=200)
    categorie: str = Field(..., min_length=2, max_length=100)
    quantite: float = Field(..., ge=0, le=10000)
    unite: str = Field(..., min_length=1, max_length=50)
    quantite_min: float = Field(..., ge=0, le=1000)
    emplacement: Optional[str] = Field(None, max_length=100)
    date_peremption: Optional[date] = None

    @validator('nom', 'categorie', 'emplacement')
    def clean_strings(cls, v):
        return clean_text(v) if v else v

    @validator('date_peremption')
    def check_date_future(cls, v):
        if v and v < date.today():
            raise ValueError("Date de péremption ne peut être dans le passé")
        return v

    @root_validator
    def check_quantites(cls, values):
        """Vérifie que seuil <= quantité"""
        qty = values.get('quantite', 0)
        seuil = values.get('quantite_min', 0)

        if seuil > qty:
            # Warning, pas erreur (peut être volontaire)
            pass

        return values


class AjustementStockInput(BaseModel):
    """Validation ajustement stock"""
    article_id: int = Field(..., gt=0)
    delta: float = Field(..., ge=-10000, le=10000)
    raison: Optional[str] = Field(None, max_length=200)

    @validator('delta')
    def check_delta_non_zero(cls, v):
        if v == 0:
            raise ValueError("Delta ne peut être zéro")
        return v


# ===================================
# COURSES
# ===================================

class ArticleCoursesInput(BaseModel):
    """Validation article de courses"""
    nom: str = Field(..., min_length=2, max_length=200)
    quantite: float = Field(..., gt=0, le=10000)
    unite: str = Field(..., min_length=1, max_length=50)
    priorite: str = Field("moyenne", regex="^(haute|moyenne|basse)$")
    magasin: Optional[str] = Field(None, max_length=100)
    rayon: Optional[str] = Field(None, max_length=100)

    @validator('nom')
    def clean_nom(cls, v):
        return clean_text(v)


# ===================================
# PLANNING
# ===================================

class RepasInput(BaseModel):
    """Validation ajout repas au planning"""
    planning_id: int = Field(..., gt=0)
    jour_semaine: int = Field(..., ge=0, le=6)
    date_repas: date
    type_repas: str = Field(
        ...,
        regex="^(petit_déjeuner|déjeuner|dîner|goûter|bébé|batch_cooking)$"
    )
    recette_id: Optional[int] = Field(None, gt=0)
    portions: int = Field(4, gt=0, le=20)
    est_adapte_bebe: bool = False
    est_batch_cooking: bool = False
    notes: Optional[str] = Field(None, max_length=500)

    @validator('date_repas')
    def check_date_coherente(cls, v, values):
        """Vérifie que date correspond au jour_semaine"""
        jour = values.get('jour_semaine')
        if jour is not None and v.weekday() != jour:
            raise ValueError(
                f"Date {v} ne correspond pas au jour {jour} (attendu: {v.weekday()})"
            )
        return v


# ===================================
# FAMILLE
# ===================================

class ProfilEnfantInput(BaseModel):
    """Validation profil enfant"""
    prenom: str = Field(..., min_length=2, max_length=100)
    date_naissance: date
    url_photo: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=2000)

    @validator('prenom')
    def clean_prenom(cls, v):
        return clean_text(v)

    @validator('date_naissance')
    def check_date_passee(cls, v):
        if v > date.today():
            raise ValueError("Date de naissance ne peut être future")

        # Vérifier pas trop vieux (max 18 ans)
        age_jours = (date.today() - v).days
        if age_jours > 18 * 365:
            raise ValueError("Profil enfant limité à 18 ans")

        return v


class EntreeBienEtreInput(BaseModel):
    """Validation entrée bien-être"""
    enfant_id: Optional[int] = Field(None, gt=0)
    date_entree: date = Field(default_factory=date.today)
    humeur: str = Field(..., regex="^(😊 Bien|😐 Moyen|😞 Mal)$")
    heures_sommeil: Optional[float] = Field(None, ge=0, le=24)
    activite: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = Field(None, max_length=1000)
    nom_utilisateur: Optional[str] = Field(None, max_length=100)

    @validator('heures_sommeil')
    def round_heures(cls, v):
        return round(v, 1) if v else v

    @validator('date_entree')
    def check_date_valide(cls, v):
        # Pas plus de 30 jours dans le passé
        delta = (date.today() - v).days
        if delta > 30:
            raise ValueError("Entrée ne peut dater de plus de 30 jours")

        if v > date.today():
            raise ValueError("Date ne peut être future")

        return v


# ===================================
# PROJETS
# ===================================

class ProjetInput(BaseModel):
    """Validation projet"""
    nom: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    categorie: Optional[str] = Field(None, max_length=100)
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    priorite: str = Field("moyenne", regex="^(haute|moyenne|basse)$")
    statut: str = Field(
        "à faire",
        regex="^(à faire|en cours|terminé|annulé)$"
    )
    progression: int = Field(0, ge=0, le=100)

    @validator('nom', 'description')
    def clean_strings(cls, v):
        return clean_text(v) if v else v

    @root_validator
    def check_dates_coherentes(cls, values):
        debut = values.get('date_debut')
        fin = values.get('date_fin')

        if debut and fin and fin < debut:
            raise ValueError("Date de fin ne peut être avant date de début")

        return values

    @root_validator
    def auto_update_statut(cls, values):
        """Auto-détecte le statut selon progression"""
        prog = values.get('progression', 0)
        statut = values.get('statut')

        if prog == 100 and statut not in ['terminé', 'annulé']:
            values['statut'] = 'terminé'
        elif prog > 0 and statut == 'à faire':
            values['statut'] = 'en cours'

        return values


# ===================================
# HELPERS DE VALIDATION
# ===================================

def validate_model(model_class: BaseModel, data: dict) -> tuple[bool, str, Optional[BaseModel]]:
    """
    Helper de validation générique

    Returns:
        (success: bool, error_message: str, validated_data: Optional[Model])

    Usage:
        success, error, validated = validate_model(RecetteInput, form_data)
        if not success:
            st.error(error)
        else:
            # Utiliser validated.dict()
    """
    try:
        validated = model_class(**data)
        return True, "", validated

    except Exception as e:
        # Parser l'erreur Pydantic
        error_msg = str(e)

        # Simplifier pour l'utilisateur
        if "field required" in error_msg.lower():
            error_msg = "Champs obligatoires manquants"
        elif "validation error" in error_msg.lower():
            error_msg = "Données invalides"

        return False, error_msg, None


def validate_and_clean(model_class: BaseModel, data: dict) -> dict:
    """
    Valide et retourne dict nettoyé (ou raise)

    Usage:
        clean_data = validate_and_clean(RecetteInput, form_data)
    """
    validated = model_class(**data)
    return validated.dict(exclude_unset=True)