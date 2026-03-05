"""
Generation de prompts IA pour le Planificateur de Repas

Prompts pour la generation de menus et alternatives.
"""

import logging
import random
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

    prompt = f"""Tu es un assistant culinaire familial expert. Génère un planning de repas COMPLET pour une famille.

CONTEXTE FAMILLE:
- {preferences.nb_adultes} adultes
- 1 bébé de {preferences.jules_age_mois} mois (Jules) qui mange avec nous
- Robots cuisine disponibles: {", ".join(preferences.robots) if preferences.robots else "poêle, four"}

CONTRAINTES:
- Temps de cuisine en semaine: {preferences.temps_semaine} ({TEMPS_CATEGORIES[preferences.temps_semaine]["label"]})
- Aliments à ÉVITER absolument: {", ".join(preferences.aliments_exclus) if preferences.aliments_exclus else "aucun"}
- Aliments favoris: {", ".join(preferences.aliments_favoris) if preferences.aliments_favoris else "variés"}

ÉQUILIBRE SOUHAITÉ PAR SEMAINE:
- Poisson: {preferences.poisson_par_semaine} fois
- Repas végétarien: {preferences.vegetarien_par_semaine} fois
- Viande rouge: maximum {preferences.viande_rouge_max} fois

APPRENTISSAGE (base sur l'historique):
- La famille a aimé: {", ".join(recettes_aimees) if recettes_aimees else "pas encore assez de données"}
- La famille n'a pas aimé: {", ".join(recettes_pas_aimees) if recettes_pas_aimees else "pas encore assez de données"}

JOURS À PLANIFIER: {", ".join(jours_a_planifier)}

⚠️ RÈGLE OBLIGATOIRE: Pour CHAQUE jour listé, tu DOIS fournir OBLIGATOIREMENT:
- "midi": un plat (JAMAIS null, JAMAIS absent)
- "soir": un plat (JAMAIS null, JAMAIS absent)
- "gouter": facultatif, pertinent pour Jules

Pour chaque repas, fournis:
1. Nom du plat (simple et familial)
2. Type de protéine principale (parmi: poulet, boeuf, porc, agneau, poisson, crevettes, oeufs, tofu, legumineuses)
3. Temps total de préparation en minutes
4. Instructions spécifiques pour adapter le repas à Jules ({preferences.jules_age_mois} mois):
   - Comment adapter la texture
   - Quelle quantité prélever avant assaisonnement
   - Comment servir pour son âge
   ⚠️ Pas de miel pour Jules (moins de 12 mois) et textures adaptées à l'âge

FORMAT DE RÉPONSE (JSON strict):
{{
  "semaine": [
    {{
      "jour": "Mercredi",
      "midi": {{
        "nom": "Poulet rôti aux légumes",
        "proteine": "poulet",
        "temps_minutes": 45,
        "robot": "four",
        "difficulte": "facile",
        "jules_adaptation": "Prélever 80g de poulet et légumes avant sel. Mixer grossièrement. Servir tiède."
      }},
      "soir": {{
        "nom": "Soupe de légumes maison",
        "proteine": "legumineuses",
        "temps_minutes": 25,
        "robot": "poele",
        "difficulte": "facile",
        "jules_adaptation": "Mixer finement la portion de Jules (100g). Servir tiède."
      }},
      "gouter": {{
        "nom": "Compote pomme-poire maison",
        "temps_minutes": 15,
        "jules_adaptation": "Texture lisse parfaite pour Jules"
      }}
    }}
  ],
  "equilibre_respecte": true,
  "conseils_batch": "Dimanche: préparer la sauce bolognaise et la soupe. Mercredi: poulet mariné.",
  "suggestions_bio": ["Poulet fermier Bio", "Légumes Grand Frais"]
}}

IMPORTANT: Propose des recettes VARIÉES et ORIGINALES. Évite les classiques trop courants (pâtes bolo, poulet riz).
Seed aléatoire pour la variété: {random.randint(1000, 9999)}
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
