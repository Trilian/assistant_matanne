"""
Logique metier du module Inventaire - Separee de l'UI
Ce module contient toute la logique pure, testable sans Streamlit
"""

import logging
from datetime import date, datetime, timedelta
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════════════════════

EMPLACEMENTS = ["Réfrigérateur", "Congélateur", "Garde-manger", "Placard cuisine", "Cave", "Autre"]

CATEGORIES = [
    "Fruits & Légumes",
    "Viandes & Poissons",
    "Produits laitiers",
    "Épicerie",
    "Surgelés",
    "Boissons",
    "Condiments",
    "Autre",
]

STATUS_CONFIG = {
    "critique": {"color": "red", "emoji": "❌", "label": "Critique"},
    "stock_bas": {"color": "orange", "emoji": "🎯", "label": "Stock bas"},
    "ok": {"color": "green", "emoji": "💡", "label": "OK"},
    "perime": {"color": "black", "emoji": "⚫", "label": "Perime"},
    "bientot_perime": {"color": "yellow", "emoji": "📅", "label": "Bientôt perime"},
}


# ═══════════════════════════════════════════════════════════
# CALCUL DE STATUT
# ═══════════════════════════════════════════════════════════


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


# ═══════════════════════════════════════════════════════════
# FILTRAGE
# ═══════════════════════════════════════════════════════════


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


# ═══════════════════════════════════════════════════════════
# ALERTES
# ═══════════════════════════════════════════════════════════


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


# ═══════════════════════════════════════════════════════════
# STATISTIQUES
# ═══════════════════════════════════════════════════════════


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


# ═══════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════


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


# ═══════════════════════════════════════════════════════════
# FORMATAGE
# ═══════════════════════════════════════════════════════════


def formater_article_label(article: dict) -> str:
    """
    Formate le label d'affichage d'un article d'inventaire.

    Args:
        article: Dictionnaire de l'article

    Returns:
        Label formate
    """
    status = calculer_status_global(article)
    emoji = status["config"]["emoji"]

    nom = article.get("ingredient_nom", "???")
    quantite = article.get("quantite", 0)
    unite = article.get("unite", "")

    label = f"{emoji} {nom} ({quantite} {unite})"

    # Ajouter la date de peremption si proche
    if status["status_peremption"] in ["perime", "bientot_perime"]:
        date_peremption = article.get("date_peremption")
        if date_peremption:
            if isinstance(date_peremption, datetime):
                date_peremption = date_peremption.date()
            label += f" | 📅 {date_peremption.strftime('%d/%m')}"

    return label


def formater_inventaire_rapport(articles: list[dict]) -> str:
    """
    Formate l'inventaire pour un rapport.

    Args:
        articles: Liste des articles

    Returns:
        Texte formate
    """
    stats = calculer_statistiques_inventaire(articles)
    alertes = calculer_alertes(articles)

    lignes = [
        "=" * 40,
        "RAPPORT D'INVENTAIRE",
        "=" * 40,
        f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        "",
        "📊 RÉSUMÉ",
        "-" * 20,
        f"Total articles: {stats['total_articles']}",
        f"Articles OK: {stats['articles_ok']} ({stats['pct_ok']:.1f}%)",
        f"Alertes: {stats['articles_alerte']}",
        f"Valeur totale: {stats['valeur_totale']:.2f}€",
        "",
    ]

    # Alertes
    if alertes_critiques_existent(alertes):
        lignes.append("âš ï¸ ALERTES CRITIQUES")
        lignes.append("-" * 20)

        for article in alertes.get("critique", []):
            lignes.append(f"  ❌ {article.get('ingredient_nom')} - Stock critique")

        for article in alertes.get("perime", []):
            lignes.append(f"  ⚫ {article.get('ingredient_nom')} - PÉRIMÉ")

        lignes.append("")

    # Par emplacement
    lignes.append("[PKG] PAR EMPLACEMENT")
    lignes.append("-" * 20)

    stats_emp = calculer_statistiques_par_emplacement(articles)
    for emplacement, emp_stats in sorted(stats_emp.items()):
        lignes.append(f"  {emplacement}: {emp_stats['count']} articles")

    lignes.append("\n" + "=" * 40)

    return "\n".join(lignes)


# ═══════════════════════════════════════════════════════════
# UTILITAIRES
# ═══════════════════════════════════════════════════════════


def calculer_jours_avant_peremption(article: dict) -> int | None:
    """
    Calcule le nombre de jours avant peremption.

    Args:
        article: Dictionnaire de l'article

    Returns:
        Nombre de jours ou None si pas de date
    """
    date_peremption = article.get("date_peremption")

    if not date_peremption:
        return None

    if isinstance(date_peremption, str):
        try:
            date_peremption = datetime.fromisoformat(date_peremption).date()
        except ValueError:
            return None
    elif isinstance(date_peremption, datetime):
        date_peremption = date_peremption.date()

    return (date_peremption - date.today()).days


def grouper_par_emplacement(articles: list[dict]) -> dict[str, list[dict]]:
    """
    Groupe les articles par emplacement.

    Args:
        articles: Liste des articles

    Returns:
        Dictionnaire {emplacement: [articles]}
    """
    groupes = {}
    for article in articles:
        emplacement = article.get("emplacement", "Autre")
        if emplacement not in groupes:
            groupes[emplacement] = []
        groupes[emplacement].append(article)
    return groupes


def grouper_par_categorie(articles: list[dict]) -> dict[str, list[dict]]:
    """
    Groupe les articles par categorie.

    Args:
        articles: Liste des articles

    Returns:
        Dictionnaire {categorie: [articles]}
    """
    groupes = {}
    for article in articles:
        categorie = article.get("categorie", "Autre")
        if categorie not in groupes:
            groupes[categorie] = []
        groupes[categorie].append(article)
    return groupes


def trier_par_peremption(articles: list[dict]) -> list[dict]:
    """
    Trie les articles par date de peremption (plus proche en premier).

    Args:
        articles: Liste des articles

    Returns:
        Liste triee
    """

    def sort_key(article):
        jours = calculer_jours_avant_peremption(article)
        return jours if jours is not None else 9999

    return sorted(articles, key=sort_key)


def trier_par_urgence(articles: list[dict]) -> list[dict]:
    """
    Trie les articles par urgence (perimes/critiques en premier).

    Args:
        articles: Liste des articles

    Returns:
        Liste triee
    """
    ordre_priorite = {"perime": 0, "critique": 1, "bientot_perime": 2, "stock_bas": 3, "ok": 4}

    def sort_key(article):
        status = calculer_status_global(article)["status_prioritaire"]
        return ordre_priorite.get(status, 99)

    return sorted(articles, key=sort_key)


def formater_article_inventaire(article: dict) -> dict:
    """
    Formate un article d'inventaire pour l'affichage.

    Args:
        article: Article brut de la base de donnees

    Returns:
        Article formate avec des champs supplementaires pour l'UI
    """
    status_stock = calculer_status_stock(article)
    status_peremption = calculer_status_peremption(article)

    emoji_stock = STATUS_CONFIG.get(status_stock, {}).get("emoji", "â“")
    emoji_peremption = STATUS_CONFIG.get(status_peremption, {}).get("emoji", "â“")

    jours_peremption = calculer_jours_avant_peremption(article)

    return {
        **article,
        "status_stock": status_stock,
        "status_peremption": status_peremption,
        "emoji_stock": emoji_stock,
        "emoji_peremption": emoji_peremption,
        "jours_avant_peremption": jours_peremption,
        "affichage_stock": f"{emoji_stock} {article.get('ingredient_nom', 'Inconnu')}",
        "affichage_quantite": f"{article.get('quantite', 0)} {article.get('unite', '')}".strip(),
    }


# ============================================================
# Fonctions importées depuis utilitaires.py
# ============================================================


def _prepare_inventory_dataframe(inventaire: list[dict[str, Any]]) -> pd.DataFrame:
    """Prépare un DataFrame pour affichage inventaire"""
    data = []
    for article in inventaire:
        statut_icon = {
            "critique": "❌",
            "stock_bas": "âš ",
            "peremption_proche": "⏰",
            "ok": "✅",
        }.get(article["statut"], "❓")

        data.append(
            {
                "Statut": f"{statut_icon} {article['statut']}",
                "Article": article["ingredient_nom"],
                "Catégorie": article["ingredient_categorie"],
                "Quantité": f"{article['quantite']:.1f} {article['unite']}",
                "Seuil min": f"{article['quantite_min']:.1f} {article['unite']}",
                "Emplacement": article["emplacement"] or "-",
                "Jours": article["jours_avant_peremption"] or "-",
                "Maj": pd.Timestamp(article["derniere_maj"]).strftime("%d/%m/%Y")
                if "derniere_maj" in article
                else "-",
            }
        )

    return pd.DataFrame(data)


def _prepare_alert_dataframe(articles: list[dict[str, Any]]) -> pd.DataFrame:
    """Prépare un DataFrame pour affichage alertes"""
    data = []
    for article in articles:
        statut_icon = {
            "critique": "❌",
            "stock_bas": "âš ",
            "peremption_proche": "⏰",
        }.get(article["statut"], "❓")

        jours = ""
        if article["jours_avant_peremption"] is not None:
            jours = f"{article['jours_avant_peremption']} jours"

        data.append(
            {
                "Article": article["ingredient_nom"],
                "Catégorie": article["ingredient_categorie"],
                "Quantité": f"{article['quantite']:.1f} {article['unite']}",
                "Seuil": f"{article['quantite_min']:.1f}",
                "Emplacement": article["emplacement"] or "-",
                "Problème": jours if jours else "Stock critique",
            }
        )

    return pd.DataFrame(data)


__all__ = ["_prepare_inventory_dataframe", "_prepare_alert_dataframe"]
