"""
Modèles pour les voyages familiaux.

Contient :
- Voyage : Voyage planifié ou effectué
- ChecklistVoyage : Checklist de bagages/préparation liée à un voyage
- TemplateChecklist : Templates réutilisables de checklists
"""

from datetime import date

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import TimestampMixin

# ═══════════════════════════════════════════════════════════
# VOYAGE
# ═══════════════════════════════════════════════════════════


class Voyage(TimestampMixin, Base):
    """Voyage familial planifié ou effectué.

    Attributes:
        titre: Titre du voyage
        destination: Destination principale
        date_depart: Date de départ
        date_retour: Date de retour
        type_voyage: Type (weekend, vacances, city_trip, camping, famille)
        budget_prevu: Budget prévu en euros
        budget_reel: Budget réellement dépensé
        statut: Statut (planifié, en_cours, terminé, annulé)
        notes: Notes et commentaires
        reservations: Détails des réservations (JSONB)
        participants: Liste des participants
    """

    __tablename__ = "voyages"

    id: Mapped[int] = mapped_column(primary_key=True)
    titre: Mapped[str] = mapped_column(String(200), nullable=False)
    destination: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    date_depart: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    date_retour: Mapped[date] = mapped_column(Date, nullable=False)
    type_voyage: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # weekend, vacances, city_trip, camping, famille
    budget_prevu: Mapped[float | None] = mapped_column(Float)
    budget_reel: Mapped[float | None] = mapped_column(Float)
    statut: Mapped[str] = mapped_column(String(50), nullable=False, default="planifié", index=True)
    notes: Mapped[str | None] = mapped_column(Text)
    reservations: Mapped[dict | None] = mapped_column(JSONB)  # {hotel: {}, vol: {}, location: {}}
    participants: Mapped[list[str] | None] = mapped_column(JSONB)

    # Relations
    checklists: Mapped[list["ChecklistVoyage"]] = relationship(
        back_populates="voyage", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("date_retour >= date_depart", name="ck_voyage_dates"),
        CheckConstraint(
            "budget_prevu >= 0 OR budget_prevu IS NULL", name="ck_voyage_budget_positif"
        ),
    )

    @property
    def duree_jours(self) -> int:
        """Calcule la durée du voyage en jours."""
        return (self.date_retour - self.date_depart).days + 1

    def __repr__(self) -> str:
        return (
            f"<Voyage(id={self.id}, titre='{self.titre}', "
            f"destination='{self.destination}', statut='{self.statut}')>"
        )


# ═══════════════════════════════════════════════════════════
# CHECKLIST VOYAGE
# ═══════════════════════════════════════════════════════════


class ChecklistVoyage(TimestampMixin, Base):
    """Checklist de préparation liée à un voyage.

    Les articles sont stockés en JSONB:
    [{"nom": "Couches", "categorie": "bébé", "coche": false, "quantite": 20}]

    Attributes:
        voyage_id: ID du voyage (FK)
        template_id: ID du template source (nullable)
        nom: Nom de la checklist
        membre: Pour qui (jules, anne, mathieu, commun)
        articles: Liste des articles (JSONB)
        commentaire: Commentaire libre
    """

    __tablename__ = "checklists_voyage"

    id: Mapped[int] = mapped_column(primary_key=True)
    voyage_id: Mapped[int] = mapped_column(
        ForeignKey("voyages.id", ondelete="CASCADE"), nullable=False, index=True
    )
    template_id: Mapped[int | None] = mapped_column(
        ForeignKey("templates_checklist.id", ondelete="SET NULL"), index=True
    )
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    membre: Mapped[str] = mapped_column(
        String(50), nullable=False, default="commun"
    )  # jules, anne, mathieu, commun
    articles: Mapped[list[dict] | None] = mapped_column(
        JSONB, default=list
    )  # [{nom, categorie, coche, quantite}]
    commentaire: Mapped[str | None] = mapped_column(Text)

    # Relations
    voyage: Mapped["Voyage"] = relationship(back_populates="checklists")
    template: Mapped["TemplateChecklist | None"] = relationship()

    @property
    def nombre_articles(self) -> int:
        """Nombre total d'articles."""
        return len(self.articles) if self.articles else 0

    @property
    def nombre_coches(self) -> int:
        """Nombre d'articles cochés."""
        if not self.articles:
            return 0
        return sum(1 for a in self.articles if a.get("coche", False))

    @property
    def pourcentage_preparation(self) -> float:
        """Pourcentage de préparation (0-100)."""
        if not self.articles:
            return 100.0
        return round(self.nombre_coches / len(self.articles) * 100, 1)

    def __repr__(self) -> str:
        return (
            f"<ChecklistVoyage(id={self.id}, nom='{self.nom}', "
            f"membre='{self.membre}', articles={self.nombre_articles})>"
        )


# ═══════════════════════════════════════════════════════════
# TEMPLATES CHECKLIST
# ═══════════════════════════════════════════════════════════


class TemplateChecklist(TimestampMixin, Base):
    """Template réutilisable de checklist de voyage.

    Articles stockés en JSONB:
    [{"nom": "Doudou", "categorie": "essentiel", "quantite": 1}]

    Attributes:
        nom: Nom du template
        type_voyage: Type de voyage associé
        membre: Pour qui (jules, anne, mathieu, commun)
        articles: Articles par défaut (JSONB)
        est_defaut: Si c'est un template système
        description: Description du template
    """

    __tablename__ = "templates_checklist"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    type_voyage: Mapped[str | None] = mapped_column(String(50), index=True)
    membre: Mapped[str] = mapped_column(String(50), nullable=False, default="commun")
    articles: Mapped[list[dict] | None] = mapped_column(
        JSONB, default=list
    )  # [{nom, categorie, quantite}]
    est_defaut: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str | None] = mapped_column(Text)

    def __repr__(self) -> str:
        return (
            f"<TemplateChecklist(id={self.id}, nom='{self.nom}', "
            f"type='{self.type_voyage}', defaut={self.est_defaut})>"
        )
