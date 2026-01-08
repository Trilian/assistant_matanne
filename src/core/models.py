"""
Models - Tous les modèles SQLAlchemy de l'application (UNIFIÉ).

Architecture simplifiée : 1 seul fichier pour tous les modèles.
Contient : Base, Enums, Recettes, Inventaire, Courses, Planning.
"""
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, DateTime, Date, Float, Boolean,
    ForeignKey, Text, CheckConstraint
)
from sqlalchemy.orm import relationship, Mapped, mapped_column, declarative_base
from sqlalchemy import MetaData
from sqlalchemy.dialects.postgresql import JSONB
import enum


# ═══════════════════════════════════════════════════════════
# BASE SQLALCHEMY
# ═══════════════════════════════════════════════════════════

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)

# Export pour accès externe
__all__ = ["Base", "metadata"]


# ═══════════════════════════════════════════════════════════
# ÉNUMÉRATIONS
# ═══════════════════════════════════════════════════════════

class PrioriteEnum(str, enum.Enum):
    """Niveaux de priorité"""
    BASSE = "basse"
    MOYENNE = "moyenne"
    HAUTE = "haute"


class SaisonEnum(str, enum.Enum):
    """Saisons"""
    PRINTEMPS = "printemps"
    ETE = "été"
    AUTOMNE = "automne"
    HIVER = "hiver"
    TOUTE_ANNEE = "toute_année"


class TypeRepasEnum(str, enum.Enum):
    """Types de repas"""
    PETIT_DEJEUNER = "petit_déjeuner"
    DEJEUNER = "déjeuner"
    DINER = "dîner"
    GOUTER = "goûter"


class TypeVersionRecetteEnum(str, enum.Enum):
    """Types de versions recettes"""
    STANDARD = "standard"
    BEBE = "bébé"
    BATCH_COOKING = "batch_cooking"


# ═══════════════════════════════════════════════════════════
# INGRÉDIENTS (Référentiel unique)
# ═══════════════════════════════════════════════════════════

class Ingredient(Base):
    """Ingrédient de base utilisé partout (recettes, inventaire, courses)"""
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False, unique=True, index=True)
    categorie: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    unite: Mapped[str] = mapped_column(String(50), nullable=False, default="pcs")
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    recette_ingredients: Mapped[List["RecetteIngredient"]] = relationship(
        back_populates="ingredient", cascade="all, delete-orphan"
    )
    inventaire: Mapped[List["ArticleInventaire"]] = relationship(
        back_populates="ingredient", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Ingredient(id={self.id}, nom='{self.nom}')>"


# ═══════════════════════════════════════════════════════════
# RECETTES
# ═══════════════════════════════════════════════════════════

class Recette(Base):
    """Recette de cuisine avec ingrédients et étapes"""
    __tablename__ = "recettes"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Temps & Portions
    temps_preparation: Mapped[int] = mapped_column(Integer, nullable=False)
    temps_cuisson: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    portions: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    difficulte: Mapped[str] = mapped_column(String(50), nullable=False, default="moyen")

    # Catégorisation
    type_repas: Mapped[str] = mapped_column(
        String(50), nullable=False, default="dîner", index=True
    )
    saison: Mapped[str] = mapped_column(
        String(50), nullable=False, default="toute_année", index=True
    )
    categorie: Mapped[Optional[str]] = mapped_column(String(100))

    # Flags
    est_rapide: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    est_equilibre: Mapped[bool] = mapped_column(Boolean, default=False)
    compatible_bebe: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    compatible_batch: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    congelable: Mapped[bool] = mapped_column(Boolean, default=False)

    # IA
    genere_par_ia: Mapped[bool] = mapped_column(Boolean, default=False)
    score_ia: Mapped[Optional[float]] = mapped_column(Float)

    # Media
    url_image: Mapped[Optional[str]] = mapped_column(String(500))

    # Timestamps
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    modifie_le: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relations
    ingredients: Mapped[List["RecetteIngredient"]] = relationship(
        back_populates="recette", cascade="all, delete-orphan"
    )
    etapes: Mapped[List["EtapeRecette"]] = relationship(
        back_populates="recette", cascade="all, delete-orphan", order_by="EtapeRecette.ordre"
    )
    versions: Mapped[List["VersionRecette"]] = relationship(
        back_populates="recette_base", cascade="all, delete-orphan"
    )

    # Contraintes
    __table_args__ = (
        CheckConstraint('temps_preparation >= 0', name='ck_temps_prep_positif'),
        CheckConstraint('temps_cuisson >= 0', name='ck_temps_cuisson_positif'),
        CheckConstraint('portions > 0 AND portions <= 20', name='ck_portions_valides'),
    )

    @property
    def temps_total(self) -> int:
        """Temps total de préparation"""
        return self.temps_preparation + self.temps_cuisson

    def __repr__(self) -> str:
        return f"<Recette(id={self.id}, nom='{self.nom}')>"


class RecetteIngredient(Base):
    """Association Recette ↔ Ingrédient avec quantité"""
    __tablename__ = "recette_ingredients"

    id: Mapped[int] = mapped_column(primary_key=True)
    recette_id: Mapped[int] = mapped_column(
        ForeignKey("recettes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    quantite: Mapped[float] = mapped_column(Float, nullable=False)
    unite: Mapped[str] = mapped_column(String(50), nullable=False)
    optionnel: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relations
    recette: Mapped["Recette"] = relationship(back_populates="ingredients")
    ingredient: Mapped["Ingredient"] = relationship(back_populates="recette_ingredients")

    __table_args__ = (
        CheckConstraint('quantite > 0', name='ck_quantite_positive'),
    )

    def __repr__(self) -> str:
        return f"<RecetteIngredient(recette={self.recette_id}, ingredient={self.ingredient_id})>"


class EtapeRecette(Base):
    """Étape de préparation d'une recette"""
    __tablename__ = "etapes_recette"

    id: Mapped[int] = mapped_column(primary_key=True)
    recette_id: Mapped[int] = mapped_column(
        ForeignKey("recettes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ordre: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    duree: Mapped[Optional[int]] = mapped_column(Integer)

    # Relations
    recette: Mapped["Recette"] = relationship(back_populates="etapes")

    __table_args__ = (
        CheckConstraint('ordre > 0', name='ck_ordre_positif'),
    )

    def __repr__(self) -> str:
        return f"<EtapeRecette(recette={self.recette_id}, ordre={self.ordre})>"


class VersionRecette(Base):
    """Version adaptée d'une recette (bébé, batch cooking)"""
    __tablename__ = "versions_recette"

    id: Mapped[int] = mapped_column(primary_key=True)
    recette_base_id: Mapped[int] = mapped_column(
        ForeignKey("recettes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type_version: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Données adaptées
    instructions_modifiees: Mapped[Optional[str]] = mapped_column(Text)
    ingredients_modifies: Mapped[Optional[dict]] = mapped_column(JSONB)

    # Spécifique bébé
    notes_bebe: Mapped[Optional[str]] = mapped_column(Text)

    # Spécifique batch
    etapes_paralleles_batch: Mapped[Optional[List[str]]] = mapped_column(JSONB)
    temps_optimise_batch: Mapped[Optional[int]] = mapped_column(Integer)

    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    recette_base: Mapped["Recette"] = relationship(back_populates="versions")

    def __repr__(self) -> str:
        return f"<VersionRecette(recette={self.recette_base_id}, type='{self.type_version}')>"


# ═══════════════════════════════════════════════════════════
# INVENTAIRE
# ═══════════════════════════════════════════════════════════

class ArticleInventaire(Base):
    """Article en stock dans l'inventaire"""
    __tablename__ = "inventaire"

    id: Mapped[int] = mapped_column(primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.id", ondelete="CASCADE"),
        nullable=False, unique=True, index=True
    )
    quantite: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    quantite_min: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    emplacement: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    date_peremption: Mapped[Optional[date]] = mapped_column(Date, index=True)
    derniere_maj: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True
    )

    # Relations
    ingredient: Mapped["Ingredient"] = relationship(back_populates="inventaire")

    __table_args__ = (
        CheckConstraint('quantite >= 0', name='ck_quantite_inventaire_positive'),
        CheckConstraint('quantite_min >= 0', name='ck_seuil_positif'),
    )

    @property
    def est_stock_bas(self) -> bool:
        """Stock sous le seuil"""
        return self.quantite < self.quantite_min

    @property
    def est_critique(self) -> bool:
        """Stock critique (< 50% du seuil)"""
        return self.quantite < (self.quantite_min * 0.5)

    def __repr__(self) -> str:
        return f"<ArticleInventaire(ingredient={self.ingredient_id}, qty={self.quantite})>"


# ═══════════════════════════════════════════════════════════
# COURSES
# ═══════════════════════════════════════════════════════════

class ArticleCourses(Base):
    """Article dans la liste de courses"""
    __tablename__ = "liste_courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    quantite_necessaire: Mapped[float] = mapped_column(Float, nullable=False)
    priorite: Mapped[str] = mapped_column(
        String(50), nullable=False, default="moyenne", index=True
    )
    achete: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    suggere_par_ia: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    achete_le: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Organisation
    rayon_magasin: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    magasin_cible: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    __table_args__ = (
        CheckConstraint('quantite_necessaire > 0', name='ck_quantite_courses_positive'),
    )

    def __repr__(self) -> str:
        return f"<ArticleCourses(ingredient={self.ingredient_id}, achete={self.achete})>"


# ═══════════════════════════════════════════════════════════
# PLANNING
# ═══════════════════════════════════════════════════════════

class Planning(Base):
    """Planning hebdomadaire de repas"""
    __tablename__ = "plannings"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    semaine_debut: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    semaine_fin: Mapped[date] = mapped_column(Date, nullable=False)
    actif: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    genere_par_ia: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    repas: Mapped[List["Repas"]] = relationship(
        back_populates="planning", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Planning(id={self.id}, nom='{self.nom}')>"


class Repas(Base):
    """Repas planifié dans un planning"""
    __tablename__ = "repas"

    id: Mapped[int] = mapped_column(primary_key=True)
    planning_id: Mapped[int] = mapped_column(
        ForeignKey("plannings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    recette_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("recettes.id", ondelete="SET NULL"), index=True
    )
    date_repas: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    type_repas: Mapped[str] = mapped_column(
        String(50), nullable=False, default="dîner", index=True
    )
    portion_ajustee: Mapped[Optional[int]] = mapped_column(Integer)
    prepare: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relations
    planning: Mapped["Planning"] = relationship(back_populates="repas")
    recette: Mapped[Optional["Recette"]] = relationship()

    def __repr__(self) -> str:
        return f"<Repas(id={self.id}, date={self.date_repas}, type='{self.type_repas}')>"


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════

def obtenir_valeurs_enum(enum_class: type[enum.Enum]) -> list[str]:
    """Récupère toutes les valeurs d'un enum"""
    return [e.value for e in enum_class]

