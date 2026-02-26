"""
Operations sur les articles de courses - Filtrage, tri, groupement, validation

Logique pure, testable sans Streamlit.
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════════════════════════════

PRIORITY_EMOJIS = {"haute": "🔴", "moyenne": "🟡", "basse": "🟢"}

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
    "Autre",
]


# ═══════════════════════════════════════════════════════════════════════════════════
# FONCTIONS DE FILTRAGE
# ═══════════════════════════════════════════════════════════════════════════════════


def filtrer_par_priorite(articles: list[dict], priorite: str) -> list[dict]:
    """
    Filtre les articles par priorite.

    Args:
        articles: Liste des articles
        priorite: 'haute', 'moyenne', 'basse' ou None pour tout garder

    Returns:
        Liste filtree
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
        Liste filtree
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
        Liste filtree (correspondance insensible à la casse)
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


def filtrer_articles(
    articles: list[dict],
    priorite: str | None = None,
    rayon: str | None = None,
    recherche: str | None = None,
) -> list[dict]:
    """
    Applique plusieurs filtres aux articles.

    Args:
        articles: Liste des articles
        priorite: Filtre par priorite
        rayon: Filtre par rayon
        recherche: Terme de recherche

    Returns:
        Liste filtree
    """
    result = articles.copy()

    if priorite:
        result = filtrer_par_priorite(result, priorite)
    if rayon:
        result = filtrer_par_rayon(result, rayon)
    if recherche:
        result = filtrer_par_recherche(result, recherche)

    return result


# ═══════════════════════════════════════════════════════════
# FONCTIONS DE TRI
# ═══════════════════════════════════════════════════════════


def trier_par_priorite(articles: list[dict], reverse: bool = False) -> list[dict]:
    """
    Trie les articles par priorite (haute -> moyenne -> basse).

    Args:
        articles: Liste des articles
        reverse: Si True, inverse l'ordre

    Returns:
        Liste triee
    """
    return sorted(
        articles,
        key=lambda a: PRIORITY_ORDER.get(a.get("priorite", "moyenne"), 99),
        reverse=reverse,
    )


def trier_par_rayon(articles: list[dict]) -> list[dict]:
    """
    Trie les articles par rayon de magasin (alphabetique).

    Args:
        articles: Liste des articles

    Returns:
        Liste triee
    """
    return sorted(articles, key=lambda a: a.get("rayon_magasin", "Autre"))


def trier_par_nom(articles: list[dict]) -> list[dict]:
    """
    Trie les articles par nom d'ingredient (alphabetique).

    Args:
        articles: Liste des articles

    Returns:
        Liste triee
    """
    return sorted(articles, key=lambda a: a.get("ingredient_nom", "").lower())


# ═══════════════════════════════════════════════════════════
# FONCTIONS DE GROUPEMENT
# ═══════════════════════════════════════════════════════════


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
    Groupe les articles par priorite.

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


# ═══════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════


def valider_article(article: dict) -> tuple[bool, list[str]]:
    """
    Valide les donnees d'un article de courses.

    Args:
        article: Dictionnaire des donnees de l'article

    Returns:
        Tuple (est_valide, liste_erreurs)
    """
    erreurs = []

    # Nom requis
    if not article.get("ingredient_nom"):
        erreurs.append("Le nom de l'ingredient est requis")
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
    nom: str, quantite: float, unite: str, priorite: str = "moyenne", rayon: str = "Autre"
) -> tuple[bool, dict | list[str]]:
    """
    Valide et prepare les donnees d'un nouvel article.

    Args:
        nom: Nom de l'ingredient
        quantite: Quantite necessaire
        unite: Unite de mesure
        priorite: Priorite (haute, moyenne, basse)
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


# ═══════════════════════════════════════════════════════════
# UTILITAIRES
# ═══════════════════════════════════════════════════════════


def get_current_user_id() -> str | None:
    """Retourne l'ID de l'utilisateur courant ou None si non authentifié."""
    try:
        from src.services.core.utilisateur import get_auth_service

        auth = get_auth_service()
        user = auth.get_current_user()
        return user.id if user else None
    except Exception:
        return None
