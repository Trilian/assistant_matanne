"""
Fonctions utilitaires d'import/export pour les recettes.

CSV, JSON et sérialisation de recettes en dictionnaires.
"""

import csv
import json
from io import StringIO

# ═══════════════════════════════════════════════════════════
# EXPORT CSV
# ═══════════════════════════════════════════════════════════


def export_recettes_to_csv(
    recettes: list[dict],
    separator: str = ",",
    fieldnames: list[str] | None = None,
) -> str:
    """Exporte une liste de recettes en format CSV.

    Args:
        recettes: Liste de dictionnaires représentant les recettes
        separator: Séparateur CSV (défaut: virgule)
        fieldnames: Noms des colonnes (défaut: champs standards)

    Returns:
        String CSV
    """
    if not recettes:
        return ""

    if fieldnames is None:
        fieldnames = [
            "nom",
            "description",
            "temps_preparation",
            "temps_cuisson",
            "portions",
            "difficulte",
            "type_repas",
            "saison",
        ]

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=separator)

    writer.writeheader()
    for r in recettes:
        row = {k: r.get(k, "") for k in fieldnames}
        writer.writerow(row)

    return output.getvalue()


def parse_csv_to_recettes(
    csv_content: str,
    separator: str = ",",
) -> list[dict]:
    """Parse un contenu CSV en liste de recettes.

    Args:
        csv_content: Contenu CSV string
        separator: Séparateur utilisé

    Returns:
        Liste de dictionnaires recettes
    """
    if not csv_content.strip():
        return []

    reader = csv.DictReader(StringIO(csv_content), delimiter=separator)
    recettes = []

    for row in reader:
        recette = {}
        for key, value in row.items():
            if key in ["temps_preparation", "temps_cuisson", "portions"]:
                try:
                    recette[key] = int(value) if value else 0
                except ValueError:
                    recette[key] = 0
            else:
                recette[key] = value
        recettes.append(recette)

    return recettes


# ═══════════════════════════════════════════════════════════
# EXPORT JSON
# ═══════════════════════════════════════════════════════════


def export_recettes_to_json(
    recettes: list[dict],
    indent: int = 2,
) -> str:
    """Exporte une liste de recettes en format JSON.

    Args:
        recettes: Liste de dictionnaires représentant les recettes
        indent: Niveau d'indentation JSON

    Returns:
        String JSON
    """
    return json.dumps(recettes, indent=indent, ensure_ascii=False)


def parse_json_to_recettes(json_content: str) -> list[dict]:
    """Parse un contenu JSON en liste de recettes.

    Args:
        json_content: Contenu JSON string

    Returns:
        Liste de dictionnaires recettes
    """
    if not json_content.strip():
        return []

    data = json.loads(json_content)
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        return [data]
    return []


# ═══════════════════════════════════════════════════════════
# CONVERSION RECETTE
# ═══════════════════════════════════════════════════════════


def recette_to_dict(
    nom: str,
    description: str = "",
    temps_preparation: int = 0,
    temps_cuisson: int = 0,
    portions: int = 4,
    difficulte: str = "moyen",
    type_repas: str = "diner",
    saison: str = "toute_année",
    ingredients: list[dict] | None = None,
    etapes: list[dict] | None = None,
) -> dict:
    """Construit un dictionnaire recette standard.

    Args:
        nom: Nom de la recette
        description: Description
        temps_preparation: Temps de préparation en minutes
        temps_cuisson: Temps de cuisson en minutes
        portions: Nombre de portions
        difficulte: Niveau de difficulté
        type_repas: Type de repas
        saison: Saison recommandée
        ingredients: Liste des ingrédients
        etapes: Liste des étapes

    Returns:
        Dictionnaire recette
    """
    return {
        "nom": nom,
        "description": description,
        "temps_preparation": temps_preparation,
        "temps_cuisson": temps_cuisson,
        "portions": portions,
        "difficulte": difficulte,
        "type_repas": type_repas,
        "saison": saison,
        "ingredients": ingredients or [],
        "etapes": etapes or [],
    }


def ingredient_to_dict(
    nom: str,
    quantite: float = 1.0,
    unite: str = "pcs",
) -> dict:
    """Construit un dictionnaire ingrédient.

    Args:
        nom: Nom de l'ingrédient
        quantite: Quantité
        unite: Unité de mesure

    Returns:
        Dictionnaire ingrédient
    """
    return {
        "nom": nom,
        "quantite": quantite,
        "unite": unite,
    }


def etape_to_dict(
    description: str,
    ordre: int = 1,
    duree: int | None = None,
) -> dict:
    """Construit un dictionnaire étape.

    Args:
        description: Description de l'étape
        ordre: Numéro d'ordre
        duree: Durée en minutes

    Returns:
        Dictionnaire étape
    """
    result = {
        "description": description,
        "ordre": ordre,
    }
    if duree is not None:
        result["duree"] = duree
    return result


__all__ = [
    "export_recettes_to_csv",
    "parse_csv_to_recettes",
    "export_recettes_to_json",
    "parse_json_to_recettes",
    "recette_to_dict",
    "ingredient_to_dict",
    "etape_to_dict",
]
