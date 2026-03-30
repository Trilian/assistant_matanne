"""Services IA pour l'analyse et la transformation des plans Habitat."""

from __future__ import annotations

import logging
from typing import Any

import httpx
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.core.models import ModificationPlanHabitat, PieceHabitat, PlanHabitat
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory
from src.services.habitat.scenarios_service import ScenariosHabitatService
from src.services.integrations.image_generation import obtenir_service_generation_image
from src.services.integrations.multimodal import obtenir_multimodal_service

logger = logging.getLogger(__name__)


class SuggestionPieceIA(BaseModel):
    nom: str
    type_piece: str
    surface_m2: float | None = None
    actions: list[str] = Field(default_factory=list)


class AnalysePlanIA(BaseModel):
    resume: str
    points_forts: list[str] = Field(default_factory=list)
    risques: list[str] = Field(default_factory=list)
    budget_estime: float | None = None
    circulation_note: float | None = Field(default=None, ge=0, le=10)
    suggestions_pieces: list[SuggestionPieceIA] = Field(default_factory=list)
    prompt_image: str | None = None


class PlansHabitatAIService(BaseAIService):
    """Analyse les plans importes et genere des variantes de reamenagement."""

    def __init__(self) -> None:
        super().__init__(service_name="habitat_plans", cache_prefix="habitat_plans")
        self._multimodal = obtenir_multimodal_service()
        self._images = obtenir_service_generation_image()

    def _charger_plan(self, session: Session, plan_id: int) -> tuple[PlanHabitat, list[PieceHabitat]]:
        plan = session.query(PlanHabitat).filter(PlanHabitat.id == plan_id).first()
        if plan is None:
            raise ValueError("Plan habitat introuvable")
        pieces = session.query(PieceHabitat).filter(PieceHabitat.plan_id == plan_id).all()
        return plan, pieces

    def _extraire_contexte_image(self, image_url: str | None) -> dict[str, Any] | None:
        if not image_url or not image_url.startswith(("http://", "https://")):
            return None
        try:
            with httpx.Client(timeout=20.0, follow_redirects=True) as client:
                response = client.get(image_url)
            response.raise_for_status()
            image = response.content
        except Exception as exc:
            logger.debug("Analyse vision Habitat indisponible: %s", exc)
            return None

        system_prompt = (
            "Analyse un plan architectural. Identifie les zones principales, la logique de circulation, "
            "les points de friction et les opportunites d'amenagement. Reponds en JSON."
        )
        try:
            image_b64 = self._multimodal._encode_image(image)
            result = self._multimodal._call_vision_model_sync(
                image_b64=image_b64,
                prompt="Analyse ce plan de maison et resume les pieces visibles.",
                system_prompt=system_prompt,
            )
            return result if isinstance(result, dict) else None
        except Exception as exc:
            logger.debug("Vision plan Habitat indisponible: %s", exc)
            return None

    def analyser_plan(
        self,
        session: Session,
        *,
        plan_id: int,
        prompt_utilisateur: str | None = None,
        generer_image: bool = False,
    ) -> dict[str, Any]:
        plan, pieces = self._charger_plan(session, plan_id)
        contexte_image = self._extraire_contexte_image(plan.image_importee_url)

        scenario_service = ScenariosHabitatService()
        score_scenario = None
        if plan.scenario_id:
            try:
                score_scenario = float(scenario_service.calculer_score_global(session, plan.scenario_id) or 0)
            except Exception:
                score_scenario = None

        prompt = f"""
Plan Habitat: {plan.nom}
Type: {plan.type_plan}
Surface totale: {float(plan.surface_totale_m2 or 0)} m2
Budget estime actuel: {float(plan.budget_estime or 0)}
Version: {plan.version}
Score scenario associe: {score_scenario}
Contraintes: {plan.contraintes or {}}
Pieces: {[
    {
        'nom': piece.nom,
        'type_piece': piece.type_piece,
        'surface_m2': float(piece.surface_m2 or 0),
        'meubles': piece.meubles or [],
        'notes': piece.notes,
    }
    for piece in pieces
]}
Analyse vision complementaire: {contexte_image or {}}
Demande utilisateur: {prompt_utilisateur or 'Analyse globale avec optimisation circulation, budget et rangements.'}
"""

        system_prompt = """
Tu es architecte d'interieur, space planner et economiste travaux.
Retourne uniquement un JSON avec:
{
  "resume": "...",
  "points_forts": ["..."],
  "risques": ["..."],
  "budget_estime": 0,
  "circulation_note": 0,
  "suggestions_pieces": [
    {"nom": "...", "type_piece": "...", "surface_m2": 0, "actions": ["..."]}
  ],
  "prompt_image": "prompt tres concret pour visualiser la meilleure variante"
}
"""

        fallback = {
            "resume": "Analyse indisponible, utiliser la version structurelle du plan.",
            "points_forts": ["Base exploitable pour une etude manuelle"],
            "risques": ["Analyse IA incomplete"],
            "budget_estime": float(plan.budget_estime or 0),
            "circulation_note": 5.0,
            "suggestions_pieces": [],
            "prompt_image": None,
        }
        analyse = self.call_with_parsing_sync(
            prompt=prompt,
            response_model=AnalysePlanIA,
            system_prompt=system_prompt,
            temperature=0.2,
            max_tokens=1800,
            fallback=fallback,
        )
        if analyse is None:
            analyse = AnalysePlanIA(**fallback)

        plan.budget_estime = analyse.budget_estime or plan.budget_estime
        if analyse.suggestions_pieces:
            plan.donnees_pieces = {
                **(plan.donnees_pieces or {}),
                "suggestions_ia": [item.model_dump() for item in analyse.suggestions_pieces],
            }

        image = None
        if generer_image and analyse.prompt_image:
            image = self._images.generer_image(prompt=analyse.prompt_image)

        historique = ModificationPlanHabitat(
            plan_id=plan.id,
            prompt_utilisateur=prompt_utilisateur or "Analyse automatique Habitat",
            analyse_ia=analyse.model_dump(),
            image_generee_url=(f"generated://habitat-plan/{plan.id}/{plan.version}" if image and image.get("image_base64") else None),
            acceptee=None,
        )
        session.add(historique)
        session.flush()

        return {
            "plan_id": plan.id,
            "analyse": analyse.model_dump(),
            "historique_id": historique.id,
            "image": image,
        }

    def historique_plan(self, session: Session, plan_id: int) -> list[dict[str, Any]]:
        items = (
            session.query(ModificationPlanHabitat)
            .filter(ModificationPlanHabitat.plan_id == plan_id)
            .order_by(ModificationPlanHabitat.id.desc())
            .all()
        )
        return [
            {
                "id": item.id,
                "prompt_utilisateur": item.prompt_utilisateur,
                "analyse_ia": item.analyse_ia,
                "image_generee_url": item.image_generee_url,
                "acceptee": item.acceptee,
            }
            for item in items
        ]


@service_factory("habitat_plans_ai", tags={"habitat", "ia", "plans"})
def obtenir_service_plans_habitat() -> PlansHabitatAIService:
    """Factory singleton du service IA plans Habitat."""
    return PlansHabitatAIService()