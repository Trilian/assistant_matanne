"""
Validators - Validation commune
"""

import re
from typing import Any


def is_valid_email(email: str) -> bool:
    """
    Valide un email

    Examples:
        >>> is_valid_email("test@example.com")
        True
        >>> is_valid_email("invalid")
        False
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def is_valid_phone(phone: str, country: str = "FR") -> bool:
    """
    Valide un numéro de téléphone

    Examples:
        >>> is_valid_phone("0612345678")
        True
    """
    if country == "FR":
        pattern = r"^(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}$"
        return bool(re.match(pattern, phone))
    return False


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Limite valeur entre min et max

    Examples:
        >>> clamp(15, 0, 10)
        10
        >>> clamp(-5, 0, 10)
        0
    """
    return max(min_val, min(value, max_val))


def validate_range(
    value: Any, min_val: Any = None, max_val: Any = None, field_name: str = "valeur"
) -> tuple[bool, str]:
    """
    Valide qu'une valeur est dans une plage

    Returns:
        (is_valid, error_message)

    Examples:
        >>> validate_range(5, 0, 10)
        (True, "")
        >>> validate_range(15, 0, 10)
        (False, "valeur doit être <= 10")
    """
    try:
        val = float(value)
    except (ValueError, TypeError):
        return False, f"{field_name} doit être un nombre"

    if min_val is not None and val < min_val:
        return False, f"{field_name} doit être >= {min_val}"

    if max_val is not None and val > max_val:
        return False, f"{field_name} doit être <= {max_val}"

    return True, ""


def validate_string_length(
    text: str, min_length: int = 0, max_length: int | None = None, field_name: str = "texte"
) -> tuple[bool, str]:
    """
    Valide longueur d'une string

    Returns:
        (is_valid, error_message)
    """
    if not isinstance(text, str):
        return False, f"{field_name} doit être du texte"

    length = len(text)

    if length < min_length:
        return False, f"{field_name} doit faire au moins {min_length} caractères"

    if max_length and length > max_length:
        return False, f"{field_name} doit faire maximum {max_length} caractères"

    return True, ""


def validate_required_fields(data: dict, required_fields: list) -> tuple[bool, list]:
    """
    Valide présence de champs requis

    Returns:
        (is_valid, list_of_missing_fields)

    Examples:
        >>> validate_required_fields({"nom": "Test"}, ["nom", "email"])
        (False, ["email"])
    """
    missing = []

    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            missing.append(field)

    return len(missing) == 0, missing


def validate_choice(
    value: Any, allowed_values: list, field_name: str = "valeur"
) -> tuple[bool, str]:
    """
    Valide qu'une valeur est dans une liste

    Returns:
        (is_valid, error_message)
    """
    if value not in allowed_values:
        return False, f"{field_name} doit être dans {allowed_values}"

    return True, ""


def is_valid_url(url: str) -> bool:
    """
    Valide une URL

    Examples:
        >>> is_valid_url("https://example.com")
        True
        >>> is_valid_url("invalid")
        False
    """
    pattern = r"^https?://[\w\.-]+\.[a-zA-Z]{2,}(/.*)?$"
    return bool(re.match(pattern, url))


# ═══════════════════════════════════════════════════════════
# ALIAS FRANÇAIS (pour compatibilité)
# ═══════════════════════════════════════════════════════════

valider_email = is_valid_email
valider_telephone = is_valid_phone
valider_url = is_valid_url
borner = clamp
valider_plage = validate_range
valider_longueur_texte = validate_string_length
valider_champs_requis = validate_required_fields
valider_choix = validate_choice
