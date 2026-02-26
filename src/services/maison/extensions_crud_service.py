"""
Service CRUD Nuisibles, Devis, Entretien Saisonnier, Relevés Compteurs.

Regroupe les services secondaires de gestion maison.
"""

import logging
from datetime import date, timedelta

from sqlalchemy.orm import Session

from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.models.maison_extensions import (
    DevisComparatif,
    EntretienSaisonnier,
    LigneDevis,
    ReleveCompteur,
    TraitementNuisible,
)
from src.core.monitoring import chronometre
from src.services.core.base import BaseService
from src.services.core.event_bus_mixin import EventBusMixin
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# NUISIBLES
# ═══════════════════════════════════════════════════════════


class NuisiblesCrudService(EventBusMixin, BaseService[TraitementNuisible]):
    """Service CRUD pour les traitements nuisibles."""

    _event_source = "nuisibles"

    def __init__(self):
        super().__init__(model=TraitementNuisible, cache_ttl=300)

    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def get_all_traitements(
        self,
        filtre_type: str | None = None,
        db: Session | None = None,
    ) -> list[TraitementNuisible]:
        """Récupère tous les traitements."""
        query = db.query(TraitementNuisible)
        if filtre_type:
            query = query.filter(TraitementNuisible.type_nuisible == filtre_type)
        return query.order_by(TraitementNuisible.date_traitement.desc()).all()

    @avec_session_db
    def create_traitement(self, data: dict, db: Session | None = None) -> TraitementNuisible:
        """Crée un nouveau traitement."""
        traitement = TraitementNuisible(**data)
        db.add(traitement)
        db.commit()
        db.refresh(traitement)
        logger.info(f"Traitement créé: {traitement.id}")
        return traitement

    @avec_session_db
    def update_traitement(
        self, traitement_id: int, data: dict, db: Session | None = None
    ) -> TraitementNuisible | None:
        """Met à jour un traitement."""
        traitement = (
            db.query(TraitementNuisible).filter(TraitementNuisible.id == traitement_id).first()
        )
        if traitement is None:
            return None
        for key, value in data.items():
            setattr(traitement, key, value)
        db.commit()
        db.refresh(traitement)
        return traitement

    @avec_session_db
    def delete_traitement(self, traitement_id: int, db: Session | None = None) -> bool:
        """Supprime un traitement."""
        traitement = (
            db.query(TraitementNuisible).filter(TraitementNuisible.id == traitement_id).first()
        )
        if traitement is None:
            return False
        db.delete(traitement)
        db.commit()
        return True

    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def get_prochains_traitements(
        self, jours_horizon: int = 30, db: Session | None = None
    ) -> list[TraitementNuisible]:
        """Récupère les prochains traitements à effectuer."""
        date_limite = date.today() + timedelta(days=jours_horizon)
        return (
            db.query(TraitementNuisible)
            .filter(
                TraitementNuisible.date_prochain_traitement.isnot(None),
                TraitementNuisible.date_prochain_traitement <= date_limite,
            )
            .order_by(TraitementNuisible.date_prochain_traitement)
            .all()
        )


# ═══════════════════════════════════════════════════════════
# DEVIS COMPARATIFS
# ═══════════════════════════════════════════════════════════


class DevisCrudService(EventBusMixin, BaseService[DevisComparatif]):
    """Service CRUD pour les devis comparatifs."""

    _event_source = "devis"

    def __init__(self):
        super().__init__(model=DevisComparatif, cache_ttl=300)

    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def get_devis_by_projet(
        self, projet_id: int, db: Session | None = None
    ) -> list[DevisComparatif]:
        """Récupère tous les devis d'un projet."""
        return (
            db.query(DevisComparatif)
            .filter(DevisComparatif.projet_id == projet_id)
            .order_by(DevisComparatif.montant_ttc)
            .all()
        )

    @avec_session_db
    def create_devis(self, data: dict, db: Session | None = None) -> DevisComparatif:
        """Crée un nouveau devis."""
        devis = DevisComparatif(**data)
        db.add(devis)
        db.commit()
        db.refresh(devis)
        logger.info(f"Devis créé: {devis.id}")
        return devis

    @avec_session_db
    def update_devis(
        self, devis_id: int, data: dict, db: Session | None = None
    ) -> DevisComparatif | None:
        """Met à jour un devis."""
        devis = db.query(DevisComparatif).filter(DevisComparatif.id == devis_id).first()
        if devis is None:
            return None
        for key, value in data.items():
            setattr(devis, key, value)
        db.commit()
        db.refresh(devis)
        return devis

    @avec_session_db
    def delete_devis(self, devis_id: int, db: Session | None = None) -> bool:
        """Supprime un devis et ses lignes."""
        devis = db.query(DevisComparatif).filter(DevisComparatif.id == devis_id).first()
        if devis is None:
            return False
        db.delete(devis)
        db.commit()
        return True

    @avec_session_db
    def add_ligne(self, data: dict, db: Session | None = None) -> LigneDevis:
        """Ajoute une ligne à un devis."""
        ligne = LigneDevis(**data)
        db.add(ligne)
        db.commit()
        db.refresh(ligne)
        return ligne

    @avec_session_db
    def choisir_devis(self, devis_id: int, db: Session | None = None) -> DevisComparatif | None:
        """Marque un devis comme choisi (et les autres du même projet comme refusés)."""
        devis = db.query(DevisComparatif).filter(DevisComparatif.id == devis_id).first()
        if devis is None:
            return None
        # Refuser les autres devis du même projet
        if devis.projet_id:
            db.query(DevisComparatif).filter(
                DevisComparatif.projet_id == devis.projet_id,
                DevisComparatif.id != devis_id,
            ).update({"choisi": False, "statut": "refuse"})
        devis.choisi = True
        devis.statut = "accepte"
        db.commit()
        db.refresh(devis)
        return devis


# ═══════════════════════════════════════════════════════════
# ENTRETIEN SAISONNIER
# ═══════════════════════════════════════════════════════════


class EntretienSaisonnierCrudService(EventBusMixin, BaseService[EntretienSaisonnier]):
    """Service CRUD pour les entretiens saisonniers."""

    _event_source = "entretien_saisonnier"

    def __init__(self):
        super().__init__(model=EntretienSaisonnier, cache_ttl=300)

    @chronometre("maison.saisonnier.lister", seuil_alerte_ms=1500)
    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def get_all_entretiens(
        self,
        filtre_saison: str | None = None,
        filtre_categorie: str | None = None,
        db: Session | None = None,
    ) -> list[EntretienSaisonnier]:
        """Récupère tous les entretiens saisonniers."""
        query = db.query(EntretienSaisonnier)
        if filtre_saison:
            query = query.filter(EntretienSaisonnier.saison == filtre_saison)
        if filtre_categorie:
            query = query.filter(EntretienSaisonnier.categorie == filtre_categorie)
        return query.order_by(EntretienSaisonnier.mois_recommande, EntretienSaisonnier.nom).all()

    @avec_session_db
    def create_entretien(self, data: dict, db: Session | None = None) -> EntretienSaisonnier:
        """Crée un entretien saisonnier personnalisé."""
        entretien = EntretienSaisonnier(**data)
        db.add(entretien)
        db.commit()
        db.refresh(entretien)
        return entretien

    @avec_session_db
    def marquer_fait(
        self, entretien_id: int, db: Session | None = None
    ) -> EntretienSaisonnier | None:
        """Marque un entretien comme fait cette année."""
        entretien = (
            db.query(EntretienSaisonnier).filter(EntretienSaisonnier.id == entretien_id).first()
        )
        if entretien is None:
            return None
        entretien.fait_cette_annee = True
        entretien.date_derniere_realisation = date.today()
        db.commit()
        db.refresh(entretien)
        return entretien

    @avec_session_db
    def reset_annuel(self, db: Session | None = None) -> int:
        """Remet à zéro le statut 'fait' pour la nouvelle année."""
        count = (
            db.query(EntretienSaisonnier)
            .filter(EntretienSaisonnier.fait_cette_annee.is_(True))
            .update({"fait_cette_annee": False})
        )
        db.commit()
        return count

    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def get_alertes_saisonnieres(self, db: Session | None = None) -> list[dict]:
        """Récupère les entretiens saisonniers du mois courant non faits."""
        mois_courant = date.today().month
        entretiens = (
            db.query(EntretienSaisonnier)
            .filter(
                EntretienSaisonnier.alerte_active.is_(True),
                EntretienSaisonnier.fait_cette_annee.is_(False),
                EntretienSaisonnier.mois_rappel == mois_courant,
            )
            .order_by(EntretienSaisonnier.obligatoire.desc(), EntretienSaisonnier.nom)
            .all()
        )
        return [
            {
                "id": e.id,
                "nom": e.nom,
                "categorie": e.categorie,
                "obligatoire": e.obligatoire,
                "professionnel_requis": e.professionnel_requis,
                "cout_estime": float(e.cout_estime or 0),
                "duree_minutes": e.duree_minutes,
            }
            for e in entretiens
        ]

    @avec_session_db
    def delete_entretien(self, entretien_id: int, db: Session | None = None) -> bool:
        """Supprime un entretien saisonnier."""
        entretien = (
            db.query(EntretienSaisonnier).filter(EntretienSaisonnier.id == entretien_id).first()
        )
        if entretien is None:
            return False
        db.delete(entretien)
        db.commit()
        return True


# ═══════════════════════════════════════════════════════════
# RELEVÉS COMPTEURS
# ═══════════════════════════════════════════════════════════


class RelevesCrudService(EventBusMixin, BaseService[ReleveCompteur]):
    """Service CRUD pour les relevés de compteurs."""

    _event_source = "releves"

    def __init__(self):
        super().__init__(model=ReleveCompteur, cache_ttl=300)

    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def get_releves(
        self,
        type_compteur: str | None = None,
        db: Session | None = None,
    ) -> list[ReleveCompteur]:
        """Récupère les relevés de compteurs."""
        query = db.query(ReleveCompteur)
        if type_compteur:
            query = query.filter(ReleveCompteur.type_compteur == type_compteur)
        return query.order_by(ReleveCompteur.date_releve.desc()).all()

    @avec_session_db
    def create_releve(self, data: dict, db: Session | None = None) -> ReleveCompteur:
        """Crée un nouveau relevé avec calcul auto de consommation."""
        # Calculer la consommation par rapport au relevé précédent
        dernier = (
            db.query(ReleveCompteur)
            .filter(ReleveCompteur.type_compteur == data["type_compteur"])
            .order_by(ReleveCompteur.date_releve.desc())
            .first()
        )

        releve = ReleveCompteur(**data)

        if dernier:
            delta_valeur = releve.valeur - dernier.valeur
            delta_jours = (releve.date_releve - dernier.date_releve).days
            if delta_jours > 0:
                releve.consommation_periode = delta_valeur
                releve.nb_jours_periode = delta_jours
                releve.consommation_jour = delta_valeur / delta_jours

                # Détection anomalie (>50% au-dessus de l'objectif)
                if releve.objectif_jour and releve.consommation_jour > releve.objectif_jour * 1.5:
                    releve.anomalie_detectee = True
                    releve.commentaire_anomalie = (
                        f"Consommation journalière ({releve.consommation_jour:.1f}) "
                        f"supérieure à 150% de l'objectif ({releve.objectif_jour:.1f})"
                    )

        db.add(releve)
        db.commit()
        db.refresh(releve)
        logger.info(f"Relevé créé: {releve.id} - {releve.type_compteur}")
        return releve

    @avec_session_db
    def delete_releve(self, releve_id: int, db: Session | None = None) -> bool:
        """Supprime un relevé."""
        releve = db.query(ReleveCompteur).filter(ReleveCompteur.id == releve_id).first()
        if releve is None:
            return False
        db.delete(releve)
        db.commit()
        return True

    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return={})
    def get_stats_compteur(self, type_compteur: str, db: Session | None = None) -> dict:
        """Statistiques pour un type de compteur."""
        releves = (
            db.query(ReleveCompteur)
            .filter(ReleveCompteur.type_compteur == type_compteur)
            .order_by(ReleveCompteur.date_releve)
            .all()
        )
        if not releves:
            return {}

        consos_jour = [r.consommation_jour for r in releves if r.consommation_jour is not None]
        moyenne_jour = sum(consos_jour) / len(consos_jour) if consos_jour else 0
        anomalies = sum(1 for r in releves if r.anomalie_detectee)

        return {
            "nb_releves": len(releves),
            "dernier_releve": releves[-1].date_releve if releves else None,
            "derniere_valeur": releves[-1].valeur if releves else None,
            "moyenne_conso_jour": moyenne_jour,
            "nb_anomalies": anomalies,
            "objectif_jour": releves[-1].objectif_jour if releves else None,
        }


# ═══════════════════════════════════════════════════════════
# FACTORIES
# ═══════════════════════════════════════════════════════════


@service_factory("nuisibles_crud", tags={"maison", "crud", "nuisibles"})
def get_nuisibles_crud_service() -> NuisiblesCrudService:
    """Factory singleton pour le service CRUD nuisibles."""
    return NuisiblesCrudService()


@service_factory("devis_crud", tags={"maison", "crud", "devis"})
def get_devis_crud_service() -> DevisCrudService:
    """Factory singleton pour le service CRUD devis."""
    return DevisCrudService()


@service_factory("entretien_saisonnier_crud", tags={"maison", "crud", "entretien_saisonnier"})
def get_entretien_saisonnier_crud_service() -> EntretienSaisonnierCrudService:
    """Factory singleton pour le service CRUD entretien saisonnier."""
    return EntretienSaisonnierCrudService()


@service_factory("releves_crud", tags={"maison", "crud", "releves"})
def get_releves_crud_service() -> RelevesCrudService:
    """Factory singleton pour le service CRUD relevés compteurs."""
    return RelevesCrudService()
