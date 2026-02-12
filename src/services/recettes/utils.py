"""
Fonctions utilitaires pures pour les recettes.

Ces fonctions ne dépendent pas de la base de données et peuvent être
testées unitairement sans mocking.
"""

import csv
import json
from io import StringIO
from typing import Any


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CONSTANTES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

DIFFICULTES = ["facile", "moyen", "difficile"]
TYPES_REPAS = ["petit_dejeuner", "dejeuner", "diner", "gouter", "apero"]
SAISONS = ["printemps", "ete", "automne", "hiver", "toute_année"]

ROBOTS_COMPATIBLES = {
    "cookeo": {"nom": "Cookeo", "temps_reduction": 0.7},
    "monsieur_cuisine": {"nom": "Monsieur Cuisine", "temps_reduction": 0.8},
    "airfryer": {"nom": "Airfryer", "temps_reduction": 0.75},
    "multicooker": {"nom": "Multicooker", "temps_reduction": 0.85},
}


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# EXPORT CSV
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# EXPORT JSON
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CONVERSION RECETTE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CALCULS DE TEMPS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def calculer_temps_total(temps_preparation: int, temps_cuisson: int) -> int:
    """Calcule le temps total de la recette.
    
    Args:
        temps_preparation: Temps de préparation en minutes
        temps_cuisson: Temps de cuisson en minutes
    
    Returns:
        Temps total en minutes
    """
    return temps_preparation + temps_cuisson


def estimer_temps_robot(
    temps_cuisson: int,
    robot_type: str,
) -> int:
    """Estime le temps de cuisson adapté pour un robot.
    
    Args:
        temps_cuisson: Temps de cuisson original
        robot_type: Type de robot culinaire
    
    Returns:
        Temps de cuisson estimé pour le robot
    """
    info = ROBOTS_COMPATIBLES.get(robot_type, {"temps_reduction": 1.0})
    reduction = info.get("temps_reduction", 1.0)
    return int(temps_cuisson * reduction)


def formater_temps(minutes: int) -> str:
    """Formate une durée en minutes en format lisible.
    
    Args:
        minutes: Durée en minutes
    
    Returns:
        Format "Xh Ymin" ou "Ymin"
    """
    if minutes < 60:
        return f"{minutes}min"
    
    heures = minutes // 60
    mins = minutes % 60
    
    if mins == 0:
        return f"{heures}h"
    return f"{heures}h {mins}min"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# AJUSTEMENT DES PORTIONS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def ajuster_quantite_ingredient(
    quantite_base: float,
    portions_base: int,
    portions_cible: int,
) -> float:
    """Ajuste la quantité d'un ingrédient pour un nombre de portions différent.
    
    Args:
        quantite_base: Quantité originale
        portions_base: Nombre de portions originales
        portions_cible: Nombre de portions voulues
    
    Returns:
        Quantité ajustée
    """
    if portions_base <= 0:
        return quantite_base
    
    ratio = portions_cible / portions_base
    return round(quantite_base * ratio, 2)


def ajuster_ingredients(
    ingredients: list[dict],
    portions_base: int,
    portions_cible: int,
) -> list[dict]:
    """Ajuste tous les ingrédients pour un nombre de portions différent.
    
    Args:
        ingredients: Liste des ingrédients avec quantite
        portions_base: Nombre de portions originales
        portions_cible: Nombre de portions voulues
    
    Returns:
        Liste des ingrédients ajustés
    """
    if portions_base == portions_cible:
        return ingredients
    
    ajustes = []
    for ing in ingredients:
        ajuste = ing.copy()
        if "quantite" in ajuste:
            ajuste["quantite"] = ajuster_quantite_ingredient(
                ajuste["quantite"],
                portions_base,
                portions_cible,
            )
        ajustes.append(ajuste)
    
    return ajustes


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FILTRES ET RECHERCHE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def filtrer_recettes_par_temps(
    recettes: list[dict],
    temps_max: int,
) -> list[dict]:
    """Filtre les recettes par temps total maximum.
    
    Args:
        recettes: Liste de recettes
        temps_max: Temps maximum en minutes
    
    Returns:
        Recettes dont le temps total <= temps_max
    """
    return [
        r for r in recettes
        if calculer_temps_total(
            r.get("temps_preparation", 0),
            r.get("temps_cuisson", 0),
        ) <= temps_max
    ]


def filtrer_recettes_par_difficulte(
    recettes: list[dict],
    difficulte: str,
) -> list[dict]:
    """Filtre les recettes par niveau de difficulté.
    
    Args:
        recettes: Liste de recettes
        difficulte: Niveau de difficulté voulu
    
    Returns:
        Recettes avec cette difficulté
    """
    return [r for r in recettes if r.get("difficulte") == difficulte]


def filtrer_recettes_par_type(
    recettes: list[dict],
    type_repas: str,
) -> list[dict]:
    """Filtre les recettes par type de repas.
    
    Args:
        recettes: Liste de recettes
        type_repas: Type de repas voulu
    
    Returns:
        Recettes de ce type
    """
    return [r for r in recettes if r.get("type_repas") == type_repas]


def filtrer_recettes_par_saison(
    recettes: list[dict],
    saison: str,
) -> list[dict]:
    """Filtre les recettes par saison.
    
    Args:
        recettes: Liste de recettes
        saison: Saison voulue
    
    Returns:
        Recettes adaptées Ã  cette saison ou toute_année
    """
    return [
        r for r in recettes
        if r.get("saison") in [saison, "toute_année"]
    ]


def rechercher_par_nom(
    recettes: list[dict],
    terme: str,
) -> list[dict]:
    """Recherche des recettes par nom.
    
    Args:
        recettes: Liste de recettes
        terme: Terme de recherche (insensible Ã  la casse)
    
    Returns:
        Recettes dont le nom contient le terme
    """
    terme_lower = terme.lower()
    return [
        r for r in recettes
        if terme_lower in r.get("nom", "").lower()
    ]


def rechercher_par_ingredient(
    recettes: list[dict],
    ingredient: str,
) -> list[dict]:
    """Recherche des recettes contenant un ingrédient.
    
    Args:
        recettes: Liste de recettes
        ingredient: Nom de l'ingrédient (insensible Ã  la casse)
    
    Returns:
        Recettes contenant cet ingrédient
    """
    ingredient_lower = ingredient.lower()
    result = []
    
    for r in recettes:
        for ing in r.get("ingredients", []):
            if ingredient_lower in ing.get("nom", "").lower():
                result.append(r)
                break
    
    return result


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# STATISTIQUES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def calculer_stats_recettes(recettes: list[dict]) -> dict:
    """Calcule des statistiques sur une collection de recettes.
    
    Args:
        recettes: Liste de recettes
    
    Returns:
        Dictionnaire de statistiques
    """
    if not recettes:
        return {
            "total": 0,
            "temps_moyen_preparation": 0,
            "temps_moyen_cuisson": 0,
            "temps_moyen_total": 0,
            "par_difficulte": {},
            "par_type": {},
            "par_saison": {},
        }
    
    temps_prep = [r.get("temps_preparation", 0) for r in recettes]
    temps_cuisson = [r.get("temps_cuisson", 0) for r in recettes]
    temps_totaux = [calculer_temps_total(r.get("temps_preparation", 0), r.get("temps_cuisson", 0)) for r in recettes]
    
    # Comptage par catégorie
    par_difficulte = {}
    par_type = {}
    par_saison = {}
    
    for r in recettes:
        diff = r.get("difficulte", "inconnu")
        par_difficulte[diff] = par_difficulte.get(diff, 0) + 1
        
        type_r = r.get("type_repas", "inconnu")
        par_type[type_r] = par_type.get(type_r, 0) + 1
        
        saison = r.get("saison", "inconnu")
        par_saison[saison] = par_saison.get(saison, 0) + 1
    
    return {
        "total": len(recettes),
        "temps_moyen_preparation": sum(temps_prep) / len(temps_prep),
        "temps_moyen_cuisson": sum(temps_cuisson) / len(temps_cuisson),
        "temps_moyen_total": sum(temps_totaux) / len(temps_totaux),
        "par_difficulte": par_difficulte,
        "par_type": par_type,
        "par_saison": par_saison,
    }


def calculer_score_recette(
    recette: dict,
    criteres: dict | None = None,
) -> float:
    """Calcule un score de pertinence pour une recette.
    
    Args:
        recette: Dictionnaire recette
        criteres: Critères de scoring {temps_max, difficulte_preferee, etc}
    
    Returns:
        Score de 0 Ã  100
    """
    score = 50.0  # Base
    
    if criteres is None:
        return score
    
    # Bonus pour temps < temps_max
    if "temps_max" in criteres:
        temps_total = calculer_temps_total(
            recette.get("temps_preparation", 0),
            recette.get("temps_cuisson", 0),
        )
        if temps_total <= criteres["temps_max"]:
            score += 20
    
    # Bonus pour difficulté préférée
    if "difficulte_preferee" in criteres:
        if recette.get("difficulte") == criteres["difficulte_preferee"]:
            score += 15
    
    # Bonus pour type de repas
    if "type_repas" in criteres:
        if recette.get("type_repas") == criteres["type_repas"]:
            score += 10
    
    # Bonus pour saison actuelle
    if "saison" in criteres:
        saison_recette = recette.get("saison", "")
        if saison_recette == criteres["saison"] or saison_recette == "toute_année":
            score += 5
    
    return min(100.0, score)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# VALIDATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def valider_difficulte(difficulte: str) -> str:
    """Valide et normalise la difficulté.
    
    Args:
        difficulte: Difficulté Ã  valider
    
    Returns:
        Difficulté normalisée
    
    Raises:
        ValueError: Si difficulté invalide
    """
    difficulte_lower = difficulte.lower()
    if difficulte_lower not in DIFFICULTES:
        raise ValueError(f"Difficulté invalide: {difficulte}. Valeurs acceptées: {DIFFICULTES}")
    return difficulte_lower


def valider_type_repas(type_repas: str) -> str:
    """Valide et normalise le type de repas.
    
    Args:
        type_repas: Type de repas Ã  valider
    
    Returns:
        Type normalisé
    
    Raises:
        ValueError: Si type invalide
    """
    type_lower = type_repas.lower()
    if type_lower not in TYPES_REPAS:
        raise ValueError(f"Type de repas invalide: {type_repas}. Valeurs acceptées: {TYPES_REPAS}")
    return type_lower


def valider_temps(temps: int | None, defaut: int = 0) -> int:
    """Valide un temps en minutes.
    
    Args:
        temps: Temps Ã  valider
        defaut: Valeur par défaut si invalide
    
    Returns:
        Temps validé (0-480 minutes)
    """
    if temps is None or temps < 0:
        return defaut
    return min(temps, 480)  # Max 8 heures


def valider_portions(portions: int | None, defaut: int = 4) -> int:
    """Valide un nombre de portions.
    
    Args:
        portions: Nombre de portions
        defaut: Valeur par défaut si invalide
    
    Returns:
        Portions validées (1-100)
    """
    if portions is None or portions < 1:
        return defaut
    return min(portions, 100)


__all__ = [
    # Constantes
    "DIFFICULTES",
    "TYPES_REPAS",
    "SAISONS",
    "ROBOTS_COMPATIBLES",
    # Export CSV
    "export_recettes_to_csv",
    "parse_csv_to_recettes",
    # Export JSON
    "export_recettes_to_json",
    "parse_json_to_recettes",
    # Conversion
    "recette_to_dict",
    "ingredient_to_dict",
    "etape_to_dict",
    # Temps
    "calculer_temps_total",
    "estimer_temps_robot",
    "formater_temps",
    # Portions
    "ajuster_quantite_ingredient",
    "ajuster_ingredients",
    # Filtres
    "filtrer_recettes_par_temps",
    "filtrer_recettes_par_difficulte",
    "filtrer_recettes_par_type",
    "filtrer_recettes_par_saison",
    "rechercher_par_nom",
    "rechercher_par_ingredient",
    # Stats
    "calculer_stats_recettes",
    "calculer_score_recette",
    # Validation
    "valider_difficulte",
    "valider_type_repas",
    "valider_temps",
    "valider_portions",
]
