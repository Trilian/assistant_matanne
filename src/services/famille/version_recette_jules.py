"""
Service pour générer une version Jules d'une recette via Mistral (CT-09).

Adapte une recette pour Jules en tenant compte de son âge et ses aliments exclus :
- Suppression du sel ajouté
- Alcool → fond de volaille
- Saumon fumé → saumon cuit
- Viande/poisson cru → cuisson complète
- Épices fortes → herbes douces
"""

import logging

from src.core.ai import obtenir_client_ia
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)

PROMPT_SYSTEM = """Tu es spécialiste nutrition pédiatrique.
Adapte la recette pour un enfant de {age_mois} mois.
Aliments exclus pour cet enfant : {aliments_exclus}

Règles absolues :
- Supprimer le sel ajouté (pas de sel)
- Alcool → fond de volaille ou bouillon sans sel
- Saumon fumé → saumon cuit vapeur
- Viande/poisson cru → cuisson complète obligatoire
- Épices fortes (piment, curry fort) → supprimer ou remplacer par herbes douces
- Miel (moins de 12 mois) → sirop d'agave ou rien
- Noix entières → poudre de noisette ou supprimer

Réponds en JSON avec ce format exact :
{{
  "ingredients_modifies": {{
    "ingredient_original": "substitution pour Jules",
    ...
  }},
  "instructions_modifiees": "Instructions complètes adaptées à Jules...",
  "notes_bebe": "Conseils spécifiques pour servir à Jules (texture, température, portion)...",
  "modifications_resume": ["Liste des principales modifications effectuées"]
}}
"""


class ServiceVersionRecetteJules(BaseAIService):
    """Génère une VersionRecette adaptée à Jules via Mistral (CT-09)."""

    def __init__(self) -> None:
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="version_jules",
            default_ttl=3600,
            service_name="version_recette_jules",
        )

    def generer_version_jules(
        self,
        recette_id: int,
        profil_jules: dict,
    ) -> dict:
        """Génère la version Jules d'une recette et la persist en DB.

        Args:
            recette_id: ID de la recette source
            profil_jules: Dict avec age_mois et aliments_exclus

        Returns:
            Dict avec les champs de VersionRecette (sans id ni cree_le)
        """
        from src.core.db import obtenir_contexte_db
        from src.core.models import Recette, VersionRecette

        age_mois = profil_jules.get("age_mois", 19)
        aliments_exclus = profil_jules.get("aliments_exclus_jules", [])
        if not aliments_exclus:
            aliments_exclus = ["sel ajouté", "alcool", "saumon fumé", "épices fortes"]

        with obtenir_contexte_db() as session:
            recette = session.query(Recette).filter(Recette.id == recette_id).first()
            if not recette:
                raise ValueError(f"Recette {recette_id} introuvable")

            # Vérifier si une version Jules existe déjà
            version_existante = (
                session.query(VersionRecette)
                .filter(
                    VersionRecette.recette_base_id == recette_id,
                    VersionRecette.type_version == "jules",
                )
                .first()
            )

            # Construire la description de la recette
            ingredients_txt = "\n".join(
                f"- {ing.quantite or ''} {ing.unite or ''} {ing.ingredient.nom if ing.ingredient else '?'}".strip()
                for ing in recette.ingredients
            ) if recette.ingredients else "Ingrédients non disponibles"

            instructions_txt = "\n".join(
                f"{idx}. {e.description}"
                for idx, e in enumerate(sorted(recette.etapes, key=lambda e: e.ordre), start=1)
            ) if recette.etapes else "Instructions non disponibles"

            prompt = f"""Recette : {recette.nom}
Catégorie : {recette.categorie or "non spécifiée"}

Ingrédients :
{ingredients_txt}

Instructions :
{instructions_txt}

Adapte cette recette pour Jules."""

            system = PROMPT_SYSTEM.format(
                age_mois=age_mois,
                aliments_exclus=", ".join(aliments_exclus) if aliments_exclus else "aucun",
            )

            result = self.call_with_json_parsing_sync(
                prompt=prompt,
                system_prompt=system,
                max_tokens=1200,
            )

            if not result:
                result = {
                    "ingredients_modifies": {},
                    "instructions_modifiees": instructions_txt,
                    "notes_bebe": "Servir à température tiède, en petites bouchées.",
                    "modifications_resume": ["Sel supprimé"],
                }

            # Créer ou mettre à jour la VersionRecette en DB
            if version_existante:
                version_existante.instructions_modifiees = result.get("instructions_modifiees")
                version_existante.ingredients_modifies = result.get("ingredients_modifies")
                version_existante.notes_bebe = result.get("notes_bebe")
                session.commit()
                session.refresh(version_existante)
                version = version_existante
            else:
                version = VersionRecette(
                    recette_base_id=recette_id,
                    type_version="jules",
                    instructions_modifiees=result.get("instructions_modifiees"),
                    ingredients_modifies=result.get("ingredients_modifies"),
                    notes_bebe=result.get("notes_bebe"),
                )
                session.add(version)
                session.commit()
                session.refresh(version)

            return {
                "id": version.id,
                "recette_base_id": version.recette_base_id,
                "type_version": version.type_version,
                "instructions_modifiees": version.instructions_modifiees,
                "ingredients_modifies": version.ingredients_modifies,
                "notes_bebe": version.notes_bebe,
                "modifications_resume": result.get("modifications_resume", []),
                "recette_nom": recette.nom,
                "age_mois_jules": age_mois,
            }


@service_factory("version_recette_jules", tags={"famille", "ia", "recettes"})
def get_version_recette_jules_service() -> ServiceVersionRecetteJules:
    """Factory singleton pour ServiceVersionRecetteJules."""
    return ServiceVersionRecetteJules()
