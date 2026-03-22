"""
Logique métier du module Courses — Filtrage, tri, groupement, formatage, validation.

Logique pure, testable sans Streamlit.
Consolide les anciens utils_operations.py, utils_formatage.py et liste_utils.py.
"""

import logging
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

PRIORITY_EMOJIS: dict[str, str] = {"haute": "🔴", "moyenne": "🟡", "basse": "🟢"}

PRIORITY_ORDER: dict[str, int] = {"haute": 0, "moyenne": 1, "basse": 2}

RAYONS_DEFAULT: list[str] = [
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

DEFAULT_RAYON_VERS_MAGASIN: dict[str, str] = {
    "Fruits & Légumes": "Marché / Primeur",
    "Boulangerie": "Boulangerie",
    "Boucherie": "Boucher / Poissonnier",
    "Charcuterie": "Boucher / Poissonnier",
    "Poissonnerie": "Boucher / Poissonnier",
    "Crèmerie": "Supermarché",
    "Fromage": "Supermarché",
    "Épicerie": "Supermarché",
    "Surgelés": "Supermarché",
    "Boissons": "Supermarché",
}


# ═══════════════════════════════════════════════════════════
# FILTRAGE
# ═══════════════════════════════════════════════════════════


def filtrer_liste(
    liste: list[dict[str, Any]],
    priorite: str | None = None,
    rayon: str | None = None,
    search_term: str | None = None,
) -> list[dict[str, Any]]:
    """Filtre la liste de courses selon les critères spécifiés."""
    liste_filtree = liste.copy()

    if priorite:
        liste_filtree = [a for a in liste_filtree if a.get("priorite") == priorite]

    if rayon:
        liste_filtree = [a for a in liste_filtree if a.get("rayon_magasin") == rayon]

    if search_term:
        term_lower = search_term.lower()
        liste_filtree = [
            a
            for a in liste_filtree
            if term_lower in a.get("ingredient_nom", "").lower()
            or term_lower in a.get("notes", "").lower()
        ]

    return liste_filtree


def filtrer_par_priorite(articles: list[dict], priorite: str) -> list[dict]:
    """Filtre les articles par priorité."""
    if not priorite or priorite.lower() == "toutes":
        return articles
    return [a for a in articles if a.get("priorite") == priorite]


def filtrer_par_rayon(articles: list[dict], rayon: str) -> list[dict]:
    """Filtre les articles par rayon de magasin."""
    if not rayon or rayon.lower() == "tous les rayons":
        return articles
    return [a for a in articles if a.get("rayon_magasin") == rayon]


def filtrer_par_recherche(articles: list[dict], terme: str) -> list[dict]:
    """Filtre les articles par terme de recherche."""
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
    """Applique plusieurs filtres aux articles."""
    result = articles.copy()
    if priorite:
        result = filtrer_par_priorite(result, priorite)
    if rayon:
        result = filtrer_par_rayon(result, rayon)
    if recherche:
        result = filtrer_par_recherche(result, recherche)
    return result


# ═══════════════════════════════════════════════════════════
# TRI
# ═══════════════════════════════════════════════════════════


def trier_par_priorite(articles: list[dict], reverse: bool = False) -> list[dict]:
    """Trie les articles par priorité (haute → moyenne → basse)."""
    return sorted(
        articles,
        key=lambda a: PRIORITY_ORDER.get(a.get("priorite", "moyenne"), 99),
        reverse=reverse,
    )


def trier_par_rayon(articles: list[dict]) -> list[dict]:
    """Trie les articles par rayon de magasin (alphabétique)."""
    return sorted(articles, key=lambda a: a.get("rayon_magasin", "Autre"))


def trier_par_nom(articles: list[dict]) -> list[dict]:
    """Trie les articles par nom d'ingrédient (alphabétique)."""
    return sorted(articles, key=lambda a: a.get("ingredient_nom", "").lower())


# ═══════════════════════════════════════════════════════════
# GROUPEMENT
# ═══════════════════════════════════════════════════════════


def grouper_par_rayon(liste: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Regroupe les articles par rayon."""
    rayons: dict[str, list[dict[str, Any]]] = {}
    for article in liste:
        rayon = article.get("rayon_magasin") or "Autre"
        if rayon not in rayons:
            rayons[rayon] = []
        rayons[rayon].append(article)
    return rayons


def grouper_par_priorite(articles: list[dict]) -> dict[str, list[dict]]:
    """Groupe les articles par priorité."""
    groupes: dict[str, list[dict]] = {"haute": [], "moyenne": [], "basse": []}
    for article in articles:
        priorite = article.get("priorite", "moyenne")
        if priorite in groupes:
            groupes[priorite].append(article)
        else:
            groupes["moyenne"].append(article)
    return groupes


def grouper_par_magasin(liste: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Regroupe les articles par type de magasin cible."""
    magasins: dict[str, list[dict[str, Any]]] = {}
    for article in liste:
        rayon = article.get("rayon_magasin") or "Autre"
        magasin = DEFAULT_RAYON_VERS_MAGASIN.get(rayon, "Autre magasin")
        if magasin not in magasins:
            magasins[magasin] = []
        magasins[magasin].append(article)
    return magasins


def grouper_par_magasin_personnalise(
    liste: list[dict[str, Any]], mapping_rayon_magasin: dict[str, str] | None = None
) -> dict[str, list[dict[str, Any]]]:
    """Regroupe les articles par magasin avec mapping personnalisable."""
    mapping = mapping_rayon_magasin or DEFAULT_RAYON_VERS_MAGASIN
    magasins: dict[str, list[dict[str, Any]]] = {}
    for article in liste:
        rayon = article.get("rayon_magasin") or "Autre"
        magasin = (mapping.get(rayon) or "Autre magasin").strip() or "Autre magasin"
        if magasin not in magasins:
            magasins[magasin] = []
        magasins[magasin].append(article)
    return magasins


def obtenir_mapping_magasins_par_defaut() -> dict[str, str]:
    """Retourne une copie du mapping rayon → magasin par défaut."""
    return DEFAULT_RAYON_VERS_MAGASIN.copy()


def extraire_rayons_uniques(liste: list[dict[str, Any]]) -> list[str]:
    """Extrait la liste des rayons uniques triés."""
    return sorted({a.get("rayon_magasin") or "Autre" for a in liste})


# ═══════════════════════════════════════════════════════════
# FORMATAGE
# ═══════════════════════════════════════════════════════════


def formater_article_label(
    article: dict[str, Any],
    priority_emojis: dict[str, str] | None = None,
    include_notes: bool = True,
    include_ia_marker: bool = True,
) -> str:
    """Formate le label d'affichage d'un article."""
    emojis = priority_emojis or PRIORITY_EMOJIS
    priorite_emoji = emojis.get(article.get("priorite", "moyenne"), "⚫")
    nom = article.get("ingredient_nom", "")
    quantite = article.get("quantite_necessaire", 0)
    unite = article.get("unite", "")

    quantite_fmt = int(quantite) if quantite == int(quantite) else round(quantite, 1)
    unite_affichage = unite.strip() if unite else ""
    unites_generiques = ("pcs", "piece", "pièce", "portion", "")

    if unite_affichage and unite_affichage.lower() not in unites_generiques:
        label = f"{priorite_emoji} {nom} ({quantite_fmt} {unite_affichage})"
    elif quantite and quantite > 1:
        label = f"{priorite_emoji} {nom} (×{quantite_fmt})"
    else:
        label = f"{priorite_emoji} {nom}"

    if include_notes and article.get("notes"):
        label += f" | 📝 {article.get('notes')}"

    if include_ia_marker and article.get("suggere_par_ia"):
        label += " ⏰"

    return label


def generer_texte_impression(
    liste: list[dict[str, Any]],
    titre: str = "LISTE DE COURSES",
    date_format: str = "%d/%m/%Y %H:%M",
    group_by: str = "rayon",
    mapping_rayon_magasin: dict[str, str] | None = None,
) -> str:
    """Génère le texte formaté pour l'impression de la liste."""
    if group_by == "magasin":
        groupes = grouper_par_magasin_personnalise(liste, mapping_rayon_magasin)
    elif group_by == "simple":
        groupes = {"Liste rapide": liste}
    else:
        groupes = grouper_par_rayon(liste)

    lignes = [
        f"📋 {titre}",
        f"📅 {datetime.now().strftime(date_format)}",
        "=" * 40,
        "",
    ]

    for groupe in sorted(groupes.keys()):
        lignes.append(f"🏪 {groupe}")
        for article in groupes[groupe]:
            quantite = article.get("quantite_necessaire", 1)
            unite = (article.get("unite") or "").strip()
            qty = f"{quantite} {unite}".strip()
            lignes.append(f"  ☐ {article.get('ingredient_nom')} ({qty})")
        lignes.append("")

    return "\n".join(lignes)


def formater_liste_impression(articles: list[dict]) -> str:
    """Formate la liste de courses pour impression (format legacy)."""
    lignes = ["=" * 40, "LISTE DE COURSES", "=" * 40, ""]

    rayons = grouper_par_rayon(articles)

    for rayon in sorted(rayons.keys()):
        lignes.append(f"\n📦 {rayon.upper()}")
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


# ═══════════════════════════════════════════════════════════
# STATISTIQUES
# ═══════════════════════════════════════════════════════════


def calculer_statistiques(articles: list[dict], articles_achetes: list[dict] | None = None) -> dict:
    """Calcule les statistiques de la liste de courses."""
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

    total = stats["total_a_acheter"] + stats["total_achetes"]
    stats["taux_completion"] = (stats["total_achetes"] / total * 100) if total > 0 else 0

    return stats


def calculer_statistiques_par_rayon(articles: list[dict]) -> dict[str, dict]:
    """Calcule les statistiques par rayon."""
    rayons = grouper_par_rayon(articles)

    stats = {}
    for rayon, articles_rayon in rayons.items():
        stats[rayon] = {
            "count": len(articles_rayon),
            "haute_priorite": len([a for a in articles_rayon if a.get("priorite") == "haute"]),
            "suggestions_ia": len([a for a in articles_rayon if a.get("suggere_par_ia")]),
        }

    return stats


def calculer_statistiques_liste(
    liste: list[dict[str, Any]],
    liste_achetee: list[dict[str, Any]] | None = None,
    alertes_stock: list[Any] | None = None,
) -> dict[str, int]:
    """Calcule les statistiques de la liste de courses (version compacte)."""
    return {
        "a_acheter": len(liste),
        "haute_priorite": len([a for a in liste if a.get("priorite") == "haute"]),
        "stock_bas": len(alertes_stock) if alertes_stock else 0,
        "total_achetes": len(liste_achetee) if liste_achetee else 0,
    }


# ═══════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════


def valider_article(article: dict) -> tuple[bool, list[str]]:
    """Valide les données d'un article de courses."""
    erreurs = []

    if not article.get("ingredient_nom"):
        erreurs.append("Le nom de l'ingredient est requis")
    elif len(article["ingredient_nom"]) < 2:
        erreurs.append("Le nom doit contenir au moins 2 caractères")

    quantite = article.get("quantite_necessaire", 0)
    if quantite is not None and quantite <= 0:
        erreurs.append("La quantité doit être positive")

    priorite = article.get("priorite")
    if priorite and priorite not in PRIORITY_ORDER:
        erreurs.append(f"Priorité invalide: {priorite}")

    rayon = article.get("rayon_magasin")
    if rayon and rayon not in RAYONS_DEFAULT:
        logger.warning(f"Rayon non standard: {rayon}")

    return len(erreurs) == 0, erreurs


def valider_nouvel_article(
    nom: str, quantite: float, unite: str, priorite: str = "moyenne", rayon: str = "Autre"
) -> tuple[bool, dict | list[str]]:
    """Valide et prépare les données d'un nouvel article."""
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


def valider_article_data(data: dict[str, Any]) -> tuple[bool, str]:
    """Valide les données d'un article avant création/modification."""
    if not data.get("ingredient_id"):
        return False, "ID d'ingrédient requis"

    quantite = data.get("quantite_necessaire", 0)
    if quantite <= 0:
        return False, "La quantité doit être positive"

    priorite = data.get("priorite", "")
    if priorite and priorite not in ("haute", "moyenne", "basse"):
        return False, "Priorité invalide (haute, moyenne, basse)"

    return True, ""


# ═══════════════════════════════════════════════════════════
# SUGGESTIONS
# ═══════════════════════════════════════════════════════════


def generer_suggestions_depuis_stock_bas(alertes: dict) -> list[dict]:
    """Génère des suggestions d'articles depuis les alertes de stock."""
    suggestions = []

    for item in alertes.get("critique", []):
        suggestions.append(
            {
                "ingredient_nom": item.get("ingredient_nom"),
                "quantite_necessaire": item.get("seuil_alerte", 1) - item.get("quantite", 0),
                "unite": item.get("unite", ""),
                "priorite": "haute",
                "rayon_magasin": item.get("rayon", "Autre"),
                "source": "stock_critique",
                "suggere_par_ia": False,
            }
        )

    for item in alertes.get("stock_bas", []):
        suggestions.append(
            {
                "ingredient_nom": item.get("ingredient_nom"),
                "quantite_necessaire": item.get("seuil_alerte", 1) - item.get("quantite", 0),
                "unite": item.get("unite", ""),
                "priorite": "moyenne",
                "rayon_magasin": item.get("rayon", "Autre"),
                "source": "stock_bas",
                "suggere_par_ia": False,
            }
        )

    return suggestions


def generer_suggestions_depuis_recettes(
    recettes_selectionnees: list[dict], inventaire: list[dict]
) -> list[dict]:
    """Génère des suggestions d'articles depuis les recettes sélectionnées."""
    suggestions = []
    stock_index = {item.get("ingredient_nom", "").lower(): item for item in inventaire}

    for recette in recettes_selectionnees:
        for ingredient in recette.get("ingredients", []):
            nom = ingredient.get("nom", "").lower()
            quantite_requise = ingredient.get("quantite", 0)
            stock = stock_index.get(nom, {})
            quantite_en_stock = stock.get("quantite", 0)

            if quantite_requise > quantite_en_stock:
                manquant = quantite_requise - quantite_en_stock
                suggestions.append(
                    {
                        "ingredient_nom": ingredient.get("nom"),
                        "quantite_necessaire": manquant,
                        "unite": ingredient.get("unite", ""),
                        "priorite": "moyenne",
                        "rayon_magasin": ingredient.get("categorie", "Autre"),
                        "source": f"recette:{recette.get('nom')}",
                        "suggere_par_ia": True,
                    }
                )

    return suggestions


def deduper_suggestions(suggestions: list[dict]) -> list[dict]:
    """Déduplique les suggestions en gardant la plus haute priorité et cumulant les quantités."""
    index: dict[str, dict] = {}

    for suggestion in suggestions:
        nom = suggestion.get("ingredient_nom", "").lower()

        if nom in index:
            existing = index[nom]
            existing["quantite_necessaire"] += suggestion.get("quantite_necessaire", 0)
            if PRIORITY_ORDER.get(suggestion.get("priorite"), 99) < PRIORITY_ORDER.get(
                existing.get("priorite"), 99
            ):
                existing["priorite"] = suggestion["priorite"]
        else:
            index[nom] = suggestion.copy()

    return list(index.values())


# ═══════════════════════════════════════════════════════════
# HISTORIQUE
# ═══════════════════════════════════════════════════════════


def analyser_historique(historique: list[dict], jours: int = 30) -> dict:
    """Analyse l'historique d'achats pour détecter les patterns."""
    date_limite = datetime.now() - timedelta(days=jours)

    achats_recents = [a for a in historique if a.get("achete_le") and a["achete_le"] >= date_limite]

    frequences: dict[str, dict] = {}
    for achat in achats_recents:
        nom = achat.get("ingredient_nom", "").lower()
        if nom not in frequences:
            frequences[nom] = {"count": 0, "quantites": [], "rayons": set()}
        frequences[nom]["count"] += 1
        frequences[nom]["quantites"].append(achat.get("quantite_necessaire", 0))
        frequences[nom]["rayons"].add(achat.get("rayon_magasin", "Autre"))

    recurrents = [
        {
            "ingredient_nom": nom,
            "frequence": data["count"],
            "quantite_moyenne": sum(data["quantites"]) / len(data["quantites"])
            if data["quantites"]
            else 0,
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
    """Génère un modèle de liste à partir de l'analyse d'historique."""
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


__all__ = [
    # Constantes
    "PRIORITY_EMOJIS",
    "PRIORITY_ORDER",
    "RAYONS_DEFAULT",
    "DEFAULT_RAYON_VERS_MAGASIN",
    # Filtrage
    "filtrer_liste",
    "filtrer_articles",
    "filtrer_par_priorite",
    "filtrer_par_rayon",
    "filtrer_par_recherche",
    # Tri
    "trier_par_nom",
    "trier_par_priorite",
    "trier_par_rayon",
    # Groupement
    "grouper_par_priorite",
    "grouper_par_rayon",
    "grouper_par_magasin",
    "grouper_par_magasin_personnalise",
    "obtenir_mapping_magasins_par_defaut",
    "extraire_rayons_uniques",
    # Formatage
    "formater_article_label",
    "formater_liste_impression",
    "generer_texte_impression",
    # Statistiques
    "calculer_statistiques",
    "calculer_statistiques_par_rayon",
    "calculer_statistiques_liste",
    # Validation
    "valider_article",
    "valider_nouvel_article",
    "valider_article_data",
    # Suggestions
    "generer_suggestions_depuis_stock_bas",
    "generer_suggestions_depuis_recettes",
    "deduper_suggestions",
    # Historique
    "analyser_historique",
    "generer_modele_depuis_historique",
    # Utilitaires
    "get_current_user_id",
]
