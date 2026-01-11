"""
Helpers - Gestion ingrédients et métier cuisine
Fonctions spécifiques au domaine alimentaire
"""
import logging
from typing import List, Dict, Optional, Tuple, Any
from sqlalchemy.orm import Session

from src.core.database import get_db_context
from src.core.models import Ingredient
from src.core.cache import Cache, cached

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# GESTION INGRÉDIENTS
# ═══════════════════════════════════════════════════════════

def find_or_create_ingredient(
        nom: str,
        unite: str,
        categorie: Optional[str] = None,
        db: Session = None
) -> int:
    """
    Trouve ou crée un ingrédient

    Args:
        nom: Nom ingrédient
        unite: Unité (kg, L, pcs, etc.)
        categorie: Catégorie (optionnel)
        db: Session DB (optionnel)

    Returns:
        ID de l'ingrédient

    Example:
        ingredient_id = find_or_create_ingredient("Tomate", "kg", "Fruits & Légumes")
    """
    def _execute(session: Session) -> int:
        ingredient = session.query(Ingredient).filter(Ingredient.nom == nom).first()
        if not ingredient:
            ingredient = Ingredient(nom=nom, unite=unite, categorie=categorie)
            session.add(ingredient)
            session.flush()
            logger.debug(f"Ingrédient créé: {nom}")
        return ingredient.id

    if db:
        return _execute(db)

    with get_db_context() as db:
        return _execute(db)


def batch_find_or_create_ingredients(
        items: List[Dict],
        db: Session = None
) -> Dict[str, int]:
    """
    Batch création ingrédients (optimisé)

    Args:
        items: Liste [{"nom": "...", "unite": "...", "categorie": "..."}]
        db: Session DB (optionnel)

    Returns:
        Dict {nom: ingredient_id}

    Example:
        items = [
            {"nom": "Tomate", "unite": "kg", "categorie": "Fruits & Légumes"},
            {"nom": "Oignon", "unite": "kg", "categorie": "Fruits & Légumes"}
        ]
        mapping = batch_find_or_create_ingredients(items)
    """
    def _execute(session: Session) -> Dict[str, int]:
        result = {}
        noms = [item["nom"] for item in items]

        # Charger existants
        existants = session.query(Ingredient).filter(Ingredient.nom.in_(noms)).all()

        for ing in existants:
            result[ing.nom] = ing.id

        # Créer manquants
        for item in items:
            if item["nom"] not in result:
                ingredient = Ingredient(
                    nom=item["nom"],
                    unite=item["unite"],
                    categorie=item.get("categorie")
                )
                session.add(ingredient)
                session.flush()
                result[item["nom"]] = ingredient.id

        return result

    if db:
        return _execute(db)

    with get_db_context() as db:
        return _execute(db)


@cached(ttl=300, cle="ingredients_all")
def get_all_ingredients_cached() -> List[Dict]:
    """
    Cache des ingrédients

    Returns:
        Liste [{"id": ..., "nom": "...", "unite": "...", "categorie": "..."}]

    Example:
        ingredients = get_all_ingredients_cached()
    """
    with get_db_context() as db:
        ingredients = db.query(Ingredient).all()
        return [
            {
                "id": ing.id,
                "nom": ing.nom,
                "unite": ing.unite,
                "categorie": ing.categorie
            }
            for ing in ingredients
        ]


def enrich_with_ingredient_info(
        items: List[Any],
        ingredient_id_field: str = "ingredient_id",
        db: Session = None
) -> List[Dict]:
    """
    Enrichit items avec infos ingrédient (évite N+1 queries)

    Args:
        items: Liste items ORM
        ingredient_id_field: Nom champ ID ingrédient
        db: Session DB (optionnel)

    Returns:
        Liste dicts enrichis

    Example:
        articles = session.query(ArticleInventaire).all()
        enriched = enrich_with_ingredient_info(articles)
    """
    def _execute(session: Session) -> List[Dict]:
        result = []
        ingredient_ids = [getattr(item, ingredient_id_field) for item in items]

        # Charger tous les ingrédients en 1 query
        ingredients = session.query(Ingredient).filter(
            Ingredient.id.in_(ingredient_ids)
        ).all()
        ing_map = {ing.id: ing for ing in ingredients}

        for item in items:
            ing_id = getattr(item, ingredient_id_field)
            ingredient = ing_map.get(ing_id)
            if not ingredient:
                continue

            enriched = {
                "id": item.id,
                "nom": ingredient.nom,
                "categorie": ingredient.categorie or "Autre",
                "unite": ingredient.unite,
            }

            # Copier autres attributs
            for attr in ["quantite", "priorite", "achete", "notes", "seuil",
                         "emplacement", "date_peremption"]:
                if hasattr(item, attr):
                    enriched[attr] = getattr(item, attr)

            result.append(enriched)

        return result

    if db:
        return _execute(db)

    with get_db_context() as db:
        return _execute(db)


# ═══════════════════════════════════════════════════════════
# VALIDATION MÉTIER
# ═══════════════════════════════════════════════════════════

def validate_stock_level(
        quantite: float,
        seuil: float,
        nom: str
) -> Tuple[str, str]:
    """
    Valide niveau de stock

    Args:
        quantite: Quantité actuelle
        seuil: Seuil minimum
        nom: Nom article

    Returns:
        (statut, icone)
        statut: "critique", "sous_seuil", "ok"
        icone: "🔴", "⚠️", "✅"

    Example:
        statut, icon = validate_stock_level(2.0, 5.0, "Tomates")
        # ("sous_seuil", "⚠️")
    """
    if quantite < seuil * 0.5:
        return "critique", "🔴"
    elif quantite < seuil:
        return "sous_seuil", "⚠️"
    else:
        return "ok", "✅"


def consolidate_duplicates(
        items: List[Dict],
        key_field: str,
        merge_strategy: Optional[callable] = None
) -> List[Dict]:
    """
    Consolide doublons dans liste

    Args:
        items: Liste items
        key_field: Champ clé pour détecter doublons
        merge_strategy: Fonction (item1, item2) -> merged_item

    Returns:
        Liste sans doublons

    Example:
        items = [
            {"nom": "tomate", "qty": 2},
            {"nom": "Tomate", "qty": 3}
        ]
        merged = consolidate_duplicates(items, "nom")
    """
    consolidation = {}

    for item in items:
        key = item.get(key_field)
        if not key:
            continue
        key_lower = str(key).lower().strip()

        if key_lower in consolidation:
            if merge_strategy:
                consolidation[key_lower] = merge_strategy(consolidation[key_lower], item)
        else:
            consolidation[key_lower] = item

    return list(consolidation.values())


# ═══════════════════════════════════════════════════════════
# FORMATAGE MÉTIER
# ═══════════════════════════════════════════════════════════

def format_recipe_summary(recette: Dict) -> str:
    """
    Formatte résumé recette

    Args:
        recette: Dict recette

    Returns:
        String résumé

    Example:
        summary = format_recipe_summary({
            "nom": "Tarte aux pommes",
            "temps_preparation": 30,
            "temps_cuisson": 45,
            "portions": 6,
            "difficulte": "moyen"
        })
        # "Tarte aux pommes - 75min - 6 portions - Moyen"
    """
    temps = recette.get("temps_preparation", 0) + recette.get("temps_cuisson", 0)
    parts = [
        recette.get("nom", "Sans nom"),
        f"{temps}min",
        f"{recette.get('portions', 4)} portions",
        recette.get("difficulte", "moyen").capitalize()
    ]
    return " - ".join(parts)


def format_inventory_summary(inventaire: List[Dict]) -> str:
    """
    Formatte résumé inventaire

    Args:
        inventaire: Liste articles

    Returns:
        String résumé

    Example:
        summary = format_inventory_summary(articles)
        # "42 articles | 5 stock bas | 3 péremption proche"
    """
    total = len(inventaire)
    stock_bas = len([i for i in inventaire if i.get("statut") in ["sous_seuil", "critique"]])
    peremption = len([i for i in inventaire if i.get("statut") == "peremption_proche"])

    return f"{total} articles | {stock_bas} stock bas | {peremption} péremption proche"


def calculate_recipe_cost(recette: Dict, prix_ingredients: Dict[str, float]) -> float:
    """
    Calcule coût recette

    Args:
        recette: Dict recette avec ingredients
        prix_ingredients: Dict {nom_ingredient: prix_unitaire}

    Returns:
        Coût total

    Example:
        recette = {
            "ingredients": [
                {"nom": "Tomate", "quantite": 0.5},
                {"nom": "Oignon", "quantite": 0.2}
            ]
        }
        prix = {"Tomate": 3.0, "Oignon": 2.0}
        cost = calculate_recipe_cost(recette, prix)
    """
    total = 0.0

    for ing in recette.get("ingredients", []):
        nom = ing["nom"]
        quantite = ing["quantite"]
        prix_unitaire = prix_ingredients.get(nom, 0.0)
        total += quantite * prix_unitaire

    return total


def suggest_ingredient_substitutes(ingredient: str) -> List[str]:
    """
    Suggère substituts pour un ingrédient

    Args:
        ingredient: Nom ingrédient

    Returns:
        Liste substituts possibles

    Example:
        substitutes = suggest_ingredient_substitutes("Beurre")
        # ["Margarine", "Huile d'olive", "Compote de pommes"]
    """
    # Mapping simple (peut être enrichi)
    substitutes_map = {
        "beurre": ["margarine", "huile d'olive", "compote de pommes"],
        "lait": ["lait d'amande", "lait de soja", "crème"],
        "oeuf": ["compote de pommes", "graines de chia", "banane écrasée"],
        "sucre": ["miel", "sirop d'érable", "stévia"],
        "farine": ["farine de riz", "farine d'amande", "fécule de maïs"]
    }

    return substitutes_map.get(ingredient.lower(), [])