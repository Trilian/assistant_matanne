"""
Modèles SQLAlchemy pour les utilitaires étendus.

Contient :
- NoteMemo : Notes et mémos rapides
- EntreeJournal : Journal de bord quotidien
- ContactUtile : Annuaire de contacts utiles
- LienFavori : Liens/bookmarks favoris
- MotDePasseMaison : Coffre-fort mots de passe WiFi/codes
- PressePapierEntree : Presse-papiers partagé
- ReleveEnergie : Suivi consommation énergie/eau
"""

from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, utc_now
from .mixins import TimestampMixin

# ═══════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════


class CategorieNote(StrEnum):
    """Catégories de notes."""

    GENERAL = "general"
    COURSES = "courses"
    CUISINE = "cuisine"
    FAMILLE = "famille"
    MAISON = "maison"
    TRAVAIL = "travail"
    SANTE = "sante"
    URGENT = "urgent"


class HumeurEnum(StrEnum):
    """Humeurs pour le journal de bord."""

    EXCELLENT = "excellent"
    BIEN = "bien"
    NEUTRE = "neutre"
    FATIGUE = "fatigue"
    STRESSE = "stresse"
    TRISTE = "triste"


class CategorieContact(StrEnum):
    """Catégories de contacts."""

    SANTE = "sante"
    EDUCATION = "education"
    URGENCE = "urgence"
    ARTISAN = "artisan"
    VOISIN = "voisin"
    ADMINISTRATIF = "administratif"
    FAMILLE = "famille"
    AUTRE = "autre"


class CategorieEnergie(StrEnum):
    """Types d'énergie/ressources."""

    ELECTRICITE = "electricite"
    GAZ = "gaz"
    EAU = "eau"


class CategorieMotDePasse(StrEnum):
    """Catégories de mots de passe."""

    WIFI = "wifi"
    ALARME = "alarme"
    DIGICODE = "digicode"
    PORTAIL = "portail"
    BOITE_LETTRES = "boite_lettres"
    AUTRE = "autre"


# ═══════════════════════════════════════════════════════════
# TABLE NOTES / MÉMOS
# ═══════════════════════════════════════════════════════════


class NoteMemo(TimestampMixin, Base):
    """Note ou mémo rapide.

    Table SQL: notes_memos

    Attributes:
        titre: Titre de la note
        contenu: Contenu texte de la note
        categorie: Catégorie (courses, cuisine, famille, etc.)
        couleur: Couleur de la note (hex)
        epingle: Note épinglée en haut
        est_checklist: Si la note est une checklist
        items_checklist: Liste d'items si checklist [{texte, fait}]
        tags: Tags libres
        rappel_date: Date de rappel optionnelle
    """

    __tablename__ = "notes_memos"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    titre: Mapped[str] = mapped_column(String(200), nullable=False)
    contenu: Mapped[str | None] = mapped_column(Text)
    categorie: Mapped[str] = mapped_column(
        String(50), nullable=False, default="general", index=True
    )
    couleur: Mapped[str | None] = mapped_column(String(7), default="#FFFFFF")
    epingle: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    est_checklist: Mapped[bool] = mapped_column(Boolean, default=False)
    items_checklist: Mapped[list | None] = mapped_column(JSONB, default=list)
    tags: Mapped[list | None] = mapped_column(JSONB, default=list)
    rappel_date: Mapped[datetime | None] = mapped_column(DateTime)
    archive: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    def __repr__(self) -> str:
        return f"<NoteMemo(id={self.id}, titre='{self.titre}', cat='{self.categorie}')>"


# ═══════════════════════════════════════════════════════════
# TABLE JOURNAL DE BORD
# ═══════════════════════════════════════════════════════════


class EntreeJournal(TimestampMixin, Base):
    """Entrée quotidienne du journal de bord.

    Table SQL: journal_bord

    Attributes:
        date_entree: Date de l'entrée
        contenu: Texte libre
        humeur: Humeur du jour (emoji)
        tags: Tags libres
        meteo: Données météo auto-capturées
        photos: URLs des photos attachées
        evenements_lies: IDs d'événements planning liés
    """

    __tablename__ = "journal_bord"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    date_entree: Mapped[date] = mapped_column(Date, nullable=False, index=True, unique=True)
    contenu: Mapped[str] = mapped_column(Text, nullable=False)
    humeur: Mapped[str | None] = mapped_column(String(20))
    gratitudes: Mapped[list | None] = mapped_column(JSONB, default=list)
    energie: Mapped[int | None] = mapped_column(Integer)
    tags: Mapped[list | None] = mapped_column(JSONB, default=list)
    meteo: Mapped[dict | None] = mapped_column(JSONB)
    photos: Mapped[list | None] = mapped_column(JSONB, default=list)
    evenements_lies: Mapped[list | None] = mapped_column(JSONB, default=list)

    def __repr__(self) -> str:
        return f"<EntreeJournal(id={self.id}, date={self.date_entree}, humeur={self.humeur})>"


# ═══════════════════════════════════════════════════════════
# TABLE CONTACTS UTILES
# ═══════════════════════════════════════════════════════════


class ContactUtile(TimestampMixin, Base):
    """Contact utile de l'annuaire familial.

    Table SQL: contacts_utiles

    Attributes:
        nom: Nom du contact
        categorie: Catégorie (santé, artisan, urgence, etc.)
        telephone: Numéro de téléphone
        email: Adresse email
        adresse: Adresse postale
        horaires: Horaires d'ouverture
        notes: Notes libres
        favori: Contact favori
    """

    __tablename__ = "contacts_utiles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    categorie: Mapped[str] = mapped_column(String(50), nullable=False, default="autre", index=True)
    specialite: Mapped[str | None] = mapped_column(String(200))
    telephone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(200))
    adresse: Mapped[str | None] = mapped_column(Text)
    horaires: Mapped[str | None] = mapped_column(String(200))
    notes: Mapped[str | None] = mapped_column(Text)
    favori: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    def __repr__(self) -> str:
        return f"<ContactUtile(id={self.id}, nom='{self.nom}', cat='{self.categorie}')>"


# ═══════════════════════════════════════════════════════════
# TABLE LIENS FAVORIS
# ═══════════════════════════════════════════════════════════


class LienFavori(TimestampMixin, Base):
    """Lien/bookmark favori.

    Table SQL: liens_favoris

    Attributes:
        titre: Titre du lien
        url: URL
        categorie: Catégorie libre
        description: Description
        tags: Tags libres
        favori: Lien favori (épinglé)
    """

    __tablename__ = "liens_favoris"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    titre: Mapped[str] = mapped_column(String(200), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    categorie: Mapped[str | None] = mapped_column(String(100), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    tags: Mapped[list | None] = mapped_column(JSONB, default=list)
    favori: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    def __repr__(self) -> str:
        return f"<LienFavori(id={self.id}, titre='{self.titre}')>"


# ═══════════════════════════════════════════════════════════
# TABLE MOTS DE PASSE / CODES MAISON
# ═══════════════════════════════════════════════════════════


class MotDePasseMaison(TimestampMixin, Base):
    """Mot de passe WiFi ou code d'accès maison (chiffré).

    Table SQL: mots_de_passe_maison

    Attributes:
        nom: Nom descriptif (ex: "WiFi Salon", "Digicode portail")
        categorie: Type (wifi, alarme, digicode, etc.)
        identifiant: SSID WiFi ou identifiant
        valeur_chiffree: Valeur chiffrée (Fernet)
        notes: Notes libres
    """

    __tablename__ = "mots_de_passe_maison"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    categorie: Mapped[str] = mapped_column(String(50), nullable=False, default="wifi", index=True)
    identifiant: Mapped[str | None] = mapped_column(String(200))
    valeur_chiffree: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<MotDePasseMaison(id={self.id}, nom='{self.nom}', cat='{self.categorie}')>"


# ═══════════════════════════════════════════════════════════
# TABLE PRESSE-PAPIERS PARTAGÉ
# ═══════════════════════════════════════════════════════════


class PressePapierEntree(TimestampMixin, Base):
    """Entrée du presse-papiers partagé familial.

    Table SQL: presse_papiers

    Attributes:
        contenu: Texte partagé
        auteur: Qui a partagé
        expire_le: Date d'expiration optionnelle
    """

    __tablename__ = "presse_papiers"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    contenu: Mapped[str] = mapped_column(Text, nullable=False)
    auteur: Mapped[str | None] = mapped_column(String(100))
    expire_le: Mapped[datetime | None] = mapped_column(DateTime)
    epingle: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"<PressePapierEntree(id={self.id}, auteur='{self.auteur}')>"


# ═══════════════════════════════════════════════════════════
# TABLE RELEVÉS ÉNERGIE
# ═══════════════════════════════════════════════════════════


class ReleveEnergie(TimestampMixin, Base):
    """Relevé de consommation énergie/eau.

    Table SQL: releves_energie

    Attributes:
        type_energie: Type (electricite, gaz, eau)
        mois: Mois du relevé (1-12)
        annee: Année
        valeur_compteur: Valeur du compteur
        consommation: Consommation calculée
        unite: Unité (kWh, m³, L)
        montant: Montant facturé
        notes: Notes
    """

    __tablename__ = "releves_energie"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    type_energie: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    mois: Mapped[int] = mapped_column(Integer, nullable=False)
    annee: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    valeur_compteur: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    consommation: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    unite: Mapped[str] = mapped_column(String(10), nullable=False, default="kWh")
    montant: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    notes: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        CheckConstraint("mois >= 1 AND mois <= 12", name="ck_releve_mois_valide"),
        CheckConstraint(
            "consommation IS NULL OR consommation >= 0",
            name="ck_releve_consommation_positive",
        ),
        CheckConstraint(
            "montant IS NULL OR montant >= 0",
            name="ck_releve_montant_positif",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<ReleveEnergie(id={self.id}, type='{self.type_energie}', {self.mois}/{self.annee})>"
        )
