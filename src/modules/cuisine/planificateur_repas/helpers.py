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
    "boeuf": {"label": "Boeuf", "emoji": "\U0001f404", "categorie": "viande_rouge"},
    "porc": {"label": "Porc", "emoji": "🐷", "categorie": "viande"},
    "agneau": {"label": "Agneau", "emoji": "🐑", "categorie": "viande_rouge"},
    "poisson": {"label": "Poisson", "emoji": "🐟", "categorie": "poisson"},
    "crevettes": {"label": "Crevettes", "emoji": "🦐", "categorie": "fruits_mer"},
    "oeufs": {"label": "Oeufs", "emoji": "\U0001f95a", "categorie": "vegetarien"},
    "tofu": {"label": "Tofu", "emoji": "🧊", "categorie": "vegan"},
    "legumineuses": {"label": "Legumineuses", "emoji": "🫘", "categorie": "vegetarien"},
}

# Équilibre recommande par semaine (nombre de repas)
EQUILIBRE_DEFAUT = {
    "poisson": 2,  # 2 fois poisson
    "viande_rouge": 1,  # Max 1-2 fois viande rouge
    "volaille": 2,  # 2-3 fois volaille
    "vegetarien": 2,  # 2 repas vege
    "pates_riz": 3,  # Max 3 feculents "lourds"
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
