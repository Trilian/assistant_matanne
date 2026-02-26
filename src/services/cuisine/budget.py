"""
Service de budget cuisine hebdomadaire.

Suivi du budget alimentation avec objectifs hebdo, alertes
et historique pour comparaison semaine-sur-semaine.
Utilise les modèles existants Depense et BudgetMensuelDB.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.decorators import avec_session_db

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


@dataclass
class BudgetHebdoCuisine:
    """Résumé budget cuisine pour une semaine."""

    semaine_debut: date
    semaine_fin: date
    budget_prevu: Decimal = Decimal("0")
    depenses_reelles: Decimal = Decimal("0")
    nb_achats: int = 0
    par_rayon: dict[str, Decimal] = field(default_factory=dict)
    depenses_detail: list[dict] = field(default_factory=list)

    @property
    def reste(self) -> Decimal:
        return self.budget_prevu - self.depenses_reelles

    @property
    def pourcentage_utilise(self) -> float:
        if self.budget_prevu == 0:
            return 0.0
        return float(self.depenses_reelles / self.budget_prevu * 100)

    @property
    def statut(self) -> str:
        """retourne: 'ok', 'attention', 'depasse'."""
        pct = self.pourcentage_utilise
        if pct <= 80:
            return "ok"
        if pct <= 100:
            return "attention"
        return "depasse"


@dataclass
class TendanceBudget:
    """Tendance sur plusieurs semaines."""

    semaines: list[BudgetHebdoCuisine]
    moyenne_hebdo: Decimal = Decimal("0")
    tendance: str = "stable"  # hausse, baisse, stable
    economie_totale: Decimal = Decimal("0")
    meilleure_semaine: BudgetHebdoCuisine | None = None
    pire_semaine: BudgetHebdoCuisine | None = None


# ═══════════════════════════════════════════════════════════
# FONCTIONS
# ═══════════════════════════════════════════════════════════

BUDGET_HEBDO_DEFAUT = Decimal("120")  # €120/semaine par défaut
CATEGORIE_ALIMENTATION = "alimentation"


def _debut_semaine(dt: date) -> date:
    """Retourne le lundi de la semaine."""
    return dt - timedelta(days=dt.weekday())


@avec_session_db
def obtenir_budget_hebdo(
    semaine_date: date | None = None,
    budget_prevu: Decimal | None = None,
    *,
    db: Session,
) -> BudgetHebdoCuisine:
    """
    Calcule le budget cuisine pour une semaine donnée.

    Args:
        semaine_date: N'importe quel jour de la semaine (défaut: cette semaine)
        budget_prevu: Budget prévu (défaut: 120€)
        db: Session SQLAlchemy (injectée)

    Returns:
        BudgetHebdoCuisine
    """
    from src.core.models.finances import Depense

    if semaine_date is None:
        semaine_date = date.today()
    if budget_prevu is None:
        budget_prevu = BUDGET_HEBDO_DEFAUT

    lundi = _debut_semaine(semaine_date)
    dimanche = lundi + timedelta(days=6)

    # Requête dépenses alimentation de la semaine
    depenses = (
        db.query(Depense)
        .filter(
            Depense.categorie == CATEGORIE_ALIMENTATION,
            Depense.date >= lundi,
            Depense.date <= dimanche,
        )
        .all()
    )

    total = Decimal("0")
    par_rayon: dict[str, Decimal] = {}
    details = []

    for dep in depenses:
        total += dep.montant
        # Extraire le rayon des tags si disponible
        rayon = "Autre"
        if dep.tags and isinstance(dep.tags, list):
            for tag in dep.tags:
                if isinstance(tag, str) and tag.startswith("rayon:"):
                    rayon = tag.replace("rayon:", "")
                    break
        par_rayon[rayon] = par_rayon.get(rayon, Decimal("0")) + dep.montant
        details.append(
            {
                "date": dep.date.isoformat(),
                "montant": float(dep.montant),
                "description": dep.description or "",
                "rayon": rayon,
            }
        )

    return BudgetHebdoCuisine(
        semaine_debut=lundi,
        semaine_fin=dimanche,
        budget_prevu=budget_prevu,
        depenses_reelles=total,
        nb_achats=len(depenses),
        par_rayon=par_rayon,
        depenses_detail=details,
    )


@avec_session_db
def obtenir_tendance(
    nb_semaines: int = 4,
    budget_prevu: Decimal | None = None,
    *,
    db: Session,
) -> TendanceBudget:
    """
    Calcule la tendance budget cuisine sur N semaines.

    Args:
        nb_semaines: Nombre de semaines à analyser
        budget_prevu: Budget hebdo prévu

    Returns:
        TendanceBudget
    """
    from src.core.models.finances import Depense

    if budget_prevu is None:
        budget_prevu = BUDGET_HEBDO_DEFAUT

    aujourd_hui = date.today()
    semaines = []

    for i in range(nb_semaines):
        dt = aujourd_hui - timedelta(weeks=i)
        lundi = _debut_semaine(dt)
        dimanche = lundi + timedelta(days=6)

        depenses = (
            db.query(func.sum(Depense.montant), func.count(Depense.id))
            .filter(
                Depense.categorie == CATEGORIE_ALIMENTATION,
                Depense.date >= lundi,
                Depense.date <= dimanche,
            )
            .first()
        )

        total = depenses[0] or Decimal("0")
        nb = depenses[1] or 0

        semaines.append(
            BudgetHebdoCuisine(
                semaine_debut=lundi,
                semaine_fin=dimanche,
                budget_prevu=budget_prevu,
                depenses_reelles=total,
                nb_achats=nb,
            )
        )

    # Calculer tendance
    if len(semaines) >= 2:
        totaux = [s.depenses_reelles for s in semaines]
        moyenne = sum(totaux, Decimal("0")) / len(totaux)
        economie = sum((s.reste for s in semaines if s.reste > 0), Decimal("0"))

        # Tendance : comparer les 2 dernières semaines aux 2 précédentes
        recentes = sum(totaux[:2], Decimal("0")) / 2
        anciennes = sum(totaux[2:4] if len(totaux) >= 4 else totaux[2:], Decimal("0"))
        nb_anc = min(2, len(totaux) - 2) or 1
        anciennes = anciennes / nb_anc

        if recentes < anciennes * Decimal("0.9"):
            tendance = "baisse"
        elif recentes > anciennes * Decimal("1.1"):
            tendance = "hausse"
        else:
            tendance = "stable"

        meilleure = min(semaines, key=lambda s: s.depenses_reelles)
        pire = max(semaines, key=lambda s: s.depenses_reelles)

        return TendanceBudget(
            semaines=semaines,
            moyenne_hebdo=moyenne,
            tendance=tendance,
            economie_totale=economie,
            meilleure_semaine=meilleure,
            pire_semaine=pire,
        )

    return TendanceBudget(semaines=semaines)


@avec_session_db
def enregistrer_depense_course(
    montant: float,
    description: str = "",
    rayon: str = "",
    dt: date | None = None,
    *,
    db: Session,
) -> int:
    """
    Enregistre une dépense alimentaire.

    Args:
        montant: Montant en €
        description: Description optionnelle
        rayon: Rayon du magasin
        dt: Date (défaut: aujourd'hui)

    Returns:
        ID de la dépense créée
    """
    from src.core.models.finances import Depense

    tags = []
    if rayon:
        tags.append(f"rayon:{rayon}")

    depense = Depense(
        montant=Decimal(str(montant)),
        categorie=CATEGORIE_ALIMENTATION,
        description=description,
        date=dt or date.today(),
        tags=tags,
    )
    db.add(depense)
    db.flush()
    return depense.id


__all__ = [
    "BudgetHebdoCuisine",
    "TendanceBudget",
    "obtenir_budget_hebdo",
    "obtenir_tendance",
    "enregistrer_depense_course",
]
