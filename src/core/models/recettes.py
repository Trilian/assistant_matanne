"""
Modèles pour les recettes et la cuisine.

Contient :
- Ingredient : Référentiel unique d'ingrédients
- Recette : Recette avec métadonnées (bio, robots, nutrition)
- RecetteIngredient : Association N:M avec quantité
- EtapeRecette : Étapes de préparation ordonnées
- VersionRecette : Variantes (bébé, batch cooking)
- HistoriqueRecette : Historique d'utilisation
- BatchMeal : Plats préparés en batch cooking
"""

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .inventaire import ArticleInventaire


# ═══════════════════════════════════════════════════════════
# INGRÉDIENTS (Référentiel unique)
# ═══════════════════════════════════════════════════════════


class Ingredient(Base):
    """Ingrédient de base utilisé partout (recettes, inventaire, courses).
    
    Attributes:
        id: Identifiant unique
        nom: Nom de l'ingrédient (unique)
        categorie: Catégorie (fruits, légumes, viandes, etc.)
        unite: Unité par défaut (pcs, kg, L, etc.)
        cree_le: Date de création
    """

    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False, unique=True, index=True)
    categorie: Mapped[str | None] = mapped_column(String(100), index=True)
    unite: Mapped[str] = mapped_column(String(50), nullable=False, default="pcs")
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    recette_ingredients: Mapped[list["RecetteIngredient"]] = relationship(
        back_populates="ingredient", cascade="all, delete-orphan"
    )
    inventaire: Mapped[list["ArticleInventaire"]] = relationship(
        back_populates="ingredient", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Ingredient(id={self.id}, nom='{self.nom}')>"


# ═══════════════════════════════════════════════════════════
# RECETTES
# ═══════════════════════════════════════════════════════════


class Recette(Base):
    """Recette de cuisine avec ingrédients et étapes.
    
    Attributes:
        nom: Nom de la recette
        description: Description détaillée
        temps_preparation: Temps de préparation en minutes
        temps_cuisson: Temps de cuisson en minutes
        portions: Nombre de portions
        difficulte: Niveau de difficulté (facile, moyen, difficile)
        type_repas: Type de repas (petit_déjeuner, déjeuner, dîner, goûter)
        saison: Saison recommandée
        
        # Tags système
        est_rapide: Recette rapide (<30 min)
        est_equilibre: Recette équilibrée
        compatible_bebe: Adaptable pour bébé
        compatible_batch: Adaptable pour batch cooking
        congelable: Peut être congelée
        
        # Bio & Local
        est_bio: Ingrédients bio
        est_local: Ingrédients locaux
        score_bio: Score bio (0-100)
        score_local: Score local (0-100)
        
        # Robots compatibles
        compatible_cookeo: Compatible Cookeo
        compatible_monsieur_cuisine: Compatible Monsieur Cuisine
        compatible_airfryer: Compatible Airfryer
        compatible_multicooker: Compatible Multicooker
        
        # Nutrition
        calories: Calories par portion
        proteines: Protéines en grammes
        lipides: Lipides en grammes
        glucides: Glucides en grammes
    """

    __tablename__ = "recettes"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)

    # Temps & Portions
    temps_preparation: Mapped[int] = mapped_column(Integer, nullable=False)
    temps_cuisson: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    portions: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    difficulte: Mapped[str] = mapped_column(String(50), nullable=False, default="moyen")

    # Catégorisation
    type_repas: Mapped[str] = mapped_column(String(50), nullable=False, default="dîner", index=True)
    saison: Mapped[str] = mapped_column(String(50), nullable=False, default="toute_année", index=True)
    categorie: Mapped[str | None] = mapped_column(String(100))

    # Flags - Tags système
    est_rapide: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    est_equilibre: Mapped[bool] = mapped_column(Boolean, default=False)
    compatible_bebe: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    compatible_batch: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    congelable: Mapped[bool] = mapped_column(Boolean, default=False)

    # Bio & Local
    est_bio: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    est_local: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    score_bio: Mapped[int] = mapped_column(Integer, default=0)
    score_local: Mapped[int] = mapped_column(Integer, default=0)

    # Robots compatibles
    compatible_cookeo: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    compatible_monsieur_cuisine: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    compatible_airfryer: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    compatible_multicooker: Mapped[bool] = mapped_column(Boolean, default=False)

    # Nutrition (optionnel)
    calories: Mapped[int | None] = mapped_column(Integer)
    proteines: Mapped[float | None] = mapped_column(Float)
    lipides: Mapped[float | None] = mapped_column(Float)
    glucides: Mapped[float | None] = mapped_column(Float)

    # IA
    genere_par_ia: Mapped[bool] = mapped_column(Boolean, default=False)
    score_ia: Mapped[float | None] = mapped_column(Float)

    # Media
    url_image: Mapped[str | None] = mapped_column(String(500))

    # Timestamps
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    modifie_le: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)  # TODO: Make NOT NULL after migration applied

    # Relations
    ingredients: Mapped[list["RecetteIngredient"]] = relationship(
        back_populates="recette", cascade="all, delete-orphan"
    )
    etapes: Mapped[list["EtapeRecette"]] = relationship(
        back_populates="recette", cascade="all, delete-orphan", order_by="EtapeRecette.ordre"
    )
    versions: Mapped[list["VersionRecette"]] = relationship(
        back_populates="recette_base", cascade="all, delete-orphan"
    )
    historique: Mapped[list["HistoriqueRecette"]] = relationship(
        back_populates="recette", cascade="all, delete-orphan"
    )

    # Contraintes
    __table_args__ = (
        CheckConstraint("temps_preparation >= 0", name="ck_temps_prep_positif"),
        CheckConstraint("temps_cuisson >= 0", name="ck_temps_cuisson_positif"),
        CheckConstraint("portions > 0 AND portions <= 20", name="ck_portions_valides"),
        CheckConstraint("score_bio >= 0 AND score_bio <= 100", name="ck_score_bio"),
        CheckConstraint("score_local >= 0 AND score_local <= 100", name="ck_score_local"),
    )

    @property
    def temps_total(self) -> int:
        """Temps total de préparation (préparation + cuisson)."""
        return self.temps_preparation + self.temps_cuisson

    @property
    def robots_compatibles(self) -> list[str]:
        """Retourne la liste des robots de cuisine compatibles."""
        robots = []
        if self.compatible_cookeo:
            robots.append("Cookeo")
        if self.compatible_monsieur_cuisine:
            robots.append("Monsieur Cuisine")
        if self.compatible_airfryer:
            robots.append("Airfryer")
        if self.compatible_multicooker:
            robots.append("Multicooker")
        return robots

    @property
    def tags(self) -> list[str]:
        """Retourne tous les tags de la recette."""
        tags_list = []
        if self.est_rapide:
            tags_list.append("rapide")
        if self.est_equilibre:
            tags_list.append("équilibré")
        if self.compatible_bebe:
            tags_list.append("bébé")
        if self.compatible_batch:
            tags_list.append("batch")
        if self.congelable:
            tags_list.append("congélation")
        if self.est_bio:
            tags_list.append("bio")
        if self.est_local:
            tags_list.append("local")
        return tags_list

    def __repr__(self) -> str:
        return f"<Recette(id={self.id}, nom='{self.nom}')>"


# Alias pour compatibilité
Recipe = Recette


class RecetteIngredient(Base):
    """Association Recette ↔ Ingrédient avec quantité.
    
    Attributes:
        recette_id: ID de la recette
        ingredient_id: ID de l'ingrédient
        quantite: Quantité nécessaire
        unite: Unité de mesure
        optionnel: Si l'ingrédient est optionnel
    """

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

    __table_args__ = (CheckConstraint("quantite > 0", name="ck_quantite_positive"),)

    def __repr__(self) -> str:
        return f"<RecetteIngredient(recette={self.recette_id}, ingredient={self.ingredient_id})>"


class EtapeRecette(Base):
    """Étape de préparation d'une recette.
    
    Attributes:
        recette_id: ID de la recette
        ordre: Numéro d'ordre de l'étape
        description: Description de l'étape
        duree: Durée estimée en minutes
    """

    __tablename__ = "etapes_recette"

    id: Mapped[int] = mapped_column(primary_key=True)
    recette_id: Mapped[int] = mapped_column(
        ForeignKey("recettes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ordre: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    duree: Mapped[int | None] = mapped_column(Integer)

    # Relations
    recette: Mapped["Recette"] = relationship(back_populates="etapes")

    __table_args__ = (CheckConstraint("ordre > 0", name="ck_ordre_positif"),)

    def __repr__(self) -> str:
        return f"<EtapeRecette(recette={self.recette_id}, ordre={self.ordre})>"


class VersionRecette(Base):
    """Version adaptée d'une recette (bébé, batch cooking).
    
    Attributes:
        recette_base_id: ID de la recette de base
        type_version: Type de version (bébé, batch_cooking)
        instructions_modifiees: Instructions adaptées
        ingredients_modifies: Modifications des ingrédients (JSON)
        notes_bebe: Notes spécifiques bébé
        etapes_paralleles_batch: Étapes parallèles pour batch cooking
        temps_optimise_batch: Temps optimisé pour batch cooking
    """

    __tablename__ = "versions_recette"

    id: Mapped[int] = mapped_column(primary_key=True)
    recette_base_id: Mapped[int] = mapped_column(
        ForeignKey("recettes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type_version: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Données adaptées
    instructions_modifiees: Mapped[str | None] = mapped_column(Text)
    ingredients_modifies: Mapped[dict | None] = mapped_column(JSONB)

    # Spécifique bébé
    notes_bebe: Mapped[str | None] = mapped_column(Text)

    # Spécifique batch
    etapes_paralleles_batch: Mapped[list[str] | None] = mapped_column(JSONB)
    temps_optimise_batch: Mapped[int | None] = mapped_column(Integer)

    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    recette_base: Mapped["Recette"] = relationship(back_populates="versions")

    def __repr__(self) -> str:
        return f"<VersionRecette(recette={self.recette_base_id}, type='{self.type_version}')>"


class HistoriqueRecette(Base):
    """Historique d'utilisation d'une recette.
    
    Attributes:
        recette_id: ID de la recette
        date_cuisson: Date de préparation
        portions_cuisinees: Nombre de portions préparées
        note: Note de 0 à 5 étoiles
        avis: Commentaire personnel
    """

    __tablename__ = "historique_recettes"

    id: Mapped[int] = mapped_column(primary_key=True)
    recette_id: Mapped[int] = mapped_column(
        ForeignKey("recettes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date_cuisson: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    portions_cuisinees: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    note: Mapped[int | None] = mapped_column(Integer)
    avis: Mapped[str | None] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    recette: Mapped["Recette"] = relationship(back_populates="historique")

    __table_args__ = (
        CheckConstraint("note IS NULL OR (note >= 0 AND note <= 5)", name="ck_note_valide"),
        CheckConstraint("portions_cuisinees > 0", name="ck_portions_cuisinees_positive"),
    )

    @property
    def nb_jours_depuis(self) -> int:
        """Nombre de jours depuis la dernière cuisson."""
        from datetime import date as dt_date
        return (dt_date.today() - self.date_cuisson).days

    def __repr__(self) -> str:
        return f"<HistoriqueRecette(recette={self.recette_id}, date={self.date_cuisson}, note={self.note})>"


class BatchMeal(Base):
    """Recette préparée en batch cooking.
    
    Attributes:
        recette_id: ID de la recette (optionnel)
        nom: Nom du plat préparé
        description: Description
        portions_creees: Nombre de portions créées
        portions_restantes: Nombre de portions restantes
        date_preparation: Date de préparation
        date_peremption: Date limite de consommation
        container_type: Type de contenant
        localisation: Où est stocké le plat (congélateur, frigo)
    """

    __tablename__ = "batch_meals"

    id: Mapped[int] = mapped_column(primary_key=True)
    recette_id: Mapped[int | None] = mapped_column(
        ForeignKey("recettes.id", ondelete="SET NULL"), index=True
    )
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    portions_creees: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    portions_restantes: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    date_preparation: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    date_peremption: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    container_type: Mapped[str | None] = mapped_column(String(100))
    localisation: Mapped[str | None] = mapped_column(String(200))
    notes: Mapped[str | None] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<BatchMeal(id={self.id}, nom='{self.nom}', portions={self.portions_restantes})>"
