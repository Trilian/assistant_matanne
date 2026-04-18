"""
Service pour générer une version robot (Cookeo, Air Fryer, Monsieur Cuisine)
d'une recette via Mistral.

Adapte les étapes de préparation d'une recette pour un appareil spécifique :
- Temps de cuisson, températures et modes adaptés
- Étapes réorganisées pour le workflow spécifique de l'appareil
- Conseils d'utilisation de l'appareil
"""

import logging

from src.core.ai import obtenir_client_ia
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)

ROBOTS_CONTEXTE = {
    "cookeo": {
        "nom": "Cookeo",
        "description": "Multicuiseur intelligent Moulinex avec cuisson sous pression, rissolage, mijotage et vapeur",
        "modes": "Pression, Rissolage, Mijotage, Vapeur, Réchauffage, Dorer",
        "conseils": (
            "- Toujours faire rissoler AVANT de lancer la cuisson sous pression\n"
            "- Mode pression : divise le temps de cuisson par 3 environ\n"
            "- Ne pas dépasser les 2/3 de la cuve pour la pression\n"
            "- Pas besoin de surveiller en mode pression\n"
            "- Déglacer avant de fermer le couvercle"
        ),
    },
    "monsieur_cuisine": {
        "nom": "Monsieur Cuisine",
        "description": "Robot cuiseur multifonction Lidl avec cuisson, mixage, pétrissage, émulsion et vapeur",
        "modes": "Mijoter, Cuire vapeur, Rissoler, Mixer, Pétrir, Émulsionner, Turbo",
        "conseils": (
            "- Peut mixer ET cuire en même temps (soupes, veloutés)\n"
            "- Utiliser le panier vapeur pour les légumes pendant que le plat cuit dans la cuve\n"
            "- Vitesse 1-2 pour mélanger sans écraser, vitesse 5+ pour mixer\n"
            "- Mode Mijotage : 100°C vitesse 1 pour les plats mijotés\n"
            "- Préchauffer la cuve avant de rissoler"
        ),
    },
    "airfryer": {
        "nom": "Air Fryer",
        "description": "Friteuse à air chaud sans huile pour cuisson croustillante",
        "modes": "Air fry, Grill, Rôtir, Réchauffer, Déshydrater",
        "conseils": (
            "- Préchauffer 3 min avant cuisson\n"
            "- Ne pas surcharger le panier — une seule couche pour un résultat croustillant\n"
            "- Secouer/retourner à mi-cuisson pour une cuisson uniforme\n"
            "- Réduire la température de 20°C par rapport au four traditionnel\n"
            "- Vaporiser légèrement d'huile pour un meilleur croustillant\n"
            "- Les aliments panés/enrobés sont idéaux"
        ),
    },
}

PROMPT_SYSTEM = """Tu es un chef cuisinier expert en appareils de cuisine.
Adapte la recette pour une cuisson au {nom_robot}.

═══ APPAREIL : {nom_robot} ═══
{description}

Modes disponibles : {modes}

Conseils d'utilisation :
{conseils}

═══ RÈGLES ═══
1. Réécris les instructions étape par étape pour le {nom_robot}
2. Indique le MODE précis à utiliser pour chaque étape (ex: "Mode Pression 12 min")
3. Adapte les TEMPS de cuisson à l'appareil
4. Adapte les TEMPÉRATURES si pertinent
5. Garde les mêmes ingrédients — seule la méthode de cuisson change
6. Si une étape ne peut pas être faite avec cet appareil (ex: gratiner au four), indique-le clairement

Réponds en JSON avec ce format exact :
{{
  "instructions_modifiees": "Étapes détaillées pour le {nom_robot} :\\n1. ...\\n2. ...\\n3. ...",
  "modifications_resume": ["Liste des changements principaux vs recette standard"],
  "temps_cuisson_estime": nombre_en_minutes_ou_null,
  "temperature_principale": nombre_en_degres_ou_null
}}
"""


class ServiceVersionRecetteRobot(BaseAIService):
    """Génère une VersionRecette adaptée à un robot de cuisine via Mistral."""

    def __init__(self) -> None:
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="version_robot",
            default_ttl=3600,
            service_name="version_recette_robot",
        )

    def generer_version_robot(
        self,
        recette_id: int,
        robot: str,
    ) -> dict:
        """Génère les instructions adaptées à un robot et persiste en DB.

        Args:
            recette_id: ID de la recette source
            robot: Type de robot ("cookeo", "monsieur_cuisine", "airfryer")

        Returns:
            Dict avec les champs de VersionRecette
        """
        from src.core.db import obtenir_contexte_db
        from src.core.models import Recette, VersionRecette

        if robot not in ROBOTS_CONTEXTE:
            raise ValueError(f"Robot inconnu : {robot}. Valeurs possibles : {list(ROBOTS_CONTEXTE)}")

        contexte = ROBOTS_CONTEXTE[robot]

        with obtenir_contexte_db() as session:
            recette = session.query(Recette).filter(Recette.id == recette_id).first()
            if not recette:
                raise ValueError(f"Recette {recette_id} introuvable")

            # Vérifier si une version robot existe déjà
            version_existante = (
                session.query(VersionRecette)
                .filter(
                    VersionRecette.recette_base_id == recette_id,
                    VersionRecette.type_version == robot,
                )
                .first()
            )

            # Description de la recette pour le prompt
            ingredients_txt = (
                "\n".join(
                    f"- {ing.quantite or ''} {ing.unite or ''} {ing.ingredient.nom if ing.ingredient else '?'}".strip()
                    for ing in recette.ingredients
                )
                if recette.ingredients
                else "Ingrédients non disponibles"
            )

            instructions_txt = (
                "\n".join(
                    f"{idx}. {e.description}"
                    for idx, e in enumerate(sorted(recette.etapes, key=lambda e: e.ordre), start=1)
                )
                if recette.etapes
                else "Instructions non disponibles"
            )

            prompt = f"""Recette : {recette.nom}
Catégorie : {recette.categorie or "non spécifiée"}
Temps de cuisson standard : {recette.temps_cuisson or "non spécifié"} min

Ingrédients :
{ingredients_txt}

Instructions standard :
{instructions_txt}

Adapte cette recette pour le {contexte['nom']}."""

            system = PROMPT_SYSTEM.format(
                nom_robot=contexte["nom"],
                description=contexte["description"],
                modes=contexte["modes"],
                conseils=contexte["conseils"],
            )

            result = self.call_with_dict_parsing_sync(
                prompt=prompt,
                system_prompt=system,
                max_tokens=1500,
            )

            if not result:
                result = {
                    "instructions_modifiees": f"Instructions {contexte['nom']} non disponibles — utiliser la recette standard.",
                    "modifications_resume": [f"Adaptation {contexte['nom']} non générée"],
                }

            # Créer ou mettre à jour la VersionRecette en DB
            if version_existante:
                version_existante.instructions_modifiees = result.get("instructions_modifiees")
                version_existante.modifications_resume = result.get("modifications_resume", [])
                session.commit()
                session.refresh(version_existante)
                version = version_existante
            else:
                version = VersionRecette(
                    recette_base_id=recette_id,
                    type_version=robot,
                    instructions_modifiees=result.get("instructions_modifiees"),
                    modifications_resume=result.get("modifications_resume", []),
                )
                session.add(version)
                session.commit()
                session.refresh(version)

            # Mettre à jour le flag compatible_xxx sur la recette
            flag_attr = f"compatible_{robot}"
            if hasattr(recette, flag_attr) and not getattr(recette, flag_attr):
                setattr(recette, flag_attr, True)
                session.commit()

            return {
                "id": version.id,
                "recette_base_id": version.recette_base_id,
                "type_version": version.type_version,
                "instructions_modifiees": version.instructions_modifiees,
                "ingredients_modifies": version.ingredients_modifies,
                "notes_bebe": None,
                "modifications_resume": result.get("modifications_resume", []),
                "recette_nom": recette.nom,
            }


@service_factory("version_recette_robot", tags={"cuisine", "ia"})
def obtenir_version_recette_robot_service() -> ServiceVersionRecetteRobot:
    return ServiceVersionRecetteRobot()
