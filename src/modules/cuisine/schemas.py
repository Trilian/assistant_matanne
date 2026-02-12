"""
Schemas/Dataclasses pour le domaine Cuisine.

Fichier sÃeparÃe pour Ãeviter les imports circulaires.
Contient les structures de donnÃees partagÃees entre:
- planificateur_repas_logic.py
- user_preferences.py (services)
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional, List


@dataclass
class PreferencesUtilisateur:
    """PrÃefÃerences alimentaires et contraintes de l'utilisateur."""
    
    # Personnes Ã  table
    nb_adultes: int = 2
    jules_present: bool = True
    jules_age_mois: int = 19
    
    # Temps de cuisine
    temps_semaine: str = "normal"  # express, normal, long
    temps_weekend: str = "long"
    
    # Goûts et restrictions
    aliments_exclus: List[str] = field(default_factory=list)
    aliments_favoris: List[str] = field(default_factory=list)
    
    # Équilibre souhaitÃe
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
    contexte: Optional[str] = None  # "trop long", "jules n'a pas aimÃe", etc.
    
    @property
    def score(self) -> int:
        """Score numÃerique pour l'apprentissage."""
        return {"like": 1, "neutral": 0, "dislike": -1}.get(self.feedback, 0)
