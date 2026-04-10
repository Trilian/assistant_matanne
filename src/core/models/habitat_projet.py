"""Modèles SQLAlchemy pour le module Habitat (vision projet)."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins import CreeLeMixin, TimestampMixin


class ScenarioHabitat(TimestampMixin, Base):
    """Scénario de décision Habitat (déménager, agrandir, rester)."""

    __tablename__ = "habitat_scenarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    budget_estime: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    surface_finale_m2: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    nb_chambres: Mapped[int | None] = mapped_column(Integer)
    score_global: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), index=True)
    avantages: Mapped[list[str] | None] = mapped_column(JSONB, default=list)
    inconvenients: Mapped[list[str] | None] = mapped_column(JSONB, default=list)
    notes: Mapped[str | None] = mapped_column(Text)
    statut: Mapped[str] = mapped_column(String(50), default="brouillon", index=True)


class CritereScenarioHabitat(CreeLeMixin, Base):
    """Critère pondéré lié à un scénario Habitat."""

    __tablename__ = "habitat_criteres"

    id: Mapped[int] = mapped_column(primary_key=True)
    scenario_id: Mapped[int] = mapped_column(
        ForeignKey("habitat_scenarios.id", ondelete="CASCADE"), index=True, nullable=False
    )
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    poids: Mapped[Decimal] = mapped_column(Numeric(4, 2), default=1)
    note: Mapped[Decimal | None] = mapped_column(Numeric(3, 1))
    commentaire: Mapped[str | None] = mapped_column(Text)


class CritereImmoHabitat(TimestampMixin, Base):
    """Critères de veille immobilière."""

    __tablename__ = "habitat_criteres_immo"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), default="Recherche principale")
    departements: Mapped[list[str] | None] = mapped_column(JSONB, default=list)
    villes: Mapped[list[str] | None] = mapped_column(JSONB, default=list)
    rayon_km: Mapped[int] = mapped_column(Integer, default=10)
    budget_min: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    budget_max: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    surface_min_m2: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    surface_terrain_min_m2: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    nb_pieces_min: Mapped[int | None] = mapped_column(Integer)
    nb_chambres_min: Mapped[int | None] = mapped_column(Integer)
    type_bien: Mapped[str | None] = mapped_column(String(50))
    criteres_supplementaires: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    seuil_alerte: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.70"))
    actif: Mapped[bool] = mapped_column(Boolean, default=True, index=True)


class AnnonceHabitat(TimestampMixin, Base):
    """Annonce immobilière agrégée depuis une source externe."""

    __tablename__ = "habitat_annonces"

    id: Mapped[int] = mapped_column(primary_key=True)
    critere_id: Mapped[int | None] = mapped_column(
        ForeignKey("habitat_criteres_immo.id", ondelete="SET NULL"), index=True
    )
    source: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    url_source: Mapped[str] = mapped_column(String(500), nullable=False)
    titre: Mapped[str | None] = mapped_column(String(500))
    prix: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), index=True)
    surface_m2: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    surface_terrain_m2: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    nb_pieces: Mapped[int | None] = mapped_column(Integer)
    ville: Mapped[str | None] = mapped_column(String(200), index=True)
    code_postal: Mapped[str | None] = mapped_column(String(10), index=True)
    departement: Mapped[str | None] = mapped_column(String(3), index=True)
    photos: Mapped[list[str] | None] = mapped_column(JSONB, default=list)
    description_brute: Mapped[str | None] = mapped_column(Text)
    score_pertinence: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), index=True)
    statut: Mapped[str] = mapped_column(String(50), default="nouveau", index=True)
    prix_m2_secteur: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    ecart_prix_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    hash_dedup: Mapped[str | None] = mapped_column(String(64), index=True)
    notes: Mapped[str | None] = mapped_column(Text)


class PlanHabitat(TimestampMixin, Base):
    """Plan importé pour un scénario Habitat."""

    __tablename__ = "habitat_plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    scenario_id: Mapped[int | None] = mapped_column(
        ForeignKey("habitat_scenarios.id", ondelete="SET NULL"), index=True
    )
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    type_plan: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    image_importee_url: Mapped[str | None] = mapped_column(String(500))
    donnees_pieces: Mapped[dict] = mapped_column(JSONB, default=dict)
    contraintes: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    surface_totale_m2: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    budget_estime: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    notes: Mapped[str | None] = mapped_column(Text)
    version: Mapped[int] = mapped_column(Integer, default=1)


class PieceHabitat(TimestampMixin, Base):
    """Pièce d'un plan Habitat."""

    __tablename__ = "habitat_pieces"

    id: Mapped[int] = mapped_column(primary_key=True)
    plan_id: Mapped[int] = mapped_column(
        ForeignKey("habitat_plans.id", ondelete="CASCADE"), index=True, nullable=False
    )
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    type_piece: Mapped[str | None] = mapped_column(String(50), index=True)
    surface_m2: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    position_x: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    position_y: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    largeur: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    longueur: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    hauteur_plafond: Mapped[Decimal | None] = mapped_column(Numeric(4, 2))
    couleur_mur: Mapped[str | None] = mapped_column(String(7))
    sol_type: Mapped[str | None] = mapped_column(String(50))
    meubles: Mapped[list | None] = mapped_column(JSONB, default=list)
    notes: Mapped[str | None] = mapped_column(Text)


class ModificationPlanHabitat(CreeLeMixin, Base):
    """Historique des demandes de modifications IA sur un plan."""

    __tablename__ = "habitat_modifications_plan"

    id: Mapped[int] = mapped_column(primary_key=True)
    plan_id: Mapped[int] = mapped_column(
        ForeignKey("habitat_plans.id", ondelete="CASCADE"), index=True, nullable=False
    )
    prompt_utilisateur: Mapped[str] = mapped_column(Text, nullable=False)
    analyse_ia: Mapped[dict] = mapped_column(JSONB, default=dict)
    image_generee_url: Mapped[str | None] = mapped_column(String(500))
    acceptee: Mapped[bool | None] = mapped_column(Boolean)


class ProjetDecoHabitat(TimestampMixin, Base):
    """Projet déco par pièce dans le module Habitat."""

    __tablename__ = "habitat_projets_deco"

    id: Mapped[int] = mapped_column(primary_key=True)
    piece_id: Mapped[int | None] = mapped_column(
        ForeignKey("habitat_pieces.id", ondelete="SET NULL"), index=True
    )
    nom_piece: Mapped[str] = mapped_column(String(200), nullable=False)
    style: Mapped[str | None] = mapped_column(String(100))
    palette_couleurs: Mapped[list | None] = mapped_column(JSONB, default=list)
    inspirations: Mapped[list | None] = mapped_column(JSONB, default=list)
    budget_prevu: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    budget_depense: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), default=0)
    statut: Mapped[str] = mapped_column(String(50), default="idee", index=True)
    notes: Mapped[str | None] = mapped_column(Text)


class ZoneJardinHabitat(TimestampMixin, Base):
    """Zone fonctionnelle du plan paysager Habitat."""

    __tablename__ = "habitat_zones_jardin"

    id: Mapped[int] = mapped_column(primary_key=True)
    plan_id: Mapped[int] = mapped_column(
        ForeignKey("habitat_plans.id", ondelete="CASCADE"), index=True, nullable=False
    )
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    type_zone: Mapped[str | None] = mapped_column(String(100), index=True)
    surface_m2: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    altitude_relative: Mapped[Decimal | None] = mapped_column(Numeric(4, 2))
    position_x: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    position_y: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    largeur: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    longueur: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    donnees_canvas: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    plantes: Mapped[list | None] = mapped_column(JSONB, default=list)
    amenagements: Mapped[list | None] = mapped_column(JSONB, default=list)
    budget_estime: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    notes: Mapped[str | None] = mapped_column(Text)
