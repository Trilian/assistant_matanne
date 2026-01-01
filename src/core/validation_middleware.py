"""
Middleware de Validation Automatique
Protection XSS, injection SQL, validation stricte des inputs
"""
import re
import html
import logging
from typing import Any, Dict, List, Optional, Union, Callable
from functools import wraps
from datetime import date, datetime

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# NETTOYAGE & SANITIZATION
# ═══════════════════════════════════════════════════════════

class InputSanitizer:
    """Sanitizer universel pour tous les inputs"""

    # Patterns dangereux
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
        """
        Nettoie une chaîne de caractères

        Protection contre:
        - XSS (scripts, événements JS)
        - Injection SQL
        - Caractères dangereux
        """
        if not value or not isinstance(value, str):
            return ""

        # Limiter longueur
        value = value[:max_length]

        # Échapper HTML
        value = html.escape(value)

        # Supprimer patterns XSS
        for pattern in InputSanitizer.XSS_PATTERNS:
            value = re.sub(pattern, '', value, flags=re.IGNORECASE)

        # Détecter SQL injection (warning uniquement)
        for pattern in InputSanitizer.SQL_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"⚠️ Tentative SQL injection détectée: {value[:50]}")

        # Supprimer caractères de contrôle
        value = re.sub(r'[\x00-\x1F\x7F]', '', value)

        # Trim
        value = value.strip()

        return value

    @staticmethod
    def sanitize_number(value: Any, min_val: float = None, max_val: float = None) -> Optional[float]:
        """Valide et nettoie un nombre"""
        try:
            # Convertir en float
            if isinstance(value, str):
                value = value.replace(',', '.')

            num = float(value)

            # Vérifier range
            if min_val is not None and num < min_val:
                logger.warning(f"Nombre trop petit: {num} < {min_val}")
                return min_val

            if max_val is not None and num > max_val:
                logger.warning(f"Nombre trop grand: {num} > {max_val}")
                return max_val

            return num

        except (ValueError, TypeError):
            logger.warning(f"Valeur numérique invalide: {value}")
            return None

    @staticmethod
    def sanitize_date(value: Any) -> Optional[date]:
        """Valide et nettoie une date"""
        if isinstance(value, date):
            return value

        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, str):
            # Essayer plusieurs formats
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']:
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue

        logger.warning(f"Date invalide: {value}")
        return None

    @staticmethod
    def sanitize_email(value: str) -> Optional[str]:
        """Valide et nettoie un email"""
        if not value or not isinstance(value, str):
            return None

        # Pattern email basique
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        value = value.strip().lower()

        if re.match(pattern, value):
            return value

        logger.warning(f"Email invalide: {value}")
        return None

    @staticmethod
    def sanitize_dict(data: Dict, schema: Dict) -> Dict:
        """
        Nettoie un dictionnaire selon un schéma

        Exemple de schéma:
        {
            "nom": {"type": "string", "max_length": 200, "required": True},
            "age": {"type": "number", "min": 0, "max": 150},
            "email": {"type": "email"}
        }
        """
        sanitized = {}

        for field, rules in schema.items():
            value = data.get(field)

            # Champ requis
            if rules.get("required", False) and not value:
                logger.warning(f"Champ requis manquant: {field}")
                continue

            # Skip si None et pas requis
            if value is None and not rules.get("required", False):
                continue

            # Sanitize selon le type
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
# DECORATOR DE VALIDATION
# ═══════════════════════════════════════════════════════════

def validate_input(schema: Dict = None, sanitize_all: bool = True):
    """
    Decorator pour valider automatiquement les inputs

    Usage:
        @validate_input(schema={
            "nom": {"type": "string", "max_length": 200, "required": True},
            "quantite": {"type": "number", "min": 0, "max": 10000}
        })
        def create_article(data: Dict):
            # data est déjà validé et nettoyé
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Trouver l'argument "data" (dict)
            data_arg = None

            # Chercher dans args
            for arg in args:
                if isinstance(arg, dict):
                    data_arg = arg
                    break

            # Chercher dans kwargs
            if not data_arg:
                for key in ['data', 'input_data', 'form_data']:
                    if key in kwargs and isinstance(kwargs[key], dict):
                        data_arg = kwargs[key]
                        break

            # Valider si trouvé
            if data_arg and schema:
                sanitized = InputSanitizer.sanitize_dict(data_arg, schema)

                # Remplacer dans args ou kwargs
                if isinstance(args, tuple) and data_arg in args:
                    args = tuple(
                        sanitized if arg is data_arg else arg
                        for arg in args
                    )

                for key in ['data', 'input_data', 'form_data']:
                    if key in kwargs and kwargs[key] is data_arg:
                        kwargs[key] = sanitized

            # Sanitize basique si pas de schéma
            elif data_arg and sanitize_all:
                for key, value in data_arg.items():
                    if isinstance(value, str):
                        data_arg[key] = InputSanitizer.sanitize_string(value)

            return func(*args, **kwargs)

        return wrapper
    return decorator


# ═══════════════════════════════════════════════════════════
# VALIDATION STREAMLIT AUTOMATIQUE
# ═══════════════════════════════════════════════════════════

def validate_streamlit_form(form_data: Dict, schema: Dict) -> tuple[bool, List[str], Dict]:
    """
    Valide un formulaire Streamlit

    Returns:
        (is_valid, errors, sanitized_data)
    """
    errors = []
    sanitized = InputSanitizer.sanitize_dict(form_data, schema)

    # Vérifier champs requis
    for field, rules in schema.items():
        if rules.get("required", False):
            if field not in sanitized or not sanitized[field]:
                errors.append(f"⚠️ {rules.get('label', field)} est requis")

    # Vérifier validité des valeurs
    for field, value in sanitized.items():
        rules = schema.get(field, {})

        # Nombre trop petit/grand
        if rules.get("type") == "number" and value is not None:
            if rules.get("min") is not None and value < rules["min"]:
                errors.append(f"⚠️ {rules.get('label', field)} doit être ≥ {rules['min']}")
            if rules.get("max") is not None and value > rules["max"]:
                errors.append(f"⚠️ {rules.get('label', field)} doit être ≤ {rules['max']}")

        # String trop longue
        if rules.get("type") == "string" and value:
            max_len = rules.get("max_length", 1000)
            if len(value) > max_len:
                errors.append(f"⚠️ {rules.get('label', field)} trop long (max {max_len} caractères)")

    is_valid = len(errors) == 0

    return is_valid, errors, sanitized


# ═══════════════════════════════════════════════════════════
# SCHÉMAS PRÉDÉFINIS POUR L'APP
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
# HELPER STREAMLIT
# ═══════════════════════════════════════════════════════════

def show_validation_errors(errors: List[str]):
    """Affiche les erreurs de validation dans Streamlit"""
    import streamlit as st

    if errors:
        with st.expander("❌ Erreurs de validation", expanded=True):
            for error in errors:
                st.error(error)


def validate_and_sanitize_form(module_name: str, form_data: Dict) -> tuple[bool, Dict]:
    """
    Helper pour valider un formulaire selon le module

    Returns:
        (is_valid, sanitized_data)
    """
    import streamlit as st

    # Choisir schéma
    schema_map = {
        "recettes": RECETTE_SCHEMA,
        "inventaire": INVENTAIRE_SCHEMA,
        "courses": COURSES_SCHEMA,
    }

    schema = schema_map.get(module_name, {})

    if not schema:
        logger.warning(f"Pas de schéma pour {module_name}, validation basique")
        # Sanitize basique
        sanitized = {}
        for key, value in form_data.items():
            if isinstance(value, str):
                sanitized[key] = InputSanitizer.sanitize_string(value)
            else:
                sanitized[key] = value
        return True, sanitized

    # Validation complète
    is_valid, errors, sanitized = validate_streamlit_form(form_data, schema)

    if not is_valid:
        show_validation_errors(errors)

    return is_valid, sanitized