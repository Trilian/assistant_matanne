"""
Service inter-modules : Weekend activites -> Courses.

Phase 5:
- P5-07: activites randonnee/pique-nique -> fournitures dans la liste courses
"""

from __future__ import annotations

import logging
from datetime import date as date_type, timedelta
from typing import Any

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class WeekendCoursesInteractionService:
    """Bridge weekend -> courses."""

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def suggerer_fournitures_weekend(self, *, db=None) -> dict[str, Any]:
        from src.core.models import ActiviteWeekend

        samedi = date_type.today() + timedelta(days=(5 - date_type.today().weekday()) % 7)
        dimanche = samedi + timedelta(days=1)

        activites = (
            db.query(ActiviteWeekend)
            .filter(ActiviteWeekend.date_prevue.in_([samedi, dimanche]))
            .all()
        )

        fournitures = []
        for a in activites:
            type_act = (a.type_activite or "").lower()
            if "randon" in type_act:
                fournitures.extend(["eau", "barres cereales", "fruits secs"])
            if "pique" in type_act:
                fournitures.extend(["pain", "fromage", "serviettes", "eau"])

        uniq = sorted(set(fournitures))
        return {
            "nb_activites": len(activites),
            "fournitures_suggerees": uniq,
            "message": f"{len(uniq)} fourniture(s) suggeree(s) pour le weekend.",
        }


@service_factory("weekend_courses_interaction", tags={"famille", "courses", "weekend"})
def obtenir_service_weekend_courses_interaction() -> WeekendCoursesInteractionService:
    """Factory pour le bridge weekend -> courses."""
    return WeekendCoursesInteractionService()
