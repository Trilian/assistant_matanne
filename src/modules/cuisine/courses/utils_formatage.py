"""
Formatage, statistiques, suggestions et historique des courses

Logique pure, testable sans Streamlit.
"""

import logging
from datetime import datetime, timedelta

from .utils_operations import (
    PRIORITY_EMOJIS,
    PRIORITY_ORDER,
    grouper_par_rayon,
    trier_par_priorite,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CALCUL DES STATISTIQUES
# ═══════════════════════════════════════════════════════════


def calculer_statistiques(articles: list[dict], articles_achetes: list[dict] = None) -> dict:
    """
    Calcule les statistiques de la liste de courses.

    Args:
        articles: Liste des articles à acheter
        articles_achetes: Liste des articles achetes (optionnel)

    Returns:
        Dictionnaire des statistiques
    """
    articles_achetes = articles_achetes or []

    stats = {
        "total_a_acheter": len(articles),
        "total_achetes": len(articles_achetes),
        "haute_priorite": len([a for a in articles if a.get("priorite") == "haute"]),
        "moyenne_priorite": len([a for a in articles if a.get("priorite") == "moyenne"]),
        "basse_priorite": len([a for a in articles if a.get("priorite") == "basse"]),
        "suggestions_ia": len([a for a in articles if a.get("suggere_par_ia")]),
        "rayons_uniques": len(set(a.get("rayon_magasin", "Autre") for a in articles)),
    }

    # Calcul du taux de completion
    total = stats["total_a_acheter"] + stats["total_achetes"]
    stats["taux_completion"] = (stats["total_achetes"] / total * 100) if total > 0 else 0

    return stats


def calculer_statistiques_par_rayon(articles: list[dict]) -> dict[str, dict]:
    """
    Calcule les statistiques par rayon.

    Args:
        articles: Liste des articles

    Returns:
        Dictionnaire {rayon: {count, haute_priorite, etc}}
    """
    rayons = grouper_par_rayon(articles)

    stats = {}
    for rayon, articles_rayon in rayons.items():
        stats[rayon] = {
            "count": len(articles_rayon),
            "haute_priorite": len([a for a in articles_rayon if a.get("priorite") == "haute"]),
            "suggestions_ia": len([a for a in articles_rayon if a.get("suggere_par_ia")]),
        }

    return stats


# ═══════════════════════════════════════════════════════════
# FORMATAGE
# ═══════════════════════════════════════════════════════════


def formater_article_label(article: dict) -> str:
    """
    Formate le label d'affichage d'un article.

    Args:
        article: Dictionnaire de l'article

    Returns:
        Label formate
    """
    priorite_emoji = PRIORITY_EMOJIS.get(article.get("priorite", "moyenne"), "[BLACK]")
    nom = article.get("ingredient_nom", "???")
    quantite = article.get("quantite_necessaire", 1)
    unite = article.get("unite", "")

    label = f"{priorite_emoji} {nom} ({quantite} {unite})"

    if article.get("notes"):
        label += f" | [NOTE] {article['notes']}"

    if article.get("suggere_par_ia"):
        label += " [SPARKLE]"

    return label


def formater_liste_impression(articles: list[dict]) -> str:
    """
    Formate la liste de courses pour impression.

    Args:
        articles: Liste des articles

    Returns:
        Texte formate pour impression
    """
    lignes = ["=" * 40, "LISTE DE COURSES", "=" * 40, ""]

    rayons = grouper_par_rayon(articles)

    for rayon in sorted(rayons.keys()):
        lignes.append(f"\n📦 {rayon.upper()}")
        lignes.append("-" * 20)

        for article in trier_par_priorite(rayons[rayon]):
            nom = article.get("ingredient_nom", "???")
            quantite = article.get("quantite_necessaire", 1)
            unite = article.get("unite", "")
            priorite_emoji = PRIORITY_EMOJIS.get(article.get("priorite"), "")

            lignes.append(f"  {priorite_emoji} [ ] {nom} - {quantite} {unite}")

    lignes.append("\n" + "=" * 40)
    lignes.append(f"Total: {len(articles)} articles")
    lignes.append(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    return "\n".join(lignes)


# ═══════════════════════════════════════════════════════════
# GÉNÉRATION DE SUGGESTIONS
# ═══════════════════════════════════════════════════════════


def generer_suggestions_depuis_stock_bas(alertes: dict) -> list[dict]:
    """
    Genère des suggestions d'articles depuis les alertes de stock.

    Args:
        alertes: Dictionnaire des alertes de l'inventaire

    Returns:
        Liste de suggestions d'articles
    """
    suggestions = []

    # Stock critique = haute priorite
    for item in alertes.get("critique", []):
        suggestions.append(
            {
                "ingredient_nom": item.get("ingredient_nom"),
                "quantite_necessaire": item.get("seuil_alerte", 1) - item.get("quantite", 0),
                "unite": item.get("unite", ""),
                "priorite": "haute",
                "rayon_magasin": item.get("rayon", "Autre"),
                "source": "stock_critique",
                "suggere_par_ia": False,
            }
        )

    # Stock bas = moyenne priorite
    for item in alertes.get("stock_bas", []):
        suggestions.append(
            {
                "ingredient_nom": item.get("ingredient_nom"),
                "quantite_necessaire": item.get("seuil_alerte", 1) - item.get("quantite", 0),
                "unite": item.get("unite", ""),
                "priorite": "moyenne",
                "rayon_magasin": item.get("rayon", "Autre"),
                "source": "stock_bas",
                "suggere_par_ia": False,
            }
        )

    return suggestions


def generer_suggestions_depuis_recettes(
    recettes_selectionnees: list[dict], inventaire: list[dict]
) -> list[dict]:
    """
    Genère des suggestions d'articles depuis les recettes selectionnees.

    Args:
        recettes_selectionnees: Liste des recettes à preparer
        inventaire: Liste de l'inventaire actuel

    Returns:
        Liste de suggestions d'articles
    """
    suggestions = []

    # Creer un index de l'inventaire par nom d'ingredient
    stock_index = {item.get("ingredient_nom", "").lower(): item for item in inventaire}

    for recette in recettes_selectionnees:
        for ingredient in recette.get("ingredients", []):
            nom = ingredient.get("nom", "").lower()
            quantite_requise = ingredient.get("quantite", 0)

            # Verifier le stock
            stock = stock_index.get(nom, {})
            quantite_en_stock = stock.get("quantite", 0)

            if quantite_requise > quantite_en_stock:
                manquant = quantite_requise - quantite_en_stock

                suggestions.append(
                    {
                        "ingredient_nom": ingredient.get("nom"),
                        "quantite_necessaire": manquant,
                        "unite": ingredient.get("unite", ""),
                        "priorite": "moyenne",
                        "rayon_magasin": ingredient.get("categorie", "Autre"),
                        "source": f"recette:{recette.get('nom')}",
                        "suggere_par_ia": True,
                    }
                )

    return suggestions


def deduper_suggestions(suggestions: list[dict]) -> list[dict]:
    """
    Deduplique les suggestions en gardant la plus haute priorite et cumulant les quantites.

    Args:
        suggestions: Liste des suggestions

    Returns:
        Liste dedupliquee avec quantites cumulees
    """
    index = {}

    for suggestion in suggestions:
        nom = suggestion.get("ingredient_nom", "").lower()

        if nom in index:
            existing = index[nom]
            # Toujours cumuler les quantites
            existing["quantite_necessaire"] += suggestion.get("quantite_necessaire", 0)
            # Garder la plus haute priorite
            if PRIORITY_ORDER.get(suggestion.get("priorite"), 99) < PRIORITY_ORDER.get(
                existing.get("priorite"), 99
            ):
                existing["priorite"] = suggestion["priorite"]
        else:
            index[nom] = suggestion.copy()

    return list(index.values())


# ═══════════════════════════════════════════════════════════
# HISTORIQUE ET MODÈLES
# ═══════════════════════════════════════════════════════════


def analyser_historique(historique: list[dict], jours: int = 30) -> dict:
    """
    Analyse l'historique d'achats pour detecter les patterns.

    Args:
        historique: Liste des achats passes
        jours: Nombre de jours à analyser

    Returns:
        Dictionnaire d'analyse
    """
    date_limite = datetime.now() - timedelta(days=jours)

    # Filtrer par date
    achats_recents = [a for a in historique if a.get("achete_le") and a["achete_le"] >= date_limite]

    # Compter les frequences
    frequences = {}
    for achat in achats_recents:
        nom = achat.get("ingredient_nom", "").lower()
        if nom not in frequences:
            frequences[nom] = {"count": 0, "quantites": [], "rayons": set()}
        frequences[nom]["count"] += 1
        frequences[nom]["quantites"].append(achat.get("quantite_necessaire", 0))
        frequences[nom]["rayons"].add(achat.get("rayon_magasin", "Autre"))

    # Identifier les articles recurrents (achetes plus de 2 fois)
    recurrents = [
        {
            "ingredient_nom": nom,
            "frequence": data["count"],
            "quantite_moyenne": sum(data["quantites"]) / len(data["quantites"])
            if data["quantites"]
            else 0,
            "rayon": list(data["rayons"])[0] if data["rayons"] else "Autre",
        }
        for nom, data in frequences.items()
        if data["count"] >= 2
    ]

    return {
        "total_achats": len(achats_recents),
        "articles_uniques": len(frequences),
        "recurrents": sorted(recurrents, key=lambda x: x["frequence"], reverse=True),
        "jours_analyses": jours,
    }


def generer_modele_depuis_historique(analyse: dict, seuil_frequence: int = 3) -> list[dict]:
    """
    Genère un modèle de liste à partir de l'analyse d'historique.

    Args:
        analyse: Resultat de analyser_historique()
        seuil_frequence: Frequence minimum pour inclusion

    Returns:
        Liste d'articles pour le modèle
    """
    return [
        {
            "ingredient_nom": item["ingredient_nom"],
            "quantite_necessaire": round(item["quantite_moyenne"]),
            "rayon_magasin": item["rayon"],
            "priorite": "moyenne",
            "source": "modele_historique",
        }
        for item in analyse.get("recurrents", [])
        if item["frequence"] >= seuil_frequence
    ]
