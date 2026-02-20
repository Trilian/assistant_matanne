"""
Registry de composants UI avec documentation auto-générée.

Le décorateur ``@composant_ui`` enregistre chaque composant dans un catalogue
global consultable via ``obtenir_catalogue()`` ou la page Design System.

Usage:
    from src.ui.registry import composant_ui

    @composant_ui("atoms", exemple='badge("Actif", Couleur.SUCCESS)')
    def badge(texte: str, couleur: str = Couleur.SUCCESS) -> None: ...
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


@dataclass(frozen=True)
class ComponentMeta:
    """Métadonnées d'un composant enregistré."""

    nom: str
    categorie: str
    description: str
    signature: str
    fichier: str
    ligne: int
    exemple: str = ""
    tags: tuple[str, ...] = ()


_REGISTRY: dict[str, ComponentMeta] = {}


def composant_ui(
    categorie: str,
    exemple: str = "",
    tags: tuple[str, ...] | list[str] = (),
) -> Callable[[F], F]:
    """Décorateur pour enregistrer un composant dans le design system.

    Args:
        categorie: Catégorie du composant (atoms, forms, data, ...).
        exemple: Exemple d'utilisation en Python.
        tags: Tags pour la recherche/filtrage.
    """

    def decorator(func: F) -> F:
        try:
            source_file = inspect.getfile(func)
            source_lines = inspect.getsourcelines(func)
            line_number = source_lines[1]
        except (TypeError, OSError):
            source_file = "<unknown>"
            line_number = 0

        meta = ComponentMeta(
            nom=func.__name__,
            categorie=categorie,
            description=(func.__doc__ or "").strip(),
            signature=str(inspect.signature(func)),
            fichier=source_file,
            ligne=line_number,
            exemple=exemple,
            tags=tuple(tags) if isinstance(tags, list) else tags,
        )
        _REGISTRY[func.__name__] = meta
        return func

    return decorator


def obtenir_catalogue() -> dict[str, list[ComponentMeta]]:
    """Retourne le catalogue groupé par catégorie."""
    catalogue: dict[str, list[ComponentMeta]] = {}
    for meta in _REGISTRY.values():
        catalogue.setdefault(meta.categorie, []).append(meta)
    return catalogue


def obtenir_composant(nom: str) -> ComponentMeta | None:
    """Retourne les métadonnées d'un composant par son nom."""
    return _REGISTRY.get(nom)


def lister_composants(categorie: str | None = None) -> list[ComponentMeta]:
    """Liste les composants, optionnellement filtrés par catégorie."""
    if categorie:
        return [m for m in _REGISTRY.values() if m.categorie == categorie]
    return list(_REGISTRY.values())


def rechercher_composants(terme: str) -> list[ComponentMeta]:
    """Recherche de composants par terme (nom, description, tags)."""
    terme_lower = terme.lower()
    resultats = []

    for meta in _REGISTRY.values():
        if (
            terme_lower in meta.nom.lower()
            or terme_lower in meta.description.lower()
            or any(terme_lower in tag.lower() for tag in meta.tags)
        ):
            resultats.append(meta)

    return resultats


__all__ = [
    "ComponentMeta",
    "composant_ui",
    "obtenir_catalogue",
    "obtenir_composant",
    "lister_composants",
    "rechercher_composants",
]
