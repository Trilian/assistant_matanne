"""
Types et schémas pour le package PDF.

Centralise tous les modèles Pydantic pour les services PDF.
"""

from datetime import datetime
from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════
# SCHÉMAS EXPORT (ex pdf_export.py)
# ═══════════════════════════════════════════════════════════


class DonneesRecettePDF(BaseModel):
    """Données pour export recette PDF."""
    id: int
    nom: str
    description: str = ""
    temps_preparation: int = 0
    temps_cuisson: int = 0
    portions: int = 4
    difficulte: str = "facile"
    ingredients: list[dict] = Field(default_factory=list)
    etapes: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class DonneesPlanningPDF(BaseModel):
    """Données pour export planning PDF."""
    semaine_debut: datetime
    semaine_fin: datetime
    repas_par_jour: dict = Field(default_factory=dict)
    total_repas: int = 0


class DonneesCoursesPDF(BaseModel):
    """Données pour export liste courses PDF."""
    date_export: datetime = Field(default_factory=datetime.now)
    articles: list[dict] = Field(default_factory=list)
    total_articles: int = 0
    par_categorie: dict = Field(default_factory=dict)


# ═══════════════════════════════════════════════════════════
# SCHÉMAS RAPPORTS (ex rapports_pdf.py)
# ═══════════════════════════════════════════════════════════


class RapportStocks(BaseModel):
    """Données pour rapport stocks."""
    date_rapport: datetime = Field(default_factory=datetime.now)
    periode_jours: int = Field(7, ge=1, le=365)
    articles_total: int = 0
    articles_faible_stock: list[dict] = Field(default_factory=list)
    articles_perimes: list[dict] = Field(default_factory=list)
    valeur_stock_total: float = 0.0
    categories_resumee: dict = Field(default_factory=dict)


class RapportBudget(BaseModel):
    """Données pour rapport budget."""
    date_rapport: datetime = Field(default_factory=datetime.now)
    periode_jours: int = Field(30, ge=1, le=365)
    depenses_total: float = 0.0
    depenses_par_categorie: dict = Field(default_factory=dict)
    evolution_semaine: list[dict] = Field(default_factory=list)
    articles_couteux: list[dict] = Field(default_factory=list)


class AnalyseGaspillage(BaseModel):
    """Données pour analyse gaspillage."""
    date_rapport: datetime = Field(default_factory=datetime.now)
    periode_jours: int = Field(30, ge=1, le=365)
    articles_perimes_total: int = 0
    valeur_perdue: float = 0.0
    categories_gaspillage: dict = Field(default_factory=dict)
    recommandations: list[str] = Field(default_factory=list)
    articles_perimes_detail: list[dict] = Field(default_factory=list)


class RapportPlanning(BaseModel):
    """Données pour rapport planning hebdomadaire."""
    date_rapport: datetime = Field(default_factory=datetime.now)
    planning_id: int = 0
    nom_planning: str = ""
    semaine_debut: datetime | None = None
    semaine_fin: datetime | None = None
    repas_par_jour: dict = Field(default_factory=dict)
    total_repas: int = 0
    liste_courses_estimee: list[dict] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# ALIAS RÉTROCOMPATIBILITÉ
# ═══════════════════════════════════════════════════════════

# Alias anglais pour pdf_export.py
RecettePDFData = DonneesRecettePDF
PlanningPDFData = DonneesPlanningPDF
CoursesPDFData = DonneesCoursesPDF


# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════

__all__ = [
    # Schémas export (français)
    "DonneesRecettePDF",
    "DonneesPlanningPDF",
    "DonneesCoursesPDF",
    # Schémas rapports (français)
    "RapportStocks",
    "RapportBudget",
    "AnalyseGaspillage",
    "RapportPlanning",
    # Alias rétrocompatibilité
    "RecettePDFData",
    "PlanningPDFData",
    "CoursesPDFData",
]
