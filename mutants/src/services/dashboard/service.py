"""
Service Accueil Data.

Centralise les accès base de données pour le module accueil/dashboard.
"""

import logging
from datetime import date

from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.core.models import TacheEntretien
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)
from typing import Annotated
from typing import Callable
from typing import ClassVar

MutantDict = Annotated[dict[str, Callable], "Mutant"] # type: ignore


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None): # type: ignore
    """Forward call to original or mutated function, depending on the environment"""
    import os # type: ignore
    mutant_under_test = os.environ['MUTANT_UNDER_TEST'] # type: ignore
    if mutant_under_test == 'fail': # type: ignore
        from mutmut.__main__ import MutmutProgrammaticFailException # type: ignore
        raise MutmutProgrammaticFailException('Failed programmatically')       # type: ignore
    elif mutant_under_test == 'stats': # type: ignore
        from mutmut.__main__ import record_trampoline_hit # type: ignore
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__) # type: ignore
        # (for class methods, orig is bound and thus does not need the explicit self argument)
        result = orig(*call_args, **call_kwargs) # type: ignore
        return result # type: ignore
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_' # type: ignore
    if not mutant_under_test.startswith(prefix): # type: ignore
        result = orig(*call_args, **call_kwargs) # type: ignore
        return result # type: ignore
    mutant_name = mutant_under_test.rpartition('.')[-1] # type: ignore
    if self_arg is not None: # type: ignore
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs) # type: ignore
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs) # type: ignore
    return result # type: ignore


class AccueilDataService:
    """Service de données pour le dashboard accueil.

    Note (dashboard service): Service read-heavy standalone sans BaseService[T] — acceptable
    car il ne fait que de la lecture agrégée, pas de CRUD standard.
    """

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def get_taches_en_retard(self, limit: int = 10, db: Session | None = None) -> list[dict]:
        """Récupère les tâches ménage en retard.

        Returns:
            Liste de dicts avec nom, prochaine_fois, jours_retard
        """
        taches = (
            db.query(TacheEntretien)
            .filter(
                TacheEntretien.prochaine_fois < date.today(),
                TacheEntretien.fait.is_(False),
            )
            .limit(limit)
            .all()
        )

        return [
            {
                "nom": t.nom,
                "prochaine_fois": t.prochaine_fois,
                "jours_retard": (date.today() - t.prochaine_fois).days,
            }
            for t in taches
        ]


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("accueil_data", tags={"accueil", "data"})
def obtenir_accueil_data_service() -> AccueilDataService:
    """Factory singleton pour le service accueil data."""
    return AccueilDataService()


def obtenir_service_accueil_data() -> AccueilDataService:
    """Factory française pour le service accueil data."""
    return get_accueil_data_service()


# ─── Aliases rétrocompatibilité  ───────────────────────────────
get_accueil_data_service = obtenir_accueil_data_service  # alias rétrocompatibilité 
