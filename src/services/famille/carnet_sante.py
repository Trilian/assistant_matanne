"""
Service Carnet de Santé - Vaccinations, RDV médicaux, courbes de croissance.

Opérations:
- CRUD vaccinations avec rappels
- Suivi des rendez-vous médicaux
- Mesures de croissance et positionnement OMS
- Alertes vaccins et RDV à venir
"""

import json
import logging
from datetime import date as date_type
from datetime import timedelta
from pathlib import Path
from typing import Any, TypedDict

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.models import MesureCroissance, NormeOMS, RendezVousMedical, Vaccin
from src.core.monitoring import chronometre
from src.services.core.base import BaseService
from src.services.core.events import obtenir_bus
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parents[3] / "data"


class AlerteVaccinDict(TypedDict):
    """Alerte pour un vaccin en retard ou à faire."""

    vaccin_nom: str
    date_prevue: date_type
    jours_retard: int
    enfant_id: int


class PositionOMSDict(TypedDict):
    """Positionnement de la mesure sur les courbes OMS."""

    percentile_estime: str
    zone: str  # "normal", "attention", "alerte"
    p3: float
    p50: float
    p97: float


class ServiceCarnetSante(BaseService[Vaccin]):
    """Service de gestion du carnet de santé numérique.

    Hérite de BaseService[Vaccin] pour le CRUD générique sur les vaccins.
    Inclut la gestion des RDV médicaux, mesures de croissance,
    et le positionnement sur les courbes OMS.
    """

    def __init__(self):
        super().__init__(model=Vaccin, cache_ttl=600)
        self._calendrier_vaccinal: list[dict[str, Any]] | None = None
        self._normes_oms: dict[str, Any] | None = None

    # ═══════════════════════════════════════════════════════════
    # DONNÉES DE RÉFÉRENCE
    # ═══════════════════════════════════════════════════════════

    def _charger_calendrier_vaccinal(self) -> list[dict[str, Any]]:
        """Charge le calendrier vaccinal français depuis le fichier JSON."""
        if self._calendrier_vaccinal is None:
            chemin = DATA_DIR / "calendrier_vaccinal_fr.json"
            if chemin.exists():
                with open(chemin, encoding="utf-8") as f:
                    data = json.load(f)
                self._calendrier_vaccinal = data.get("vaccins", [])
            else:
                logger.warning("Fichier calendrier vaccinal non trouvé: %s", chemin)
                self._calendrier_vaccinal = []
        return self._calendrier_vaccinal

    def _charger_normes_oms(self) -> dict[str, Any]:
        """Charge les normes OMS depuis le fichier JSON."""
        if self._normes_oms is None:
            chemin = DATA_DIR / "normes_oms.json"
            if chemin.exists():
                with open(chemin, encoding="utf-8") as f:
                    self._normes_oms = json.load(f)
            else:
                logger.warning("Fichier normes OMS non trouvé: %s", chemin)
                self._normes_oms = {}
        return self._normes_oms

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

    @chronometre("carnet_sante.alertes_vaccins", seuil_alerte_ms=1500)
    @avec_cache(ttl=600, key_func=lambda self, child_id: f"alertes_vaccins_{child_id}")
    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def obtenir_alertes_vaccins(
        self, child_id: int, *, db: Session | None = None
    ) -> list[AlerteVaccinDict]:
        """Identifie les vaccins en retard ou à planifier bientôt."""
        if db is None:
            return []
        alertes: list[AlerteVaccinDict] = []
        aujourd_hui = date_type.today()
        rappels_a_venir = (
            db.query(Vaccin)
            .filter(
                and_(
                    Vaccin.child_id == child_id,
                    Vaccin.rappel_prevu.isnot(None),
                    Vaccin.rappel_prevu <= aujourd_hui + timedelta(days=30),
                )
            )
            .all()
        )
        for v in rappels_a_venir:
            if v.rappel_prevu:
                jours_retard = (aujourd_hui - v.rappel_prevu).days
                alertes.append(
                    AlerteVaccinDict(
                        vaccin_nom=v.nom,
                        date_prevue=v.rappel_prevu,
                        jours_retard=max(0, jours_retard),
                        enfant_id=child_id,
                    )
                )
        return sorted(alertes, key=lambda a: a["jours_retard"], reverse=True)

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
    # MESURES DE CROISSANCE
    # ═══════════════════════════════════════════════════════════

    @chronometre("carnet_sante.mesures_enfant", seuil_alerte_ms=1000)
    @avec_cache(ttl=300, key_func=lambda self, child_id: f"mesures_{child_id}")
    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def obtenir_mesures(
        self, child_id: int, *, db: Session | None = None
    ) -> list[MesureCroissance]:
        """Récupère les mesures de croissance d'un enfant."""
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
        """Ajoute une mesure de croissance."""
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

    def positionner_sur_oms(
        self,
        sexe: str,
        type_mesure: str,
        age_mois: float,
        valeur: float,
    ) -> PositionOMSDict | None:
        """Positionne une mesure par rapport aux normes OMS.

        Args:
            sexe: "garcon" ou "fille"
            type_mesure: "poids", "taille" ou "perimetre_cranien"
            age_mois: Âge en mois
            valeur: Valeur mesurée

        Returns:
            Dict avec percentile estimé et zone ou None si données manquantes.
        """
        normes = self._charger_normes_oms()
        cle_sexe = "garcons" if sexe == "garcon" else "filles"
        donnees = normes.get(cle_sexe, {}).get(type_mesure, [])

        if not donnees:
            return None

        # Trouver la tranche d'âge la plus proche
        plus_proche = min(donnees, key=lambda d: abs(d["age_mois"] - age_mois))

        p3 = plus_proche["p3"]
        p15 = plus_proche["p15"]
        p50 = plus_proche["p50"]
        p85 = plus_proche["p85"]
        p97 = plus_proche["p97"]

        # Estimer la zone
        if valeur < p3:
            zone = "alerte"
            percentile = "<P3"
        elif valeur < p15:
            zone = "attention"
            percentile = "P3-P15"
        elif valeur <= p85:
            zone = "normal"
            percentile = "P15-P85"
        elif valeur <= p97:
            zone = "attention"
            percentile = "P85-P97"
        else:
            zone = "alerte"
            percentile = ">P97"

        return PositionOMSDict(
            percentile_estime=percentile,
            zone=zone,
            p3=p3,
            p50=p50,
            p97=p97,
        )

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
                "poids": float(derniere_mesure.poids_kg)
                if derniere_mesure and derniere_mesure.poids_kg
                else None,
                "taille": float(derniere_mesure.taille_cm)
                if derniere_mesure and derniere_mesure.taille_cm
                else None,
                "date": derniere_mesure.date_mesure.isoformat() if derniere_mesure else None,
            },
            "prochain_rdv": {
                "specialite": prochain_rdv.specialite if prochain_rdv else None,
                "date": prochain_rdv.date_rdv.isoformat() if prochain_rdv else None,
            },
        }


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("carnet_sante", tags={"famille", "sante"})
def obtenir_service_carnet_sante() -> ServiceCarnetSante:
    """Factory pour le service carnet de santé (singleton via ServiceRegistry)."""
    return ServiceCarnetSante()


# Alias anglais
get_carnet_sante_service = obtenir_service_carnet_sante
