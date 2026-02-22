"""
Service CRUD Dépenses Maison.

Centralise tous les accès base de données pour les dépenses maison
(gaz, eau, électricité, loyer, crèche, etc.).
"""

import logging
from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.core.models import HouseExpense
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)

# Noms des mois en français (index 1-12)
MOIS_FR = [
    "",
    "Janvier",
    "Fevrier",
    "Mars",
    "Avril",
    "Mai",
    "Juin",
    "Juillet",
    "Août",
    "Septembre",
    "Octobre",
    "Novembre",
    "Decembre",
]

# Catégories avec suivi consommation (kWh, m³)
CATEGORIES_AVEC_CONSO = {"gaz", "electricite", "eau"}


class DepensesCrudService:
    """Service CRUD pour les dépenses maison."""

    _instance: Optional["DepensesCrudService"] = None

    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def get_depenses_mois(self, mois: int, annee: int, db: Session | None = None) -> list:
        """Récupère les dépenses d'un mois."""
        return (
            db.query(HouseExpense)
            .filter(HouseExpense.mois == mois, HouseExpense.annee == annee)
            .order_by(HouseExpense.categorie)
            .all()
        )

    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def get_depenses_annee(self, annee: int, db: Session | None = None) -> list:
        """Récupère toutes les dépenses d'une année."""
        return (
            db.query(HouseExpense)
            .filter(HouseExpense.annee == annee)
            .order_by(HouseExpense.mois, HouseExpense.categorie)
            .all()
        )

    @avec_session_db
    @avec_gestion_erreurs(default_return=None)
    def get_depense_by_id(self, depense_id: int, db: Session | None = None):
        """Récupère une dépense par ID."""
        return db.query(HouseExpense).filter(HouseExpense.id == depense_id).first()

    @avec_session_db
    def create_depense(self, data: dict, db: Session | None = None):
        """Crée une nouvelle dépense.

        Pour les catégories énergie (gaz/elec/eau), passe aussi par le service budget.
        """
        if data.get("categorie") in CATEGORIES_AVEC_CONSO:
            try:
                from src.services.famille.budget import (
                    CategorieDepense,
                    FactureMaison,
                    get_budget_service,
                )

                service = get_budget_service()
                facture = FactureMaison(
                    categorie=CategorieDepense(data["categorie"]),
                    montant=data["montant"],
                    consommation=data.get("consommation"),
                    unite_consommation=data.get("unite", ""),
                    mois=data["mois"],
                    annee=data["annee"],
                    date_facture=data.get("date_facture"),
                    fournisseur=data.get("fournisseur", ""),
                    numero_facture=data.get("numero_facture", ""),
                    note=data.get("note", ""),
                )
                service.ajouter_facture_maison(facture)
            except Exception as e:
                logger.warning(f"Erreur service budget: {e}")

        depense = HouseExpense(**data)
        db.add(depense)
        db.commit()
        db.refresh(depense)
        return depense

    @avec_session_db
    def update_depense(self, depense_id: int, data: dict, db: Session | None = None):
        """Met à jour une dépense."""
        depense = db.query(HouseExpense).filter(HouseExpense.id == depense_id).first()
        if depense:
            for key, value in data.items():
                setattr(depense, key, value)
            db.commit()
            db.refresh(depense)
        return depense

    @avec_session_db
    def delete_depense(self, depense_id: int, db: Session | None = None) -> bool:
        """Supprime une dépense."""
        depense = db.query(HouseExpense).filter(HouseExpense.id == depense_id).first()
        if depense:
            db.delete(depense)
            db.commit()
            return True
        return False

    def get_stats_globales(self) -> dict:
        """Calcule les statistiques globales."""
        today = date.today()

        # Ce mois
        depenses_mois = self.get_depenses_mois(today.month, today.year)
        total_mois = sum(float(d.montant) for d in depenses_mois)

        # Mois précédent
        if today.month == 1:
            mois_prec, annee_prec = 12, today.year - 1
        else:
            mois_prec, annee_prec = today.month - 1, today.year

        depenses_prec = self.get_depenses_mois(mois_prec, annee_prec)
        total_prec = sum(float(d.montant) for d in depenses_prec)

        # Delta
        delta = total_mois - total_prec if total_prec > 0 else 0
        delta_pct = (delta / total_prec * 100) if total_prec > 0 else 0

        # Moyenne mensuelle (12 derniers mois)
        depenses_annee = self.get_depenses_annee(today.year)
        depenses_annee_prec = self.get_depenses_annee(today.year - 1)
        all_depenses = depenses_annee + depenses_annee_prec

        # Grouper par mois
        par_mois = {}
        for d in all_depenses:
            key = f"{d.annee}-{d.mois:02d}"
            if key not in par_mois:
                par_mois[key] = 0
            par_mois[key] += float(d.montant)

        moyenne = sum(par_mois.values()) / len(par_mois) if par_mois else 0

        return {
            "total_mois": total_mois,
            "total_prec": total_prec,
            "delta": delta,
            "delta_pct": delta_pct,
            "moyenne_mensuelle": moyenne,
            "nb_categories": len(set(d.categorie for d in depenses_mois)),
        }

    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def get_historique_categorie(
        self, categorie: str, nb_mois: int = 12, db: Session | None = None
    ) -> list[dict]:
        """Récupère l'historique d'une catégorie."""
        today = date.today()
        result = []

        for i in range(nb_mois):
            mois = today.month - i
            annee = today.year
            while mois <= 0:
                mois += 12
                annee -= 1

            depense = (
                db.query(HouseExpense)
                .filter(
                    HouseExpense.categorie == categorie,
                    HouseExpense.mois == mois,
                    HouseExpense.annee == annee,
                )
                .first()
            )

            result.append(
                {
                    "mois": mois,
                    "annee": annee,
                    "label": f"{MOIS_FR[mois][:3]} {annee}",
                    "montant": float(depense.montant) if depense else 0,
                    "consommation": float(depense.consommation)
                    if depense and depense.consommation
                    else 0,
                }
            )

        return list(reversed(result))


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("depenses_crud", tags={"maison", "crud", "depenses"})
def get_depenses_crud_service() -> DepensesCrudService:
    """Factory singleton pour le service CRUD dépenses."""
    if DepensesCrudService._instance is None:
        DepensesCrudService._instance = DepensesCrudService()
    return DepensesCrudService._instance


def obtenir_service_depenses_crud() -> DepensesCrudService:
    """Factory française pour le service CRUD dépenses."""
    return get_depenses_crud_service()
