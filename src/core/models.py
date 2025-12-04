"""
Modèles SQLAlchemy - Version nettoyée et unifiée
Tous les noms de tables en anglais pour cohérence
"""
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, DateTime, Date, Float, Boolean,
    ForeignKey, Text, JSON, Enum as SQLEnum, CheckConstraint,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column, declarative_base
from sqlalchemy.dialects.postgresql import JSONB
import enum

Base = declarative_base()

# ===================================
# ENUMS
# ===================================
class PriorityEnum(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class StatusEnum(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"

class MoodEnum(str, enum.Enum):
    GOOD = "good"
    OKAY = "okay"
    BAD = "bad"

class RecipeVersionEnum(str, enum.Enum):
    STANDARD = "standard"
    BABY = "baby"
    BATCH_COOKING = "batch_cooking"

class SeasonEnum(str, enum.Enum):
    SPRING = "spring"
    SUMMER = "summer"
    FALL = "fall"
    WINTER = "winter"
    ALL_YEAR = "all_year"

class MealTypeEnum(str, enum.Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"

# ===================================
# 🍲 RECETTES - ARCHITECTURE UNIFIÉE
# ===================================

class Ingredient(Base):
    """Ingrédient de base (ex: tomate, oeuf)"""
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    category: Mapped[Optional[str]] = mapped_column(String(100))  # Légumes, Protéines, etc.
    unit: Mapped[str] = mapped_column(String(50))  # kg, L, pcs
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    recipe_ingredients: Mapped[List["RecipeIngredient"]] = relationship(
        back_populates="ingredient", cascade="all, delete-orphan"
    )
    inventory_items: Mapped[List["InventoryItem"]] = relationship(
        back_populates="ingredient", cascade="all, delete-orphan"
    )


class Recipe(Base):
    """Recette de base (version parente)"""
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Temps & Difficulté
    prep_time: Mapped[int] = mapped_column(Integer)  # minutes
    cook_time: Mapped[int] = mapped_column(Integer)  # minutes
    servings: Mapped[int] = mapped_column(Integer, default=4)
    difficulty: Mapped[str] = mapped_column(String(50), default="medium")  # easy/medium/hard

    # Catégories & Tags
    meal_type: Mapped[str] = mapped_column(SQLEnum(MealTypeEnum), default=MealTypeEnum.DINNER)
    season: Mapped[str] = mapped_column(SQLEnum(SeasonEnum), default=SeasonEnum.ALL_YEAR)
    category: Mapped[Optional[str]] = mapped_column(String(100))  # Végétarien, Viande, etc.

    # Tags booléens
    is_quick: Mapped[bool] = mapped_column(Boolean, default=False)  # <30min
    is_balanced: Mapped[bool] = mapped_column(Boolean, default=False)
    is_baby_friendly: Mapped[bool] = mapped_column(Boolean, default=False)
    is_batch_friendly: Mapped[bool] = mapped_column(Boolean, default=False)
    is_freezable: Mapped[bool] = mapped_column(Boolean, default=False)

    # IA
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_score: Mapped[Optional[float]] = mapped_column(Float)  # 0-100

    # Image
    image_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Dates
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relations
    ingredients: Mapped[List["RecipeIngredient"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan"
    )
    steps: Mapped[List["RecipeStep"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan", order_by="RecipeStep.order"
    )
    versions: Mapped[List["RecipeVersion"]] = relationship(
        back_populates="base_recipe", cascade="all, delete-orphan"
    )
    batch_meals: Mapped[List["BatchMeal"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan"
    )


class RecipeIngredient(Base):
    """Ingrédient dans une recette (quantité spécifique)"""
    __tablename__ = "recipe_ingredients"

    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"))
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id", ondelete="CASCADE"))
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50))  # g, mL, pcs
    optional: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relations
    recipe: Mapped["Recipe"] = relationship(back_populates="ingredients")
    ingredient: Mapped["Ingredient"] = relationship(back_populates="recipe_ingredients")


class RecipeStep(Base):
    """Étape d'une recette"""
    __tablename__ = "recipe_steps"

    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"))
    order: Mapped[int] = mapped_column(Integer, nullable=False)  # 1, 2, 3...
    description: Mapped[str] = mapped_column(Text, nullable=False)
    duration: Mapped[Optional[int]] = mapped_column(Integer)  # minutes (optionnel)

    # Relations
    recipe: Mapped["Recipe"] = relationship(back_populates="steps")


class RecipeVersion(Base):
    """Versions adaptées d'une recette (bébé, batch cooking)"""
    __tablename__ = "recipe_versions"

    id: Mapped[int] = mapped_column(primary_key=True)
    base_recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"))
    version_type: Mapped[str] = mapped_column(SQLEnum(RecipeVersionEnum), nullable=False)

    # Instructions modifiées
    modified_instructions: Mapped[Optional[str]] = mapped_column(Text)

    # Ingrédients modifiés (JSON)
    modified_ingredients: Mapped[Optional[dict]] = mapped_column(JSONB)

    # Infos spécifiques
    baby_notes: Mapped[Optional[str]] = mapped_column(Text)  # Précautions pour bébé
    batch_parallel_steps: Mapped[Optional[List[str]]] = mapped_column(JSONB)  # Étapes parallèles
    batch_optimized_time: Mapped[Optional[int]] = mapped_column(Integer)  # Temps optimisé

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    base_recipe: Mapped["Recipe"] = relationship(back_populates="versions")


# ===================================
# 📦 INVENTAIRE & COURSES
# ===================================

class InventoryItem(Base):
    """Article en stock"""
    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id", ondelete="CASCADE"))
    quantity: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    min_quantity: Mapped[float] = mapped_column(Float, default=1.0)
    location: Mapped[Optional[str]] = mapped_column(String(100))  # Frigo, Placard
    expiry_date: Mapped[Optional[date]] = mapped_column(Date)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relations
    ingredient: Mapped["Ingredient"] = relationship(back_populates="inventory_items")


class ShoppingList(Base):
    """Liste de courses"""
    __tablename__ = "shopping_lists"

    id: Mapped[int] = mapped_column(primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id", ondelete="CASCADE"))
    needed_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    priority: Mapped[str] = mapped_column(SQLEnum(PriorityEnum), default=PriorityEnum.MEDIUM)
    purchased: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_suggested: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    purchased_at: Mapped[Optional[datetime]] = mapped_column(DateTime)


class BatchMeal(Base):
    """Repas planifié (batch cooking)"""
    __tablename__ = "batch_meals"

    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"))
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False)
    portions: Mapped[int] = mapped_column(Integer, default=4)
    status: Mapped[str] = mapped_column(SQLEnum(StatusEnum), default=StatusEnum.TODO)
    ai_planned: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    recipe: Mapped["Recipe"] = relationship(back_populates="batch_meals")


# ===================================
# 👶 FAMILLE (conservé mais nettoyé)
# ===================================

class ChildProfile(Base):
    __tablename__ = "child_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    photo_url: Mapped[Optional[str]] = mapped_column(String(500))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    wellbeing_entries: Mapped[List["WellbeingEntry"]] = relationship(
        back_populates="child", cascade="all, delete-orphan"
    )
    routines: Mapped[List["Routine"]] = relationship(back_populates="child")


class WellbeingEntry(Base):
    __tablename__ = "wellbeing_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    child_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("child_profiles.id", ondelete="CASCADE")
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    mood: Mapped[str] = mapped_column(SQLEnum(MoodEnum), nullable=False)
    sleep_hours: Mapped[Optional[float]] = mapped_column(Float)
    activity: Mapped[Optional[str]] = mapped_column(String(200))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    username: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    child: Mapped[Optional["ChildProfile"]] = relationship(back_populates="wellbeing_entries")


class Routine(Base):
    __tablename__ = "routines"

    id: Mapped[int] = mapped_column(primary_key=True)
    child_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("child_profiles.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    frequency: Mapped[str] = mapped_column(String(50), default="daily")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    child: Mapped[Optional["ChildProfile"]] = relationship(back_populates="routines")
    tasks: Mapped[List["RoutineTask"]] = relationship(
        back_populates="routine", cascade="all, delete-orphan"
    )


class RoutineTask(Base):
    __tablename__ = "routine_tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    routine_id: Mapped[int] = mapped_column(ForeignKey("routines.id", ondelete="CASCADE"))
    task_name: Mapped[str] = mapped_column(String(200), nullable=False)
    scheduled_time: Mapped[Optional[str]] = mapped_column(String(10))
    status: Mapped[str] = mapped_column(SQLEnum(StatusEnum), default=StatusEnum.TODO)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relations
    routine: Mapped["Routine"] = relationship(back_populates="tasks")


# ===================================
# 🏡 MAISON (nettoyé)
# ===================================

class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(String(100))
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    priority: Mapped[str] = mapped_column(SQLEnum(PriorityEnum), default=PriorityEnum.MEDIUM)
    status: Mapped[str] = mapped_column(SQLEnum(StatusEnum), default=StatusEnum.TODO)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relations
    tasks: Mapped[List["ProjectTask"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class ProjectTask(Base):
    __tablename__ = "project_tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    task_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(SQLEnum(StatusEnum), default=StatusEnum.TODO)
    due_date: Mapped[Optional[date]] = mapped_column(Date)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relations
    project: Mapped["Project"] = relationship(back_populates="tasks")


class GardenItem(Base):
    __tablename__ = "garden_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(100))
    planting_date: Mapped[Optional[date]] = mapped_column(Date)
    harvest_date: Mapped[Optional[date]] = mapped_column(Date)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    location: Mapped[Optional[str]] = mapped_column(String(200))
    watering_frequency_days: Mapped[int] = mapped_column(Integer, default=2)
    last_watered: Mapped[Optional[date]] = mapped_column(Date)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    logs: Mapped[List["GardenLog"]] = relationship(
        back_populates="item", cascade="all, delete-orphan"
    )


class GardenLog(Base):
    __tablename__ = "garden_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("garden_items.id", ondelete="CASCADE"))
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relations
    item: Mapped["GardenItem"] = relationship(back_populates="logs")


# ===================================
# 📅 PLANNING
# ===================================

class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    location: Mapped[Optional[str]] = mapped_column(String(200))
    category: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ===================================
# 👤 UTILISATEURS
# ===================================

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    settings: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relations
    profiles: Mapped[List["UserProfile"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    notifications: Mapped[List["Notification"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    profile_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(50))
    preferences: Mapped[dict] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    user: Mapped["User"] = relationship(back_populates="profiles")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    module: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(SQLEnum(PriorityEnum), default=PriorityEnum.MEDIUM)
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    user: Mapped["User"] = relationship(back_populates="notifications")