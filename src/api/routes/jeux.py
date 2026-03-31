"""Routes API pour les jeux (Paris sportifs, Loto, Euromillions).

Agregateur: inclut 4 sous-routeurs thematiques:
- jeux_paris       : Equipes, Matchs, Paris, Bankroll, Series, Predictions, Cotes
- jeux_loto        : Loto tirages, grilles, stats, generation IA
- jeux_euromillions: Euromillions tirages, grilles, stats, generation IA
- jeux_dashboard   : Dashboard, Performance, Resume Mensuel, Analyse IA, Backtest

Pour routes/__init__.py, "jeux_router": ".jeux" reste inchange.
"""

from fastapi import APIRouter

from .jeux_paris import router as paris_router
from .jeux_loto import router as loto_router
from .jeux_euromillions import router as euromillions_router
from .jeux_dashboard import router as dashboard_router

router = APIRouter(prefix="/api/v1/jeux", tags=["Jeux"])

router.include_router(paris_router)
router.include_router(loto_router)
router.include_router(euromillions_router)
router.include_router(dashboard_router)
