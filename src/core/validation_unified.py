"""
Validation Unifiée - Fusion de validation.py + validation_middleware.py
Validation Pydantic + Sanitization + Sécurité
"""
import re
import html
import logging
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from functools import wraps
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator, model_validator, ValidationError

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SANITIZATION (XSS, SQL Injection)
# ═══════════════════════════════════════════════════════════

class InputSanitizer:
    """Sanitizer universel pour tous les inputs"""

    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe',
        r'<object',
        r'<embed',
    ]

    SQL_PATTERNS = [
        r"('\s*(OR|AND)\s*'?\d)",
        r'("\s*(OR|AND)\s*"?\d)',
        r'(;\s*DROP\s+TABLE)',
        r'(;\s*DELETE\s+FROM)',
        r'(UNION\s+SELECT)',
    ]

    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """Nettoie une chaîne (XSS, SQL injection)"""
        if not value or not isinstance(value, str):
            return ""

        value = value[:max_length]
        value = html.escape(value)

        for pattern in InputSanitizer.XSS_PATTERNS:
            value = re.sub(pattern, '', value, flags=re.IGNORECASE)

        for pattern in InputSanitizer.SQL_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"⚠️ Tentative SQL injection: {value[:50]}")

        value = re.sub(r'[\x00-\x1F\x7F]', '', value)
        return value.strip()

    @staticmethod
    def sanitize_number(value: Any, min_val: float = None, max_val: float = None) -> Optional[float]:
        """Valide et nettoie un nombre"""
        try:
            if isinstance(value, str):
                value = value.replace(',', '.')
            num = float(value)

            if min_val is not None and num < min_val:
                return min_val
            if max_val is not None and num > max_val:
                return max_val

            return num
        except (ValueError, TypeError):
            return None

    @staticmethod
    def sanitize_date(value: Any) -> Optional[date]:
        """Valide et nettoie une date"""
        if isinstance(value, date):
            return value
        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, str):
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']:
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
        return None

    @staticmethod
    def sanitize_email(value: str) -> Optional[str]:
        """Valide un email"""
        if not value or not isinstance(value, str):
            return None

        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        value = value.strip().lower()

        if re.match(pattern, value):
            return value
        return None

    @staticmethod
    def sanitize_dict(data: Dict, schema: Dict) -> Dict:
        """Nettoie un dictionnaire selon un schéma"""
        sanitized = {}

        for field, rules in schema.items():
            value = data.get(field)

            if rules.get("required", False) and not value:
                continue

            if value is None and not rules.get("required", False):
                continue

            field_type = rules.get("type", "string")

            if field_type == "string":
                sanitized[field] = InputSanitizer.sanitize_string(
                    value,
                    max_length=rules.get("max_length", 1000)
                )
            elif field_type == "number":
                sanitized[field] = InputSanitizer.sanitize_number(
                    value,
                    min_val=rules.get("min"),
                    max_val=rules.get("max")
                )
            elif field_type == "date":
                sanitized[field] = InputSanitizer.sanitize_date(value)
            elif field_type == "email":
                sanitized[field] = InputSanitizer.sanitize_email(value)
            elif field_type == "list":
                if isinstance(value, list):
                    sanitized[field] = [
                        InputSanitizer.sanitize_string(str(item))
                        for item in value
                    ]
            else:
                sanitized[field] = value

        return sanitized


# ═══════════════════════════════════════════════════════════
# MODÈLES PYDANTIC (Validation Métier)
# ═══════════════════════════════════════════════════════════

def clean_text(v: str) -> str:
    """Helper nettoyage texte"""
    if not v:
        return v
    return re.sub(r"[<>{}]", "", v).strip()


# --- RECETTES ---

class IngredientInput(BaseModel):
    """Validation ingrédient"""
    nom: str = Field(..., min_length=2, max_length=200)
    quantite: float = Field(..., gt=0, le=10000)
    unite: str = Field(..., min_length=1, max_length=50)
    optionnel: bool = False

    @field_validator("nom")
    @classmethod
    def clean_nom(cls, v):
        return clean_text(v)


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
    """Validation recette complète"""
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


# --- INVENTAIRE ---

class ArticleInventaireInput(BaseModel):
    """Validation article inventaire"""
    nom: str = Field(..., min_length=2, max_length=200)
    categorie: str = Field(..., min_length=2, max_length=100)
    quantite: float = Field(..., ge=0, le=10000)
    unite: str = Field(..., min_length=1, max_length=50)
    quantite_min: float = Field(..., ge=0, le=1000)
    emplacement: Optional[str] = None
    date_peremption: Optional[date] = None

    @field_validator("nom", "categorie")
    @classmethod
    def clean_strings(cls, v):
        return clean_text(v) if v else v


# --- COURSES ---

class ArticleCoursesInput(BaseModel):
    """Validation article courses"""
    nom: str = Field(..., min_length=2, max_length=200)
    quantite: float = Field(..., gt=0, le=10000)
    unite: str = Field(..., min_length=1, max_length=50)
    priorite: str = Field("moyenne", pattern="^(haute|moyenne|basse)$")
    magasin: Optional[str] = None

    @field_validator("nom")
    @classmethod
    def clean_nom(cls, v):
        return clean_text(v)


# --- PLANNING ---

class RepasInput(BaseModel):
    """Validation repas planning"""
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


# ═══════════════════════════════════════════════════════════
# SCHÉMAS DE VALIDATION (Dict-based)
# ═══════════════════════════════════════════════════════════

RECETTE_SCHEMA = {
    "nom": {"type": "string", "max_length": 200, "required": True, "label": "Nom"},
    "description": {"type": "string", "max_length": 2000, "label": "Description"},
    "temps_preparation": {"type": "number", "min": 0, "max": 300, "required": True, "label": "Temps préparation"},
    "temps_cuisson": {"type": "number", "min": 0, "max": 300, "required": True, "label": "Temps cuisson"},
    "portions": {"type": "number", "min": 1, "max": 20, "required": True, "label": "Portions"},
}

INVENTAIRE_SCHEMA = {
    "nom": {"type": "string", "max_length": 200, "required": True, "label": "Nom"},
    "categorie": {"type": "string", "max_length": 100, "required": True, "label": "Catégorie"},
    "quantite": {"type": "number", "min": 0, "max": 10000, "required": True, "label": "Quantité"},
    "unite": {"type": "string", "max_length": 50, "required": True, "label": "Unité"},
    "quantite_min": {"type": "number", "min": 0, "max": 1000, "label": "Seuil"},
    "emplacement": {"type": "string", "max_length": 100, "label": "Emplacement"},
    "date_peremption": {"type": "date", "label": "Date péremption"},
}

COURSES_SCHEMA = {
    "nom": {"type": "string", "max_length": 200, "required": True, "label": "Article"},
    "quantite": {"type": "number", "min": 0.1, "max": 10000, "required": True, "label": "Quantité"},
    "unite": {"type": "string", "max_length": 50, "required": True, "label": "Unité"},
    "priorite": {"type": "string", "max_length": 20, "label": "Priorité"},
    "magasin": {"type": "string", "max_length": 100, "label": "Magasin"},
}


# ═══════════════════════════════════════════════════════════
# DECORATORS
# ═══════════════════════════════════════════════════════════

def validate_input(schema: Dict = None, sanitize_all: bool = True):
    """Decorator pour valider automatiquement les inputs"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            data_arg = None

            for arg in args:
                if isinstance(arg, dict):
                    data_arg = arg
                    break

            if not data_arg:
                for key in ['data', 'input_data', 'form_data']:
                    if key in kwargs and isinstance(kwargs[key], dict):
                        data_arg = kwargs[key]
                        break

            if data_arg and schema:
                sanitized = InputSanitizer.sanitize_dict(data_arg, schema)

                if isinstance(args, tuple) and data_arg in args:
                    args = tuple(
                        sanitized if arg is data_arg else arg
                        for arg in args
                    )

                for key in ['data', 'input_data', 'form_data']:
                    if key in kwargs and kwargs[key] is data_arg:
                        kwargs[key] = sanitized

            elif data_arg and sanitize_all:
                for key, value in data_arg.items():
                    if isinstance(value, str):
                        data_arg[key] = InputSanitizer.sanitize_string(value)

            return func(*args, **kwargs)

        return wrapper
    return decorator


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════

def validate_model(model_class: BaseModel, data: dict) -> Tuple[bool, str, Optional[BaseModel]]:
    """Valide données avec modèle Pydantic"""
    try:
        validated = model_class(**data)
        return True, "", validated
    except ValidationError as e:
        error_msg = str(e)
        if "field required" in error_msg.lower():
            error_msg = "Champs obligatoires manquants"
        elif "validation error" in error_msg.lower():
            error_msg = "Données invalides"
        return False, error_msg, None
    except Exception as e:
        return False, str(e), None


def validate_streamlit_form(form_data: Dict, schema: Dict) -> Tuple[bool, List[str], Dict]:
    """Valide un formulaire Streamlit"""
    errors = []
    sanitized = InputSanitizer.sanitize_dict(form_data, schema)

    for field, rules in schema.items():
        if rules.get("required", False):
            if field not in sanitized or not sanitized[field]:
                errors.append(f"⚠️ {rules.get('label', field)} est requis")

    for field, value in sanitized.items():
        rules = schema.get(field, {})

        if rules.get("type") == "number" and value is not None:
            if rules.get("min") is not None and value < rules["min"]:
                errors.append(f"⚠️ {rules.get('label', field)} doit être ≥ {rules['min']}")
            if rules.get("max") is not None and value > rules["max"]:
                errors.append(f"⚠️ {rules.get('label', field)} doit être ≤ {rules['max']}")

        if rules.get("type") == "string" and value:
            max_len = rules.get("max_length", 1000)
            if len(value) > max_len:
                errors.append(f"⚠️ {rules.get('label', field)} trop long (max {max_len} caractères)")

    is_valid = len(errors) == 0
    return is_valid, errors, sanitized


def validate_and_sanitize_form(module_name: str, form_data: Dict) -> Tuple[bool, Dict]:
    """
    Helper pour valider un formulaire selon le module

    Returns:
        (is_valid, sanitized_data)
    """
    import streamlit as st

    schema_map = {
        "recettes": RECETTE_SCHEMA,
        "inventaire": INVENTAIRE_SCHEMA,
        "courses": COURSES_SCHEMA,
    }

    schema = schema_map.get(module_name, {})

    if not schema:
        logger.warning(f"Pas de schéma pour {module_name}")
        sanitized = {}
        for key, value in form_data.items():
            if isinstance(value, str):
                sanitized[key] = InputSanitizer.sanitize_string(value)
            else:
                sanitized[key] = value
        return True, sanitized

    is_valid, errors, sanitized = validate_streamlit_form(form_data, schema)

    if not is_valid:
        show_validation_errors(errors)

    return is_valid, sanitized


def show_validation_errors(errors: List[str]):
    """Affiche les erreurs de validation dans Streamlit"""
    import streamlit as st

    if errors:
        with st.expander("❌ Erreurs de validation", expanded=True):
            for error in errors:
                st.error(error)


# ═══════════════════════════════════════════════════════════
# VALIDATION HELPERS MÉTIER
# ═══════════════════════════════════════════════════════════

def require_fields(data: Dict, fields: List[str], object_name: str = "objet"):
    """Vérifie que les champs requis sont présents"""
    missing = [f for f in fields if not data.get(f)]
    if missing:
        from src.core.errors import ValidationError
        raise ValidationError(
            f"Champs manquants: {missing}",
            details={"missing_fields": missing},
            user_message=f"Champs obligatoires : {', '.join(missing)}"
        )


def require_positive(value: float, field_name: str):
    """Vérifie qu'une valeur est positive"""
    if value <= 0:
        from src.core.errors import ValidationError
        raise ValidationError(
            f"{field_name} doit être positif",
            user_message=f"{field_name} doit être supérieur à 0"
        )


def require_exists(obj: Any, object_type: str, object_id: Any):
    """Vérifie qu'un objet existe"""
    if obj is None:
        from src.core.errors import NotFoundError
        raise NotFoundError(
            f"{object_type} {object_id} not found",
            user_message=f"{object_type} introuvable"
        )