"""
Service inter-modules : Entretien -> Courses.

Bridge inter-modules :
- P5-05: taches entretien necessitant un produit -> ajout/reco courses
"""

from __future__ import annotations

import logging
from typing import Any

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


PRODUITS_PAR_CATEGORIE = {
    "vitres": ["nettoyant vitres", "chiffon microfibre"],
    "salle_de_bain": ["desinfectant", "anticalcaire", "eponges"],
    "cuisine": ["degraissant", "essuie-tout"],
    "jardin": ["sacs de dechets verts", "gants"],
    "menage": ["lessive", "produit multi-surfaces"],
}


class EntretienCoursesInteractionService:
    """Bridge taches entretien -> besoins courses."""

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def suggerer_produits_entretien_pour_courses(self, *, db=None) -> dict[str, Any]:
        from src.core.models import TacheEntretien

        taches = db.query(TacheEntretien).filter(TacheEntretien.fait.is_(False)).all()

        suggestions = []
        for tache in taches:
            categorie = (tache.categorie or "").lower()
            produits = PRODUITS_PAR_CATEGORIE.get(categorie, [])
            for produit in produits:
                suggestions.append(
                    {
                        "tache_id": tache.id,
                        "tache": tache.nom,
                        "categorie": categorie,
                        "produit": produit,
                    }
                )

        return {
            "suggestions": suggestions,
            "message": f"{len(suggestions)} produit(s) entretien suggere(s) pour les courses.",
        }


@service_factory("entretien_courses_interaction", tags={"maison", "courses", "entretien"})
def obtenir_service_entretien_courses_interaction() -> EntretienCoursesInteractionService:
    """Factory pour le bridge entretien -> courses."""
    return EntretienCoursesInteractionService()
