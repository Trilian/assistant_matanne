"""Logique de calcul des alertes d'inventaire."""

from .status import calculer_status_global


def calculer_alertes(articles: list[dict], jours_peremption: int = 7) -> dict:
    """
    Calcule toutes les alertes de l'inventaire.

    Args:
        articles: Liste des articles de l'inventaire
        jours_peremption: Jours avant peremption pour alerter

    Returns:
        Dictionnaire des alertes par type
    """
    alertes = {
        "critique": [],
        "stock_bas": [],
        "perime": [],
        "bientot_perime": [],
    }

    for article in articles:
        status = calculer_status_global(article, jours_peremption)

        if status["status_stock"] == "critique":
            alertes["critique"].append(article)
        elif status["status_stock"] == "stock_bas":
            alertes["stock_bas"].append(article)

        if status["status_peremption"] == "perime":
            alertes["perime"].append(article)
        elif status["status_peremption"] == "bientot_perime":
            alertes["bientot_perime"].append(article)

    return alertes


def compter_alertes(alertes: dict) -> dict:
    """
    Compte le nombre d'alertes par type.

    Args:
        alertes: Dictionnaire des alertes

    Returns:
        Dictionnaire {type: count}
    """
    return {key: len(value) for key, value in alertes.items()}


def alertes_critiques_existent(alertes: dict) -> bool:
    """
    Verifie s'il existe des alertes critiques.

    Args:
        alertes: Dictionnaire des alertes

    Returns:
        True si des alertes critiques ou perimees existent
    """
    return len(alertes.get("critique", [])) > 0 or len(alertes.get("perime", [])) > 0
