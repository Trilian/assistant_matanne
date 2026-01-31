"""
Logique métier du module Inventaire - Séparée de l'UI
Ce module contient toute la logique pure, testable sans Streamlit
"""

from datetime import datetime, timedelta, date
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════════════════════

EMPLACEMENTS = [
    "Réfrigérateur",
    "Congélateur",
    "Garde-manger",
    "Placard cuisine",
    "Cave",
    "Autre"
]

CATEGORIES = [
    "Fruits & Légumes",
    "Viandes & Poissons",
    "Produits laitiers",
    "Épicerie",
    "Surgelés",
    "Boissons",
    "Condiments",
    "Autre"
]

STATUS_CONFIG = {
    "critique": {"color": "red", "emoji": "❌", "label": "Critique"},
    "stock_bas": {"color": "orange", "emoji": "🎯", "label": "Stock bas"},
    "ok": {"color": "green", "emoji": "💡", "label": "OK"},
    "perime": {"color": "black", "emoji": "⚫", "label": "Périmé"},
    "bientot_perime": {"color": "yellow", "emoji": "📅", "label": "Bientôt périmé"},
}


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CALCUL DE STATUT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

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
    Calcule le statut de péremption d'un article.
    
    Args:
        article: Dictionnaire de l'article d'inventaire
        jours_alerte: Nombre de jours avant péremption pour alerter
        
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
    Calcule le statut global d'un article (stock + péremption).
    
    Args:
        article: Dictionnaire de l'article d'inventaire
        jours_alerte_peremption: Jours avant péremption pour alerter
        
    Returns:
        Dictionnaire avec status_stock, status_peremption, status_prioritaire
    """
    status_stock = calculer_status_stock(article)
    status_peremption = calculer_status_peremption(article, jours_alerte_peremption)
    
    # Priorité: périmé > critique > bientôt périmé > stock bas > ok
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
        "config": STATUS_CONFIG.get(prioritaire, STATUS_CONFIG["ok"])
    }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FILTRAGE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def filtrer_par_emplacement(articles: list[dict], emplacement: str) -> list[dict]:
    """
    Filtre les articles par emplacement.
    
    Args:
        articles: Liste des articles
        emplacement: Emplacement à filtrer ou None pour tout
        
    Returns:
        Liste filtrée
    """
    if not emplacement or emplacement.lower() == "tous":
        return articles
    
    return [a for a in articles if a.get("emplacement") == emplacement]


def filtrer_par_categorie(articles: list[dict], categorie: str) -> list[dict]:
    """
    Filtre les articles par catégorie.
    
    Args:
        articles: Liste des articles
        categorie: Catégorie à filtrer ou None pour tout
        
    Returns:
        Liste filtrée
    """
    if not categorie or categorie.lower() == "toutes":
        return articles
    
    return [a for a in articles if a.get("categorie") == categorie]


def filtrer_par_status(articles: list[dict], status: str) -> list[dict]:
    """
    Filtre les articles par statut.
    
    Args:
        articles: Liste des articles (avec status_prioritaire calculé)
        status: Statut à filtrer ou None pour tout
        
    Returns:
        Liste filtrée
    """
    if not status or status.lower() == "tous":
        return articles
    
    return [
        a for a in articles 
        if calculer_status_global(a)["status_prioritaire"] == status
    ]


def filtrer_par_recherche(articles: list[dict], terme: str) -> list[dict]:
    """
    Filtre les articles par terme de recherche.
    
    Args:
        articles: Liste des articles
        terme: Terme de recherche
        
    Returns:
        Liste filtrée
    """
    if not terme:
        return articles
    
    terme_lower = terme.lower()
    return [
        a for a in articles
        if terme_lower in a.get("ingredient_nom", "").lower()
        or terme_lower in a.get("notes", "").lower()
    ]


def filtrer_inventaire(
    articles: list[dict],
    emplacement: Optional[str] = None,
    categorie: Optional[str] = None,
    status: Optional[str] = None,
    recherche: Optional[str] = None
) -> list[dict]:
    """
    Applique plusieurs filtres à l'inventaire.
    
    Args:
        articles: Liste des articles
        emplacement: Filtre par emplacement
        categorie: Filtre par catégorie
        status: Filtre par statut
        recherche: Terme de recherche
        
    Returns:
        Liste filtrée
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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ALERTES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def calculer_alertes(articles: list[dict], jours_peremption: int = 7) -> dict:
    """
    Calcule toutes les alertes de l'inventaire.
    
    Args:
        articles: Liste des articles de l'inventaire
        jours_peremption: Jours avant péremption pour alerter
        
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
    Vérifie s'il existe des alertes critiques.
    
    Args:
        alertes: Dictionnaire des alertes
        
    Returns:
        True si des alertes critiques ou périmées existent
    """
    return len(alertes.get("critique", [])) > 0 or len(alertes.get("perime", [])) > 0


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# STATISTIQUES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def calculer_statistiques_inventaire(articles: list[dict]) -> dict:
    """
    Calcule les statistiques générales de l'inventaire.
    
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
        "valeur_totale": sum(
            a.get("quantite", 0) * a.get("prix_unitaire", 0)
            for a in articles
        ),
        "articles_ok": len([a for a in articles if calculer_status_global(a)["status_prioritaire"] == "ok"]),
        "articles_alerte": sum(compter_alertes(alertes).values()),
        "emplacements_uniques": len(set(a.get("emplacement", "Autre") for a in articles)),
        "categories_uniques": len(set(a.get("categorie", "Autre") for a in articles)),
    }
    
    # Pourcentages
    stats["pct_ok"] = (stats["articles_ok"] / stats["total_articles"] * 100) if stats["total_articles"] > 0 else 0
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
            "valeur": sum(
                a.get("quantite", 0) * a.get("prix_unitaire", 0)
                for a in articles_emp
            ),
        }
    
    return stats


def calculer_statistiques_par_categorie(articles: list[dict]) -> dict[str, dict]:
    """
    Calcule les statistiques par catégorie.
    
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
            "valeur": sum(
                a.get("quantite", 0) * a.get("prix_unitaire", 0)
                for a in articles_cat
            ),
        }
    
    return stats


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# VALIDATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def valider_article_inventaire(article: dict) -> tuple[bool, list[str]]:
    """
    Valide les données d'un article d'inventaire.
    
    Args:
        article: Dictionnaire des données
        
    Returns:
        Tuple (est_valide, liste_erreurs)
    """
    erreurs = []
    
    # Nom requis
    if not article.get("ingredient_nom"):
        erreurs.append("Le nom de l'ingrédient est requis")
    elif len(article["ingredient_nom"]) < 2:
        erreurs.append("Le nom doit contenir au moins 2 caractères")
    
    # Quantité positive ou zéro
    quantite = article.get("quantite", 0)
    if quantite is not None and quantite < 0:
        erreurs.append("La quantité ne peut pas être négative")
    
    # Seuils cohérents
    seuil_alerte = article.get("seuil_alerte", 5)
    seuil_critique = article.get("seuil_critique", 2)
    if seuil_critique > seuil_alerte:
        erreurs.append("Le seuil critique ne peut pas être supérieur au seuil d'alerte")
    
    # Emplacement valide
    emplacement = article.get("emplacement")
    if emplacement and emplacement not in EMPLACEMENTS:
        logger.warning(f"Emplacement non standard: {emplacement}")
    
    # Catégorie valide
    categorie = article.get("categorie")
    if categorie and categorie not in CATEGORIES:
        logger.warning(f"Catégorie non standard: {categorie}")
    
    # Date de péremption dans le futur (si fournie pour nouvel article)
    date_peremption = article.get("date_peremption")
    if date_peremption:
        if isinstance(date_peremption, str):
            try:
                date_peremption = datetime.fromisoformat(date_peremption).date()
            except ValueError:
                erreurs.append("Format de date de péremption invalide")
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
    date_peremption: Optional[date] = None,
    seuil_alerte: int = 5,
    seuil_critique: int = 2
) -> tuple[bool, dict | list[str]]:
    """
    Valide et prépare les données d'un nouvel article d'inventaire.
    
    Args:
        nom: Nom de l'ingrédient
        quantite: Quantité en stock
        unite: Unité de mesure
        emplacement: Emplacement de stockage
        categorie: Catégorie de l'article
        date_peremption: Date de péremption (optionnel)
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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FORMATAGE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def formater_article_label(article: dict) -> str:
    """
    Formate le label d'affichage d'un article d'inventaire.
    
    Args:
        article: Dictionnaire de l'article
        
    Returns:
        Label formaté
    """
    status = calculer_status_global(article)
    emoji = status["config"]["emoji"]
    
    nom = article.get("ingredient_nom", "???")
    quantite = article.get("quantite", 0)
    unite = article.get("unite", "")
    
    label = f"{emoji} {nom} ({quantite} {unite})"
    
    # Ajouter la date de péremption si proche
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
        Texte formaté
    """
    stats = calculer_statistiques_inventaire(articles)
    alertes = calculer_alertes(articles)
    
    lignes = [
        "=" * 40,
        "RAPPORT D'INVENTAIRE",
        "=" * 40,
        f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        "",
        "[CHART] RÉSUMÉ",
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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# UTILITAIRES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def calculer_jours_avant_peremption(article: dict) -> Optional[int]:
    """
    Calcule le nombre de jours avant péremption.
    
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
    Groupe les articles par catégorie.
    
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
    Trie les articles par date de péremption (plus proche en premier).
    
    Args:
        articles: Liste des articles
        
    Returns:
        Liste triée
    """
    def sort_key(article):
        jours = calculer_jours_avant_peremption(article)
        return jours if jours is not None else 9999
    
    return sorted(articles, key=sort_key)


def trier_par_urgence(articles: list[dict]) -> list[dict]:
    """
    Trie les articles par urgence (périmés/critiques en premier).
    
    Args:
        articles: Liste des articles
        
    Returns:
        Liste triée
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
        article: Article brut de la base de données
        
    Returns:
        Article formaté avec des champs supplémentaires pour l'UI
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

