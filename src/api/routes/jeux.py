"""Routes API pour les jeux (Paris sportifs, Loto, Euromillions).

Agrégateur : inclut 4 sous-routeurs thématiques via include_router() :
- jeux_paris       : Équipes, Matchs, Paris, Bankroll, Séries, Prédictions, Cotes
  → /equipes, /matchs, /paris/*, /bankroll/*
- jeux_loto        : Loto tirages, grilles, stats, génération IA
  → /loto/*
- jeux_euromillions: Euromillions tirages, grilles, stats, génération IA
  → /euromillions/*
- jeux_dashboard   : Dashboard, Performance, Résumé mensuel, Analyse IA, Backtest
  → /dashboard, /stats/*, /performance/*, /resume-mensuel

Préfixe parent : /api/v1/jeux
Pour routes/__init__.py, "jeux_router": ".jeux" reste inchangé.
"""

from fastapi import APIRouter

from .jeux_paris import router as paris_router
from .jeux_loto import router as loto_router
from .jeux_euromillions import router as euromillions_router
from .jeux_dashboard import router as dashboard_router

router = APIRouter(prefix="/api/v1/jeux", tags=["Jeux"])

router.include_router(paris_router, tags=["Jeux — Paris"])
router.include_router(loto_router, tags=["Jeux — Loto"])
router.include_router(euromillions_router, tags=["Jeux — Euromillions"])
router.include_router(dashboard_router, tags=["Jeux — Dashboard"])
