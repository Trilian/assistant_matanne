"""Utilitaires partages de calcul de seuils budgetaires."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EtatSeuilBudget:
    """Etat calcule d'un budget par rapport a ses seuils."""

    pourcentage: float
    seuils_franchis: list[int]
    niveau: str


def calculer_pourcentage_utilisation(cumul: float, limite: float) -> float:
    """Calcule le pourcentage d'utilisation d'un budget."""
    if limite <= 0:
        return 0.0
    return max(0.0, (cumul / limite) * 100)


def evaluer_seuils_budget(
    cumul: float,
    limite: float,
    seuils: tuple[int, ...] = (50, 75, 90, 100),
) -> EtatSeuilBudget:
    """Evalue les seuils franchis et retourne un niveau lisible."""
    pourcentage = calculer_pourcentage_utilisation(cumul, limite)
    seuils_franchis = [s for s in seuils if pourcentage >= s]

    if pourcentage >= 100:
        niveau = "bloque"
    elif pourcentage >= 90:
        niveau = "danger"
    elif pourcentage >= 75:
        niveau = "attention"
    elif pourcentage >= 50:
        niveau = "info"
    else:
        niveau = "normal"

    return EtatSeuilBudget(
        pourcentage=round(pourcentage, 2),
        seuils_franchis=seuils_franchis,
        niveau=niveau,
    )
