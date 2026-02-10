"""
Logique métier du module Courses - Séparée de l'UI
Ce module contient toute la logique pure, testable sans Streamlit
"""

from datetime import datetime, timedelta, date
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════════════════════════════

PRIORITY_EMOJIS = {
    "haute": "🔴",
    "moyenne": "🟡",
    "basse": "🟢"
}

PRIORITY_ORDER = {"haute": 0, "moyenne": 1, "basse": 2}

RAYONS_DEFAULT = [
    "Fruits & Légumes",
    "Laitier",
    "Boulangerie",
    "Viandes",
    "Poissons",
    "Surgelés",
    "Épices",
    "Boissons",
    "Autre"
]


# ═══════════════════════════════════════════════════════════════════════════════════
# FONCTIONS DE FILTRAGE
# ═══════════════════════════════════════════════════════════════════════════════════

def filtrer_par_priorite(articles: list[dict], priorite: str) -> list[dict]:
    """
    Filtre les articles par priorité.
    
    Args:
        articles: Liste des articles
        priorite: 'haute', 'moyenne', 'basse' ou None pour tout garder
        
    Returns:
        Liste filtrée
    """
    if not priorite or priorite.lower() == "toutes":
        return articles
    
    return [a for a in articles if a.get("priorite") == priorite]


def filtrer_par_rayon(articles: list[dict], rayon: str) -> list[dict]:
    """
    Filtre les articles par rayon de magasin.
    
    Args:
        articles: Liste des articles
        rayon: Nom du rayon ou None pour tout garder
        
    Returns:
        Liste filtrée
    """
    if not rayon or rayon.lower() == "tous les rayons":
        return articles
    
    return [a for a in articles if a.get("rayon_magasin") == rayon]


def filtrer_par_recherche(articles: list[dict], terme: str) -> list[dict]:
    """
    Filtre les articles par terme de recherche.
    
    Args:
        articles: Liste des articles
        terme: Terme de recherche
        
    Returns:
        Liste filtrée (correspondance insensible à la casse)
    """
    if not terme:
        return articles
    
    terme_lower = terme.lower()
    return [
        a for a in articles 
        if terme_lower in a.get("ingredient_nom", "").lower()
        or terme_lower in a.get("notes", "").lower()
    ]


def filtrer_articles(
    articles: list[dict],
    priorite: Optional[str] = None,
    rayon: Optional[str] = None,
    recherche: Optional[str] = None
) -> list[dict]:
    """
    Applique plusieurs filtres aux articles.
    
    Args:
        articles: Liste des articles
        priorite: Filtre par priorité
        rayon: Filtre par rayon
        recherche: Terme de recherche
        
    Returns:
        Liste filtrée
    """
    result = articles.copy()
    
    if priorite:
        result = filtrer_par_priorite(result, priorite)
    if rayon:
        result = filtrer_par_rayon(result, rayon)
    if recherche:
        result = filtrer_par_recherche(result, recherche)
    
    return result


# ═══════════════════════════════════════════════════════════════════════════
# FONCTIONS DE TRI
# ═══════════════════════════════════════════════════════════════════════════

def trier_par_priorite(articles: list[dict], reverse: bool = False) -> list[dict]:
    """
    Trie les articles par priorité (haute -> moyenne -> basse).
    
    Args:
        articles: Liste des articles
        reverse: Si True, inverse l'ordre
        
    Returns:
        Liste triée
    """
    return sorted(
        articles,
        key=lambda a: PRIORITY_ORDER.get(a.get("priorite", "moyenne"), 99),
        reverse=reverse
    )


def trier_par_rayon(articles: list[dict]) -> list[dict]:
    """
    Trie les articles par rayon de magasin (alphabétique).
    
    Args:
        articles: Liste des articles
        
    Returns:
        Liste triée
    """
    return sorted(articles, key=lambda a: a.get("rayon_magasin", "Autre"))


def trier_par_nom(articles: list[dict]) -> list[dict]:
    """
    Trie les articles par nom d'ingrédient (alphabétique).
    
    Args:
        articles: Liste des articles
        
    Returns:
        Liste triée
    """
    return sorted(articles, key=lambda a: a.get("ingredient_nom", "").lower())


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FONCTIONS DE GROUPEMENT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def grouper_par_rayon(articles: list[dict]) -> dict[str, list[dict]]:
    """
    Groupe les articles par rayon de magasin.
    
    Args:
        articles: Liste des articles
        
    Returns:
        Dictionnaire {rayon: [articles]}
    """
    rayons = {}
    for article in articles:
        rayon = article.get("rayon_magasin", "Autre")
        if rayon not in rayons:
            rayons[rayon] = []
        rayons[rayon].append(article)
    
    return rayons


def grouper_par_priorite(articles: list[dict]) -> dict[str, list[dict]]:
    """
    Groupe les articles par priorité.
    
    Args:
        articles: Liste des articles
        
    Returns:
        Dictionnaire {priorite: [articles]}
    """
    groupes = {"haute": [], "moyenne": [], "basse": []}
    
    for article in articles:
        priorite = article.get("priorite", "moyenne")
        if priorite in groupes:
            groupes[priorite].append(article)
        else:
            groupes["moyenne"].append(article)
    
    return groupes


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CALCUL DES STATISTIQUES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def calculer_statistiques(articles: list[dict], articles_achetes: list[dict] = None) -> dict:
    """
    Calcule les statistiques de la liste de courses.
    
    Args:
        articles: Liste des articles à acheter
        articles_achetes: Liste des articles achetés (optionnel)
        
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
    
    # Calcul du taux de complétion
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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# VALIDATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def valider_article(article: dict) -> tuple[bool, list[str]]:
    """
    Valide les données d'un article de courses.
    
    Args:
        article: Dictionnaire des données de l'article
        
    Returns:
        Tuple (est_valide, liste_erreurs)
    """
    erreurs = []
    
    # Nom requis
    if not article.get("ingredient_nom"):
        erreurs.append("Le nom de l'ingrédient est requis")
    elif len(article["ingredient_nom"]) < 2:
        erreurs.append("Le nom doit contenir au moins 2 caractères")
    
    # Quantité positive
    quantite = article.get("quantite_necessaire", 0)
    if quantite is not None and quantite <= 0:
        erreurs.append("La quantité doit être positive")
    
    # Priorité valide
    priorite = article.get("priorite")
    if priorite and priorite not in PRIORITY_ORDER:
        erreurs.append(f"Priorité invalide: {priorite}")
    
    # Rayon valide (si fourni)
    rayon = article.get("rayon_magasin")
    if rayon and rayon not in RAYONS_DEFAULT:
        # On accepte quand même, mais on log un warning
        logger.warning(f"Rayon non standard: {rayon}")
    
    return len(erreurs) == 0, erreurs


def valider_nouvel_article(
    nom: str,
    quantite: float,
    unite: str,
    priorite: str = "moyenne",
    rayon: str = "Autre"
) -> tuple[bool, dict | list[str]]:
    """
    Valide et prépare les données d'un nouvel article.
    
    Args:
        nom: Nom de l'ingrédient
        quantite: Quantité nécessaire
        unite: Unité de mesure
        priorite: Priorité (haute, moyenne, basse)
        rayon: Rayon du magasin
        
    Returns:
        Tuple (est_valide, article_ou_erreurs)
    """
    article = {
        "ingredient_nom": nom.strip() if nom else "",
        "quantite_necessaire": quantite,
        "unite": unite,
        "priorite": priorite,
        "rayon_magasin": rayon,
        "achete": False,
        "date_ajout": datetime.now(),
    }
    
    est_valide, erreurs = valider_article(article)
    
    if est_valide:
        return True, article
    return False, erreurs


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FORMATAGE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def formater_article_label(article: dict) -> str:
    """
    Formate le label d'affichage d'un article.
    
    Args:
        article: Dictionnaire de l'article
        
    Returns:
        Label formaté
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
        Texte formaté pour impression
    """
    lignes = ["=" * 40, "LISTE DE COURSES", "=" * 40, ""]
    
    rayons = grouper_par_rayon(articles)
    
    for rayon in sorted(rayons.keys()):
        lignes.append(f"\n[PKG] {rayon.upper()}")
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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# GÉNÉRATION DE SUGGESTIONS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def generer_suggestions_depuis_stock_bas(alertes: dict) -> list[dict]:
    """
    Génère des suggestions d'articles depuis les alertes de stock.
    
    Args:
        alertes: Dictionnaire des alertes de l'inventaire
        
    Returns:
        Liste de suggestions d'articles
    """
    suggestions = []
    
    # Stock critique = haute priorité
    for item in alertes.get("critique", []):
        suggestions.append({
            "ingredient_nom": item.get("ingredient_nom"),
            "quantite_necessaire": item.get("seuil_alerte", 1) - item.get("quantite", 0),
            "unite": item.get("unite", ""),
            "priorite": "haute",
            "rayon_magasin": item.get("rayon", "Autre"),
            "source": "stock_critique",
            "suggere_par_ia": False,
        })
    
    # Stock bas = moyenne priorité
    for item in alertes.get("stock_bas", []):
        suggestions.append({
            "ingredient_nom": item.get("ingredient_nom"),
            "quantite_necessaire": item.get("seuil_alerte", 1) - item.get("quantite", 0),
            "unite": item.get("unite", ""),
            "priorite": "moyenne",
            "rayon_magasin": item.get("rayon", "Autre"),
            "source": "stock_bas",
            "suggere_par_ia": False,
        })
    
    return suggestions


def generer_suggestions_depuis_recettes(
    recettes_selectionnees: list[dict],
    inventaire: list[dict]
) -> list[dict]:
    """
    Génère des suggestions d'articles depuis les recettes sélectionnées.
    
    Args:
        recettes_selectionnees: Liste des recettes à préparer
        inventaire: Liste de l'inventaire actuel
        
    Returns:
        Liste de suggestions d'articles
    """
    suggestions = []
    
    # Créer un index de l'inventaire par nom d'ingrédient
    stock_index = {
        item.get("ingredient_nom", "").lower(): item
        for item in inventaire
    }
    
    for recette in recettes_selectionnees:
        for ingredient in recette.get("ingredients", []):
            nom = ingredient.get("nom", "").lower()
            quantite_requise = ingredient.get("quantite", 0)
            
            # Vérifier le stock
            stock = stock_index.get(nom, {})
            quantite_en_stock = stock.get("quantite", 0)
            
            if quantite_requise > quantite_en_stock:
                manquant = quantite_requise - quantite_en_stock
                
                suggestions.append({
                    "ingredient_nom": ingredient.get("nom"),
                    "quantite_necessaire": manquant,
                    "unite": ingredient.get("unite", ""),
                    "priorite": "moyenne",
                    "rayon_magasin": ingredient.get("categorie", "Autre"),
                    "source": f"recette:{recette.get('nom')}",
                    "suggere_par_ia": True,
                })
    
    return suggestions


def deduper_suggestions(suggestions: list[dict]) -> list[dict]:
    """
    Déduplique les suggestions en gardant la plus haute priorité et cumulant les quantités.
    
    Args:
        suggestions: Liste des suggestions
        
    Returns:
        Liste dédupliquée avec quantités cumulées
    """
    index = {}
    
    for suggestion in suggestions:
        nom = suggestion.get("ingredient_nom", "").lower()
        
        if nom in index:
            existing = index[nom]
            # Toujours cumuler les quantités
            existing["quantite_necessaire"] += suggestion.get("quantite_necessaire", 0)
            # Garder la plus haute priorité
            if PRIORITY_ORDER.get(suggestion.get("priorite"), 99) < PRIORITY_ORDER.get(existing.get("priorite"), 99):
                existing["priorite"] = suggestion["priorite"]
        else:
            index[nom] = suggestion.copy()
    
    return list(index.values())


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# HISTORIQUE ET MODÃˆLES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def analyser_historique(historique: list[dict], jours: int = 30) -> dict:
    """
    Analyse l'historique d'achats pour détecter les patterns.
    
    Args:
        historique: Liste des achats passés
        jours: Nombre de jours à analyser
        
    Returns:
        Dictionnaire d'analyse
    """
    date_limite = datetime.now() - timedelta(days=jours)
    
    # Filtrer par date
    achats_recents = [
        a for a in historique
        if a.get("achete_le") and a["achete_le"] >= date_limite
    ]
    
    # Compter les fréquences
    frequences = {}
    for achat in achats_recents:
        nom = achat.get("ingredient_nom", "").lower()
        if nom not in frequences:
            frequences[nom] = {"count": 0, "quantites": [], "rayons": set()}
        frequences[nom]["count"] += 1
        frequences[nom]["quantites"].append(achat.get("quantite_necessaire", 0))
        frequences[nom]["rayons"].add(achat.get("rayon_magasin", "Autre"))
    
    # Identifier les articles récurrents (achetés plus de 2 fois)
    recurrents = [
        {
            "ingredient_nom": nom,
            "frequence": data["count"],
            "quantite_moyenne": sum(data["quantites"]) / len(data["quantites"]) if data["quantites"] else 0,
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
    Génère un modèle de liste à partir de l'analyse d'historique.
    
    Args:
        analyse: Résultat de analyser_historique()
        seuil_frequence: Fréquence minimum pour inclusion
        
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
