"""
Fonctions utilitaires pures pour la liste de courses.
Ces fonctions n'ont pas de dépendance Streamlit et sont facilement testables.
"""

from datetime import datetime
from typing import Any

# -----------------------------------------------------------
# FILTRAGE ET TRANSFORMATION
# -----------------------------------------------------------


def filtrer_liste(
    liste: list[dict[str, Any]],
    priorite: str | None = None,
    rayon: str | None = None,
    search_term: str | None = None,
) -> list[dict[str, Any]]:
    """
    Filtre la liste de courses selon les critères spécifiés.

    Args:
        liste: Liste brute des articles
        priorite: Priorité à filtrer ("haute", "moyenne", "basse") ou None
        rayon: Rayon à filtrer ou None
        search_term: Terme de recherche ou None

    Returns:
        Liste filtrée
    """
    liste_filtree = liste.copy()

    if priorite:
        liste_filtree = [a for a in liste_filtree if a.get("priorite") == priorite]

    if rayon:
        liste_filtree = [a for a in liste_filtree if a.get("rayon_magasin") == rayon]

    if search_term:
        term_lower = search_term.lower()
        liste_filtree = [
            a for a in liste_filtree if term_lower in a.get("ingredient_nom", "").lower()
        ]

    return liste_filtree


def grouper_par_rayon(liste: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """
    Regroupe les articles par rayon.

    Args:
        liste: Liste des articles

    Returns:
        Dictionnaire {rayon: [articles]}
    """
    rayons: dict[str, list[dict[str, Any]]] = {}

    for article in liste:
        rayon = article.get("rayon_magasin") or "Autre"
        if rayon not in rayons:
            rayons[rayon] = []
        rayons[rayon].append(article)

    return rayons


def calculer_statistiques_liste(
    liste: list[dict[str, Any]],
    liste_achetee: list[dict[str, Any]] | None = None,
    alertes_stock: list[Any] | None = None,
) -> dict[str, int]:
    """
    Calcule les statistiques de la liste de courses.

    Args:
        liste: Liste des articles à acheter
        liste_achetee: Liste des articles achetés (optionnel)
        alertes_stock: Liste des alertes de stock bas (optionnel)

    Returns:
        Dict avec les statistiques
    """
    return {
        "a_acheter": len(liste),
        "haute_priorite": len([a for a in liste if a.get("priorite") == "haute"]),
        "stock_bas": len(alertes_stock) if alertes_stock else 0,
        "total_achetes": len(liste_achetee) if liste_achetee else 0,
    }


# -----------------------------------------------------------
# FORMATAGE
# -----------------------------------------------------------


def formater_article_label(
    article: dict[str, Any],
    priority_emojis: dict[str, str],
    include_notes: bool = True,
    include_ia_marker: bool = True,
) -> str:
    """
    Formate le label d'affichage d'un article.

    Args:
        article: Article à formater
        priority_emojis: Mapping priorité → emoji
        include_notes: Inclure les notes dans le label
        include_ia_marker: Inclure le marqueur IA

    Returns:
        Label formaté
    """
    priorite_emoji = priority_emojis.get(article.get("priorite", "moyenne"), "⚫")
    nom = article.get("ingredient_nom", "")
    quantite = article.get("quantite_necessaire", 0)
    unite = article.get("unite", "")

    # Nettoyer l'unité pour l'affichage
    quantite_fmt = int(quantite) if quantite == int(quantite) else round(quantite, 1)
    unite_affichage = unite.strip() if unite else ""
    unites_generiques = ("pcs", "piece", "pièce", "portion", "")

    if unite_affichage and unite_affichage.lower() not in unites_generiques:
        label = f"{priorite_emoji} {nom} ({quantite_fmt} {unite_affichage})"
    elif quantite and quantite > 1:
        # Pour les quantités > 1 avec unité générique, afficher ×N
        label = f"{priorite_emoji} {nom} (×{quantite_fmt})"
    else:
        label = f"{priorite_emoji} {nom}"

    if include_notes and article.get("notes"):
        label += f" | 📝 {article.get('notes')}"

    if include_ia_marker and article.get("suggere_par_ia"):
        label += " ⏰"

    return label


def generer_texte_impression(
    liste: list[dict[str, Any]],
    titre: str = "LISTE DE COURSES",
    date_format: str = "%d/%m/%Y %H:%M",
) -> str:
    """
    Génère le texte formaté pour l'impression de la liste.

    Args:
        liste: Liste des articles
        titre: Titre de la liste
        date_format: Format de la date

    Returns:
        Texte formaté pour impression
    """
    rayons = grouper_par_rayon(liste)

    lignes = [
        f"📋 {titre}",
        f"📅 {datetime.now().strftime(date_format)}",
        "=" * 40,
        "",
    ]

    for rayon in sorted(rayons.keys()):
        lignes.append(f"🏪 {rayon}")
        for article in rayons[rayon]:
            checkbox = "☐"
            qty = f"{article.get('quantite_necessaire')} {article.get('unite')}"
            lignes.append(f"  {checkbox} {article.get('ingredient_nom')} ({qty})")
        lignes.append("")

    return "\n".join(lignes)


# -----------------------------------------------------------
# VALIDATION
# -----------------------------------------------------------


def valider_article_data(data: dict[str, Any]) -> tuple[bool, str]:
    """
    Valide les données d'un article avant création/modification.

    Args:
        data: Données de l'article

    Returns:
        Tuple (est_valide, message_erreur)
    """
    if not data.get("ingredient_id"):
        return False, "ID d'ingrédient requis"

    quantite = data.get("quantite_necessaire", 0)
    if quantite <= 0:
        return False, "La quantité doit être positive"

    priorite = data.get("priorite", "")
    if priorite and priorite not in ("haute", "moyenne", "basse"):
        return False, "Priorité invalide (haute, moyenne, basse)"

    return True, ""


def extraire_rayons_uniques(liste: list[dict[str, Any]]) -> list[str]:
    """
    Extrait la liste des rayons uniques triés.

    Args:
        liste: Liste des articles

    Returns:
        Liste des rayons uniques triés
    """
    return sorted({a.get("rayon_magasin") or "Autre" for a in liste})


__all__ = [
    "filtrer_liste",
    "grouper_par_rayon",
    "calculer_statistiques_liste",
    "formater_article_label",
    "generer_texte_impression",
    "valider_article_data",
    "extraire_rayons_uniques",
]
