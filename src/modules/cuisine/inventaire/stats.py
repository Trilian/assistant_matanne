"""Statistiques de l'inventaire."""

from .alertes_logic import calculer_alertes, compter_alertes
from .status import calculer_status_global


def calculer_statistiques_inventaire(articles: list[dict]) -> dict:
    """
    Calcule les statistiques generales de l'inventaire.

    Args:
        articles: Liste des articles de l'inventaire

    Returns:
        Dictionnaire des statistiques
    """
    if not articles:
        return {
            "total_articles": 0,
            "valeur_totale": 0,
            "articles_ok": 0,
            "articles_alerte": 0,
            "emplacements_uniques": 0,
            "categories_uniques": 0,
            "pct_ok": 0.0,
            "pct_alerte": 0.0,
        }

    alertes = calculer_alertes(articles)

    stats = {
        "total_articles": len(articles),
        "valeur_totale": sum(a.get("quantite", 0) * a.get("prix_unitaire", 0) for a in articles),
        "articles_ok": len(
            [a for a in articles if calculer_status_global(a)["status_prioritaire"] == "ok"]
        ),
        "articles_alerte": sum(compter_alertes(alertes).values()),
        "emplacements_uniques": len(set(a.get("emplacement", "Autre") for a in articles)),
        "categories_uniques": len(set(a.get("categorie", "Autre") for a in articles)),
    }

    # Pourcentages
    stats["pct_ok"] = (
        (stats["articles_ok"] / stats["total_articles"] * 100) if stats["total_articles"] > 0 else 0
    )
    stats["pct_alerte"] = 100 - stats["pct_ok"]

    return stats


def calculer_statistiques_par_emplacement(articles: list[dict]) -> dict[str, dict]:
    """
    Calcule les statistiques par emplacement.

    Args:
        articles: Liste des articles

    Returns:
        Dictionnaire {emplacement: {stats}}
    """
    emplacements = {}

    for article in articles:
        emplacement = article.get("emplacement", "Autre")
        if emplacement not in emplacements:
            emplacements[emplacement] = []
        emplacements[emplacement].append(article)

    stats = {}
    for emplacement, articles_emp in emplacements.items():
        alertes = calculer_alertes(articles_emp)
        stats[emplacement] = {
            "count": len(articles_emp),
            "alertes": sum(compter_alertes(alertes).values()),
            "valeur": sum(a.get("quantite", 0) * a.get("prix_unitaire", 0) for a in articles_emp),
        }

    return stats


def calculer_statistiques_par_categorie(articles: list[dict]) -> dict[str, dict]:
    """
    Calcule les statistiques par categorie.

    Args:
        articles: Liste des articles

    Returns:
        Dictionnaire {categorie: {stats}}
    """
    categories = {}

    for article in articles:
        categorie = article.get("categorie", "Autre")
        if categorie not in categories:
            categories[categorie] = []
        categories[categorie].append(article)

    stats = {}
    for categorie, articles_cat in categories.items():
        alertes = calculer_alertes(articles_cat)
        stats[categorie] = {
            "count": len(articles_cat),
            "alertes": sum(compter_alertes(alertes).values()),
            "valeur": sum(a.get("quantite", 0) * a.get("prix_unitaire", 0) for a in articles_cat),
        }

    return stats
