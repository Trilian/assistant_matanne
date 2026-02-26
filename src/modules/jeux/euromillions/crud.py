"""
CRUD Euromillions - Opérations base de données
"""

import logging
from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from src.core.decorators import avec_session_db

logger = logging.getLogger(__name__)


@avec_session_db
def ajouter_tirage(
    date_tirage: date,
    numeros: list[int],
    etoiles: list[int],
    jackpot: int | None = None,
    code_my_million: str | None = None,
    db: Session | None = None,
) -> bool:
    """Ajoute un tirage Euromillions en base."""
    from src.core.models.jeux import TirageEuromillions

    existant = db.query(TirageEuromillions).filter_by(date_tirage=date_tirage).first()
    if existant:
        logger.debug(f"Tirage {date_tirage} déjà en base")
        return False

    tirage = TirageEuromillions(
        date_tirage=date_tirage,
        numero_1=numeros[0],
        numero_2=numeros[1],
        numero_3=numeros[2],
        numero_4=numeros[3],
        numero_5=numeros[4],
        etoile_1=etoiles[0],
        etoile_2=etoiles[1],
        jackpot_euros=jackpot,
        code_my_million=code_my_million,
    )
    db.add(tirage)
    db.commit()
    logger.info(f"Tirage Euromillions {date_tirage} ajouté")
    return True


@avec_session_db
def enregistrer_grille(
    numeros: list[int],
    etoiles: list[int],
    source: str = "manuel",
    est_virtuelle: bool = True,
    mise: Decimal = Decimal("2.50"),
    notes: str | None = None,
    db: Session | None = None,
) -> int:
    """Enregistre une grille Euromillions jouée."""
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
    logger.info(f"Grille Euromillions enregistrée (id={grille.id})")
    return grille.id


@avec_session_db
def charger_tirages_db(limite: int = 200, db: Session | None = None) -> list[dict[str, Any]]:
    """Charge les tirages depuis la base de données."""
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
            **{f"numero_{i + 1}": t.numeros[i] for i in range(5)},
            **{f"etoile_{i + 1}": t.etoiles[i] for i in range(2)},
        }
        for t in tirages
    ]


@avec_session_db
def charger_grilles_utilisateur(
    limite: int = 50,
    db: Session | None = None,
) -> list[dict[str, Any]]:
    """Charge les grilles de l'utilisateur."""
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
