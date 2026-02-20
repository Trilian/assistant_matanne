"""Calcul de statut des articles d'inventaire."""

from datetime import date, datetime, timedelta

from .constants import STATUS_CONFIG


def calculer_status_stock(article: dict) -> str:
    """
    Calcule le statut de stock d'un article.

    Args:
        article: Dictionnaire de l'article d'inventaire

    Returns:
        Statut: 'critique', 'stock_bas', 'ok'
    """
    quantite = article.get("quantite", 0)
    seuil_alerte = article.get("seuil_alerte", 5)
    seuil_critique = article.get("seuil_critique", 2)

    if quantite <= seuil_critique:
        return "critique"
    elif quantite <= seuil_alerte:
        return "stock_bas"
    return "ok"


def calculer_status_peremption(article: dict, jours_alerte: int = 7) -> str:
    """
    Calcule le statut de peremption d'un article.

    Args:
        article: Dictionnaire de l'article d'inventaire
        jours_alerte: Nombre de jours avant peremption pour alerter

    Returns:
        Statut: 'perime', 'bientot_perime', 'ok'
    """
    date_peremption = article.get("date_peremption")

    if not date_peremption:
        return "ok"

    # Normaliser la date
    if isinstance(date_peremption, str):
        try:
            date_peremption = datetime.fromisoformat(date_peremption).date()
        except ValueError:
            return "ok"
    elif isinstance(date_peremption, datetime):
        date_peremption = date_peremption.date()

    aujourd_hui = date.today()

    if date_peremption < aujourd_hui:
        return "perime"
    elif date_peremption <= aujourd_hui + timedelta(days=jours_alerte):
        return "bientot_perime"
    return "ok"


def calculer_status_global(article: dict, jours_alerte_peremption: int = 7) -> dict:
    """
    Calcule le statut global d'un article (stock + peremption).

    Args:
        article: Dictionnaire de l'article d'inventaire
        jours_alerte_peremption: Jours avant peremption pour alerter

    Returns:
        Dictionnaire avec status_stock, status_peremption, status_prioritaire
    """
    status_stock = calculer_status_stock(article)
    status_peremption = calculer_status_peremption(article, jours_alerte_peremption)

    # Priorite: perime > critique > bientôt perime > stock bas > ok
    if status_peremption == "perime":
        prioritaire = "perime"
    elif status_stock == "critique":
        prioritaire = "critique"
    elif status_peremption == "bientot_perime":
        prioritaire = "bientot_perime"
    elif status_stock == "stock_bas":
        prioritaire = "stock_bas"
    else:
        prioritaire = "ok"

    return {
        "status_stock": status_stock,
        "status_peremption": status_peremption,
        "status_prioritaire": prioritaire,
        "config": STATUS_CONFIG.get(prioritaire, STATUS_CONFIG["ok"]),
    }
