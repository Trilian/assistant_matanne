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
    recettes_imposees: list[str] | None = None,
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
        recettes_imposees: Liste de plats spécifiques que l'utilisateur veut cette semaine

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

    # Section recettes imposées par l'utilisateur
    section_recettes_imposees = ""
    if recettes_imposees:
        plats = "\n".join(f"  - {plat}" for plat in recettes_imposees)
        section_recettes_imposees = f"""

🍽️ PLATS IMPOSÉS PAR L'UTILISATEUR (OBLIGATOIRE):
- Tu DOIS inclure ces plats dans le planning de la semaine:
{plats}
- Intègre-les aux jours et créneaux (midi/soir) les plus adaptés.
- Complète le reste de la semaine avec d'autres recettes pour respecter l'équilibre demandé.
- Si un plat imposé est végétarien, il compte dans le quota végétarien.
- Si un plat imposé contient du poisson, précise le type (blanc ou gras) dans "proteine"."""

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

ÉQUILIBRE SOUHAITÉ PAR SEMAINE (RESPECTER STRICTEMENT):
- Poisson BLANC (cabillaud, merlu, colin, sole, bar, daurade): EXACTEMENT {preferences.poisson_blanc_par_semaine} repas
- Poisson GRAS (saumon, sardine, thon, maquereau, truite): EXACTEMENT {preferences.poisson_gras_par_semaine} repas
  ⚠️ Bien VARIER les types de poisson: {preferences.poisson_blanc_par_semaine} blanc + {preferences.poisson_gras_par_semaine} gras = {preferences.poisson_par_semaine} poisson(s) au total.
- Repas végétarien/vegan: MAXIMUM {preferences.vegetarien_par_semaine} repas dans la semaine, PAS PLUS.
  ⚠️ ATTENTION: Ne PAS dépasser {preferences.vegetarien_par_semaine} repas végétarien(s). Tous les autres repas DOIVENT contenir une protéine animale (poulet, boeuf, porc, agneau, poisson, crevettes, oeufs).
  Les repas avec oeufs ou poisson NE comptent PAS comme végétariens — seuls les repas avec tofu, légumineuses ou sans aucune protéine animale comptent.
- Viande rouge (boeuf, agneau, veau): maximum {preferences.viande_rouge_max} repas
- Le RESTE des repas: privilégier VOLAILLE (poulet, dinde) et un peu de porc. Pas trop de porc.

APPRENTISSAGE (base sur l'historique):
- La famille a aimé: {", ".join(recettes_aimees) if recettes_aimees else "pas encore assez de données"}
- La famille n'a pas aimé: {", ".join(recettes_pas_aimees) if recettes_pas_aimees else "pas encore assez de données"}

JOURS À PLANIFIER: {", ".join(jours_a_planifier)}

═══════════════════════════════════════════════════
⚠️ RÈGLES CRITIQUES DE CONCEPTION DU MENU:
═══════════════════════════════════════════════════

🔄 RÉUTILISATION DES REPAS (RÉCHAUFFÉ):
- Parmi les 14 repas (7 midis + 7 soirs), 3 à 4 MIDIS en semaine (lun-ven) DOIVENT être des réchauffés d'un DÎNER préparé un jour précédent.
- ⚠️ RÈGLE DU DÉCALAGE DE 2 JOURS: Le réchauffé doit être servi 2 jours APRÈS le dîner source (pas le lendemain).
  Cela laisse le temps au plat de reposer au frigo et permet de ne pas manger la même chose 2 jours de suite.
  Exemples VALIDES:
    - Lundi soir → réchauffé Mercredi midi (2 jours après)
    - Mardi soir → réchauffé Jeudi midi (2 jours après)
    - Mercredi soir → réchauffé Vendredi midi (2 jours après)
  Exemples INVALIDES:
    - Lundi soir → Mardi midi (trop tôt, seulement 1 jour)
    - Dimanche soir → Lundi midi (dimanche pas encore cuisiné en début de semaine)
    - Mardi soir → Mardi midi (même jour, impossible)
- Le premier réchauffé possible est MERCREDI midi (source: Lundi soir).
- Le dîner source est cuisiné en double portion. Le midi réchauffé est simplement réchauffé.
- Mettre "est_rechauffe": true et "rechauffe_de": "Lundi soir" pour ces midis.
- Résultat: seulement ~10 repas à cuisiner au lieu de 14.

🚫 VARIÉTÉ OBLIGATOIRE:
- Chaque plat cuisiné (non réchauffé) doit avoir un NOM DIFFÉRENT. JAMAIS 2 plats identiques dans la semaine.
- Même avec des ingrédients en commun, les RECETTES doivent être différentes (ex: courgettes → gratin de courgettes ET ratatouille, pas 2 gratins).
- Les réchauffés reprennent le même plat = c'est normal, mais la recette source ne doit apparaître QU'UNE seule fois comme dîner cuisiné.

{section_bases}
{section_recettes_imposees}

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
          "nom": "Pâtes au pesto et jambon",
          "proteine": "porc",
          "temps_minutes": 15,
          "robot": "plaque",
          "difficulte": "facile",
          "complexite": "simple",
          "est_rechauffe": false,
          "jules_adaptation": "Mixer les pâtes, couper le jambon en petits morceaux."
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
    {{"midi": "Mercredi midi", "source": "Lundi soir", "plat": "Émincés de poulet"}},
    {{"midi": "Jeudi midi", "source": "Mardi soir", "plat": "Gratin de courgettes"}},
    {{"midi": "Vendredi midi", "source": "Mercredi soir", "plat": "Curry de légumes"}}
  ],
  "equilibre_respecte": true,
  "conseils_batch": "Dimanche: préparer les légumes de base (courgettes, carottes). Couper le poulet en deux lots. Cuire le riz pour 2 jours.",
  "suggestions_bio": ["<5-8 suggestions VARIÉES et CONCRÈTES>"]
}}

🌿 SUGGESTIONS BIO/LOCAL (champ "suggestions_bio"):
- Génère 5 à 8 suggestions CONCRÈTES et VARIÉES, directement liées aux recettes du planning.
- Pour chaque ingrédient clé de la semaine, propose une alternative bio, locale, ou de meilleure qualité.
- Format: "Ingrédient bio/local + où le trouver ou pourquoi" (ex: "Courgettes bio de saison au marché", "Oeufs plein air Label Rouge")
- INTERDICTION de répéter "Poulet fermier Bio" et "Légumes Grand Frais" à chaque fois.
- Varier les catégories: viandes, poissons, légumes, fruits, produits laitiers, épicerie.
- Exemples de formats acceptés:
  "Saumon sauvage Label Rouge plutôt que d'élevage"
  "Carottes bio en vrac au marché (moins cher qu'en supermarché)"
  "Yaourts nature La Fermière ou local plutôt qu'industriel"
  "Huile d'olive extra-vierge première pression à froid"

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
- Poisson blanc dejà prevu: {contraintes_equilibre.get("poisson_blanc", 0)}/{preferences.poisson_blanc_par_semaine}
- Poisson gras dejà prevu: {contraintes_equilibre.get("poisson_gras", 0)}/{preferences.poisson_gras_par_semaine}
- Vegetarien: {contraintes_equilibre.get("vegetarien", 0)}/{preferences.vegetarien_par_semaine} max
- Viande rouge: {contraintes_equilibre.get("viande_rouge", 0)}/{preferences.viande_rouge_max} max

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
