"""
Constantes et dataclasses du Planificateur de Repas

Types de donnees et constantes partagees.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Any

from src.core.constants import JOURS_SEMAINE

# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

# Types de repas
TYPES_REPAS = ["déjeuner", "dîner", "goûter"]

# Categories de proteines
PROTEINES = {
    "poulet": {"label": "Poulet", "emoji": "🐔", "categorie": "volaille"},
    "boeuf": {"label": "Boeuf", "emoji": "🐄", "categorie": "viande_rouge"},
    "porc": {"label": "Porc", "emoji": "🐷", "categorie": "viande"},
    "agneau": {"label": "Agneau", "emoji": "🐑", "categorie": "viande_rouge"},
    "poisson": {"label": "Poisson", "emoji": "🐟", "categorie": "poisson"},
    "saumon": {"label": "Saumon", "emoji": "🩽", "categorie": "poisson_gras"},
    "cabillaud": {"label": "Cabillaud", "emoji": "🐟", "categorie": "poisson_blanc"},
    "crevettes": {"label": "Crevettes", "emoji": "🦐", "categorie": "fruits_mer"},
    "oeufs": {"label": "Oeufs", "emoji": "🥚", "categorie": "autre"},
    "tofu": {"label": "Tofu", "emoji": "🧊", "categorie": "vegan"},
    "legumineuses": {"label": "Legumineuses", "emoji": "🫘", "categorie": "vegetarien"},
}

# Légumes de base courants pour le batch cooking
LEGUMES_BASE = [
    "carottes", "courgettes", "poireaux", "tomates", "oignons",
    "brocoli", "haricots verts", "épinards", "champignons", "poivrons",
    "aubergines", "chou-fleur", "petits pois", "patate douce", "potimarron",
    "céleri", "navets", "betteraves", "fenouil", "endives",
]

# Féculents de base courants
FECULENTS_BASE = [
    "riz", "pâtes", "pommes de terre", "semoule", "quinoa",
    "lentilles", "boulgour", "blé", "gnocchi", "pain",
    "pois chiches", "haricots blancs", "polenta", "patate douce",
]

# Protéines de base
PROTEINES_BASE = [
    "poulet", "boeuf haché", "porc", "saumon", "cabillaud",
    "oeufs", "tofu", "lentilles", "crevettes", "dinde",
    "merlu", "thon", "agneau", "jambon", "sardines",
]

# Équilibre recommande par semaine (nombre de repas)
EQUILIBRE_DEFAUT = {
    "poisson_blanc": 1,  # 1 fois poisson blanc (cabillaud, merlu, colin...)
    "poisson_gras": 1,  # 1 fois poisson gras (saumon, sardine, thon...)
    "viande_rouge": 1,  # Max 1-2 fois viande rouge
    "volaille": 3,  # Volaille = protéine principale
    "vegetarien": 2,  # 1-2 repas vegétariens/vegan
    "pates_riz": 3,  # Max 3 féculents "lourds"
}

# Temps de preparation
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

# Desserts adaptés Jules (19 mois)
DESSERTS_JULES = [
    "Compote pomme",
    "Compote pomme-banane",
    "Compote pomme-poire",
    "Compote poire",
    "Compote pêche-abricot",
    "Yaourt nature",
    "Petit-suisse nature",
    "Fromage blanc",
    "Fruit frais (banane)",
    "Fruit frais (fraise)",
    "Fruit frais (kiwi)",
    "Fruit frais (mangue)",
    "Semoule au lait",
    "Riz au lait",
    "Biscuit bébé",
    "Crème dessert vanille",
]

# Desserts famille
DESSERTS_FAMILLE = [
    "Yaourt nature",
    "Yaourt aux fruits",
    "Fruit frais",
    "Salade de fruits",
    "Compote",
    "Fromage blanc",
    "Crème dessert",
    "Mousse au chocolat",
    "Tarte aux fruits",
    "Crumble",
    "Clafoutis",
    "Gâteau au yaourt",
    "Île flottante",
    "Panna cotta",
    "Flan",
]

# Entrées simples
ENTREES_SUGGESTIONS = [
    "Salade verte",
    "Salade de tomates",
    "Salade de concombre",
    "Soupe de légumes",
    "Velouté",
    "Carottes râpées",
    "Crudités",
    "Taboulé",
    "Melon",
    "Avocat vinaigrette",
]


# ═══════════════════════════════════════════════════════════
# DATACLASSES
# ═══════════════════════════════════════════════════════════


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
    type_proteine: str | None = None
    categorie_proteine: str | None = None

    # Tags
    compatible_batch: bool = False
    compatible_jules: bool = True
    est_vegetarien: bool = False
    est_bio_possible: bool = False
    est_local_possible: bool = False

    # Version Jules
    instructions_jules: str | None = None

    # Robot suggere
    robot_suggere: str | None = None

    # Score IA
    score_match: float = 0.0  # 0-100, correspondance avec preferences
    raison_suggestion: str | None = None

    # Stock
    ingredients_en_stock: list[str] = field(default_factory=list)
    ingredients_manquants: list[str] = field(default_factory=list)

    @property
    def temps_total(self) -> int:
        return self.temps_preparation + self.temps_cuisson

    @property
    def emoji_difficulte(self) -> str:
        return {"facile": "🟢", "moyen": "🟡", "difficile": "🔴"}.get(self.difficulte, "⚪")


@dataclass
class RepasPlannifie:
    """Un repas planifie dans la semaine."""

    jour: date
    type_repas: str  # dejeuner, dîner, goûter
    recette: RecetteSuggestion | None = None
    notes: str | None = None
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
    repas: list[RepasPlannifie] = field(default_factory=list)
    gouters: list[RepasPlannifie] = field(default_factory=list)

    @property
    def nb_repas_planifies(self) -> int:
        return len([r for r in self.repas if not r.est_vide])

    @property
    def nb_repas_total(self) -> int:
        return len(self.repas)

    def get_repas_jour(self, jour: date) -> list[RepasPlannifie]:
        return [r for r in self.repas if r.jour == jour]

    def get_equilibre(self) -> dict[str, int]:
        """Calcule l'equilibre actuel de la semaine."""
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
