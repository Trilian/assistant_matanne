"""
Service Santé Famille - Logique métier pour objectifs, routines et stats santé.

Opérations:
- Objectifs santé actifs et progression
- Routines santé actives
- Statistiques de santé hebdomadaires
- Budget santé par période
"""

import logging
from datetime import date as date_type
from datetime import timedelta
from typing import Any, TypedDict

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.models import (
    ActiviteFamille,
    BudgetFamille,
    EntreeSante,
    ObjectifSante,
    RoutineSante,
)
from src.services.core.base import BaseService
from src.services.core.events import obtenir_bus
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class StatsSanteDict(TypedDict):
    """Structure de données pour les stats santé hebdomadaires."""

    nb_seances: int
    total_minutes: int
    total_calories: int
    energie_moyenne: float
    moral_moyen: float


class ServiceSante(BaseService[EntreeSante]):
    """Service de gestion de la santé familiale.

    Hérite de BaseService[EntreeSante] pour le CRUD générique.
    Centralise l'accès DB pour les objectifs, routines et
    statistiques de santé, éliminant les requêtes directes
    depuis la couche modules.
    """

    def __init__(self):
        super().__init__(model=EntreeSante, cache_ttl=300)

    # ═══════════════════════════════════════════════════════════
    # CRUD OVERRIDES — Émission d'événements
    # ═══════════════════════════════════════════════════════════

    def create(self, data: dict, db: Session | None = None) -> EntreeSante:
        """Crée une entrée santé et émet un événement."""
        result = super().create(data, db)
        obtenir_bus().emettre(
            "sante.modifie",
            {"entree_id": result.id, "type_donnee": "entree", "action": "creee"},
            source="sante",
        )
        return result

    def update(self, entity_id: int, data: dict, db: Session | None = None) -> EntreeSante | None:
        """Met à jour une entrée santé et émet un événement."""
        result = super().update(entity_id, data, db)
        if result:
            obtenir_bus().emettre(
                "sante.modifie",
                {"entree_id": entity_id, "type_donnee": "entree", "action": "modifiee"},
                source="sante",
            )
        return result

    def delete(self, entity_id: int, db: Session | None = None) -> bool:
        """Supprime une entrée santé et émet un événement."""
        result = super().delete(entity_id, db)
        if result:
            obtenir_bus().emettre(
                "sante.modifie",
                {"entree_id": entity_id, "type_donnee": "entree", "action": "supprimee"},
                source="sante",
            )
        return result

    # ═══════════════════════════════════════════════════════════
    # OBJECTIFS
    # ═══════════════════════════════════════════════════════════

    @staticmethod
    def calculer_progression_objectif(objective: ObjectifSante) -> float:
        """Calcule le % de progression d'un objectif santé.

        Args:
            objective: L'objectif santé (ou mock avec valeur_cible/valeur_actuelle).

        Returns:
            Pourcentage entre 0.0 et 100.0.
        """
        try:
            if not objective.valeur_cible or not objective.valeur_actuelle:
                return 0.0
            progression = (objective.valeur_actuelle / objective.valeur_cible) * 100
            return min(progression, 100.0)
        except Exception:
            return 0.0

    @avec_gestion_erreurs(default_return=[])
    @avec_cache(ttl=300)
    @avec_session_db
    def get_objectives_actifs(self, db: Session | None = None) -> list[dict[str, Any]]:
        """Récupère tous les objectifs en cours avec progression.

        Args:
            db: Session DB (injectée automatiquement).

        Returns:
            Liste de dicts avec id, titre, catégorie, progression, etc.
        """
        if db is None:
            raise ValueError("Session DB requise")

        objectives = db.query(ObjectifSante).filter_by(statut="en_cours").all()

        result = []
        for obj in objectives:
            result.append(
                {
                    "id": obj.id,
                    "titre": obj.titre,
                    "categorie": obj.categorie,
                    "progression": self.calculer_progression_objectif(obj),
                    "valeur_cible": obj.valeur_cible,
                    "valeur_actuelle": obj.valeur_actuelle,
                    "unite": obj.unite,
                    "priorite": obj.priorite,
                    "date_cible": obj.date_cible,
                    "jours_restants": (obj.date_cible - date_type.today()).days,
                }
            )

        return sorted(result, key=lambda x: x["priorite"] == "haute", reverse=True)

    # ═══════════════════════════════════════════════════════════
    # ROUTINES SANTÉ
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=[])
    @avec_cache(ttl=300)
    @avec_session_db
    def get_routines_actives(self, db: Session | None = None) -> list[dict[str, Any]]:
        """Récupère les routines de santé actives.

        Args:
            db: Session DB (injectée automatiquement).

        Returns:
            Liste de dicts décrivant chaque routine active.
        """
        if db is None:
            raise ValueError("Session DB requise")

        routines = db.query(RoutineSante).filter_by(actif=True).all()

        return [
            {
                "id": r.id,
                "nom": r.nom,
                "type": r.type_routine,
                "frequence": r.frequence,
                "duree": r.duree_minutes,
                "intensite": r.intensite,
                "calories": r.calories_brulees_estimees,
            }
            for r in routines
        ]

    # ═══════════════════════════════════════════════════════════
    # STATISTIQUES
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return={})
    @avec_cache(ttl=300)
    @avec_session_db
    def get_stats_sante_semaine(self, db: Session | None = None) -> StatsSanteDict:
        """Calcule les stats de santé pour cette semaine.

        Args:
            db: Session DB (injectée automatiquement).

        Returns:
            StatsSanteDict avec nb_seances, total_minutes, etc.
        """
        if db is None:
            raise ValueError("Session DB requise")

        debut_semaine = date_type.today() - timedelta(days=date_type.today().weekday())

        entries = db.query(EntreeSante).filter(EntreeSante.date >= debut_semaine).all()

        nb_avec_energie = len([e for e in entries if e.note_energie])
        nb_avec_moral = len([e for e in entries if e.note_moral])

        return {
            "nb_seances": len(entries),
            "total_minutes": sum(e.duree_minutes for e in entries),
            "total_calories": sum(e.calories_brulees or 0 for e in entries),
            "energie_moyenne": (
                sum(e.note_energie or 0 for e in entries if e.note_energie)
                / max(nb_avec_energie, 1)
            ),
            "moral_moyen": (
                sum(e.note_moral or 0 for e in entries if e.note_moral) / max(nb_avec_moral, 1)
            ),
        }

    # ═══════════════════════════════════════════════════════════
    # BUDGET FAMILLE
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return={})
    @avec_cache(ttl=300)
    @avec_session_db
    def get_budget_par_period(
        self, period: str = "month", db: Session | None = None
    ) -> dict[str, float]:
        """Récupère le budget familial par période.

        Args:
            period: 'day', 'week' ou 'month'.
            db: Session DB (injectée automatiquement).

        Returns:
            Dict {catégorie: montant, 'TOTAL': total}.
        """
        if db is None:
            raise ValueError("Session DB requise")

        if period == "day":
            debut = date_type.today()
            fin = date_type.today()
        elif period == "week":
            debut = date_type.today() - timedelta(days=date_type.today().weekday())
            fin = debut + timedelta(days=6)
        else:  # month
            debut = date_type(date_type.today().year, date_type.today().month, 1)
            if date_type.today().month == 12:
                fin = date_type(date_type.today().year + 1, 1, 1) - timedelta(days=1)
            else:
                fin = date_type(date_type.today().year, date_type.today().month + 1, 1) - timedelta(
                    days=1
                )

        budgets = (
            db.query(BudgetFamille)
            .filter(and_(BudgetFamille.date >= debut, BudgetFamille.date <= fin))
            .all()
        )

        result: dict[str, float] = {}
        total = 0.0
        for budget in budgets:
            cat = budget.categorie
            if cat not in result:
                result[cat] = 0.0
            result[cat] += budget.montant
            total += budget.montant

        result["TOTAL"] = total
        return result

    @avec_gestion_erreurs(default_return=0.0)
    @avec_cache(ttl=300)
    @avec_session_db
    def get_budget_mois_dernier(self, db: Session | None = None) -> float:
        """Récupère le budget total du mois dernier.

        Args:
            db: Session DB (injectée automatiquement).

        Returns:
            Montant total en euros.
        """
        if db is None:
            raise ValueError("Session DB requise")

        aujourd_hui = date_type.today()

        if aujourd_hui.month == 1:
            mois_dernier = date_type(aujourd_hui.year - 1, 12, 1)
        else:
            mois_dernier = date_type(aujourd_hui.year, aujourd_hui.month - 1, 1)

        mois_prochain = date_type(mois_dernier.year, mois_dernier.month, 1) + timedelta(days=32)
        mois_prochain = date_type(mois_prochain.year, mois_prochain.month, 1)

        total = (
            db.query(func.sum(BudgetFamille.montant))
            .filter(and_(BudgetFamille.date >= mois_dernier, BudgetFamille.date < mois_prochain))
            .scalar()
            or 0
        )

        return float(total)

    # ═══════════════════════════════════════════════════════════
    # ACTIVITÉS - STATS RAPIDES
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=[])
    @avec_cache(ttl=300)
    @avec_session_db
    def get_activites_semaine(self, db: Session | None = None) -> list[dict[str, Any]]:
        """Récupère les activités familiales de cette semaine.

        Args:
            db: Session DB (injectée automatiquement).

        Returns:
            Liste de dicts décrivant chaque activité.
        """
        if db is None:
            raise ValueError("Session DB requise")

        debut_semaine = date_type.today() - timedelta(days=date_type.today().weekday())
        fin_semaine = debut_semaine + timedelta(days=6)

        activities = (
            db.query(ActiviteFamille)
            .filter(
                and_(
                    ActiviteFamille.date_prevue >= debut_semaine,
                    ActiviteFamille.date_prevue <= fin_semaine,
                    ActiviteFamille.statut != "annule",
                )
            )
            .order_by(ActiviteFamille.date_prevue)
            .all()
        )

        return [
            {
                "id": act.id,
                "titre": act.titre,
                "date": act.date_prevue,
                "type": act.type_activite,
                "lieu": act.lieu,
                "participants": act.qui_participe or [],
                "cout_estime": act.cout_estime,
                "statut": act.statut,
            }
            for act in activities
        ]

    @avec_gestion_erreurs(default_return=0.0)
    @avec_cache(ttl=300)
    @avec_session_db
    def get_budget_activites_mois(self, db: Session | None = None) -> float:
        """Récupère les dépenses en activités ce mois.

        Args:
            db: Session DB (injectée automatiquement).

        Returns:
            Montant total en euros.
        """
        if db is None:
            raise ValueError("Session DB requise")

        debut_mois = date_type(date_type.today().year, date_type.today().month, 1)
        if date_type.today().month == 12:
            fin_mois = date_type(date_type.today().year + 1, 1, 1) - timedelta(days=1)
        else:
            fin_mois = date_type(
                date_type.today().year, date_type.today().month + 1, 1
            ) - timedelta(days=1)

        total = (
            db.query(func.sum(ActiviteFamille.cout_reel))
            .filter(
                and_(
                    ActiviteFamille.date_prevue >= debut_mois,
                    ActiviteFamille.date_prevue <= fin_mois,
                    ActiviteFamille.cout_reel > 0,
                )
            )
            .scalar()
            or 0
        )

        return float(total)


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("sante", tags={"famille", "sante"})
def obtenir_service_sante() -> ServiceSante:
    """Factory pour le service santé (singleton via ServiceRegistry)."""
    return ServiceSante()


# Alias anglais
get_sante_service = obtenir_service_sante
