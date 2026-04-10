"""
Types et schémas Pydantic pour le package batch_cooking.

Module unifié avec tous les modèles de données pour les services de batch cooking.
Deux familles de schémas :
- Schéma « simplifié » (SessionBatchIA) pour generer_plan_ia (recettes DB)
- Schéma « détaillé » (PlanBatchDetailIA) pour generer_plan_depuis_planning (dict planning)
"""

from pydantic import BaseModel, ConfigDict, Field

# ═══════════════════════════════════════════════════════════
# SCHÉMA SIMPLIFIÉ (recettes DB → plan batch)
# ═══════════════════════════════════════════════════════════


class EtapeBatchIA(BaseModel):
    """Étape générée par l'IA pour une session batch cooking."""

    ordre: int = Field(..., ge=1)
    titre: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=5)
    duree_minutes: int = Field(..., ge=1, le=180)
    robots: list[str] = Field(default_factory=list)
    groupe_parallele: int = Field(default=0, ge=0)
    est_supervision: bool = Field(default=False)
    alerte_bruit: bool = Field(default=False)
    temperature: int | None = Field(default=None, ge=0, le=300)
    recette_nom: str | None = Field(default=None)


class SessionBatchIA(BaseModel):
    """Session batch cooking générée par l'IA."""

    recettes: list[str] = Field(..., min_length=1)
    duree_totale_estimee: int = Field(..., ge=5, le=480)
    etapes: list[EtapeBatchIA] = Field(..., min_length=1)
    conseils_jules: list[str] = Field(default_factory=list)
    ordre_optimal: str = Field(default="")


class PreparationIA(BaseModel):
    """Préparation générée par l'IA."""

    nom: str = Field(..., min_length=3, max_length=200)
    portions: int = Field(..., ge=1, le=20)
    conservation_jours: int = Field(..., ge=1, le=90)
    localisation: str = Field(default="frigo")
    container_suggere: str = Field(default="")


# ═══════════════════════════════════════════════════════════
# SCHÉMA DÉTAILLÉ (dict planning → instructions batch complètes)
# Permissif (extra="allow") car l'IA ajoute parfois des champs imprévus.
# ═══════════════════════════════════════════════════════════


class IngredientDetailIA(BaseModel):
    """Ingrédient détaillé généré par l'IA."""

    model_config = ConfigDict(extra="allow")

    nom: str = ""
    quantite: str = ""
    decoupe: str = ""
    tache_jules: str | None = None


class EtapeDetailIA(BaseModel):
    """Étape détaillée d'une recette batch cooking générée par l'IA."""

    model_config = ConfigDict(extra="allow")

    titre: str = ""
    duree_minutes: int = Field(default=10, ge=0, le=300)
    robot: str | None = None
    temperature: int | None = None
    est_passif: bool = False
    detail: str = ""
    jules_participation: bool = False
    tache_jules: str | None = None


class RecetteDetailIA(BaseModel):
    """Recette détaillée générée par l'IA pour le batch cooking."""

    model_config = ConfigDict(extra="allow")

    nom: str = ""
    pour_jours: list[str] = Field(default_factory=list)
    portions: int = Field(default=4, ge=1, le=20)
    ingredients: list[IngredientDetailIA] = Field(default_factory=list)
    etapes_batch: list[EtapeDetailIA] = Field(default_factory=list)
    instructions_finition: list[str] = Field(default_factory=list)
    stockage: str = "frigo"
    duree_conservation_jours: int = Field(default=3, ge=1, le=90)


class MomentJulesIA(BaseModel):
    """Moment de participation de Jules généré par l'IA."""

    model_config = ConfigDict(extra="allow")

    temps: str = ""
    tache: str = ""


class TimelineEntryIA(BaseModel):
    """Entrée de la timeline générée par l'IA."""

    model_config = ConfigDict(extra="allow")

    debut_min: int = Field(default=0, ge=0)
    fin_min: int = Field(default=0, ge=0)
    tache: str = ""
    robot: str | None = None


class SessionInfoIA(BaseModel):
    """Info de session générale générée par l'IA."""

    model_config = ConfigDict(extra="allow")

    duree_estimee_minutes: int = Field(default=120, ge=5, le=480)
    conseils_organisation: list[str] = Field(default_factory=list)


class PlanBatchDetailIA(BaseModel):
    """Plan complet de batch cooking détaillé généré par l'IA.

    Schéma riche retourné par generer_plan_depuis_planning().
    Validation permissive (extra='allow') pour tolérer les variations IA.
    """

    model_config = ConfigDict(extra="allow")

    session: SessionInfoIA = Field(default_factory=SessionInfoIA)
    recettes: list[RecetteDetailIA] = Field(default_factory=list)
    moments_jules: list[MomentJulesIA] = Field(default_factory=list)
    timeline: list[TimelineEntryIA] = Field(default_factory=list)


__all__ = [
    "EtapeBatchIA",
    "SessionBatchIA",
    "PreparationIA",
    "IngredientDetailIA",
    "EtapeDetailIA",
    "RecetteDetailIA",
    "MomentJulesIA",
    "TimelineEntryIA",
    "SessionInfoIA",
    "PlanBatchDetailIA",
]
