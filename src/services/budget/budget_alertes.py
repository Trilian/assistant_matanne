"""
Mixin d'alertes budgétaires et gestion des factures maison.

Méthodes de vérification d'alertes de dépassement et gestion
des factures (gaz, eau, électricité) extraites de BudgetService.
"""

import logging
from datetime import date as date_type

from sqlalchemy.orm import Session

from src.core.decorators import avec_cache, avec_session_db
from src.core.models import FamilyBudget

from .schemas import (
    CategorieDepense,
    FactureMaison,
    FrequenceRecurrence,
)

logger = logging.getLogger(__name__)


class BudgetAlertesMixin:
    """Mixin pour les alertes budgétaires et la gestion des factures maison."""

    # ═══════════════════════════════════════════════════════════
    # ALERTES
    # ═══════════════════════════════════════════════════════════

    def _verifier_alertes_budget(self, mois: int, annee: int, db: Session):
        """Vérifie et génère les alertes de budget."""
        budgets = self.get_tous_budgets(mois, annee, db=db)
        depenses = self.get_depenses_mois(mois, annee, db=db)

        # Calculer les totaux par catégorie
        totaux = {}
        for dep in depenses:
            totaux[dep.categorie] = totaux.get(dep.categorie, 0) + dep.montant

        alertes = []

        for cat, budget in budgets.items():
            depense = totaux.get(cat, 0)
            pourcentage = (depense / budget * 100) if budget > 0 else 0

            if pourcentage >= 100:
                alertes.append(
                    {
                        "type": "danger",
                        "categorie": cat.value,
                        "message": f"Budget {cat.value} dépassé! ({depense:.0f}€ / {budget:.0f}€)",
                        "pourcentage": pourcentage,
                    }
                )
            elif pourcentage >= 80:
                alertes.append(
                    {
                        "type": "warning",
                        "categorie": cat.value,
                        "message": f"Budget {cat.value} à {pourcentage:.0f}%",
                        "pourcentage": pourcentage,
                    }
                )

        # Stocker les alertes (sans dépendance Streamlit)
        self._derniers_alertes = alertes
        return alertes

    # ═══════════════════════════════════════════════════════════
    # GESTION DES FACTURES MAISON (gaz, eau, électricité)
    # ═══════════════════════════════════════════════════════════

    @avec_session_db
    def ajouter_facture_maison(self, facture: FactureMaison, db: Session = None) -> FactureMaison:
        """
        Ajoute une facture maison avec suivi consommation.
        Utilise la table house_expenses si disponible, sinon FamilyBudget.

        Args:
            facture: Facture à ajouter
            db: Session DB

        Returns:
            Facture créée avec ID
        """
        try:
            # Essayer d'utiliser house_expenses (table dédiée factures)
            from src.core.models import HouseExpense

            entry = HouseExpense(
                categorie=facture.categorie.value,
                montant=facture.montant,
                consommation=facture.consommation,
                mois=facture.mois,
                annee=facture.annee,
                date_facture=facture.date_facture,
                fournisseur=facture.fournisseur,
                numero_facture=facture.numero_facture,
                note=facture.note,
            )
            db.add(entry)
            db.commit()
            db.refresh(entry)

            facture.id = entry.id
            logger.info(f"✅ Facture {facture.categorie.value} ajoutée: {facture.montant}€")
            return facture

        except Exception as e:
            logger.warning(f"Table house_expenses indisponible, fallback vers FamilyBudget: {e}")

            # Fallback: utiliser FamilyBudget
            date_facture = facture.date_facture or date_type(facture.annee, facture.mois, 1)

            entry = FamilyBudget(
                date=date_facture,
                montant=facture.montant,
                categorie=facture.categorie.value,
                description=f"Facture {facture.fournisseur} - {facture.consommation} {facture.unite_consommation}",
                est_recurrent=True,
                frequence_recurrence=FrequenceRecurrence.MENSUEL.value,
            )
            db.add(entry)
            db.commit()

            facture.id = entry.id
            return facture

    @avec_cache(ttl=300)
    @avec_session_db
    def get_factures_maison(
        self,
        categorie: CategorieDepense | None = None,
        annee: int | None = None,
        db: Session = None,
    ) -> list[FactureMaison]:
        """
        Récupère les factures maison avec consommation.

        Args:
            categorie: Filtrer par catégorie (GAZ, ELECTRICITE, EAU...)
            annee: Filtrer par année
            db: Session DB

        Returns:
            Liste des factures
        """
        try:
            from src.core.models import HouseExpense

            query = db.query(HouseExpense)

            if categorie:
                query = query.filter(HouseExpense.categorie == categorie.value)
            if annee:
                query = query.filter(HouseExpense.annee == annee)

            entries = query.order_by(HouseExpense.annee.desc(), HouseExpense.mois.desc()).all()

            return [
                FactureMaison(
                    id=e.id,
                    categorie=CategorieDepense(e.categorie),
                    montant=float(e.montant),
                    consommation=float(e.consommation) if e.consommation else None,
                    unite_consommation="kWh" if e.categorie == "electricite" else "m³",
                    mois=e.mois,
                    annee=e.annee,
                    date_facture=e.date_facture,
                    fournisseur=e.fournisseur or "",
                    numero_facture=e.numero_facture or "",
                    note=e.note or "",
                )
                for e in entries
            ]

        except Exception as e:
            logger.warning(f"Table house_expenses indisponible: {e}")
            return []

    def get_evolution_consommation(
        self,
        categorie: CategorieDepense,
        nb_mois: int = 12,
    ) -> list[dict]:
        """
        Retourne l'évolution de la consommation sur les derniers mois.
        Utile pour les graphiques.

        Args:
            categorie: GAZ, ELECTRICITE, ou EAU
            nb_mois: Nombre de mois à afficher

        Returns:
            Liste de {mois, annee, consommation, montant, prix_unitaire}
        """
        factures = self.get_factures_maison(categorie=categorie)

        # Trier par date et limiter
        factures_triees = sorted(factures, key=lambda f: (f.annee, f.mois), reverse=True)[:nb_mois]

        return [
            {
                "periode": f.periode,
                "mois": f.mois,
                "annee": f.annee,
                "consommation": f.consommation,
                "montant": f.montant,
                "prix_unitaire": f.prix_unitaire,
            }
            for f in reversed(factures_triees)  # Ordre chronologique
        ]
