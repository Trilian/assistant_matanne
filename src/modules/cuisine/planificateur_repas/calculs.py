"""
Calculs de scores, filtrage, suggestions et validation equilibre du Planificateur de Repas

Logique pure de scoring et equilibrage nutritionnel.
"""

import logging
from typing import Any

from src.modules.cuisine.schemas import FeedbackRecette, PreferencesUtilisateur

from .helpers import (
    PROTEINES,
    TEMPS_CATEGORIES,
    PlanningSemaine,
    RecetteSuggestion,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# APPRENTISSAGE DES GOÛTS
# ═══════════════════════════════════════════════════════════


def calculer_score_recette(
    recette: Any,
    preferences: PreferencesUtilisateur,
    feedbacks: list[FeedbackRecette],
    equilibre_actuel: dict[str, int],
    stock_disponible: list[str],
) -> tuple[float, str]:
    """
    Calcule un score de pertinence pour une recette.

    Args:
        recette: Objet recette (SQLAlchemy ou dict)
        preferences: Preferences utilisateur
        feedbacks: Historique des feedbacks
        equilibre_actuel: Équilibre de la semaine en cours
        stock_disponible: Ingredients en stock

    Returns:
        (score 0-100, raison principale)
    """
    score = 50.0  # Score de base
    raison = "Suggestion standard"

    # Nom de la recette
    nom = recette.nom if hasattr(recette, "nom") else recette.get("nom", "")
    recette_id = recette.id if hasattr(recette, "id") else recette.get("id", 0)

    # 1. Verifier les exclusions (eliminatoire)
    for exclu in preferences.aliments_exclus:
        if exclu.lower() in nom.lower():
            return 0.0, f"Contient {exclu} (exclu)"

    # 2. Bonus pour les favoris (+20)
    for favori in preferences.aliments_favoris:
        if favori.lower() in nom.lower():
            score += 20
            raison = f"Contient {favori} (favori)"

    # 3. Feedback historique (+/- 15)
    for fb in feedbacks:
        if fb.recette_id == recette_id:
            score += fb.score * 15
            if fb.feedback == "like":
                raison = "Vous avez aime cette recette"
            elif fb.feedback == "dislike":
                raison = "Vous n'avez pas aime cette recette"

    # 4. Équilibre de la semaine (+10 si manquant)
    categorie = None
    if hasattr(recette, "type_proteine"):
        prot = recette.type_proteine
        if prot in PROTEINES:
            categorie = PROTEINES[prot]["categorie"]

    if categorie:
        objectif = {
            "poisson": preferences.poisson_par_semaine,
            "vegetarien": preferences.vegetarien_par_semaine,
            "viande_rouge": preferences.viande_rouge_max,
        }.get(categorie, 2)

        actuel = equilibre_actuel.get(categorie, 0)

        if actuel < objectif:
            score += 10
            raison = f"Aide à l'equilibre ({categorie})"
        elif categorie == "viande_rouge" and actuel >= objectif:
            score -= 15
            raison = "Dejà assez de viande rouge cette semaine"

    # 5. Stock disponible (+15 si ingredients en stock)
    nb_en_stock = 0
    if hasattr(recette, "ingredients") and recette.ingredients:
        for ing in recette.ingredients:
            ing_nom = ing.nom if hasattr(ing, "nom") else ing.get("nom", "")
            if any(s.lower() in ing_nom.lower() for s in stock_disponible):
                nb_en_stock += 1

        if nb_en_stock >= 3:
            score += 15
            raison = f"Utilise {nb_en_stock} ingredients de votre stock"

    # 6. Temps de preparation
    temps_total = 0
    if hasattr(recette, "temps_preparation"):
        temps_total = recette.temps_preparation + (recette.temps_cuisson or 0)

    temps_max = TEMPS_CATEGORIES.get(preferences.temps_semaine, {}).get("max_minutes", 40)
    if temps_total > temps_max:
        score -= 10
        raison = f"Temps de preparation long ({temps_total} min)"

    # 7. Compatible Jules (+5)
    if preferences.jules_present:
        if hasattr(recette, "compatible_bebe") and recette.compatible_bebe:
            score += 5
        elif hasattr(recette, "instructions_bebe") and recette.instructions_bebe:
            score += 5

    # 8. Compatible batch cooking (+5)
    if hasattr(recette, "compatible_batch") and recette.compatible_batch:
        score += 5

    # Normaliser entre 0 et 100
    score = max(0, min(100, score))

    return score, raison


def filtrer_recettes_eligibles(
    recettes: list[Any],
    preferences: PreferencesUtilisateur,
    type_repas: str = "dejeuner",
) -> list[Any]:
    """
    Filtre les recettes eligibles selon les contraintes.

    Args:
        recettes: Liste des recettes
        preferences: Preferences utilisateur
        type_repas: Type de repas (dejeuner, dîner, goûter)

    Returns:
        Liste filtree
    """
    eligibles = []

    for recette in recettes:
        nom = recette.nom if hasattr(recette, "nom") else recette.get("nom", "")

        # Verifier exclusions
        exclu = False
        for aliment_exclu in preferences.aliments_exclus:
            if aliment_exclu.lower() in nom.lower():
                exclu = True
                break

        if exclu:
            continue

        # Verifier type de repas
        if hasattr(recette, "type_repas"):
            if recette.type_repas:
                # Gerer les types multiples separes par virgule
                types_valides = [t.strip() for t in recette.type_repas.split(",")]
                if type_repas not in types_valides:
                    continue

        eligibles.append(recette)

    return eligibles


def generer_suggestions_alternatives(
    recette_actuelle: RecetteSuggestion,
    toutes_recettes: list[Any],
    preferences: PreferencesUtilisateur,
    feedbacks: list[FeedbackRecette],
    equilibre_actuel: dict[str, int],
    stock: list[str],
    nb_alternatives: int = 3,
) -> list[RecetteSuggestion]:
    """
    Genère des alternatives à une recette.

    Returns:
        Liste de suggestions alternatives triees par score
    """
    alternatives = []

    # Filtrer les recettes similaires (même type de repas)
    eligibles = filtrer_recettes_eligibles(toutes_recettes, preferences)

    for recette in eligibles:
        recette_id = recette.id if hasattr(recette, "id") else recette.get("id", 0)

        # Ignorer la recette actuelle
        if recette_actuelle and recette_id == recette_actuelle.id:
            continue

        score, raison = calculer_score_recette(
            recette, preferences, feedbacks, equilibre_actuel, stock
        )

        if score > 30:  # Seuil minimum
            suggestion = RecetteSuggestion(
                id=recette_id,
                nom=recette.nom if hasattr(recette, "nom") else recette.get("nom", ""),
                description=recette.description if hasattr(recette, "description") else "",
                temps_preparation=recette.temps_preparation
                if hasattr(recette, "temps_preparation")
                else 30,
                temps_cuisson=recette.temps_cuisson if hasattr(recette, "temps_cuisson") else 0,
                portions=recette.portions if hasattr(recette, "portions") else 4,
                difficulte=recette.difficulte if hasattr(recette, "difficulte") else "moyen",
                score_match=score,
                raison_suggestion=raison,
                instructions_jules=recette.instructions_bebe
                if hasattr(recette, "instructions_bebe")
                else None,
                compatible_batch=recette.compatible_batch
                if hasattr(recette, "compatible_batch")
                else False,
            )
            alternatives.append(suggestion)

    # Trier par score et limiter
    alternatives.sort(key=lambda x: x.score_match, reverse=True)

    return alternatives[:nb_alternatives]


# ═══════════════════════════════════════════════════════════
# VALIDATION ET ÉQUILIBRE
# ═══════════════════════════════════════════════════════════


def valider_equilibre_semaine(
    planning: PlanningSemaine,
    preferences: PreferencesUtilisateur,
) -> tuple[bool, list[str]]:
    """
    Valide l'equilibre nutritionnel d'une semaine.

    Returns:
        (est_valide, liste_alertes)
    """
    alertes = []
    equilibre = planning.get_equilibre()

    # Verifier poisson
    if equilibre["poisson"] < preferences.poisson_par_semaine:
        alertes.append(
            f"⚠️ Seulement {equilibre['poisson']} repas poisson (objectif: {preferences.poisson_par_semaine})"
        )

    # Verifier vegetarien
    if equilibre["vegetarien"] < preferences.vegetarien_par_semaine:
        alertes.append(
            f"⚠️ Seulement {equilibre['vegetarien']} repas vegetarien (objectif: {preferences.vegetarien_par_semaine})"
        )

    # Verifier viande rouge
    if equilibre["viande_rouge"] > preferences.viande_rouge_max:
        alertes.append(
            f"⚠️ Trop de viande rouge: {equilibre['viande_rouge']} (max: {preferences.viande_rouge_max})"
        )

    # Verifier repas planifies
    if planning.nb_repas_planifies < 10:  # Au moins 10 repas sur 14 possibles
        alertes.append(f"⚠️ Seulement {planning.nb_repas_planifies} repas planifies sur 14")

    est_valide = len(alertes) == 0

    return est_valide, alertes


def suggerer_ajustements_equilibre(
    equilibre_actuel: dict[str, int],
    preferences: PreferencesUtilisateur,
) -> list[str]:
    """
    Suggère des ajustements pour atteindre l'equilibre.

    Returns:
        Liste de suggestions
    """
    suggestions = []

    if equilibre_actuel["poisson"] < preferences.poisson_par_semaine:
        manque = preferences.poisson_par_semaine - equilibre_actuel["poisson"]
        suggestions.append(f"Ajouter {manque} repas poisson (saumon, cabillaud, sardines...)")

    if equilibre_actuel["vegetarien"] < preferences.vegetarien_par_semaine:
        manque = preferences.vegetarien_par_semaine - equilibre_actuel["vegetarien"]
        suggestions.append(
            f"Ajouter {manque} repas vegetarien (omelette, gratin legumes, curry legumineuses...)"
        )

    if equilibre_actuel["viande_rouge"] > preferences.viande_rouge_max:
        exces = equilibre_actuel["viande_rouge"] - preferences.viande_rouge_max
        suggestions.append(f"Remplacer {exces} repas viande rouge par du poulet ou poisson")

    return suggestions
