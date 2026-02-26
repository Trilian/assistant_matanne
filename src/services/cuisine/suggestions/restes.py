"""
Service de suggestions «Restes Créatifs» — Valorisation IA des restes.

Prend une liste d'ingrédients restants et génère des idées de recettes
créatives via Mistral AI, avec prompt contextualisé et parsing structuré.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


@dataclass
class ResteDisponible:
    """Un ingrédient restant à utiliser."""

    nom: str
    quantite_approx: str = ""  # "environ 200g", "un peu", "3 tranches"
    etat: str = "bon"  # bon, a_cuisiner_vite, congelé


@dataclass
class SuggestionReste:
    """Suggestion de recette à partir de restes."""

    titre: str
    description: str
    restes_utilises: list[str]
    ingredients_supplementaires: list[str] = field(default_factory=list)
    temps_minutes: int = 30
    difficulte: str = "facile"  # facile, moyen, difficile
    type_plat: str = ""  # entrée, plat, dessert, accompagnement
    astuce: str = ""


# ═══════════════════════════════════════════════════════════
# PROMPTS IA
# ═══════════════════════════════════════════════════════════

SYSTEM_PROMPT_RESTES = """Tu es un chef cuisinier familial expert en cuisine anti-gaspillage.
Tu ADORES transformer les restes en plats délicieux et créatifs.

RÈGLES:
- Propose 3 à 5 idées de recettes utilisant un maximum des restes listés
- Chaque recette doit être réaliste et familiale (adaptée pour un couple avec enfant)
- Indique les ingrédients supplémentaires nécessaires (basiques de cuisine seulement)
- Sois créatif mais pas bizarre — les plats doivent être appétissants
- Donne un temps de préparation réaliste
- Ajoute une astuce anti-gaspi pour chaque recette

IMPORTANT: Réponds UNIQUEMENT en JSON valide, un array d'objets avec:
{
  "titre": "nom du plat",
  "description": "2-3 phrases décrivant le plat",
  "restes_utilises": ["reste1", "reste2"],
  "ingredients_supplementaires": ["sel", "huile"],
  "temps_minutes": 25,
  "difficulte": "facile",
  "type_plat": "plat",
  "astuce": "conseil anti-gaspi"
}"""


def _construire_prompt_restes(restes: list[ResteDisponible]) -> str:
    """Construit le prompt utilisateur pour la suggestion de restes."""
    lignes = ["Voici mes restes à utiliser:\n"]
    for r in restes:
        ligne = f"- {r.nom}"
        if r.quantite_approx:
            ligne += f" ({r.quantite_approx})"
        if r.etat != "bon":
            ligne += f" [état: {r.etat}]"
        lignes.append(ligne)

    lignes.append("\nPropose des recettes créatives pour les utiliser !")
    return "\n".join(lignes)


# ═══════════════════════════════════════════════════════════
# FONCTIONS PRINCIPALES
# ═══════════════════════════════════════════════════════════


def suggerer_recettes_restes(
    restes: list[ResteDisponible],
    preferences: dict | None = None,
) -> list[SuggestionReste]:
    """
    Génère des suggestions de recettes à partir de restes via IA.

    Args:
        restes: Liste des ingrédients restants
        preferences: Préférences optionnelles (régime, temps_max, etc.)

    Returns:
        Liste de SuggestionReste
    """
    if not restes:
        return []

    try:
        from src.core.ai.client import ClientIA

        client = ClientIA()
        prompt = _construire_prompt_restes(restes)

        if preferences:
            if temps_max := preferences.get("temps_max"):
                prompt += f"\n\nContrainte: max {temps_max} minutes de préparation."
            if regime := preferences.get("regime"):
                prompt += f"\nContrainte: régime {regime}."

        reponse = client.generer_texte(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT_RESTES,
            temperature=0.8,  # Plus créatif pour les restes
        )

        return _parser_suggestions(reponse)

    except Exception:
        logger.exception("Erreur lors de la suggestion de restes via IA")
        return _suggestions_fallback(restes)


def _parser_suggestions(reponse: str) -> list[SuggestionReste]:
    """Parse la réponse JSON de l'IA en SuggestionReste."""
    try:
        # Nettoyer la réponse (enlever ```json si présent)
        texte = reponse.strip()
        if texte.startswith("```"):
            texte = texte.split("\n", 1)[1] if "\n" in texte else texte[3:]
        if texte.endswith("```"):
            texte = texte[:-3]
        texte = texte.strip()

        data = json.loads(texte)
        if not isinstance(data, list):
            data = [data]

        suggestions = []
        for item in data:
            suggestions.append(
                SuggestionReste(
                    titre=item.get("titre", "Recette créative"),
                    description=item.get("description", ""),
                    restes_utilises=item.get("restes_utilises", []),
                    ingredients_supplementaires=item.get("ingredients_supplementaires", []),
                    temps_minutes=item.get("temps_minutes", 30),
                    difficulte=item.get("difficulte", "facile"),
                    type_plat=item.get("type_plat", "plat"),
                    astuce=item.get("astuce", ""),
                )
            )

        return suggestions

    except (json.JSONDecodeError, KeyError):
        logger.warning("Impossible de parser la réponse IA pour les restes")
        return []


def _suggestions_fallback(restes: list[ResteDisponible]) -> list[SuggestionReste]:
    """Suggestions de base sans IA, basées sur des templates."""
    noms = [r.nom.lower() for r in restes]

    suggestions = []

    # Template: si légumes → soupe / poêlée
    legumes = [
        n
        for n in noms
        if any(
            l in n
            for l in [
                "carotte",
                "courgette",
                "poireau",
                "pomme de terre",
                "oignon",
                "tomate",
                "aubergine",
                "poivron",
                "navet",
                "chou",
                "épinard",
                "haricot",
                "brocoli",
            ]
        )
    ]
    if len(legumes) >= 2:
        suggestions.append(
            SuggestionReste(
                titre="Soupe de légumes maison",
                description=f"Une soupe réconfortante avec {', '.join(legumes[:3])}. "
                "Faites revenir les légumes dans un peu d'huile, couvrez d'eau et mixez.",
                restes_utilises=legumes[:4],
                ingredients_supplementaires=["bouillon cube", "sel", "poivre"],
                temps_minutes=35,
                difficulte="facile",
                type_plat="entrée",
                astuce="Les fanes et épluchures peuvent aussi aller dans la soupe !",
            )
        )
        suggestions.append(
            SuggestionReste(
                titre="Poêlée de légumes",
                description=f"Poêlée colorée de {', '.join(legumes[:3])} avec herbes.",
                restes_utilises=legumes[:4],
                ingredients_supplementaires=["huile d'olive", "ail", "herbes de Provence"],
                temps_minutes=20,
                difficulte="facile",
                type_plat="accompagnement",
                astuce="Ajoutez un œuf au plat pour un repas complet.",
            )
        )

    # Template: si féculents → gratin / salade composée
    feculents = [
        n
        for n in noms
        if any(f in n for f in ["riz", "pâtes", "pomme de terre", "semoule", "quinoa", "pain"])
    ]
    if feculents:
        suggestions.append(
            SuggestionReste(
                titre="Gratin de restes",
                description=f"Gratin avec {feculents[0]} et les légumes/protéines restants. "
                "Nappez de béchamel ou crème, et gratinez.",
                restes_utilises=feculents[:1] + legumes[:2],
                ingredients_supplementaires=["crème", "fromage râpé"],
                temps_minutes=30,
                difficulte="facile",
                type_plat="plat",
                astuce="Le pain rassis mixé fait une excellente chapelure gratinée.",
            )
        )

    # Template: si protéines → wrap / sandwich
    proteines = [
        n
        for n in noms
        if any(
            p in n
            for p in [
                "poulet",
                "jambon",
                "viande",
                "thon",
                "saumon",
                "boeuf",
                "dinde",
                "oeuf",
                "œuf",
            ]
        )
    ]
    if proteines:
        suggestions.append(
            SuggestionReste(
                titre="Wraps garnis",
                description=f"Wraps avec {proteines[0]}, crudités et sauce au choix.",
                restes_utilises=proteines[:1] + legumes[:2],
                ingredients_supplementaires=["tortillas", "sauce", "salade"],
                temps_minutes=10,
                difficulte="facile",
                type_plat="plat",
                astuce="Les restes de viande rôtie sont parfaits effilochés en wraps.",
            )
        )

    # Suggestion par défaut
    if not suggestions:
        tous_noms = [r.nom for r in restes[:4]]
        suggestions.append(
            SuggestionReste(
                titre="Omelette surprise",
                description=f"Omelette garnie avec ce que vous avez : {', '.join(tous_noms)}.",
                restes_utilises=tous_noms,
                ingredients_supplementaires=["œufs", "sel", "poivre"],
                temps_minutes=15,
                difficulte="facile",
                type_plat="plat",
                astuce="Presque tout peut aller dans une omelette !",
            )
        )

    return suggestions


__all__ = [
    "ResteDisponible",
    "SuggestionReste",
    "suggerer_recettes_restes",
]
