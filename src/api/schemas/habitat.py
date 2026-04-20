"""Schémas Pydantic pour le module Habitat."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field


class ScenarioHabitatCreate(BaseModel):
    nom: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    budget_estime: Decimal | None = Field(None, ge=0)
    surface_finale_m2: Decimal | None = Field(None, ge=0)
    nb_chambres: int | None = Field(None, ge=0, le=20)
    avantages: list[str] = Field(default_factory=list)
    inconvenients: list[str] = Field(default_factory=list)
    notes: str | None = None
    statut: str = Field(default="brouillon", max_length=50)


class ScenarioHabitatPatch(BaseModel):
    nom: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    budget_estime: Decimal | None = Field(None, ge=0)
    surface_finale_m2: Decimal | None = Field(None, ge=0)
    nb_chambres: int | None = Field(None, ge=0, le=20)
    avantages: list[str] | None = None
    inconvenients: list[str] | None = None
    notes: str | None = None
    statut: str | None = Field(None, max_length=50)


class CritereScenarioCreate(BaseModel):
    nom: str = Field(..., min_length=1, max_length=200)
    poids: Decimal = Field(default=Decimal("1.00"), ge=0, le=10)
    note: Decimal | None = Field(None, ge=0, le=10)
    commentaire: str | None = None


class CritereImmoCreate(BaseModel):
    nom: str = Field(default="Recherche principale", max_length=200)
    departements: list[str] = Field(default_factory=list)
    villes: list[str] = Field(default_factory=list)
    rayon_km: int = Field(default=10, ge=1, le=100)
    budget_min: Decimal | None = Field(None, ge=0)
    budget_max: Decimal | None = Field(None, ge=0)
    surface_min_m2: Decimal | None = Field(None, ge=0)
    surface_terrain_min_m2: Decimal | None = Field(None, ge=0)
    nb_pieces_min: int | None = Field(None, ge=1)
    nb_chambres_min: int | None = Field(None, ge=1)
    type_bien: str | None = Field(None, max_length=50)
    criteres_supplementaires: dict = Field(default_factory=dict)
    seuil_alerte: Decimal = Field(default=Decimal("0.70"), ge=0, le=1)
    actif: bool = True


class AnnonceHabitatCreate(BaseModel):
    critere_id: int | None = None
    source: str = Field(..., min_length=2, max_length=100)
    url_source: str = Field(..., min_length=8, max_length=500)
    titre: str | None = Field(None, max_length=500)
    prix: Decimal | None = Field(None, ge=0)
    surface_m2: Decimal | None = Field(None, ge=0)
    surface_terrain_m2: Decimal | None = Field(None, ge=0)
    nb_pieces: int | None = Field(None, ge=0)
    ville: str | None = Field(None, max_length=200)
    code_postal: str | None = Field(None, max_length=10)
    departement: str | None = Field(None, max_length=3)
    photos: list[str] = Field(default_factory=list)
    description_brute: str | None = None
    score_pertinence: Decimal | None = Field(None, ge=0, le=1)
    statut: str = Field(default="nouveau", max_length=50)
    prix_m2_secteur: Decimal | None = Field(None, ge=0)
    ecart_prix_pct: Decimal | None = None
    hash_dedup: str | None = Field(None, max_length=64)
    notes: str | None = None


class PlanHabitatCreate(BaseModel):
    scenario_id: int | None = None
    nom: str = Field(..., min_length=1, max_length=200)
    type_plan: str = Field(..., min_length=3, max_length=50)
    image_importee_url: str | None = Field(None, max_length=500)
    donnees_pieces: dict = Field(default_factory=dict)
    contraintes: dict = Field(default_factory=dict)
    surface_totale_m2: Decimal | None = Field(None, ge=0)
    budget_estime: Decimal | None = Field(None, ge=0)
    notes: str | None = None


class PlanHabitatAnalyseCreate(BaseModel):
    prompt_utilisateur: str | None = Field(None, max_length=2000)
    generer_image: bool = False


class PlanHabitatPiece3DConfig(BaseModel):
    id: int = Field(..., ge=1)
    x: float
    z: float
    width: float = Field(..., ge=1.8, le=12)
    depth: float = Field(..., ge=1.8, le=12)
    nom: str | None = Field(None, min_length=1, max_length=200)
    type_piece: str | None = Field(None, max_length=50)


class PlanHabitatConfiguration3D(BaseModel):
    layout_edition: list[PlanHabitatPiece3DConfig] = Field(default_factory=list)
    palette_par_type: dict[str, str] = Field(default_factory=dict)


class PlanHabitatVariante3D(BaseModel):
    id: str | None = Field(None, min_length=1, max_length=120)
    nom: str = Field(..., min_length=1, max_length=120)
    source: str = Field(default="manuel", max_length=50)
    configuration: PlanHabitatConfiguration3D


class PlanHabitatConfiguration3DUpdate(BaseModel):
    configuration_courante: PlanHabitatConfiguration3D = Field(default_factory=PlanHabitatConfiguration3D)
    variantes: list[PlanHabitatVariante3D] = Field(default_factory=list)
    variante_active_id: str | None = Field(None, min_length=1, max_length=120)


class PieceHabitatCreate(BaseModel):
    nom: str = Field(..., min_length=1, max_length=200)
    type_piece: str | None = Field(None, max_length=50)
    surface_m2: Decimal | None = Field(None, ge=0)
    position_x: Decimal | None = None
    position_y: Decimal | None = None
    largeur: Decimal | None = Field(None, ge=0)
    longueur: Decimal | None = Field(None, ge=0)
    hauteur_plafond: Decimal | None = Field(None, ge=0)
    couleur_mur: str | None = Field(None, max_length=7)
    sol_type: str | None = Field(None, max_length=50)
    meubles: list = Field(default_factory=list)
    notes: str | None = None


class ProjetDecoHabitatCreate(BaseModel):
    piece_id: int | None = None
    nom_piece: str = Field(..., min_length=1, max_length=200)
    style: str | None = Field(None, max_length=100)
    palette_couleurs: list = Field(default_factory=list)
    inspirations: list = Field(default_factory=list)
    budget_prevu: Decimal | None = Field(None, ge=0)
    notes: str | None = None


class ProjetDecoSuggestionCreate(BaseModel):
    brief: str | None = Field(None, max_length=2000)
    generer_image: bool = False


class ProjetDecoDepenseCreate(BaseModel):
    montant: Decimal = Field(..., gt=0)
    fournisseur: str | None = Field(None, max_length=200)
    note: str | None = None
    categorie_depense: str = Field(default="travaux", max_length=50)


class ZoneJardinHabitatCreate(BaseModel):
    plan_id: int
    nom: str = Field(..., min_length=1, max_length=200)
    type_zone: str | None = Field(None, max_length=100)
    surface_m2: Decimal | None = Field(None, ge=0)
    altitude_relative: Decimal | None = None
    position_x: Decimal | None = None
    position_y: Decimal | None = None
    largeur: Decimal | None = Field(None, ge=0)
    longueur: Decimal | None = Field(None, ge=0)
    donnees_canvas: dict = Field(default_factory=dict)
    plantes: list = Field(default_factory=list)
    amenagements: list = Field(default_factory=list)
    budget_estime: Decimal | None = Field(None, ge=0)
    notes: str | None = None


class ZoneJardinHabitatPatch(BaseModel):
    nom: str | None = Field(None, min_length=1, max_length=200)
    type_zone: str | None = Field(None, max_length=100)
    surface_m2: Decimal | None = Field(None, ge=0)
    altitude_relative: Decimal | None = None
    position_x: Decimal | None = None
    position_y: Decimal | None = None
    largeur: Decimal | None = Field(None, ge=0)
    longueur: Decimal | None = Field(None, ge=0)
    donnees_canvas: dict | None = None
    plantes: list | None = None
    amenagements: list | None = None
    budget_estime: Decimal | None = Field(None, ge=0)
    notes: str | None = None


class SynchronisationVeilleHabitatCreate(BaseModel):
    critere_id: int | None = None
    limite_par_source: int = Field(default=12, ge=1, le=50)
    sources: list[str] | None = None
    envoyer_alertes: bool = True


class GenerationImageHabitatCreate(BaseModel):
    prompt: str = Field(..., min_length=10, max_length=2000)
    negative_prompt: str | None = Field(None, max_length=1000)
