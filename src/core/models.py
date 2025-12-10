"""
Modèles SQLAlchemy - Version française
Tous les noms de tables et colonnes en français
"""
from datetime import datetime, date
from typing import Optional, List, Dict
from sqlalchemy import (
    Column, Integer, String, DateTime, Date, Float, Boolean,
    ForeignKey, Text, JSON, Enum as SQLEnum, CheckConstraint,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column, declarative_base
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
import enum

Base = declarative_base()

# ===================================
# ENUMS EN FRANÇAIS
# ===================================
class PrioriteEnum(str, enum.Enum):
    BASSE = "basse"
    MOYENNE = "moyenne"
    HAUTE = "haute"

class StatutEnum(str, enum.Enum):
    A_FAIRE = "à faire"
    EN_COURS = "en cours"
    TERMINE = "terminé"
    ANNULE = "annulé"

class HumeurEnum(str, enum.Enum):
    BIEN = "😊 Bien"
    MOYEN = "😐 Moyen"
    MAL = "😞 Mal"

class TypeVersionRecetteEnum(str, enum.Enum):
    STANDARD = "standard"
    BEBE = "bébé"
    BATCH_COOKING = "batch_cooking"

class SaisonEnum(str, enum.Enum):
    PRINTEMPS = "printemps"
    ETE = "été"
    AUTOMNE = "automne"
    HIVER = "hiver"
    TOUTE_ANNEE = "toute_année"

class TypeRepasEnum(str, enum.Enum):
    PETIT_DEJEUNER = "petit_déjeuner"
    DEJEUNER = "déjeuner"
    DINER = "dîner"
    GOUTER = "goûter"

# ===================================
# 🍲 RECETTES
# ===================================

class Ingredient(Base):
    """Ingrédient de base"""
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    categorie: Mapped[Optional[str]] = mapped_column(String(100))
    unite: Mapped[str] = mapped_column(String(50))
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    recette_ingredients: Mapped[List["RecetteIngredient"]] = relationship(
        back_populates="ingredient", cascade="all, delete-orphan"
    )
    inventaire: Mapped[List["ArticleInventaire"]] = relationship(
        back_populates="ingredient", cascade="all, delete-orphan"
    )


class Recette(Base):
    """Recette de base"""
    __tablename__ = "recettes"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Temps & Difficulté
    temps_preparation: Mapped[int] = mapped_column(Integer)  # minutes
    temps_cuisson: Mapped[int] = mapped_column(Integer)  # minutes
    portions: Mapped[int] = mapped_column(Integer, default=4)
    difficulte: Mapped[str] = mapped_column(String(50), default="moyen")

    # Catégories & Tags
    type_repas: Mapped[str] = mapped_column(String(50), default=TypeRepasEnum.DINER.value)
    saison: Mapped[str] = mapped_column(String(50), default=SaisonEnum.TOUTE_ANNEE.value)
    categorie: Mapped[Optional[str]] = mapped_column(String(100))

    # Tags booléens
    est_rapide: Mapped[bool] = mapped_column(Boolean, default=False)
    est_equilibre: Mapped[bool] = mapped_column(Boolean, default=False)
    compatible_bebe: Mapped[bool] = mapped_column(Boolean, default=False)
    compatible_batch: Mapped[bool] = mapped_column(Boolean, default=False)
    congelable: Mapped[bool] = mapped_column(Boolean, default=False)

    # IA
    genere_par_ia: Mapped[bool] = mapped_column(Boolean, default=False)
    score_ia: Mapped[Optional[float]] = mapped_column(Float)

    # Image
    url_image: Mapped[Optional[str]] = mapped_column(String(500))

    # Dates
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
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
    repas_planning: Mapped[List["RepasPlanning"]] = relationship(
        back_populates="recette",
        cascade="all, delete-orphan",
        foreign_keys="[RepasPlanning.recette_id]"  # Explicite la clé étrangère
    )



class RecetteIngredient(Base):
    """Ingrédient dans une recette"""
    __tablename__ = "recette_ingredients"

    id: Mapped[int] = mapped_column(primary_key=True)
    recette_id: Mapped[int] = mapped_column(ForeignKey("recettes.id", ondelete="CASCADE"))
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id", ondelete="CASCADE"))
    quantite: Mapped[float] = mapped_column(Float, nullable=False)
    unite: Mapped[str] = mapped_column(String(50))
    optionnel: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relations
    recette: Mapped["Recette"] = relationship(back_populates="ingredients")
    ingredient: Mapped["Ingredient"] = relationship(back_populates="recette_ingredients")


class EtapeRecette(Base):
    """Étape xxxd'une recette"""
    __tablename__ = "etapes_recette"

    id: Mapped[int] = mapped_column(primary_key=True)
    recette_id: Mapped[int] = mapped_column(ForeignKey("recettes.id", ondelete="CASCADE"))
    ordre: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    duree: Mapped[Optional[int]] = mapped_column(Integer)

    # Relations
    recette: Mapped["Recette"] = relationship(back_populates="etapes")


class VersionRecette(Base):
    """Versions adaptées d'une recette"""
    __tablename__ = "versions_recette"

    id: Mapped[int] = mapped_column(primary_key=True)
    recette_base_id: Mapped[int] = mapped_column(ForeignKey("recettes.id", ondelete="CASCADE"))
    type_version: Mapped[str] = mapped_column(String(50), nullable=False)

    # Instructions modifiées
    instructions_modifiees: Mapped[Optional[str]] = mapped_column(Text)
    ingredients_modifies: Mapped[Optional[dict]] = mapped_column(JSONB)

    # Infos spécifiques
    notes_bebe: Mapped[Optional[str]] = mapped_column(Text)
    etapes_paralleles_batch: Mapped[Optional[List[str]]] = mapped_column(JSONB)
    temps_optimise_batch: Mapped[Optional[int]] = mapped_column(Integer)

    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    recette_base: Mapped["Recette"] = relationship(back_populates="versions")


# ===================================
# 📦 INVENTAIRE & COURSES
# ===================================

class ArticleInventaire(Base):
    """Article en stock"""
    __tablename__ = "inventaire"

    id: Mapped[int] = mapped_column(primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id", ondelete="CASCADE"))
    quantite: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    quantite_min: Mapped[float] = mapped_column(Float, default=1.0)
    emplacement: Mapped[Optional[str]] = mapped_column(String(100))
    date_peremption: Mapped[Optional[date]] = mapped_column(Date)
    derniere_maj: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relations
    ingredient: Mapped["Ingredient"] = relationship(back_populates="inventaire")


class ArticleCourses(Base):
    """Liste de courses"""
    __tablename__ = "liste_courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id", ondelete="CASCADE"))
    quantite_necessaire: Mapped[float] = mapped_column(Float, nullable=False)
    priorite: Mapped[str] = mapped_column(String(50), default="moyenne")
    achete: Mapped[bool] = mapped_column(Boolean, default=False)
    suggere_par_ia: Mapped[bool] = mapped_column(Boolean, default=False)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    achete_le: Mapped[Optional[datetime]] = mapped_column(DateTime)
    rayon_magasin: Mapped[Optional[str]] = mapped_column(String(100))
    magasin_cible: Mapped[Optional[str]] = mapped_column(String(50))
    notes: Mapped[Optional[str]] = mapped_column(Text)


# ===================================
# PLANNING HEBDOMADAIRE
# ===================================

class PlanningHebdomadaire(Base):
    """Planning d'une semaine"""
    __tablename__ = "plannings_hebdomadaires"

    id: Mapped[int] = mapped_column(primary_key=True)
    semaine_debut: Mapped[date] = mapped_column(Date, nullable=False)  # Lundi
    nom: Mapped[Optional[str]] = mapped_column(String(200))
    genere_par_ia: Mapped[bool] = mapped_column(Boolean, default=False)
    statut: Mapped[str] = mapped_column(String(50), default="brouillon")  # brouillon, actif, archive
    notes: Mapped[Optional[str]] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    modifie_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    repas: Mapped[List["RepasPlanning"]] = relationship(
        "RepasPlanning",
        back_populates="planning",
        cascade="all, delete-orphan",
        order_by="RepasPlanning.jour_semaine, RepasPlanning.ordre"
    )

class RepasPlanning(Base):
    """Repas individuel dans un planning"""
    __tablename__ = "repas_planning"

    id: Mapped[int] = mapped_column(primary_key=True)
    planning_id: Mapped[int] = mapped_column(ForeignKey("plannings_hebdomadaires.id", ondelete="CASCADE"))
    jour_semaine: Mapped[int] = mapped_column(Integer, nullable=False)  # 0=lundi, 6=dimanche
    date: Mapped[date] = mapped_column(Date, nullable=False)
    type_repas: Mapped[str] = mapped_column(String(50), nullable=False)
    recette_id: Mapped[Optional[int]] = mapped_column(ForeignKey("recettes.id", ondelete="SET NULL"))
    portions: Mapped[int] = mapped_column(Integer, default=4)
    est_adapte_bebe: Mapped[bool] = mapped_column(Boolean, default=False)
    est_batch_cooking: Mapped[bool] = mapped_column(Boolean, default=False)
    recettes_batch: Mapped[Optional[List[int]]] = mapped_column(ARRAY(Integer))  # IDs recettes produites
    notes: Mapped[Optional[str]] = mapped_column(Text)
    ordre: Mapped[int] = mapped_column(Integer, default=0)  # Ordre dans la journée
    statut: Mapped[str] = mapped_column(String(50), default="planifié")
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    planning: Mapped["PlanningHebdomadaire"] = relationship(back_populates="repas")
    recette: Mapped[Optional["Recette"]] = relationship(back_populates="repas_planning")

class ConfigPlanningUtilisateur(Base):
    """Configuration utilisateur pour le planning"""
    __tablename__ = "config_planning_utilisateur"

    id: Mapped[int] = mapped_column(primary_key=True)
    utilisateur_id: Mapped[Optional[int]] = mapped_column(ForeignKey("utilisateurs.id", ondelete="CASCADE"))
    repas_actifs: Mapped[Dict] = mapped_column(JSONB, default={
        "petit_déjeuner": False,
        "déjeuner": True,
        "dîner": True,
        "goûter": False,
        "bébé": False,
        "batch_cooking": False
    })
    nb_adultes: Mapped[int] = mapped_column(Integer, default=2)
    nb_enfants: Mapped[int] = mapped_column(Integer, default=0)
    a_bebe: Mapped[bool] = mapped_column(Boolean, default=False)
    batch_cooking_actif: Mapped[bool] = mapped_column(Boolean, default=False)
    jours_batch: Mapped[List[int]] = mapped_column(ARRAY(Integer), default=[])  # [0, 6] = lundi/dimanche
    preferences: Mapped[Dict] = mapped_column(JSONB, default={})
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ===================================
# 👶 FAMILLE
# ===================================

class ProfilEnfant(Base):
    __tablename__ = "profils_enfants"

    id: Mapped[int] = mapped_column(primary_key=True)
    prenom: Mapped[str] = mapped_column(String(100), nullable=False)
    date_naissance: Mapped[date] = mapped_column(Date, nullable=False)
    url_photo: Mapped[Optional[str]] = mapped_column(String(500))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    entrees_bien_etre: Mapped[List["EntreeBienEtre"]] = relationship(
        back_populates="enfant", cascade="all, delete-orphan"
    )
    routines: Mapped[List["Routine"]] = relationship(back_populates="enfant")


class EntreeBienEtre(Base):
    __tablename__ = "entrees_bien_etre"

    id: Mapped[int] = mapped_column(primary_key=True)
    enfant_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("profils_enfants.id", ondelete="CASCADE")
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    humeur: Mapped[str] = mapped_column(String(50), nullable=False)
    heures_sommeil: Mapped[Optional[float]] = mapped_column(Float)
    activite: Mapped[Optional[str]] = mapped_column(String(200))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    nom_utilisateur: Mapped[Optional[str]] = mapped_column(String(100))
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    enfant: Mapped[Optional["ProfilEnfant"]] = relationship(back_populates="entrees_bien_etre")


class Routine(Base):
    __tablename__ = "routines"

    id: Mapped[int] = mapped_column(primary_key=True)
    enfant_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("profils_enfants.id", ondelete="CASCADE")
    )
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    frequence: Mapped[str] = mapped_column(String(50), default="quotidien")
    est_active: Mapped[bool] = mapped_column(Boolean, default=True)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    enfant: Mapped[Optional["ProfilEnfant"]] = relationship(back_populates="routines")
    taches: Mapped[List["TacheRoutine"]] = relationship(
        back_populates="routine", cascade="all, delete-orphan"
    )


class TacheRoutine(Base):
    __tablename__ = "taches_routine"

    id: Mapped[int] = mapped_column(primary_key=True)
    routine_id: Mapped[int] = mapped_column(ForeignKey("routines.id", ondelete="CASCADE"))
    nom_tache: Mapped[str] = mapped_column(String(200), nullable=False)
    heure_prevue: Mapped[Optional[str]] = mapped_column(String(10))
    statut: Mapped[str] = mapped_column(String(50), default="à faire")
    termine_le: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relations
    routine: Mapped["Routine"] = relationship(back_populates="taches")


# ===================================
# 🏡 MAISON
# ===================================

class Projet(Base):
    __tablename__ = "projets"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    categorie: Mapped[Optional[str]] = mapped_column(String(100))
    date_debut: Mapped[Optional[date]] = mapped_column(Date)
    date_fin: Mapped[Optional[date]] = mapped_column(Date)
    priorite: Mapped[str] = mapped_column(String(50), default="moyenne")
    statut: Mapped[str] = mapped_column(String(50), default="à faire")
    progression: Mapped[int] = mapped_column(Integer, default=0)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    modifie_le: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relations
    taches: Mapped[List["TacheProjet"]] = relationship(
        back_populates="projet", cascade="all, delete-orphan"
    )


class TacheProjet(Base):
    __tablename__ = "taches_projet"

    id: Mapped[int] = mapped_column(primary_key=True)
    projet_id: Mapped[int] = mapped_column(ForeignKey("projets.id", ondelete="CASCADE"))
    nom_tache: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    statut: Mapped[str] = mapped_column(String(50), default="à faire")
    date_echeance: Mapped[Optional[date]] = mapped_column(Date)
    termine_le: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relations
    projet: Mapped["Projet"] = relationship(back_populates="taches")


class ElementJardin(Base):
    __tablename__ = "elements_jardin"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    categorie: Mapped[str] = mapped_column(String(100))
    date_plantation: Mapped[Optional[date]] = mapped_column(Date)
    date_recolte: Mapped[Optional[date]] = mapped_column(Date)
    quantite: Mapped[int] = mapped_column(Integer, default=1)
    emplacement: Mapped[Optional[str]] = mapped_column(String(200))
    frequence_arrosage_jours: Mapped[int] = mapped_column(Integer, default=2)
    dernier_arrosage: Mapped[Optional[date]] = mapped_column(Date)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    logs: Mapped[List["LogJardin"]] = relationship(
        back_populates="element", cascade="all, delete-orphan"
    )


class LogJardin(Base):
    __tablename__ = "logs_jardin"

    id: Mapped[int] = mapped_column(primary_key=True)
    element_id: Mapped[int] = mapped_column(ForeignKey("elements_jardin.id", ondelete="CASCADE"))
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relations
    element: Mapped["ElementJardin"] = relationship(back_populates="logs")


# ===================================
# 📅 PLANNING
# ===================================

class EvenementCalendrier(Base):
    __tablename__ = "evenements_calendrier"

    id: Mapped[int] = mapped_column(primary_key=True)
    titre: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    date_debut: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    date_fin: Mapped[Optional[datetime]] = mapped_column(DateTime)
    lieu: Mapped[Optional[str]] = mapped_column(String(200))
    categorie: Mapped[Optional[str]] = mapped_column(String(100))
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ===================================
# 👤 UTILISATEURS
# ===================================

class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom_utilisateur: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    parametres: Mapped[dict] = mapped_column(JSON, default=dict)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    modifie_le: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relations
    profils: Mapped[List["ProfilUtilisateur"]] = relationship(
        back_populates="utilisateur", cascade="all, delete-orphan"
    )
    notifications: Mapped[List["Notification"]] = relationship(
        back_populates="utilisateur", cascade="all, delete-orphan"
    )


class ProfilUtilisateur(Base):
    __tablename__ = "profils_utilisateur"

    id: Mapped[int] = mapped_column(primary_key=True)
    utilisateur_id: Mapped[int] = mapped_column(ForeignKey("utilisateurs.id", ondelete="CASCADE"))
    nom_profil: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(50))
    preferences: Mapped[dict] = mapped_column(JSON, default=dict)
    est_actif: Mapped[bool] = mapped_column(Boolean, default=True)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    utilisateur: Mapped["Utilisateur"] = relationship(back_populates="profils")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    utilisateur_id: Mapped[int] = mapped_column(ForeignKey("utilisateurs.id", ondelete="CASCADE"))
    module: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    priorite: Mapped[str] = mapped_column(String(50), default="moyenne")
    lu: Mapped[bool] = mapped_column(Boolean, default=False)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    utilisateur: Mapped["Utilisateur"] = relationship(back_populates="notifications")