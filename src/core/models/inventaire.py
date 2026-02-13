"""
Modèles pour l'inventaire et le stock.

Contient :
- ArticleInventaire : Stock d'un ingrédient
- HistoriqueInventaire : Trace des modifications
"""

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .recettes import Ingredient


# ═══════════════════════════════════════════════════════════
# INVENTAIRE
# ═══════════════════════════════════════════════════════════


class ArticleInventaire(Base):
    """Article en stock dans l'inventaire.

    Attributes:
        ingredient_id: ID de l'ingrédient
        quantite: Quantité en stock
        quantite_min: Seuil d'alerte de stock bas
        emplacement: Où est stocké l'article (frigo, placard, etc.)
        date_peremption: Date de péremption
        photo_url: URL de la photo
        photo_filename: Nom du fichier photo
        code_barres: Code-barres (EAN-13, QR, etc.)
        prix_unitaire: Prix unitaire pour les rapports
    """

    __tablename__ = "inventaire"

    id: Mapped[int] = mapped_column(primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    quantite: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    quantite_min: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    emplacement: Mapped[str | None] = mapped_column(String(100), index=True)
    date_peremption: Mapped[date | None] = mapped_column(Date, index=True)
    derniere_maj: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True
    )

    # Photos
    photo_url: Mapped[str | None] = mapped_column(String(500))
    photo_filename: Mapped[str | None] = mapped_column(String(200))
    photo_uploaded_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Code-barres
    code_barres: Mapped[str | None] = mapped_column(
        String(50), unique=True, index=True, nullable=True
    )
    prix_unitaire: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Relations
    ingredient: Mapped["Ingredient"] = relationship(back_populates="inventaire")
    historique: Mapped[list["HistoriqueInventaire"]] = relationship(
        back_populates="article", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("quantite >= 0", name="ck_quantite_inventaire_positive"),
        CheckConstraint("quantite_min >= 0", name="ck_seuil_positif"),
    )

    @property
    def est_stock_bas(self) -> bool:
        """Stock sous le seuil minimum."""
        return self.quantite < self.quantite_min

    @property
    def est_critique(self) -> bool:
        """Stock critique (< 50% du seuil)."""
        return self.quantite < (self.quantite_min * 0.5)

    def __repr__(self) -> str:
        return f"<ArticleInventaire(ingredient={self.ingredient_id}, qty={self.quantite})>"


class HistoriqueInventaire(Base):
    """Trace chaque modification de l'inventaire.

    Attributes:
        article_id: ID de l'article modifié
        ingredient_id: ID de l'ingrédient
        type_modification: Type (ajout, modification, suppression)
        quantite_avant/apres: Quantités avant/après
        date_modification: Date de la modification
        utilisateur: Utilisateur ayant fait la modification
    """

    __tablename__ = "historique_inventaire"

    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(
        ForeignKey("inventaire.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Type de modification
    type_modification: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # "ajout", "modification", "suppression"

    # Avant/Après
    quantite_avant: Mapped[float | None] = mapped_column(Float)
    quantite_apres: Mapped[float | None] = mapped_column(Float)
    quantite_min_avant: Mapped[float | None] = mapped_column(Float)
    quantite_min_apres: Mapped[float | None] = mapped_column(Float)
    date_peremption_avant: Mapped[date | None] = mapped_column(Date)
    date_peremption_apres: Mapped[date | None] = mapped_column(Date)
    emplacement_avant: Mapped[str | None] = mapped_column(String(100))
    emplacement_apres: Mapped[str | None] = mapped_column(String(100))

    # Métadonnées
    date_modification: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, index=True
    )
    utilisateur: Mapped[str | None] = mapped_column(String(100))
    notes: Mapped[str | None] = mapped_column(Text)

    # Relations
    article: Mapped["ArticleInventaire"] = relationship(back_populates="historique")
    ingredient: Mapped["Ingredient"] = relationship()

    def __repr__(self) -> str:
        return f"<HistoriqueInventaire(article={self.article_id}, type={self.type_modification})>"
