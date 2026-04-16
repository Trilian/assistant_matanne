"""

Service pour générer une version Jules d'une recette via Mistral.



Adapte une recette pour Jules en tenant compte de son âge et ses aliments exclus :

- Recommandations nutritionnelles basées sur l'âge (recommandations_age.json)

- Aliments interdits et limités par tranche d'âge

- Liste configurable d'aliments exclus (via préférences utilisateur)

- Gestion stricte des aliments crus (viande, poisson, œuf, lait cru)

- Propositions automatiques de substitution par l'IA

"""

import json
import logging
from pathlib import Path

from src.core.ai import obtenir_client_ia
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


# Chargement des recommandations par âge (portions + restrictions)

_RECOMMANDATIONS_PATH = (
    Path(__file__).resolve().parents[3] / "data" / "reference" / "recommandations_age.json"
)

_RECOMMANDATIONS_AGE: dict = {}


try:
    with open(_RECOMMANDATIONS_PATH, encoding="utf-8") as f:
        _RECOMMANDATIONS_AGE = json.load(f)

except Exception:
    logger.warning(
        "Impossible de charger recommandations_age.json — recommandations par défaut utilisées"
    )


def _tranche_age_pour(age_mois: int) -> dict:
    """Retourne la tranche d'âge correspondante depuis recommandations_age.json."""

    for tranche in _RECOMMANDATIONS_AGE.get("tranches_age", []):
        age_max = tranche.get("age_max_mois") or 999

        if tranche.get("age_min_mois", 0) <= age_mois < age_max:
            return tranche

    return {}


def _facteur_adaptation(age_mois: int) -> float:
    """Retourne le facteur multiplicateur de portions pour l'âge donné."""

    tranche = _tranche_age_pour(age_mois)

    tranche_id = tranche.get("id", "")

    return _RECOMMANDATIONS_AGE.get("facteur_adaptation", {}).get(tranche_id, 0.35)


def _construire_contexte_portions(age_mois: int) -> str:
    """Construit le texte de recommandations nutritionnelles pour le prompt IA."""

    tranche = _tranche_age_pour(age_mois)

    if not tranche:
        return "Pas de données de portions disponibles pour cet âge."

    facteur = _facteur_adaptation(age_mois)

    lignes = [
        f"Tranche d'âge : {tranche.get('label', '?')} ({tranche.get('age_min_mois', '?')}-{tranche.get('age_max_mois', '?')} mois)",
        f"Calories/jour recommandées : {tranche.get('calories_jour', '?')} kcal",
        f"Facteur de portion vs adulte : x{facteur}",
        "",
        "Portions recommandées par repas :",
    ]

    for groupe, info in tranche.get("portions", {}).items():
        nom = groupe.replace("_", " ").capitalize()

        lignes.append(f"  - {nom} : {info.get('portion_g', '?')}g/repas ({info.get('notes', '')})")

    return "\n".join(lignes)


def _construire_contexte_restrictions(age_mois: int) -> str:
    """Construit le texte des aliments interdits et limités pour le prompt IA."""

    tranche = _tranche_age_pour(age_mois)

    if not tranche:
        return "Pas de données de restrictions disponibles pour cet âge."

    lignes = [f"Restrictions pour {tranche.get('label', '?')} :"]

    interdits = tranche.get("aliments_interdits", [])

    if interdits:
        lignes.append("")

        lignes.append("ALIMENTS STRICTEMENT INTERDITS à cet âge :")

        for aliment in interdits:
            lignes.append(f"  ❌ {aliment}")

    limites = tranche.get("aliments_limites", [])

    if limites:
        lignes.append("")

        lignes.append("ALIMENTS À LIMITER à cet âge :")

        for item in limites:
            lignes.append(f"  ⚠️ {item.get('aliment', '?')} — {item.get('limite', '')}")

    return "\n".join(lignes)


# Liste par défaut des aliments crus interdits pour les enfants

ALIMENTS_CRUS_INTERDITS = [
    "tartare",
    "carpaccio",
    "sushi",
    "sashimi",
    "ceviche",
    "steak tartare",
    "viande crue",
    "poisson cru",
    "œuf cru",
    "oeuf cru",
    "lait cru",
    "fromage au lait cru",
    "mayonnaise maison",
    "mousse au chocolat crue",
    "tiramisu",
    "sabayon",
]


PROMPT_SYSTEM = """Tu es spécialiste en nutrition pédiatrique.

Adapte la recette pour un enfant de {age_mois} mois.



═══ RECOMMANDATIONS NUTRITIONNELLES POUR CET ÂGE ═══

{contexte_portions}



═══ RESTRICTIONS PAR ÂGE (données médicales PNNS/OMS/Anses) ═══

{contexte_restrictions}



═══ ALIMENTS EXCLUS SUPPLÉMENTAIRES (configurés par les parents) ═══

{aliments_exclus}



═══ RÈGLES ABSOLUES — à appliquer systématiquement ═══

1. ZÉRO SEL AJOUTÉ — supprimer tout sel, réduire les condiments salés

2. ZÉRO ALCOOL — remplacer vin/bière/alcool par du bouillon sans sel ou fond de volaille

3. ZÉRO CRU — tout doit être CUIT :

   - Viande/poisson cru (tartare, sushi, carpaccio) → cuisson complète

   - Œuf cru (mayonnaise maison, mousse, tiramisu) → œuf dur ou supprimer

   - Lait/fromage au lait cru → version pasteurisée

4. MIEL interdit avant 12 mois → sirop d'agave ou supprimer

5. NOIX ENTIÈRES → poudre (risque étouffement) ou supprimer

6. ÉPICES FORTES (piment, curry fort, poivre abondant) → herbes douces (persil, ciboulette, basilic)

7. Adapter les PORTIONS selon le facteur x{facteur_adaptation} par rapport à l'adulte

8. Adapter la TEXTURE selon l'âge : {texture_conseil}



═══ SUBSTITUTIONS AUTOMATIQUES ═══

Pour CHAQUE ingrédient interdit ou inadapté, tu DOIS proposer une alternative concrète.

Ne te contente jamais de "supprimer" — propose un remplacement quand c'est possible.



Réponds en JSON avec ce format exact :

{{

  "ingredients_modifies": {{

    "ingredient_original": "substitution pour Jules (avec quantité adaptée)",

    ...

  }},

  "instructions_modifiees": "Instructions complètes adaptées...",

  "notes_bebe": "Conseils : texture, température, portion recommandée en grammes...",

  "modifications_resume": ["Liste des principales modifications effectuées"],

  "alertes": ["Alerte si un ingrédient est potentiellement allergène ou à surveiller"]

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

        # Contexte nutritionnel et restrictions basés sur l'âge

        contexte_portions = _construire_contexte_portions(age_mois)

        contexte_restrictions = _construire_contexte_restrictions(age_mois)

        facteur = _facteur_adaptation(age_mois)

        # Aliments interdits par tranche d'âge (doit être défini avant aliments_complets)

        tranche = _tranche_age_pour(age_mois)

        interdits_age = tranche.get("aliments_interdits", [])

        # Fusionner : exclusions parents + crus interdits + interdits par âge

        aliments_complets = list(set(aliments_exclus + ALIMENTS_CRUS_INTERDITS + interdits_age))

        # Conseil texture adapté à l'âge

        if age_mois < 12:
            texture_conseil = "Purée lisse obligatoire, pas de morceaux"

        elif age_mois < 18:
            texture_conseil = "Écrasé ou petits morceaux fondants, pas de morceaux durs"

        elif age_mois < 36:
            texture_conseil = "Morceaux tendres, bien cuits, taille adaptée (risque étouffement)"

        else:
            texture_conseil = (
                "Morceaux normaux, surveiller les aliments ronds/durs (raisins, noix, saucisses)"
            )

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



Ingrédients :

{ingredients_txt}



Instructions :

{instructions_txt}



Adapte cette recette pour Jules."""

            system = PROMPT_SYSTEM.format(
                age_mois=age_mois,
                contexte_portions=contexte_portions,
                contexte_restrictions=contexte_restrictions,
                aliments_exclus=", ".join(aliments_complets)
                if aliments_complets
                else "aucun spécifiquement ajouté par les parents",
                facteur_adaptation=facteur,
                texture_conseil=texture_conseil,
            )

            result = self.call_with_dict_parsing_sync(
                prompt=prompt,
                system_prompt=system,
                max_tokens=1200,
            )

            if not result:
                result = {
                    "ingredients_modifies": {},
                    "instructions_modifiees": instructions_txt,
                    "notes_bebe": f"Servir à température tiède, en petites bouchées. Portion : facteur x{facteur} vs adulte.",
                    "modifications_resume": ["Sel supprimé"],
                    "alertes": [],
                }

            # Créer ou mettre à jour la VersionRecette en DB

            if version_existante:
                version_existante.instructions_modifiees = result.get("instructions_modifiees")

                version_existante.ingredients_modifies = result.get("ingredients_modifies")

                version_existante.notes_bebe = result.get("notes_bebe")

                version_existante.modifications_resume = result.get("modifications_resume", [])

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
                    modifications_resume=result.get("modifications_resume", []),
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
                "alertes": result.get("alertes", []),
                "recette_nom": recette.nom,
                "age_mois_jules": age_mois,
                "facteur_portions": facteur,
            }

    def adapter_planning(self, planning_id: int) -> dict:
        """Adapte TOUS les repas d'une semaine pour Jules (IM1).



        Parcourt tous les repas du planning, génère une version Jules pour chacun,

        et met à jour les champs plat_jules / notes_jules du repas.



        Args:

            planning_id: ID du planning à adapter



        Returns:

            Dict avec résumé des adaptations : nombre adapté, recettes skippées, erreurs

        """

        from src.core.db import obtenir_contexte_db
        from src.core.models import Planning, ProfilFamille, Repas

        with obtenir_contexte_db() as session:
            # Charger le planning et ses repas

            planning = session.query(Planning).filter(Planning.id == planning_id).first()

            if not planning:
                raise ValueError(f"Planning {planning_id} introuvable")

            repas_semaine = (
                session.query(Repas)
                .filter(Repas.planning_id == planning_id, Repas.recette_id.isnot(None))
                .all()
            )

            # Charger le profil de Jules

            profil_jules = (
                session.query(ProfilFamille)
                .filter(ProfilFamille.relation == "fils", ProfilFamille.prenom.ilike("Jules"))
                .first()
            )

            if not profil_jules:
                logger.warning(f"⚠️ Profil Jules non trouvé pour le planning {planning_id}")

                profil_data = {"age_mois": 19, "aliments_exclus_jules": []}

            else:
                profil_data = {
                    "age_mois": profil_jules.age_mois or 19,
                    "aliments_exclus_jules": profil_jules.aliments_exclus or [],
                }

            adaptations = {"adapte": 0, "skipped": 0, "erreurs": 0, "details": []}

            # Adapter chaque repas

            for repas in repas_semaine:
                try:
                    result = self.generer_version_jules(repas.recette_id, profil_data)

                    # Mettre à jour le repas avec la version Jules

                    repas.plat_jules = result.get("instructions_modifiees")

                    repas.notes_jules = result.get("notes_bebe")

                    repas.adaptation_auto = True

                    adapte_details = {
                        "repas_id": repas.id,
                        "date": repas.date_repas.isoformat(),
                        "type_repas": repas.type_repas,
                        "recette_nom": result.get("recette_nom"),
                        "modifications": result.get("modifications_resume", []),
                    }

                    adaptations["details"].append(adapte_details)

                    adaptations["adapte"] += 1

                    logger.info(
                        f"✅ Repas {repas.id} ({result.get('recette_nom')}) adapté pour Jules"
                    )

                except Exception as e:
                    logger.error(f"❌ Erreur adaptation repas {repas.id}: {e}")

                    adaptations["erreurs"] += 1

            session.commit()

            adaptations["summary"] = (
                f"{adaptations['adapte']} repas adaptés, {adaptations['erreurs']} erreurs"
            )

            return adaptations


@service_factory("version_recette_jules", tags={"famille", "ia", "recettes"})
def obtenir_version_recette_jules_service() -> ServiceVersionRecetteJules:
    """Factory singleton pour ServiceVersionRecetteJules."""

    return ServiceVersionRecetteJules()


# ─── Aliases rétrocompatibilité  ───────────────────────────────

obtenir_version_recette_jules_service = (
    obtenir_version_recette_jules_service  # alias rétrocompatibilité
)
