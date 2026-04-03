"""
Modèles SQLAlchemy pour abonnements et artisans.

Contient :
- Abonnement : Abonnements maison (eau, électricité, gaz, assurances, etc.)
- Artisan : Carnet d'adresses artisans
- InterventionArtisan : Historique interventions
"""

from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import TimestampMixin

# ═══════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════


class MetierArtisan(StrEnum):
    """Métier d'artisan."""

    PLOMBIER = "plombier"
    ELECTRICIEN = "electricien"
    CHAUFFAGISTE = "chauffagiste"
    PEINTRE = "peintre"
    MENUISIER = "menuisier"
    CARRELEUR = "carreleur"
    MACON = "macon"
    COUVREUR = "couvreur"
    JARDINIER = "jardinier"
    SERRURIER = "serrurier"
    VITRIER = "vitrier"
    RAMONEUR = "ramoneur"
    CLIMATICIEN = "climaticien"
    DOMOTICIEN = "domoticien"
    TERRASSIER = "terrassier"
    PISCINISTE = "pisciniste"
    AUTRE = "autre"


class TypeAbonnement(StrEnum):
    """Type d'abonnement maison."""

    EAU = "eau"
    ELECTRICITE = "electricite"
    GAZ = "gaz"
    ASSURANCE_HABITATION = "assurance_habitation"
    ASSURANCE_AUTO = "assurance_auto"
    CHAUDIERE = "chaudiere"
    TELEPHONE = "telephone"
    INTERNET = "internet"


# ═══════════════════════════════════════════════════════════
# ABONNEMENTS
# ═══════════════════════════════════════════════════════════


class Abonnement(TimestampMixin, Base):
    """Abonnement maison (eau, électricité, gaz, assurances, téléphone, internet).

    Permet de comparer les abonnements et de trouver de meilleures offres.
    """

    __tablename__ = "abonnements"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Type et fournisseur
    type_abonnement: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    fournisseur: Mapped[str] = mapped_column(String(200), nullable=False)
    numero_contrat: Mapped[str | None] = mapped_column(String(100))

    # Coûts
    prix_mensuel: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))

    # Dates
    date_debut: Mapped[date | None] = mapped_column(Date)
    date_fin_engagement: Mapped[date | None] = mapped_column(Date)

    # Comparateur
    meilleur_prix_trouve: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    fournisseur_alternatif: Mapped[str | None] = mapped_column(String(200))

    # Notes
    notes: Mapped[str | None] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<Abonnement(id={self.id}, type='{self.type_abonnement}', fournisseur='{self.fournisseur}')>"


# ═══════════════════════════════════════════════════════════
# ARTISANS
# ═══════════════════════════════════════════════════════════


class Artisan(TimestampMixin, Base):
    """Artisan dans le carnet d'adresses.

    Plombier, électricien, etc. avec historique d'interventions.
    """

    __tablename__ = "artisans"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Identification
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    entreprise: Mapped[str | None] = mapped_column(String(200))
    metier: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    specialite: Mapped[str | None] = mapped_column(String(200))

    # Contact
    telephone: Mapped[str | None] = mapped_column(String(20))
    telephone2: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(200))
    adresse: Mapped[str | None] = mapped_column(Text)
    zone_intervention: Mapped[str | None] = mapped_column(String(200))

    # Évaluation
    note: Mapped[int | None] = mapped_column(Integer)  # 1-5
    recommande: Mapped[bool] = mapped_column(Boolean, default=True)

    # Infos pratiques
    site_web: Mapped[str | None] = mapped_column(String(500))
    siret: Mapped[str | None] = mapped_column(String(20))
    assurance_decennale: Mapped[bool] = mapped_column(Boolean, default=False)
    qualifications: Mapped[str | None] = mapped_column(Text)  # RGE, Qualibat, etc.

    # Notes
    notes: Mapped[str | None] = mapped_column(Text)

    # Relations
    interventions: Mapped[list["InterventionArtisan"]] = relationship(
        back_populates="artisan", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Artisan(id={self.id}, nom='{self.nom}', metier='{self.metier}')>"


class InterventionArtisan(TimestampMixin, Base):
    """Intervention d'un artisan (historique)."""

    __tablename__ = "interventions_artisans"

    id: Mapped[int] = mapped_column(primary_key=True)
    artisan_id: Mapped[int] = mapped_column(ForeignKey("artisans.id"), nullable=False, index=True)

    # Détails
    date_intervention: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    piece: Mapped[str | None] = mapped_column(String(50))  # Pièce concernée

    # Coûts
    montant_devis: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    montant_facture: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    paye: Mapped[bool] = mapped_column(Boolean, default=False)

    # Satisfaction
    satisfaction: Mapped[int | None] = mapped_column(Integer)  # 1-5
    commentaire: Mapped[str | None] = mapped_column(Text)

    # Document
    facture_path: Mapped[str | None] = mapped_column(String(500))

    # Relation
    artisan: Mapped["Artisan"] = relationship(back_populates="interventions")

    def __repr__(self) -> str:
        return f"<InterventionArtisan(id={self.id}, artisan_id={self.artisan_id})>"
