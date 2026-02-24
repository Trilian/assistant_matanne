"""
Service de suivi du budget familial.

Fonctionnalités:
- CRUD dépenses
- Gestion des budgets mensuels (persistés en DB)
- Calcul des statistiques
- Prévisions
- Alertes dépassement

Les analyses/prévisions et alertes/factures sont dans des mixins séparés:
- BudgetAnalysesMixin (budget_analyses.py)
- BudgetAlertesMixin (budget_alertes.py)
"""

import logging
from datetime import date as date_type
from decimal import Decimal

from sqlalchemy import extract
from sqlalchemy.orm import Session

from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.models import BudgetFamille, BudgetMensuelDB
from src.services.core.base import BaseService

from .budget_alertes import BudgetAlertesMixin
from .budget_analyses import BudgetAnalysesMixin
from .schemas import (
    DEFAULT_USER_ID,
    CategorieDepense,
    Depense,
)

logger = logging.getLogger(__name__)


class BudgetService(BaseService[BudgetFamille], BudgetAnalysesMixin, BudgetAlertesMixin):
    """
    Service de gestion du budget familial.

    Hérite de BaseService[BudgetFamille] pour le CRUD générique.

    Fonctionnalités:
    - CRUD dépenses
    - Gestion des budgets mensuels
    - Calcul des statistiques (via BudgetAnalysesMixin)
    - Prévisions (via BudgetAnalysesMixin)
    - Alertes dépassement (via BudgetAlertesMixin)
    - Factures maison (via BudgetAlertesMixin)
    """

    # Budgets par défaut suggérés (pour une famille)
    BUDGETS_DEFAUT = {
        CategorieDepense.ALIMENTATION: 600,
        CategorieDepense.COURSES: 200,
        CategorieDepense.MAISON: 300,
        CategorieDepense.SANTE: 100,
        CategorieDepense.TRANSPORT: 200,
        CategorieDepense.LOISIRS: 150,
        CategorieDepense.VETEMENTS: 100,
        CategorieDepense.ENFANT: 200,
        CategorieDepense.SERVICES: 150,
    }

    def __init__(self):
        """Initialise le service."""
        super().__init__(model=BudgetFamille, cache_ttl=300)
        self._depenses_cache: dict[str, list[Depense]] = {}

    # ═══════════════════════════════════════════════════════════
    # GESTION DES DÉPENSES
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def ajouter_depense(self, depense: Depense, db: Session = None) -> Depense:
        """
        Ajoute une nouvelle dépense.

        Args:
            depense: Dépense à ajouter
            db: Session DB

        Returns:
            Dépense créée avec ID
        """
        # Créer l'entrée BudgetFamille
        budget_entry = BudgetFamille(
            date=depense.date,
            montant=depense.montant,
            categorie=depense.categorie.value,
            description=depense.description,
            magasin=depense.magasin,
            est_recurrent=depense.est_recurrente,
            frequence_recurrence=depense.frequence.value if depense.est_recurrente else None,
        )

        db.add(budget_entry)
        db.commit()
        db.refresh(budget_entry)

        depense.id = budget_entry.id

        logger.info(f"Dépense ajoutée: {depense.montant}€ ({depense.categorie.value})")

        # Vérifier si budget dépassé
        self._verifier_alertes_budget(depense.date.month, depense.date.year, db)

        return depense

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def modifier_depense(self, depense_id: int, updates: dict, db: Session = None) -> bool:
        """Modifie une dépense existante."""
        entry = db.query(BudgetFamille).filter(BudgetFamille.id == depense_id).first()

        if not entry:
            return False

        for key, value in updates.items():
            if hasattr(entry, key):
                setattr(entry, key, value)

        db.commit()
        return True

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def supprimer_depense(self, depense_id: int, db: Session = None) -> bool:
        """Supprime une dépense."""
        entry = db.query(BudgetFamille).filter(BudgetFamille.id == depense_id).first()

        if not entry:
            return False

        db.delete(entry)
        db.commit()
        return True

    @avec_gestion_erreurs(default_return=[])
    @avec_cache(ttl=300)
    @avec_session_db
    def get_depenses_mois(
        self,
        mois: int,
        annee: int,
        categorie: CategorieDepense | None = None,
        db: Session = None,
    ) -> list[Depense]:
        """
        Récupère les dépenses d'un mois.

        Args:
            mois: Mois (1-12)
            annee: Année
            categorie: Filtrer par catégorie (optionnel)
            db: Session DB

        Returns:
            Liste des dépenses
        """
        query = db.query(BudgetFamille).filter(
            extract("month", BudgetFamille.date) == mois,
            extract("year", BudgetFamille.date) == annee,
        )

        if categorie:
            query = query.filter(BudgetFamille.categorie == categorie.value)

        entries = query.order_by(BudgetFamille.date.desc()).all()

        return [
            Depense(
                id=e.id,
                date=e.date,
                montant=float(e.montant),
                categorie=CategorieDepense(e.categorie)
                if e.categorie in [c.value for c in CategorieDepense]
                else CategorieDepense.AUTRE,
                description=e.description or "",
            )
            for e in entries
        ]

    # ═══════════════════════════════════════════════════════════
    # GESTION DES BUDGETS (PERSISTÉ EN DB)
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def definir_budget(
        self,
        categorie: CategorieDepense,
        montant: float,
        mois: int | None = None,
        annee: int | None = None,
        user_id: str = DEFAULT_USER_ID,
        db: Session = None,
    ):
        """
        Définit le budget pour une catégorie (persisté en DB).

        Args:
            categorie: Catégorie de dépense
            montant: Budget mensuel
            mois: Mois spécifique (optionnel, défaut = mois courant)
            annee: Année spécifique (optionnel, défaut = année courante)
            user_id: ID utilisateur
            db: Session DB
        """
        mois = mois or date_type.today().month
        annee = annee or date_type.today().year

        # Date du premier jour du mois
        date_mois = date_type(annee, mois, 1)

        # Chercher ou créer le budget mensuel
        budget_db = (
            db.query(BudgetMensuelDB)
            .filter(
                BudgetMensuelDB.mois == date_mois,
                BudgetMensuelDB.user_id == user_id,
            )
            .first()
        )

        if not budget_db:
            budget_db = BudgetMensuelDB(
                mois=date_mois,
                user_id=user_id,
                budgets_par_categorie={},
            )
            db.add(budget_db)

        # Mettre à jour le budget de la catégorie
        budgets = budget_db.budgets_par_categorie or {}
        budgets[categorie.value] = montant
        budget_db.budgets_par_categorie = budgets

        # Recalculer le total
        budget_db.budget_total = Decimal(str(sum(budgets.values())))

        db.commit()
        logger.info(f"✅ Budget défini: {categorie.value} = {montant}€ ({mois}/{annee})")

    @avec_gestion_erreurs(default_return=0.0)
    @avec_cache(ttl=300)
    @avec_session_db
    def get_budget(
        self,
        categorie: CategorieDepense,
        mois: int | None = None,
        annee: int | None = None,
        user_id: str = DEFAULT_USER_ID,
        db: Session = None,
    ) -> float:
        """Récupère le budget d'une catégorie depuis la DB."""
        mois = mois or date_type.today().month
        annee = annee or date_type.today().year
        date_mois = date_type(annee, mois, 1)

        budget_db = (
            db.query(BudgetMensuelDB)
            .filter(
                BudgetMensuelDB.mois == date_mois,
                BudgetMensuelDB.user_id == user_id,
            )
            .first()
        )

        if budget_db and budget_db.budgets_par_categorie:
            return budget_db.budgets_par_categorie.get(
                categorie.value, self.BUDGETS_DEFAUT.get(categorie, 0)
            )

        return self.BUDGETS_DEFAUT.get(categorie, 0)

    @avec_gestion_erreurs(default_return={})
    @avec_cache(ttl=300)
    @avec_session_db
    def get_tous_budgets(
        self,
        mois: int | None = None,
        annee: int | None = None,
        user_id: str = DEFAULT_USER_ID,
        db: Session = None,
    ) -> dict[CategorieDepense, float]:
        """Récupère tous les budgets du mois depuis la DB."""
        mois = mois or date_type.today().month
        annee = annee or date_type.today().year
        date_mois = date_type(annee, mois, 1)

        budget_db = (
            db.query(BudgetMensuelDB)
            .filter(
                BudgetMensuelDB.mois == date_mois,
                BudgetMensuelDB.user_id == user_id,
            )
            .first()
        )

        budgets_db = budget_db.budgets_par_categorie if budget_db else {}

        result = {}
        for cat in CategorieDepense:
            if budgets_db and cat.value in budgets_db:
                result[cat] = budgets_db[cat.value]
            elif cat in self.BUDGETS_DEFAUT:
                result[cat] = self.BUDGETS_DEFAUT[cat]

        return result

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def definir_budgets_batch(
        self,
        budgets: dict[CategorieDepense, float],
        mois: int | None = None,
        annee: int | None = None,
        user_id: str = DEFAULT_USER_ID,
        db: Session = None,
    ):
        """
        Définit plusieurs budgets en une fois.

        Args:
            budgets: Dict catégorie → montant
            mois: Mois
            annee: Année
            user_id: ID utilisateur
            db: Session DB
        """
        mois = mois or date_type.today().month
        annee = annee or date_type.today().year
        date_mois = date_type(annee, mois, 1)

        budget_db = (
            db.query(BudgetMensuelDB)
            .filter(
                BudgetMensuelDB.mois == date_mois,
                BudgetMensuelDB.user_id == user_id,
            )
            .first()
        )

        if not budget_db:
            budget_db = BudgetMensuelDB(
                mois=date_mois,
                user_id=user_id,
                budgets_par_categorie={},
            )
            db.add(budget_db)

        # Mettre à jour tous les budgets
        budgets_dict = budget_db.budgets_par_categorie or {}
        for cat, montant in budgets.items():
            budgets_dict[cat.value] = montant

        budget_db.budgets_par_categorie = budgets_dict
        budget_db.budget_total = Decimal(str(sum(budgets_dict.values())))

        db.commit()
        logger.info(f"✅ {len(budgets)} budgets définis pour {mois}/{annee}")


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


from src.services.core.registry import service_factory


@service_factory("budget", tags={"famille", "crud"})
def obtenir_service_budget() -> BudgetService:
    """Factory pour le service budget (thread-safe via registre)."""
    return BudgetService()


def get_budget_service() -> BudgetService:
    """Factory pour le service budget (alias anglais)."""
    return obtenir_service_budget()
