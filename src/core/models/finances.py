"""
Modèles SQLAlchemy pour les finances et le budget.

Contient :
- Depense : Suivi des dépenses familiales
- BudgetMensuelDB : Budget mensuel par catégorie
- HouseExpense : Dépenses récurrentes maison (gaz, eau, électricité)
"""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

# ═══════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════


class CategorieDepenseDB(str, Enum):
    """Catégories de dépenses (aligné avec contrainte SQL)."""

    ALIMENTATION = "alimentation"
    TRANSPORT = "transport"
    LOGEMENT = "logement"
    SANTE = "sante"
    LOISIRS = "loisirs"
    VETEMENTS = "vetements"
    EDUCATION = "education"
    CADEAUX = "cadeaux"
    ABONNEMENTS = "abonnements"
    RESTAURANT = "restaurant"
    VACANCES = "vacances"
    BEBE = "bebe"
    AUTRE = "autre"


class RecurrenceType(str, Enum):
    """Types de récurrence."""

    PONCTUEL = "ponctuel"
    HEBDOMADAIRE = "hebdomadaire"
    MENSUEL = "mensuel"
    TRIMESTRIEL = "trimestriel"
    ANNUEL = "annuel"


class ExpenseCategory(str, Enum):
    """Catégorie de dépense maison."""

    GAZ = "gaz"
    ELECTRICITE = "electricite"
    EAU = "eau"
    INTERNET = "internet"
    LOYER = "loyer"
    ASSURANCE = "assurance"
    TAXE_FONCIERE = "taxe_fonciere"
    TAXE_HABITATION = "taxe_habitation"
    CRECHE = "creche"
    NOURRITURE = "nourriture"
    TRAVAUX = "travaux"
    JARDIN = "jardin"
    AUTRE = "autre"


# ═══════════════════════════════════════════════════════════
# TABLE DÉPENSES
# ═══════════════════════════════════════════════════════════


class Depense(Base):
    """Dépense familiale.

    Table SQL: depenses
    Utilisé par: src/services/budget.py

    Attributes:
        montant: Montant de la dépense
        categorie: Catégorie (alimentation, transport, etc.)
        description: Description de la dépense
        date: Date de la dépense
        recurrence: Type de récurrence (ponctuel, mensuel, etc.)
        tags: Tags libres en JSON
        user_id: UUID de l'utilisateur Supabase
    """

    __tablename__ = "depenses"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    montant: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    categorie: Mapped[str] = mapped_column(String(50), nullable=False, default="autre", index=True)
    description: Mapped[str | None] = mapped_column(Text)
    date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today, index=True)
    recurrence: Mapped[str | None] = mapped_column(String(20))  # 'mensuel', 'hebdomadaire', etc.
    tags: Mapped[list | None] = mapped_column(JSONB, default=list)

    # Supabase user
    user_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), index=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        CheckConstraint(
            "categorie IN ('alimentation', 'transport', 'logement', 'sante', "
            "'loisirs', 'vetements', 'education', 'cadeaux', 'abonnements', "
            "'restaurant', 'vacances', 'bebe', 'autre')",
            name="check_categorie_valide",
        ),
    )

    def __repr__(self) -> str:
        return f"<Depense(id={self.id}, montant={self.montant}, categorie='{self.categorie}')>"

    @property
    def est_recurrente(self) -> bool:
        """Vérifie si la dépense est récurrente."""
        return self.recurrence is not None and self.recurrence != "ponctuel"


# ═══════════════════════════════════════════════════════════
# TABLE BUDGETS MENSUELS
# ═══════════════════════════════════════════════════════════


class BudgetMensuelDB(Base):
    """Budget mensuel par utilisateur.

    Table SQL: budgets_mensuels

    Attributes:
        mois: Premier jour du mois
        budget_total: Budget total du mois
        budgets_par_categorie: JSON avec budgets par catégorie
        notes: Notes libres
        user_id: UUID de l'utilisateur Supabase
    """

    __tablename__ = "budgets_mensuels"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    mois: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    budget_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    budgets_par_categorie: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    notes: Mapped[str | None] = mapped_column(Text)

    # Supabase user
    user_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), index=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (UniqueConstraint("mois", "user_id", name="uq_budget_mois_user"),)

    def __repr__(self) -> str:
        return f"<BudgetMensuelDB(id={self.id}, mois={self.mois}, total={self.budget_total})>"


# ═══════════════════════════════════════════════════════════
# DÉPENSES MAISON
# ═══════════════════════════════════════════════════════════


class HouseExpense(Base):
    """Dépense récurrente ou ponctuelle de la maison.

    Pour suivre gaz, eau, électricité, loyer, crèche, etc.
    """

    __tablename__ = "house_expenses"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Catégorie et période
    categorie: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    mois: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-12
    annee: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Montant
    montant: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Consommation (pour gaz, eau, électricité)
    consommation: Mapped[float | None] = mapped_column(Float)  # kWh, m³, litres
    unite_consommation: Mapped[str | None] = mapped_column(String(20))  # kWh, m³, L

    # Fournisseur
    fournisseur: Mapped[str | None] = mapped_column(String(200))
    numero_contrat: Mapped[str | None] = mapped_column(String(100))

    # Notes
    notes: Mapped[str | None] = mapped_column(Text)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<HouseExpense(id={self.id}, cat='{self.categorie}', montant={self.montant})>"
