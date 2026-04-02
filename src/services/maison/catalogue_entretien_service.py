"""
Service Catalogue Entretien — Sync automatique catalogue JSON → tâches DB.

Quand un objet_maison existe dans la base, génère automatiquement les
TacheEntretien correspondantes depuis entretien_catalogue.json.
"""

import json
import logging
from datetime import date, timedelta
from pathlib import Path

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.models import ObjetMaison, TacheEntretien
from src.core.monitoring import chronometre
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)

CATALOGUE_PATH = Path("data/reference/entretien_catalogue.json")


class SyncResult(BaseModel):
    """Résultat de la synchronisation catalogue."""

    taches_creees: int = 0
    taches_existantes: int = 0
    objets_traites: int = 0
    erreurs: list[str] = Field(default_factory=list)


class CatalogueEntretienService:
    """Synchronise le catalogue d'entretien JSON avec les tâches DB."""

    def __init__(self):
        self._catalogue: dict | None = None

    @property
    def catalogue(self) -> dict:
        """Charge le catalogue en lazy, met en mémoire."""
        if self._catalogue is None:
            self._catalogue = self._charger_catalogue()
        return self._catalogue

    @staticmethod
    def _charger_catalogue() -> dict:
        """Charge le catalogue JSON depuis le disque."""
        if not CATALOGUE_PATH.exists():
            logger.warning(f"Catalogue introuvable: {CATALOGUE_PATH}")
            return {}
        with open(CATALOGUE_PATH, encoding="utf-8") as f:
            return json.load(f)

    def _lookup_taches_catalogue(self, type_objet: str) -> list[dict]:
        """Trouve les tâches d'entretien pour un type d'objet."""
        categories = self.catalogue.get("categories", {})
        for _cat_key, cat_data in categories.items():
            objets = cat_data.get("objets", {})
            if type_objet in objets:
                return objets[type_objet].get("taches", [])
        return []

    def _lookup_duree_vie(self, type_objet: str) -> int | None:
        """Trouve la durée de vie pour un type d'objet."""
        categories = self.catalogue.get("categories", {})
        for _cat_key, cat_data in categories.items():
            objets = cat_data.get("objets", {})
            if type_objet in objets:
                return objets[type_objet].get("duree_vie_ans")
        return None

    @chronometre("maison.sync_catalogue", seuil_alerte_ms=3000)
    @avec_session_db
    @avec_gestion_erreurs(default_return=None)
    def sync_catalogue(self, db: Session | None = None) -> SyncResult:
        """Synchronise le catalogue avec les objets en base.

        Pour chaque ObjetMaison, vérifie si les tâches d'entretien
        correspondantes existent déjà. Crée les manquantes.
        """
        result = SyncResult()

        # Récupérer tous les objets maison avec un type renseigné
        objets = db.query(ObjetMaison).filter(ObjetMaison.type.isnot(None)).all()

        for objet in objets:
            result.objets_traites += 1
            type_objet = self._normaliser_type(objet.type)
            taches_catalogue = self._lookup_taches_catalogue(type_objet)

            if not taches_catalogue:
                continue

            for tache_def in taches_catalogue:
                nom_tache = f"{tache_def['nom']} — {objet.nom}"
                # Vérifier si la tâche existe déjà
                existe = (
                    db.query(TacheEntretien)
                    .filter(
                        TacheEntretien.nom == nom_tache,
                    )
                    .first()
                )

                if existe:
                    result.taches_existantes += 1
                    continue

                # Créer la tâche
                frequence = tache_def.get("frequence_jours")
                prochaine = date.today() + timedelta(days=frequence) if frequence else None

                tache = TacheEntretien(
                    nom=nom_tache,
                    description=tache_def.get("description", ""),
                    categorie="entretien",
                    frequence_jours=frequence,
                    duree_minutes=tache_def.get("duree_min", 30),
                    prochaine_fois=prochaine,
                    fait=False,
                    priorite="normale",
                )
                db.add(tache)
                result.taches_creees += 1

        if result.taches_creees > 0:
            db.commit()
            logger.info(
                f"Sync catalogue: {result.taches_creees} tâches créées, "
                f"{result.objets_traites} objets traités"
            )

        return result

    @avec_cache(ttl=3600)
    def obtenir_taches_par_type(self, type_objet: str) -> list[dict]:
        """Retourne les tâches catalogue pour un type d'objet."""
        return self._lookup_taches_catalogue(self._normaliser_type(type_objet))

    @avec_cache(ttl=3600)
    def obtenir_duree_vie(self, type_objet: str) -> int | None:
        """Retourne la durée de vie catalogue pour un type d'objet."""
        return self._lookup_duree_vie(self._normaliser_type(type_objet))

    @staticmethod
    def _normaliser_type(type_objet: str) -> str:
        """Normalise le type d'objet (minuscules, underscores)."""
        return type_objet.lower().strip().replace(" ", "_").replace("-", "_")


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("catalogue_entretien", tags={"maison"})
def obtenir_catalogue_entretien_service() -> CatalogueEntretienService:
    """Factory singleton pour le service catalogue entretien."""
    return CatalogueEntretienService()


def obtenir_service_catalogue_entretien() -> CatalogueEntretienService:
    """Alias français."""
    return get_catalogue_entretien_service()


# ─── Aliases rétrocompatibilité  ───────────────────────────────
get_catalogue_entretien_service = obtenir_catalogue_entretien_service  # alias rétrocompatibilité 
