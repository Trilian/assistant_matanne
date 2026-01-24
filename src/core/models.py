"""
Models - Tous les modèles SQLAlchemy de l'application (UNIFIÉ).

Architecture simplifiée : 1 seul fichier pour tous les modèles.
Contient : Base, Enums, Recettes, Inventaire, Courses, Planning.
"""

import enum
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column, relationship

# ═══════════════════════════════════════════════════════════
# BASE SQLALCHEMY
# ═══════════════════════════════════════════════════════════

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


metadata = MetaData(naming_convention=convention)


class Base(DeclarativeBase):
    metadata = metadata

# Expose tous les modèles et symboles du module (laisser Python gérer l'export)


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
    """Recette de cuisine avec ingrédients et étapes"""

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
    saison: Mapped[str] = mapped_column(
        String(50), nullable=False, default="toute_année", index=True
    )
    categorie: Mapped[str | None] = mapped_column(String(100))

    # Flags - Tags système
    est_rapide: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    est_equilibre: Mapped[bool] = mapped_column(Boolean, default=False)
    compatible_bebe: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    compatible_batch: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    congelable: Mapped[bool] = mapped_column(Boolean, default=False)

    # ✨ NOUVEAU - Bio & Local
    est_bio: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    est_local: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    score_bio: Mapped[int] = mapped_column(Integer, default=0)  # 0-100
    score_local: Mapped[int] = mapped_column(Integer, default=0)  # 0-100

    # ✨ NOUVEAU - Robots compatibles
    compatible_cookeo: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    compatible_monsieur_cuisine: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    compatible_airfryer: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    compatible_multicooker: Mapped[bool] = mapped_column(Boolean, default=False)

    # ✨ NOUVEAU - Nutrition (optionnel)
    calories: Mapped[int | None] = mapped_column(Integer)
    proteines: Mapped[float | None] = mapped_column(Float)  # grammes
    lipides: Mapped[float | None] = mapped_column(Float)  # grammes
    glucides: Mapped[float | None] = mapped_column(Float)  # grammes

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
        """Temps total de préparation"""
        return self.temps_preparation + self.temps_cuisson

    @property
    def robots_compatibles(self) -> list[str]:
        """Retourne la liste des robots compatibles"""
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
        """Retourne tous les tags de la recette"""
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

    __table_args__ = (CheckConstraint("quantite > 0", name="ck_quantite_positive"),)

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
    duree: Mapped[int | None] = mapped_column(Integer)

    # Relations
    recette: Mapped["Recette"] = relationship(back_populates="etapes")

    __table_args__ = (CheckConstraint("ordre > 0", name="ck_ordre_positif"),)

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


# ═══════════════════════════════════════════════════════════
# INVENTAIRE
# ═══════════════════════════════════════════════════════════


class ArticleInventaire(Base):
    """Article en stock dans l'inventaire"""

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
    
    # Photos (Nouveau!)
    photo_url: Mapped[str | None] = mapped_column(String(500))  # URL vers la photo stockée
    photo_filename: Mapped[str | None] = mapped_column(String(200))  # Nom du fichier
    photo_uploaded_at: Mapped[datetime | None] = mapped_column(DateTime)  # Quand uploadée
    
    # Code-barres (Nouveau!)
    code_barres: Mapped[str | None] = mapped_column(String(50), unique=True, index=True, nullable=True)  # EAN-13, QR, etc.
    prix_unitaire: Mapped[float | None] = mapped_column(Float, nullable=True)  # Prix unitaire pour rapports

    # Relations
    ingredient: Mapped["Ingredient"] = relationship(back_populates="inventaire")

    __table_args__ = (
        CheckConstraint("quantite >= 0", name="ck_quantite_inventaire_positive"),
        CheckConstraint("quantite_min >= 0", name="ck_seuil_positif"),
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
    priorite: Mapped[str] = mapped_column(String(50), nullable=False, default="moyenne", index=True)
    achete: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    suggere_par_ia: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    achete_le: Mapped[datetime | None] = mapped_column(DateTime)

    # Organisation
    rayon_magasin: Mapped[str | None] = mapped_column(String(100), index=True)
    magasin_cible: Mapped[str | None] = mapped_column(String(50), index=True)
    notes: Mapped[str | None] = mapped_column(Text)

    # Relationships
    ingredient: Mapped["Ingredient"] = relationship("Ingredient", foreign_keys=[ingredient_id])

    __table_args__ = (
        CheckConstraint("quantite_necessaire > 0", name="ck_quantite_courses_positive"),
    )

    def __repr__(self) -> str:
        return f"<ArticleCourses(ingredient={self.ingredient_id}, achete={self.achete})>"


# ═══════════════════════════════════════════════════════════
# FAMILLE & BIEN-ÊTRE
# ═══════════════════════════════════════════════════════════


class ChildProfile(Base):
    """Profil d'un enfant suivi"""

    __tablename__ = "child_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    gender: Mapped[str | None] = mapped_column(String(20))
    notes: Mapped[str | None] = mapped_column(Text)
    actif: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    wellbeing_entries: Mapped[list["WellbeingEntry"]] = relationship(
        back_populates="child", cascade="all, delete-orphan"
    )
    milestones: Mapped[list["Milestone"]] = relationship(
        back_populates="child", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ChildProfile(name='{self.name}', id={self.id})>"


class WellbeingEntry(Base):
    """Entrée de bien-être familial"""

    __tablename__ = "wellbeing_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    child_id: Mapped[int | None] = mapped_column(
        ForeignKey("child_profiles.id", ondelete="CASCADE"), index=True
    )
    username: Mapped[str | None] = mapped_column(String(200), index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True, default=date.today)
    mood: Mapped[str | None] = mapped_column(String(100))
    sleep_hours: Mapped[float | None] = mapped_column(Float)
    activity: Mapped[str | None] = mapped_column(String(200))
    notes: Mapped[str | None] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    child: Mapped[Optional["ChildProfile"]] = relationship(back_populates="wellbeing_entries")

    def __repr__(self) -> str:
        return f"<WellbeingEntry(id={self.id}, date={self.date}, mood='{self.mood}')>"


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
    notes: Mapped[str | None] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    repas: Mapped[list["Repas"]] = relationship(
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
    recette_id: Mapped[int | None] = mapped_column(
        ForeignKey("recettes.id", ondelete="SET NULL"), index=True
    )
    date_repas: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    type_repas: Mapped[str] = mapped_column(String(50), nullable=False, default="dîner", index=True)
    portion_ajustee: Mapped[int | None] = mapped_column(Integer)
    prepare: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text)

    # Relations
    planning: Mapped["Planning"] = relationship(back_populates="repas")
    recette: Mapped[Optional["Recette"]] = relationship()

    def __repr__(self) -> str:
        return f"<Repas(id={self.id}, date={self.date_repas}, type='{self.type_repas}')>"


# ═══════════════════════════════════════════════════════════
# ALIAS POUR COMPATIBILITÉ (Recette = Recipe)
# ═══════════════════════════════════════════════════════════

# Alias pour la compatibilité avec les modules qui utilisent Recipe
Recipe = Recette


# ═══════════════════════════════════════════════════════════
# PROJETS
# ═══════════════════════════════════════════════════════════


class Project(Base):
    """Projet domestique"""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    statut: Mapped[str] = mapped_column(String(50), nullable=False, default="en_cours", index=True)
    priorite: Mapped[str] = mapped_column(String(50), nullable=False, default="moyenne", index=True)
    date_debut: Mapped[date | None] = mapped_column(Date)
    date_fin_prevue: Mapped[date | None] = mapped_column(Date)
    date_fin_reelle: Mapped[date | None] = mapped_column(Date)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    tasks: Mapped[list["ProjectTask"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, nom='{self.nom}', statut='{self.statut}')>"


class ProjectTask(Base):
    """Tâche d'un projet"""

    __tablename__ = "project_tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    statut: Mapped[str] = mapped_column(String(50), nullable=False, default="à_faire", index=True)
    priorite: Mapped[str] = mapped_column(String(50), nullable=False, default="moyenne")
    date_echéance: Mapped[date | None] = mapped_column(Date)
    assigné_à: Mapped[str | None] = mapped_column(String(200))
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    project: Mapped["Project"] = relationship(back_populates="tasks")

    def __repr__(self) -> str:
        return f"<ProjectTask(id={self.id}, project={self.project_id}, statut='{self.statut}')>"


# ═══════════════════════════════════════════════════════════
# ROUTINES
# ═══════════════════════════════════════════════════════════


class Routine(Base):
    """Routine ou habitude quotidienne"""

    __tablename__ = "routines"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    categorie: Mapped[str | None] = mapped_column(String(100), index=True)
    frequence: Mapped[str] = mapped_column(String(50), nullable=False, default="quotidien")
    actif: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    tasks: Mapped[list["RoutineTask"]] = relationship(
        back_populates="routine", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Routine(id={self.id}, nom='{self.nom}')>"


class RoutineTask(Base):
    """Tâche d'une routine"""

    __tablename__ = "routine_tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    routine_id: Mapped[int] = mapped_column(
        ForeignKey("routines.id", ondelete="CASCADE"), nullable=False, index=True
    )
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    ordre: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    heure_prevue: Mapped[str | None] = mapped_column(String(5))  # Format: HH:MM
    fait_le: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    routine: Mapped["Routine"] = relationship(back_populates="tasks")

    def __repr__(self) -> str:
        return f"<RoutineTask(id={self.id}, routine={self.routine_id}, nom='{self.nom}')>"


# ═══════════════════════════════════════════════════════════
# JARDIN
# ═══════════════════════════════════════════════════════════


class GardenItem(Base):
    """Élément du jardin (plante, légume, etc)"""

    __tablename__ = "garden_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # plante, légume, fleur, etc
    location: Mapped[str | None] = mapped_column(String(200))
    statut: Mapped[str] = mapped_column(String(50), nullable=False, default="actif", index=True)  # actif, inactif, mort
    date_plantation: Mapped[date | None] = mapped_column(Date)
    date_recolte_prevue: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    logs: Mapped[list["GardenLog"]] = relationship(
        back_populates="garden_item", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<GardenItem(id={self.id}, nom='{self.nom}', type='{self.type}')>"


class GardenLog(Base):
    """Journal d'entretien du jardin"""

    __tablename__ = "garden_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    garden_item_id: Mapped[int | None] = mapped_column(
        ForeignKey("garden_items.id", ondelete="CASCADE"), index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True, default=date.today)
    action: Mapped[str] = mapped_column(String(200), nullable=False)  # arrosage, désherbage, taille, récolte, etc
    notes: Mapped[str | None] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    garden_item: Mapped[Optional["GardenItem"]] = relationship(back_populates="logs")


# ═══════════════════════════════════════════════════════════
# FAMILLE - JALONS & DÉVELOPPEMENT JULES
# ═══════════════════════════════════════════════════════════


class Milestone(Base):
    """Jalons & apprentissages de Jules"""

    __tablename__ = "milestones"

    id: Mapped[int] = mapped_column(primary_key=True)
    child_id: Mapped[int] = mapped_column(
        ForeignKey("child_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    titre: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    categorie: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # "langage", "motricité", "social", "cognitif", etc
    date_atteint: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    photo_url: Mapped[str | None] = mapped_column(String(500))
    notes: Mapped[str | None] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    child: Mapped["ChildProfile"] = relationship(back_populates="milestones")

    def __repr__(self) -> str:
        return f"<Milestone(id={self.id}, titre='{self.titre}', date={self.date_atteint})>"


# ═══════════════════════════════════════════════════════════
# FAMILLE - ACTIVITÉS & SORTIES
# ═══════════════════════════════════════════════════════════


class FamilyActivity(Base):
    """Activités et sorties familiales"""

    __tablename__ = "family_activities"

    id: Mapped[int] = mapped_column(primary_key=True)
    titre: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    type_activite: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # "parc", "musée", "piscine", "jeu_maison", "sport", etc
    date_prevue: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    duree_heures: Mapped[float | None] = mapped_column(Float)  # durée en heures
    lieu: Mapped[str | None] = mapped_column(String(200))
    qui_participe: Mapped[list[str] | None] = mapped_column(JSONB)  # ["Jules", "Papa", "Maman"]
    age_minimal_recommande: Mapped[int | None] = mapped_column(Integer)  # en mois
    cout_estime: Mapped[float | None] = mapped_column(Float)
    cout_reel: Mapped[float | None] = mapped_column(Float)
    statut: Mapped[str] = mapped_column(String(50), nullable=False, default="planifié", index=True)  # planifié, terminé, annulé
    notes: Mapped[str | None] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("duree_heures > 0", name="ck_activite_duree_positive"),
        CheckConstraint("age_minimal_recommande >= 0", name="ck_activite_age_positif"),
    )

    def __repr__(self) -> str:
        return f"<FamilyActivity(id={self.id}, titre='{self.titre}', date={self.date_prevue})>"


# ═══════════════════════════════════════════════════════════
# SANTÉ & BIEN-ÊTRE - ROUTINES & OBJECTIFS SANTÉ
# ═══════════════════════════════════════════════════════════


class HealthRoutine(Base):
    """Routine de santé/sport"""

    __tablename__ = "health_routines"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    type_routine: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # "yoga", "course", "gym", "marche", "sport", etc
    frequence: Mapped[str] = mapped_column(String(50), nullable=False)  # "3x/semaine", "quotidien", etc
    duree_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    intensite: Mapped[str] = mapped_column(String(50), nullable=False, default="modérée")  # "basse", "modérée", "haute"
    jours_semaine: Mapped[list[str] | None] = mapped_column(JSONB)  # ["lundi", "mercredi", "vendredi"]
    calories_brulees_estimees: Mapped[int | None] = mapped_column(Integer)
    actif: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    notes: Mapped[str | None] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    entries: Mapped[list["HealthEntry"]] = relationship(
        back_populates="routine", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("duree_minutes > 0", name="ck_routine_duree_positive"),
    )

    def __repr__(self) -> str:
        return f"<HealthRoutine(id={self.id}, nom='{self.nom}', type='{self.type_routine}')>"


class HealthObjective(Base):
    """Objectifs de santé/bien-être"""

    __tablename__ = "health_objectives"

    id: Mapped[int] = mapped_column(primary_key=True)
    titre: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    categorie: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # "poids", "endurance", "force", "flexibilité", "alimentation", etc
    valeur_cible: Mapped[float] = mapped_column(Float, nullable=False)
    unite: Mapped[str] = mapped_column(String(50))  # "kg", "km", "reps", "days", etc
    valeur_actuelle: Mapped[float | None] = mapped_column(Float)
    date_debut: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    date_cible: Mapped[date] = mapped_column(Date, nullable=False)
    priorite: Mapped[str] = mapped_column(String(50), nullable=False, default="moyenne")  # "haute", "moyenne", "basse"
    statut: Mapped[str] = mapped_column(String(50), nullable=False, default="en_cours", index=True)  # "en_cours", "atteint", "abandonné"
    notes: Mapped[str | None] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("valeur_cible > 0", name="ck_objective_valeur_positive"),
        CheckConstraint("date_debut <= date_cible", name="ck_objective_dates"),
    )

    def __repr__(self) -> str:
        return f"<HealthObjective(id={self.id}, titre='{self.titre}', statut='{self.statut}')>"


class HealthEntry(Base):
    """Entrée quotidienne de suivi santé"""

    __tablename__ = "health_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    routine_id: Mapped[int | None] = mapped_column(
        ForeignKey("health_routines.id", ondelete="CASCADE"), index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True, default=date.today)
    type_activite: Mapped[str] = mapped_column(String(100), nullable=False)  # "course", "yoga", "gym", etc
    duree_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    intensite: Mapped[str] = mapped_column(String(50))  # "basse", "modérée", "haute"
    calories_brulees: Mapped[int | None] = mapped_column(Integer)
    note_energie: Mapped[int | None] = mapped_column(Integer)  # 1-10
    note_moral: Mapped[int | None] = mapped_column(Integer)  # 1-10
    ressenti: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    routine: Mapped[Optional["HealthRoutine"]] = relationship(back_populates="entries")

    __table_args__ = (
        CheckConstraint("duree_minutes > 0", name="ck_entry_duree_positive"),
        CheckConstraint("note_energie >= 1 AND note_energie <= 10", name="ck_entry_energie"),
        CheckConstraint("note_moral >= 1 AND note_moral <= 10", name="ck_entry_moral"),
    )

    def __repr__(self) -> str:
        return f"<HealthEntry(id={self.id}, date={self.date}, type='{self.type_activite}')>"


# ═══════════════════════════════════════════════════════════
# FAMILLE - BUDGET FAMILLE
# ═══════════════════════════════════════════════════════════


class FamilyBudget(Base):
    """Dépenses familiales par catégorie"""

    __tablename__ = "family_budgets"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True, default=date.today)
    categorie: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # "Jules_jouets", "Jules_vetements", "Jules_couches", "Nous_sport", "Nous_nutrition", "Activités", "Autre"
    description: Mapped[str | None] = mapped_column(String(200))
    montant: Mapped[float] = mapped_column(Float, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("montant > 0", name="ck_budget_montant_positive"),
    )

    def __repr__(self) -> str:
        return f"<FamilyBudget(id={self.id}, categorie='{self.categorie}', montant={self.montant})>"

    def __repr__(self) -> str:
        return f"<GardenLog(id={self.id}, action='{self.action}', date={self.date})>"


# ═══════════════════════════════════════════════════════════
# ÉVÉNEMENTS CALENDRIER
# ═══════════════════════════════════════════════════════════


class CalendarEvent(Base):
    """Événement du calendrier"""

    __tablename__ = "calendar_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    titre: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    date_debut: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    date_fin: Mapped[datetime | None] = mapped_column(DateTime)
    lieu: Mapped[str | None] = mapped_column(String(200))
    type_event: Mapped[str] = mapped_column(String(50), nullable=False, default="autre", index=True)
    couleur: Mapped[str | None] = mapped_column(String(20))  # rouge, bleu, vert, etc
    rappel_avant_minutes: Mapped[int | None] = mapped_column(Integer)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<CalendarEvent(id={self.id}, titre='{self.titre}', date={self.date_debut})>"


# ═══════════════════════════════════════════════════════════
# BATCH COOKING
# ═══════════════════════════════════════════════════════════


class BatchMeal(Base):
    """Recette préparée en batch cooking"""

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
    localisation: Mapped[str | None] = mapped_column(String(200))  # congélateur, frigo, etc
    notes: Mapped[str | None] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<BatchMeal(id={self.id}, nom='{self.nom}', portions={self.portions_restantes})>"


# ═══════════════════════════════════════════════════════════
# HISTORIQUE RECETTES
# ═══════════════════════════════════════════════════════════


class HistoriqueRecette(Base):
    """Historique d'utilisation d'une recette"""

    __tablename__ = "historique_recettes"

    id: Mapped[int] = mapped_column(primary_key=True)
    recette_id: Mapped[int] = mapped_column(
        ForeignKey("recettes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date_cuisson: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    portions_cuisinees: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    note: Mapped[int | None] = mapped_column(Integer)  # 0-5 stars
    avis: Mapped[str | None] = mapped_column(Text)  # Commentaire personnel
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    recette: Mapped["Recette"] = relationship("Recette")

    __table_args__ = (
        CheckConstraint("note IS NULL OR (note >= 0 AND note <= 5)", name="ck_note_valide"),
        CheckConstraint("portions_cuisinees > 0", name="ck_portions_cuisinees_positive"),
    )

    @property
    def nb_jours_depuis(self) -> int:
        """Nombre de jours depuis la dernière cuisson"""
        from datetime import date as dt_date
        return (dt_date.today() - self.date_cuisson).days

    def __repr__(self) -> str:
        return f"<HistoriqueRecette(recette={self.recette_id}, date={self.date_cuisson}, note={self.note})>"


# ═══════════════════════════════════════════════════════════
# HISTORIQUE INVENTAIRE (Nouveau!)
# ═══════════════════════════════════════════════════════════


class HistoriqueInventaire(Base):
    """Trace chaque modification de l'inventaire"""

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
    utilisateur: Mapped[str | None] = mapped_column(String(100))  # Pour future feature multi-user
    notes: Mapped[str | None] = mapped_column(Text)
    
    # Relations
    article: Mapped["ArticleInventaire"] = relationship(back_populates="historique")
    ingredient: Mapped["Ingredient"] = relationship()

    def __repr__(self) -> str:
        return f"<HistoriqueInventaire(article={self.article_id}, type={self.type_modification}, date={self.date_modification})>"


# Ajouter relation inverse dans ArticleInventaire
ArticleInventaire.historique = relationship(
    "HistoriqueInventaire", 
    back_populates="article",
    cascade="all, delete-orphan"
)


# ═══════════════════════════════════════════════════════════
# MODÈLES COURSES - PHASE 2 (PERSISTANCE MULTI-USER)
# ═══════════════════════════════════════════════════════════


class ModeleCourses(Base):
    """Template persistant pour listes de courses réutilisables - PHASE 2"""

    __tablename__ = "modeles_courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    
    # Phase 2: Support multi-user
    utilisateur_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    
    # Métadonnées
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    modifie_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    actif: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    
    # Données articles (JSON pour flexibilité Phase 2)
    articles_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # Liste articles du modèle
    
    # Relations
    articles: Mapped[list["ArticleModele"]] = relationship(
        "ArticleModele",
        back_populates="modele",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ModeleCourses(nom={self.nom}, articles={len(self.articles)}, user={self.utilisateur_id})>"


class ArticleModele(Base):
    """Article d'un modèle de courses - PHASE 2"""

    __tablename__ = "articles_modeles"

    id: Mapped[int] = mapped_column(primary_key=True)
    modele_id: Mapped[int] = mapped_column(
        ForeignKey("modeles_courses.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    ingredient_id: Mapped[int | None] = mapped_column(
        ForeignKey("ingredients.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Propriétés de l'article
    nom_article: Mapped[str] = mapped_column(String(100), nullable=False)
    quantite: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    unite: Mapped[str] = mapped_column(String(20), nullable=False, default="pièce")
    rayon_magasin: Mapped[str] = mapped_column(String(100), nullable=False, default="Autre")
    priorite: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default="moyenne"
    )  # haute, moyenne, basse
    notes: Mapped[str | None] = mapped_column(Text)
    
    # Tri/Ordre
    ordre: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Métadonnées
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint("quantite > 0", name="ck_article_modele_quantite_positive"),
        CheckConstraint(
            "priorite IN ('haute', 'moyenne', 'basse')", 
            name="ck_article_modele_priorite_valide"
        ),
    )

    # Relations
    modele: Mapped["ModeleCourses"] = relationship(back_populates="articles")
    ingredient: Mapped["Ingredient | None"] = relationship()

    def __repr__(self) -> str:
        return f"<ArticleModele(modele={self.modele_id}, article={self.nom_article}, qty={self.quantite})>"


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════


def obtenir_valeurs_enum(enum_class: type[enum.Enum]) -> list[str]:
    """Récupère toutes les valeurs d'un enum"""
    return [e.value for e in enum_class]
