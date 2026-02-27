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

from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.models import Jalon, ProfilEnfant
from src.core.monitoring import chronometre
from src.services.core.events import obtenir_bus
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

    @chronometre(nom="jules.get_or_create", seuil_alerte_ms=2000)
    @avec_gestion_erreurs(default_return=None)
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
        if db is None:
            raise ValueError("Session DB requise")

        child = db.query(ProfilEnfant).filter_by(name="Jules", actif=True).first()

        if not child:
            child = ProfilEnfant(
                name="Jules",
                date_of_birth=date_type(2024, 6, 22),
                gender="M",
                notes="Notre petit Jules ❤️",
                # Defaults for clothing sizes / shoe size (per-child)
                taille_vetements={},
                pointure=None,
                actif=True,
            )
            db.add(child)
            db.commit()
            logger.info("Profil Jules créé (id=%d)", child.id)

            # Émettre événement profil créé
            obtenir_bus().emettre(
                "enfant.profil_cree",
                {"child_id": child.id, "name": "Jules"},
                source="ServiceJules",
            )

        return child.id

    # ═══════════════════════════════════════════════════════════
    # MILESTONES (JALONS)
    # ═══════════════════════════════════════════════════════════

    @chronometre(nom="jules.milestones_by_category", seuil_alerte_ms=1500)
    @avec_gestion_erreurs(default_return={})
    @avec_cache(ttl=300)
    @avec_session_db
    def get_milestones_by_category(self, child_id: int, db: Session | None = None) -> dict:
        """Récupère les jalons groupés par catégorie.

        Args:
            child_id: ID du profil enfant.
            db: Session DB (injectée automatiquement).

        Returns:
            Dict {catégorie: [liste de jalons]}.
        """
        if db is None:
            raise ValueError("Session DB requise")

        milestones = db.query(Jalon).filter_by(child_id=child_id).all()

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

    @chronometre(nom="jules.count_milestones", seuil_alerte_ms=1000)
    @avec_gestion_erreurs(default_return={})
    @avec_cache(ttl=300)
    @avec_session_db
    def count_milestones_by_category(self, child_id: int, db: Session | None = None) -> dict:
        """Compte les jalons par catégorie.

        Args:
            child_id: ID du profil enfant.
            db: Session DB (injectée automatiquement).

        Returns:
            Dict {catégorie: nombre}.
        """
        if db is None:
            raise ValueError("Session DB requise")

        result = (
            db.query(Jalon.categorie, func.count(Jalon.id).label("count"))
            .filter_by(child_id=child_id)
            .group_by(Jalon.categorie)
            .all()
        )

        return {cat: count for cat, count in result}

    # ═══════════════════════════════════════════════════════════
    # ÂGE / DATE DE NAISSANCE
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=None)
    @avec_cache(ttl=300)
    @avec_session_db
    def get_date_naissance_jules(self, db: Session | None = None) -> date_type | None:
        """Récupère la date de naissance de Jules depuis la BD.

        Args:
            db: Session DB (injectée automatiquement).

        Returns:
            Date de naissance ou None si non trouvée.
        """
        if db is None:
            raise ValueError("Session DB requise")
        try:
            jules = db.query(ProfilEnfant).filter_by(name="Jules", actif=True).first()
            if jules and jules.date_of_birth:
                return jules.date_of_birth
        except Exception:
            logger.debug("Erreur récupération date naissance Jules")
        return None


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("jules", tags={"famille", "enfant"})
def obtenir_service_jules() -> ServiceJules:
    """Factory pour le service Jules (singleton via ServiceRegistry)."""
    return ServiceJules()


# Alias anglais
get_jules_service = obtenir_service_jules
