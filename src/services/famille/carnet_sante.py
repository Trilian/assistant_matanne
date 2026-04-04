"""
Service Carnet de Santé - Vaccinations, RDV médicaux et suivi santé.

Opérations:
- CRUD vaccinations avec rappels
- Suivi des rendez-vous médicaux
- Mesures de santé privées si besoin
- Alertes vaccins et RDV à venir
"""

import json
import logging
from datetime import date as date_type
from datetime import timedelta
from pathlib import Path
from typing import Any

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.models import MesureCroissance, RendezVousMedical, Vaccin
from src.core.monitoring import chronometre
from src.services.core.base import BaseService
from src.services.core.events import obtenir_bus
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parents[3] / "data"


class ServiceCarnetSante(BaseService[Vaccin]):
    """Service de gestion du carnet de santé numérique.

    Hérite de `BaseService[Vaccin]` pour le CRUD générique sur les vaccins.
    Inclut la gestion des RDV médicaux et d'un suivi santé léger,
    sans exposition de courbes de référence dans le produit.
    """

    def __init__(self):
        super().__init__(model=Vaccin, cache_ttl=600)
        self._calendrier_vaccinal: list[dict[str, Any]] | None = None

    # ═══════════════════════════════════════════════════════════
    # DONNÉES DE RÉFÉRENCE
    # ═══════════════════════════════════════════════════════════

    def _charger_calendrier_vaccinal(self) -> list[dict[str, Any]]:
        """Charge le calendrier vaccinal de référence, limité aux rappels à partir de 6 ans."""
        if self._calendrier_vaccinal is None:
            chemin = DATA_DIR / "reference" / "calendrier_vaccinal_fr.json"
            if chemin.exists():
                with open(chemin, encoding="utf-8") as f:
                    data = json.load(f)

                vaccins = data.get("vaccins", [])
                calendrier_filtre: list[dict[str, Any]] = []
                for vaccin in vaccins:
                    doses = [
                        dose
                        for dose in vaccin.get("doses", [])
                        if int(dose.get("age_mois", 0) or 0) >= 72
                    ]
                    if not doses:
                        continue
                    calendrier_filtre.append({**vaccin, "doses": doses})

                self._calendrier_vaccinal = calendrier_filtre
            else:
                logger.warning("Fichier calendrier vaccinal non trouvé: %s", chemin)
                self._calendrier_vaccinal = []
        return self._calendrier_vaccinal

    # ═══════════════════════════════════════════════════════════
    # VACCINATIONS
    # ═══════════════════════════════════════════════════════════

    @chronometre("carnet_sante.vaccins_enfant", seuil_alerte_ms=1000)
    @avec_cache(ttl=300, key_func=lambda self, child_id: f"vaccins_{child_id}")
    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def obtenir_vaccins(self, child_id: int, *, db: Session | None = None) -> list[Vaccin]:
        """Récupère tous les vaccins d'un enfant."""
        if db is None:
            return []
        return (
            db.query(Vaccin)
            .filter_by(child_id=child_id)
            .order_by(Vaccin.date_vaccination.desc())
            .all()
        )

    @chronometre("carnet_sante.ajouter_vaccin", seuil_alerte_ms=2000)
    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def ajouter_vaccin(self, data: dict[str, Any], *, db: Session | None = None) -> Vaccin | None:
        """Ajoute un vaccin au carnet de santé."""
        if db is None:
            return None
        vaccin = Vaccin(**data)
        db.add(vaccin)
        db.commit()
        db.refresh(vaccin)
        logger.info("Vaccin ajouté: %s pour enfant %d", vaccin.nom, vaccin.child_id)
        obtenir_bus().emettre(
            "carnet_sante.vaccin_ajoute",
            {"vaccin_id": vaccin.id, "nom": vaccin.nom},
            source="ServiceCarnetSante",
        )
        return vaccin

    # ═══════════════════════════════════════════════════════════
    # RENDEZ-VOUS MÉDICAUX
    # ═══════════════════════════════════════════════════════════

    @chronometre("carnet_sante.rdv_a_venir", seuil_alerte_ms=1000)
    @avec_cache(ttl=300)
    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def obtenir_rdv_a_venir(
        self, *, jours: int = 60, db: Session | None = None
    ) -> list[RendezVousMedical]:
        """Récupère les prochains RDV médicaux (tous membres famille)."""
        if db is None:
            return []
        limite = date_type.today() + timedelta(days=jours)
        return (
            db.query(RendezVousMedical)
            .filter(RendezVousMedical.date_rdv >= func.now())
            .filter(RendezVousMedical.date_rdv <= limite)
            .order_by(RendezVousMedical.date_rdv.asc())
            .all()
        )

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def ajouter_rdv(
        self, data: dict[str, Any], *, db: Session | None = None
    ) -> RendezVousMedical | None:
        """Ajoute un rendez-vous médical."""
        if db is None:
            return None
        rdv = RendezVousMedical(**data)
        db.add(rdv)
        db.commit()
        db.refresh(rdv)
        logger.info("RDV médical ajouté: %s le %s", rdv.specialite, rdv.date_rdv)
        obtenir_bus().emettre(
            "carnet_sante.rdv_ajoute",
            {"rdv_id": rdv.id, "specialite": rdv.specialite},
            source="ServiceCarnetSante",
        )
        return rdv

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def obtenir_historique_rdv(
        self,
        *,
        child_id: int | None = None,
        membre: str | None = None,
        db: Session | None = None,
    ) -> list[RendezVousMedical]:
        """Récupère l'historique des RDV médicaux (filtré optionnellement)."""
        if db is None:
            return []
        query = db.query(RendezVousMedical)
        if child_id is not None:
            query = query.filter_by(child_id=child_id)
        if membre is not None:
            query = query.filter_by(membre_famille=membre)
        return query.order_by(RendezVousMedical.date_rdv.desc()).all()

    # ═══════════════════════════════════════════════════════════
    # MESURES DE SUIVI
    # ═══════════════════════════════════════════════════════════

    @chronometre("carnet_sante.mesures_enfant", seuil_alerte_ms=1000)
    @avec_cache(ttl=300, key_func=lambda self, child_id: f"mesures_{child_id}")
    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def obtenir_mesures(
        self, child_id: int, *, db: Session | None = None
    ) -> list[MesureCroissance]:
        """Récupère les mesures de suivi santé d'un enfant."""
        if db is None:
            return []
        return (
            db.query(MesureCroissance)
            .filter_by(child_id=child_id)
            .order_by(MesureCroissance.date_mesure.desc())
            .all()
        )

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def ajouter_mesure(
        self, data: dict[str, Any], *, db: Session | None = None
    ) -> MesureCroissance | None:
        """Ajoute une mesure ponctuelle au suivi santé."""
        if db is None:
            return None
        mesure = MesureCroissance(**data)
        db.add(mesure)
        db.commit()
        db.refresh(mesure)
        logger.info("Mesure ajoutée: enfant %d à %s mois", mesure.child_id, mesure.age_mois)
        obtenir_bus().emettre(
            "carnet_sante.mesure_ajoutee",
            {"mesure_id": mesure.id, "child_id": mesure.child_id},
            source="ServiceCarnetSante",
        )
        return mesure

    # ═══════════════════════════════════════════════════════════
    # STATISTIQUES
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=600)
    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def obtenir_resume_sante(self, child_id: int, *, db: Session | None = None) -> dict[str, Any]:
        """Résumé de santé complet pour un enfant."""
        if db is None:
            return {}
        nb_vaccins = db.query(func.count(Vaccin.id)).filter_by(child_id=child_id).scalar() or 0
        derniere_mesure = (
            db.query(MesureCroissance)
            .filter_by(child_id=child_id)
            .order_by(MesureCroissance.date_mesure.desc())
            .first()
        )
        prochain_rdv = (
            db.query(RendezVousMedical)
            .filter(
                and_(
                    RendezVousMedical.child_id == child_id,
                    RendezVousMedical.date_rdv >= func.now(),
                )
            )
            .order_by(RendezVousMedical.date_rdv.asc())
            .first()
        )

        return {
            "nb_vaccins": nb_vaccins,
            "derniere_mesure": {
                "date": derniere_mesure.date_mesure.isoformat() if derniere_mesure else None,
                "notes": derniere_mesure.notes if derniere_mesure else None,
            },
            "prochain_rdv": {
                "specialite": prochain_rdv.specialite if prochain_rdv else None,
                "date": prochain_rdv.date_rdv.isoformat() if prochain_rdv else None,
            },
        }

    # Compatibility aliases for older UI code
    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def lister_vaccins(
        self, child_id: int | None = None, *, db: Session | None = None
    ) -> list[Vaccin]:
        """Alias historique: retourne les vaccins (optionnellement filtrés par enfant)."""
        if db is None:
            return []
        query = db.query(Vaccin).order_by(Vaccin.date_vaccination.desc())
        if child_id is not None:
            query = query.filter_by(child_id=child_id)
        return query.all()

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def lister_prochains_rdv(self, limite: int = 10, *, db: Session | None = None):
        """Alias historique: retourne les prochains RDV (limit)."""
        if db is None:
            return []
        return (
            db.query(RendezVousMedical)
            .filter(RendezVousMedical.date_rdv >= func.now())
            .order_by(RendezVousMedical.date_rdv.asc())
            .limit(limite)
            .all()
        )

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def lister_mesures(
        self, child_id: int | None = None, *, db: Session | None = None
    ) -> list[MesureCroissance]:
        """Alias historique: retourne les mesures de suivi (optionnellement pour un enfant)."""
        if db is None:
            return []
        query = db.query(MesureCroissance).order_by(MesureCroissance.date_mesure.desc())
        if child_id is not None:
            query = query.filter_by(child_id=child_id)
        return query.all()


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("carnet_sante", tags={"famille", "sante"})
def obtenir_service_carnet_sante() -> ServiceCarnetSante:
    """Factory pour le service carnet de santé (singleton via ServiceRegistry)."""
    return ServiceCarnetSante()


# Alias anglais
get_carnet_sante_service = obtenir_service_carnet_sante
