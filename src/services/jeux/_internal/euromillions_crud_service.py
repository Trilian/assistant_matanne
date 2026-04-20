"""
Service CRUD Euromillions — Opérations base de données.

Hérite de LoterieCrudBase pour les opérations CRUD communes et
ajoute les spécificités Euromillions (étoiles, code My Million, stats).
"""

import logging
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from src.core.decorators import avec_session_db
from src.core.models.jeux import (
    GrilleEuromillions,
    StatistiquesEuromillions,
    TirageEuromillions,
)
from src.services.core.registry import service_factory
from src.services.jeux._internal.loterie_base import LoterieCrudBase

logger = logging.getLogger(__name__)


class EuromillionsCrudService(LoterieCrudBase):
    """Service de persistance des données Euromillions.

    Hérite de LoterieCrudBase pour: inserer_tirages, obtenir_tirages,
    enregistrer_grille, obtenir_grilles.
    """

    _tirage_cls = TirageEuromillions
    _grille_cls = GrilleEuromillions
    _cout_defaut = Decimal("2.50")
    _nom_jeu = "euromillions"

    # ── Méthodes template LoterieCrudBase ────────────────

    def _champs_secondaires_tirage(self, data: dict[str, Any]) -> dict[str, int] | None:
        etoiles = data.get("etoiles", [])
        return {"etoile_1": etoiles[0], "etoile_2": etoiles[1]} if len(etoiles) >= 2 else None

    def _champs_extra_tirage(self, data: dict[str, Any]) -> dict[str, Any]:
        extras: dict[str, Any] = {}
        code = data.get("code_my_million")
        if code:
            extras["code_my_million"] = code
        return extras

    def _serialiser_tirage(self, t: Any) -> dict[str, Any]:
        return {
            "id": t.id,
            "date_tirage": t.date_tirage,
            "numeros": t.numeros,
            "etoiles": t.etoiles,
            "jackpot_euros": t.jackpot_euros,
            "code_my_million": t.code_my_million,
        }

    def _serialiser_grille(self, g: Any) -> dict[str, Any]:
        return {
            "id": g.id,
            "numeros": g.numeros,
            "etoiles": g.etoiles,
            "source": g.source_prediction,
            "est_virtuelle": g.est_virtuelle,
            "mise": float(g.mise),
            "gain": float(g.gain) if g.gain else None,
            "rang": g.rang,
            "date_creation": g.date_creation,
        }

    # ── CRUD (délégué à LoterieCrudBase) ─────────────────

    @avec_session_db
    def inserer_tirages_scraper(
        self, tirages: list[dict[str, Any]], db: Session | None = None
    ) -> int:
        """Insère les tirages récupérés par le scraper."""
        return self._inserer_tirages_impl(tirages, db)

    @avec_session_db
    def obtenir_tirages(self, limite: int = 200, db: Session | None = None) -> list[dict[str, Any]]:
        """Charge les tirages depuis la BD."""
        return self._charger_tirages_impl(db, limite=limite)

    @avec_session_db
    def enregistrer_grille(
        self,
        numeros: list[int],
        etoiles: list[int],
        source: str = "manuel",
        est_virtuelle: bool = True,
        mise: Decimal = Decimal("2.50"),
        notes: str | None = None,
        db: Session | None = None,
    ) -> int:
        """Enregistre une grille Euromillions."""
        return self._enregistrer_grille_impl(
            db,
            numeros,
            {"etoile_1": etoiles[0], "etoile_2": etoiles[1]},
            source,
            est_virtuelle,
            mise,
            notes,
        )

    @avec_session_db
    def obtenir_grilles(self, limite: int = 50, db: Session | None = None) -> list[dict[str, Any]]:
        """Charge les grilles utilisateur."""
        return self._charger_grilles_impl(db, limite=limite)

    # ── Spécifique Euromillions ──────────────────────────

    @avec_session_db
    def sauvegarder_stats(self, stats: dict[str, Any], db: Session | None = None) -> None:
        """Sauvegarde les statistiques calculées."""
        assert db is not None
        entry = StatistiquesEuromillions(
            frequences_numeros=stats.get("frequences_numeros"),
            frequences_etoiles=stats.get("frequences_etoiles"),
            numeros_chauds=stats.get("numeros_chauds"),
            numeros_froids=stats.get("numeros_froids"),
            numeros_retard=stats.get("numeros_retard"),
            etoiles_chaudes=stats.get("etoiles_chaudes"),
            etoiles_froides=stats.get("etoiles_froides"),
            somme_moyenne=stats.get("somme_moyenne"),
            paires_frequentes=stats.get("paires_frequentes"),
            nb_tirages_analyses=stats.get("nb_tirages", 0),
        )
        db.add(entry)
        db.commit()


@service_factory("euromillions_crud", tags={"jeux", "crud", "euromillions"})
def obtenir_euromillions_crud_service() -> EuromillionsCrudService:
    """Factory pour le service CRUD Euromillions."""
    return EuromillionsCrudService()
