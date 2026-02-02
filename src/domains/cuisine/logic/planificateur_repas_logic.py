"""
Logique métier du Planificateur de Repas Intelligent

Inspiré de Jow:
- Génération IA de menus équilibrés
- Apprentissage des goûts (👍/👎)
- Versions Jules intégrées aux recettes
- Prise en compte du stock existant
- Suggestions alternatives

Séparée de l'UI pour être testable sans Streamlit.
"""

from datetime import date, timedelta, time
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

JOURS_SEMAINE = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

# Types de repas
TYPES_REPAS = ["déjeuner", "dîner", "goûter"]

# Catégories de protéines
PROTEINES = {
    "poulet": {"label": "Poulet", "emoji": "🐔", "categorie": "volaille"},
    "boeuf": {"label": "Bœuf", "emoji": "🐄", "categorie": "viande_rouge"},
    "porc": {"label": "Porc", "emoji": "🐷", "categorie": "viande"},
    "agneau": {"label": "Agneau", "emoji": "🐑", "categorie": "viande_rouge"},
    "poisson": {"label": "Poisson", "emoji": "🐟", "categorie": "poisson"},
    "crevettes": {"label": "Crevettes", "emoji": "🦐", "categorie": "fruits_mer"},
    "oeufs": {"label": "Œufs", "emoji": "🥚", "categorie": "vegetarien"},
    "tofu": {"label": "Tofu", "emoji": "🧊", "categorie": "vegan"},
    "legumineuses": {"label": "Légumineuses", "emoji": "🫘", "categorie": "vegetarien"},
}

# Équilibre recommandé par semaine (nombre de repas)
EQUILIBRE_DEFAUT = {
    "poisson": 2,           # 2 fois poisson
    "viande_rouge": 1,      # Max 1-2 fois viande rouge
    "volaille": 2,          # 2-3 fois volaille
    "vegetarien": 2,        # 2 repas végé
    "pates_riz": 3,         # Max 3 féculents "lourds"
}

# Temps de préparation
TEMPS_CATEGORIES = {
    "express": {"max_minutes": 20, "label": "Express (< 20 min)"},
    "normal": {"max_minutes": 40, "label": "Normal (20-40 min)"},
    "long": {"max_minutes": 90, "label": "Long (> 40 min)"},
}

# Robots cuisine
ROBOTS_CUISINE = {
    "monsieur_cuisine": {"label": "Monsieur Cuisine", "emoji": "🤖"},
    "cookeo": {"label": "Cookeo", "emoji": "🍲"},
    "four": {"label": "Four", "emoji": "🔥"},
    "airfryer": {"label": "Airfryer", "emoji": "🍟"},
    "poele": {"label": "Poêle/Casserole", "emoji": "🍳"},
}


# ═══════════════════════════════════════════════════════════
# DATACLASSES
# ═══════════════════════════════════════════════════════════


@dataclass
class PreferencesUtilisateur:
    """Préférences alimentaires et contraintes de l'utilisateur."""
    
    # Personnes à table
    nb_adultes: int = 2
    jules_present: bool = True
    jules_age_mois: int = 19
    
    # Temps de cuisine
    temps_semaine: str = "normal"  # express, normal, long
    temps_weekend: str = "long"
    
    # Goûts et restrictions
    aliments_exclus: List[str] = field(default_factory=list)
    aliments_favoris: List[str] = field(default_factory=list)
    
    # Équilibre souhaité
    poisson_par_semaine: int = 2
    vegetarien_par_semaine: int = 1
    viande_rouge_max: int = 2
    
    # Robots disponibles
    robots: List[str] = field(default_factory=lambda: ["four", "poele"])
    
    # Magasins
    magasins_preferes: List[str] = field(default_factory=lambda: ["Carrefour", "Bio Coop", "Grand Frais"])
    
    # Budget
    budget_semaine: Optional[float] = None
    
    def to_dict(self) -> dict:
        return {
            "nb_adultes": self.nb_adultes,
            "jules_present": self.jules_present,
            "jules_age_mois": self.jules_age_mois,
            "temps_semaine": self.temps_semaine,
            "temps_weekend": self.temps_weekend,
            "aliments_exclus": self.aliments_exclus,
            "aliments_favoris": self.aliments_favoris,
            "poisson_par_semaine": self.poisson_par_semaine,
            "vegetarien_par_semaine": self.vegetarien_par_semaine,
            "viande_rouge_max": self.viande_rouge_max,
            "robots": self.robots,
            "magasins_preferes": self.magasins_preferes,
            "budget_semaine": self.budget_semaine,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "PreferencesUtilisateur":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class FeedbackRecette:
    """Feedback utilisateur sur une recette (apprentissage)."""
    recette_id: int
    recette_nom: str
    feedback: str  # "like", "dislike", "neutral"
    date_feedback: Optional[date] = field(default_factory=date.today)
    contexte: Optional[str] = None  # "trop long", "jules n'a pas aimé", etc.
    
    @property
    def score(self) -> int:
        """Score numérique pour l'apprentissage."""
        return {"like": 1, "neutral": 0, "dislike": -1}.get(self.feedback, 0)


@dataclass
class RecetteSuggestion:
    """Suggestion de recette pour le planificateur."""
    id: int
    nom: str
    description: str
    temps_preparation: int
    temps_cuisson: int
    portions: int
    difficulte: str
    type_proteine: Optional[str] = None
    categorie_proteine: Optional[str] = None
    
    # Tags
    compatible_batch: bool = False
    compatible_jules: bool = True
    est_vegetarien: bool = False
    est_bio_possible: bool = False
    est_local_possible: bool = False
    
    # Version Jules
    instructions_jules: Optional[str] = None
    
    # Robot suggéré
    robot_suggere: Optional[str] = None
    
    # Score IA
    score_match: float = 0.0  # 0-100, correspondance avec préférences
    raison_suggestion: Optional[str] = None
    
    # Stock
    ingredients_en_stock: List[str] = field(default_factory=list)
    ingredients_manquants: List[str] = field(default_factory=list)
    
    @property
    def temps_total(self) -> int:
        return self.temps_preparation + self.temps_cuisson
    
    @property
    def emoji_difficulte(self) -> str:
        return {"facile": "🟢", "moyen": "🟡", "difficile": "🔴"}.get(self.difficulte, "⚪")


@dataclass
class RepasPlannifie:
    """Un repas planifié dans la semaine."""
    jour: date
    type_repas: str  # déjeuner, dîner, goûter
    recette: Optional[RecetteSuggestion] = None
    notes: Optional[str] = None
    prepare: bool = False  # Pour batch cooking
    
    @property
    def est_vide(self) -> bool:
        return self.recette is None
    
    @property
    def jour_nom(self) -> str:
        return JOURS_SEMAINE[self.jour.weekday()]


@dataclass
class PlanningSemaine:
    """Planning complet d'une semaine."""
    date_debut: date
    date_fin: date
    repas: List[RepasPlannifie] = field(default_factory=list)
    gouters: List[RepasPlannifie] = field(default_factory=list)
    
    @property
    def nb_repas_planifies(self) -> int:
        return len([r for r in self.repas if not r.est_vide])
    
    @property
    def nb_repas_total(self) -> int:
        return len(self.repas)
    
    def get_repas_jour(self, jour: date) -> List[RepasPlannifie]:
        return [r for r in self.repas if r.jour == jour]
    
    def get_equilibre(self) -> Dict[str, int]:
        """Calcule l'équilibre actuel de la semaine."""
        equilibre = {
            "poisson": 0,
            "viande_rouge": 0,
            "volaille": 0,
            "vegetarien": 0,
        }
        
        for repas in self.repas:
            if repas.recette and repas.recette.categorie_proteine:
                cat = repas.recette.categorie_proteine
                if cat in equilibre:
                    equilibre[cat] += 1
                elif cat == "vegan":
                    equilibre["vegetarien"] += 1
        
        return equilibre


# ═══════════════════════════════════════════════════════════
# APPRENTISSAGE DES GOÛTS
# ═══════════════════════════════════════════════════════════


def calculer_score_recette(
    recette: Any,
    preferences: PreferencesUtilisateur,
    feedbacks: List[FeedbackRecette],
    equilibre_actuel: Dict[str, int],
    stock_disponible: List[str],
) -> Tuple[float, str]:
    """
    Calcule un score de pertinence pour une recette.
    
    Args:
        recette: Objet recette (SQLAlchemy ou dict)
        preferences: Préférences utilisateur
        feedbacks: Historique des feedbacks
        equilibre_actuel: Équilibre de la semaine en cours
        stock_disponible: Ingrédients en stock
    
    Returns:
        (score 0-100, raison principale)
    """
    score = 50.0  # Score de base
    raison = "Suggestion standard"
    
    # Nom de la recette
    nom = recette.nom if hasattr(recette, 'nom') else recette.get('nom', '')
    recette_id = recette.id if hasattr(recette, 'id') else recette.get('id', 0)
    
    # 1. Vérifier les exclusions (éliminatoire)
    for exclu in preferences.aliments_exclus:
        if exclu.lower() in nom.lower():
            return 0.0, f"Contient {exclu} (exclu)"
    
    # 2. Bonus pour les favoris (+20)
    for favori in preferences.aliments_favoris:
        if favori.lower() in nom.lower():
            score += 20
            raison = f"Contient {favori} (favori)"
    
    # 3. Feedback historique (+/- 15)
    for fb in feedbacks:
        if fb.recette_id == recette_id:
            score += fb.score * 15
            if fb.feedback == "like":
                raison = "Vous avez aimé cette recette"
            elif fb.feedback == "dislike":
                raison = "Vous n'avez pas aimé cette recette"
    
    # 4. Équilibre de la semaine (+10 si manquant)
    categorie = None
    if hasattr(recette, 'type_proteine'):
        prot = recette.type_proteine
        if prot in PROTEINES:
            categorie = PROTEINES[prot]["categorie"]
    
    if categorie:
        objectif = {
            "poisson": preferences.poisson_par_semaine,
            "vegetarien": preferences.vegetarien_par_semaine,
            "viande_rouge": preferences.viande_rouge_max,
        }.get(categorie, 2)
        
        actuel = equilibre_actuel.get(categorie, 0)
        
        if actuel < objectif:
            score += 10
            raison = f"Aide à l'équilibre ({categorie})"
        elif categorie == "viande_rouge" and actuel >= objectif:
            score -= 15
            raison = "Déjà assez de viande rouge cette semaine"
    
    # 5. Stock disponible (+15 si ingrédients en stock)
    nb_en_stock = 0
    if hasattr(recette, 'ingredients') and recette.ingredients:
        for ing in recette.ingredients:
            ing_nom = ing.nom if hasattr(ing, 'nom') else ing.get('nom', '')
            if any(s.lower() in ing_nom.lower() for s in stock_disponible):
                nb_en_stock += 1
        
        if nb_en_stock >= 3:
            score += 15
            raison = f"Utilise {nb_en_stock} ingrédients de votre stock"
    
    # 6. Temps de préparation
    temps_total = 0
    if hasattr(recette, 'temps_preparation'):
        temps_total = recette.temps_preparation + (recette.temps_cuisson or 0)
    
    temps_max = TEMPS_CATEGORIES.get(preferences.temps_semaine, {}).get("max_minutes", 40)
    if temps_total > temps_max:
        score -= 10
        raison = f"Temps de préparation long ({temps_total} min)"
    
    # 7. Compatible Jules (+5)
    if preferences.jules_present:
        if hasattr(recette, 'compatible_bebe') and recette.compatible_bebe:
            score += 5
        elif hasattr(recette, 'instructions_bebe') and recette.instructions_bebe:
            score += 5
    
    # 8. Compatible batch cooking (+5)
    if hasattr(recette, 'compatible_batch') and recette.compatible_batch:
        score += 5
    
    # Normaliser entre 0 et 100
    score = max(0, min(100, score))
    
    return score, raison


def filtrer_recettes_eligibles(
    recettes: List[Any],
    preferences: PreferencesUtilisateur,
    type_repas: str = "déjeuner",
) -> List[Any]:
    """
    Filtre les recettes éligibles selon les contraintes.
    
    Args:
        recettes: Liste des recettes
        preferences: Préférences utilisateur
        type_repas: Type de repas (déjeuner, dîner, goûter)
    
    Returns:
        Liste filtrée
    """
    eligibles = []
    
    for recette in recettes:
        nom = recette.nom if hasattr(recette, 'nom') else recette.get('nom', '')
        
        # Vérifier exclusions
        exclu = False
        for aliment_exclu in preferences.aliments_exclus:
            if aliment_exclu.lower() in nom.lower():
                exclu = True
                break
        
        if exclu:
            continue
        
        # Vérifier type de repas
        if hasattr(recette, 'type_repas'):
            if recette.type_repas and type_repas not in recette.type_repas:
                continue
        
        eligibles.append(recette)
    
    return eligibles


def generer_suggestions_alternatives(
    recette_actuelle: RecetteSuggestion,
    toutes_recettes: List[Any],
    preferences: PreferencesUtilisateur,
    feedbacks: List[FeedbackRecette],
    equilibre_actuel: Dict[str, int],
    stock: List[str],
    nb_alternatives: int = 3,
) -> List[RecetteSuggestion]:
    """
    Génère des alternatives à une recette.
    
    Returns:
        Liste de suggestions alternatives triées par score
    """
    alternatives = []
    
    # Filtrer les recettes similaires (même type de repas)
    eligibles = filtrer_recettes_eligibles(toutes_recettes, preferences)
    
    for recette in eligibles:
        recette_id = recette.id if hasattr(recette, 'id') else recette.get('id', 0)
        
        # Ignorer la recette actuelle
        if recette_actuelle and recette_id == recette_actuelle.id:
            continue
        
        score, raison = calculer_score_recette(
            recette, preferences, feedbacks, equilibre_actuel, stock
        )
        
        if score > 30:  # Seuil minimum
            suggestion = RecetteSuggestion(
                id=recette_id,
                nom=recette.nom if hasattr(recette, 'nom') else recette.get('nom', ''),
                description=recette.description if hasattr(recette, 'description') else '',
                temps_preparation=recette.temps_preparation if hasattr(recette, 'temps_preparation') else 30,
                temps_cuisson=recette.temps_cuisson if hasattr(recette, 'temps_cuisson') else 0,
                portions=recette.portions if hasattr(recette, 'portions') else 4,
                difficulte=recette.difficulte if hasattr(recette, 'difficulte') else 'moyen',
                score_match=score,
                raison_suggestion=raison,
                instructions_jules=recette.instructions_bebe if hasattr(recette, 'instructions_bebe') else None,
                compatible_batch=recette.compatible_batch if hasattr(recette, 'compatible_batch') else False,
            )
            alternatives.append(suggestion)
    
    # Trier par score et limiter
    alternatives.sort(key=lambda x: x.score_match, reverse=True)
    
    return alternatives[:nb_alternatives]


# ═══════════════════════════════════════════════════════════
# GÉNÉRATION DE PROMPTS IA
# ═══════════════════════════════════════════════════════════


def generer_prompt_semaine(
    preferences: PreferencesUtilisateur,
    feedbacks: List[FeedbackRecette],
    date_debut: date,
    jours_a_planifier: List[str] = None,
) -> str:
    """
    Génère un prompt pour l'IA pour créer une semaine de repas.
    
    Args:
        preferences: Préférences utilisateur
        feedbacks: Historique feedbacks pour apprentissage
        date_debut: Date de début de la semaine
        jours_a_planifier: Liste des jours (si partiel)
    
    Returns:
        Prompt formaté pour l'IA
    """
    
    # Construire le contexte d'apprentissage
    recettes_aimees = [f.recette_nom for f in feedbacks if f.feedback == "like"][-10:]
    recettes_pas_aimees = [f.recette_nom for f in feedbacks if f.feedback == "dislike"][-5:]
    
    # Jours à planifier
    if not jours_a_planifier:
        jours_a_planifier = JOURS_SEMAINE
    
    prompt = f"""Tu es un assistant culinaire familial expert. Génère un planning de repas pour une famille.

CONTEXTE FAMILLE:
- {preferences.nb_adultes} adultes
- 1 bébé de {preferences.jules_age_mois} mois (Jules) qui mange avec nous
- Robots cuisine disponibles: {', '.join(preferences.robots)}

CONTRAINTES:
- Temps de cuisine en semaine: {preferences.temps_semaine} ({TEMPS_CATEGORIES[preferences.temps_semaine]['label']})
- Aliments à ÉVITER: {', '.join(preferences.aliments_exclus) if preferences.aliments_exclus else 'aucun'}
- Aliments favoris: {', '.join(preferences.aliments_favoris) if preferences.aliments_favoris else 'variés'}

ÉQUILIBRE SOUHAITÉ PAR SEMAINE:
- Poisson: {preferences.poisson_par_semaine} fois
- Repas végétarien: {preferences.vegetarien_par_semaine} fois
- Viande rouge: maximum {preferences.viande_rouge_max} fois

APPRENTISSAGE (basé sur l'historique):
- La famille a aimé: {', '.join(recettes_aimees) if recettes_aimees else 'pas encore assez de données'}
- La famille n'a pas aimé: {', '.join(recettes_pas_aimees) if recettes_pas_aimees else 'pas encore assez de données'}

JOURS À PLANIFIER: {', '.join(jours_a_planifier)}

Pour chaque repas, fournis:
1. Nom du plat (simple et familial)
2. Type de protéine principale
3. Temps total de préparation
4. Instructions SPÉCIFIQUES pour adapter le repas à Jules ({preferences.jules_age_mois} mois):
   - Comment adapter la texture
   - Quelle quantité prélever avant assaisonnement
   - Comment servir pour son âge

FORMAT DE RÉPONSE (JSON):
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
        "jules_adaptation": "Prélever 80g de poulet et légumes avant sel. Mixer grossièrement pour texture avec morceaux. Servir tiède."
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
  "conseils_batch": "Dimanche: préparer la sauce bolognaise et la soupe. Mercredi: poulet mariné + gratin.",
  "suggestions_bio": ["Le poulet fermier Bio Coop", "Les légumes Grand Frais"]
}}
"""
    
    return prompt


def generer_prompt_alternative(
    recette_a_remplacer: str,
    type_repas: str,
    jour: str,
    preferences: PreferencesUtilisateur,
    contraintes_equilibre: Dict[str, int],
) -> str:
    """
    Génère un prompt pour obtenir des alternatives à une recette.
    """
    
    prompt = f"""Propose 3 alternatives à "{recette_a_remplacer}" pour le {type_repas} du {jour}.

CONTRAINTES:
- Famille avec bébé de {preferences.jules_age_mois} mois
- Temps disponible: {preferences.temps_semaine}
- Équipement: {', '.join(preferences.robots)}
- À éviter: {', '.join(preferences.aliments_exclus) if preferences.aliments_exclus else 'rien'}

ÉQUILIBRE ACTUEL DE LA SEMAINE:
- Poisson déjà prévu: {contraintes_equilibre.get('poisson', 0)}/{preferences.poisson_par_semaine}
- Végétarien: {contraintes_equilibre.get('vegetarien', 0)}/{preferences.vegetarien_par_semaine}
- Viande rouge: {contraintes_equilibre.get('viande_rouge', 0)}/{preferences.viande_rouge_max}

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


# ═══════════════════════════════════════════════════════════
# VALIDATION ET ÉQUILIBRE
# ═══════════════════════════════════════════════════════════


def valider_equilibre_semaine(
    planning: PlanningSemaine,
    preferences: PreferencesUtilisateur,
) -> Tuple[bool, List[str]]:
    """
    Valide l'équilibre nutritionnel d'une semaine.
    
    Returns:
        (est_valide, liste_alertes)
    """
    alertes = []
    equilibre = planning.get_equilibre()
    
    # Vérifier poisson
    if equilibre["poisson"] < preferences.poisson_par_semaine:
        alertes.append(f"⚠️ Seulement {equilibre['poisson']} repas poisson (objectif: {preferences.poisson_par_semaine})")
    
    # Vérifier végétarien
    if equilibre["vegetarien"] < preferences.vegetarien_par_semaine:
        alertes.append(f"⚠️ Seulement {equilibre['vegetarien']} repas végétarien (objectif: {preferences.vegetarien_par_semaine})")
    
    # Vérifier viande rouge
    if equilibre["viande_rouge"] > preferences.viande_rouge_max:
        alertes.append(f"⚠️ Trop de viande rouge: {equilibre['viande_rouge']} (max: {preferences.viande_rouge_max})")
    
    # Vérifier repas planifiés
    if planning.nb_repas_planifies < 10:  # Au moins 10 repas sur 14 possibles
        alertes.append(f"⚠️ Seulement {planning.nb_repas_planifies} repas planifiés sur 14")
    
    est_valide = len(alertes) == 0
    
    return est_valide, alertes


def suggerer_ajustements_equilibre(
    equilibre_actuel: Dict[str, int],
    preferences: PreferencesUtilisateur,
) -> List[str]:
    """
    Suggère des ajustements pour atteindre l'équilibre.
    
    Returns:
        Liste de suggestions
    """
    suggestions = []
    
    if equilibre_actuel["poisson"] < preferences.poisson_par_semaine:
        manque = preferences.poisson_par_semaine - equilibre_actuel["poisson"]
        suggestions.append(f"Ajouter {manque} repas poisson (saumon, cabillaud, sardines...)")
    
    if equilibre_actuel["vegetarien"] < preferences.vegetarien_par_semaine:
        manque = preferences.vegetarien_par_semaine - equilibre_actuel["vegetarien"]
        suggestions.append(f"Ajouter {manque} repas végétarien (omelette, gratin légumes, curry légumineuses...)")
    
    if equilibre_actuel["viande_rouge"] > preferences.viande_rouge_max:
        exces = equilibre_actuel["viande_rouge"] - preferences.viande_rouge_max
        suggestions.append(f"Remplacer {exces} repas viande rouge par du poulet ou poisson")
    
    return suggestions
