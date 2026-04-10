"""Service Habitat pour la deco avancee, le budget et le jardin."""

from __future__ import annotations

import logging
from datetime import date

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.core.models import DepenseMaison, ProjetDecoHabitat, ZoneJardinHabitat
from src.services.core.base import BaseAIService
from src.services.core.events import obtenir_bus
from src.services.core.registry import service_factory
from src.services.integrations.image_generation import obtenir_service_generation_image

logger = logging.getLogger(__name__)


class ConceptDecoIA(BaseModel):
    resume: str
    palette_couleurs: list[str] = Field(default_factory=list)
    materiaux: list[str] = Field(default_factory=list)
    achats_prioritaires: list[str] = Field(default_factory=list)
    prompt_image: str | None = None


class DecoHabitatService(BaseAIService):
    """Produit des concepts deco et synchronise leur budget vers les depenses maison."""

    def __init__(self) -> None:
        super().__init__(service_name="habitat_deco", cache_prefix="habitat_deco")
        self._images = obtenir_service_generation_image()

    def generer_concept(
        self,
        session: Session,
        *,
        projet_id: int,
        brief: str | None = None,
        generer_image: bool = False,
    ) -> dict:
        projet = session.query(ProjetDecoHabitat).filter(ProjetDecoHabitat.id == projet_id).first()
        if projet is None:
            raise ValueError("Projet deco habitat introuvable")

        prompt = f"""
Projet deco Habitat: {projet.nom_piece}
Style existant: {projet.style or "non defini"}
Budget prevu: {float(projet.budget_prevu or 0)}
Budget depense: {float(projet.budget_depense or 0)}
Palette actuelle: {projet.palette_couleurs or []}
Inspirations actuelles: {projet.inspirations or []}
Notes: {projet.notes or ""}
Brief: {brief or "Créer une version réaliste, chaleureuse et durable."}
"""
        system_prompt = """
Tu es decorateur d'interieur et acheteur travaux.
Retourne uniquement un JSON avec:
{
  "resume": "...",
  "palette_couleurs": ["#..."],
  "materiaux": ["..."],
  "achats_prioritaires": ["..."],
  "prompt_image": "prompt photo realiste"
}
"""
        fallback = {
            "resume": "Proposition deco structuree manuellement.",
            "palette_couleurs": projet.palette_couleurs or ["#F2E7D8", "#3E4C42", "#C98B5B"],
            "materiaux": ["bois clair", "lin lave", "metal noir mat"],
            "achats_prioritaires": ["luminaire principal", "textiles", "rangements"],
            "prompt_image": None,
        }
        concept = self.call_with_parsing_sync(
            prompt=prompt,
            response_model=ConceptDecoIA,
            system_prompt=system_prompt,
            temperature=0.4,
            max_tokens=1400,
            fallback=fallback,
        )
        if concept is None:
            concept = ConceptDecoIA(**fallback)

        projet.palette_couleurs = concept.palette_couleurs
        projet.inspirations = concept.achats_prioritaires + concept.materiaux
        projet.notes = (projet.notes or "") + f"\n\n[IA] {concept.resume}"

        image = None
        if generer_image and concept.prompt_image:
            image = self._images.generer_image(prompt=concept.prompt_image)

        obtenir_bus().emettre(
            "habitat.deco.concept_genere",
            {
                "projet_id": projet.id,
                "nom_piece": projet.nom_piece,
                "budget_prevu": float(projet.budget_prevu or 0),
            },
            source="habitat",
        )

        return {
            "projet_id": projet.id,
            "concept": concept.model_dump(),
            "image": image,
        }

    def synchroniser_depense(
        self,
        session: Session,
        *,
        projet_id: int,
        montant: float,
        fournisseur: str | None,
        note: str | None,
        categorie_depense: str,
    ) -> dict:
        projet = session.query(ProjetDecoHabitat).filter(ProjetDecoHabitat.id == projet_id).first()
        if projet is None:
            raise ValueError("Projet deco habitat introuvable")

        mois = date.today().month
        annee = date.today().year
        note_budget = f"[habitat_deco:{projet.id}] {note or ''}".strip()

        depense = DepenseMaison(
            categorie=categorie_depense,
            mois=mois,
            annee=annee,
            montant=montant,
            fournisseur=fournisseur,
            notes=note_budget,
        )
        session.add(depense)
        session.flush()

        projet.budget_depense = float(projet.budget_depense or 0) + montant
        projet.statut = "en_cours" if projet.budget_depense else projet.statut

        obtenir_bus().emettre(
            "habitat.deco.depense_synchro",
            {
                "projet_id": projet.id,
                "depense_maison_id": depense.id,
                "montant": montant,
                "categorie": categorie_depense,
            },
            source="habitat",
        )

        return {
            "projet_id": projet.id,
            "depense_maison_id": depense.id,
            "budget_depense": float(projet.budget_depense or 0),
        }

    def resume_jardin(self, session: Session, plan_id: int | None = None) -> dict:
        query = session.query(ZoneJardinHabitat)
        if plan_id is not None:
            query = query.filter(ZoneJardinHabitat.plan_id == plan_id)
        zones = query.all()
        total_surface = sum(float(zone.surface_m2 or 0) for zone in zones)
        total_budget = sum(float(zone.budget_estime or 0) for zone in zones)
        return {
            "zones": len(zones),
            "surface_totale_m2": round(total_surface, 2),
            "budget_estime": round(total_budget, 2),
            "types": sorted({zone.type_zone for zone in zones if zone.type_zone}),
        }


@service_factory("habitat_deco", tags={"habitat", "deco", "budget"})
def obtenir_service_deco_habitat() -> DecoHabitatService:
    """Factory singleton du service deco Habitat."""
    return DecoHabitatService()
