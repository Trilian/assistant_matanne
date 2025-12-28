"""
Helpers Services Unifiés
Élimine duplication entre recette/inventaire/courses services
"""
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from src.core.database import get_db_context
from src.core.models import Ingredient


# ═══════════════════════════════════════════════════════════════
# GESTION INGRÉDIENTS (DRY)
# ═══════════════════════════════════════════════════════════════

def find_or_create_ingredient(
        nom: str,
        unite: str,
        categorie: Optional[str] = None,
        db: Session = None
) -> int:
    """
    Trouve ou crée un ingrédient (utilisé par recettes/inventaire/courses)

    Returns:
        ingredient_id
    """
    def _execute(session: Session) -> int:
        ingredient = session.query(Ingredient).filter(Ingredient.nom == nom).first()

        if not ingredient:
            ingredient = Ingredient(
                nom=nom,
                unite=unite,
                categorie=categorie
            )
            session.add(ingredient)
            session.flush()

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
    Batch création ingrédients

    Returns:
        {"nom": ingredient_id}
    """
    def _execute(session: Session) -> Dict[str, int]:
        result = {}

        # Chercher existants
        noms = [item["nom"] for item in items]
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


# ═══════════════════════════════════════════════════════════════
# ENRICHISSEMENT (DRY)
# ═══════════════════════════════════════════════════════════════

def enrich_with_ingredient_info(
        items: List[Any],
        ingredient_id_field: str = "ingredient_id",
        db: Session = None
) -> List[Dict]:
    """
    Enrichit liste d'items avec infos ingrédient

    Utilisé par inventaire/courses pour éviter duplication _enrich_items()
    """
    def _execute(session: Session) -> List[Dict]:
        result = []

        # Récupérer tous les ingrédients en 1 query
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
    """Extrait champs pertinents d'un modèle"""
    fields = {}

    # Champs communs
    for attr in ["quantite", "priorite", "achete", "notes", "rayon_magasin",
                 "magasin_cible", "cree_le", "achete_le", "quantite_necessaire",
                 "quantite_min", "emplacement", "date_peremption", "derniere_maj",
                 "suggere_par_ia", "statut"]:
        if hasattr(item, attr):
            fields[attr] = getattr(item, attr)

    return fields


# ═══════════════════════════════════════════════════════════════
# HELPERS CONVERSION (DRY)
# ═══════════════════════════════════════════════════════════════

def model_to_dict_safe(obj: Any, exclude: Optional[List[str]] = None) -> Dict:
    """
    Conversion modèle → dict sécurisée

    Remplace les multiples _recette_to_dict(), etc.
    """
    if not obj:
        return {}

    exclude = exclude or []
    result = {}

    # Colonnes SQLAlchemy
    if hasattr(obj, "__table__"):
        for col in obj.__table__.columns:
            if col.name not in exclude:
                value = getattr(obj, col.name)

                # Serialization datetime
                if hasattr(value, "isoformat"):
                    value = value.isoformat()

                result[col.name] = value

    return result


def batch_models_to_dicts(
        objects: List[Any],
        exclude: Optional[List[str]] = None
) -> List[Dict]:
    """Conversion batch"""
    return [model_to_dict_safe(obj, exclude) for obj in objects]


# ═══════════════════════════════════════════════════════════════
# CACHE QUERIES (OPTIMISATION)
# ═══════════════════════════════════════════════════════════════

from src.core.smart_cache import SmartCache

@SmartCache.cached(ttl=300, level="session", key_prefix="ingredients_all")
def get_all_ingredients_cached() -> List[Dict]:
    """
    Cache des ingrédients (évite queries répétées)
    """
    with get_db_context() as db:
        ingredients = db.query(Ingredient).all()
        return batch_models_to_dicts(ingredients)


# ═══════════════════════════════════════════════════════════════
# VALIDATION COMMUNE
# ═══════════════════════════════════════════════════════════════

def validate_quantity(value: float, field_name: str = "quantité"):
    """Validation quantité"""
    from src.core.exceptions import ValidationError

    if value < 0:
        raise ValidationError(
            f"{field_name} négative",
            details={"field": field_name, "value": value},
            user_message=f"{field_name} doit être positive"
        )


def validate_date_not_past(value, field_name: str = "date"):
    """Validation date future"""
    from datetime import date
    from src.core.exceptions import ValidationError

    if value and value < date.today():
        raise ValidationError(
            f"{field_name} dans le passé",
            user_message=f"{field_name} ne peut être passée"
        )