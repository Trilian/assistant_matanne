"""
Modèles pour les listes de courses.

Contient :
- ArticleCourses : Article dans la liste de courses
- ModeleCourses : Template réutilisable
- ArticleModele : Article d'un modèle
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, utc_now

if TYPE_CHECKING:
    from .recettes import Ingredient


# ═══════════════════════════════════════════════════════════
# COURSES
# ═══════════════════════════════════════════════════════════


class ListeCourses(Base):
    """Liste de courses.

    Attributes:
        nom: Nom de la liste
        archivee: Si la liste est archivée
        cree_le: Date de création
        modifie_le: Date de modification
    """

    __tablename__ = "listes_courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    archivee: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    cree_le: Mapped[datetime] = mapped_column("created_at", DateTime, default=utc_now, index=True)
    modifie_le: Mapped[datetime] = mapped_column(
        "updated_at", DateTime, default=utc_now, onupdate=utc_now
    )

    # Relations
    articles: Mapped[list["ArticleCourses"]] = relationship(
        back_populates="liste", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ListeCourses(id={self.id}, nom='{self.nom}')>"


class ArticleCourses(Base):
    """Article dans la liste de courses.

    Attributes:
        ingredient_id: ID de l'ingrédient
        quantite_necessaire: Quantité à acheter
        priorite: Priorité (haute, moyenne, basse)
        achete: Si l'article a été acheté
        suggere_par_ia: Si suggéré par l'IA
        rayon_magasin: Rayon du magasin
        magasin_cible: Magasin préféré
        notes: Notes supplémentaires
    """

    __tablename__ = "liste_courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    liste_id: Mapped[int] = mapped_column(
        ForeignKey("listes_courses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    quantite_necessaire: Mapped[float] = mapped_column(Float, nullable=False)
    priorite: Mapped[str] = mapped_column(String(50), nullable=False, default="moyenne", index=True)
    achete: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    suggere_par_ia: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=utc_now, index=True)
    achete_le: Mapped[datetime | None] = mapped_column(DateTime)

    # Organisation
    rayon_magasin: Mapped[str | None] = mapped_column(String(100), index=True)
    magasin_cible: Mapped[str | None] = mapped_column(String(50), index=True)
    notes: Mapped[str | None] = mapped_column(Text)

    # Relations
    liste: Mapped["ListeCourses"] = relationship(back_populates="articles")
    ingredient: Mapped["Ingredient"] = relationship("Ingredient", foreign_keys=[ingredient_id])

    __table_args__ = (
        CheckConstraint("quantite_necessaire > 0", name="ck_quantite_courses_positive"),
    )

    def __repr__(self) -> str:
        return f"<ArticleCourses(ingredient={self.ingredient_id}, achete={self.achete})>"


# ═══════════════════════════════════════════════════════════
# MODÈLES COURSES (Templates réutilisables)
# ═══════════════════════════════════════════════════════════


class ModeleCourses(Base):
    """Template persistant pour listes de courses réutilisables.

    Attributes:
        nom: Nom du modèle
        description: Description
        utilisateur_id: ID utilisateur (support multi-user)
        actif: Si le modèle est actif
        articles_data: Données JSON pour flexibilité
    """

    __tablename__ = "modeles_courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)

    # Support multi-user
    utilisateur_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)

    # Métadonnées
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    modifie_le: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)
    actif: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    # Données articles (JSON)
    articles_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relations
    articles: Mapped[list["ArticleModele"]] = relationship(
        "ArticleModele", back_populates="modele", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ModeleCourses(nom={self.nom}, articles={len(self.articles)})>"


class ArticleModele(Base):
    """Article d'un modèle de courses.

    Attributes:
        modele_id: ID du modèle parent
        ingredient_id: ID de l'ingrédient (optionnel)
        nom_article: Nom de l'article
        quantite: Quantité
        unite: Unité de mesure
        rayon_magasin: Rayon du magasin
        priorite: Priorité (haute, moyenne, basse)
        ordre: Ordre d'affichage
    """

    __tablename__ = "articles_modeles"

    id: Mapped[int] = mapped_column(primary_key=True)
    modele_id: Mapped[int] = mapped_column(
        ForeignKey("modeles_courses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ingredient_id: Mapped[int | None] = mapped_column(
        ForeignKey("ingredients.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Propriétés
    nom_article: Mapped[str] = mapped_column(String(100), nullable=False)
    quantite: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    unite: Mapped[str] = mapped_column(String(20), nullable=False, default="pièce")
    rayon_magasin: Mapped[str] = mapped_column(String(100), nullable=False, default="Autre")
    priorite: Mapped[str] = mapped_column(String(20), nullable=False, default="moyenne")
    notes: Mapped[str | None] = mapped_column(Text)

    # Tri
    ordre: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Métadonnées
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    __table_args__ = (
        CheckConstraint("quantite > 0", name="ck_article_modele_quantite_positive"),
        CheckConstraint(
            "priorite IN ('haute', 'moyenne', 'basse')", name="ck_article_modele_priorite_valide"
        ),
    )

    # Relations
    modele: Mapped["ModeleCourses"] = relationship(back_populates="articles")
    ingredient: Mapped["Ingredient | None"] = relationship()

    def __repr__(self) -> str:
        return f"<ArticleModele(modele={self.modele_id}, article={self.nom_article})>"
