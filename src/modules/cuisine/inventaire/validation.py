"""Validation des articles d'inventaire."""

import logging
from datetime import date, datetime

from .constants import CATEGORIES, EMPLACEMENTS

logger = logging.getLogger(__name__)


def valider_article_inventaire(article: dict) -> tuple[bool, list[str]]:
    """
    Valide les donnees d'un article d'inventaire.

    Args:
        article: Dictionnaire des donnees

    Returns:
        Tuple (est_valide, liste_erreurs)
    """
    erreurs = []

    # Nom requis
    if not article.get("ingredient_nom"):
        erreurs.append("Le nom de l'ingredient est requis")
    elif len(article["ingredient_nom"]) < 2:
        erreurs.append("Le nom doit contenir au moins 2 caractères")

    # Quantite positive ou zero
    quantite = article.get("quantite", 0)
    if quantite is not None and quantite < 0:
        erreurs.append("La quantite ne peut pas être negative")

    # Seuils coherents
    seuil_alerte = article.get("seuil_alerte", 5)
    seuil_critique = article.get("seuil_critique", 2)
    if seuil_critique > seuil_alerte:
        erreurs.append("Le seuil critique ne peut pas être superieur au seuil d'alerte")

    # Emplacement valide
    emplacement = article.get("emplacement")
    if emplacement and emplacement not in EMPLACEMENTS:
        logger.warning(f"Emplacement non standard: {emplacement}")

    # Categorie valide
    categorie = article.get("categorie")
    if categorie and categorie not in CATEGORIES:
        logger.warning(f"Categorie non standard: {categorie}")

    # Date de peremption dans le futur (si fournie pour nouvel article)
    date_peremption = article.get("date_peremption")
    if date_peremption:
        if isinstance(date_peremption, str):
            try:
                date_peremption = datetime.fromisoformat(date_peremption).date()
            except ValueError:
                erreurs.append("Format de date de peremption invalide")
                return len(erreurs) == 0, erreurs

        if isinstance(date_peremption, datetime):
            date_peremption = date_peremption.date()

    return len(erreurs) == 0, erreurs


def valider_nouvel_article_inventaire(
    nom: str,
    quantite: float,
    unite: str,
    emplacement: str = "Autre",
    categorie: str = "Autre",
    date_peremption: date | None = None,
    seuil_alerte: int = 5,
    seuil_critique: int = 2,
) -> tuple[bool, dict | list[str]]:
    """
    Valide et prepare les donnees d'un nouvel article d'inventaire.

    Args:
        nom: Nom de l'ingredient
        quantite: Quantite en stock
        unite: Unite de mesure
        emplacement: Emplacement de stockage
        categorie: Categorie de l'article
        date_peremption: Date de peremption (optionnel)
        seuil_alerte: Seuil pour alerte stock bas
        seuil_critique: Seuil pour alerte critique

    Returns:
        Tuple (est_valide, article_ou_erreurs)
    """
    article = {
        "ingredient_nom": nom.strip() if nom else "",
        "quantite": quantite,
        "unite": unite,
        "emplacement": emplacement,
        "categorie": categorie,
        "date_peremption": date_peremption,
        "seuil_alerte": seuil_alerte,
        "seuil_critique": seuil_critique,
        "date_ajout": datetime.now(),
    }

    est_valide, erreurs = valider_article_inventaire(article)

    if est_valide:
        return True, article
    return False, erreurs
