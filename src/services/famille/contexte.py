"""
Service Contexte Familial — Agrège toutes les sources en un seul appel.

Fournit un snapshot contextuel de la vie familiale :
- Météo actuelle et prévisions 7j
- Jours fériés / ponts / fermetures crèche proches
- Anniversaires dans les 14 prochains jours
- Profil Jules (âge, prochains repères de développement)
- Documents expirant dans 30 jours
- Routines du moment
- Activités à venir (7j)
- Achats urgents (top 5)
"""

import json
import logging
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from src.core.decorators import avec_cache, avec_gestion_erreurs
from src.core.monitoring import chronometre
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)

# Référentiel de développement Jules
_REFERENTIEL_JULES_PATH = Path(__file__).resolve().parents[3] / "data" / "reference" / "normes_oms.json"


def _charger_referentiel_jules() -> dict[str, Any]:
    """Charge le référentiel de développement utilisé pour Jules."""
    try:
        with open(_REFERENTIEL_JULES_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning("Impossible de charger le référentiel Jules: %s", e)
        return {}


class ContexteFamilialService:
    """Service d'agrégation du contexte familial.

    Un seul appel retourne toutes les données contextuelles
    pour le hub famille frontend.
    """

    def __init__(self):
        self._referentiel_jules: dict[str, Any] | None = None

    @property
    def referentiel_jules(self) -> dict[str, Any]:
        if self._referentiel_jules is None:
            self._referentiel_jules = _charger_referentiel_jules()
        return self._referentiel_jules

    # ═══════════════════════════════════════════════════════════
    # AGRÉGATION PRINCIPALE
    # ═══════════════════════════════════════════════════════════

    @chronometre(nom="contexte_familial.get", seuil_alerte_ms=5000)
    @avec_gestion_erreurs(default_return={})
    @avec_cache(ttl=300)  # 5 min
    def obtenir_contexte(self) -> dict[str, Any]:
        """Retourne le contexte familial complet."""
        aujourd_hui = date.today()
        maintenant = datetime.now()

        return {
            "meteo": self._section_meteo(),
            "jours_speciaux": self._section_jours_speciaux(aujourd_hui),
            "anniversaires_proches": self._section_anniversaires(aujourd_hui),
            "jules": self._section_jules(aujourd_hui),
            "documents_expirants": self._section_documents(),
            "routines_du_moment": self._section_routines(maintenant),
            "activites_a_venir": self._section_activites(aujourd_hui),
            "achats_urgents": self._section_achats_urgents(),
        }

    # ═══════════════════════════════════════════════════════════
    # SECTIONS INDIVIDUELLES
    # ═══════════════════════════════════════════════════════════

    def _section_meteo(self) -> dict[str, Any] | None:
        """Météo actuelle + prévisions 7j."""
        try:
            from src.services.integrations.weather.service import obtenir_service_meteo

            service = obtenir_service_meteo()
            previsions = service.get_previsions(nb_jours=7)
            if not previsions:
                return None

            aujourd_hui_meteo = previsions[0]
            return {
                "emoji": aujourd_hui_meteo.icone,
                "temperature_min": aujourd_hui_meteo.temperature_min,
                "temperature_max": aujourd_hui_meteo.temperature_max,
                "condition": aujourd_hui_meteo.condition,
                "precipitation_mm": aujourd_hui_meteo.precipitation_mm,
                "vent_km_h": aujourd_hui_meteo.vent_km_h,
                "previsions_7j": [
                    {
                        "date": p.date.isoformat(),
                        "emoji": p.icone,
                        "temp_min": p.temperature_min,
                        "temp_max": p.temperature_max,
                        "condition": p.condition,
                        "precipitation_mm": p.precipitation_mm,
                    }
                    for p in previsions
                ],
            }
        except Exception as e:
            logger.warning("Erreur section météo: %s", e)
            return None

    def _section_jours_speciaux(self, aujourd_hui: date) -> list[dict[str, Any]]:
        """Jours fériés / ponts / crèche dans les 10 prochains jours."""
        try:
            from src.services.famille.jours_speciaux import obtenir_service_jours_speciaux

            service = obtenir_service_jours_speciaux()
            prochains = service.prochains_jours_speciaux(nb=15)
            limite = aujourd_hui + timedelta(days=10)

            return [
                {
                    "nom": j.nom,
                    "date": j.date_jour.isoformat(),
                    "type": j.type,
                    "jours_restants": (j.date_jour - aujourd_hui).days,
                }
                for j in prochains
                if j.date_jour <= limite
            ]
        except Exception as e:
            logger.warning("Erreur section jours spéciaux: %s", e)
            return []

    def _section_anniversaires(self, aujourd_hui: date) -> list[dict[str, Any]]:
        """Anniversaires dans les 14 prochains jours."""
        try:
            from src.core.decorators import avec_session_db
            from src.core.models import AnniversaireFamille

            from src.api.utils import executer_avec_session

            with executer_avec_session() as session:
                items = (
                    session.query(AnniversaireFamille)
                    .filter(AnniversaireFamille.actif == True)  # noqa: E712
                    .all()
                )
                result = []
                for a in items:
                    jours_restants = a.jours_restants
                    if jours_restants is not None and jours_restants <= 14:
                        result.append({
                            "id": a.id,
                            "nom_personne": a.nom_personne,
                            "age": a.age,
                            "relation": a.relation,
                            "jours_restants": jours_restants,
                            "idees_cadeaux": a.idees_cadeaux,
                        })
                return sorted(result, key=lambda x: x["jours_restants"])
        except Exception as e:
            logger.warning("Erreur section anniversaires: %s", e)
            return []

    def _section_jules(self, aujourd_hui: date) -> dict[str, Any] | None:
        """Profil Jules + prochains repères de développement attendus."""
        try:
            from src.services.famille.jules import obtenir_service_jules

            service = obtenir_service_jules()
            date_naissance = service.get_date_naissance_jules()
            if not date_naissance:
                return None

            age_mois = service.get_age_mois()
            prochains_jalons = self._prochains_jalons_developpement(age_mois)

            return {
                "age_mois": age_mois,
                "date_naissance": date_naissance.isoformat(),
                "prochains_jalons": prochains_jalons,
            }
        except Exception as e:
            logger.warning("Erreur section Jules: %s", e)
            return None

    def _section_documents(self) -> list[dict[str, Any]]:
        """Documents expirant dans les 30 prochains jours."""
        try:
            from src.services.famille.documents import obtenir_service_documents

            service = obtenir_service_documents()
            alertes = service.obtenir_alertes_expiration(jours=30)
            if not alertes:
                return []

            result = []
            for doc in alertes:
                jours = doc.get("jours_avant_expiration", 30)
                severite = "danger" if jours <= 7 else ("warning" if jours <= 14 else "info")
                result.append({
                    "titre": doc.get("titre", "Document"),
                    "jours_restants": jours,
                    "severite": severite,
                })
            return result
        except Exception as e:
            logger.warning("Erreur section documents: %s", e)
            return []

    def _section_routines(self, maintenant: datetime) -> list[dict[str, Any]]:
        """Routines du moment (matin/soir selon l'heure)."""
        try:
            from src.core.models import Routine

            from src.api.utils import executer_avec_session

            heure = maintenant.hour
            moment = "matin" if heure < 14 else "soir"

            with executer_avec_session() as session:
                items = (
                    session.query(Routine)
                    .filter(Routine.actif == True)  # noqa: E712
                    .all()
                )
                result = []
                for r in items:
                    cat = getattr(r, "categorie", "")
                    if moment in (cat or "").lower() or not cat:
                        result.append({
                            "id": r.id,
                            "nom": r.nom,
                            "categorie": cat,
                        })
                return result
        except Exception as e:
            logger.warning("Erreur section routines: %s", e)
            return []

    def _section_activites(self, aujourd_hui: date) -> list[dict[str, Any]]:
        """Activités des 7 prochains jours."""
        try:
            from src.core.models import ActiviteFamille

            from src.api.utils import executer_avec_session

            limite = aujourd_hui + timedelta(days=7)

            with executer_avec_session() as session:
                items = (
                    session.query(ActiviteFamille)
                    .filter(
                        ActiviteFamille.date >= aujourd_hui,
                        ActiviteFamille.date <= limite,
                    )
                    .order_by(ActiviteFamille.date)
                    .all()
                )
                return [
                    {
                        "id": a.id,
                        "titre": a.titre,
                        "date": a.date.isoformat() if a.date else None,
                        "type_activite": getattr(a, "type_activite", None),
                        "lieu": getattr(a, "lieu", None),
                    }
                    for a in items
                ]
        except Exception as e:
            logger.warning("Erreur section activités: %s", e)
            return []

    def _section_achats_urgents(self) -> list[dict[str, Any]]:
        """Top 5 achats urgents non achetés."""
        try:
            from src.services.famille.achats import obtenir_service_achats_famille

            service = obtenir_service_achats_famille()
            urgents = service.get_urgents(limit=5)
            return [
                {
                    "id": a.id,
                    "nom": a.nom,
                    "categorie": a.categorie,
                    "priorite": a.priorite,
                    "prix_estime": a.prix_estime,
                    "suggere_par": a.suggere_par,
                }
                for a in urgents
            ]
        except Exception as e:
            logger.warning("Erreur section achats urgents: %s", e)
            return []

    # ═══════════════════════════════════════════════════════════
    # HELPERS JULES
    # ═══════════════════════════════════════════════════════════

    def _prochains_jalons_developpement(self, age_mois: int) -> list[str]:
        """Retourne les prochains repères de développement attendus pour cet âge."""
        referentiel = self.referentiel_jules
        if not referentiel:
            return []

        jalons = []
        etapes = referentiel.get("etapes_developpement", referentiel.get("milestones", {}))
        if isinstance(etapes, dict):
            for tranche, desc_list in etapes.items():
                try:
                    age_tranche = int(tranche.split("_")[0]) if "_" in tranche else int(tranche)
                except (ValueError, IndexError):
                    continue
                if age_mois <= age_tranche <= age_mois + 3:
                    if isinstance(desc_list, list):
                        jalons.extend(desc_list[:3])
                    elif isinstance(desc_list, str):
                        jalons.append(desc_list)

        return jalons[:5]


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("contexte_familial", tags={"famille"})
def obtenir_service_contexte_familial() -> ContexteFamilialService:
    """Factory singleton pour ContexteFamilialService."""
    return ContexteFamilialService()


# Alias de compatibilité
ContexteFamilleService = ContexteFamilialService
get_contexte_familial_service = obtenir_service_contexte_familial
