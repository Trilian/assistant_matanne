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


class FaisabiliteDomaineIA(BaseModel):
    score: float = Field(default=5.0, ge=0, le=10)
    niveau_risque: str = Field(default="modere")
    verdict: str
    points_vigilance: list[str] = Field(default_factory=list)
    actions_recommandees: list[str] = Field(default_factory=list)
    budget_estime_min: float | None = None
    budget_estime_max: float | None = None


class FaisabilitePlanIA(BaseModel):
    score_global: float = Field(default=5.0, ge=0, le=10)
    synthese: str
    priorites_travaux: list[str] = Field(default_factory=list)
    budget_travaux_estime_min: float | None = None
    budget_travaux_estime_max: float | None = None
    domaines: dict[str, FaisabiliteDomaineIA] = Field(default_factory=dict)


class AnalysePlanIA(BaseModel):
    resume: str
    points_forts: list[str] = Field(default_factory=list)
    risques: list[str] = Field(default_factory=list)
    budget_estime: float | None = None
    circulation_note: float | None = Field(default=None, ge=0, le=10)
    suggestions_pieces: list[SuggestionPieceIA] = Field(default_factory=list)
    prompt_image: str | None = None
    faisabilite: FaisabilitePlanIA | None = None


class PlansHabitatAIService(BaseAIService):
    """Analyse les plans importes et genere des variantes de reamenagement."""

    def __init__(self) -> None:
        super().__init__(service_name="habitat_plans", cache_prefix="habitat_plans")
        self._multimodal = obtenir_multimodal_service()
        self._images = obtenir_service_generation_image()

    def _charger_plan(
        self, session: Session, plan_id: int
    ) -> tuple[PlanHabitat, list[PieceHabitat]]:
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

    def _extraire_resume_canvas(self, plan: PlanHabitat) -> dict[str, Any]:
        donnees = plan.donnees_pieces or {}
        canvas = donnees.get("canvas_2d") or {}
        murs = canvas.get("murs") or []
        portes = canvas.get("portes") or []
        fenetres = canvas.get("fenetres") or []
        meubles = canvas.get("meubles") or []
        annotations = canvas.get("annotations") or []
        annotations_techniques = [
            annotation.get("texte")
            for annotation in annotations
            if annotation.get("type") in {"warning", "coffrage", "imaison"}
            and annotation.get("texte")
        ]
        return {
            "largeur_canvas": donnees.get("largeur_canvas") or 1200,
            "hauteur_canvas": donnees.get("hauteur_canvas") or 800,
            "nb_murs": len(murs),
            "nb_murs_porteurs": sum(1 for mur in murs if mur.get("porteur")),
            "nb_portes": len(portes),
            "nb_fenetres": len(fenetres),
            "nb_meubles": len(meubles),
            "annotations_techniques": annotations_techniques,
        }

    def _construire_fallback_faisabilite(
        self, plan: PlanHabitat, resume_canvas: dict[str, Any]
    ) -> FaisabilitePlanIA:
        budget_reference = float(plan.budget_estime or 0) or None
        budget_min = round(budget_reference * 0.8, 2) if budget_reference else None
        budget_max = round(budget_reference * 1.2, 2) if budget_reference else None
        murs_porteurs = int(resume_canvas.get("nb_murs_porteurs") or 0)
        points_structure = [
            "Valider les reprises de charge avant ouverture ou suppression de cloison."
            if murs_porteurs
            else "Aucun mur porteur explicite dans le canvas, contrôle terrain recommandé.",
            "Relever les portées et réservations avant chiffrage final.",
        ]
        return FaisabilitePlanIA(
            score_global=5.8,
            synthese="Pré-analyse exploitable, mais plusieurs validations métier restent nécessaires avant engagement travaux.",
            priorites_travaux=[
                "Confirmer la structure porteuse",
                "Valider les réseaux techniques",
                "Sécuriser l'enveloppe thermique et les autorisations",
            ],
            budget_travaux_estime_min=budget_min,
            budget_travaux_estime_max=budget_max,
            domaines={
                "structure": FaisabiliteDomaineIA(
                    score=5.5,
                    niveau_risque="modere" if murs_porteurs else "a_verifier",
                    verdict="Faisable sous réserve d'un relevé structurel et d'une validation des reprises de charge.",
                    points_vigilance=points_structure,
                    actions_recommandees=[
                        "Faire valider les murs porteurs par un BE structure si ouverture prévue.",
                        "Relever précisément portées, poutres et refends sur site.",
                    ],
                    budget_estime_min=budget_min,
                    budget_estime_max=budget_max,
                ),
                "electricite": FaisabiliteDomaineIA(
                    score=6.0,
                    niveau_risque="modere",
                    verdict="Reconfiguration probable du tableau et des circuits si redistribution des pièces.",
                    points_vigilance=[
                        "Anticiper prises, éclairage et courants faibles dans les nouvelles zones.",
                        "Vérifier la capacité du tableau avant ajout de nouveaux usages.",
                    ],
                    actions_recommandees=[
                        "Prévoir un schéma pièce par pièce avant devis.",
                    ],
                ),
                "chauffage": FaisabiliteDomaineIA(
                    score=6.1,
                    niveau_risque="modere",
                    verdict="Le chauffage reste adaptable mais impose de recalculer émetteurs et circulation d'air.",
                    points_vigilance=[
                        "Contrôler l'équilibrage si pièces agrandies ou fusionnées.",
                    ],
                    actions_recommandees=[
                        "Refaire un zonage chauffage/ventilation avec l'implantation cible.",
                    ],
                ),
                "thermique": FaisabiliteDomaineIA(
                    score=5.7,
                    niveau_risque="modere",
                    verdict="L'enveloppe peut suivre le projet, mais les ouvertures et ponts thermiques doivent être revus.",
                    points_vigilance=[
                        "Vérifier l'impact des ouvertures et de la redistribution sur l'isolation.",
                    ],
                    actions_recommandees=[
                        "Préciser les performances visées avant figer les matériaux.",
                    ],
                ),
                "urbanisme": FaisabiliteDomaineIA(
                    score=6.4,
                    niveau_risque="faible",
                    verdict="Faisabilité administrative probable pour un réaménagement intérieur, à confirmer si façade ou surface modifiée.",
                    points_vigilance=[
                        "Déclarer toute modification de façade ou création d'ouverture.",
                    ],
                    actions_recommandees=[
                        "Lister en amont les travaux visibles depuis l'extérieur.",
                    ],
                ),
                "terrain": FaisabiliteDomaineIA(
                    score=6.0,
                    niveau_risque="a_verifier",
                    verdict="Le terrain paraît compatible, mais les altimétries et accès doivent être rapprochés du plan retenu.",
                    points_vigilance=[
                        "Vérifier les raccordements et les interfaces intérieur/extérieur.",
                    ],
                    actions_recommandees=[
                        "Confronter le plan aux zones jardin et aux niveaux existants.",
                    ],
                ),
            },
        )

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
        resume_canvas = self._extraire_resume_canvas(plan)

        scenario_service = ScenariosHabitatService()
        score_scenario = None
        if plan.scenario_id:
            try:
                score_scenario = float(
                    scenario_service.calculer_score_global(session, plan.scenario_id) or 0
                )
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
Resume canvas 2D: {resume_canvas}
Pieces: {
            [
                {
                    "nom": piece.nom,
                    "type_piece": piece.type_piece,
                    "surface_m2": float(piece.surface_m2 or 0),
                    "meubles": piece.meubles or [],
                    "notes": piece.notes,
                }
                for piece in pieces
            ]
        }
Analyse vision complementaire: {contexte_image or {}}
Demande utilisateur: {
            prompt_utilisateur
            or "Analyse globale avec optimisation circulation, budget et rangements."
        }
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
    "faisabilite": {
        "score_global": 0,
        "synthese": "...",
        "priorites_travaux": ["..."],
        "budget_travaux_estime_min": 0,
        "budget_travaux_estime_max": 0,
        "domaines": {
            "structure": {
                "score": 0,
                "niveau_risque": "faible|modere|eleve|a_verifier",
                "verdict": "...",
                "points_vigilance": ["..."],
                "actions_recommandees": ["..."],
                "budget_estime_min": 0,
                "budget_estime_max": 0
            },
            "electricite": {},
            "chauffage": {},
            "thermique": {},
            "urbanisme": {},
            "terrain": {}
        }
    },
  "suggestions_pieces": [
    {"nom": "...", "type_piece": "...", "surface_m2": 0, "actions": ["..."]}
  ],
  "prompt_image": "prompt tres concret pour visualiser la meilleure variante"
}
"""

        fallback_faisabilite = self._construire_fallback_faisabilite(plan, resume_canvas)
        fallback = {
            "resume": "Analyse indisponible, utiliser la version structurelle du plan.",
            "points_forts": ["Base exploitable pour une etude manuelle"],
            "risques": ["Analyse IA incomplete"],
            "budget_estime": float(plan.budget_estime or 0),
            "circulation_note": 5.0,
            "suggestions_pieces": [],
            "prompt_image": None,
            "faisabilite": fallback_faisabilite.model_dump(),
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
        elif analyse.faisabilite is None:
            analyse.faisabilite = fallback_faisabilite

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
            image_generee_url=(
                f"generated://habitat-plan/{plan.id}/{plan.version}"
                if image and image.get("image_base64")
                else None
            ),
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
