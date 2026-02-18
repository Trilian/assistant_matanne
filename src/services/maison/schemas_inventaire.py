"""
Schemas Pydantic pour l'Inventaire Maison.

Modèles de validation pour:
- Pièces, conteneurs, versioning
- Objets (création, mise à jour, statut)
- Recherche d'objets
- Intégration inter-modules (courses, budget)
- Pipeline automatique
"""

from datetime import date as date_type
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .schemas_enums import (
    CategorieObjet,
    NiveauUrgence,
    PrioriteRemplacement,
    StatutObjet,
    TypeModificationPiece,
)

__all__ = [
    "ConteneurCreate",
    "PieceCreate",
    "ModificationPieceCreate",
    "PieceVersion",
    "PlanReorganisationPiece",
    "CoutTravauxPiece",
    "ResumeTravauxMaison",
    "ObjetCreate",
    "ObjetUpdate",
    "DemandeChangementObjet",
    "ObjetAvecStatut",
    "ResultatRecherche",
    "ArticleCoursesGenere",
    "PipelineResult",
    "PipelineResultat",
    "LienObjetBudget",
    "LienObjetCourses",
    "ActionObjetResult",
]


# ═══════════════════════════════════════════════════════════
# INVENTAIRE MAISON
# ═══════════════════════════════════════════════════════════


class ConteneurCreate(BaseModel):
    """Conteneur/rangement dans une pièce."""

    nom: str
    type: str  # placard, tiroir, etagere, boite, autre
    position: str | None = None  # gauche, droite, sous_evier


class PieceCreate(BaseModel):
    """Création d'une pièce."""

    nom: str
    etage: str = "RDC"  # RDC, 1er, Sous-sol, Grenier
    superficie_m2: float | None = None
    conteneurs: list[ConteneurCreate] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# VERSIONING PIÈCES & COÛTS TRAVAUX
# ═══════════════════════════════════════════════════════════


class ModificationPieceCreate(BaseModel):
    """Modification apportée à une pièce (pour versioning)."""

    type_modification: TypeModificationPiece
    description: str
    objet_concerne: str | None = None  # Ex: "Bibliothèque BILLY"
    cout_estime: Decimal = Decimal("0")
    cout_reel: Decimal | None = None
    date_modification: date_type = Field(default_factory=date_type.today)
    notes: str | None = None


class PieceVersion(BaseModel):
    """Version d'une pièce avec son état à un moment donné."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    piece_id: int
    numero_version: int
    date_creation: datetime
    nom_version: str | None = None  # Ex: "Avant réaménagement", "Config été 2024"
    modifications: list[ModificationPieceCreate] = Field(default_factory=list)
    cout_total_version: Decimal = Decimal("0")
    image_url: str | None = None  # Photo avant/après
    commentaire: str | None = None


class PlanReorganisationPiece(BaseModel):
    """Plan de réorganisation d'une pièce avec coûts."""

    piece_id: int
    nom_version: str  # Ex: "Nouveau bureau gaming"
    modifications_prevues: list[ModificationPieceCreate] = Field(default_factory=list)
    budget_total_estime: Decimal = Decimal("0")
    objets_a_acheter: list["ObjetCreate"] = Field(default_factory=list)
    objets_a_retirer: list[int] = Field(default_factory=list)  # IDs des objets
    date_fin_prevue: date_type | None = None
    ajouter_au_budget_global: bool = True


class CoutTravauxPiece(BaseModel):
    """Suivi des coûts de travaux pour une pièce."""

    model_config = ConfigDict(from_attributes=True)

    piece_id: int
    piece_nom: str
    type_travaux: TypeModificationPiece
    description: str
    budget_prevu: Decimal
    budget_reel: Decimal = Decimal("0")
    date_debut: date_type | None = None
    date_fin: date_type | None = None
    statut: str = "planifie"  # planifie, en_cours, termine, annule
    fournisseur: str | None = None
    factures: list[str] = Field(default_factory=list)  # URLs/refs factures
    notes: str | None = None


class ResumeTravauxMaison(BaseModel):
    """Résumé de tous les travaux maison."""

    budget_total_prevu: Decimal = Decimal("0")
    budget_total_depense: Decimal = Decimal("0")
    budget_restant: Decimal = Decimal("0")
    travaux_en_cours: int = 0
    travaux_planifies: int = 0
    travaux_termines: int = 0
    prochaine_echeance: date_type | None = None
    cout_par_piece: dict[str, Decimal] = Field(default_factory=dict)


class ObjetCreate(BaseModel):
    """Création d'un objet dans l'inventaire."""

    nom: str
    categorie: CategorieObjet = CategorieObjet.AUTRE
    conteneur_id: int | None = None
    quantite: int = 1
    marque: str | None = None
    modele: str | None = None
    date_achat: date_type | None = None
    prix_achat: Decimal | None = None
    date_garantie: date_type | None = None
    code_barre: str | None = None
    notes: str | None = None
    # Nouveaux champs statut/remplacement
    statut: StatutObjet = StatutObjet.FONCTIONNE
    priorite_remplacement: PrioriteRemplacement | None = None
    cout_remplacement_estime: Decimal | None = None
    url_produit_remplacement: str | None = None


class ObjetUpdate(BaseModel):
    """Mise à jour d'un objet (changement statut, etc.)."""

    nom: str | None = None
    statut: StatutObjet | None = None
    priorite_remplacement: PrioriteRemplacement | None = None
    cout_remplacement_estime: Decimal | None = None
    url_produit_remplacement: str | None = None
    notes: str | None = None


class DemandeChangementObjet(BaseModel):
    """Demande de changement/achat d'un objet.

    Créé quand on clique "À changer" ou "À acheter" sur un objet.
    Peut être lié au budget et à la liste de courses.
    """

    objet_id: int
    ancien_statut: StatutObjet
    nouveau_statut: StatutObjet
    raison: str | None = None
    priorite: PrioriteRemplacement = PrioriteRemplacement.NORMALE
    cout_estime: Decimal | None = None
    date_souhaitee: date_type | None = None
    ajouter_liste_courses: bool = False
    ajouter_budget: bool = False


class ObjetAvecStatut(BaseModel):
    """Objet avec son statut et liens vers modules."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nom: str
    categorie: CategorieObjet
    piece: str
    conteneur: str | None = None
    statut: StatutObjet
    priorite_remplacement: PrioriteRemplacement | None = None
    cout_remplacement_estime: Decimal | None = None
    url_produit_remplacement: str | None = None
    date_statut_change: datetime | None = None
    # Liens inter-modules
    lien_course_id: int | None = None  # Article liste courses
    lien_budget_id: int | None = None  # Dépense budget prévue


class ResultatRecherche(BaseModel):
    """Résultat de recherche 'où est...'"""

    objet_trouve: str
    emplacement: str  # "Cuisine > Placard haut > Étagère 2"
    piece: str
    conteneur: str | None = None
    quantite: int = 1
    confiance: float = 1.0  # 1.0 = exact, <1.0 = suggestion IA
    suggestions_similaires: list[str] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# INTEGRATION INTER-MODULES
# ═══════════════════════════════════════════════════════════


class ArticleCoursesGenere(BaseModel):
    """Article de courses généré automatiquement."""

    nom: str
    quantite: float = 1.0
    unite: str = "unité"
    categorie: str  # menage, bricolage, jardin
    prix_estime: Decimal | None = None
    source: str  # projet, jardin, stock_bas, objet_a_acheter, objet_a_changer
    source_id: int | None = None
    priorite: str = "normale"


class PipelineResult(BaseModel):
    """Résultat d'un pipeline automatique."""

    succes: bool
    pipeline: str  # nom du pipeline exécuté
    etapes_completees: list[str] = Field(default_factory=list)
    erreurs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


# Alias pour compatibilité
PipelineResultat = PipelineResult


# ═══════════════════════════════════════════════════════════
# INTÉGRATION OBJETS → BUDGET/COURSES
# ═══════════════════════════════════════════════════════════


class LienObjetBudget(BaseModel):
    """Lien entre un objet à acheter/changer et le budget."""

    model_config = ConfigDict(from_attributes=True)

    objet_id: int
    objet_nom: str
    depense_budget_id: int | None = None
    montant_prevu: Decimal
    categorie_budget: str = "maison"  # maison, travaux, equipement
    date_prevue: date_type | None = None
    statut: str = "prevu"  # prevu, achete, annule


class LienObjetCourses(BaseModel):
    """Lien entre un objet à acheter et la liste de courses."""

    model_config = ConfigDict(from_attributes=True)

    objet_id: int
    objet_nom: str
    article_courses_id: int | None = None
    magasin_suggere: str | None = None
    prix_estime: Decimal | None = None
    url_produit: str | None = None
    date_ajout: datetime = Field(default_factory=datetime.now)


class ActionObjetResult(BaseModel):
    """Résultat d'une action sur un objet (changer/acheter)."""

    succes: bool
    objet_id: int
    nouveau_statut: StatutObjet
    message: str
    lien_budget: LienObjetBudget | None = None
    lien_courses: LienObjetCourses | None = None
    erreurs: list[str] = Field(default_factory=list)
