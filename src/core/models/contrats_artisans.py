"""
Modèles SQLAlchemy pour contrats, artisans et garanties.

Contient :
- Contrat : Suivi contrats (assurance, énergie, box, etc.)
- Artisan : Carnet d'adresses artisans
- InterventionArtisan : Historique interventions
- Garantie : Suivi garanties appareils/équipements
- IncidentSAV : Historique pannes et réparations
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


class TypeContrat(StrEnum):
    """Type de contrat maison."""

    ASSURANCE_HABITATION = "assurance_habitation"
    ASSURANCE_AUTO = "assurance_auto"
    ELECTRICITE = "electricite"
    GAZ = "gaz"
    EAU = "eau"
    BOX_INTERNET = "box_internet"
    TELEPHONE = "telephone"
    ALARME = "alarme"
    ENTRETIEN_CHAUDIERE = "entretien_chaudiere"
    RAMONAGE = "ramonage"
    JARDIN = "jardin"
    DOMOTIQUE = "domotique"
    CRECHE = "creche"
    MUTUELLE = "mutuelle"
    PREVOYANCE = "prevoyance"
    AUTRE = "autre"


class StatutContrat(StrEnum):
    """Statut d'un contrat."""

    ACTIF = "actif"
    EN_COURS_RESILIATION = "en_cours_resiliation"
    RESILIE = "resilie"
    EXPIRE = "expire"
    EN_ATTENTE = "en_attente"


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


class StatutGarantie(StrEnum):
    """Statut d'une garantie."""

    ACTIVE = "active"
    EXPIREE = "expiree"
    PROLONGEE = "prolongee"


class StatutIncident(StrEnum):
    """Statut d'un incident SAV."""

    OUVERT = "ouvert"
    EN_COURS = "en_cours"
    RESOLU = "resolu"
    CLOS = "clos"


# ═══════════════════════════════════════════════════════════
# CONTRATS
# ═══════════════════════════════════════════════════════════


class Contrat(TimestampMixin, Base):
    """Contrat maison (assurance, énergie, box internet, etc.).

    Suivi des dates, montants, conditions de résiliation et alertes.
    """

    __tablename__ = "contrats_maison"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Identification
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    type_contrat: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    fournisseur: Mapped[str] = mapped_column(String(200), nullable=False)
    numero_contrat: Mapped[str | None] = mapped_column(String(100))
    numero_client: Mapped[str | None] = mapped_column(String(100))

    # Dates
    date_debut: Mapped[date] = mapped_column(Date, nullable=False)
    date_fin: Mapped[date | None] = mapped_column(Date)
    date_renouvellement: Mapped[date | None] = mapped_column(Date, index=True)
    duree_engagement_mois: Mapped[int | None] = mapped_column(Integer)

    # Résiliation
    tacite_reconduction: Mapped[bool] = mapped_column(Boolean, default=True)
    preavis_resiliation_jours: Mapped[int | None] = mapped_column(Integer)  # Jours de préavis
    date_limite_resiliation: Mapped[date | None] = mapped_column(Date)

    # Financier
    montant_mensuel: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    montant_annuel: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))

    # Contact
    telephone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(200))
    espace_client_url: Mapped[str | None] = mapped_column(String(500))

    # Statut
    statut: Mapped[str] = mapped_column(String(30), default="actif", index=True)

    # Alertes
    alerte_jours_avant: Mapped[int] = mapped_column(Integer, default=30)
    alerte_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Notes et documents
    notes: Mapped[str | None] = mapped_column(Text)
    document_path: Mapped[str | None] = mapped_column(String(500))  # Chemin PDF scanné

    def __repr__(self) -> str:
        return f"<Contrat(id={self.id}, nom='{self.nom}', type='{self.type_contrat}')>"


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


# ═══════════════════════════════════════════════════════════
# GARANTIES & SAV
# ═══════════════════════════════════════════════════════════


class Garantie(TimestampMixin, Base):
    """Garantie d'un appareil ou équipement.

    Suivi dates, alertes expiration, historique pannes.
    """

    __tablename__ = "garanties"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Appareil
    nom_appareil: Mapped[str] = mapped_column(String(200), nullable=False)
    marque: Mapped[str | None] = mapped_column(String(100))
    modele: Mapped[str | None] = mapped_column(String(100))
    numero_serie: Mapped[str | None] = mapped_column(String(100))
    piece: Mapped[str | None] = mapped_column(String(50), index=True)  # Pièce de la maison

    # Achat
    date_achat: Mapped[date] = mapped_column(Date, nullable=False)
    lieu_achat: Mapped[str | None] = mapped_column(String(200))
    prix_achat: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    preuve_achat_path: Mapped[str | None] = mapped_column(String(500))

    # Garantie
    duree_garantie_mois: Mapped[int] = mapped_column(Integer, default=24)
    date_fin_garantie: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    garantie_etendue: Mapped[bool] = mapped_column(Boolean, default=False)
    date_fin_garantie_etendue: Mapped[date | None] = mapped_column(Date)

    # Statut
    statut: Mapped[str] = mapped_column(String(20), default="active", index=True)

    # Alertes
    alerte_jours_avant: Mapped[int] = mapped_column(Integer, default=30)
    alerte_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Coût remplacement estimé
    cout_remplacement: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))

    # Notes
    notes: Mapped[str | None] = mapped_column(Text)

    # Relations
    incidents: Mapped[list["IncidentSAV"]] = relationship(
        back_populates="garantie", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Garantie(id={self.id}, appareil='{self.nom_appareil}')>"


class IncidentSAV(TimestampMixin, Base):
    """Incident / panne / réparation d'un appareil sous garantie."""

    __tablename__ = "incidents_sav"

    id: Mapped[int] = mapped_column(primary_key=True)
    garantie_id: Mapped[int] = mapped_column(ForeignKey("garanties.id"), nullable=False, index=True)

    # Détails
    date_incident: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    sous_garantie: Mapped[bool] = mapped_column(Boolean, default=True)

    # Réparation
    date_resolution: Mapped[date | None] = mapped_column(Date)
    reparateur: Mapped[str | None] = mapped_column(String(200))  # Nom artisan ou SAV
    artisan_id: Mapped[int | None] = mapped_column(ForeignKey("artisans.id"))
    cout_reparation: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    pris_en_charge: Mapped[bool] = mapped_column(Boolean, default=False)

    # Statut
    statut: Mapped[str] = mapped_column(String(20), default="ouvert", index=True)

    # Notes
    notes: Mapped[str | None] = mapped_column(Text)

    # Relation
    garantie: Mapped["Garantie"] = relationship(back_populates="incidents")

    def __repr__(self) -> str:
        return f"<IncidentSAV(id={self.id}, garantie_id={self.garantie_id})>"
