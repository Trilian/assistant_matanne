"""
Service Jules - Logique métier pour le profil enfant et jalons.

Opérations:
- Récupération/création du profil Jules
- Gestion des milestones (jalons de développement)
- Calcul d'âge (délègue à age_utils)
"""

import logging
from datetime import date as date_type
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.decorators import avec_session_db
from src.core.models import ChildProfile, Milestone
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class ServiceJules:
    """Service de gestion du profil enfant Jules et de ses jalons.

    Centralise l'accès DB pour le profil enfant, éliminant
    les requêtes directes depuis la couche modules.
    """

    # ═══════════════════════════════════════════════════════════
    # PROFIL
    # ═══════════════════════════════════════════════════════════

    @avec_session_db
    def get_or_create_jules(self, db: Session | None = None) -> int:
        """Récupère ou crée le profil Jules, retourne son ID.

        Args:
            db: Session DB (injectée automatiquement).

        Returns:
            ID du profil Jules.

        Raises:
            RuntimeError: Si la création échoue.
        """
        assert db is not None

        child = db.query(ChildProfile).filter_by(name="Jules", actif=True).first()

        if not child:
            child = ChildProfile(
                name="Jules",
                date_of_birth=date_type(2024, 6, 22),
                gender="M",
                notes="Notre petit Jules ❤️",
                actif=True,
            )
            db.add(child)
            db.commit()
            logger.info("Profil Jules créé (id=%d)", child.id)

        return child.id

    # ═══════════════════════════════════════════════════════════
    # MILESTONES (JALONS)
    # ═══════════════════════════════════════════════════════════

    @avec_session_db
    def get_milestones_by_category(self, child_id: int, db: Session | None = None) -> dict:
        """Récupère les jalons groupés par catégorie.

        Args:
            child_id: ID du profil enfant.
            db: Session DB (injectée automatiquement).

        Returns:
            Dict {catégorie: [liste de jalons]}.
        """
        assert db is not None

        milestones = db.query(Milestone).filter_by(child_id=child_id).all()

        result: dict[str, list[dict[str, Any]]] = {}
        for milestone in milestones:
            cat = milestone.categorie
            if cat not in result:
                result[cat] = []
            result[cat].append(
                {
                    "id": milestone.id,
                    "titre": milestone.titre,
                    "date": milestone.date_atteint,
                    "description": milestone.description,
                    "notes": milestone.notes,
                }
            )

        return result

    @avec_session_db
    def count_milestones_by_category(self, child_id: int, db: Session | None = None) -> dict:
        """Compte les jalons par catégorie.

        Args:
            child_id: ID du profil enfant.
            db: Session DB (injectée automatiquement).

        Returns:
            Dict {catégorie: nombre}.
        """
        assert db is not None

        result = (
            db.query(Milestone.categorie, func.count(Milestone.id).label("count"))
            .filter_by(child_id=child_id)
            .group_by(Milestone.categorie)
            .all()
        )

        return {cat: count for cat, count in result}


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("jules", tags={"famille", "enfant"})
def obtenir_service_jules() -> ServiceJules:
    """Factory pour le service Jules (singleton via ServiceRegistry)."""
    return ServiceJules()


# Alias anglais
get_jules_service = obtenir_service_jules
