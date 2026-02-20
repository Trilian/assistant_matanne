"""Filtrage des articles d'inventaire."""

from .status import calculer_status_global


def filtrer_par_emplacement(articles: list[dict], emplacement: str) -> list[dict]:
    """
    Filtre les articles par emplacement.

    Args:
        articles: Liste des articles
        emplacement: Emplacement à filtrer ou None pour tout

    Returns:
        Liste filtree
    """
    if not emplacement or emplacement.lower() == "tous":
        return articles

    return [a for a in articles if a.get("emplacement") == emplacement]


def filtrer_par_categorie(articles: list[dict], categorie: str) -> list[dict]:
    """
    Filtre les articles par categorie.

    Args:
        articles: Liste des articles
        categorie: Categorie à filtrer ou None pour tout

    Returns:
        Liste filtree
    """
    if not categorie or categorie.lower() == "toutes":
        return articles

    return [a for a in articles if a.get("categorie") == categorie]


def filtrer_par_status(articles: list[dict], status: str) -> list[dict]:
    """
    Filtre les articles par statut.

    Args:
        articles: Liste des articles (avec status_prioritaire calcule)
        status: Statut à filtrer ou None pour tout

    Returns:
        Liste filtree
    """
    if not status or status.lower() == "tous":
        return articles

    return [a for a in articles if calculer_status_global(a)["status_prioritaire"] == status]


def filtrer_par_recherche(articles: list[dict], terme: str) -> list[dict]:
    """
    Filtre les articles par terme de recherche.

    Args:
        articles: Liste des articles
        terme: Terme de recherche

    Returns:
        Liste filtree
    """
    if not terme:
        return articles

    terme_lower = terme.lower()
    return [
        a
        for a in articles
        if terme_lower in a.get("ingredient_nom", "").lower()
        or terme_lower in a.get("notes", "").lower()
    ]


def filtrer_inventaire(
    articles: list[dict],
    emplacement: str | None = None,
    categorie: str | None = None,
    status: str | None = None,
    recherche: str | None = None,
) -> list[dict]:
    """
    Applique plusieurs filtres à l'inventaire.

    Args:
        articles: Liste des articles
        emplacement: Filtre par emplacement
        categorie: Filtre par categorie
        status: Filtre par statut
        recherche: Terme de recherche

    Returns:
        Liste filtree
    """
    result = articles.copy()

    if emplacement:
        result = filtrer_par_emplacement(result, emplacement)
    if categorie:
        result = filtrer_par_categorie(result, categorie)
    if status:
        result = filtrer_par_status(result, status)
    if recherche:
        result = filtrer_par_recherche(result, recherche)

    return result
