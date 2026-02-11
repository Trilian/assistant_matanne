"""
Formatters - Texte
"""

import re


def tronquer(text: str, length: int = 100, suffix: str = "...") -> str:
    """
    Tronque un texte

    Examples:
        >>> tronquer("Un texte très long...", length=10)
        "Un texte..."
    """
    if len(text) <= length:
        return text
    return text[: length - len(suffix)] + suffix


def nettoyer_texte(text: str) -> str:
    """
    Nettoie texte (évite injection)

    Examples:
        >>> nettoyer_texte("<script>alert('xss')</script>")
        "scriptalert('xss')/script"
    """
    if not text:
        return text
    return re.sub(r"[<>{}]", "", text).strip()


def generer_slug(text: str) -> str:
    """
    Convertit texte en slug

    Examples:
        >>> generer_slug("Tarte aux Pommes")
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


def extraire_nombre(text: str) -> float | None:
    """
    Extrait un nombre depuis une string

    Examples:
        >>> extraire_nombre("2.5 kg")
        2.5
        >>> extraire_nombre("Prix: 10,50€")
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


def capitaliser_premiere(text: str) -> str:
    """
    Capitalise première lettre uniquement

    Examples:
        >>> capitaliser_premiere("tomate")
        "Tomate"
    """
    if not text:
        return text
    return text[0].upper() + text[1:].lower() if len(text) > 0 else text


def capitaliser_mots(text: str) -> str:
    """
    Capitalise chaque mot

    Examples:
        >>> capitaliser_mots("bonjour le monde")
        "Bonjour Le Monde"
    """
    if not text:
        return text
    return " ".join(word.capitalize() for word in text.split())

