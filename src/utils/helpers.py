"""
Helpers Unifiés - VERSION CONSOLIDÉE
Fusionne tous les helpers en structure claire

Structure:
- src/utils/helpers.py (fonctions génériques)
- src/utils/service_helpers.py (helpers métier services)
"""
import logging
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from datetime import date, datetime, timedelta
from collections import defaultdict, Counter
import hashlib
import json
import re

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# MANIPULATION DONNÉES
# ═══════════════════════════════════════════════════════════

def safe_get(data: Dict, *keys, default=None) -> Any:
    """
    Récupère valeur avec fallback

    Usage:
        safe_get(user, "address", "city", default="Paris")
    """
    result = data
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key)
        else:
            return default

        if result is None:
            return default

    return result


def deep_merge(dict1: Dict, dict2: Dict) -> Dict:
    """Fusion profonde de dicts"""
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result


def flatten_dict(data: Dict, parent_key: str = '', sep: str = '.') -> Dict:
    """
    Aplatit dict imbriqué

    Usage:
        flatten_dict({"a": {"b": 1}})  # {"a.b": 1}
    """
    items = []

    for key, value in data.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key

        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, sep=sep).items())
        else:
            items.append((new_key, value))

    return dict(items)


def group_by(items: List[Dict], key: str) -> Dict[Any, List[Dict]]:
    """
    Regroupe items par clé

    Usage:
        group_by(recettes, "categorie")
    """
    grouped = defaultdict(list)

    for item in items:
        group_key = item.get(key)
        grouped[group_key].append(item)

    return dict(grouped)


def count_by(items: List[Dict], key: str) -> Dict[Any, int]:
    """
    Compte items par clé

    Usage:
        count_by(inventaire, "categorie")
    """
    return dict(Counter(item.get(key) for item in items))


def deduplicate(items: List[Any], key: Optional[Callable] = None) -> List[Any]:
    """
    Déduplique liste

    Usage:
        deduplicate([1, 2, 2, 3])
        deduplicate(items, key=lambda x: x["id"])
    """
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


def chunk_list(items: List, size: int) -> List[List]:
    """
    Découpe liste en chunks

    Usage:
        chunk_list([1,2,3,4,5], 2)  # [[1,2], [3,4], [5]]
    """
    return [items[i:i + size] for i in range(0, len(items), size)]


# ═══════════════════════════════════════════════════════════
# MANIPULATION DATES
# ═══════════════════════════════════════════════════════════

def get_week_bounds(d: date) -> Tuple[date, date]:
    """Retourne (lundi, dimanche) de la semaine"""
    monday = d - timedelta(days=d.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


def get_month_bounds(d: date) -> Tuple[date, date]:
    """Retourne (premier, dernier) jour du mois"""
    first_day = d.replace(day=1)

    if d.month == 12:
        next_month = first_day.replace(year=d.year + 1, month=1)
    else:
        next_month = first_day.replace(month=d.month + 1)

    last_day = next_month - timedelta(days=1)

    return first_day, last_day


def date_range(start: date, end: date) -> List[date]:
    """Génère liste de dates"""
    delta = end - start
    return [start + timedelta(days=i) for i in range(delta.days + 1)]


def relative_date(d: date) -> str:
    """
    Date relative

    Usage:
        relative_date(date.today())  # "Aujourd'hui"
    """
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


def days_between(date1: date, date2: date) -> int:
    """Jours entre deux dates"""
    return abs((date2 - date1).days)


# ═══════════════════════════════════════════════════════════
# HASH & IDENTIFIANTS
# ═══════════════════════════════════════════════════════════

def generate_id(data: Any) -> str:
    """
    Génère ID unique basé sur données

    Usage:
        generate_id({"nom": "Pizza", "prix": 12})
    """
    data_str = json.dumps(data, sort_keys=True, default=str)
    return hashlib.md5(data_str.encode()).hexdigest()[:16]


def short_id(length: int = 8) -> str:
    """Génère ID court aléatoire"""
    import random
    import string

    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def slugify(text: str) -> str:
    """
    Convertit texte en slug

    Usage:
        slugify("Mon Titre!")  # "mon-titre"
    """
    text = text.lower()

    # Remplacer accents
    replacements = {
        'à': 'a', 'á': 'a', 'â': 'a', 'ã': 'a', 'ä': 'a', 'å': 'a',
        'è': 'e', 'é': 'e', 'ê': 'e', 'ë': 'e',
        'ì': 'i', 'í': 'i', 'î': 'i', 'ï': 'i',
        'ò': 'o', 'ó': 'o', 'ô': 'o', 'õ': 'o', 'ö': 'o',
        'ù': 'u', 'ú': 'u', 'û': 'u', 'ü': 'u',
        'ý': 'y', 'ÿ': 'y'
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = text.strip('-')

    return text


# ═══════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════

def is_valid_email(email: str) -> bool:
    """Valide email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_url(url: str) -> bool:
    """Valide URL"""
    pattern = r'^https?://[\w\-]+(\.[\w\-]+)+[/#?]?.*$'
    return bool(re.match(pattern, url))


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Limite valeur entre min et max"""
    return max(min_val, min(value, max_val))


def validate_positive(value: float, field_name: str = "valeur"):
    """Valide que valeur est positive (raise si négatif)"""
    from src.core.errors import ValidationError

    if value <= 0:
        raise ValidationError(
            f"{field_name} doit être positif",
            details={"field": field_name, "value": value},
            user_message=f"{field_name} doit être supérieur à 0"
        )


def validate_range(value: float, min_val: float, max_val: float, field_name: str = "valeur"):
    """Valide que valeur est dans range"""
    from src.core.errors import ValidationError

    if not min_val <= value <= max_val:
        raise ValidationError(
            f"{field_name} hors limites",
            details={"value": value, "min": min_val, "max": max_val},
            user_message=f"{field_name} doit être entre {min_val} et {max_val}"
        )


# ═══════════════════════════════════════════════════════════
# STRINGS
# ═══════════════════════════════════════════════════════════

def truncate(text: str, length: int = 100, suffix: str = "...") -> str:
    """Tronque texte"""
    if len(text) <= length:
        return text

    return text[:length - len(suffix)] + suffix


def pluralize(count: int, singular: str, plural: str) -> str:
    """
    Pluralise mot

    Usage:
        pluralize(1, "jour", "jours")  # "jour"
        pluralize(2, "jour", "jours")  # "jours"
    """
    return singular if count <= 1 else plural


def clean_text(text: str) -> str:
    """Nettoie texte (évite injection)"""
    if not text:
        return text

    text = re.sub(r"[<>{}]", "", text)
    return text.strip()


def extract_number(text: str) -> Optional[float]:
    """
    Extrait nombre depuis string

    Usage:
        extract_number("2.5 kg")  # 2.5
        extract_number("Prix: 10,50€")  # 10.5
    """
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


# ═══════════════════════════════════════════════════════════
# RETRY & ERROR HANDLING
# ═══════════════════════════════════════════════════════════

def retry(
        func: Callable,
        max_attempts: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
        exceptions: tuple = (Exception,)
):
    """
    Retry fonction avec backoff

    Usage:
        result = retry(lambda: api_call(), max_attempts=3)
    """
    import time

    current_delay = delay

    for attempt in range(max_attempts):
        try:
            return func()
        except exceptions as e:
            if attempt == max_attempts - 1:
                raise

            time.sleep(current_delay)
            current_delay *= backoff


def safe_execute(func: Callable, default=None, log_error: bool = True):
    """
    Exécute fonction avec gestion d'erreur

    Usage:
        value = safe_execute(lambda: risky_operation(), default=0)
    """
    try:
        return func()
    except Exception as e:
        if log_error:
            logger.error(f"Error in safe_execute: {e}")
        return default


# ═══════════════════════════════════════════════════════════
# MÉMOIZATION
# ═══════════════════════════════════════════════════════════

def memoize(func: Callable) -> Callable:
    """
    Decorator mémoization simple

    Usage:
        @memoize
        def expensive_func(n):
            return n * 2
    """
    cache = {}

    def wrapper(*args, **kwargs):
        key = str(args) + str(sorted(kwargs.items()))

        if key not in cache:
            cache[key] = func(*args, **kwargs)

        return cache[key]

    return wrapper


# ═══════════════════════════════════════════════════════════
# STATISTIQUES
# ═══════════════════════════════════════════════════════════

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


def calculate_percentile(values: List[float], percentile: int) -> float:
    """Percentile"""
    if not values:
        return 0.0

    sorted_values = sorted(values)
    index = int(len(sorted_values) * percentile / 100)
    return sorted_values[min(index, len(sorted_values) - 1)]


# ═══════════════════════════════════════════════════════════
# CONVERSION
# ═══════════════════════════════════════════════════════════

def model_to_dict(obj: Any, exclude: Optional[List[str]] = None) -> Dict:
    """
    Convertit modèle SQLAlchemy en dict

    Usage:
        recipe_dict = model_to_dict(recipe, exclude=["id"])
    """
    if not obj:
        return {}

    exclude = exclude or []
    result = {}

    if hasattr(obj, "__table__"):
        for col in obj.__table__.columns:
            if col.name not in exclude:
                value = getattr(obj, col.name)

                if hasattr(value, "isoformat"):
                    value = value.isoformat()

                result[col.name] = value

    return result


def batch_to_dicts(objects: List[Any], exclude: Optional[List[str]] = None) -> List[Dict]:
    """Conversion batch"""
    return [model_to_dict(obj, exclude) for obj in objects]