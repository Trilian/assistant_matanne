"""
Service IA — Suggestions IA diverses.

Services IA pour :
- Batch cooking intelligent (B4.4 / IA8)
- Jules conseil développement (B4.8 / IA9)
- Checklist voyage IA (B4.10 / IA11)
- Score écologique repas (B4.11 / IA12)
- Optimisation énergie prédictive (B4.6 / IA6)
- Analyse nutritionnelle (B4.7 / IA7)
"""

import logging

from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class SuggestionsIAService(BaseAIService):
    """Service centralisé pour les suggestions IA multidomaine."""

    def __init__(self):
        super().__init__(
            cache_prefix="suggestions_ia",
            default_ttl=3600,
            service_name="suggestions_ia",
        )

    def batch_cooking_intelligent(self, recettes: list[str], nb_personnes: int = 4) -> dict:
        """Plan optimal de batch cooking avec timeline parallèle par appareil (B4.4).

        Args:
            recettes: Liste de noms de recettes à préparer
            nb_personnes: Nombre de portions

        Returns:
            Dict avec timeline, appareils, etapes, temps_total
        """
        prompt = f"""Crée un plan de batch cooking optimisé pour {nb_personnes} personnes.

Recettes à préparer: {', '.join(recettes)}

Optimise l'ordre des étapes pour utiliser les appareils en parallèle.
Réponds en JSON:
{{
  "temps_total_minutes": 120,
  "etapes": [
    {{
      "heure": "0:00",
      "action": "Description",
      "appareil": "four|plaque|robot|aucun",
      "duree_minutes": 15,
      "recette": "nom_recette"
    }}
  ],
  "appareils_utilises": ["four", "plaque"],
  "conseils": ["conseil 1"],
  "ordre_optimal": ["recette1", "recette2"]
}}"""

        try:
            result = self.call_with_parsing_sync(
                prompt=prompt,
                system_prompt="Tu es un expert en batch cooking et organisation cuisine. JSON valide.",
            )
            if isinstance(result, dict):
                return result
        except Exception as e:
            logger.warning(f"Erreur IA batch cooking: {e}")

        return {"temps_total_minutes": 0, "etapes": [], "erreur": "IA indisponible"}

    def conseil_developpement_jules(self, age_mois: int, jalons_atteints: list[str] | None = None) -> dict:
        """Conseils de développement proactifs pour Jules basés sur l'âge (B4.8).

        Args:
            age_mois: Âge en mois
            jalons_atteints: Jalons déjà validés

        Returns:
            Dict avec activites_recommandees, points_attention, jalons_attendus
        """
        jalons_str = ", ".join(jalons_atteints) if jalons_atteints else "aucun renseigné"

        prompt = f"""Un enfant a {age_mois} mois.
Jalons de développement déjà atteints: {jalons_str}

Donne des conseils de développement adaptés.
Réponds en JSON:
{{
  "activites_recommandees": [
    {{"activite": "Description", "domaine": "moteur|langage|social|cognitif", "duree_minutes": 15}}
  ],
  "jalons_attendus": [
    {{"jalon": "Description", "domaine": "moteur|langage|social|cognitif", "age_moyen_mois": {age_mois}}}
  ],
  "points_attention": ["point 1"],
  "jeux_adaptes": ["jeu 1", "jeu 2"]
}}"""

        try:
            result = self.call_with_parsing_sync(
                prompt=prompt,
                system_prompt="Tu es pédiatre spécialisé en développement de l'enfant. JSON valide.",
            )
            if isinstance(result, dict):
                return result
        except Exception as e:
            logger.warning(f"Erreur IA conseil Jules: {e}")

        return {"activites_recommandees": [], "jalons_attendus": [], "erreur": "IA indisponible"}

    def generer_checklist_voyage(
        self, destination: str, dates: str, participants: list[str] | None = None
    ) -> dict:
        """Génère une checklist de voyage personnalisée (B4.10).

        Args:
            destination: Destination du voyage
            dates: Dates du voyage (texte libre)
            participants: Liste des participants

        Returns:
            Dict avec categories, items, rappels
        """
        parts_str = ", ".join(participants) if participants else "famille"

        prompt = f"""Crée une checklist voyage complète.

Destination: {destination}
Dates: {dates}
Participants: {parts_str}

Réponds en JSON:
{{
  "categories": [
    {{
      "nom": "Documents",
      "items": [
        {{"item": "Passeport", "important": true, "fait": false}}
      ]
    }}
  ],
  "rappels": [
    {{"rappel": "Vérifier validité passeport", "jours_avant": 30}}
  ],
  "conseils_destination": ["conseil 1"]
}}"""

        try:
            result = self.call_with_parsing_sync(
                prompt=prompt,
                system_prompt="Tu es un expert en organisation de voyages. JSON valide.",
            )
            if isinstance(result, dict):
                return result
        except Exception as e:
            logger.warning(f"Erreur IA checklist voyage: {e}")

        return {"categories": [], "rappels": [], "erreur": "IA indisponible"}

    def score_ecologique_repas(self, ingredients: list[str], saison: str = "") -> dict:
        """Calcule le score écologique d'un repas (B4.11).

        Args:
            ingredients: Liste des ingrédients
            saison: Saison actuelle

        Returns:
            Dict avec score, details, suggestions_amelioration
        """
        prompt = f"""Évalue le score écologique de ce repas.

Ingrédients: {', '.join(ingredients)}
Saison actuelle: {saison or 'non précisée'}

Critères: saisonnalité, distance transport, impact protéines, emballages.
Réponds en JSON:
{{
  "score_global": 7.5,
  "score_max": 10,
  "details": {{
    "saisonnalite": 8,
    "transport": 6,
    "impact_proteines": 7,
    "emballages": 8
  }},
  "ingredients_problematiques": ["avocat (hors saison, import)"],
  "suggestions_amelioration": ["Remplacer X par Y (local et de saison)"]
}}"""

        try:
            result = self.call_with_parsing_sync(
                prompt=prompt,
                system_prompt="Tu es un expert en alimentation durable. JSON valide.",
            )
            if isinstance(result, dict):
                return result
        except Exception as e:
            logger.warning(f"Erreur IA score écologique: {e}")

        return {"score_global": None, "erreur": "IA indisponible"}

    def optimisation_energie(self, releves: list[dict], meteo: dict | None = None) -> dict:
        """Analyse les relevés énergie et prédit la prochaine facture (B4.6).

        Args:
            releves: Liste de relevés [{mois, kwh, montant}]
            meteo: Prévisions météo optionnelles

        Returns:
            Dict avec prevision, tendance, conseils
        """
        prompt = f"""Analyse ces relevés d'énergie et prédit la prochaine facture.

Relevés récents: {releves}
Météo prévue: {meteo or 'non disponible'}

Réponds en JSON:
{{
  "prevision_prochaine_facture": {{"kwh": 350, "montant_estime": 80}},
  "tendance": "hausse|baisse|stable",
  "variation_pct": 5.2,
  "conseils_economies": ["conseil 1", "conseil 2"],
  "comparaison_moyenne_nationale": "en dessous|dans la moyenne|au dessus"
}}"""

        try:
            result = self.call_with_parsing_sync(
                prompt=prompt,
                system_prompt="Tu es un expert en efficacité énergétique. JSON valide.",
            )
            if isinstance(result, dict):
                return result
        except Exception as e:
            logger.warning(f"Erreur IA énergie: {e}")

        return {"prevision_prochaine_facture": None, "erreur": "IA indisponible"}

    def analyse_nutritionnelle(self, description_repas: str) -> dict:
        """Analyse nutritionnelle d'un repas décrit en texte (B4.7).

        Args:
            description_repas: Description du repas

        Returns:
            Dict avec calories, macros, micronutriments, score
        """
        prompt = f"""Analyse nutritionnelle de ce repas:
"{description_repas}"

Réponds en JSON:
{{
  "calories_estimees": 650,
  "macronutriments": {{
    "proteines_g": 30,
    "glucides_g": 80,
    "lipides_g": 25,
    "fibres_g": 8
  }},
  "score_nutritionnel": 7,
  "points_forts": ["Riche en fibres"],
  "points_faibles": ["Manque de légumes verts"],
  "suggestion_amelioration": "Ajouter une salade verte en accompagnement"
}}"""

        try:
            result = self.call_with_parsing_sync(
                prompt=prompt,
                system_prompt="Tu es nutritionniste. Réponds en JSON valide.",
            )
            if isinstance(result, dict):
                return result
        except Exception as e:
            logger.warning(f"Erreur IA nutrition: {e}")

        return {"calories_estimees": None, "erreur": "IA indisponible"}


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("suggestions_ia", tags={"ia"})
def obtenir_service_suggestions_ia() -> SuggestionsIAService:
    """Factory singleton."""
    return SuggestionsIAService()


get_suggestions_ia_service = obtenir_service_suggestions_ia
