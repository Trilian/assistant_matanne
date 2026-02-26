"""
Score d'efficacité Batch Cooking — Gamification.

Calcule un score d'efficacité pour une session de batch cooking
en évaluant la diversité, le temps, l'utilisation des restes, etc.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


@dataclass
class ScoreEfficacite:
    """Score d'efficacité d'une session batch cooking."""

    score_total: float = 0.0  # 0-100
    niveau: str = ""  # Débutant, Apprenti, Confirmé, Expert, Maître
    etoiles: int = 0  # 1-5

    # Sous-scores (chacun 0-20)
    score_diversite: float = 0.0  # Variété des recettes
    score_temps: float = 0.0  # Efficacité du temps
    score_portions: float = 0.0  # Nb portions produites
    score_economie: float = 0.0  # Économie vs plats individuels
    score_anti_gaspi: float = 0.0  # Utilisation d'ingrédients à consommer

    details: dict = field(default_factory=dict)
    badges: list[str] = field(default_factory=list)
    conseils: list[str] = field(default_factory=list)


NIVEAUX = {
    (0, 20): ("Débutant 🌱", 1),
    (20, 40): ("Apprenti 🍳", 2),
    (40, 60): ("Confirmé 👨‍🍳", 3),
    (60, 80): ("Expert ⭐", 4),
    (80, 101): ("Maître Chef 🏆", 5),
}

BADGES_DISPONIBLES = {
    "marathon": ("🏃 Marathon", "Plus de 3h de batch cooking"),
    "express": ("⚡ Express", "Batch cooking en moins d'1h"),
    "mega_portions": ("📦 Méga Stock", "Plus de 20 portions produites"),
    "diversite_max": ("🌈 Arc-en-ciel", "5+ recettes différentes"),
    "zero_waste": ("♻️ Zéro Déchet", "100% des ingrédients utilisés"),
    "anti_gaspi": ("🦸 Anti-Gaspi", "3+ ingrédients urgents sauvés"),
    "freezer_king": ("🧊 Roi du Congélo", "10+ portions congelées"),
    "rapide": ("🚀 Speed Cook", "Temps/portion < 5 min"),
    "economiste": ("💰 Économiste", "Économie > 30% vs plats individuels"),
    "regulier": ("📅 Régulier", "Batch cooking hebdomadaire sur 4 semaines"),
}


# ═══════════════════════════════════════════════════════════
# FONCTIONS
# ═══════════════════════════════════════════════════════════


def calculer_score_efficacite(
    nb_recettes: int,
    nb_portions_total: int,
    temps_total_min: int,
    nb_ingredients_urgents_utilises: int = 0,
    nb_ingredients_total: int = 0,
    nb_ingredients_utilises: int = 0,
    cout_batch: float = 0.0,
    cout_individuel_estime: float = 0.0,
) -> ScoreEfficacite:
    """
    Calcule le score d'efficacité d'une session de batch cooking.

    Args:
        nb_recettes: Nombre de recettes préparées
        nb_portions_total: Total de portions produites
        temps_total_min: Temps total en minutes
        nb_ingredients_urgents_utilises: Ingrédients "à consommer vite" utilisés
        nb_ingredients_total: Total d'ingrédients disponibles
        nb_ingredients_utilises: Ingrédients effectivement utilisés
        cout_batch: Coût total du batch cooking
        cout_individuel_estime: Coût estimé si préparé individuellement

    Returns:
        ScoreEfficacite
    """
    # 1. Score diversité (0-20)
    if nb_recettes >= 5:
        score_div = 20
    elif nb_recettes >= 3:
        score_div = 15
    elif nb_recettes >= 2:
        score_div = 10
    else:
        score_div = 5

    # 2. Score temps (0-20) — temps par portion
    if nb_portions_total > 0 and temps_total_min > 0:
        temps_par_portion = temps_total_min / nb_portions_total
        if temps_par_portion <= 5:
            score_temps = 20
        elif temps_par_portion <= 10:
            score_temps = 15
        elif temps_par_portion <= 15:
            score_temps = 10
        else:
            score_temps = 5
    else:
        score_temps = 0

    # 3. Score portions (0-20)
    if nb_portions_total >= 20:
        score_portions = 20
    elif nb_portions_total >= 15:
        score_portions = 16
    elif nb_portions_total >= 10:
        score_portions = 12
    elif nb_portions_total >= 5:
        score_portions = 8
    else:
        score_portions = 4

    # 4. Score économie (0-20)
    if cout_individuel_estime > 0 and cout_batch > 0:
        economie_pct = (1 - cout_batch / cout_individuel_estime) * 100
        if economie_pct >= 50:
            score_eco = 20
        elif economie_pct >= 30:
            score_eco = 15
        elif economie_pct >= 15:
            score_eco = 10
        else:
            score_eco = 5
    else:
        score_eco = 10  # Neutre si pas d'info

    # 5. Score anti-gaspi (0-20)
    if nb_ingredients_urgents_utilises >= 5:
        score_gaspi = 20
    elif nb_ingredients_urgents_utilises >= 3:
        score_gaspi = 15
    elif nb_ingredients_urgents_utilises >= 1:
        score_gaspi = 10
    else:
        # Bonus si bon taux d'utilisation
        if nb_ingredients_total > 0:
            taux = nb_ingredients_utilises / nb_ingredients_total
            score_gaspi = int(taux * 15)
        else:
            score_gaspi = 5

    score_total = score_div + score_temps + score_portions + score_eco + score_gaspi

    # Déterminer niveau et étoiles
    niveau = "Débutant 🌱"
    etoiles = 1
    for (low, high), (niv, stars) in NIVEAUX.items():
        if low <= score_total < high:
            niveau = niv
            etoiles = stars
            break

    # Badges
    badges = []
    if temps_total_min > 180:
        badges.append(BADGES_DISPONIBLES["marathon"][0])
    if temps_total_min and temps_total_min < 60:
        badges.append(BADGES_DISPONIBLES["express"][0])
    if nb_portions_total >= 20:
        badges.append(BADGES_DISPONIBLES["mega_portions"][0])
    if nb_recettes >= 5:
        badges.append(BADGES_DISPONIBLES["diversite_max"][0])
    if nb_ingredients_total > 0 and nb_ingredients_utilises >= nb_ingredients_total:
        badges.append(BADGES_DISPONIBLES["zero_waste"][0])
    if nb_ingredients_urgents_utilises >= 3:
        badges.append(BADGES_DISPONIBLES["anti_gaspi"][0])
    if nb_portions_total > 0 and temps_total_min / nb_portions_total < 5:
        badges.append(BADGES_DISPONIBLES["rapide"][0])

    # Conseils personnalisés
    conseils = []
    if score_div < 10:
        conseils.append("🌈 Essayez de varier : ajoutez 1-2 recettes différentes la prochaine fois")
    if score_temps < 10:
        conseils.append("⏱️ Optimisez le temps : lancez les cuissons longues en premier")
    if score_portions < 10:
        conseils.append("📦 Doublez les quantités pour constituer un stock congélateur")
    if score_gaspi < 10:
        conseils.append(
            "♻️ Vérifiez l'inventaire avant de planifier — utilisez les urgents en priorité"
        )
    if not badges:
        conseils.append("🎯 Continuez ainsi pour débloquer votre premier badge !")

    return ScoreEfficacite(
        score_total=round(score_total, 1),
        niveau=niveau,
        etoiles=etoiles,
        score_diversite=score_div,
        score_temps=score_temps,
        score_portions=score_portions,
        score_economie=score_eco,
        score_anti_gaspi=score_gaspi,
        badges=badges,
        conseils=conseils,
        details={
            "temps_par_portion": round(temps_total_min / max(nb_portions_total, 1), 1),
            "economie_pct": round((1 - cout_batch / max(cout_individuel_estime, 0.01)) * 100, 1)
            if cout_individuel_estime
            else 0,
        },
    )


def generer_resume_session(score: ScoreEfficacite) -> str:
    """Génère un résumé textuel game-ified de la session."""
    lines = [
        f"🏆 Score Batch Cooking : {score.score_total}/100",
        f"{'⭐' * score.etoiles} {score.niveau}",
        "",
        "📊 Détails :",
        f"  🌈 Diversité : {score.score_diversite}/20",
        f"  ⏱️ Temps : {score.score_temps}/20",
        f"  📦 Portions : {score.score_portions}/20",
        f"  💰 Économie : {score.score_economie}/20",
        f"  ♻️ Anti-gaspi : {score.score_anti_gaspi}/20",
    ]

    if score.badges:
        lines.extend(["", "🎖️ Badges débloqués :"])
        lines.extend(f"  {b}" for b in score.badges)

    if score.conseils:
        lines.extend(["", "💡 Conseils :"])
        lines.extend(f"  {c}" for c in score.conseils)

    return "\n".join(lines)


__all__ = [
    "ScoreEfficacite",
    "BADGES_DISPONIBLES",
    "calculer_score_efficacite",
    "generer_resume_session",
]
