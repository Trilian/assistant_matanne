"""
Helpers - Manipulation de strings
"""

import hashlib
import json
from typing import Any


def generer_id(data: Any) -> str:
    """
    Génère ID unique basé sur données

    Examples:
        >>> generer_id({"nom": "test", "value": 123})
        "a1b2c3d4e5f6g7h8"
    """
    data_str = json.dumps(data, sort_keys=True, default=str)
    return hashlib.md5(data_str.encode()).hexdigest()[:16]


def normaliser_espaces(text: str) -> str:
    """
    Normalise espaces (single space, trim)

    Examples:
        >>> normaliser_espaces("  hello    world  ")
        "hello world"
    """
    return " ".join(text.split())


def retirer_accents(text: str) -> str:
    """
    Retire les accents d'un texte

    Examples:
        >>> retirer_accents("café crème")
        "cafe creme"
    """
    replacements = {
        "à": "a",
        "á": "a",
        "â": "a",
        "ä": "a",
        "ã": "a",
        "è": "e",
        "é": "e",
        "ê": "e",
        "ë": "e",
        "ì": "i",
        "í": "i",
        "î": "i",
        "ï": "i",
        "ò": "o",
        "ó": "o",
        "ô": "o",
        "ö": "o",
        "õ": "o",
        "ù": "u",
        "ú": "u",
        "û": "u",
        "ü": "u",
        "ç": "c",
        "ñ": "n",
    }

    result = text
    for old, new in replacements.items():
        result = result.replace(old, new)
        result = result.replace(old.upper(), new.upper())

    return result


def camel_vers_snake(text: str) -> str:
    """
    Convertit camelCase en snake_case

    Examples:
        >>> camel_vers_snake("myVariableName")
        "my_variable_name"
    """
    import re

    return re.sub(r"(?<!^)(?=[A-Z])", "_", text).lower()


def snake_vers_camel(text: str) -> str:
    """
    Convertit snake_case en camelCase

    Examples:
        >>> snake_vers_camel("my_variable_name")
        "myVariableName"
    """
    components = text.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def pluraliser(word: str, count: int, plural_form: str | None = None) -> str:
    """
    Pluralise un mot selon le nombre

    Examples:
        >>> pluraliser("item", 1)
        "1 item"
        >>> pluraliser("item", 5)
        "5 items"
        >>> pluraliser("cheval", 2, "chevaux")
        "2 chevaux"
    """
    if count == 1:
        return f"{count} {word}"

    if plural_form:
        return f"{count} {plural_form}"

    # Règle simple anglaise
    if word.endswith("y"):
        return f"{count} {word[:-1]}ies"
    elif word.endswith("s"):
        return f"{count} {word}es"
    else:
        return f"{count} {word}s"


def masquer_sensible(text: str, visible_chars: int = 4) -> str:
    """
    Masque données sensibles

    Examples:
        >>> masquer_sensible("1234567890", 4)
        "1234******"
    """
    if len(text) <= visible_chars:
        return text

    visible = text[:visible_chars]
    masked = "*" * (len(text) - visible_chars)
    return visible + masked
