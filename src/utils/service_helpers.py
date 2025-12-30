"""
Service Helpers - Helpers métier pour services
Séparé des helpers génériques
"""
import logging
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from src.core.database import get_db_context
from src.core.models import Ingredient
from src.core.cache import Cache

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# GESTION INGRÉDIENTS (DRY)
# ═══════════════════════════════════════════════════════════

def find_or_create_ingredient(
        nom: str,
        unite: str,
        categorie: Optional[str] = None,
        db: Session = None
) -> int:
    """
    Trouve ou crée un ingrédient

    Utilisé par recettes/inventaire/courses pour éviter duplication

    Args:
        nom: Nom ingrédient
        unite: Unité
        categorie: Catégorie (optionnel)
        db: Session (optionnelle)

    Returns:
        ingredient_id

    Usage:
        ing_id = find_or_create_ingredient("Tomates", "kg", "Légumes")
    """
    def _execute(session: Session) -> int:
        # Chercher existant
        ingredient = session.query(Ingredient).filter(
            Ingredient.nom == nom
        ).first()

        if not ingredient:
            # Créer
            ingredient = Ingredient(
                nom=nom,
                unite=unite,
                categorie=categorie
            )
            session.add(ingredient)
            session.flush()

            logger.debug(f"Ingrédient créé: {nom}")

        return ingredient.id

    if db:
        return _execute(db)

    with get_db_context() as db:
        return _execute(db)


def batch_find_or_create_ingredients(
        items: List[Dict],  # [{"nom": str, "unite": str, "categorie": str}]
        db: Session = None
) -> Dict[str, int]:
    """
    Batch création ingrédients (optimisé)

    Args:
        items: Liste d'ingrédients à créer
        db: Session (optionnelle)

    Returns:
        {"nom": ingredient_id}

    Usage:
        ing_map = batch_find_or_create_ingredients([
            {"nom": "Tomates", "unite": "kg"},
            {"nom": "Oignons", "unite": "pcs"}
        ])
        # {"Tomates": 1, "Oignons": 2}
    """
    def _execute(session: Session) -> Dict[str, int]:
        result = {}

        # Chercher existants (1 query)
        noms = [item["nom"] for item in items]
        existants = session.query(Ingredient).filter(
            Ingredient.nom.in_(noms)
        ).all()

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

                logger.debug(f"Ingrédient créé: {item['nom']}")

        return result

    if db:
        return _execute(db)

    with get_db_context() as db:
        return _execute(db)


# ═══════════════════════════════════════════════════════════
# ENRICHISSEMENT (DRY)
# ═══════════════════════════════════════════════════════════

def enrich_with_ingredient_info(
        items: List[Any],
        ingredient_id_field: str = "ingredient_id",
        db: Session = None
) -> List[Dict]:
    """
    Enrichit items avec infos ingrédient

    Utilisé par inventaire/courses pour éviter N+1 queries

    Args:
        items: Liste d'items (modèles SQLAlchemy)
        ingredient_id_field: Nom du champ contenant l'ID ingrédient
        db: Session (optionnelle)

    Returns:
        Liste de dicts enrichis

    Usage:
        items = db.query(ArticleInventaire).all()
        enriched = enrich_with_ingredient_info(items)
        # [{"id": 1, "nom": "Tomates", "categorie": "Légumes", ...}]
    """
    def _execute(session: Session) -> List[Dict]:
        result = []

        # Récupérer tous les ingrédients (1 query)
        ingredient_ids = [getattr(item, ingredient_id_field) for item in items]
        ingredients = session.query(Ingredient).filter(
            Ingredient.id.in_(ingredient_ids)
        ).all()

        # Mapper
        ing_map = {ing.id: ing for ing in ingredients}

        for item in items:
            ing_id = getattr(item, ingredient_id_field)
            ingredient = ing_map.get(ing_id)

            if not ingredient:
                continue

            # Construire dict enrichi
            enriched = {
                "id": item.id,
                "nom": ingredient.nom,
                "categorie": ingredient.categorie or "Autre",
                "unite": ingredient.unite,
                **_extract_item_fields(item)
            }

            result.append(enriched)

        return result

    if db:
        return _execute(db)

    with get_db_context() as db:
        return _execute(db)


def _extract_item_fields(item: Any) -> Dict:
    """Extrait champs pertinents d'un item"""
    fields = {}

    # Champs communs
    common_fields = [
        "quantite", "priorite", "achete", "notes", "rayon_magasin",
        "magasin_cible", "cree_le", "achete_le", "quantite_necessaire",
        "quantite_min", "emplacement", "date_peremption", "derniere_maj",
        "suggere_par_ia", "statut"
    ]

    for attr in common_fields:
        if hasattr(item, attr):
            fields[attr] = getattr(item, attr)

    return fields


# ═══════════════════════════════════════════════════════════
# CACHE QUERIES (OPTIMISATION)
# ═══════════════════════════════════════════════════════════

@Cache.cached(ttl=300, key="ingredients_all")
def get_all_ingredients_cached() -> List[Dict]:
    """
    Cache des ingrédients (évite queries répétées)

    Returns:
        Liste de tous les ingrédients

    Usage:
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


def get_ingredient_by_name(nom: str) -> Optional[Dict]:
    """
    Récupère ingrédient par nom (utilise cache)

    Args:
        nom: Nom ingrédient

    Returns:
        Dict ingrédient ou None
    """
    ingredients = get_all_ingredients_cached()

    for ing in ingredients:
        if ing["nom"].lower() == nom.lower():
            return ing

    return None


# ═══════════════════════════════════════════════════════════
# VALIDATION MÉTIER
# ═══════════════════════════════════════════════════════════

def validate_quantity(value: float, field_name: str = "quantité"):
    """
    Valide quantité (positive)

    Args:
        value: Valeur à valider
        field_name: Nom du champ (pour message erreur)

    Raises:
        ValidationError si invalide

    Usage:
        validate_quantity(recette.quantite, "quantité")
    """
    from src.core.errors import ValidationError

    if value < 0:
        raise ValidationError(
            f"{field_name} négative",
            details={"field": field_name, "value": value},
            user_message=f"{field_name} doit être positive"
        )


def validate_date_not_past(value: Any, field_name: str = "date"):
    """
    Valide que date n'est pas passée

    Args:
        value: Date à valider
        field_name: Nom du champ

    Raises:
        ValidationError si passée
    """
    from datetime import date
    from src.core.errors import ValidationError

    if value and value < date.today():
        raise ValidationError(
            f"{field_name} dans le passé",
            user_message=f"{field_name} ne peut être passée"
        )


def validate_stock_level(quantite: float, seuil: float, nom: str):
    """
    Valide niveau de stock

    Args:
        quantite: Quantité actuelle
        seuil: Seuil minimum
        nom: Nom article

    Returns:
        (statut, icone)

    Usage:
        statut, icone = validate_stock_level(5, 10, "Tomates")
    """
    if quantite < seuil * 0.5:
        return "critique", "🔴"
    elif quantite < seuil:
        return "sous_seuil", "⚠️"
    else:
        return "ok", "✅"


# ═══════════════════════════════════════════════════════════
# CONSOLIDATION DONNÉES
# ═══════════════════════════════════════════════════════════

def consolidate_duplicates(
        items: List[Dict],
        key_field: str,
        merge_strategy: Optional[callable] = None
) -> List[Dict]:
    """
    Consolide doublons dans liste

    Args:
        items: Liste d'items
        key_field: Champ pour détecter doublons
        merge_strategy: Fonction(existing, new) -> merged

    Returns:
        Liste consolidée

    Usage:
        def merge_max_qty(existing, new):
            return {
                **existing,
                "quantite": max(existing["quantite"], new["quantite"])
            }

        consolidated = consolidate_duplicates(
            articles,
            "nom",
            merge_max_qty
        )
    """
    consolidation = {}

    for item in items:
        key = item.get(key_field)

        if not key:
            continue

        key_lower = str(key).lower().strip()

        if key_lower in consolidation:
            if merge_strategy:
                consolidation[key_lower] = merge_strategy(
                    consolidation[key_lower],
                    item
                )
            else:
                # Par défaut: garder le premier
                pass
        else:
            consolidation[key_lower] = item

    return list(consolidation.values())


# ═══════════════════════════════════════════════════════════
# HELPERS STATISTIQUES MÉTIER
# ═══════════════════════════════════════════════════════════

def calculate_stock_value(inventaire: List[Dict]) -> float:
    """
    Calcule valeur totale stock

    Args:
        inventaire: Liste articles inventaire

    Returns:
        Valeur estimée totale
    """
    # Simplification: pas de prix dans inventaire actuel
    # À implémenter si besoin
    return 0.0


def calculate_waste_score(inventaire: List[Dict]) -> int:
    """
    Calcule score de gaspillage (0-100)

    Args:
        inventaire: Liste articles

    Returns:
        Score (0=parfait, 100=gaspillage critique)
    """
    if not inventaire:
        return 0

    # Compter items à risque
    risque = len([
        i for i in inventaire
        if i.get("jours_peremption") is not None and i["jours_peremption"] <= 3
    ])

    # Score proportionnel
    score = min(100, int((risque / len(inventaire)) * 100))

    return score


def calculate_shopping_urgency(courses: List[Dict]) -> str:
    """
    Calcule urgence des courses

    Args:
        courses: Liste articles courses

    Returns:
        "urgent" | "normal" | "peut_attendre"
    """
    if not courses:
        return "peut_attendre"

    prioritaires = len([c for c in courses if c.get("priorite") == "haute"])

    if prioritaires >= 5:
        return "urgent"
    elif prioritaires >= 2:
        return "normal"
    else:
        return "peut_attendre"


# ═══════════════════════════════════════════════════════════
# HELPERS FORMATAGE MÉTIER
# ═══════════════════════════════════════════════════════════

def format_recipe_summary(recette: Dict) -> str:
    """
    Formatte résumé recette

    Args:
        recette: Dict recette

    Returns:
        String résumé

    Usage:
        summary = format_recipe_summary(recette)
        # "Pizza Margherita - 30min - 4 portions - Facile"
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

    Usage:
        summary = format_inventory_summary(inventaire)
        # "42 articles | 5 stock bas | 3 péremption proche"
    """
    total = len(inventaire)
    stock_bas = len([i for i in inventaire if i.get("statut") in ["sous_seuil", "critique"]])
    peremption = len([i for i in inventaire if i.get("statut") == "peremption_proche"])

    return f"{total} articles | {stock_bas} stock bas | {peremption} péremption proche"