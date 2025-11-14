# core/models.py
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float, JSON
)
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# -------------------------
# Utilisateurs / Profil
# -------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    preferences = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    recipes = relationship("Recipe", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")

# -------------------------
# Routines & Tâches
# -------------------------
class Routine(Base):
    __tablename__ = "routines"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    frequency = Column(String, default="quotidien")  # "quotidien", "hebdomadaire", etc.

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=True)
    status = Column(String, default="à faire")  # "à faire", "en cours", "terminé"

    # Relation
    project = relationship("Project", back_populates="tasks")


# -------------------------
# Recettes et Ingrédients
# -------------------------
class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String)
    season = Column(String)
    location = Column(String)  # placard, frigo, congélateur

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relation
    user = relationship("User", back_populates="recipes")


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    recipe_id = Column(Integer, ForeignKey("recipes.id"), primary_key=True)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), primary_key=True)
    quantity = Column(String)  # ex: "200g"

# -------------------------
# Projets maison
# -------------------------
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relation
    user = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")


# -------------------------
# Inventaire / Matériel
# -------------------------
class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String)
    purchase_date = Column(DateTime)
    warranty_end = Column(DateTime)
    is_active = Column(Boolean, default=True)
    archived_at = Column(DateTime, nullable=True)

# -------------------------
# Enfant / Jules
# -------------------------
class ChildProfile(Base):
    __tablename__ = "children"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    birth_date = Column(DateTime)
    weight = Column(Float)
    height = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    activities = relationship("ChildActivity", back_populates="child")
    meals = relationship("ChildMeal", back_populates="child")

class ChildActivity(Base):
    __tablename__ = "child_activities"

    id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey("children.id"))
    name = Column(String)
    date = Column(DateTime, default=datetime.utcnow)

    child = relationship("ChildProfile", back_populates="activities")

class ChildMeal(Base):
    __tablename__ = "child_meals"

    id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey("children.id"))
    recipe_id = Column(Integer, ForeignKey("recipes.id"))
    date = Column(DateTime, default=datetime.utcnow)

    child = relationship("ChildProfile", back_populates="meals")
    recipe = relationship("Recipe")

# -------------------------
# Jardin / Potager
# -------------------------
class Plant(Base):
    __tablename__ = "plants"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    planted_at = Column(DateTime)
    harvest_estimate = Column(DateTime)
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    archived_at = Column(DateTime, nullable=True)

    garden_notes = relationship("GardenNote", back_populates="plant")

class GardenNote(Base):
    __tablename__ = "garden_notes"

    id = Column(Integer, primary_key=True)
    plant_id = Column(Integer, ForeignKey("plants.id"))
    date = Column(DateTime, default=datetime.utcnow)
    note = Column(Text)

    plant = relationship("Plant", back_populates="garden_notes")

# -------------------------
# Météo
# -------------------------
class WeatherLog(Base):
    __tablename__ = "weather_logs"

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow)
    temperature = Column(Float)
    condition = Column(String)
    notes = Column(Text)