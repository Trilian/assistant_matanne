"""
Service Plan Maison 2D — CRUD plans, gestion canvas.

Fournit :
- CRUD plans (créer, lister, récupérer, modifier, supprimer)
- Gestion versions plans
- Sauvegarde/chargement canvas JSON
- Génération thumbnail/export image

Usage:
    service = get_plan_2d_service()
    plans = service.lister_plans()
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.orm import Session

from src.core.decorators import avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class Plan2DService:
    """Service de gestion des plans 2D/3D de la maison."""

    # ─────────────────────────────────────────────────────────
    # PLANS — CRUD
    # ─────────────────────────────────────────────────────────

    @avec_session_db
    def lister_plans(
        self,
        db: Session | None = None,
        type_plan: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """Liste les plans avec filtres et pagination."""
        from src.core.models.maison_extensions import PlanMaison

        assert db is not None
        query = db.query(PlanMaison).filter(PlanMaison.est_actif == True)

        if type_plan:
            query = query.filter(PlanMaison.type_plan == type_plan)

        total = query.count()
        items = (
            query.order_by(PlanMaison.modifie_le.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return {
            "items": [self._plan_to_dict(p) for p in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @avec_session_db
    def obtenir_plan(self, plan_id: int, db: Session | None = None) -> dict[str, Any]:
        """Récupère un plan avec toutes ses données."""
        from src.core.models.maison_extensions import PlanMaison

        assert db is not None
        plan = db.query(PlanMaison).filter_by(id=plan_id, est_actif=True).first()
        if not plan:
            raise ValueError(f"Plan {plan_id} introuvable")
        return self._plan_to_dict(plan)

    @avec_session_db
    def creer_plan(self, data: dict[str, Any], db: Session | None = None) -> dict[str, Any]:
        """Crée un nouveau plan."""
        from src.core.models.maison_extensions import PlanMaison

        assert db is not None
        plan = PlanMaison(**data)
        db.add(plan)
        db.flush()
        result = self._plan_to_dict(plan)
        db.commit()
        logger.info(f"Plan créé: {plan.id} - {plan.nom} ({plan.type_plan})")
        return result

    @avec_session_db
    def modifier_plan(
        self, plan_id: int, data: dict[str, Any], db: Session | None = None
    ) -> dict[str, Any]:
        """Modifie un plan existant."""
        from src.core.models.maison_extensions import PlanMaison

        assert db is not None
        plan = db.query(PlanMaison).filter_by(id=plan_id).first()
        if not plan:
            raise ValueError(f"Plan {plan_id} introuvable")

        # Incrémenter la version si donnees_canvas est modifiées
        if "donnees_canvas" in data and data["donnees_canvas"] != plan.donnees_canvas:
            plan.version = (plan.version or 1) + 1

        for key, value in data.items():
            if hasattr(plan, key) and value is not None:
                setattr(plan, key, value)

        db.flush()
        result = self._plan_to_dict(plan)
        db.commit()
        logger.info(f"Plan {plan_id} modifié (v{plan.version})")
        return result

    @avec_session_db
    def supprimer_plan(self, plan_id: int, db: Session | None = None) -> bool:
        """Supprime un plan (soft delete – est_actif=False)."""
        from src.core.models.maison_extensions import PlanMaison

        assert db is not None
        plan = db.query(PlanMaison).filter_by(id=plan_id).first()
        if not plan:
            raise ValueError(f"Plan {plan_id} introuvable")

        plan.est_actif = False
        db.commit()
        logger.info(f"Plan {plan_id} supprimé (soft delete)")
        return True

    # ─────────────────────────────────────────────────────────
    # VERSIONS & EXPORT
    # ─────────────────────────────────────────────────────────

    @avec_session_db
    def dupliquer_plan(self, plan_id: int, db: Session | None = None) -> dict[str, Any]:
        """Duplique un plan (crée une nouvelle version)."""
        from src.core.models.maison_extensions import PlanMaison

        assert db is not None
        original = db.query(PlanMaison).filter_by(id=plan_id).first()
        if not original:
            raise ValueError(f"Plan {plan_id} introuvable")

        copie = PlanMaison(
            nom=f"{original.nom} (v{original.version + 1})",
            description=original.description,
            type_plan=original.type_plan,
            version=original.version + 1,
            donnees_canvas=original.donnees_canvas,
            echelle_px_par_m=original.echelle_px_par_m,
            largeur_canvas=original.largeur_canvas,
            hauteur_canvas=original.hauteur_canvas,
            etage=original.etage,
            notes=f"Copie de {original.nom}",
        )
        db.add(copie)
        db.flush()
        result = self._plan_to_dict(copie)
        db.commit()
        logger.info(f"Plan {plan_id} dupliqué → {copie.id} (v{copie.version})")
        return result

    @avec_session_db
    def sauvegarder_canvas(
        self, plan_id: int, donnees_canvas: dict[str, Any], db: Session | None = None
    ) -> dict[str, Any]:
        """Sauvegarde les données canvas JSON du plan."""
        from src.core.models.maison_extensions import PlanMaison

        assert db is not None
        plan = db.query(PlanMaison).filter_by(id=plan_id).first()
        if not plan:
            raise ValueError(f"Plan {plan_id} introuvable")

        plan.donnees_canvas = donnees_canvas
        plan.version = (plan.version or 1) + 1

        db.flush()
        result = self._plan_to_dict(plan)
        db.commit()
        logger.info(f"Canvas sauvegardé pour plan {plan_id} (v{plan.version})")
        return result

    @avec_session_db
    def charger_canvas(self, plan_id: int, db: Session | None = None) -> dict[str, Any]:
        """Récupère les données canvas d'un plan pour l'édition."""
        from src.core.models.maison_extensions import PlanMaison

        assert db is not None
        plan = db.query(PlanMaison).filter_by(id=plan_id).first()
        if not plan:
            raise ValueError(f"Plan {plan_id} introuvable")

        return {
            "id": plan.id,
            "nom": plan.nom,
            "type_plan": plan.type_plan,
            "version": plan.version,
            "echelle_px_par_m": plan.echelle_px_par_m,
            "largeur_canvas": plan.largeur_canvas,
            "hauteur_canvas": plan.hauteur_canvas,
            "etage": plan.etage,
            "donnees_canvas": plan.donnees_canvas or {},
        }

    # ─────────────────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────────────────

    @staticmethod
    def _plan_to_dict(plan: Any) -> dict[str, Any]:
        """Convertit un PlanMaison en dict."""
        return {
            "id": plan.id,
            "nom": plan.nom,
            "description": plan.description,
            "type_plan": plan.type_plan,
            "version": plan.version,
            "est_actif": plan.est_actif,
            "donnees_canvas": plan.donnees_canvas,
            "echelle_px_par_m": plan.echelle_px_par_m,
            "largeur_canvas": plan.largeur_canvas,
            "hauteur_canvas": plan.hauteur_canvas,
            "etage": plan.etage,
            "thumbnail_path": plan.thumbnail_path,
            "notes": plan.notes,
            "created_at": plan.cree_le.isoformat() if plan.cree_le else None,
            "updated_at": plan.modifie_le.isoformat() if plan.modifie_le else None,
        }


@service_factory("plan_2d", tags={"maison", "visualisation"})
def get_plan_2d_service() -> Plan2DService:
    """Factory singleton pour Plan2DService."""
    return Plan2DService()
