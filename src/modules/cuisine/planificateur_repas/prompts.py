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
    bases_choisies: dict[str, list[str]] | None = None,
) -> str:
    """
    Genère un prompt pour l'IA pour creer une semaine de repas.

    Args:
        preferences: Preferences utilisateur
        feedbacks: Historique feedbacks pour apprentissage
        date_debut: Date de debut de la semaine
        jours_a_planifier: Liste des jours (si partiel)
        bases_choisies: Dict optionnel {legumes: [...], feculents: [...], proteines: [...]}
                        Si fourni, l'IA DOIT utiliser ces ingrédients comme base.

    Returns:
        Prompt formate pour l'IA
    """

    # Construire le contexte d'apprentissage
    recettes_aimees = [f.recette_nom for f in feedbacks if f.feedback == "like"][-10:]
    recettes_pas_aimees = [f.recette_nom for f in feedbacks if f.feedback == "dislike"][-5:]

    # Jours à planifier
    if not jours_a_planifier:
        jours_a_planifier = JOURS_SEMAINE

    # Construire la section ingrédients de base
    bases = bases_choisies or {}
    legumes_choisis = bases.get("legumes", [])
    feculents_choisis = bases.get("feculents", [])
    proteines_choisies = bases.get("proteines", [])

    if legumes_choisis or feculents_choisis or proteines_choisies:
        section_bases = """🥕 INGRÉDIENTS DE BASE IMPOSÉS PAR L'UTILISATEUR:
- Tu DOIS construire les repas de la semaine autour de ces ingrédients de base choisis.
- Utilise chaque ingrédient imposé dans EXACTEMENT 2 repas différents (pas plus, pour garder de la variété)."""
        if legumes_choisis:
            section_bases += f"\n  * LÉGUMES imposés: {', '.join(legumes_choisis)}"
        if feculents_choisis:
            section_bases += f"\n  * FÉCULENTS imposés: {', '.join(feculents_choisis)}"
        if proteines_choisies:
            section_bases += f"\n  * PROTÉINES imposées: {', '.join(proteines_choisies)}"
        section_bases += "\n- Tu peux ajouter d'autres ingrédients en complément. Les bases sont centrales MAIS la variété prime."
        section_bases += '\n- Lister TOUS les ingrédients partagés (imposés + complémentaires) dans "ingredients_communs_semaine".'
    else:
        section_bases = """🥕 INGRÉDIENTS EN COMMUN (BATCH COOKING):
- Les repas de la semaine DOIVENT partager des bases communes pour simplifier les courses et la préparation batch:
  * Choisir 2-3 LÉGUMES de base utilisés dans 2 repas chacun (ex: carottes, courgettes, poireaux)
  * Choisir 1-2 FÉCULENTS de base réutilisés dans 2 repas chacun (ex: riz, pommes de terre, pâtes)
  * La même PROTÉINE peut servir 2 repas différents (ex: poulet rôti dimanche → émincés de poulet mardi)
- Lister ces ingrédients partagés dans "ingredients_communs_semaine"."""

    prompt = f"""Tu es un assistant culinaire familial expert en BATCH COOKING et organisation hebdomadaire.
Génère un planning de repas COMPLET pour une famille, optimisé pour minimiser le temps de préparation.

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

═══════════════════════════════════════════════════
⚠️ RÈGLES CRITIQUES DE CONCEPTION DU MENU:
═══════════════════════════════════════════════════

🔄 RÉUTILISATION DES REPAS (RÉCHAUFFÉ):
- Parmi les 14 repas (7 midis + 7 soirs), 3 à 4 MIDIS en semaine (lun-ven) DOIVENT être des réchauffés d'un DÎNER préparé un JOUR PRÉCÉDENT.
- ⚠️ RÈGLE CHRONOLOGIQUE STRICTE: Un midi réchauffé ne peut référencer QUE un dîner d'un jour ANTÉRIEUR.
  Exemples VALIDES: Mardi midi = réchauffé de Lundi soir. Jeudi midi = réchauffé de Mardi soir.
  Exemples INVALIDES: Lundi midi = réchauffé de Dimanche soir (pas encore cuisiné!). Mardi midi = réchauffé de Mardi soir (pas logique).
- Le premier réchauffé possible est MARDI midi (source: Lundi soir).
- Le dîner source est cuisiné en double portion. Le midi réchauffé est simplement réchauffé.
- Le midi réchauffé peut être 1-3 jours après le dîner source (pas forcément le lendemain).
- Mettre "est_rechauffe": true et "rechauffe_de": "Lundi soir" pour ces midis.
- Résultat: seulement ~10 repas à cuisiner au lieu de 14.

🚫 VARIÉTÉ OBLIGATOIRE:
- Chaque plat cuisiné (non réchauffé) doit avoir un NOM DIFFÉRENT. JAMAIS 2 plats identiques dans la semaine.
- Même avec des ingrédients en commun, les RECETTES doivent être différentes (ex: courgettes → gratin de courgettes ET ratatouille, pas 2 gratins).
- Les réchauffés reprennent le même plat = c'est normal, mais la recette source ne doit apparaître QU'UNE seule fois comme dîner cuisiné.

{section_bases}

⚡ MIX SIMPLE / ÉLABORÉ:
- La MAJORITÉ des repas (8-10 sur 14) doivent être SIMPLES et RAPIDES (≤ 25 min, "difficulte": "facile").
  Exemples: omelette, pâtes au pesto, steak haché-purée, croque-monsieur, wrap, salade composée, soupe, gratin simple.
- Seulement 2-3 repas par semaine peuvent être plus ÉLABORÉS (30-60 min, "difficulte": "moyen" ou "difficile").
  Exemples: tajine, gratin dauphinois, poulet rôti, poisson en papillote, risotto, curry maison.
- Les repas élaborés sont idéalement placés le weekend ou les soirs où on a plus de temps.
- Mettre "complexite": "simple" ou "complexite": "elabore" pour chaque plat.

═══════════════════════════════════════════════════

⚠️ RÈGLE OBLIGATOIRE: Pour CHAQUE jour listé, tu DOIS fournir OBLIGATOIREMENT:
- "midi": un repas complet (JAMAIS null, JAMAIS absent)
- "soir": un repas complet (JAMAIS null, JAMAIS absent)
- "gouter": facultatif, pertinent pour Jules

Chaque repas (midi/soir) DOIT contenir:
1. "entree": entrée simple (texte libre ou null)
2. "plat": objet complet (voir ci-dessous)
3. "dessert": dessert famille (texte libre)
4. "dessert_jules": dessert adapté Jules {preferences.jules_age_mois} mois

Pour le plat, fournis:
1. "nom": Nom du plat
2. "proteine": Type de protéine (poulet, boeuf, porc, agneau, poisson, crevettes, oeufs, tofu, legumineuses)
3. "temps_minutes": Temps total en minutes
4. "robot": Robot utilisé
5. "difficulte": facile/moyen/difficile
6. "complexite": "simple" ou "elabore"
7. "est_rechauffe": true/false (si ce midi est un réchauffé d'un dîner)
8. "rechauffe_de": "Jour soir" (si est_rechauffe=true, ex: "Lundi soir")
9. "jules_adaptation": Instructions pour adapter à Jules ({preferences.jules_age_mois} mois)

FORMAT DE RÉPONSE (JSON strict):
{{
  "semaine": [
    {{
      "jour": "Lundi",
      "midi": {{
        "entree": null,
        "plat": {{
          "nom": "Réchauffé: Gratin de courgettes",
          "proteine": "oeufs",
          "temps_minutes": 5,
          "robot": "four",
          "difficulte": "facile",
          "complexite": "simple",
          "est_rechauffe": true,
          "rechauffe_de": "Vendredi soir",
          "jules_adaptation": "Réchauffer la portion de Jules séparément."
        }},
        "dessert": "Yaourt nature",
        "dessert_jules": "Compote pomme-banane"
      }},
      "soir": {{
        "entree": "Salade verte",
        "plat": {{
          "nom": "Émincés de poulet aux courgettes et riz",
          "proteine": "poulet",
          "temps_minutes": 20,
          "robot": "poele",
          "difficulte": "facile",
          "complexite": "simple",
          "est_rechauffe": false,
          "jules_adaptation": "Prélever 80g avant sel. Écraser les morceaux de poulet."
        }},
        "dessert": "Fruit frais",
        "dessert_jules": "Petit-suisse nature"
      }},
      "gouter": {{
        "nom": "Compote pomme-poire maison",
        "temps_minutes": 15,
        "jules_adaptation": "Texture lisse parfaite pour Jules"
      }}
    }}
  ],
  "ingredients_communs_semaine": {{
    "legumes": ["courgettes", "carottes", "poireaux"],
    "feculents": ["riz", "pommes de terre"],
    "proteines": ["poulet", "oeufs"]
  }},
  "repas_rechauffe_resume": [
    {{"midi": "Mardi midi", "source": "Lundi soir", "plat": "Émincés de poulet"}},
    {{"midi": "Jeudi midi", "source": "Mercredi soir", "plat": "Curry de légumes"}},
    {{"midi": "Vendredi midi", "source": "Mardi soir", "plat": "Gratin de courgettes"}}
  ],
  "equilibre_respecte": true,
  "conseils_batch": "Dimanche: préparer les légumes de base (courgettes, carottes). Couper le poulet en deux lots. Cuire le riz pour 2 jours.",
  "suggestions_bio": ["Poulet fermier Bio", "Légumes Grand Frais"]
}}

IMPORTANT:
- Les repas réchauffés au midi ont "temps_minutes": 5 (juste réchauffer).
- Privilégie des recettes familiales SIMPLES et rapides pour les soirs de semaine.
- Les plats plus élaborés sont pour le weekend ou un soir calme.
- RÉUTILISE les mêmes légumes/féculents dans plusieurs repas pour faciliter le batch.
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
