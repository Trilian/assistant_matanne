"""
Logique métier du module Shopping (famille) - Séparée de l'UI
Ce module contient toute la logique pure, testable sans Streamlit
"""

from datetime import date, timedelta
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CONSTANTES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

CATEGORIES_SHOPPING = ["Vêtements", "Chaussures", "Jouets", "Livres", "Ã‰lectronique", "Maison", "Puériculture", "Autre"]
LISTES = ["Jules", "Nous", "Maison"]
PRIORITES = ["Haute", "Moyenne", "Basse"]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CALCULS FINANCIERS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def calculer_cout_liste(articles: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calcule le coût d'une liste de shopping."""
    cout_estime = 0.0
    cout_reel = 0.0
    
    for art in articles:
        qty = art.get("quantite", 1)
        prix_est = art.get("prix_estime", 0.0)
        prix_reel = art.get("prix_reel")
        
        cout_estime += qty * prix_est
        if prix_reel is not None:
            cout_reel += qty * prix_reel
    
    economie = None
    if cout_reel > 0:
        economie = cout_estime - cout_reel
    
    return {
        "estime": cout_estime,
        "reel": cout_reel if cout_reel > 0 else None,
        "economie": economie
    }


def calculer_budget_mensuel(articles: List[Dict[str, Any]], mois: int = 1) -> Dict[str, Any]:
    """Calcule le budget mensuel moyen."""
    if not articles or mois == 0:
        return {
            "total": 0.0,
            "par_mois": 0.0,
            "par_categorie": {}
        }
    
    # Total
    couts = calculer_cout_liste(articles)
    total = couts["reel"] if couts["reel"] else couts["estime"]
    
    # Par catégorie
    par_categorie = {}
    for art in articles:
        cat = art.get("categorie", "Autre")
        qty = art.get("quantite", 1)
        prix = art.get("prix_reel") or art.get("prix_estime", 0.0)
        
        if cat not in par_categorie:
            par_categorie[cat] = 0.0
        par_categorie[cat] += qty * prix
    
    return {
        "total": total,
        "par_mois": total / mois,
        "par_categorie": par_categorie
    }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FILTRAGE ET TRI
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def filtrer_par_liste(articles: List[Dict[str, Any]], liste: str) -> List[Dict[str, Any]]:
    """Filtre les articles par liste."""
    return [a for a in articles if a.get("liste") == liste]


def filtrer_par_categorie(articles: List[Dict[str, Any]], categorie: str) -> List[Dict[str, Any]]:
    """Filtre les articles par catégorie."""
    return [a for a in articles if a.get("categorie") == categorie]


def filtrer_par_priorite(articles: List[Dict[str, Any]], priorite: str) -> List[Dict[str, Any]]:
    """Filtre les articles par priorité."""
    return [a for a in articles if a.get("priorite") == priorite]


def get_articles_non_achetes(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Retourne les articles non achetés."""
    return [a for a in articles if not a.get("achete", False)]


def get_articles_achetes(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Retourne les articles achetés."""
    return [a for a in articles if a.get("achete", False)]


def trier_par_priorite(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Trie les articles par priorité."""
    ordre_priorite = {"Haute": 0, "Moyenne": 1, "Basse": 2}
    return sorted(articles, key=lambda x: ordre_priorite.get(x.get("priorite", "Moyenne"), 1))


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# STATISTIQUES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def calculer_statistiques_shopping(articles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calcule les statistiques shopping."""
    total = len(articles)
    
    if total == 0:
        return {
            "total": 0,
            "achetes": 0,
            "non_achetes": 0,
            "taux_completion": 0.0,
            "par_categorie": {},
            "par_liste": {},
            "couts": {"estime": 0.0, "reel": None, "economie": None}
        }
    
    achetes = len(get_articles_achetes(articles))
    non_achetes = len(get_articles_non_achetes(articles))
    
    # Par catégorie
    par_categorie = {}
    for art in articles:
        cat = art.get("categorie", "Autre")
        par_categorie[cat] = par_categorie.get(cat, 0) + 1
    
    # Par liste
    par_liste = {}
    for art in articles:
        liste = art.get("liste", "Autre")
        par_liste[liste] = par_liste.get(liste, 0) + 1
    
    # Coûts
    couts = calculer_cout_liste(articles)
    
    return {
        "total": total,
        "achetes": achetes,
        "non_achetes": non_achetes,
        "taux_completion": (achetes / total * 100) if total > 0 else 0.0,
        "par_categorie": par_categorie,
        "par_liste": par_liste,
        "couts": couts
    }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SUGGESTIONS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def suggerer_budget_optimal(historique: List[Dict[str, Any]], mois: int = 3) -> Dict[str, float]:
    """Suggère un budget optimal basé sur l'historique."""
    if not historique:
        return {
            "mensuel_suggere": 0.0,
            "par_categorie": {}
        }
    
    budget = calculer_budget_mensuel(historique, mois)
    
    # Ajouter marge de 10%
    mensuel_suggere = budget["par_mois"] * 1.1
    
    # Par catégorie avec marge
    par_categorie = {}
    for cat, montant in budget["par_categorie"].items():
        par_categorie[cat] = (montant / mois) * 1.1
    
    return {
        "mensuel_suggere": mensuel_suggere,
        "par_categorie": par_categorie
    }


def detecter_articles_recurrents(historique: List[Dict[str, Any]], seuil: int = 3) -> List[str]:
    """Détecte les articles achetés récurremment."""
    from collections import Counter
    
    titres = [a.get("titre", "").lower() for a in historique if a.get("achete")]
    compteur = Counter(titres)
    
    return [titre for titre, count in compteur.items() if count >= seuil]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# VALIDATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def valider_article_shopping(data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """Valide un article shopping."""
    erreurs = []
    
    if "titre" not in data or not data["titre"]:
        erreurs.append("Le titre est requis")
    
    if "categorie" in data and data["categorie"] not in CATEGORIES_SHOPPING:
        erreurs.append(f"Catégorie invalide. Valeurs: {', '.join(CATEGORIES_SHOPPING)}")
    
    if "liste" in data and data["liste"] not in LISTES:
        erreurs.append(f"Liste invalide. Valeurs: {', '.join(LISTES)}")
    
    if "quantite" in data:
        qty = data["quantite"]
        if not isinstance(qty, int) or qty < 1:
            erreurs.append("La quantité doit être >= 1")
    
    if "prix_estime" in data:
        prix = data["prix_estime"]
        if not isinstance(prix, (int, float)) or prix < 0:
            erreurs.append("Le prix estimé doit être >= 0")
    
    return len(erreurs) == 0, erreurs


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FORMATAGE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def formater_article_label(article: Dict[str, Any]) -> str:
    """Formate le label d'un article."""
    titre = article.get("titre", "Article")
    qty = article.get("quantite", 1)
    prix = article.get("prix_estime", 0.0)
    
    if qty > 1:
        return f"{titre} (x{qty}) - {prix * qty:.2f}â‚¬"
    else:
        return f"{titre} - {prix:.2f}â‚¬"


def grouper_par_magasin(articles: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Groupe les articles par magasin."""
    groupes = {}
    
    for art in articles:
        magasin = art.get("magasin", "Non défini")
        if magasin not in groupes:
            groupes[magasin] = []
        groupes[magasin].append(art)
    
    return groupes

