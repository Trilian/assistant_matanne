"""
Models Cuisine - Modèles pour Recettes, Inventaire et Courses.

Ce module contient tous les modèles SQLAlchemy refactorisés
pour le domaine Cuisine avec documentation complète en français.
"""
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Date,
    Float,
    Boolean,
    ForeignKey,
    Text,
    CheckConstraint,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from .base import Base, SaisonEnum, TypeRepasEnum, TypeVersionRecetteEnum, PrioriteEnum


# ═══════════════════════════════════════════════════════════
# INGRÉDIENTS
# ═══════════════════════════════════════════════════════════

class Ingredient(Base):
    """
    Ingrédient de base.

    Représente un ingrédient utilisable dans les recettes et l'inventaire.
    Sert de référentiel unique pour tous les articles alimentaires.

    Attributes:
        id: Identifiant unique
        nom: Nom de l'ingrédient (ex: "Tomates")
        categorie: Catégorie (ex: "Légumes", "Protéines")
        unite: Unité de mesure par défaut (ex: "kg", "L", "pcs")
        cree_le: Date de création
    """

    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False, unique=True, index=True)
    categorie: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    unite: Mapped[str] = mapped_column(String(50), nullable=False)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    recette_ingredients: Mapped[List["RecetteIngredient"]] = relationship(
        back_populates="ingredient",
        cascade="all, delete-orphan"
    )
    inventaire: Mapped[List["ArticleInventaire"]] = relationship(
        back_populates="ingredient",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Ingredient(id={self.id}, nom='{self.nom}')>"


# ═══════════════════════════════════════════════════════════
# RECETTES
# ═══════════════════════════════════════════════════════════

class Recette(Base):
    """
    Recette de cuisine.

    Modèle principal pour les recettes avec toutes leurs caractéristiques,
    ingrédients, étapes et métadonnées.

    Attributes:
        id: Identifiant unique
        nom: Nom de la recette
        description: Description détaillée
        temps_preparation: Temps de préparation en minutes
        temps_cuisson: Temps de cuisson en minutes
        portions: Nombre de portions
        difficulte: Niveau de difficulté (facile, moyen, difficile)
        type_repas: Type de repas (petit_déjeuner, déjeuner, dîner, goûter)
        saison: Saison recommandée
        categorie: Catégorie (entrée, plat, dessert, etc.)
        est_rapide: Flag pour recettes rapides (<30min)
        est_equilibre: Flag pour recettes équilibrées
        compatible_bebe: Peut être adaptée pour bébé
        compatible_batch: Peut être préparée en batch cooking
        congelable: Peut être congelée
        genere_par_ia: A été générée par IA
        score_ia: Score de qualité IA (0-1)
        url_image: URL de l'image
        cree_le: Date de création
        modifie_le: Date de dernière modification
    """

    __tablename__ = "recettes"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Temps et portions
    temps_preparation: Mapped[int] = mapped_column(Integer, nullable=False)
    temps_cuisson: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    portions: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    difficulte: Mapped[str] = mapped_column(String(50), nullable=False, default="moyen", index=True)

    # Catégorisation
    type_repas: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=TypeRepasEnum.DINER.value,
        index=True
    )
    saison: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=SaisonEnum.TOUTE_ANNEE.value,
        index=True
    )
    categorie: Mapped[Optional[str]] = mapped_column(String(100))

    # Tags booléens (optimisés avec index)
    est_rapide: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    est_equilibre: Mapped[bool] = mapped_column(Boolean, default=False)
    compatible_bebe: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    compatible_batch: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    congelable: Mapped[bool] = mapped_column(Boolean, default=False)

    # Métadonnées IA
    genere_par_ia: Mapped[bool] = mapped_column(Boolean, default=False)
    score_ia: Mapped[Optional[float]] = mapped_column(Float)

    # Image
    url_image: Mapped[Optional[str]] = mapped_column(String(500))

    # Timestamps
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    modifie_le: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relations
    ingredients: Mapped[List["RecetteIngredient"]] = relationship(
        back_populates="recette",
        cascade="all, delete-orphan"
    )
    etapes: Mapped[List["EtapeRecette"]] = relationship(
        back_populates="recette",
        cascade="all, delete-orphan",
        order_by="EtapeRecette.ordre"
    )
    versions: Mapped[List["VersionRecette"]] = relationship(
        back_populates="recette_base",
        cascade="all, delete-orphan"
    )

    # Contraintes
    __table_args__ = (
        CheckConstraint('temps_preparation >= 0', name='ck_temps_prep_positif'),
        CheckConstraint('temps_cuisson >= 0', name='ck_temps_cuisson_positif'),
        CheckConstraint('portions > 0 AND portions <= 20', name='ck_portions_valides'),
    )

    @property
    def temps_total(self) -> int:
        """
        Calcule le temps total de préparation.

        Returns:
            Temps total en minutes
        """
        return self.temps_preparation + self.temps_cuisson

    def __repr__(self) -> str:
        return f"<Recette(id={self.id}, nom='{self.nom}', portions={self.portions})>"


class RecetteIngredient(Base):
    """
    Association entre une recette et un ingrédient.

    Représente la quantité et les détails d'un ingrédient
    dans une recette spécifique.

    Attributes:
        id: Identifiant unique
        recette_id: ID de la recette
        ingredient_id: ID de l'ingrédient
        quantite: Quantité nécessaire
        unite: Unité de mesure
        optionnel: L'ingrédient est-il optionnel
    """

    __tablename__ = "recette_ingredients"

    id: Mapped[int] = mapped_column(primary_key=True)
    recette_id: Mapped[int] = mapped_column(
        ForeignKey("recettes.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    quantite: Mapped[float] = mapped_column(Float, nullable=False)
    unite: Mapped[str] = mapped_column(String(50), nullable=False)
    optionnel: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relations
    recette: Mapped["Recette"] = relationship(back_populates="ingredients")
    ingredient: Mapped["Ingredient"] = relationship(back_populates="recette_ingredients")

    # Contraintes
    __table_args__ = (
        CheckConstraint('quantite > 0', name='ck_quantite_positive'),
    )

    def __repr__(self) -> str:
        return f"<RecetteIngredient(recette_id={self.recette_id}, ingredient_id={self.ingredient_id})>"


class EtapeRecette(Base):
    """
    Étape d'une recette.

    Représente une étape de préparation avec son ordre
    et éventuellement sa durée.

    Attributes:
        id: Identifiant unique
        recette_id: ID de la recette
        ordre: Ordre de l'étape (1, 2, 3...)
        description: Description de l'étape
        duree: Durée estimée en minutes (optionnelle)
    """

    __tablename__ = "etapes_recette"

    id: Mapped[int] = mapped_column(primary_key=True)
    recette_id: Mapped[int] = mapped_column(
        ForeignKey("recettes.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    ordre: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    duree: Mapped[Optional[int]] = mapped_column(Integer)

    # Relations
    recette: Mapped["Recette"] = relationship(back_populates="etapes")

    # Contraintes
    __table_args__ = (
        CheckConstraint('ordre > 0', name='ck_ordre_positif'),
        CheckConstraint('duree IS NULL OR duree >= 0', name='ck_duree_positive'),
    )

    def __repr__(self) -> str:
        return f"<EtapeRecette(recette_id={self.recette_id}, ordre={self.ordre})>"


class VersionRecette(Base):
    """
    Version adaptée d'une recette.

    Permet de stocker des adaptations de recettes (bébé, batch cooking)
    avec instructions et ingrédients modifiés.

    Attributes:
        id: Identifiant unique
        recette_base_id: ID de la recette originale
        type_version: Type d'adaptation (bébé, batch_cooking)
        instructions_modifiees: Instructions adaptées
        ingredients_modifies: Ingrédients modifiés (JSON)
        notes_bebe: Notes spécifiques pour version bébé
        etapes_paralleles_batch: Étapes parallélisables (batch)
        temps_optimise_batch: Temps optimisé pour batch
        cree_le: Date de création
    """

    __tablename__ = "versions_recette"

    id: Mapped[int] = mapped_column(primary_key=True)
    recette_base_id: Mapped[int] = mapped_column(
        ForeignKey("recettes.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    type_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )

    # Instructions modifiées
    instructions_modifiees: Mapped[Optional[str]] = mapped_column(Text)
    ingredients_modifies: Mapped[Optional[dict]] = mapped_column(JSONB)

    # Infos spécifiques bébé
    notes_bebe: Mapped[Optional[str]] = mapped_column(Text)

    # Infos spécifiques batch cooking
    etapes_paralleles_batch: Mapped[Optional[List[str]]] = mapped_column(JSONB)
    temps_optimise_batch: Mapped[Optional[int]] = mapped_column(Integer)

    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    recette_base: Mapped["Recette"] = relationship(back_populates="versions")

    def __repr__(self) -> str:
        return f"<VersionRecette(recette_id={self.recette_base_id}, type='{self.type_version}')>"


# ═══════════════════════════════════════════════════════════
# INVENTAIRE
# ═══════════════════════════════════════════════════════════

class ArticleInventaire(Base):
    """
    Article en stock dans l'inventaire.

    Représente un article alimentaire en stock avec sa quantité,
    son seuil d'alerte et sa date de péremption.

    Attributes:
        id: Identifiant unique
        ingredient_id: ID de l'ingrédient
        quantite: Quantité en stock
        quantite_min: Seuil d'alerte minimal
        emplacement: Lieu de stockage (Frigo, Placard, etc.)
        date_peremption: Date de péremption (optionnelle)
        derniere_maj: Date de dernière modification
    """

    __tablename__ = "inventaire"

    id: Mapped[int] = mapped_column(primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    quantite: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    quantite_min: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    emplacement: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    date_peremption: Mapped[Optional[date]] = mapped_column(Date, index=True)
    derniere_maj: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        index=True
    )

    # Relations
    ingredient: Mapped["Ingredient"] = relationship(back_populates="inventaire")

    # Contraintes
    __table_args__ = (
        CheckConstraint('quantite >= 0', name='ck_quantite_inventaire_positive'),
        CheckConstraint('quantite_min >= 0', name='ck_seuil_positif'),
    )

    @property
    def est_stock_bas(self) -> bool:
        """
        Vérifie si le stock est sous le seuil.

        Returns:
            True si stock bas
        """
        return self.quantite < self.quantite_min

    @property
    def est_critique(self) -> bool:
        """
        Vérifie si le stock est critique (< 50% du seuil).

        Returns:
            True si critique
        """
        return self.quantite < (self.quantite_min * 0.5)

    def __repr__(self) -> str:
        return f"<ArticleInventaire(id={self.id}, ingredient_id={self.ingredient_id}, qty={self.quantite})>"


# ═══════════════════════════════════════════════════════════
# COURSES
# ═══════════════════════════════════════════════════════════

class ArticleCourses(Base):
    """
    Article dans la liste de courses.

    Représente un article à acheter avec sa quantité,
    priorité et informations de suivi.

    Attributes:
        id: Identifiant unique
        ingredient_id: ID de l'ingrédient
        quantite_necessaire: Quantité à acheter
        priorite: Priorité d'achat (haute, moyenne, basse)
        achete: Article déjà acheté
        suggere_par_ia: Suggéré automatiquement par l'IA
        cree_le: Date d'ajout
        achete_le: Date d'achat (si acheté)
        rayon_magasin: Rayon du magasin
        magasin_cible: Magasin cible
        notes: Notes supplémentaires
    """

    __tablename__ = "liste_courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    quantite_necessaire: Mapped[float] = mapped_column(Float, nullable=False)
    priorite: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=PrioriteEnum.MOYENNE.value,
        index=True
    )
    achete: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    suggere_par_ia: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    achete_le: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Organisation magasin
    rayon_magasin: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    magasin_cible: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Contraintes
    __table_args__ = (
        CheckConstraint('quantite_necessaire > 0', name='ck_quantite_courses_positive'),
    )

    def __repr__(self) -> str:
        return f"<ArticleCourses(id={self.id}, ingredient_id={self.ingredient_id}, achete={self.achete})>"