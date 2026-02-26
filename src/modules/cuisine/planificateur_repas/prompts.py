"""
Generation de prompts IA pour le Planificateur de Repas

Prompts pour la generation de menus et alternatives.
"""

import logging
from datetime import date

from src.core.constants import JOURS_SEMAINE
from src.modules.cuisine.schemas import FeedbackRecette, PreferencesUtilisateur

from .helpers import TEMPS_CATEGORIES

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# GÉNÉRATION DE PROMPTS IA
# ═══════════════════════════════════════════════════════════


def generer_prompt_semaine(
    preferences: PreferencesUtilisateur,
    feedbacks: list[FeedbackRecette],
    date_debut: date,
    jours_a_planifier: list[str] = None,
) -> str:
    """
    Genère un prompt pour l'IA pour creer une semaine de repas.

    Args:
        preferences: Preferences utilisateur
        feedbacks: Historique feedbacks pour apprentissage
        date_debut: Date de debut de la semaine
        jours_a_planifier: Liste des jours (si partiel)

    Returns:
        Prompt formate pour l'IA
    """

    # Construire le contexte d'apprentissage
    recettes_aimees = [f.recette_nom for f in feedbacks if f.feedback == "like"][-10:]
    recettes_pas_aimees = [f.recette_nom for f in feedbacks if f.feedback == "dislike"][-5:]

    # Jours à planifier
    if not jours_a_planifier:
        jours_a_planifier = JOURS_SEMAINE

    prompt = f"""Tu es un assistant culinaire familial expert. Genère un planning de repas pour une famille.

CONTEXTE FAMILLE:
- {preferences.nb_adultes} adultes
- 1 bebe de {preferences.jules_age_mois} mois (Jules) qui mange avec nous
- Robots cuisine disponibles: {", ".join(preferences.robots)}

CONTRAINTES:
- Temps de cuisine en semaine: {preferences.temps_semaine} ({TEMPS_CATEGORIES[preferences.temps_semaine]["label"]})
- Aliments à ÉVITER: {", ".join(preferences.aliments_exclus) if preferences.aliments_exclus else "aucun"}
- Aliments favoris: {", ".join(preferences.aliments_favoris) if preferences.aliments_favoris else "varies"}

ÉQUILIBRE SOUHAITÉ PAR SEMAINE:
- Poisson: {preferences.poisson_par_semaine} fois
- Repas vegetarien: {preferences.vegetarien_par_semaine} fois
- Viande rouge: maximum {preferences.viande_rouge_max} fois

APPRENTISSAGE (base sur l'historique):
- La famille a aime: {", ".join(recettes_aimees) if recettes_aimees else "pas encore assez de donnees"}
- La famille n'a pas aime: {", ".join(recettes_pas_aimees) if recettes_pas_aimees else "pas encore assez de donnees"}

JOURS À PLANIFIER: {", ".join(jours_a_planifier)}

Pour chaque repas, fournis:
1. Nom du plat (simple et familial)
2. Type de proteine principale
3. Temps total de preparation
4. Instructions SPÉCIFIQUES pour adapter le repas à Jules ({preferences.jules_age_mois} mois):
   - Comment adapter la texture
   - Quelle quantite prelever avant assaisonnement
   - Comment servir pour son âge

FORMAT DE RÉPONSE (JSON):
{{
  "semaine": [
    {{
      "jour": "Mercredi",
      "midi": {{
        "nom": "Poulet rôti aux legumes",
        "proteine": "poulet",
        "temps_minutes": 45,
        "robot": "four",
        "difficulte": "facile",
        "jules_adaptation": "Prelever 80g de poulet et legumes avant sel. Mixer grossièrement pour texture avec morceaux. Servir tiède."
      }},
      "soir": {{...}},
      "gouter": {{
        "nom": "Compote pomme-poire maison",
        "temps_minutes": 15,
        "jules_adaptation": "Parfait tel quel, texture lisse"
      }}
    }}
  ],
  "equilibre_respecte": true,
  "conseils_batch": "Dimanche: preparer la sauce bolognaise et la soupe. Mercredi: poulet marine + gratin.",
  "suggestions_bio": ["Le poulet fermier Bio Coop", "Les legumes Grand Frais"]
}}
"""

    return prompt


def generer_prompt_alternative(
    recette_a_remplacer: str,
    type_repas: str,
    jour: str,
    preferences: PreferencesUtilisateur,
    contraintes_equilibre: dict[str, int],
) -> str:
    """
    Genère un prompt pour obtenir des alternatives à une recette.
    """

    prompt = f"""Propose 3 alternatives à "{recette_a_remplacer}" pour le {type_repas} du {jour}.

CONTRAINTES:
- Famille avec bebe de {preferences.jules_age_mois} mois
- Temps disponible: {preferences.temps_semaine}
- Équipement: {", ".join(preferences.robots)}
- À eviter: {", ".join(preferences.aliments_exclus) if preferences.aliments_exclus else "rien"}

ÉQUILIBRE ACTUEL DE LA SEMAINE:
- Poisson dejà prevu: {contraintes_equilibre.get("poisson", 0)}/{preferences.poisson_par_semaine}
- Vegetarien: {contraintes_equilibre.get("vegetarien", 0)}/{preferences.vegetarien_par_semaine}
- Viande rouge: {contraintes_equilibre.get("viande_rouge", 0)}/{preferences.viande_rouge_max}

FORMAT JSON:
{{
  "alternatives": [
    {{
      "nom": "Nom du plat",
      "proteine": "type",
      "temps_minutes": 30,
      "pourquoi": "Raison de la suggestion",
      "jules_adaptation": "Instructions pour Jules"
    }}
  ]
}}
"""

    return prompt
