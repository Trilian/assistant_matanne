"""
Fonctions utilitaires pures pour le service de suggestions IA.

Ces fonctions peuvent être testées sans base de données ni clients IA.
Elles représentent la logique métier pure extraite de suggestions_ia.py.
"""

from collections import Counter
from datetime import date, datetime, timedelta
from typing import Any


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

# Saisons et mois associés
SAISONS = {
    "printemps": [3, 4, 5],
    "été": [6, 7, 8],
    "automne": [9, 10, 11],
    "hiver": [12, 1, 2],
}

# Ingrédients de saison
INGREDIENTS_SAISON = {
    "printemps": [
        "asperge", "radis", "épinard", "petit pois", "fève", "carotte nouvelle",
        "fraise", "rhubarbe", "artichaut", "chou-fleur", "laitue", "cresson"
    ],
    "été": [
        "tomate", "courgette", "aubergine", "poivron", "concombre", "haricot vert",
        "melon", "pastèque", "pêche", "abricot", "cerise", "framboise", "myrtille"
    ],
    "automne": [
        "champignon", "potiron", "courge", "butternut", "châtaigne", "noix",
        "pomme", "poire", "raisin", "coing", "chou", "poireau", "céleri"
    ],
    "hiver": [
        "endive", "mâche", "chou de bruxelles", "navet", "panais", "topinambour",
        "orange", "clémentine", "kiwi", "pamplemousse", "pomme de terre", "oignon"
    ],
}

# Types de protéines
PROTEINES_POISSON = ["poisson", "saumon", "cabillaud", "thon", "dorade", "bar", "sole", "truite"]
PROTEINES_VIANDE_ROUGE = ["boeuf", "agneau", "veau", "porc", "canard", "gibier"]
PROTEINES_VOLAILLE = ["poulet", "dinde", "pintade"]
PROTEINES_VEGETARIEN = ["tofu", "tempeh", "seitan", "légumineuse", "lentille", "pois chiche"]

# Scores de pertinence
SCORE_INGREDIENT_DISPONIBLE = 10
SCORE_INGREDIENT_PRIORITAIRE = 25  # À consommer vite
SCORE_INGREDIENT_SAISON = 5
SCORE_CATEGORIE_PREFEREE = 15
SCORE_JAMAIS_PREPAREE = 20
SCORE_DIFFICULTE_ADAPTEE = 10
SCORE_TEMPS_ADAPTE = 15
SCORE_VARIETE = 10  # Pas préparée récemment


# ═══════════════════════════════════════════════════════════
# DÉTERMINATION DE LA SAISON
# ═══════════════════════════════════════════════════════════


def get_current_season(dt: date | datetime | None = None) -> str:
    """
    Détermine la saison pour une date donnée.
    
    Args:
        dt: Date (par défaut: aujourd'hui)
        
    Returns:
        Nom de la saison (printemps, été, automne, hiver)
        
    Examples:
        >>> get_current_season(date(2024, 7, 15))
        'été'
        >>> get_current_season(date(2024, 12, 25))
        'hiver'
    """
    if dt is None:
        dt = date.today()
    elif isinstance(dt, datetime):
        dt = dt.date()
    
    month = dt.month
    
    for saison, mois in SAISONS.items():
        if month in mois:
            return saison
    
    return "hiver"  # Fallback


def get_seasonal_ingredients(saison: str | None = None) -> list[str]:
    """
    Retourne les ingrédients de saison.
    
    Args:
        saison: Nom de la saison (calcule automatiquement si None)
        
    Returns:
        Liste des ingrédients de saison
        
    Examples:
        >>> get_seasonal_ingredients("été")
        ['tomate', 'courgette', ...]
    """
    if saison is None:
        saison = get_current_season()
    
    saison = saison.lower().replace("é", "e").replace("è", "e")
    
    # Normaliser les noms
    if saison == "ete":
        saison = "été"
    
    return INGREDIENTS_SAISON.get(saison, [])


def is_ingredient_in_season(ingredient: str, saison: str | None = None) -> bool:
    """
    Vérifie si un ingrédient est de saison.
    
    Args:
        ingredient: Nom de l'ingrédient
        saison: Saison (calcule automatiquement si None)
        
    Returns:
        True si l'ingrédient est de saison
    """
    ingredients_saison = get_seasonal_ingredients(saison)
    ingredient_lower = ingredient.lower()
    
    return any(ing in ingredient_lower or ingredient_lower in ing for ing in ingredients_saison)


# ═══════════════════════════════════════════════════════════
# ANALYSE DU PROFIL CULINAIRE
# ═══════════════════════════════════════════════════════════


def analyze_categories(historique: list[dict]) -> list[str]:
    """
    Analyse les catégories préférées à partir de l'historique.
    
    Args:
        historique: Liste de dicts avec clé 'categorie'
        
    Returns:
        Liste des catégories par ordre de préférence (max 5)
        
    Examples:
        >>> analyze_categories([{'categorie': 'italien'}, {'categorie': 'italien'}, {'categorie': 'asiatique'}])
        ['italien', 'asiatique']
    """
    categories = [h.get("categorie") for h in historique if h.get("categorie")]
    counter = Counter(categories)
    return [cat for cat, _ in counter.most_common(5)]


def analyze_frequent_ingredients(historique: list[dict]) -> list[str]:
    """
    Identifie les ingrédients fréquemment utilisés.
    
    Args:
        historique: Liste de dicts avec clé 'ingredients' (liste de noms)
        
    Returns:
        Liste des ingrédients par fréquence (max 10)
    """
    all_ingredients = []
    for h in historique:
        ingredients = h.get("ingredients", [])
        if isinstance(ingredients, list):
            all_ingredients.extend(ingredients)
    
    counter = Counter(all_ingredients)
    return [ing for ing, _ in counter.most_common(10)]


def calculate_average_difficulty(historique: list[dict]) -> str:
    """
    Calcule la difficulté moyenne des recettes préparées.
    
    Args:
        historique: Liste de dicts avec clé 'difficulte'
        
    Returns:
        Difficulté moyenne (facile, moyen, difficile)
    """
    difficultes = [h.get("difficulte") for h in historique if h.get("difficulte")]
    
    if not difficultes:
        return "moyen"
    
    counter = Counter(difficultes)
    return counter.most_common(1)[0][0]


def calculate_average_time(historique: list[dict]) -> int:
    """
    Calcule le temps de préparation moyen.
    
    Args:
        historique: Liste de dicts avec clé 'temps_preparation' (minutes)
        
    Returns:
        Temps moyen en minutes
    """
    temps = [h.get("temps_preparation", 0) for h in historique if h.get("temps_preparation")]
    
    if not temps:
        return 45  # Valeur par défaut
    
    return int(sum(temps) / len(temps))


def calculate_average_portions(historique: list[dict]) -> int:
    """
    Calcule le nombre de portions moyen.
    
    Args:
        historique: Liste de dicts avec clé 'portions'
        
    Returns:
        Nombre de portions moyen
    """
    portions = [h.get("portions", 0) for h in historique if h.get("portions")]
    
    if not portions:
        return 4  # Valeur par défaut
    
    return int(sum(portions) / len(portions))


def identify_favorites(historique: list[dict], min_count: int = 3) -> list[int]:
    """
    Identifie les recettes favorites (préparées plusieurs fois).
    
    Args:
        historique: Liste de dicts avec clé 'recette_id'
        min_count: Nombre minimum de préparations pour être favori
        
    Returns:
        Liste des IDs de recettes favorites
    """
    recette_ids = [h.get("recette_id") for h in historique if h.get("recette_id")]
    counter = Counter(recette_ids)
    
    return [rid for rid, count in counter.items() if count >= min_count]


def days_since_last_preparation(
    recette_id: int,
    historique: list[dict],
    reference_date: date | None = None
) -> int | None:
    """
    Calcule le nombre de jours depuis la dernière préparation d'une recette.
    
    Args:
        recette_id: ID de la recette
        historique: Historique avec 'recette_id' et 'date' ou 'date_cuisson'
        reference_date: Date de référence (par défaut: aujourd'hui)
        
    Returns:
        Nombre de jours, ou None si jamais préparée
    """
    if reference_date is None:
        reference_date = date.today()
    elif isinstance(reference_date, datetime):
        reference_date = reference_date.date()
    
    dates_preparation = []
    for h in historique:
        if h.get("recette_id") == recette_id:
            d = h.get("date") or h.get("date_cuisson")
            if d:
                if isinstance(d, datetime):
                    d = d.date()
                elif isinstance(d, str):
                    try:
                        d = date.fromisoformat(d[:10])
                    except ValueError:
                        continue
                dates_preparation.append(d)
    
    if not dates_preparation:
        return None
    
    derniere = max(dates_preparation)
    return (reference_date - derniere).days


# ═══════════════════════════════════════════════════════════
# SCORING DES RECETTES
# ═══════════════════════════════════════════════════════════


def calculate_recipe_score(
    recette: dict,
    contexte: dict,
    profil: dict | None = None,
    historique: list[dict] | None = None
) -> float:
    """
    Calcule un score de pertinence pour une recette.
    
    Args:
        recette: Dict avec infos de la recette (nom, ingredients, categorie, temps_preparation, difficulte)
        contexte: Dict avec (ingredients_disponibles, ingredients_a_utiliser, temps_disponible_minutes, contraintes)
        profil: Dict avec préférences (categories_preferees, difficulte_moyenne, temps_moyen_minutes)
        historique: Historique des préparations
        
    Returns:
        Score de pertinence (0-100)
    """
    score = 0.0
    
    # Ingrédients disponibles
    recette_ingredients = recette.get("ingredients", [])
    if isinstance(recette_ingredients, str):
        recette_ingredients = [recette_ingredients]
    
    ingredients_disponibles = set(i.lower() for i in contexte.get("ingredients_disponibles", []))
    ingredients_prioritaires = set(i.lower() for i in contexte.get("ingredients_a_utiliser", []))
    
    for ing in recette_ingredients:
        ing_lower = ing.lower() if isinstance(ing, str) else ""
        if ing_lower in ingredients_prioritaires:
            score += SCORE_INGREDIENT_PRIORITAIRE
        elif ing_lower in ingredients_disponibles:
            score += SCORE_INGREDIENT_DISPONIBLE
    
    # Ingrédient de saison
    saison = contexte.get("saison") or get_current_season()
    for ing in recette_ingredients:
        if is_ingredient_in_season(ing, saison):
            score += SCORE_INGREDIENT_SAISON
            break  # Un seul bonus saison par recette
    
    # Catégorie préférée
    if profil:
        categories_preferees = profil.get("categories_preferees", [])
        if recette.get("categorie") in categories_preferees:
            score += SCORE_CATEGORIE_PREFEREE
    
    # Temps adapté
    temps_disponible = contexte.get("temps_disponible_minutes", 60)
    temps_recette = recette.get("temps_preparation", 0) + recette.get("temps_cuisson", 0)
    
    if temps_recette > 0 and temps_recette <= temps_disponible:
        score += SCORE_TEMPS_ADAPTE
    elif temps_recette > temps_disponible:
        # Pénalité si trop long
        score -= 10
    
    # Difficulté adaptée
    if profil:
        difficulte_profil = profil.get("difficulte_moyenne", "moyen")
        difficulte_recette = recette.get("difficulte", "moyen")
        
        if difficulte_recette == difficulte_profil:
            score += SCORE_DIFFICULTE_ADAPTEE
    
    # Variété (pas préparée récemment)
    if historique:
        jours = days_since_last_preparation(recette.get("id"), historique)
        if jours is None:
            score += SCORE_JAMAIS_PREPAREE
        elif jours >= 14:
            score += SCORE_VARIETE
    
    # Contraintes alimentaires
    contraintes = contexte.get("contraintes", [])
    if "vegetarien" in contraintes or "végétarien" in contraintes:
        if not recette.get("est_vegetarien", False):
            score -= 50
    
    if "sans gluten" in contraintes:
        if recette.get("contient_gluten", False):
            score -= 50
    
    # Normaliser entre 0 et 100
    return max(0.0, min(100.0, score))


def rank_recipes(
    recettes: list[dict],
    contexte: dict,
    profil: dict | None = None,
    historique: list[dict] | None = None,
    limit: int = 5
) -> list[dict]:
    """
    Classe les recettes par pertinence.
    
    Args:
        recettes: Liste de recettes à scorer
        contexte: Contexte de suggestion
        profil: Profil culinaire
        historique: Historique des préparations
        limit: Nombre max de résultats
        
    Returns:
        Liste de recettes avec score, triée par pertinence
    """
    scored = []
    
    for recette in recettes:
        score = calculate_recipe_score(recette, contexte, profil, historique)
        scored.append({
            **recette,
            "score": score,
        })
    
    # Trier par score décroissant
    scored.sort(key=lambda r: r["score"], reverse=True)
    
    return scored[:limit]


def generate_suggestion_reason(recette: dict, contexte: dict) -> str:
    """
    Génère une explication pour la suggestion d'une recette.
    
    Args:
        recette: Infos de la recette
        contexte: Contexte de suggestion
        
    Returns:
        Phrase explicative
    """
    raisons = []
    
    # Ingrédients à utiliser
    ingredients_prioritaires = set(i.lower() for i in contexte.get("ingredients_a_utiliser", []))
    recette_ingredients = recette.get("ingredients", [])
    
    matching = [ing for ing in recette_ingredients if ing.lower() in ingredients_prioritaires]
    if matching:
        raisons.append(f"Utilise {', '.join(matching[:2])} à consommer rapidement")
    
    # Saison
    saison = contexte.get("saison") or get_current_season()
    for ing in recette_ingredients:
        if is_ingredient_in_season(ing, saison):
            raisons.append(f"Ingrédient de saison: {ing}")
            break
    
    # Score
    score = recette.get("score", 0)
    if score >= 80:
        raisons.append("Parfaitement adapté à vos préférences")
    elif score >= 60:
        raisons.append("Correspond à vos habitudes")
    
    # Jamais préparée
    if recette.get("est_nouvelle"):
        raisons.append("Recette à découvrir")
    
    if not raisons:
        raisons.append("Suggestion basée sur votre profil")
    
    return ". ".join(raisons[:2])


# ═══════════════════════════════════════════════════════════
# DÉTECTION DE TYPE DE PROTÉINE
# ═══════════════════════════════════════════════════════════


def detect_protein_type(recette: dict) -> str:
    """
    Détecte le type de protéine principal d'une recette.
    
    Args:
        recette: Dict avec 'type_proteines', 'description', 'nom' ou 'ingredients'
        
    Returns:
        Type de protéine (poisson, viande_rouge, volaille, vegetarien, autre)
    """
    # Champ explicite
    type_proteines = recette.get("type_proteines", "").lower()
    if type_proteines:
        if any(p in type_proteines for p in PROTEINES_POISSON):
            return "poisson"
        if any(p in type_proteines for p in PROTEINES_VIANDE_ROUGE):
            return "viande_rouge"
        if any(p in type_proteines for p in PROTEINES_VOLAILLE):
            return "volaille"
        if any(p in type_proteines for p in PROTEINES_VEGETARIEN):
            return "vegetarien"
    
    # Recette explicitement végétarienne
    if recette.get("est_vegetarien"):
        return "vegetarien"
    
    # Analyse du nom et de la description
    text = f"{recette.get('nom', '')} {recette.get('description', '')}".lower()
    
    if any(p in text for p in PROTEINES_POISSON):
        return "poisson"
    if any(p in text for p in PROTEINES_VIANDE_ROUGE):
        return "viande_rouge"
    if any(p in text for p in PROTEINES_VOLAILLE):
        return "volaille"
    
    # Analyse des ingrédients
    ingredients = recette.get("ingredients", [])
    ingredients_text = " ".join(i.lower() if isinstance(i, str) else "" for i in ingredients)
    
    if any(p in ingredients_text for p in PROTEINES_POISSON):
        return "poisson"
    if any(p in ingredients_text for p in PROTEINES_VIANDE_ROUGE):
        return "viande_rouge"
    if any(p in ingredients_text for p in PROTEINES_VOLAILLE):
        return "volaille"
    if any(p in ingredients_text for p in PROTEINES_VEGETARIEN):
        return "vegetarien"
    
    return "autre"


def calculate_week_protein_balance(repas: list[dict]) -> dict:
    """
    Calcule l'équilibre protéique sur une semaine.
    
    Args:
        repas: Liste de repas avec infos recette
        
    Returns:
        Dict avec comptage par type de protéine
    """
    balance = {
        "poisson": 0,
        "viande_rouge": 0,
        "volaille": 0,
        "vegetarien": 0,
        "autre": 0,
    }
    
    for r in repas:
        protein_type = detect_protein_type(r)
        balance[protein_type] = balance.get(protein_type, 0) + 1
    
    return balance


def is_week_balanced(repas: list[dict]) -> tuple[bool, list[str]]:
    """
    Vérifie si une semaine est équilibrée nutritionnellement.
    
    Recommandations:
    - Au moins 2 repas de poisson
    - Maximum 2 repas de viande rouge
    - Au moins 1 repas végétarien
    
    Args:
        repas: Liste de repas de la semaine
        
    Returns:
        Tuple (est_equilibre, liste_problemes)
    """
    balance = calculate_week_protein_balance(repas)
    problemes = []
    
    if balance["poisson"] < 2:
        problemes.append(f"Pas assez de poisson ({balance['poisson']}/2 minimum)")
    
    if balance["viande_rouge"] > 2:
        problemes.append(f"Trop de viande rouge ({balance['viande_rouge']}/2 maximum)")
    
    if balance["vegetarien"] < 1:
        problemes.append("Aucun repas végétarien")
    
    return len(problemes) == 0, problemes


# ═══════════════════════════════════════════════════════════
# CALCUL DE VARIÉTÉ
# ═══════════════════════════════════════════════════════════


def calculate_variety_score(
    recettes_selectionnees: list[dict],
    historique: list[dict],
    jours_reference: int = 14
) -> float:
    """
    Calcule un score de variété pour une sélection de recettes.
    
    Args:
        recettes_selectionnees: Recettes proposées
        historique: Historique des préparations
        jours_reference: Période de référence
        
    Returns:
        Score de variété (0-100)
    """
    if not recettes_selectionnees:
        return 100.0
    
    # Recettes récentes
    reference_date = date.today()
    recettes_recentes = set()
    
    for h in historique:
        d = h.get("date") or h.get("date_cuisson")
        if d:
            if isinstance(d, datetime):
                d = d.date()
            elif isinstance(d, str):
                try:
                    d = date.fromisoformat(d[:10])
                except ValueError:
                    continue
            
            if (reference_date - d).days <= jours_reference:
                recettes_recentes.add(h.get("recette_id"))
    
    # Compter les répétitions
    repetitions = sum(1 for r in recettes_selectionnees if r.get("id") in recettes_recentes)
    
    # Score
    ratio_nouveau = (len(recettes_selectionnees) - repetitions) / len(recettes_selectionnees)
    
    return round(ratio_nouveau * 100, 1)


def get_least_prepared_recipes(
    recettes: list[dict],
    historique: list[dict],
    limit: int = 5
) -> list[dict]:
    """
    Retourne les recettes les moins préparées (pour découverte).
    
    Args:
        recettes: Pool de recettes disponibles
        historique: Historique des préparations
        limit: Nombre de résultats
        
    Returns:
        Liste des recettes rarement préparées
    """
    preparation_count = Counter(h.get("recette_id") for h in historique)
    
    scored = []
    for r in recettes:
        rid = r.get("id")
        count = preparation_count.get(rid, 0)
        scored.append((r, count))
    
    # Trier par nombre de préparations (croissant)
    scored.sort(key=lambda x: x[1])
    
    return [r for r, _ in scored[:limit]]


# ═══════════════════════════════════════════════════════════
# FORMATAGE ET AFFICHAGE
# ═══════════════════════════════════════════════════════════


def format_suggestion(recette: dict, raison: str = "") -> dict:
    """
    Formate une suggestion de recette pour l'affichage.
    
    Args:
        recette: Données de la recette
        raison: Raison de la suggestion
        
    Returns:
        Dict formaté pour l'UI
    """
    temps_total = (recette.get("temps_preparation", 0) or 0) + (recette.get("temps_cuisson", 0) or 0)
    
    return {
        "id": recette.get("id"),
        "nom": recette.get("nom", "Sans nom"),
        "raison": raison,
        "score": recette.get("score", 0),
        "temps_total": temps_total,
        "temps_display": f"{temps_total} min" if temps_total > 0 else "Non spécifié",
        "difficulte": recette.get("difficulte", "moyen"),
        "categorie": recette.get("categorie", ""),
        "est_nouvelle": recette.get("est_nouvelle", False),
        "protein_type": detect_protein_type(recette),
    }


def format_profile_summary(profil: dict) -> str:
    """
    Formate un résumé du profil culinaire.
    
    Args:
        profil: Dict avec les données du profil
        
    Returns:
        Résumé textuel
    """
    parts = []
    
    categories = profil.get("categories_preferees", [])
    if categories:
        parts.append(f"Cuisines préférées: {', '.join(categories[:3])}")
    
    ingredients = profil.get("ingredients_frequents", [])
    if ingredients:
        parts.append(f"Ingrédients favoris: {', '.join(ingredients[:5])}")
    
    temps = profil.get("temps_moyen_minutes", 0)
    if temps:
        parts.append(f"Temps moyen de préparation: {temps} min")
    
    nb_favorites = len(profil.get("recettes_favorites", []))
    if nb_favorites:
        parts.append(f"{nb_favorites} recettes favorites")
    
    return ". ".join(parts) if parts else "Profil en cours de construction"


def filter_by_constraints(
    recettes: list[dict],
    contraintes: list[str]
) -> list[dict]:
    """
    Filtre les recettes selon les contraintes alimentaires.
    
    Args:
        recettes: Liste de recettes
        contraintes: Liste de contraintes (vegetarien, sans gluten, etc.)
        
    Returns:
        Liste filtrée
    """
    if not contraintes:
        return recettes
    
    contraintes_lower = [c.lower() for c in contraintes]
    filtered = []
    
    for r in recettes:
        keep = True
        
        if "vegetarien" in contraintes_lower or "végétarien" in contraintes_lower:
            if not r.get("est_vegetarien", False):
                protein = detect_protein_type(r)
                if protein not in ["vegetarien", "autre"]:
                    keep = False
        
        if "vegan" in contraintes_lower or "végétalien" in contraintes_lower:
            if not r.get("est_vegan", False):
                keep = False
        
        if "sans gluten" in contraintes_lower:
            if r.get("contient_gluten", False):
                keep = False
        
        if "sans lactose" in contraintes_lower:
            if r.get("contient_lactose", False):
                keep = False
        
        if keep:
            filtered.append(r)
    
    return filtered
