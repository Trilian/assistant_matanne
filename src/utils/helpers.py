"""
Helpers Utilitaires
Fonctions génériques réutilisables
"""
from typing import Any, List, Dict, Optional, Callable
from datetime import date, datetime, timedelta
import hashlib
import json


# ═══════════════════════════════════════════════════════════════
# MANIPULATION DONNÉES
# ═══════════════════════════════════════════════════════════════

def safe_get(data: Dict, *keys, default=None) -> Any:
    """
    Récupère une valeur avec fallback

    Args:
        data: Dictionnaire
        keys: Chemin vers la valeur
        default: Valeur par défaut

    Returns:
        Valeur ou default

    Usage:
        safe_get(user, "address", "city", default="Unknown")
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
    """
    Fusion profonde de deux dictionnaires

    Args:
        dict1: Premier dict
        dict2: Deuxième dict (prioritaire)

    Returns:
        Dict fusionné
    """
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result


def flatten_dict(data: Dict, parent_key: str = '', sep: str = '.') -> Dict:
    """
    Aplatit un dictionnaire imbriqué

    Args:
        data: Dictionnaire à aplatir
        parent_key: Clé parente
        sep: Séparateur

    Returns:
        Dict aplati

    Usage:
        flatten_dict({"a": {"b": 1}})
        # {"a.b": 1}
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
    Regroupe des items par clé

    Args:
        items: Liste d'items
        key: Clé de regroupement

    Returns:
        Dict groupé

    Usage:
        group_by([{"type": "A", "val": 1}, {"type": "A", "val": 2}], "type")
        # {"A": [{"type": "A", "val": 1}, {"type": "A", "val": 2}]}
    """
    from collections import defaultdict

    grouped = defaultdict(list)

    for item in items:
        group_key = item.get(key)
        grouped[group_key].append(item)

    return dict(grouped)


def deduplicate(items: List[Any], key: Optional[Callable] = None) -> List[Any]:
    """
    Déduplique une liste

    Args:
        items: Liste à dédupliquer
        key: Fonction pour extraire la clé (optionnel)

    Returns:
        Liste dédupliquée

    Usage:
        deduplicate([1, 2, 2, 3])  # [1, 2, 3]
        deduplicate([{"id": 1}, {"id": 1}], key=lambda x: x["id"])
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


# ═══════════════════════════════════════════════════════════════
# MANIPULATION DATES
# ═══════════════════════════════════════════════════════════════

def get_week_bounds(d: date) -> tuple[date, date]:
    """
    Retourne lundi et dimanche de la semaine

    Args:
        d: Date de référence

    Returns:
        (lundi, dimanche)
    """
    monday = d - timedelta(days=d.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


def get_month_bounds(d: date) -> tuple[date, date]:
    """
    Retourne premier et dernier jour du mois

    Args:
        d: Date de référence

    Returns:
        (premier_jour, dernier_jour)
    """
    first_day = d.replace(day=1)

    # Dernier jour = premier jour du mois suivant - 1 jour
    if d.month == 12:
        next_month = first_day.replace(year=d.year + 1, month=1)
    else:
        next_month = first_day.replace(month=d.month + 1)

    last_day = next_month - timedelta(days=1)

    return first_day, last_day


def date_range(start: date, end: date) -> List[date]:
    """
    Génère une liste de dates

    Args:
        start: Date de début
        end: Date de fin

    Returns:
        Liste de dates
    """
    delta = end - start
    return [start + timedelta(days=i) for i in range(delta.days + 1)]


def relative_date(d: date) -> str:
    """
    Formatte une date relativement (hier, aujourd'hui, demain)

    Args:
        d: Date

    Returns:
        String formaté

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


# ═══════════════════════════════════════════════════════════════
# HASH & IDENTIFIANTS
# ═══════════════════════════════════════════════════════════════

def generate_id(data: Any) -> str:
    """
    Génère un ID unique basé sur les données

    Args:
        data: Données à hasher

    Returns:
        ID unique (hash MD5)
    """
    data_str = json.dumps(data, sort_keys=True, default=str)
    return hashlib.md5(data_str.encode()).hexdigest()[:16]


def short_id(length: int = 8) -> str:
    """
    Génère un ID court aléatoire

    Args:
        length: Longueur de l'ID

    Returns:
        ID aléatoire
    """
    import random
    import string

    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


# ═══════════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════════

def is_valid_email(email: str) -> bool:
    """
    Valide une adresse email

    Args:
        email: Email à valider

    Returns:
        True si valide
    """
    import re

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_url(url: str) -> bool:
    """
    Valide une URL

    Args:
        url: URL à valider

    Returns:
        True si valide
    """
    import re

    pattern = r'^https?://[\w\-]+(\.[\w\-]+)+[/#?]?.*$'
    return bool(re.match(pattern, url))


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Limite une valeur entre min et max

    Args:
        value: Valeur
        min_val: Min
        max_val: Max

    Returns:
        Valeur limitée
    """
    return max(min_val, min(value, max_val))


# ═══════════════════════════════════════════════════════════════
# STRINGS
# ═══════════════════════════════════════════════════════════════

def truncate(text: str, length: int = 100, suffix: str = "...") -> str:
    """
    Tronque un texte

    Args:
        text: Texte
        length: Longueur max
        suffix: Suffixe si tronqué

    Returns:
        Texte tronqué
    """
    if len(text) <= length:
        return text

    return text[:length - len(suffix)] + suffix


def slugify(text: str) -> str:
    """
    Convertit un texte en slug

    Args:
        text: Texte à slugifier

    Returns:
        Slug

    Usage:
        slugify("Mon Titre!")  # "mon-titre"
    """
    import re

    text = text.lower()
    text = re.sub(r'[àáâãäå]', 'a', text)
    text = re.sub(r'[èéêë]', 'e', text)
    text = re.sub(r'[ìíîï]', 'i', text)
    text = re.sub(r'[òóôõö]', 'o', text)
    text = re.sub(r'[ùúûü]', 'u', text)
    text = re.sub(r'[ýÿ]', 'y', text)
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = text.strip('-')

    return text


def pluralize(count: int, singular: str, plural: str) -> str:
    """
    Pluralise un mot

    Args:
        count: Nombre
        singular: Forme singulier
        plural: Forme pluriel

    Returns:
        Forme correcte

    Usage:
        pluralize(1, "jour", "jours")  # "jour"
        pluralize(2, "jour", "jours")  # "jours"
    """
    return singular if count <= 1 else plural


# ═══════════════════════════════════════════════════════════════
# RETRY & ERROR HANDLING
# ═══════════════════════════════════════════════════════════════

def retry(
        func: Callable,
        max_attempts: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
        exceptions: tuple = (Exception,)
):
    """
    Retry une fonction avec backoff exponentiel

    Args:
        func: Fonction à exécuter
        max_attempts: Nombre max de tentatives
        delay: Délai initial
        backoff: Multiplicateur du délai
        exceptions: Exceptions à catch

    Returns:
        Résultat de la fonction

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
    Exécute une fonction avec gestion d'erreur

    Args:
        func: Fonction à exécuter
        default: Valeur par défaut si erreur
        log_error: Logger l'erreur

    Returns:
        Résultat ou default
    """
    try:
        return func()
    except Exception as e:
        if log_error:
            import logging
            logging.error(f"Error in safe_execute: {e}")
        return default


# ═══════════════════════════════════════════════════════════════
# CACHE & MEMOIZATION
# ═══════════════════════════════════════════════════════════════

def memoize(func: Callable) -> Callable:
    """
    Decorator simple de mémoization

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