"""
Formatters - Texte
"""

import re


def truncate(text: str, length: int = 100, suffix: str = "...") -> str:
    """
    Tronque un texte

    Examples:
        >>> truncate("Un texte très long...", length=10)
        "Un texte..."
    """
    if len(text) <= length:
        return text
    return text[: length - len(suffix)] + suffix


def clean_text(text: str) -> str:
    """
    Nettoie texte (évite injection)

    Examples:
        >>> clean_text("<script>alert('xss')</script>")
        "scriptalert('xss')/script"
    """
    if not text:
        return text
    return re.sub(r"[<>{}]", "", text).strip()


def slugify(text: str) -> str:
    """
    Convertit texte en slug

    Examples:
        >>> slugify("Tarte aux Pommes")
        "tarte-aux-pommes"
    """
    text = text.lower()

    # Remplacer accents
    replacements = {
        "à": "a",
        "á": "a",
        "â": "a",
        "ä": "a",
        "è": "e",
        "é": "e",
        "ê": "e",
        "ë": "e",
        "ù": "u",
        "ú": "u",
        "û": "u",
        "ü": "u",
        "ç": "c",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    # Garder alphanumériques
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def extract_number(text: str) -> float | None:
    """
    Extrait un nombre depuis une string

    Examples:
        >>> extract_number("2.5 kg")
        2.5
        >>> extract_number("Prix: 10,50€")
        10.5
    """
    if not text:
        return None

    # Remplacer virgules par points
    text = str(text).replace(",", ".")

    # Extraire le nombre
    match = re.search(r"-?\d+\.?\d*", text)

    if match:
        try:
            return float(match.group())
        except ValueError:
            return None

    return None


def capitalize_first(text: str) -> str:
    """
    Capitalise première lettre uniquement

    Examples:
        >>> capitalize_first("tomate")
        "Tomate"
    """
    if not text:
        return text
    return text[0].upper() + text[1:].lower() if len(text) > 0 else text
