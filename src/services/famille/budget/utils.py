"""
Fonctions utilitaires pures pour le service budget.

Ces fonctions ne dépendent pas de la base de données et sont testables unitairement.
"""

from datetime import date as date_type
from typing import Any

from src.services.famille.budget import (
    BudgetMensuel,
    CategorieDepense,
    Depense,
    FrequenceRecurrence,
    PrevisionDepense,
    ResumeFinancier,
)

# ═══════════════════════════════════════════════════════════
# CONVERSION DB → PYDANTIC
# ═══════════════════════════════════════════════════════════


def db_entry_to_depense(entry: Any) -> Depense:
    """
    Convertit une entrée BudgetFamille de la DB en objet Depense.

    Args:
        entry: Objet SQLAlchemy BudgetFamille

    Returns:
        Objet Depense Pydantic
    """
    # Déterminer la catégorie
    try:
        categorie = CategorieDepense(entry.categorie)
    except ValueError:
        categorie = CategorieDepense.AUTRE

    # Déterminer la fréquence
    try:
        frequence = (
            FrequenceRecurrence(entry.frequence_recurrence)
            if entry.frequence_recurrence
            else FrequenceRecurrence.PONCTUEL
        )
    except ValueError:
        frequence = FrequenceRecurrence.PONCTUEL

    return Depense(
        id=entry.id,
        date=entry.date,
        montant=float(entry.montant) if entry.montant else 0.0,
        categorie=categorie,
        description=entry.description or "",
        magasin=getattr(entry, "magasin", "") or "",
        est_recurrente=getattr(entry, "est_recurrent", False) or False,
        frequence=frequence,
    )


def db_entries_to_depenses(entries: list[Any]) -> list[Depense]:
    """
    Convertit une liste d'entrées DB en liste de Depense.

    Args:
        entries: Liste d'objets SQLAlchemy

    Returns:
        Liste d'objets Depense
    """
    return [db_entry_to_depense(e) for e in entries]


# ═══════════════════════════════════════════════════════════
# CALCULS STATISTIQUES
# ═══════════════════════════════════════════════════════════


def calculer_moyenne_ponderee(valeurs: list[float], poids: list[float] | None = None) -> float:
    """
    Calcule la moyenne pondérée d'une liste de valeurs.

    Args:
        valeurs: Liste de valeurs numériques
        poids: Liste de poids (optionnel, défaut: poids croissants)

    Returns:
        Moyenne pondérée
    """
    if not valeurs:
        return 0.0

    if poids is None:
        # Poids croissants par défaut (plus récent = plus de poids)
        poids = [1.0 + i * 0.2 for i in range(len(valeurs))]

    # S'assurer que les listes ont la même longueur
    poids = poids[: len(valeurs)]

    somme_poids = sum(poids)
    if somme_poids == 0:
        return 0.0

    return sum(v * p for v, p in zip(valeurs, poids, strict=False)) / somme_poids


def calculer_tendance(valeurs: list[float]) -> float:
    """
    Calcule la tendance (croissance/décroissance) d'une série.

    Args:
        valeurs: Liste de valeurs chronologiques

    Returns:
        Valeur de tendance (positif = croissance, négatif = décroissance)
    """
    if len(valeurs) < 2:
        return 0.0

    return (valeurs[-1] - valeurs[0]) / len(valeurs)


def calculer_variance(valeurs: list[float], moyenne: float | None = None) -> float:
    """
    Calcule la variance d'une liste de valeurs.

    Args:
        valeurs: Liste de valeurs
        moyenne: Moyenne précalculée (optionnel)

    Returns:
        Variance
    """
    if len(valeurs) < 2:
        return 0.0

    if moyenne is None:
        moyenne = sum(valeurs) / len(valeurs)

    return sum((v - moyenne) ** 2 for v in valeurs) / len(valeurs)


def calculer_confiance_prevision(valeurs: list[float], moyenne: float) -> float:
    """
    Calcule un score de confiance pour une prévision.

    Basé sur la variance des données historiques.

    Args:
        valeurs: Valeurs historiques
        moyenne: Moyenne utilisée pour la prévision

    Returns:
        Score de confiance entre 0 et 1
    """
    if len(valeurs) < 3:
        return 0.5

    variance = calculer_variance(valeurs, moyenne)

    # Confiance basée sur le coefficient de variation
    # Plus la variance est faible par rapport à la moyenne, plus on est confiant
    confiance = max(0, 1 - (variance / (moyenne**2 + 1)))

    return round(min(1.0, confiance), 2)


def generer_prevision_categorie(
    categorie: CategorieDepense,
    valeurs_historiques: list[float],
) -> PrevisionDepense | None:
    """
    Génère une prévision pour une catégorie à partir de l'historique.

    Args:
        categorie: Catégorie de dépense
        valeurs_historiques: Historique des dépenses

    Returns:
        Prévision ou None si pas assez de données
    """
    if not valeurs_historiques or all(v == 0 for v in valeurs_historiques):
        return None

    moyenne = calculer_moyenne_ponderee(valeurs_historiques)
    tendance = calculer_tendance(valeurs_historiques)
    confiance = calculer_confiance_prevision(valeurs_historiques, moyenne)

    montant_prevu = max(0, moyenne + tendance)

    return PrevisionDepense(
        categorie=categorie,
        montant_prevu=round(montant_prevu, 2),
        confiance=confiance,
        base_calcul=f"Moyenne pondérée sur {len(valeurs_historiques)} mois",
    )


# ═══════════════════════════════════════════════════════════
# CALCULS DE BUDGET
# ═══════════════════════════════════════════════════════════


def calculer_pourcentage_budget(depense: float, budget: float) -> float:
    """
    Calcule le pourcentage du budget utilisé.

    Args:
        depense: Montant dépensé
        budget: Budget prévu

    Returns:
        Pourcentage (plafonné à 999%)
    """
    if budget <= 0:
        return 0.0

    return min((depense / budget) * 100, 999.0)


def calculer_reste_disponible(budget: float, depense: float) -> float:
    """
    Calcule le reste disponible sur un budget.

    Args:
        budget: Budget prévu
        depense: Montant déjà dépensé

    Returns:
        Montant restant (minimum 0)
    """
    return max(0.0, budget - depense)


def est_budget_depasse(depense: float, budget: float) -> bool:
    """
    Vérifie si un budget est dépassé.

    Args:
        depense: Montant dépensé
        budget: Budget prévu

    Returns:
        True si dépassé
    """
    return depense > budget


def est_budget_a_risque(depense: float, budget: float, seuil: float = 80.0) -> bool:
    """
    Vérifie si un budget est à risque de dépassement.

    Args:
        depense: Montant dépensé
        budget: Budget prévu
        seuil: Seuil de pourcentage pour considérer à risque

    Returns:
        True si à risque
    """
    if budget <= 0:
        return False

    pourcentage = (depense / budget) * 100
    return seuil <= pourcentage < 100


# ═══════════════════════════════════════════════════════════
# AGRÉGATION DES DÉPENSES
# ═══════════════════════════════════════════════════════════


def agreger_depenses_par_categorie(depenses: list[Depense]) -> dict[CategorieDepense, float]:
    """
    Agrège les dépenses par catégorie.

    Args:
        depenses: Liste de dépenses

    Returns:
        Dictionnaire catégorie → total
    """
    totaux: dict[CategorieDepense, float] = {}

    for dep in depenses:
        totaux[dep.categorie] = totaux.get(dep.categorie, 0) + dep.montant

    return totaux


def calculer_total_depenses(depenses: list[Depense]) -> float:
    """
    Calcule le total des dépenses.

    Args:
        depenses: Liste de dépenses

    Returns:
        Total
    """
    return sum(dep.montant for dep in depenses)


def filtrer_depenses_par_categorie(
    depenses: list[Depense],
    categorie: CategorieDepense,
) -> list[Depense]:
    """
    Filtre les dépenses par catégorie.

    Args:
        depenses: Liste de dépenses
        categorie: Catégorie à filtrer

    Returns:
        Dépenses filtrées
    """
    return [d for d in depenses if d.categorie == categorie]


def filtrer_depenses_par_periode(
    depenses: list[Depense],
    date_debut: date_type,
    date_fin: date_type,
) -> list[Depense]:
    """
    Filtre les dépenses par période.

    Args:
        depenses: Liste de dépenses
        date_debut: Date de début (incluse)
        date_fin: Date de fin (incluse)

    Returns:
        Dépenses filtrées
    """
    return [d for d in depenses if date_debut <= d.date <= date_fin]


# ═══════════════════════════════════════════════════════════
# CONSTRUCTION DE RÉSUMÉS
# ═══════════════════════════════════════════════════════════


def construire_resume_financier(
    mois: int,
    annee: int,
    depenses: list[Depense],
    budgets: dict[CategorieDepense, float],
    depenses_mois_precedent: list[Depense] | None = None,
) -> ResumeFinancier:
    """
    Construit un résumé financier mensuel.

    Args:
        mois: Mois du résumé
        annee: Année du résumé
        depenses: Dépenses du mois
        budgets: Budgets par catégorie
        depenses_mois_precedent: Dépenses du mois précédent (optionnel)

    Returns:
        Résumé financier
    """
    # Totaux
    total_depenses = calculer_total_depenses(depenses)
    total_budget = sum(budgets.values())

    # Par catégorie
    depenses_par_cat = agreger_depenses_par_categorie(depenses)

    # Construire les budgets mensuels
    budgets_mensuels: dict[str, BudgetMensuel] = {}
    categories_depassees = []
    categories_a_risque = []

    for cat, budget_montant in budgets.items():
        depense_cat = depenses_par_cat.get(cat, 0)

        budget = BudgetMensuel(
            mois=mois,
            annee=annee,
            categorie=cat,
            budget_prevu=budget_montant,
            depense_reelle=depense_cat,
        )

        budgets_mensuels[cat.value] = budget

        if est_budget_depasse(depense_cat, budget_montant):
            categories_depassees.append(cat.value)
        elif est_budget_a_risque(depense_cat, budget_montant):
            categories_a_risque.append(cat.value)

    # Variation vs mois précédent
    variation = 0.0
    if depenses_mois_precedent:
        total_prec = calculer_total_depenses(depenses_mois_precedent)
        if total_prec > 0:
            variation = ((total_depenses - total_prec) / total_prec) * 100

    return ResumeFinancier(
        mois=mois,
        annee=annee,
        total_depenses=total_depenses,
        total_budget=total_budget,
        depenses_par_categorie={k.value: v for k, v in depenses_par_cat.items()},
        budgets_par_categorie=budgets_mensuels,
        variation_vs_mois_precedent=variation,
        categories_depassees=categories_depassees,
        categories_a_risque=categories_a_risque,
    )


# ═══════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════


def valider_montant(montant: float | str) -> float:
    """
    Valide et convertit un montant.

    Args:
        montant: Montant à valider

    Returns:
        Montant comme float

    Raises:
        ValueError: Si le montant n'est pas valide
    """
    try:
        result = float(montant)
        return result
    except (TypeError, ValueError):
        raise ValueError(f"Montant invalide: {montant}") from None


def valider_mois(mois: int) -> int:
    """
    Valide un numéro de mois.

    Args:
        mois: Numéro de mois (1-12)

    Returns:
        Mois validé

    Raises:
        ValueError: Si le mois n'est pas valide
    """
    if not 1 <= mois <= 12:
        raise ValueError(f"Mois invalide: {mois} (doit être entre 1 et 12)")
    return mois


def valider_annee(annee: int) -> int:
    """
    Valide une année.

    Args:
        annee: Année

    Returns:
        Année validée

    Raises:
        ValueError: Si l'année n'est pas valide
    """
    if not 1900 <= annee <= 2100:
        raise ValueError(f"Année invalide: {annee}")
    return annee
