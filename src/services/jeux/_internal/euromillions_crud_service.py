"""
Service CRUD Euromillions — Opérations base de données
"""

import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from src.core.decorators import avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class EuromillionsCrudService:
    """Service de persistance des données Euromillions."""

    @avec_session_db
    def inserer_tirages_scraper(
        self, tirages: list[dict[str, Any]], db: Session | None = None
    ) -> int:
        """Insère les tirages récupérés par le scraper."""
        from src.core.models.jeux import TirageEuromillions

        nb_ajoutes = 0
        for t in tirages:
            date_str = t.get("date_tirage", "")
            try:
                if isinstance(date_str, str):
                    date_t = date.fromisoformat(date_str)
                else:
                    date_t = date_str
            except (ValueError, TypeError):
                continue

            existant = db.query(TirageEuromillions).filter_by(date_tirage=date_t).first()
            if existant:
                continue

            numeros = t.get("numeros", [])
            etoiles = t.get("etoiles", [])
            if len(numeros) < 5 or len(etoiles) < 2:
                continue

            tirage = TirageEuromillions(
                date_tirage=date_t,
                numero_1=numeros[0],
                numero_2=numeros[1],
                numero_3=numeros[2],
                numero_4=numeros[3],
                numero_5=numeros[4],
                etoile_1=etoiles[0],
                etoile_2=etoiles[1],
                jackpot_euros=t.get("jackpot_euros"),
                code_my_million=t.get("code_my_million"),
            )
            db.add(tirage)
            nb_ajoutes += 1

        if nb_ajoutes:
            db.commit()
        logger.info(f"{nb_ajoutes} tirages Euromillions insérés")
        return nb_ajoutes

    @avec_session_db
    def obtenir_tirages(self, limite: int = 200, db: Session | None = None) -> list[dict[str, Any]]:
        """Charge les tirages depuis la BD."""
        from src.core.models.jeux import TirageEuromillions

        tirages = (
            db.query(TirageEuromillions)
            .order_by(TirageEuromillions.date_tirage.desc())
            .limit(limite)
            .all()
        )
        return [
            {
                "id": t.id,
                "date_tirage": t.date_tirage,
                "numeros": t.numeros,
                "etoiles": t.etoiles,
                "jackpot_euros": t.jackpot_euros,
                "code_my_million": t.code_my_million,
            }
            for t in tirages
        ]

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
        from src.core.models.jeux import GrilleEuromillions

        grille = GrilleEuromillions(
            numero_1=numeros[0],
            numero_2=numeros[1],
            numero_3=numeros[2],
            numero_4=numeros[3],
            numero_5=numeros[4],
            etoile_1=etoiles[0],
            etoile_2=etoiles[1],
            source_prediction=source,
            est_virtuelle=est_virtuelle,
            mise=mise,
            notes=notes,
        )
        db.add(grille)
        db.commit()
        return grille.id

    @avec_session_db
    def obtenir_grilles(self, limite: int = 50, db: Session | None = None) -> list[dict[str, Any]]:
        """Charge les grilles utilisateur."""
        from src.core.models.jeux import GrilleEuromillions

        grilles = (
            db.query(GrilleEuromillions)
            .order_by(GrilleEuromillions.date_creation.desc())
            .limit(limite)
            .all()
        )
        return [
            {
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
            for g in grilles
        ]

    @avec_session_db
    def sauvegarder_stats(self, stats: dict[str, Any], db: Session | None = None) -> None:
        """Sauvegarde les statistiques calculées."""
        from src.core.models.jeux import StatistiquesEuromillions

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
def get_euromillions_crud_service() -> EuromillionsCrudService:
    """Factory pour le service CRUD Euromillions."""
    return EuromillionsCrudService()
