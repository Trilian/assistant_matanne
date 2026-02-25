"""
Service de Gamification Universel — Points, badges et streaks multi-modules.

Étend le concept de gamification existant dans entretien_gamification_mixin.py
à tous les modules: recettes, courses, routines, activités, planification.

Usage:
    from src.services.core.gamification import (
        get_gamification_service,
        BADGES_GLOBAUX,
    )

    service = get_gamification_service()

    # Enregistrer une action
    service.enregistrer_action("recette_ajoutee")

    # Obtenir les stats gamification
    stats = service.obtenir_stats()

    # Vérifier les badges débloqués
    badges = service.obtenir_badges()
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import streamlit as st

from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


@dataclass
class BadgeDefinition:
    """Définition d'un badge gamification."""

    id: str
    nom: str
    emoji: str
    description: str
    categorie: str  # cuisine, famille, maison, planning, global
    condition_cle: str  # Clé dans les stats à vérifier
    condition_seuil: int | float  # Seuil pour débloquer


@dataclass
class StatsGamification:
    """Statistiques gamification d'un utilisateur."""

    # Compteurs par module
    recettes_ajoutees: int = 0
    recettes_cuisinees: int = 0
    courses_completees: int = 0
    plannings_crees: int = 0
    activites_jules: int = 0
    activites_famille: int = 0
    taches_entretien: int = 0
    routines_completees: int = 0
    modules_utilises: int = 0

    # Streaks
    streak_cuisine: int = 0
    streak_entretien: int = 0
    streak_routines: int = 0

    # Score global
    points_total: int = 0
    niveau: int = 1

    # Badges débloqués (liste d'IDs)
    badges_debloques: list[str] = field(default_factory=list)
    derniere_activite: datetime | None = None


# ═══════════════════════════════════════════════════════════
# BADGES
# ═══════════════════════════════════════════════════════════

BADGES_GLOBAUX: list[BadgeDefinition] = [
    # Cuisine
    BadgeDefinition(
        "chef_debutant",
        "Chef Débutant",
        "👨‍🍳",
        "Ajouter 5 recettes",
        "cuisine",
        "recettes_ajoutees",
        5,
    ),
    BadgeDefinition(
        "chef_confirme",
        "Chef Confirmé",
        "🧑‍🍳",
        "Ajouter 25 recettes",
        "cuisine",
        "recettes_ajoutees",
        25,
    ),
    BadgeDefinition(
        "chef_etoile",
        "Chef Étoilé",
        "⭐",
        "Ajouter 100 recettes",
        "cuisine",
        "recettes_ajoutees",
        100,
    ),
    BadgeDefinition(
        "cuisinier_assidu",
        "Cuisinier Assidu",
        "🍳",
        "Cuisiner 50 recettes",
        "cuisine",
        "recettes_cuisinees",
        50,
    ),
    BadgeDefinition(
        "batch_master",
        "Batch Master",
        "🏭",
        "10 sessions batch cooking",
        "cuisine",
        "plannings_crees",
        10,
    ),
    # Courses
    BadgeDefinition(
        "coursier_express",
        "Coursier Express",
        "🛒",
        "50 listes complétées",
        "cuisine",
        "courses_completees",
        50,
    ),
    # Famille
    BadgeDefinition(
        "parent_actif",
        "Parent Actif",
        "👶",
        "20 activités avec Jules",
        "famille",
        "activites_jules",
        20,
    ),
    BadgeDefinition(
        "famille_unie",
        "Famille Unie",
        "👨‍👩‍👦",
        "30 activités en famille",
        "famille",
        "activites_famille",
        30,
    ),
    BadgeDefinition(
        "routinier",
        "Routinier",
        "📅",
        "Compléter 100 routines",
        "famille",
        "routines_completees",
        100,
    ),
    # Maison
    BadgeDefinition(
        "premiere_tache",
        "Premier Pas",
        "🎯",
        "Première tâche d'entretien",
        "maison",
        "taches_entretien",
        1,
    ),
    BadgeDefinition(
        "maison_parfaite",
        "Maison Parfaite",
        "✨",
        "50 tâches d'entretien",
        "maison",
        "taches_entretien",
        50,
    ),
    BadgeDefinition(
        "streak_7_cuisine",
        "Flamme Cuisine",
        "🔥",
        "7 jours cuisine consécutifs",
        "cuisine",
        "streak_cuisine",
        7,
    ),
    BadgeDefinition(
        "streak_30_entretien",
        "Mois Parfait Entretien",
        "🏆",
        "30 jours entretien consécutifs",
        "maison",
        "streak_entretien",
        30,
    ),
    # Global
    BadgeDefinition(
        "explorateur",
        "Explorateur",
        "🧭",
        "Utiliser 5 modules différents",
        "global",
        "modules_utilises",
        5,
    ),
    BadgeDefinition(
        "assidu_global",
        "Assidu",
        "📅",
        "500 points totaux",
        "global",
        "points_total",
        500,
    ),
    BadgeDefinition(
        "expert_matanne",
        "Expert Matanne",
        "🏅",
        "2000 points totaux",
        "global",
        "points_total",
        2000,
    ),
]

# Points par action
POINTS_PAR_ACTION: dict[str, int] = {
    "recette_ajoutee": 10,
    "recette_cuisinee": 5,
    "course_completee": 8,
    "planning_cree": 15,
    "activite_jules": 10,
    "activite_famille": 10,
    "tache_entretien": 5,
    "routine_completee": 3,
    "badge_debloque": 50,
}

# Seuils de niveaux
SEUILS_NIVEAUX: list[int] = [0, 50, 150, 350, 700, 1200, 2000, 3500, 5000, 8000, 12000]

TITRES_NIVEAUX: dict[int, str] = {
    1: "Débutant",
    2: "Apprenti",
    3: "Confirmé",
    4: "Expert",
    5: "Maître",
    6: "Grand Maître",
    7: "Légende",
    8: "Mythique",
    9: "Divin",
    10: "Ultime",
}


# ═══════════════════════════════════════════════════════════
# SERVICE GAMIFICATION
# ═══════════════════════════════════════════════════════════


class ServiceGamification:
    """Service de gamification multi-modules.

    Gère les points, badges, streaks et niveaux pour tous les modules.
    Stocke les données en session_state pour persistance intra-session.
    """

    _SK_STATS = "gamification_stats"
    _SK_HISTORIQUE = "gamification_historique"

    def __init__(self) -> None:
        """Initialise le service de gamification."""
        if self._SK_STATS not in st.session_state:
            st.session_state[self._SK_STATS] = StatsGamification()
        if self._SK_HISTORIQUE not in st.session_state:
            st.session_state[self._SK_HISTORIQUE] = []

    @property
    def stats(self) -> StatsGamification:
        """Accès aux stats courantes."""
        return st.session_state[self._SK_STATS]

    def enregistrer_action(self, action: str, **kwargs: Any) -> dict[str, Any]:
        """Enregistre une action et met à jour les stats.

        Args:
            action: Type d'action (ex: 'recette_ajoutee')
            **kwargs: Métadonnées additionnelles

        Returns:
            Dict avec points gagnés et éventuels badges débloqués.
        """
        stats = self.stats
        points = POINTS_PAR_ACTION.get(action, 1)

        # Incrémenter le compteur correspondant
        compteurs_mapping = {
            "recette_ajoutee": "recettes_ajoutees",
            "recette_cuisinee": "recettes_cuisinees",
            "course_completee": "courses_completees",
            "planning_cree": "plannings_crees",
            "activite_jules": "activites_jules",
            "activite_famille": "activites_famille",
            "tache_entretien": "taches_entretien",
            "routine_completee": "routines_completees",
        }

        compteur = compteurs_mapping.get(action)
        if compteur and hasattr(stats, compteur):
            setattr(stats, compteur, getattr(stats, compteur) + 1)

        stats.points_total += points
        stats.niveau = self._calculer_niveau(stats.points_total)
        stats.derniere_activite = datetime.now()

        # Historique
        st.session_state[self._SK_HISTORIQUE].append(
            {
                "action": action,
                "points": points,
                "timestamp": datetime.now().isoformat(),
                **kwargs,
            }
        )

        # Vérifier les nouveaux badges
        nouveaux_badges = self._verifier_nouveaux_badges(stats)

        # Points bonus pour badges
        for _badge in nouveaux_badges:
            stats.points_total += POINTS_PAR_ACTION["badge_debloque"]

        result: dict[str, Any] = {
            "points_gagnes": points,
            "points_total": stats.points_total,
            "niveau": stats.niveau,
            "nouveaux_badges": nouveaux_badges,
        }

        logger.info(f"Gamification: {action} → +{points}pts (total: {stats.points_total})")
        return result

    def _calculer_niveau(self, points: int) -> int:
        """Calcule le niveau basé sur les points (progression logarithmique)."""
        for i in range(len(SEUILS_NIVEAUX) - 1, -1, -1):
            if points >= SEUILS_NIVEAUX[i]:
                return min(i + 1, 10)
        return 1

    def _verifier_nouveaux_badges(self, stats: StatsGamification) -> list[BadgeDefinition]:
        """Vérifie et retourne les badges nouvellement débloqués."""
        nouveaux: list[BadgeDefinition] = []

        for badge_def in BADGES_GLOBAUX:
            if badge_def.id in stats.badges_debloques:
                continue

            valeur = getattr(stats, badge_def.condition_cle, 0)
            if valeur >= badge_def.condition_seuil:
                stats.badges_debloques.append(badge_def.id)
                nouveaux.append(badge_def)
                logger.info(f"🏅 Badge débloqué: {badge_def.nom}")

        return nouveaux

    def obtenir_stats(self) -> StatsGamification:
        """Retourne les stats gamification courantes."""
        return self.stats

    def obtenir_badges(self) -> list[dict[str, Any]]:
        """Retourne tous les badges avec leur statut (débloqué ou non)."""
        stats = self.stats
        resultats: list[dict[str, Any]] = []

        for badge_def in BADGES_GLOBAUX:
            debloque = badge_def.id in stats.badges_debloques
            valeur_actuelle = getattr(stats, badge_def.condition_cle, 0)
            progression = min(100, int((valeur_actuelle / badge_def.condition_seuil) * 100))

            resultats.append(
                {
                    "badge": badge_def,
                    "debloque": debloque,
                    "progression": progression,
                    "valeur_actuelle": valeur_actuelle,
                }
            )

        return resultats

    def obtenir_historique(self, limit: int = 20) -> list[dict[str, Any]]:
        """Retourne l'historique des actions récentes."""
        historique: list[dict[str, Any]] = st.session_state.get(self._SK_HISTORIQUE, [])
        return list(reversed(historique[-limit:]))


@service_factory("gamification", tags={"global", "ui"})
def get_gamification_service() -> ServiceGamification:
    """Factory pour le service de gamification."""
    return ServiceGamification()


__all__ = [
    "ServiceGamification",
    "get_gamification_service",
    "StatsGamification",
    "BadgeDefinition",
    "BADGES_GLOBAUX",
    "POINTS_PAR_ACTION",
    "SEUILS_NIVEAUX",
    "TITRES_NIVEAUX",
]
