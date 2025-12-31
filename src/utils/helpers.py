"""
Helpers Consolidés
"""
import logging
from typing import Any, Dict, List, Optional, Tuple
from datetime import date, datetime, timedelta
from collections import defaultdict, Counter
from sqlalchemy.orm import Session
import hashlib
import json
import re

from src.core.database import get_db_context
from src.core.models import Ingredient
from src.core.cache import Cache

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════
# MANIPULATION DONNÉES
# ════════════════════════════════════════════════════════════

def safe_get(data: Dict, *keys, default=None) -> Any:
    """Récupère valeur avec fallback"""
    result = data
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key)
        else:
            return default
        if result is None:
            return default
    return result


def group_by(items: List[Dict], key: str) -> Dict[Any, List[Dict]]:
    """Regroupe items par clé"""
    grouped = defaultdict(list)
    for item in items:
        group_key = item.get(key)
        grouped[group_key].append(item)
    return dict(grouped)


def count_by(items: List[Dict], key: str) -> Dict[Any, int]:
    """Compte items par clé"""
    return dict(Counter(item.get(key) for item in items))


def deduplicate(items: List[Any], key: Optional[callable] = None) -> List[Any]:
    """Déduplique liste"""
    if not key:
        return list(dict.fromkeys(items))
    seen = set()
    result = []
    for item in items:
        item_key = key(item)
        if item_key not in seen:
            seen.add(item_key)
            result.append(item)
    return result


# ════════════════════════════════════════════════════════════
# MANIPULATION DATES
# ════════════════════════════════════════════════════════════

def get_week_bounds(d: date) -> Tuple[date, date]:
    """Retourne (lundi, dimanche) de la semaine"""
    monday = d - timedelta(days=d.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


def date_range(start: date, end: date) -> List[date]:
    """Génère liste de dates"""
    delta = end - start
    return [start + timedelta(days=i) for i in range(delta.days + 1)]


def relative_date(d: date) -> str:
    """Date relative (Aujourd'hui, Hier, etc.)"""
    today = date.today()
    delta = (d - today).days
    if delta == 0:
        return "Aujourd'hui"
    elif delta == 1:
        return "Demain"
    elif delta == -1:
        return "Hier"
    elif 2 <= delta <= 7:
        return f"Dans {delta} jours"
    elif -7 <= delta <= -2:
        return f"Il y a {abs(delta)} jours"
    else:
        return d.strftime("%d/%m/%Y")


# ════════════════════════════════════════════════════════════
# HASH & IDENTIFIANTS
# ════════════════════════════════════════════════════════════

def generate_id(data: Any) -> str:
    """Génère ID unique basé sur données"""
    data_str = json.dumps(data, sort_keys=True, default=str)
    return hashlib.md5(data_str.encode()).hexdigest()[:16]


def slugify(text: str) -> str:
    """Convertit texte en slug"""
    text = text.lower()
    replacements = {
        'à': 'a', 'á': 'a', 'â': 'a', 'ä': 'a',
        'è': 'e', 'é': 'e', 'ê': 'e', 'ë': 'e',
        'ù': 'u', 'ú': 'u', 'û': 'u', 'ü': 'u'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')


# ════════════════════════════════════════════════════════════
# VALIDATION
# ════════════════════════════════════════════════════════════

def is_valid_email(email: str) -> bool:
    """Valide email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Limite valeur entre min et max"""
    return max(min_val, min(value, max_val))


# ════════════════════════════════════════════════════════════
# STRINGS
# ════════════════════════════════════════════════════════════

def truncate(text: str, length: int = 100, suffix: str = "...") -> str:
    """Tronque texte"""
    if len(text) <= length:
        return text
    return text[:length - len(suffix)] + suffix


def clean_text(text: str) -> str:
    """Nettoie texte (évite injection)"""
    if not text:
        return text
    return re.sub(r"[<>{}]", "", text).strip()


def extract_number(text: str) -> Optional[float]:
    """Extrait nombre depuis string"""
    if not text:
        return None
    text = str(text).replace(",", ".")
    match = re.search(r"-?\d+\.?\d*", text)
    if match:
        try:
            return float(match.group())
        except ValueError:
            return None
    return None


# ════════════════════════════════════════════════════════════
# STATISTIQUES
# ════════════════════════════════════════════════════════════

def calculate_average(values: List[float]) -> float:
    """Moyenne"""
    return sum(values) / len(values) if values else 0.0


def calculate_median(values: List[float]) -> float:
    """Médiane"""
    if not values:
        return 0.0
    sorted_values = sorted(values)
    n = len(sorted_values)
    if n % 2 == 0:
        return (sorted_values[n//2 - 1] + sorted_values[n//2]) / 2
    else:
        return sorted_values[n//2]


# ════════════════════════════════════════════════════════════
# GESTION INGRÉDIENTS (SERVICE HELPERS)
# ════════════════════════════════════════════════════════════

def find_or_create_ingredient(nom: str, unite: str, categorie: Optional[str] = None,
                              db: Session = None) -> int:
    """Trouve ou crée un ingrédient"""
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


def batch_find_or_create_ingredients(items: List[Dict], db: Session = None) -> Dict[str, int]:
    """Batch création ingrédients (optimisé)"""
    def _execute(session: Session) -> Dict[str, int]:
        result = {}
        noms = [item["nom"] for item in items]
        existants = session.query(Ingredient).filter(Ingredient.nom.in_(noms)).all()

        for ing in existants:
            result[ing.nom] = ing.id

        for item in items:
            if item["nom"] not in result:
                ingredient = Ingredient(nom=item["nom"], unite=item["unite"],
                                        categorie=item.get("categorie"))
                session.add(ingredient)
                session.flush()
                result[item["nom"]] = ingredient.id

        return result

    if db:
        return _execute(db)
    with get_db_context() as db:
        return _execute(db)


@Cache.cached(ttl=300, key="ingredients_all")
def get_all_ingredients_cached() -> List[Dict]:
    """Cache des ingrédients"""
    with get_db_context() as db:
        ingredients = db.query(Ingredient).all()
        return [
            {"id": ing.id, "nom": ing.nom, "unite": ing.unite, "categorie": ing.categorie}
            for ing in ingredients
        ]


def enrich_with_ingredient_info(items: List[Any], ingredient_id_field: str = "ingredient_id",
                                db: Session = None) -> List[Dict]:
    """Enrichit items avec infos ingrédient (évite N+1 queries)"""
    def _execute(session: Session) -> List[Dict]:
        result = []
        ingredient_ids = [getattr(item, ingredient_id_field) for item in items]
        ingredients = session.query(Ingredient).filter(Ingredient.id.in_(ingredient_ids)).all()
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

            for attr in ["quantite", "priorite", "achete", "notes", "seuil", "emplacement", "date_peremption"]:
                if hasattr(item, attr):
                    enriched[attr] = getattr(item, attr)

            result.append(enriched)

        return result

    if db:
        return _execute(db)
    with get_db_context() as db:
        return _execute(db)


# ════════════════════════════════════════════════════════════
# CONSOLIDATION DONNÉES
# ════════════════════════════════════════════════════════════

def consolidate_duplicates(items: List[Dict], key_field: str,
                           merge_strategy: Optional[callable] = None) -> List[Dict]:
    """Consolide doublons dans liste"""
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


# ════════════════════════════════════════════════════════════
# HELPERS MÉTIER
# ════════════════════════════════════════════════════════════

def validate_stock_level(quantite: float, seuil: float, nom: str) -> Tuple[str, str]:
    """Valide niveau de stock"""
    if quantite < seuil * 0.5:
        return "critique", "🔴"
    elif quantite < seuil:
        return "sous_seuil", "⚠️"
    else:
        return "ok", "✅"


def format_recipe_summary(recette: Dict) -> str:
    """Formatte résumé recette"""
    temps = recette.get("temps_preparation", 0) + recette.get("temps_cuisson", 0)
    parts = [
        recette.get("nom", "Sans nom"),
        f"{temps}min",
        f"{recette.get('portions', 4)} portions",
        recette.get("difficulte", "moyen").capitalize()
    ]
    return " - ".join(parts)


def format_inventory_summary(inventaire: List[Dict]) -> str:
    """Formatte résumé inventaire"""
    total = len(inventaire)
    stock_bas = len([i for i in inventaire if i.get("statut") in ["sous_seuil", "critique"]])
    peremption = len([i for i in inventaire if i.get("statut") == "peremption_proche"])
    return f"{total} articles | {stock_bas} stock bas | {peremption} péremption proche"