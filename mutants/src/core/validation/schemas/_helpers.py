"""Helpers partagés pour les schémas de validation."""

import re


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
