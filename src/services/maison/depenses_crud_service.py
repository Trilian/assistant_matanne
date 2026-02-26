"""
Service CRUD Dépenses Maison.

Hérite de BaseService[DepenseMaison] pour CRUD générique.

Centralise tous les accès base de données pour les dépenses maison
(gaz, eau, électricité, loyer, crèche, etc.).
"""

import logging
from datetime import date

from sqlalchemy.orm import Session

from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db, avec_validation
from src.core.models import DepenseMaison
from src.core.monitoring import chronometre
from src.core.validation.schemas import DepenseMaisonInput
from src.services.core.base import BaseService
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)

# Noms des mois en français (index 1-12)
MOIS_FR = [
    "",
    "Janvier",
    "Février",
    "Mars",
    "Avril",
    "Mai",
    "Juin",
    "Juillet",
    "Août",
    "Septembre",
    "Octobre",
    "Novembre",
    "Décembre",
]

# Catégories avec suivi consommation (kWh, m³)
CATEGORIES_AVEC_CONSO = {"gaz", "electricite", "eau"}


class DepensesCrudService(BaseService[DepenseMaison]):
    """Service CRUD pour les dépenses maison.

    Hérite de BaseService[DepenseMaison] pour le CRUD générique.
    """

    def __init__(self):
        super().__init__(model=DepenseMaison, cache_ttl=600)

    @chronometre("maison.depenses.mois", seuil_alerte_ms=1500)
    @avec_cache(ttl=600)
    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def get_depenses_mois(self, mois: int, annee: int, db: Session | None = None) -> list:
        """Récupère les dépenses d'un mois."""
        return (
            db.query(DepenseMaison)
            .filter(DepenseMaison.mois == mois, DepenseMaison.annee == annee)
            .order_by(DepenseMaison.categorie)
            .all()
        )

    @chronometre("maison.depenses.annee", seuil_alerte_ms=2000)
    @avec_cache(ttl=600)
    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def get_depenses_annee(self, annee: int, db: Session | None = None) -> list:
        """Récupère toutes les dépenses d'une année."""
        return (
            db.query(DepenseMaison)
            .filter(DepenseMaison.annee == annee)
            .order_by(DepenseMaison.mois, DepenseMaison.categorie)
            .all()
        )

    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return=None)
    def get_depense_by_id(self, depense_id: int, db: Session | None = None):
        """Récupère une dépense par ID."""
        return db.query(DepenseMaison).filter(DepenseMaison.id == depense_id).first()

    @avec_validation(DepenseMaisonInput)
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

        depense = DepenseMaison(**data)
        db.add(depense)
        db.commit()
        db.refresh(depense)

        # Émettre événement pour invalidation cache
        try:
            from src.services.core.events.bus import obtenir_bus

            obtenir_bus().emettre(
                "depenses.modifiee",
                {
                    "depense_id": depense.id,
                    "categorie": data.get("categorie", ""),
                    "montant": float(data.get("montant", 0)),
                    "action": "creee",
                },
                source="depenses_crud",
            )
        except Exception:  # noqa: BLE001
            pass

        return depense

    @avec_session_db
    def update_depense(self, depense_id: int, data: dict, db: Session | None = None):
        """Met à jour une dépense."""
        depense = db.query(DepenseMaison).filter(DepenseMaison.id == depense_id).first()
        if depense:
            for key, value in data.items():
                setattr(depense, key, value)
            db.commit()
            db.refresh(depense)

            # Émettre événement pour invalidation cache
            try:
                from src.services.core.events.bus import obtenir_bus

                obtenir_bus().emettre(
                    "depenses.modifiee",
                    {
                        "depense_id": depense_id,
                        "categorie": data.get("categorie", ""),
                        "montant": float(data.get("montant", 0)),
                        "action": "modifiee",
                    },
                    source="depenses_crud",
                )
            except Exception:  # noqa: BLE001
                pass

        return depense

    @avec_session_db
    def delete_depense(self, depense_id: int, db: Session | None = None) -> bool:
        """Supprime une dépense."""
        depense = db.query(DepenseMaison).filter(DepenseMaison.id == depense_id).first()
        if depense:
            db.delete(depense)
            db.commit()

            # Émettre événement pour invalidation cache
            try:
                from src.services.core.events.bus import obtenir_bus

                obtenir_bus().emettre(
                    "depenses.modifiee",
                    {"depense_id": depense_id, "action": "supprimee"},
                    source="depenses_crud",
                )
            except Exception:  # noqa: BLE001
                pass

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
                db.query(DepenseMaison)
                .filter(
                    DepenseMaison.categorie == categorie,
                    DepenseMaison.mois == mois,
                    DepenseMaison.annee == annee,
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

    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def charger_historique_energie(
        self, type_energie: str, nb_mois: int = 12, db: Session | None = None
    ) -> list[dict]:
        """Charge l'historique de consommation énergétique depuis la DB.

        Args:
            type_energie: Type d'énergie (electricite, gaz, eau).
            nb_mois: Nombre de mois d'historique.
            db: Session DB (injectée par @avec_session_db)

        Returns:
            Liste de dicts avec mois, annee, label, montant, consommation.
        """
        today = date.today()
        result = []

        for i in range(nb_mois):
            # Calculer le mois cible (en remontant depuis aujourd'hui)
            mois_offset = nb_mois - 1 - i
            mois = today.month - mois_offset
            annee = today.year
            while mois <= 0:
                mois += 12
                annee -= 1

            label = MOIS_FR[mois] if 1 <= mois <= 12 else f"M{mois}"

            # Requête DB pour ce mois
            depense = (
                db.query(DepenseMaison)
                .filter(
                    DepenseMaison.categorie == type_energie,
                    DepenseMaison.mois == mois,
                    DepenseMaison.annee == annee,
                )
                .first()
            )

            montant = None
            consommation = None
            if depense:
                montant = depense.montant
                consommation = getattr(depense, "consommation", None)

            result.append(
                {
                    "mois": mois,
                    "annee": annee,
                    "label": label,
                    "montant": montant,
                    "consommation": consommation,
                }
            )

        return result


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("depenses_crud", tags={"maison", "crud", "depenses"})
def get_depenses_crud_service() -> DepensesCrudService:
    """Factory singleton pour le service CRUD dépenses."""
    return DepensesCrudService()


def obtenir_service_depenses_crud() -> DepensesCrudService:
    """Factory française pour le service CRUD dépenses."""
    return get_depenses_crud_service()
